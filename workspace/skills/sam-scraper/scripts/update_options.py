"""
SAM NPA Scraper — Step 1: Fetch & cache dropdown options
Usage: python update_options.py [--db-uri postgresql://...]
"""

import argparse
import asyncio
import os
import sys
from datetime import datetime

import httpx
from selectolax.parser import HTMLParser

from html_utils import create_http_client, text_of, attr_of
from models import SamDropdownCache, Base, SAMDropdownOption

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DEFAULT_DB_URI = "postgresql://arsapolm@localhost:5432/npa_kb"

BASE_URL = "https://sam.or.th/site/npa/page_list.php"
AJAX_URL = "https://sam.or.th/site/npa/api/getMasterData.php"


async def fetch_page(client: httpx.AsyncClient) -> HTMLParser:
    """GET the list page (dropdowns are in the initial HTML)."""
    resp = await client.get(BASE_URL)
    resp.raise_for_status()
    resp.encoding = "utf-8"
    return HTMLParser(resp.text)


def parse_options(tree: HTMLParser) -> list[SAMDropdownOption]:
    """Extract all dropdown options from the search form."""
    options: list[SAMDropdownOption] = []

    for select_id, option_type in [
        ("product_type", "product_type"),
        ("province", "province"),
        ("district", "district"),
        ("s_status", "status"),
    ]:
        sel = tree.css_first(f"select#{select_id}")
        if not sel:
            continue
        for opt in sel.css("option"):
            val = attr_of(opt, "value").strip()
            if not val:
                continue
            options.append(
                SAMDropdownOption(
                    option_type=option_type,
                    option_id=int(val),
                    option_name=text_of(opt),
                )
            )

    return options


async def fetch_districts_for_province(
    client: httpx.AsyncClient,
    province_id: int,
    semaphore: asyncio.Semaphore,
    delay: float = 0.5,
) -> list[SAMDropdownOption]:
    """Fetch districts for a specific province via AJAX endpoint."""
    async with semaphore:
        await asyncio.sleep(delay)
        try:
            resp = await client.post(
                AJAX_URL,
                data={"act": "getDistrict", "province_id": str(province_id)},
                timeout=15,
            )
            if resp.status_code != 200:
                return []
            tree = HTMLParser(resp.text)
            results = []
            for opt in tree.css("option"):
                val = attr_of(opt, "value").strip()
                if not val:
                    continue
                results.append(
                    SAMDropdownOption(
                        option_type="district",
                        option_id=int(val),
                        option_name=text_of(opt),
                        parent_id=province_id,
                    )
                )
            return results
        except Exception:
            return []


def sync_to_db(options: list[SAMDropdownOption], db_uri: str) -> tuple[int, int]:
    """Upsert options to database. Returns (new, updated)."""
    engine = create_engine(db_uri)
    Base.metadata.create_all(engine, tables=[SamDropdownCache.__table__])
    Session = sessionmaker(bind=engine)

    new_count = 0
    updated_count = 0

    with Session() as session:
        for opt in options:
            existing = (
                session.query(SamDropdownCache)
                .filter_by(option_type=opt.option_type, option_id=opt.option_id)
                .first()
            )
            if existing is None:
                session.add(
                    SamDropdownCache(
                        option_type=opt.option_type,
                        option_id=opt.option_id,
                        option_name=opt.option_name,
                        parent_id=opt.parent_id,
                    )
                )
                new_count += 1
            elif existing.option_name != opt.option_name or existing.parent_id != opt.parent_id:
                existing.option_name = opt.option_name
                existing.parent_id = opt.parent_id
                existing.updated_at = datetime.now()
                updated_count += 1

        session.commit()

    return new_count, updated_count


async def main():
    parser = argparse.ArgumentParser(description="Fetch SAM dropdown options")
    parser.add_argument(
        "--db-uri",
        default=os.getenv("POSTGRES_URI", DEFAULT_DB_URI),
        help="PostgreSQL connection string",
    )
    parser.add_argument(
        "--fetch-districts",
        action="store_true",
        help="Also fetch districts for all provinces via AJAX",
    )
    args = parser.parse_args()

    print("Fetching SAM dropdown options...")
    async with create_http_client() as client:
        tree = await fetch_page(client)
        options = parse_options(tree)
        print(f"   Found {len(options)} options from search form")

        if args.fetch_districts:
            provinces = [o for o in options if o.option_type == "province"]
            print(f"   Fetching districts for {len(provinces)} provinces...")

            semaphore = asyncio.Semaphore(10)
            tasks = [
                fetch_districts_for_province(client, prov.option_id, semaphore)
                for prov in provinces
            ]
            results = await asyncio.gather(*tasks)

            for prov, dists in zip(provinces, results):
                options.extend(dists)
                print(f"     {prov.option_name}: {len(dists)} districts")
            print(f"   Total options: {len(options)}")

    new, updated = sync_to_db(options, args.db_uri)
    print(f"Options synced: {new} new, {updated} updated")

    by_type: dict[str, int] = {}
    for o in options:
        by_type[o.option_type] = by_type.get(o.option_type, 0) + 1
    for t, c in sorted(by_type.items()):
        print(f"   {t}: {c}")


if __name__ == "__main__":
    asyncio.run(main())

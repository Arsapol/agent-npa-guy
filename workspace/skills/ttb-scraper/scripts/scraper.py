"""
TTB/PAMCO NPA Scraper — List API paginator with PostgreSQL upsert.

Scrapes all NPA properties from TTB/PAMCO's property-new/display endpoint,
upserts into PostgreSQL, and tracks price changes.

Architecture:
  - List-only (no detail endpoint needed — all fields in list response)
  - Simple REST JSON, just needs User-Agent header
  - ~1,356 properties, 7 pages at limit=200
  - Two sources: PAMCO (type=3) and TTB (type=4)

Usage:
    python scraper.py                           # full scrape
    python scraper.py --province 10             # Bangkok only
    python scraper.py --category 4              # condos only
    python scraper.py --limit 5                 # first N items (test)
    python scraper.py --create-tables           # create DB tables only
"""

import argparse
import asyncio
import sys
from datetime import datetime

import httpx
from sqlalchemy.orm import Session

from database import create_tables, get_engine, upsert_properties
from models import TtbListResponse, TtbPropertyItem, TtbScrapeLog

API_BASE = "https://property-api-prod.automer.io/"
SITE_BASE = "https://property.pamco.co.th"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "th-TH,th;q=0.9,en;q=0.7",
    "Origin": SITE_BASE,
    "Referer": f"{SITE_BASE}/",
}

PAGE_SIZE = 200
BATCH_SIZE = 200


async def fetch_page(
    client: httpx.AsyncClient,
    page: int,
    limit: int,
    province: int | None = None,
    category: int | None = None,
) -> TtbListResponse:
    """Fetch a single page from the list endpoint."""
    params: dict = {"page": page, "limit": limit}
    if province is not None:
        params["province"] = province
    if category is not None:
        params["type"] = category

    r = await client.get(f"{API_BASE}property-new/display", params=params)
    r.raise_for_status()
    data = r.json()
    return TtbListResponse(**data)


async def scrape_all(
    province: int | None = None,
    category: int | None = None,
    limit: int | None = None,
) -> None:
    """Scrape all TTB/PAMCO properties and upsert to DB."""
    engine = get_engine()
    started_at = datetime.now().astimezone()
    log = TtbScrapeLog(started_at=started_at)

    total_api = 0
    all_items: list[TtbPropertyItem] = []
    failed_pages = 0

    async with httpx.AsyncClient(headers=HEADERS, timeout=30, follow_redirects=True) as client:
        # First request to get total count
        print("Fetching page 1...")
        try:
            first_page = await fetch_page(client, 1, PAGE_SIZE, province, category)
        except Exception as e:
            print(f"FATAL: Failed to fetch first page: {e}", file=sys.stderr)
            with Session(engine) as session:
                log.finished_at = datetime.now().astimezone()
                log.error = str(e)
                session.add(log)
                session.commit()
            return

        total_api = first_page.total
        print(f"Total properties: {total_api}")

        # Parse first page
        for raw in first_page.items:
            try:
                item = TtbPropertyItem.from_api(raw)
                all_items.append(item)
            except Exception as e:
                print(f"  WARN: parse error: {e}")

        if limit and len(all_items) >= limit:
            all_items = all_items[:limit]
        else:
            # Fetch remaining pages
            total_pages = (total_api + PAGE_SIZE - 1) // PAGE_SIZE
            for page_num in range(2, total_pages + 1):
                if limit and len(all_items) >= limit:
                    break
                print(f"Fetching page {page_num}/{total_pages}...")
                try:
                    page_data = await fetch_page(client, page_num, PAGE_SIZE, province, category)
                    for raw in page_data.items:
                        try:
                            item = TtbPropertyItem.from_api(raw)
                            all_items.append(item)
                        except Exception as e:
                            print(f"  WARN: parse error: {e}")
                except Exception as e:
                    print(f"  ERROR page {page_num}: {e}", file=sys.stderr)
                    failed_pages += 1

            if limit:
                all_items = all_items[:limit]

    print(f"\nParsed {len(all_items)} properties. Upserting to DB...")

    # Upsert in batches
    total_counts = {"new": 0, "updated": 0, "price_changed": 0}

    with Session(engine) as session:
        for i in range(0, len(all_items), BATCH_SIZE):
            batch = all_items[i : i + BATCH_SIZE]
            counts = upsert_properties(session, batch)
            for k in total_counts:
                total_counts[k] += counts[k]
            session.commit()
            print(
                f"  Batch {i // BATCH_SIZE + 1}: "
                f"+{counts['new']} new, "
                f"~{counts['updated']} updated, "
                f"${counts['price_changed']} price changes"
            )

        # Write scrape log
        log.finished_at = datetime.now().astimezone()
        log.total_api = total_api
        log.new_count = total_counts["new"]
        log.updated_count = total_counts["updated"]
        log.price_changed_count = total_counts["price_changed"]
        log.failed_pages = failed_pages
        session.add(log)
        session.commit()

    print(
        f"\nDone! "
        f"new={total_counts['new']}, "
        f"updated={total_counts['updated']}, "
        f"price_changed={total_counts['price_changed']}, "
        f"failed_pages={failed_pages}"
    )


def main():
    parser = argparse.ArgumentParser(description="TTB/PAMCO NPA scraper")
    parser.add_argument("--create-tables", action="store_true", help="Create DB tables only")
    parser.add_argument("--province", type=int, help="Province code (e.g. 10=Bangkok)")
    parser.add_argument("--category", type=int, help="Category (1-7, 4=condo)")
    parser.add_argument("--limit", type=int, help="Max properties to scrape (test)")
    args = parser.parse_args()

    if args.create_tables:
        create_tables()
        return

    asyncio.run(scrape_all(
        province=args.province,
        category=args.category,
        limit=args.limit,
    ))


if __name__ == "__main__":
    main()

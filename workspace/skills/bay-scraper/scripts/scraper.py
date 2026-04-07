"""
BAY/Krungsri Production Scraper

Scrapes all NPA properties from krungsriproperty.com, upserts into PostgreSQL,
and tracks price changes.

Architecture:
  - Step 1: GET /search-result → regex extract ALL property codes from HTML
  - Step 2: GET /Helpers/GetProperties → JSON (74 fields) in batches of 50
  - No rate limiting observed, but polite delays included

Usage:
    python scraper.py                         # full scrape (all properties)
    python scraper.py --category C            # condos only
    python scraper.py --limit 50              # first N properties (test)
    python scraper.py --create-tables         # create DB tables only
"""

import argparse
import asyncio
import re
import sys
import time
from datetime import datetime

import httpx
from sqlalchemy.orm import Session

from database import create_tables, get_engine, upsert_properties
from models import BayProperty, BayScrapeLog

BASE_URL = "https://www.krungsriproperty.com"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
}
API_HEADERS = {
    **HEADERS,
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": f"{BASE_URL}/home",
}

CODE_PATTERN = re.compile(r"[A-Z]{1,3}[XYZ]\d{3,5}(?:_[A-Z]+\d+)?")
BATCH_SIZE = 50
BATCH_DELAY = 0.5  # seconds between batches


async def discover_codes(
    client: httpx.AsyncClient,
    category: str | None = None,
) -> list[str]:
    """Step 1: Discover all property codes from search-result page."""
    params: dict[str, str] = {"keyWord": ""}
    if category:
        params["category"] = category

    resp = await client.get(
        f"{BASE_URL}/search-result",
        params=params,
        headers=HEADERS,
        follow_redirects=True,
        timeout=30,
    )
    resp.raise_for_status()

    total_match = re.findall(r"_convertDatasource\((\d+)\)", resp.text)
    total = int(total_match[0]) if total_match else 0
    print(f"  Declared total: {total}", flush=True)

    codes = sorted(set(CODE_PATTERN.findall(resp.text)))
    print(f"  Unique codes extracted: {len(codes)}", flush=True)

    return codes


async def fetch_batch(
    client: httpx.AsyncClient,
    codes: list[str],
) -> list[dict]:
    """Fetch a batch of properties via GetProperties API."""
    codes_str = ",".join(codes)
    resp = await client.get(
        f"{BASE_URL}/Helpers/GetProperties",
        params={
            "listCodes": codes_str,
            "pageNumber": "1",
            "pageSize": "100",
            "orderBy": "",
        },
        headers=API_HEADERS,
        follow_redirects=True,
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def parse_properties(raw_list: list[dict]) -> list[BayProperty]:
    """Parse raw JSON dicts into BayProperty Pydantic models."""
    results: list[BayProperty] = []
    for raw in raw_list:
        try:
            prop = BayProperty.model_validate(raw)
            prop.raw_json = raw
            results.append(prop)
        except Exception as e:
            code = raw.get("code", "?")
            print(f"  WARN: failed to parse {code}: {e}", flush=True)
    return results


async def run_scraper(
    category: str | None = None,
    limit: int | None = None,
) -> dict:
    """Main scraper entrypoint."""
    started_at = datetime.now()
    engine = get_engine()

    print(f"\n=== BAY scraper starting at {started_at} ===", flush=True)

    async with httpx.AsyncClient() as client:
        # Step 1: Discover codes
        print("\nStep 1: Discovering property codes...", flush=True)
        codes = await discover_codes(client, category=category)

        if not codes:
            print("ERROR: No codes discovered. Aborting.", flush=True)
            return {"error": "No codes discovered"}

        if limit:
            codes = codes[:limit]
            print(f"  Limited to {limit} codes", flush=True)

        # Step 2: Fetch in batches
        print(f"\nStep 2: Fetching {len(codes)} properties in batches of {BATCH_SIZE}...", flush=True)
        batches = [codes[i : i + BATCH_SIZE] for i in range(0, len(codes), BATCH_SIZE)]

        all_parsed: list[BayProperty] = []
        failed_batches = 0

        for batch_idx, batch in enumerate(batches):
            try:
                raw_list = await fetch_batch(client, batch)
                parsed = parse_properties(raw_list)
                all_parsed.extend(parsed)
                print(
                    f"  Batch {batch_idx + 1}/{len(batches)}: "
                    f"requested {len(batch)}, got {len(raw_list)}, parsed {len(parsed)}",
                    flush=True,
                )
            except Exception as e:
                failed_batches += 1
                print(
                    f"  Batch {batch_idx + 1}/{len(batches)}: FAILED — {e}",
                    flush=True,
                )

            if batch_idx < len(batches) - 1:
                await asyncio.sleep(BATCH_DELAY)

    # Step 3: Upsert into database
    print(f"\nStep 3: Upserting {len(all_parsed)} properties into database...", flush=True)

    with Session(engine) as session:
        counts = upsert_properties(session, all_parsed)
        session.commit()

        # Log scrape run
        finished_at = datetime.now()
        log = BayScrapeLog(
            started_at=started_at,
            finished_at=finished_at,
            total_codes_discovered=len(codes),
            total_fetched=len(all_parsed),
            new_count=counts["new"],
            updated_count=counts["updated"],
            price_changed_count=counts["price_changed"],
            failed_batches=failed_batches,
        )
        session.add(log)
        session.commit()

    elapsed = (finished_at - started_at).total_seconds()
    print(f"\n=== BAY scraper finished in {elapsed:.1f}s ===", flush=True)
    print(f"  Codes discovered: {len(codes)}", flush=True)
    print(f"  Properties fetched: {len(all_parsed)}", flush=True)
    print(f"  New: {counts['new']}", flush=True)
    print(f"  Updated: {counts['updated']}", flush=True)
    print(f"  Price changed: {counts['price_changed']}", flush=True)
    print(f"  Failed batches: {failed_batches}", flush=True)

    return {
        "codes_discovered": len(codes),
        "fetched": len(all_parsed),
        **counts,
        "failed_batches": failed_batches,
        "elapsed_seconds": elapsed,
    }


def main():
    parser = argparse.ArgumentParser(description="BAY/Krungsri NPA Scraper")
    parser.add_argument(
        "--create-tables", action="store_true",
        help="Create database tables and exit",
    )
    parser.add_argument(
        "--category", type=str, default=None,
        help="Filter by category: A (house), B (townhouse), C (condo), D (shophouse), E (land), F (other)",
    )
    parser.add_argument(
        "--limit", type=int, default=None,
        help="Limit number of properties to scrape (for testing)",
    )
    args = parser.parse_args()

    if args.create_tables:
        create_tables()
        sys.exit(0)

    asyncio.run(run_scraper(category=args.category, limit=args.limit))


if __name__ == "__main__":
    main()

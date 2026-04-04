"""
JAM Production Scraper

Scrapes all properties from jjpropertythai.com, upserts into PostgreSQL,
and tracks price changes + sold transitions.

Usage:
    python scraper.py                  # full scrape
    python scraper.py --limit 100      # scrape first 100 properties (test)
    python scraper.py --create-tables  # create DB tables only
"""

import argparse
import asyncio
import time
from datetime import datetime, timezone

import httpx
from sqlalchemy.orm import Session

from crypto import decrypt_response
from database import create_tables, get_engine, upsert_properties
from models import JamPropertyParsed, JamScrapeLog

BASE_URL = "https://www.jjpropertythai.com/api/proxy/v1"
HEADERS = {
    "Accept": "application/json",
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Referer": "https://www.jjpropertythai.com/Search",
}
CONCURRENCY = 5
PAGE_SIZE = 50


async def init_session(client: httpx.AsyncClient) -> bool:
    """Visit homepage to acquire cookiesession1."""
    resp = await client.get("https://www.jjpropertythai.com/", headers=HEADERS)
    cookie = dict(client.cookies).get("cookiesession1", "none")
    print(f"  Cookie: {cookie[:16]}...")
    return resp.status_code == 200


async def fetch_with_retry(
    client: httpx.AsyncClient,
    url: str,
    params: dict,
    max_retries: int = 3,
    base_delay: float = 2.0,
) -> dict | None:
    for attempt in range(max_retries):
        try:
            resp = await client.get(url, params=params, headers=HEADERS)
            resp.raise_for_status()
            return decrypt_response(resp.json())
        except httpx.HTTPStatusError as e:
            if e.response.status_code >= 500:
                delay = base_delay * (2 ** attempt)
                print(f"    Server {e.response.status_code}, retry {attempt + 1} in {delay:.0f}s...")
                await asyncio.sleep(delay)
            else:
                print(f"    HTTP {e.response.status_code}")
                return None
        except (httpx.ReadTimeout, httpx.ConnectTimeout):
            delay = base_delay * (2 ** attempt)
            print(f"    Timeout, retry {attempt + 1} in {delay:.0f}s...")
            await asyncio.sleep(delay)
        except Exception as e:
            delay = base_delay * (2 ** attempt)
            print(f"    Error: {e}, retry {attempt + 1} in {delay:.0f}s...")
            await asyncio.sleep(delay)
    return None


async def fetch_page(client: httpx.AsyncClient, page: int) -> dict | None:
    return await fetch_with_retry(client, f"{BASE_URL}/assets", {
        "freeText": "",
        "page": page,
        "user_code": "521789",
        "limit": PAGE_SIZE,
        "SellingStart": 0,
        "SellingEnd": 100000000,
    })


def parse_properties(raw_items: list[dict]) -> list[JamPropertyParsed]:
    """Parse raw API items into Pydantic models."""
    parsed = []
    for item in raw_items:
        try:
            p = JamPropertyParsed.model_validate(item)
            p.raw_json = item
            parsed.append(p)
        except Exception as e:
            asset_id = item.get("Asset_ID", "?")
            print(f"    Parse error for asset {asset_id}: {e}")
    return parsed


async def scrape_all(max_properties: int | None = None) -> tuple[list[JamPropertyParsed], list[int]]:
    """Scrape all properties from JAM API. Returns (properties, failed_pages)."""
    all_parsed: list[JamPropertyParsed] = []
    seen_ids: set[int] = set()
    failed_pages: list[int] = []

    async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
        await init_session(client)

        # First page (slow ~30s)
        print("  Fetching page 1 (cold start, may take ~30s)...")
        t0 = time.time()
        result = await fetch_page(client, page=1)
        if not result:
            print("  FATAL: Failed to fetch page 1")
            return all_parsed, [1]

        total = result.get("count", 0)
        total_pages = (total + PAGE_SIZE - 1) // PAGE_SIZE
        if max_properties:
            total_pages = min(total_pages, (max_properties + PAGE_SIZE - 1) // PAGE_SIZE)
        print(f"  Page 1 OK ({time.time() - t0:.1f}s) — {total:,} properties, scraping {total_pages} pages")

        # Process page 1
        items = parse_properties(result.get("data", []))
        for p in items:
            if p.asset_id not in seen_ids:
                seen_ids.add(p.asset_id)
                all_parsed.append(p)

        # Concurrent pagination
        sem = asyncio.Semaphore(CONCURRENCY)

        async def fetch_one(page: int) -> tuple[int, list[dict], float, bool]:
            async with sem:
                t = time.time()
                r = await fetch_page(client, page=page)
                elapsed = time.time() - t
                if r:
                    return page, r.get("data", []), elapsed, True
                return page, [], elapsed, False

        for batch_start in range(2, total_pages + 1, CONCURRENCY):
            batch_end = min(batch_start + CONCURRENCY, total_pages + 1)
            tasks = [fetch_one(p) for p in range(batch_start, batch_end)]
            results = await asyncio.gather(*tasks)

            for page_num, raw_items, elapsed, ok in sorted(results):
                if ok:
                    items = parse_properties(raw_items)
                    new = 0
                    for p in items:
                        if p.asset_id not in seen_ids:
                            seen_ids.add(p.asset_id)
                            all_parsed.append(p)
                            new += 1
                    print(f"    Page {page_num}/{total_pages}: +{new} → {len(all_parsed):,} ({elapsed:.1f}s)")
                else:
                    failed_pages.append(page_num)
                    print(f"    Page {page_num}/{total_pages}: FAILED ({elapsed:.1f}s)")

            await asyncio.sleep(0.5)

        # Retry failed pages sequentially
        if failed_pages:
            print(f"\n  Retrying {len(failed_pages)} failed pages...")
            still_failed = []
            for p in failed_pages:
                await asyncio.sleep(2.0)
                r = await fetch_page(client, page=p)
                if r:
                    items = parse_properties(r.get("data", []))
                    for item in items:
                        if item.asset_id not in seen_ids:
                            seen_ids.add(item.asset_id)
                            all_parsed.append(item)
                    print(f"    Page {p}: recovered")
                else:
                    still_failed.append(p)
                    print(f"    Page {p}: still failed")
            failed_pages = still_failed

    return all_parsed, failed_pages


def save_to_db(
    properties: list[JamPropertyParsed],
    failed_pages: list[int],
    started_at: datetime,
) -> dict[str, int]:
    """Upsert properties into database with price tracking."""
    engine = get_engine()
    batch_size = 500
    total_counts = {"new": 0, "updated": 0, "price_changed": 0, "sold": 0, "unsold": 0}

    with Session(engine) as session:
        # Process in batches
        for i in range(0, len(properties), batch_size):
            batch = properties[i : i + batch_size]
            counts = upsert_properties(session, batch)
            for k, v in counts.items():
                total_counts[k] += v
            session.flush()

            if (i + batch_size) % 2000 == 0 or i + batch_size >= len(properties):
                print(f"    DB batch {i + batch_size}/{len(properties)}: {total_counts}")

        # Log the scrape run
        log = JamScrapeLog(
            started_at=started_at,
            finished_at=datetime.now(timezone.utc),
            total_api=len(properties),
            new_count=total_counts["new"],
            updated_count=total_counts["updated"],
            sold_count=total_counts["sold"],
            failed_pages=len(failed_pages),
        )
        session.add(log)
        session.commit()

    return total_counts


async def main(limit: int | None = None, create_tables_only: bool = False):
    if create_tables_only:
        create_tables()
        return

    started_at = datetime.now(timezone.utc)
    print(f"=== JAM Scraper — {started_at.isoformat()} ===\n")

    # Ensure tables exist
    create_tables()

    # Scrape
    print("\n1. Scraping API...")
    properties, failed_pages = await scrape_all(max_properties=limit)
    print(f"\n   Scraped: {len(properties):,} properties, {len(failed_pages)} failed pages")

    if not properties:
        print("   No properties scraped — aborting DB save")
        return

    # Save to DB
    print("\n2. Saving to database...")
    counts = save_to_db(properties, failed_pages, started_at)

    elapsed = (datetime.now(timezone.utc) - started_at).total_seconds()
    print(f"\n=== Done in {elapsed:.0f}s ({elapsed / 60:.1f}m) ===")
    print(f"   New: {counts['new']:,}")
    print(f"   Updated: {counts['updated']:,}")
    print(f"   Price changed: {counts['price_changed']:,}")
    print(f"   Sold: {counts['sold']:,}")
    print(f"   Unsold: {counts['unsold']:,}")
    print(f"   Failed pages: {len(failed_pages)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="JAM Property Scraper")
    parser.add_argument("--limit", type=int, help="Max properties to scrape (for testing)")
    parser.add_argument("--create-tables", action="store_true", help="Create DB tables only")
    args = parser.parse_args()

    asyncio.run(main(limit=args.limit, create_tables_only=args.create_tables))

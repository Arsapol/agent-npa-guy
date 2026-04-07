"""
SCB Production Scraper — JSON search API + HTML detail pages.

Scrapes all NPA properties from asset.home.scb, upserts into PostgreSQL,
and tracks price changes + state transitions.

Architecture:
  - Search: paginated JSON API (get_project command), 200 items/page
  - Detail: HTML pages parsed with selectolax for beds/baths/title deed
  - Detail consumer pool: 10 concurrent workers via asyncio.Semaphore
  - DB saves in batches per page

Usage:
    python scraper.py                              # full scrape (all types)
    python scraper.py --type condominiums           # single asset type
    python scraper.py --limit 50                    # first N assets (test)
    python scraper.py --skip-detail                 # search only, no detail fetch
    python scraper.py --create-tables               # create DB tables only
"""

import argparse
import asyncio
from datetime import datetime

import httpx
from sqlalchemy.orm import Session

from database import create_tables, get_engine, upsert_properties
from models import (
    ScbAssetSearch,
    ScbSearchResponse,
    ScbScrapeLog,
    parse_detail_html,
)

BASE_URL = "https://asset.home.scb"

API_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Accept": "application/json",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": f"{BASE_URL}/",
}

HTML_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Accept": "text/html",
}

PAGE_SIZE = 200
DETAIL_CONCURRENCY = 10
DETAIL_DELAY = 0.1  # 100ms between detail requests


async def _noop() -> None:
    return None


# Asset types that return results
ASSET_TYPES = [
    "condominiums",
    "townhouses",
    "single_houses",
    "duplex_homes",
    "vacant_land",
    "warehouses",
    "office_buildings",
    "factories",
    "building",
    "semi_concrete_and_wood",
    "apartment_or_dormitories",
    "hotels",
    "gas_station",
]


async def fetch_search_page(
    client: httpx.AsyncClient,
    page: int,
    asset_type: str | None = None,
) -> ScbSearchResponse:
    """Fetch one page of search results."""
    params: dict[str, str | int] = {
        "command": "get_project",
        "type": "project",
        "page": page,
        "limit": PAGE_SIZE,
    }
    if asset_type:
        params["asset-type"] = asset_type

    r = await client.get(
        f"{BASE_URL}/api/project/cmd",
        params=params,
        headers=API_HEADERS,
    )
    r.raise_for_status()
    data = r.json()
    return ScbSearchResponse(**data)


async def fetch_detail_html(
    client: httpx.AsyncClient,
    slug: str,
    semaphore: asyncio.Semaphore,
) -> str | None:
    """Fetch detail page HTML for a single property."""
    async with semaphore:
        await asyncio.sleep(DETAIL_DELAY)
        try:
            r = await client.get(
                f"{BASE_URL}/project/{slug}",
                headers=HTML_HEADERS,
            )
            if r.status_code == 200:
                return r.text
            print(f"    Detail HTTP {r.status_code} for {slug}")
            return None
        except httpx.HTTPError as e:
            print(f"    Detail error for {slug}: {e}")
            return None


async def scrape_all(
    asset_type: str | None = None,
    limit: int | None = None,
    skip_detail: bool = False,
) -> dict:
    """Run the full scrape pipeline."""
    engine = create_tables()
    started_at = datetime.now()
    stats = {
        "total_search": 0,
        "total_detail": 0,
        "new": 0,
        "updated": 0,
        "price_changed": 0,
        "state_changed": 0,
        "failed_pages": 0,
        "failed_details": 0,
    }

    types_to_scrape = [asset_type] if asset_type else [None]
    # If no type filter, scrape without filter (gets all types at once)

    semaphore = asyncio.Semaphore(DETAIL_CONCURRENCY)
    collected = 0

    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as api_client:
        async with httpx.AsyncClient(timeout=30, follow_redirects=True) as detail_client:
            for atype in types_to_scrape:
                type_label = atype or "all"
                print(f"\n--- Scraping type: {type_label} ---")

                # First page to get total
                try:
                    first_resp = await fetch_search_page(api_client, 1, atype)
                except httpx.HTTPError as e:
                    print(f"  Failed to fetch page 1: {e}")
                    stats["failed_pages"] += 1
                    continue

                total = first_resp.total
                print(f"  Total: {total}")

                if not first_resp.d:
                    continue

                total_pages = (total + PAGE_SIZE - 1) // PAGE_SIZE
                print(f"  Pages: {total_pages}")

                for page in range(1, total_pages + 1):
                    if limit and collected >= limit:
                        print(f"  Limit reached ({limit}), stopping.")
                        break

                    if page == 1:
                        resp = first_resp
                    else:
                        try:
                            resp = await fetch_search_page(api_client, page, atype)
                        except httpx.HTTPError as e:
                            print(f"  Failed page {page}: {e}")
                            stats["failed_pages"] += 1
                            continue

                    items = resp.d
                    if not items:
                        break

                    # Apply limit
                    if limit:
                        remaining = limit - collected
                        items = items[:remaining]

                    print(f"  Page {page}/{total_pages}: {len(items)} items")

                    # Parse search results
                    search_items: list[ScbAssetSearch] = []
                    for raw in items:
                        try:
                            item = ScbAssetSearch(
                                project_id=raw["project_id"],
                                **{k: v for k, v in raw.items() if k != "project_id"},
                                raw_json=raw,
                            )
                            search_items.append(item)
                        except Exception as e:
                            print(f"    Parse error: {e}")
                            continue

                    stats["total_search"] += len(search_items)

                    # Fetch details
                    pairs: list[tuple[ScbAssetSearch, ...]] = []
                    if skip_detail:
                        pairs = [(s, None) for s in search_items]
                    else:
                        detail_tasks = []
                        for s in search_items:
                            if s.slug:
                                detail_tasks.append(
                                    fetch_detail_html(detail_client, s.slug, semaphore)
                                )
                            else:
                                detail_tasks.append(_noop())

                        detail_htmls = await asyncio.gather(*detail_tasks, return_exceptions=True)

                        for s, html_result in zip(search_items, detail_htmls):
                            if isinstance(html_result, Exception):
                                stats["failed_details"] += 1
                                pairs.append((s, None))
                            elif html_result:
                                try:
                                    detail = parse_detail_html(html_result, s.project_id)
                                    stats["total_detail"] += 1
                                    pairs.append((s, detail))
                                except Exception as e:
                                    print(f"    Detail parse error for {s.slug}: {e}")
                                    stats["failed_details"] += 1
                                    pairs.append((s, None))
                            else:
                                if s.slug:
                                    stats["failed_details"] += 1
                                pairs.append((s, None))

                    # Upsert batch
                    with Session(engine) as session:
                        counts = upsert_properties(session, pairs)
                        session.commit()

                    stats["new"] += counts["new"]
                    stats["updated"] += counts["updated"]
                    stats["price_changed"] += counts["price_changed"]
                    stats["state_changed"] += counts["state_changed"]
                    collected += len(search_items)

    # Log scrape run
    finished_at = datetime.now()
    with Session(engine) as session:
        log = ScbScrapeLog(
            started_at=started_at,
            finished_at=finished_at,
            total_search=stats["total_search"],
            total_detail=stats["total_detail"],
            new_count=stats["new"],
            updated_count=stats["updated"],
            price_changed_count=stats["price_changed"],
            state_changed_count=stats["state_changed"],
            failed_pages=stats["failed_pages"],
            failed_details=stats["failed_details"],
            asset_types_scraped=asset_type or "all",
        )
        session.add(log)
        session.commit()

    duration = (finished_at - started_at).total_seconds()
    print(f"\n{'='*60}")
    print(f"SCB scrape complete in {duration:.0f}s")
    print(f"  Search: {stats['total_search']} | Detail: {stats['total_detail']}")
    print(f"  New: {stats['new']} | Updated: {stats['updated']}")
    print(f"  Price changed: {stats['price_changed']} | State changed: {stats['state_changed']}")
    print(f"  Failed pages: {stats['failed_pages']} | Failed details: {stats['failed_details']}")

    return stats


def main() -> None:
    parser = argparse.ArgumentParser(description="SCB NPA Property Scraper")
    parser.add_argument(
        "--type", type=str, default=None,
        help="Asset type to scrape (e.g. condominiums, townhouses)",
    )
    parser.add_argument(
        "--limit", type=int, default=None,
        help="Max properties to scrape (for testing)",
    )
    parser.add_argument(
        "--skip-detail", action="store_true",
        help="Skip fetching detail pages (search data only)",
    )
    parser.add_argument(
        "--create-tables", action="store_true",
        help="Create database tables and exit",
    )
    args = parser.parse_args()

    if args.create_tables:
        create_tables()
        return

    asyncio.run(scrape_all(
        asset_type=args.type,
        limit=args.limit,
        skip_detail=args.skip_detail,
    ))


if __name__ == "__main__":
    main()

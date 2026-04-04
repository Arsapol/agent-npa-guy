"""
KTB NPA Scraper — 2-phase sequential pipeline.

Scrapes all NPA properties from npa.krungthai.com API, upserts into PostgreSQL,
and tracks price changes + sale category transitions.

Architecture:
  - Phase 1: Paginate searchAll (50/page, ~54 pages)
  - Phase 2: Fetch detail for each item (POST searchSaleDetail)
  - Both share same origin → single rate limiter
  - DB saves in batches after scrape completes

Usage:
    python scraper.py                        # full scrape
    python scraper.py --limit 10             # first N assets (test)
    python scraper.py --skip-detail          # search only, no detail fetch
    python scraper.py --create-tables        # create DB tables only
    python scraper.py --province ขอนแก่น     # filter by province
"""

import argparse
import asyncio
import time
from datetime import datetime, timezone

import httpx
from sqlalchemy.orm import Session

from database import create_tables, get_engine, upsert_properties
from models import (
    KtbProperty,
    KtbSearchItem,
    KtbSearchResponse,
    KtbScrapeLog,
)

BASE_URL = "https://npa.krungthai.com/api/v1"
PROVINCE_URL = f"{BASE_URL}/system/DopaProvince/dopaProvinceListNew/detail?amphurCode=&provinceCode=&tambonCode=&zipCode="

BASE_HEADERS = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/json",
    "origin": "https://npa.krungthai.com",
    "referer": "https://npa.krungthai.com/property",
    "role": "",
    "user-id": "-",
    "user-agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/146.0.0.0 Safari/537.36"
    ),
}

PAGE_SIZE = 50
DETAIL_CONCURRENCY = 20
DETAIL_DELAY = 0.05

# Rate limiter for search only — detail uses concurrency control
RATE_WINDOW_SIZE = 100
RATE_WINDOW_SECONDS = 60.0


# ---------------------------------------------------------------------------
# Rate limiter
# ---------------------------------------------------------------------------


class SlidingWindowLimiter:
    """Sliding window rate limiter. Sleeps when window is full."""

    def __init__(self, max_requests: int, window_seconds: float):
        self._max = max_requests
        self._window = window_seconds
        self._timestamps: list[float] = []

    async def acquire(self) -> None:
        now = time.monotonic()
        cutoff = now - self._window
        self._timestamps = [t for t in self._timestamps if t > cutoff]

        if len(self._timestamps) >= self._max:
            wait = self._timestamps[0] - cutoff
            if wait > 0:
                await asyncio.sleep(wait)

        self._timestamps.append(time.monotonic())

    @property
    def count(self) -> int:
        now = time.monotonic()
        cutoff = now - self._window
        return sum(1 for t in self._timestamps if t > cutoff)


# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------


async def fetch_with_retry(
    client: httpx.AsyncClient,
    method: str,
    url: str,
    json_body: dict | None = None,
    max_retries: int = 2,
    base_delay: float = 10.0,
) -> dict | list | None:
    for attempt in range(max_retries + 1):
        try:
            if method == "POST":
                resp = await client.post(url, json=json_body, headers=BASE_HEADERS)
            else:
                resp = await client.get(url, headers=BASE_HEADERS)
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code >= 500 and attempt < max_retries:
                delay = base_delay * (2 ** attempt)
                print(f"    Server {e.response.status_code}, retry {attempt + 1}/{max_retries} in {delay:.0f}s...")
                await asyncio.sleep(delay)
            else:
                print(f"    HTTP {e.response.status_code} for {url}")
                return None
        except (httpx.ReadTimeout, httpx.ConnectTimeout):
            if attempt < max_retries:
                delay = base_delay * (2 ** attempt)
                print(f"    Timeout, retry {attempt + 1}/{max_retries} in {delay:.0f}s...")
                await asyncio.sleep(delay)
            else:
                return None
        except Exception as e:
            if attempt < max_retries:
                delay = base_delay * (2 ** attempt)
                print(f"    Error: {e}, retry {attempt + 1}/{max_retries} in {delay:.0f}s...")
                await asyncio.sleep(delay)
            else:
                return None
    return None


# ---------------------------------------------------------------------------
# Phase 1: Search
# ---------------------------------------------------------------------------


async def resolve_province_codes(
    client: httpx.AsyncClient,
    names: list[str],
) -> list[tuple[str, str]]:
    """Resolve Thai province names to API codes. Returns list of (code, name)."""
    data = await fetch_with_retry(client, "GET", PROVINCE_URL)
    if not data or not isinstance(data, dict):
        return []
    provinces = data.get("data", [])
    name_to_code = {p["text"]: p["value"] for p in provinces}

    results = []
    for name in names:
        if name in name_to_code:
            results.append((name_to_code[name], name))
        else:
            # Partial match
            matches = [(v, k) for k, v in name_to_code.items() if name in k]
            if matches:
                results.append(matches[0])
                print(f"  Province '{name}' matched to '{matches[0][1]}' (code {matches[0][0]})")
            else:
                print(f"  WARNING: Province '{name}' not found, skipping")
    return results


def parse_search_items(items: list[dict]) -> list[KtbSearchItem]:
    parsed = []
    for item in items:
        try:
            p = KtbSearchItem.model_validate(item)
            p.raw_json = item
            parsed.append(p)
        except Exception as e:
            gid = item.get("collGrpId", "?")
            print(f"    Parse error for collGrpId {gid}: {e}")
    return parsed


async def search_all(
    client: httpx.AsyncClient,
    limiter: SlidingWindowLimiter,
    province_code: str | None = None,
    max_assets: int | None = None,
) -> tuple[list[KtbSearchItem], int]:
    """Paginate searchAll, returns (items, fail_count)."""
    all_items: list[KtbSearchItem] = []
    seen_ids: set[int] = set()
    fail_count = 0

    body: dict = {
        "paging": {"totalRows": 0, "rowsPerPage": PAGE_SIZE, "currentPage": 1},
    }
    if province_code:
        body["shrProvince"] = province_code

    await limiter.acquire()
    data = await fetch_with_retry(client, "POST", f"{BASE_URL}/product/searchAll", body)
    if not data:
        print("  FATAL: Failed to fetch first page")
        return [], 1

    resp = KtbSearchResponse.model_validate(data)
    total = resp.total_rows
    total_pages = (total + PAGE_SIZE - 1) // PAGE_SIZE
    print(f"  Total: {total:,} properties across {total_pages} pages")

    for item in parse_search_items(resp.data_response):
        if item.coll_grp_id not in seen_ids:
            seen_ids.add(item.coll_grp_id)
            all_items.append(item)

    for page in range(2, total_pages + 1):
        if max_assets and len(all_items) >= max_assets:
            all_items = all_items[:max_assets]
            print(f"  Reached limit ({max_assets}), stopping search")
            break

        body["paging"]["currentPage"] = page
        await limiter.acquire()
        data = await fetch_with_retry(client, "POST", f"{BASE_URL}/product/searchAll", body)

        if not data:
            fail_count += 1
            continue

        resp = KtbSearchResponse.model_validate(data)
        new_items = parse_search_items(resp.data_response)
        for item in new_items:
            if item.coll_grp_id not in seen_ids:
                seen_ids.add(item.coll_grp_id)
                all_items.append(item)

        if page % 10 == 0 or page == total_pages:
            print(
                f"  Page {page}/{total_pages}: {len(all_items):,} items "
                f"[rate: {limiter.count}/{RATE_WINDOW_SIZE}]"
            )

    return all_items, fail_count


# ---------------------------------------------------------------------------
# Phase 2: Detail
# ---------------------------------------------------------------------------


async def fetch_detail(
    client: httpx.AsyncClient,
    search_item: KtbSearchItem,
) -> KtbSearchItem | None:
    """Fetch detail for a single property. No rate limiter — uses concurrency control only."""
    body = {
        "speedDy": search_item.is_speedy or 0,
        "collGrpId": str(search_item.coll_grp_id),
        "cateNo": search_item.cate_no or 1,
    }
    data = await fetch_with_retry(client, "POST", f"{BASE_URL}/product/searchSaleDetail", body)
    if not data:
        return None

    items = data if isinstance(data, list) else [data]
    if not items:
        return None

    try:
        detail = KtbSearchItem.model_validate(items[0])
        detail.raw_json = items[0]
        return detail
    except Exception as e:
        print(f"    Detail parse error for {search_item.coll_grp_id}: {e}")
        return None


async def fetch_details_batch(
    search_items: list[KtbSearchItem],
) -> tuple[dict[int, KtbSearchItem | None], int, int]:
    """Fetch details for all items with bounded concurrency (no rate limiter)."""
    results: dict[int, KtbSearchItem | None] = {}
    sem = asyncio.Semaphore(DETAIL_CONCURRENCY)
    ok_count = 0
    fail_count = 0

    async def fetch_one(item: KtbSearchItem) -> None:
        nonlocal ok_count, fail_count
        async with sem:
            async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
                detail = await fetch_detail(client, item)
            results[item.coll_grp_id] = detail
            if detail:
                ok_count += 1
            else:
                fail_count += 1
            await asyncio.sleep(DETAIL_DELAY)

    tasks = [asyncio.create_task(fetch_one(item)) for item in search_items]

    total = len(tasks)
    done = 0
    for coro in asyncio.as_completed(tasks):
        await coro
        done += 1
        if done % 50 == 0 or done == total:
            print(
                f"  Detail: {done}/{total} ({ok_count} ok, {fail_count} fail)"
            )

    return results, ok_count, fail_count


# ---------------------------------------------------------------------------
# DB save
# ---------------------------------------------------------------------------


def save_to_db(
    items: list[tuple[KtbSearchItem, KtbSearchItem | None]],
    page_fails: int,
    detail_fails: int,
    started_at: datetime,
) -> dict[str, int]:
    engine = get_engine()
    batch_size = 500
    total_counts = {"new": 0, "updated": 0, "price_changed": 0, "category_changed": 0}

    with Session(engine) as session:
        for i in range(0, len(items), batch_size):
            batch = items[i: i + batch_size]
            counts = upsert_properties(session, batch)
            for k, v in counts.items():
                total_counts[k] += v
            session.flush()

            end = min(i + batch_size, len(items))
            print(f"    DB batch {end}/{len(items)}: {total_counts}")

        log = KtbScrapeLog(
            started_at=started_at,
            finished_at=datetime.now(timezone.utc),
            total_search=len(items),
            total_detail=sum(1 for _, d in items if d is not None),
            new_count=total_counts["new"],
            updated_count=total_counts["updated"],
            price_changed_count=total_counts["price_changed"],
            category_changed_count=total_counts["category_changed"],
            failed_pages=page_fails,
            failed_details=detail_fails,
        )
        session.add(log)
        session.commit()

    return total_counts


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


async def main(
    provinces: list[str] | None = None,
    limit: int | None = None,
    skip_detail: bool = False,
    create_tables_only: bool = False,
):
    if create_tables_only:
        create_tables()
        return

    started_at = datetime.now(timezone.utc)
    print(f"=== KTB Scraper — {started_at.isoformat()} ===\n")

    create_tables()

    limiter = SlidingWindowLimiter(RATE_WINDOW_SIZE, RATE_WINDOW_SECONDS)

    # Resolve province names to codes
    targets: list[tuple[str | None, str | None]] = [(None, None)]
    if provinces:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            resolved = await resolve_province_codes(client, provinces)
        if not resolved:
            print("  FATAL: Could not resolve any provinces")
            return
        targets = resolved
        print(f"  Resolved {len(resolved)} province(s): {', '.join(n for _, n in resolved)}\n")

    # Phase 1: Search (loop over provinces if specified, else scrape all)
    all_search: list[KtbSearchItem] = []
    page_fails = 0

    print(f"1. Scraping search results ({len(targets)} target(s))...")
    for code, name in targets:
        if name:
            print(f"\n  --- {name} (code={code}) ---")
        async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
            items, fails = await search_all(client, limiter, province_code=code, max_assets=limit)
        all_search.extend(items)
        page_fails += fails

    if not all_search:
        print("  No properties found — aborting")
        return

    print(f"\n  Search complete: {len(all_search):,} properties ({page_fails} page fails)")

    # Phase 2: Detail
    detail_results: dict[int, KtbSearchItem | None] = {}
    detail_fails = 0

    if not skip_detail:
        print(f"\n2. Fetching details for {len(all_search):,} properties...")
        detail_results, detail_ok, detail_fails = await fetch_details_batch(all_search)
        print(f"  Details: {detail_ok} ok, {detail_fails} failed")

    # Merge search + detail
    merged: list[tuple[KtbSearchItem, KtbSearchItem | None]] = [
        (s, detail_results.get(s.coll_grp_id)) for s in all_search
    ]

    # Phase 3: Save to DB
    print(f"\n3. Saving {len(merged):,} properties to database...")
    counts = save_to_db(merged, page_fails, detail_fails, started_at)

    elapsed = (datetime.now(timezone.utc) - started_at).total_seconds()
    print(f"\n=== Done in {elapsed:.0f}s ({elapsed / 60:.1f}m) ===")
    print(f"  New: {counts['new']:,}")
    print(f"  Updated: {counts['updated']:,}")
    print(f"  Price changed: {counts['price_changed']:,}")
    print(f"  Category changed: {counts['category_changed']:,}")
    print(f"  Page fails: {page_fails}")
    print(f"  Detail fails: {detail_fails}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="KTB NPA Property Scraper")
    parser.add_argument("--province", type=str, nargs="+", help="Province(s) to scrape (Thai name, space-separated)")
    parser.add_argument("--limit", type=int, help="Max assets to scrape per province (for testing)")
    parser.add_argument("--skip-detail", action="store_true", help="Skip detail endpoint (faster)")
    parser.add_argument("--create-tables", action="store_true", help="Create DB tables only")
    args = parser.parse_args()

    asyncio.run(
        main(
            provinces=args.province,
            limit=args.limit,
            skip_detail=args.skip_detail,
            create_tables_only=args.create_tables,
        )
    )

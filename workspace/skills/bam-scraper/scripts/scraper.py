"""
BAM Production Scraper (v2 — interleaved search + detail)

Scrapes all NPA properties from bam.co.th API, upserts into PostgreSQL,
and tracks price changes + state transitions.

Architecture:
  - Search producer: sequential with sliding-window rate limiter (~30 req/min)
  - Detail consumer pool: 20 concurrent workers on separate client
  - Both run simultaneously via asyncio.Queue
  - DB saves stream in batches during scrape, not after

Usage:
    python scraper.py                              # full scrape (all provinces)
    python scraper.py --province กรุงเทพมหานคร      # single province
    python scraper.py --limit 100                   # first N assets (test)
    python scraper.py --skip-detail                 # search only, no detail fetch
    python scraper.py --create-tables               # create DB tables only
"""

import argparse
import asyncio
import time
from datetime import datetime, timedelta

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import create_tables, get_engine, upsert_properties
from models import (
    BamAssetDetail,
    BamAssetSearch,
    BamProperty,
    BamScrapeLog,
    BamSearchResponse,
)

BASE_HEADERS = {
    "accept": "application/json, text/plain, */*",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/json",
    "origin": "https://www.bam.co.th",
    "referer": "https://www.bam.co.th/",
    "user-agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/146.0.0.0 Safari/537.36"
    ),
}

SEARCH_URL = "https://bam-els-sync-api-prd.bam.co.th/api/asset-detail/search"
PROVINCE_URL = "https://bam-bo-api-prd.bam.co.th/master/province/filter"
DISTRICT_URL = "https://bam-bo-api-prd.bam.co.th/master/District/Dropdown/find"
DETAIL_URL = "https://bam-bo-api-prd.bam.co.th/property-detail/getExpiredSubscriptionDateTimeByAssetId"

PAGE_SIZE = 50
DETAIL_CONCURRENCY = 20
DETAIL_DELAY = 0.05  # 50ms between detail requests (20 concurrent = ~400 req/s peak, but IO-bound)
MAX_SEARCH_RESULTS = 1600  # BAM API silently caps results

# Sliding window rate limiter for search endpoint
SEARCH_WINDOW_SIZE = 28  # max requests in window (under ~30 limit)
SEARCH_WINDOW_SECONDS = 60.0  # window duration


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
        # Purge old timestamps
        cutoff = now - self._window
        self._timestamps = [t for t in self._timestamps if t > cutoff]

        if len(self._timestamps) >= self._max:
            # Wait until oldest entry expires
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


async def _do_request(
    client: httpx.AsyncClient,
    method: str,
    url: str,
    json_body: dict | None = None,
) -> httpx.Response:
    if method == "POST":
        return await client.post(url, json=json_body, headers=BASE_HEADERS)
    return await client.get(url, headers=BASE_HEADERS)


async def fetch_with_retry(
    client: httpx.AsyncClient,
    method: str,
    url: str,
    json_body: dict | None = None,
    max_retries: int = 2,
    base_delay: float = 10.0,
) -> dict | None:
    for attempt in range(max_retries):
        try:
            resp = await _do_request(client, method, url, json_body)
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code >= 500:
                delay = base_delay * (2**attempt)
                short_url = url.split("/")[-1][:30]
                print(
                    f"    Server {e.response.status_code} on {short_url}, "
                    f"retry {attempt + 1}/{max_retries} in {delay:.0f}s..."
                )
                await asyncio.sleep(delay)
            else:
                print(f"    HTTP {e.response.status_code} for {url}")
                return None
        except (httpx.ReadTimeout, httpx.ConnectTimeout):
            delay = base_delay * (2**attempt)
            print(f"    Timeout, retry {attempt + 1}/{max_retries} in {delay:.0f}s...")
            await asyncio.sleep(delay)
        except Exception as e:
            delay = base_delay * (2**attempt)
            print(f"    Error: {e}, retry {attempt + 1}/{max_retries} in {delay:.0f}s...")
            await asyncio.sleep(delay)
    return None


def _search_body(province: str = "", district: str = "", page: int = 1) -> dict:
    return {
        "pageSize": PAGE_SIZE,
        "pageNumber": page,
        "inputText": "",
        "assetType": "",
        "bedroom": "",
        "bathroom": "",
        "startMeter": "",
        "endMeter": "",
        "province": province,
        "district": district,
        "firstPriceRange": "",
        "secondPriceRange": "",
        "thirdPriceRange": "",
        "fourthPriceRange": "",
        "sortby": "",
        "startTwoMeter": "",
        "endTwoMeter": "",
        "nearby": [],
        "isHotDeal": "",
        "isCampaign": "",
        "campaignName": "",
        "stars": "",
        "isCenterPrice": "",
        "isSpecialPrice": "",
        "isShockPrice": "",
        "isFourthPrice": "",
        "userKey": "",
        "smartSearch": None,
        "semanticSearch": None,
    }


# ---------------------------------------------------------------------------
# Search producer
# ---------------------------------------------------------------------------


async def fetch_provinces(client: httpx.AsyncClient) -> list[str]:
    data = await fetch_with_retry(client, "POST", PROVINCE_URL, {"text": ""})
    if not data or not isinstance(data, list):
        return []
    return [p["value"] for p in data if "value" in p]


async def fetch_districts(client: httpx.AsyncClient, province: str) -> list[str]:
    data = await fetch_with_retry(client, "POST", DISTRICT_URL, {"province": province})
    if not data or not isinstance(data, list):
        return []
    return [d["value"] for d in data if "value" in d]


def parse_search_items(items: list[dict]) -> list[BamAssetSearch]:
    parsed = []
    for item in items:
        try:
            p = BamAssetSearch.model_validate(item)
            p.raw_json = item
            parsed.append(p)
        except Exception as e:
            aid = item.get("id", "?")
            print(f"    Parse error for asset {aid}: {e}")
    return parsed


async def search_page(
    client: httpx.AsyncClient,
    limiter: SlidingWindowLimiter,
    province: str,
    page: int,
    district: str = "",
) -> tuple[list[dict], int]:
    """Search one page, respecting rate limit. Returns (items, totalData)."""
    await limiter.acquire()
    body = _search_body(province=province, district=district, page=page)
    data = await fetch_with_retry(client, "POST", SEARCH_URL, body)
    if not data:
        return [], 0
    resp = BamSearchResponse.model_validate(data)
    return resp.data, resp.total_data


async def scrape_search_partition(
    client: httpx.AsyncClient,
    limiter: SlidingWindowLimiter,
    province: str,
    district: str = "",
    seen_ids: set[int] | None = None,
    detail_queue: asyncio.Queue | None = None,
) -> tuple[list[BamAssetSearch], int]:
    """Scrape all search pages for a partition. Pushes discovered assets to detail_queue."""
    if seen_ids is None:
        seen_ids = set()
    all_search: list[BamAssetSearch] = []
    fail_count = 0

    items, total = await search_page(client, limiter, province, 1, district=district)
    if total == 0:
        return [], 0

    for p in parse_search_items(items):
        if p.id not in seen_ids:
            seen_ids.add(p.id)
            all_search.append(p)
            if detail_queue:
                await detail_queue.put(p)

    total_pages = min(
        (total + PAGE_SIZE - 1) // PAGE_SIZE, MAX_SEARCH_RESULTS // PAGE_SIZE
    )

    for page in range(2, total_pages + 1):
        items, _ = await search_page(client, limiter, province, page, district=district)
        if items:
            for p in parse_search_items(items):
                if p.id not in seen_ids:
                    seen_ids.add(p.id)
                    all_search.append(p)
                    if detail_queue:
                        await detail_queue.put(p)
        else:
            fail_count += 1

    return all_search, fail_count


async def search_producer(
    provinces: list[str],
    detail_queue: asyncio.Queue,
    skip_detail: bool = False,
    max_assets: int | None = None,
) -> tuple[list[BamAssetSearch], int]:
    """
    Search all provinces, push discovered assets to detail_queue.
    Returns (all_search_items, total_page_fails).
    """
    limiter = SlidingWindowLimiter(SEARCH_WINDOW_SIZE, SEARCH_WINDOW_SECONDS)
    all_search: list[BamAssetSearch] = []
    total_fails = 0
    seen_ids: set[int] = set()

    for i, prov in enumerate(provinces):
        async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
            # Check total
            _, total = await search_page(client, limiter, prov, 1)

            prov_items: list[BamAssetSearch] = []
            prov_fails = 0

            if total > MAX_SEARCH_RESULTS:
                # Drill down by district
                districts = await fetch_districts(client, prov)
                for dist in districts:
                    items, fails = await scrape_search_partition(
                        client,
                        limiter,
                        prov,
                        district=dist,
                        seen_ids=seen_ids,
                        detail_queue=detail_queue if not skip_detail else None,
                    )
                    prov_items.extend(items)
                    prov_fails += fails
                    if items:
                        print(f"    {dist}: {len(items)} assets")
            else:
                items, fails = await scrape_search_partition(
                    client,
                    limiter,
                    prov,
                    seen_ids=seen_ids,
                    detail_queue=detail_queue if not skip_detail else None,
                )
                prov_items.extend(items)
                prov_fails += fails

        all_search.extend(prov_items)
        total_fails += prov_fails

        if prov_items:
            print(
                f"  [{i + 1}/{len(provinces)}] {prov}: "
                f"{len(prov_items)} assets ({prov_fails} page fails) "
                f"[rate: {limiter.count}/{SEARCH_WINDOW_SIZE} in window]"
            )

        if max_assets and len(all_search) >= max_assets:
            all_search = all_search[:max_assets]
            print(f"  Reached limit ({max_assets}), stopping search")
            break

    return all_search, total_fails


# ---------------------------------------------------------------------------
# Detail consumer pool
# ---------------------------------------------------------------------------


async def detail_consumer(
    queue: asyncio.Queue,
    results: dict[int, BamAssetDetail | None],
    skip_ids: set[int],
    stats: dict[str, int],
) -> None:
    """
    Worker pool: consume asset IDs from queue, fetch details concurrently.
    Runs until it receives None sentinel.
    """
    sem = asyncio.Semaphore(DETAIL_CONCURRENCY)
    pending: set[asyncio.Task] = set()

    async def fetch_one(search_item: BamAssetSearch) -> None:
        async with sem:
            if search_item.id in skip_ids:
                stats["skipped"] += 1
                return
            async with httpx.AsyncClient(timeout=60.0) as client:
                detail = await fetch_detail(client, search_item.id)
            results[search_item.id] = detail
            if detail:
                stats["ok"] += 1
            else:
                stats["fail"] += 1
            await asyncio.sleep(DETAIL_DELAY)

    while True:
        item = await queue.get()
        if item is None:
            break
        task = asyncio.create_task(fetch_one(item))
        pending.add(task)
        task.add_done_callback(pending.discard)

    # Wait for remaining tasks
    if pending:
        await asyncio.gather(*pending, return_exceptions=True)


async def fetch_detail(
    client: httpx.AsyncClient,
    asset_id: int,
) -> BamAssetDetail | None:
    data = await fetch_with_retry(client, "GET", f"{DETAIL_URL}/{asset_id}")
    if not data:
        return None
    try:
        return BamAssetDetail.model_validate(data)
    except Exception as e:
        print(f"    Detail parse error for {asset_id}: {e}")
        return None


# ---------------------------------------------------------------------------
# DB helpers
# ---------------------------------------------------------------------------


def load_recent_detail_ids(max_age_hours: int = 24) -> set[int]:
    """Load asset IDs that already have detail data scraped recently."""
    engine = get_engine()
    cutoff = datetime.now() - timedelta(hours=max_age_hours)
    with Session(engine) as session:
        stmt = (
            select(BamProperty.id)
            .where(BamProperty.has_detail.is_(True))
            .where(BamProperty.last_scraped_at >= cutoff)
        )
        return {row[0] for row in session.execute(stmt)}


def save_to_db(
    items: list[tuple[BamAssetSearch, BamAssetDetail | None]],
    page_fails: int,
    detail_fails: int,
    detail_skipped: int,
    started_at: datetime,
    provinces_scraped: str,
) -> dict[str, int]:
    engine = get_engine()
    batch_size = 500
    total_counts = {"new": 0, "updated": 0, "price_changed": 0, "state_changed": 0}

    with Session(engine) as session:
        for i in range(0, len(items), batch_size):
            batch = items[i : i + batch_size]
            counts = upsert_properties(session, batch)
            for k, v in counts.items():
                total_counts[k] += v
            session.flush()

            if (i + batch_size) % 2000 == 0 or i + batch_size >= len(items):
                print(
                    f"    DB batch {min(i + batch_size, len(items))}/{len(items)}: {total_counts}"
                )

        log = BamScrapeLog(
            started_at=started_at,
            finished_at=datetime.now(),
            total_api=len(items),
            total_detail=sum(1 for _, d in items if d is not None),
            new_count=total_counts["new"],
            updated_count=total_counts["updated"],
            price_changed_count=total_counts["price_changed"],
            state_changed_count=total_counts["state_changed"],
            failed_pages=page_fails,
            failed_details=detail_fails,
            provinces_scraped=provinces_scraped,
        )
        session.add(log)
        session.commit()

    return total_counts


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


async def main(
    province: str | None = None,
    limit: int | None = None,
    skip_detail: bool = False,
    create_tables_only: bool = False,
):
    if create_tables_only:
        create_tables()
        return

    started_at = datetime.now()
    print(f"=== BAM Scraper v2 — {started_at.isoformat()} ===\n")

    create_tables()

    # Resolve provinces
    if province:
        provinces = [province]
    else:
        async with httpx.AsyncClient(timeout=30.0) as tmp:
            provinces = await fetch_provinces(tmp)
        if not provinces:
            print("  FATAL: Failed to fetch provinces")
            return
    print(f"  {len(provinces)} province(s) to scrape")

    # Load recently-detailed IDs to skip
    skip_ids: set[int] = set()
    if not skip_detail:
        try:
            skip_ids = load_recent_detail_ids(max_age_hours=24)
            if skip_ids:
                print(f"  Skipping detail for {len(skip_ids)} recently-scraped assets")
        except Exception:
            pass  # first run, table might not exist yet

    # Set up interleaved pipeline
    detail_queue: asyncio.Queue[BamAssetSearch | None] = asyncio.Queue(maxsize=200)
    detail_results: dict[int, BamAssetDetail | None] = {}
    detail_stats = {"ok": 0, "fail": 0, "skipped": 0}

    # Start detail consumer (runs in background)
    detail_task = None
    if not skip_detail:
        detail_task = asyncio.create_task(
            detail_consumer(detail_queue, detail_results, skip_ids, detail_stats)
        )

    # Run search producer (blocks until all provinces scraped)
    print("\n1. Scraping (search + detail interleaved)...")
    all_search, page_fails = await search_producer(
        provinces, detail_queue, skip_detail=skip_detail, max_assets=limit
    )

    # Signal detail consumer to finish
    if detail_task:
        await detail_queue.put(None)
        print(
            f"\n  Search done ({len(all_search):,} assets). "
            f"Waiting for {detail_queue.qsize()} remaining details..."
        )
        await detail_task
        print(
            f"  Details: {detail_stats['ok']} ok, "
            f"{detail_stats['fail']} failed, "
            f"{detail_stats['skipped']} skipped"
        )

    # Merge search + detail
    merged: list[tuple[BamAssetSearch, BamAssetDetail | None]] = [
        (s, detail_results.get(s.id)) for s in all_search
    ]

    if not merged:
        print("   No properties scraped — aborting DB save")
        return

    # Save to DB
    print("\n2. Saving to database...")
    prov_str = province or "all"
    detail_fails = detail_stats["fail"]
    counts = save_to_db(
        merged, page_fails, detail_fails, detail_stats["skipped"], started_at, prov_str
    )

    elapsed = (datetime.now() - started_at).total_seconds()
    print(f"\n=== Done in {elapsed:.0f}s ({elapsed / 60:.1f}m) ===")
    print(f"   New: {counts['new']:,}")
    print(f"   Updated: {counts['updated']:,}")
    print(f"   Price changed: {counts['price_changed']:,}")
    print(f"   State changed: {counts['state_changed']:,}")
    print(f"   Page fails: {page_fails}")
    print(f"   Detail: {detail_stats['ok']} ok, {detail_fails} failed, {detail_stats['skipped']} skipped")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="BAM NPA Property Scraper")
    parser.add_argument("--province", type=str, help="Scrape single province (Thai name)")
    parser.add_argument("--limit", type=int, help="Max assets to scrape (for testing)")
    parser.add_argument(
        "--skip-detail", action="store_true", help="Skip detail endpoint (faster)"
    )
    parser.add_argument(
        "--create-tables", action="store_true", help="Create DB tables only"
    )
    args = parser.parse_args()

    asyncio.run(
        main(
            province=args.province,
            limit=args.limit,
            skip_detail=args.skip_detail,
            create_tables_only=args.create_tables,
        )
    )

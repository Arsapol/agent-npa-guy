"""
BAM Production Scraper

Scrapes all NPA properties from bam.co.th API, upserts into PostgreSQL,
and tracks price changes + state transitions.

Usage:
    python scraper.py                              # full scrape (all provinces)
    python scraper.py --province กรุงเทพมหานคร      # single province
    python scraper.py --limit 100                   # first N assets (test)
    python scraper.py --skip-detail                 # search only, no detail fetch
    python scraper.py --create-tables               # create DB tables only
"""

import argparse
import asyncio
from datetime import datetime, timezone

import httpx
from database import create_tables, get_engine, upsert_properties
from models import BamAssetDetail, BamAssetSearch, BamScrapeLog, BamSearchResponse
from sqlalchemy.orm import Session

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
DETAIL_CONCURRENCY = 5
SEARCH_DELAY = 2.5  # seconds between search requests (BAM rate limit ~30/min)


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
                    f"    Server {e.response.status_code} on {short_url}, retry {attempt + 1}/{max_retries} in {delay:.0f}s..."
                )
                await asyncio.sleep(delay)
                # On 500, retry with a fresh client to reset connection
                if attempt >= 1:
                    try:
                        async with httpx.AsyncClient(timeout=60.0) as fresh:
                            resp = await _do_request(fresh, method, url, json_body)
                            resp.raise_for_status()
                            return resp.json()
                    except Exception:
                        continue
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


async def fetch_provinces(client: httpx.AsyncClient) -> list[str]:
    """Fetch all province names."""
    data = await fetch_with_retry(client, "POST", PROVINCE_URL, {"text": ""})
    if not data or not isinstance(data, list):
        return []
    return [p["value"] for p in data if "value" in p]


async def fetch_districts(client: httpx.AsyncClient, province: str) -> list[str]:
    """Fetch district names for a province."""
    data = await fetch_with_retry(
        client, "POST", DISTRICT_URL, {"province": province}
    )
    if not data or not isinstance(data, list):
        return []
    return [d["value"] for d in data if "value" in d]


_search_request_count = 0


async def search_page(
    client: httpx.AsyncClient,
    province: str,
    page: int,
    district: str = "",
) -> tuple[list[dict], int]:
    """Search one page. Returns (items, totalData)."""
    global _search_request_count
    _search_request_count += 1
    await asyncio.sleep(SEARCH_DELAY)
    body = _search_body(province=province, district=district, page=page)
    data = await fetch_with_retry(client, "POST", SEARCH_URL, body)
    if not data:
        return [], 0
    resp = BamSearchResponse.model_validate(data)
    return resp.data, resp.total_data


async def fetch_detail(
    client: httpx.AsyncClient,
    asset_id: int,
) -> BamAssetDetail | None:
    """Fetch detail for a single asset."""
    data = await fetch_with_retry(client, "GET", f"{DETAIL_URL}/{asset_id}")
    if not data:
        return None
    try:
        return BamAssetDetail.model_validate(data)
    except Exception as e:
        print(f"    Detail parse error for {asset_id}: {e}")
        return None


def parse_search_items(items: list[dict]) -> list[BamAssetSearch]:
    """Parse raw search items into Pydantic models."""
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


MAX_SEARCH_RESULTS = 1600  # BAM API silently caps results at ~1600


async def _scrape_search_partition(
    client: httpx.AsyncClient,
    province: str,
    district: str = "",
    seen_ids: set[int] | None = None,
) -> tuple[list[BamAssetSearch], int]:
    """Scrape all search pages for a province+district partition. Returns (items, fail_count)."""
    if seen_ids is None:
        seen_ids = set()
    all_search: list[BamAssetSearch] = []
    fail_count = 0

    items, total = await search_page(client, province, 1, district=district)
    if total == 0:
        return [], 0

    for p in parse_search_items(items):
        if p.id not in seen_ids:
            seen_ids.add(p.id)
            all_search.append(p)

    total_pages = min((total + PAGE_SIZE - 1) // PAGE_SIZE, MAX_SEARCH_RESULTS // PAGE_SIZE)

    for page in range(2, total_pages + 1):
        await asyncio.sleep(SEARCH_DELAY)
        items, _ = await search_page(client, province, page, district=district)
        if items:
            for p in parse_search_items(items):
                if p.id not in seen_ids:
                    seen_ids.add(p.id)
                    all_search.append(p)
        else:
            fail_count += 1

    return all_search, fail_count


async def scrape_province(
    client: httpx.AsyncClient,
    province: str,
    skip_detail: bool = False,
) -> tuple[list[tuple[BamAssetSearch, BamAssetDetail | None]], int, int]:
    """
    Scrape all assets for a province.
    Drills down by district if province has >1600 assets (API cap).
    Returns (merged_items, page_fail_count, detail_fail_count).
    """
    seen_ids: set[int] = set()
    all_search: list[BamAssetSearch] = []
    fail_count = 0

    # Check total for this province
    _, total = await search_page(client, province, 1)

    if total > MAX_SEARCH_RESULTS:
        # Drill down by district
        districts = await fetch_districts(client, province)
        if not districts:
            print(f"    WARN: no districts for {province}, scraping province-level only")
            items, fails = await _scrape_search_partition(client, province, seen_ids=seen_ids)
            all_search.extend(items)
            fail_count += fails
        else:
            for dist in districts:
                await asyncio.sleep(SEARCH_DELAY)
                items, fails = await _scrape_search_partition(
                    client, province, district=dist, seen_ids=seen_ids
                )
                all_search.extend(items)
                fail_count += fails
                if items:
                    print(f"    {dist}: {len(items)} assets")
    else:
        items, fails = await _scrape_search_partition(client, province, seen_ids=seen_ids)
        all_search.extend(items)
        fail_count += fails

    # Fetch details
    detail_fails = 0
    if skip_detail:
        return [(s, None) for s in all_search], fail_count, 0

    detail_sem = asyncio.Semaphore(DETAIL_CONCURRENCY)
    detail_map: dict[int, BamAssetDetail | None] = {}

    async def fetch_one_detail(asset_id: int) -> None:
        async with detail_sem:
            detail_map[asset_id] = await fetch_detail(client, asset_id)
            await asyncio.sleep(0.2)

    ids = [s.id for s in all_search]
    for i in range(0, len(ids), DETAIL_CONCURRENCY):
        batch = ids[i : i + DETAIL_CONCURRENCY]
        await asyncio.gather(*[fetch_one_detail(aid) for aid in batch])
        await asyncio.sleep(0.3)

    detail_fails = sum(1 for v in detail_map.values() if v is None)
    merged = [(s, detail_map.get(s.id)) for s in all_search]

    return merged, fail_count, detail_fails


async def scrape_all(
    target_province: str | None = None,
    max_assets: int | None = None,
    skip_detail: bool = False,
) -> tuple[list[tuple[BamAssetSearch, BamAssetDetail | None]], int, int]:
    """
    Scrape all provinces (or one).
    Returns (merged_items, total_page_fails, total_detail_fails).
    """
    all_items: list[tuple[BamAssetSearch, BamAssetDetail | None]] = []
    total_page_fails = 0
    total_detail_fails = 0

    # Fetch province list with a throwaway client
    if target_province:
        provinces = [target_province]
    else:
        async with httpx.AsyncClient(timeout=30.0) as tmp:
            provinces = await fetch_provinces(tmp)
        if not provinces:
            print("  FATAL: Failed to fetch provinces")
            return all_items, 1, 0
    print(f"  {len(provinces)} province(s) to scrape\n")

    for i, prov in enumerate(provinces):
        # Fresh client per province to avoid connection pool issues
        async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
            items, page_fails, detail_fails = await scrape_province(
                client, prov, skip_detail=skip_detail
            )

        all_items.extend(items)
        total_page_fails += page_fails
        total_detail_fails += detail_fails

        if items:
            detail_ok = sum(1 for _, d in items if d is not None)
            print(
                f"  [{i + 1}/{len(provinces)}] {prov}: "
                f"{len(items)} assets, {detail_ok} details "
                f"({page_fails} page fails, {detail_fails} detail fails)"
            )

        # Pause between provinces to avoid rate limiting
        if i < len(provinces) - 1:
            await asyncio.sleep(3.0)

        if max_assets and len(all_items) >= max_assets:
            all_items = all_items[:max_assets]
            print(f"  Reached limit ({max_assets}), stopping")
            break

    print(
        f"\n  Total: {len(all_items):,} assets, {total_page_fails} page fails, {total_detail_fails} detail fails"
    )
    return all_items, total_page_fails, total_detail_fails


def save_to_db(
    items: list[tuple[BamAssetSearch, BamAssetDetail | None]],
    page_fails: int,
    detail_fails: int,
    started_at: datetime,
    provinces_scraped: str,
) -> dict[str, int]:
    """Upsert properties into database with price tracking."""
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
            finished_at=datetime.now(timezone.utc),
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


async def main(
    province: str | None = None,
    limit: int | None = None,
    skip_detail: bool = False,
    create_tables_only: bool = False,
):
    if create_tables_only:
        create_tables()
        return

    global _search_request_count
    _search_request_count = 0

    started_at = datetime.now(timezone.utc)
    print(f"=== BAM Scraper — {started_at.isoformat()} ===\n")

    create_tables()

    print("\n1. Scraping API...")
    items, page_fails, detail_fails = await scrape_all(
        target_province=province,
        max_assets=limit,
        skip_detail=skip_detail,
    )

    if not items:
        print("   No properties scraped — aborting DB save")
        return

    print("\n2. Saving to database...")
    prov_str = province or "all"
    counts = save_to_db(items, page_fails, detail_fails, started_at, prov_str)

    elapsed = (datetime.now(timezone.utc) - started_at).total_seconds()
    print(f"\n=== Done in {elapsed:.0f}s ({elapsed / 60:.1f}m) ===")
    print(f"   New: {counts['new']:,}")
    print(f"   Updated: {counts['updated']:,}")
    print(f"   Price changed: {counts['price_changed']:,}")
    print(f"   State changed: {counts['state_changed']:,}")
    print(f"   Page fails: {page_fails}")
    print(f"   Detail fails: {detail_fails}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="BAM NPA Property Scraper")
    parser.add_argument(
        "--province", type=str, help="Scrape single province (Thai name)"
    )
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

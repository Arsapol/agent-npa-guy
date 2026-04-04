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
AMPHUR_CONCURRENCY = 8
PAGE_SIZE = 200
# Provinces with fewer items than this skip amphur partitioning (1 call vs many)
PROVINCE_DIRECT_THRESHOLD = 200


async def init_session(client: httpx.AsyncClient, quiet: bool = False) -> bool:
    """Visit homepage to acquire/refresh cookiesession1."""
    resp = await client.get("https://www.jjpropertythai.com/", headers=HEADERS)
    cookie = dict(client.cookies).get("cookiesession1", "none")
    if not quiet:
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


async def fetch_page(
    client: httpx.AsyncClient,
    page: int,
    province: str | None = None,
    district: str | None = None,
    subdistrict: str | None = None,
) -> dict | None:
    params: dict = {
        "freeText": "",
        "page": page,
        "user_code": "521789",
        "limit": PAGE_SIZE,
        "SellingStart": 0,
        "SellingEnd": 100000000,
    }
    if province is not None:
        params["Province"] = province
    if district is not None:
        params["District"] = district
    if subdistrict is not None:
        params["SubDistrict"] = subdistrict
    return await fetch_with_retry(client, f"{BASE_URL}/assets", params)


async def fetch_provinces(client: httpx.AsyncClient) -> list[dict]:
    """Fetch province dropdown list."""
    result = await fetch_with_retry(client, f"{BASE_URL}/dropdown/province", {})
    if result and "data" in result:
        return result["data"]
    return []


async def fetch_all_amphurs(client: httpx.AsyncClient) -> dict[int, list[dict]]:
    """Fetch all amphurs, grouped by PROVINCE_ID."""
    result = await fetch_with_retry(client, f"{BASE_URL}/dropdown/amphur", {})
    grouped: dict[int, list[dict]] = {}
    if result and isinstance(result, dict) and "data" in result:
        data = result["data"]
        items = data if isinstance(data, list) else []
        for item in items:
            pid = item.get("PROVINCE_ID")
            if pid is not None:
                grouped.setdefault(pid, []).append(item)
    print(f"  Loaded {sum(len(v) for v in grouped.values())} amphurs across {len(grouped)} provinces")
    return grouped


async def fetch_all_subdistricts(client: httpx.AsyncClient) -> dict[int, list[dict]]:
    """Fetch all subdistricts (tambons), grouped by AMPHUR_ID."""
    result = await fetch_with_retry(client, f"{BASE_URL}/dropdown/district", {})
    grouped: dict[int, list[dict]] = {}
    if result and isinstance(result, dict) and "data" in result:
        data = result["data"]
        items = data if isinstance(data, list) else []
        for item in items:
            aid = item.get("AMPHUR_ID")
            if aid is not None:
                grouped.setdefault(aid, []).append(item)
    print(f"  Loaded {sum(len(v) for v in grouped.values())} subdistricts across {len(grouped)} amphurs")
    return grouped


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


MAX_PAGES_BEFORE_DRILL = 50


async def scrape_partition(
    client: httpx.AsyncClient,
    seen_ids: set[int],
    province: str | None = None,
    district: str | None = None,
    subdistrict: str | None = None,
) -> tuple[list[JamPropertyParsed], int, int]:
    """Scrape all pages for a partition. Returns (properties, fail_count, api_total)."""
    props: list[JamPropertyParsed] = []
    fail_count = 0

    label = "/".join(filter(None, [province, district, subdistrict]))
    t0 = time.time()
    result = await fetch_page(
        client, page=1, province=province, district=district, subdistrict=subdistrict
    )
    if not result:
        print(f"      [{label}] page 1 FAILED ({time.time()-t0:.1f}s)")
        return props, 1, 0

    total = result.get("count", 0)
    if total == 0:
        return props, 0, 0

    total_pages = (total + PAGE_SIZE - 1) // PAGE_SIZE
    print(f"      [{label}] {total} items, {total_pages}p ({time.time()-t0:.1f}s)")

    # Process page 1
    for p in parse_properties(result.get("data", [])):
        if p.asset_id not in seen_ids:
            seen_ids.add(p.asset_id)
            props.append(p)

    # Paginate sequentially — the backend can't handle concurrent deep pagination
    for page in range(2, total_pages + 1):
        r = await fetch_page(
            client, page=page, province=province, district=district, subdistrict=subdistrict
        )
        if r:
            for p in parse_properties(r.get("data", [])):
                if p.asset_id not in seen_ids:
                    seen_ids.add(p.asset_id)
                    props.append(p)
        else:
            fail_count += 1
        await asyncio.sleep(0.3)

    if total_pages > 1:
        print(f"      [{label}] done: {len(props)} scraped, {fail_count} fails ({time.time()-t0:.1f}s)")

    return props, fail_count, total


async def scrape_all(
    max_properties: int | None = None,
    province_ids: list[int] | None = None,
) -> tuple[list[JamPropertyParsed], int]:
    """Scrape all properties: province → amphur → subdistrict (if needed). Returns (properties, total_fails)."""
    all_parsed: list[JamPropertyParsed] = []
    seen_ids: set[int] = set()
    total_fails = 0

    async with httpx.AsyncClient(timeout=120.0, follow_redirects=True) as client:
        await init_session(client)

        # Load reference data upfront
        provinces = await fetch_provinces(client)
        if not provinces:
            print("  FATAL: Failed to fetch provinces")
            return all_parsed, 1

        if province_ids:
            provinces = [p for p in provinces if p["PROVINCE_ID"] in province_ids]
            print(f"  Filtered to {len(provinces)} provinces: {[p['PROVINCE_NAME'] for p in provinces]}")

        amphurs_by_prov = await fetch_all_amphurs(client)
        subs_by_amphur = await fetch_all_subdistricts(client)
        print(f"  {len(provinces)} provinces to scrape\n")

        # Province → Amphur → SubDistrict (if >50 pages)
        # First pass: quick count per province to decide strategy
        # (reuse page 1 data to avoid extra calls)

        async def scrape_province(prov: dict) -> tuple[str, int, int]:
            """Scrape one province. Returns (name, props_count, fails)."""
            prov_id = prov["PROVINCE_ID"]
            prov_name = prov["PROVINCE_NAME"]
            amphurs = amphurs_by_prov.get(prov_id, [])

            # Small province or no amphurs → scrape directly
            if not amphurs:
                props, fails, api_total = await scrape_partition(
                    client, seen_ids, province=str(prov_id)
                )
                all_parsed.extend(props)
                if props:
                    print(f"  {prov_name}: {len(props)} props ({fails} fails)")
                return prov_name, len(props), fails

            # Large province → parallel amphur scraping
            prov_total = 0
            prov_fails = 0
            sem = asyncio.Semaphore(AMPHUR_CONCURRENCY)

            async def scrape_amphur(amp: dict) -> tuple[list[JamPropertyParsed], int]:
                async with sem:
                    a_id = amp["AMPHUR_ID"]
                    a_name = amp.get("AMPHUR_NAME", str(a_id))

                    props, fails, api_total = await scrape_partition(
                        client, seen_ids,
                        province=str(prov_id), district=str(a_id),
                    )
                    api_pages = (api_total + PAGE_SIZE - 1) // PAGE_SIZE

                    if api_pages > MAX_PAGES_BEFORE_DRILL and a_id in subs_by_amphur:
                        subs = subs_by_amphur[a_id]
                        print(f"    {a_name}: {api_total} ({api_pages}p) → {len(subs)} subdistricts")
                        for sub in subs:
                            sub_id = sub.get("DISTRICT_ID", "")
                            sub_props, sub_fails, _ = await scrape_partition(
                                client, seen_ids,
                                province=str(prov_id), district=str(a_id),
                                subdistrict=str(sub_id),
                            )
                            props.extend(sub_props)
                            fails += sub_fails

                    return props, fails

            results = await asyncio.gather(*[scrape_amphur(a) for a in amphurs])
            for props, fails in results:
                all_parsed.extend(props)
                prov_total += len(props)
                prov_fails += fails

            if prov_total > 0:
                print(f"  {prov_name}: {prov_total} props, {len(amphurs)} amphurs ({prov_fails} fails)")
            return prov_name, prov_total, prov_fails

        # Run provinces: big ones sequential, small ones in parallel batches
        big = [p for p in provinces if len(amphurs_by_prov.get(p["PROVINCE_ID"], [])) > 0]
        small = [p for p in provinces if len(amphurs_by_prov.get(p["PROVINCE_ID"], [])) == 0]

        # Big provinces one at a time (they use internal amphur parallelism)
        for i, prov in enumerate(big):
            if i > 0 and i % 15 == 0:
                await init_session(client, quiet=True)
            _, _, fails = await scrape_province(prov)
            total_fails += fails

            if max_properties and len(all_parsed) >= max_properties:
                print(f"  Reached limit ({max_properties}), stopping")
                break  # noqa: this break is inside the for loop above

        # Small provinces in parallel (no amphur data, just direct scrape)
        if small and not (max_properties and len(all_parsed) >= max_properties):
            print(f"\n  Scraping {len(small)} small provinces in parallel...")
            small_sem = asyncio.Semaphore(5)

            async def scrape_small(prov: dict) -> tuple[str, int, int]:
                async with small_sem:
                    return await scrape_province(prov)

            results = await asyncio.gather(*[scrape_small(p) for p in small])
            for _, _, fails in results:
                total_fails += fails

        print(f"\n  Total: {len(all_parsed):,} properties, {total_fails} fails")

    return all_parsed, total_fails


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


async def main(
    limit: int | None = None,
    create_tables_only: bool = False,
    province_ids: list[int] | None = None,
):
    if create_tables_only:
        create_tables()
        return

    started_at = datetime.now(timezone.utc)
    print(f"=== JAM Scraper — {started_at.isoformat()} ===\n")

    # Ensure tables exist
    create_tables()

    # Scrape
    print("\n1. Scraping API...")
    properties, total_fails = await scrape_all(
        max_properties=limit, province_ids=province_ids
    )
    print(f"\n   Scraped: {len(properties):,} properties, {total_fails} failed pages")

    if not properties:
        print("   No properties scraped — aborting DB save")
        return

    # Save to DB
    print("\n2. Saving to database...")
    counts = save_to_db(properties, list(range(total_fails)), started_at)

    elapsed = (datetime.now(timezone.utc) - started_at).total_seconds()
    print(f"\n=== Done in {elapsed:.0f}s ({elapsed / 60:.1f}m) ===")
    print(f"   New: {counts['new']:,}")
    print(f"   Updated: {counts['updated']:,}")
    print(f"   Price changed: {counts['price_changed']:,}")
    print(f"   Sold: {counts['sold']:,}")
    print(f"   Unsold: {counts['unsold']:,}")
    print(f"   Failed pages: {total_fails}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="JAM Property Scraper")
    parser.add_argument("--limit", type=int, help="Max properties to scrape (for testing)")
    parser.add_argument("--create-tables", action="store_true", help="Create DB tables only")
    parser.add_argument(
        "--provinces", type=int, nargs="+", metavar="ID",
        help="Only scrape these PROVINCE_IDs (e.g. --provinces 1 3 11)",
    )
    args = parser.parse_args()

    asyncio.run(main(
        limit=args.limit,
        create_tables_only=args.create_tables,
        province_ids=args.provinces,
    ))

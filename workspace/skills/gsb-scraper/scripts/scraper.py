"""
GSB (ออมสิน) Production NPA Scraper

Scrapes all NPA properties from npa-assets.gsb.or.th, upserts into PostgreSQL,
and tracks price changes.

Architecture:
  - 3 list calls (one per asset_type_id: 341, 342, 343) → gets ALL items
  - Detail via HTML __NEXT_DATA__ parsing (asyncio.Semaphore(10))
  - DB saves in batches during scrape

Usage:
    python scraper.py                          # full scrape (all 3 types)
    python scraper.py --limit 5                # first N assets per type (test)
    python scraper.py --skip-detail            # search only, no detail fetch
    python scraper.py --create-tables          # create DB tables only
    python scraper.py --type 343               # condos only
"""

import argparse
import asyncio
import json
import re
import sys
import time
from datetime import datetime

import httpx
from sqlalchemy.orm import Session

from database import create_tables, get_engine, upsert_properties
from models import GsbAssetDetail, GsbAssetSearch, GsbScrapeLog

BASE_URL = "https://npa-assets.gsb.or.th"
API_URL = f"{BASE_URL}/apipr"

HEADERS = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "accept-language": "en-US,en;q=0.9,th;q=0.8",
    "user-agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/146.0.0.0 Safari/537.36"
    ),
}

# Relevant real-estate asset types
ASSET_TYPES = {
    341: "ที่ดิน",
    342: "ที่ดินพร้อมสิ่งปลูกสร้าง",
    343: "คอนโด/อาคารชุด/ห้องชุด",
}

DETAIL_CONCURRENCY = 15
DETAIL_DELAY = 0.05  # 50ms between detail requests
BATCH_SIZE = 50  # commit to DB every N items


# ---------------------------------------------------------------------------
# List/Search
# ---------------------------------------------------------------------------


async def fetch_list(
    client: httpx.AsyncClient,
    asset_type_id: int,
) -> list[dict]:
    """Fetch ALL items for a given asset_type_id. API returns everything in one call."""
    params = {
        "asset_type_dev": "npa",
        "asset_type_id": asset_type_id,
        "page": 1,
        "page_size": 12,
    }
    r = await client.get(f"{API_URL}/npa/asset", params=params)
    r.raise_for_status()
    data = r.json()

    if data.get("status") != 200 or not data.get("data"):
        print(f"  [WARN] No data for type {asset_type_id}")
        return []

    group = data["data"][0]
    items = group.get("asset_list", [])
    count = group.get("asset_type_count", len(items))
    print(f"  Type {asset_type_id} ({ASSET_TYPES.get(asset_type_id, '?')}): "
          f"{count} items, {len(items)} returned")
    return items


# ---------------------------------------------------------------------------
# Detail (HTML __NEXT_DATA__ parsing)
# ---------------------------------------------------------------------------


_detail_counter = 0
_detail_total = 0


async def fetch_detail(
    client: httpx.AsyncClient,
    npa_id: str,
    asset_type_id: int,
    semaphore: asyncio.Semaphore,
) -> dict | None:
    """Fetch detail page and parse __NEXT_DATA__ JSON."""
    global _detail_counter
    async with semaphore:
        await asyncio.sleep(DETAIL_DELAY)
        t0 = time.time()
        max_retries = 2
        r = None
        for attempt in range(max_retries + 1):
            try:
                r = await client.get(
                    f"{BASE_URL}/asset/npa",
                    params={
                        "id": npa_id,
                        "asset_type_id": asset_type_id,
                        "type_id": "asset_group_id_npa",
                    },
                    timeout=20.0,
                )
                r.raise_for_status()
                break
            except httpx.HTTPError as e:
                if attempt < max_retries:
                    wait = 3.0 * (attempt + 1)
                    print(f"  [{_detail_counter+1}/{_detail_total}] RETRY {npa_id} (attempt {attempt+2}, wait {wait:.0f}s): {e}")
                    await asyncio.sleep(wait)
                else:
                    _detail_counter += 1
                    print(f"  [{_detail_counter}/{_detail_total}] FAIL {npa_id}: {e} ({time.time()-t0:.1f}s)")
                    return None

        _detail_counter += 1
        elapsed = time.time() - t0
        if _detail_counter % 100 == 0 or elapsed > 5:
            print(f"  [{_detail_counter}/{_detail_total}] fetched ({elapsed:.1f}s)")

        m = re.search(
            r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
            r.text,
            re.DOTALL,
        )
        if not m:
            print(f"  [WARN] No __NEXT_DATA__ for {npa_id}")
            return None

        try:
            data = json.loads(m.group(1))
            return data["props"]["pageProps"]["info"]
        except (json.JSONDecodeError, KeyError) as e:
            print(f"  [ERR] Parse {npa_id}: {e}")
            return None


# ---------------------------------------------------------------------------
# Main scrape loop
# ---------------------------------------------------------------------------


async def scrape(
    asset_type_ids: list[int],
    limit: int | None = None,
    skip_detail: bool = False,
) -> None:
    started_at = datetime.now()
    engine = create_tables()

    print(f"\n=== GSB scraper starting at {started_at:%Y-%m-%d %H:%M:%S} ===")
    print(f"Asset types: {asset_type_ids}")
    if limit:
        print(f"Limit: {limit} per type")
    if skip_detail:
        print("Skipping detail fetch")

    total_search = 0
    total_detail = 0
    total_new = 0
    total_updated = 0
    total_price_changed = 0
    total_failed_details = 0

    async with httpx.AsyncClient(
        follow_redirects=True,
        timeout=30,
        headers=HEADERS,
    ) as client:
        for type_id in asset_type_ids:
            print(f"\n--- Fetching type {type_id} ---")
            items = await fetch_list(client, type_id)

            if limit:
                items = items[:limit]

            total_search += len(items)

            if not items:
                continue

            # Parse search results
            search_results: list[GsbAssetSearch] = []
            for raw in items:
                try:
                    parsed = GsbAssetSearch(
                        asset_id=str(raw.get("asset_id", "")),
                        asset_group_id=raw.get("asset_group_id"),
                        asset_group_id_npa=raw["asset_group_id_npa"],
                        asset_type_id=raw.get("asset_type_id", type_id),
                        asset_type_desc=raw.get("asset_type_desc"),
                        asset_subtype_desc=raw.get("asset_subtype_desc"),
                        asset_name=raw.get("asset_name"),
                        current_offer_price=raw.get("current_offer_price"),
                        xprice_normal=raw.get("xprice_normal"),
                        xprice=raw.get("xprice"),
                        xtype=raw.get("xtype"),
                        group_sell_price=raw.get("group_sell_price"),
                        group_special_price=raw.get("group_special_price"),
                        province_name=raw.get("province_name"),
                        district_name=raw.get("district_name"),
                        sub_district_name=raw.get("sub_district_name"),
                        village_head=raw.get("village_head"),
                        sum_rai=raw.get("sum_rai"),
                        sum_ngan=raw.get("sum_ngan"),
                        sum_square_wa=raw.get("sum_square_wa"),
                        square_meter=raw.get("square_meter"),
                        rai_ngan_wa=raw.get("rai_ngan_wa"),
                        deed_info=raw.get("deed_info"),
                        image_id=raw.get("image_id"),
                        ind_flag=raw.get("ind_flag"),
                        is_recommend=raw.get("is_recommend"),
                        promo_type=raw.get("promo_type"),
                        promotion_type=raw.get("promotion_type"),
                        events=json.dumps(raw.get("events")) if raw.get("events") else None,
                        raw_json=raw,
                    )
                    search_results.append(parsed)
                except Exception as e:
                    print(f"  [ERR] Parse search item: {e}")
                    continue

            # Fetch details
            detail_map: dict[str, dict] = {}
            if not skip_detail:
                global _detail_counter, _detail_total
                _detail_counter = 0
                _detail_total = len(search_results)
                semaphore = asyncio.Semaphore(DETAIL_CONCURRENCY)
                print(f"  Fetching {_detail_total} details (concurrency={DETAIL_CONCURRENCY})...")

                tasks = [
                    fetch_detail(client, s.asset_group_id_npa, s.asset_type_id, semaphore)
                    for s in search_results
                ]
                results = await asyncio.gather(*tasks)

                for s, detail_raw in zip(search_results, results):
                    if detail_raw is not None:
                        detail_map[s.asset_group_id_npa] = detail_raw
                        total_detail += 1
                    else:
                        total_failed_details += 1

                print(f"  Details fetched: {total_detail}, failed: {total_failed_details}")

            # Upsert in batches
            batch: list[tuple[GsbAssetSearch, GsbAssetDetail | None]] = []
            for s in search_results:
                detail_raw = detail_map.get(s.asset_group_id_npa)
                detail = None
                if detail_raw:
                    try:
                        detail = GsbAssetDetail(
                            latitude=detail_raw.get("latitude"),
                            longitude=detail_raw.get("longitude"),
                            building_no=detail_raw.get("building_no"),
                            floor_no=detail_raw.get("floor_no"),
                            asset_number=detail_raw.get("asset_number"),
                            square_meter=detail_raw.get("square_meter"),
                            square_wa=detail_raw.get("square_wa"),
                            width_meter=detail_raw.get("width_meter"),
                            depth_meter=detail_raw.get("depth_meter"),
                            builded_year=detail_raw.get("builded_year"),
                            road=detail_raw.get("road"),
                            alley=detail_raw.get("alley"),
                            remark=detail_raw.get("remark"),
                            booking_count=detail_raw.get("booking_count"),
                            count_view=detail_raw.get("count_view"),
                            asset_image=detail_raw.get("asset_image"),
                            asset_map=detail_raw.get("asset_map"),
                            panorama_image=detail_raw.get("panorama_image"),
                            asset_pdf=detail_raw.get("asset_pdf"),
                            buildings=detail_raw.get("buildings"),
                            events=detail_raw.get("events"),
                        )
                    except Exception as e:
                        print(f"  [ERR] Parse detail {s.asset_group_id_npa}: {e}")

                batch.append((s, detail))

                if len(batch) >= BATCH_SIZE:
                    with Session(engine) as session:
                        counts = upsert_properties(session, batch)
                        session.commit()
                    total_new += counts["new"]
                    total_updated += counts["updated"]
                    total_price_changed += counts["price_changed"]
                    batch = []

            # Flush remaining batch
            if batch:
                with Session(engine) as session:
                    counts = upsert_properties(session, batch)
                    session.commit()
                total_new += counts["new"]
                total_updated += counts["updated"]
                total_price_changed += counts["price_changed"]

    # Log scrape run
    finished_at = datetime.now()
    duration = (finished_at - started_at).total_seconds()

    with Session(engine) as session:
        session.add(GsbScrapeLog(
            started_at=started_at,
            finished_at=finished_at,
            total_search=total_search,
            total_detail=total_detail,
            new_count=total_new,
            updated_count=total_updated,
            price_changed_count=total_price_changed,
            failed_details=total_failed_details,
            asset_types_scraped=",".join(str(t) for t in asset_type_ids),
        ))
        session.commit()

    print(f"\n=== GSB scraper finished at {finished_at:%Y-%m-%d %H:%M:%S} ({duration:.0f}s) ===")
    print(f"  Search: {total_search}")
    print(f"  Detail: {total_detail} (failed: {total_failed_details})")
    print(f"  New: {total_new}")
    print(f"  Updated: {total_updated}")
    print(f"  Price changed: {total_price_changed}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description="GSB NPA Scraper")
    parser.add_argument(
        "--create-tables", action="store_true",
        help="Create DB tables only (no scraping)",
    )
    parser.add_argument(
        "--limit", type=int, default=None,
        help="Limit items per asset type (for testing)",
    )
    parser.add_argument(
        "--skip-detail", action="store_true",
        help="Skip detail page fetching",
    )
    parser.add_argument(
        "--type", type=int, nargs="+", dest="types",
        help="Asset type IDs to scrape (default: 341 342 343)",
    )
    args = parser.parse_args()

    if args.create_tables:
        create_tables()
        return

    type_ids = args.types or [341, 342, 343]
    for t in type_ids:
        if t not in ASSET_TYPES:
            print(f"Unknown asset type: {t}. Valid: {list(ASSET_TYPES.keys())}")
            sys.exit(1)

    asyncio.run(scrape(
        asset_type_ids=type_ids,
        limit=args.limit,
        skip_detail=args.skip_detail,
    ))


if __name__ == "__main__":
    main()

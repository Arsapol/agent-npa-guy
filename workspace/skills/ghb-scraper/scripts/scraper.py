"""
GHB Production Scraper — HTML pagination + detail page parsing

Scrapes all NPA properties from ghbhomecenter.com, upserts into PostgreSQL,
and tracks price changes.

Architecture:
  - Phase 1: Paginate HTML search listings to discover property IDs
  - Phase 2: Fetch detail pages for each property (HTML parsing + GPS/images)
  - JWT acquired from homepage, refreshed when expired (~7d TTL)
  - Rate limited: ~2 req/sec for HTML, conservative sliding window

Usage:
    python scraper.py                              # full scrape (all property types)
    python scraper.py --type 4                     # condos only (pt[]=4)
    python scraper.py --province 3001              # Bangkok only (province_id)
    python scraper.py --limit 50                   # first N properties (test)
    python scraper.py --skip-detail                # listing only, no detail fetch
    python scraper.py --create-tables              # create DB tables only
"""

import argparse
import asyncio
import re
import time
from datetime import datetime

import httpx
from selectolax.parser import HTMLParser
from sqlalchemy.orm import Session

from database import (
    create_tables,
    get_engine,
    upsert_from_listing,
    _merge_detail_to_prop,
)
from models import (
    GhbDetailPage,
    GhbProperty,
    GhbSearchCard,
    GhbScrapeLog,
)

BASE_URL = "https://www.ghbhomecenter.com"

HTML_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "th,en-US;q=0.9,en;q=0.8",
}

# Property type IDs (from pt[] checkboxes on /property-for-sale):
#   1=บ้านเดี่ยว, 2=บ้านแฝด, 3=ทาวน์เฮ้าส์, 4=คอนโด,
#   5=อาคารพาณิชย์, 6=ที่ดิน, 7=แฟลต, 8=อื่นๆ
ALL_TYPE_IDS = [1, 2, 3, 4, 5, 6, 7, 8]
ITEMS_PER_PAGE = 20

# Rate limiting
LISTING_DELAY = 0.5       # 500ms between listing page requests
DETAIL_DELAY = 0.5        # 500ms between detail page requests
DETAIL_CONCURRENCY = 5    # concurrent detail fetches
BATCH_SIZE = 50           # DB commit batch size


# ---------------------------------------------------------------------------
# JWT management
# ---------------------------------------------------------------------------


class JwtManager:
    """Manages anonymous JWT extraction and refresh from GHB pages."""

    def __init__(self):
        self._token: str | None = None
        self._acquired_at: float = 0

    @property
    def token(self) -> str | None:
        return self._token

    def extract_from_html(self, html: str) -> str | None:
        match = re.search(r'var\s+accessToken\s*=\s*"([^"]+)"', html)
        if match:
            self._token = match.group(1)
            self._acquired_at = time.monotonic()
        return self._token

    async def ensure_token(self, client: httpx.AsyncClient) -> str:
        """Get a valid JWT, refreshing from homepage if needed."""
        # Refresh if no token or older than 6 days
        if not self._token or (time.monotonic() - self._acquired_at) > 518400:
            r = await client.get(BASE_URL, headers=HTML_HEADERS)
            r.raise_for_status()
            token = self.extract_from_html(r.text)
            if not token:
                raise RuntimeError("Failed to extract JWT from GHB homepage")
            print(f"[JWT] Acquired token: {token[:40]}...")
        return self._token


# ---------------------------------------------------------------------------
# HTML parsing
# ---------------------------------------------------------------------------


def parse_search_page(html: str) -> tuple[list[GhbSearchCard], int]:
    """
    Parse an HTML search results page.
    Returns (list of property cards, total property count).
    """
    tree = HTMLParser(html)
    cards: list[GhbSearchCard] = []

    # Extract total count from "ค้นพบทรัพย์ 26,648 รายการ" in <h2>
    total = 0
    total_match = re.search(r"ค้นพบ[^<]*?([\d,]+)\s*รายการ", html)
    if total_match:
        total = int(total_match.group(1).replace(",", ""))

    # Each property card is a .card containing a link to /property-{id}
    seen_ids: set[int] = set()
    for card_el in tree.css(".card"):
        link = card_el.css_first("a[href*='/property-']")
        if not link:
            continue
        href = link.attributes.get("href") or ""
        m = re.search(r"/property-(\d+)", href)
        if not m:
            continue
        pid = int(m.group(1))
        if pid in seen_ids:
            continue
        seen_ids.add(pid)

        # Price from .text-propertyprice → "210,000 บาท"
        price_el = card_el.css_first(".text-propertyprice")
        price_text = (price_el.text() or "").strip() if price_el else None

        # Title + property code from .text-header-titletype divs
        # First one = title, the one with "รหัสทรัพย์" = property code
        title = None
        property_no = None
        for div in card_el.css(".text-header-titletype"):
            t = (div.text() or "").strip()
            if "รหัสทรัพย์" in t:
                code_m = re.search(r"รหัสทรัพย์[:\s]*(\S+)", t)
                if code_m:
                    property_no = code_m.group(1)
            elif title is None and t:
                title = t

        # Location from .text-location → "ทุ่งโพธิ์, นาดี, ปราจีนบุรี"
        loc_el = card_el.css_first(".text-location")
        location = (loc_el.text() or "").strip() if loc_el else None

        # Area from .text-area → "10.4 ตร.ว."
        area_el = card_el.css_first(".text-area")
        area_text = (area_el.text() or "").strip() if area_el else None

        # Promotion label
        tag_el = card_el.css_first(".card-tag")
        promotion_label = (tag_el.text() or "").strip() if tag_el else None

        # Image URL
        img_el = card_el.css_first("img[src*='/Media/']")
        image_url = (img_el.attributes.get("src") or None) if img_el else None

        cards.append(GhbSearchCard(
            property_id=pid,
            property_no=property_no,
            title=title,
            price=price_text,
            location=location,
            area_text=area_text,
            image_url=image_url,
            promotion_label=promotion_label,
        ))

    return cards, total


def parse_detail_page(html: str, property_id: int) -> GhbDetailPage:
    """Parse an HTML property detail page for all available fields."""
    tree = HTMLParser(html)
    detail = GhbDetailPage(property_id=property_id)

    # Title from h1
    for h1 in tree.css("h1"):
        t = (h1.text() or "").strip()
        if t and len(t) < 200:
            detail.title = t
            break

    # Price from h3.text-price
    for h3 in tree.css("h3.text-price"):
        t = (h3.text() or "").strip()
        if t:
            price_match = re.search(r"([\d,]+)", t)
            if price_match:
                detail.price = int(price_match.group(1).replace(",", ""))
            break

    # Key-value pairs from .row > .col layout
    field_map = {}
    for row in tree.css(".row"):
        cols = row.css("[class*='col-']")
        if len(cols) >= 2:
            label = (cols[0].text() or "").strip()
            value = (cols[1].text() or "").strip()
            if label and value and len(label) < 80 and len(value) < 200:
                if not any(k in label + value for k in ["function", "var ", "$(", "document"]):
                    field_map[label] = value

    # Map Thai labels to fields
    detail.property_no = field_map.get("รหัสทรัพย์") or _extract_code(field_map)
    detail.property_type = field_map.get("ประเภททรัพย์")
    detail.project_name = field_map.get("โครงการ")
    detail.deed_no = field_map.get("เลขที่โฉนด/นส 3ก.")
    detail.house_no = field_map.get("เลขที่")
    detail.soi = field_map.get("ซอย")
    detail.road = field_map.get("ถนน")
    detail.sub_district = field_map.get("แขวง/ตำบล")
    detail.district = field_map.get("เขต/อำเภอ")
    detail.province = field_map.get("จังหวัด")

    # Area/floor from merged field keys
    for key, val in field_map.items():
        if "ตร.ม." in key or "ตร.ว." in key:
            detail.area_text = key
            if "ชั้น" in val:
                detail.floor_info = val
            break

    # GPS from Google Maps daddr param or JS variables
    gps = re.findall(r"daddr=([\d.]+),([\d.]+)", html)
    if gps:
        detail.lat = float(gps[0][0])
        detail.lon = float(gps[0][1])
    else:
        geo_lat = re.search(r"var\s+geoLat\s*=\s*([\d.]+)", html)
        geo_lon = re.search(r"var\s+geoLong\s*=\s*([\d.]+)", html)
        if geo_lat:
            detail.lat = float(geo_lat.group(1))
        if geo_lon:
            detail.lon = float(geo_lon.group(1))

    # Image media IDs (exclude thumbnails with size suffix)
    media_ids = sorted(set(re.findall(r"/v3/property/api/Media/(\d+)(?!-)", html)))
    detail.image_ids = media_ids

    # Description from meta tag
    for meta in tree.css("meta[name='description']"):
        content = meta.attributes.get("content") or ""
        if content:
            detail.description = content
            break

    return detail, field_map


def _extract_code(field_map: dict) -> str | None:
    """Try to extract property code from field_map keys containing digits."""
    for key in field_map:
        if "รหัสทรัพย์" in key:
            # Key might be "รหัสทรัพย์ 1301201301"
            code_match = re.search(r"(\d{8,})", key)
            if code_match:
                return code_match.group(1)
            return field_map[key]
    return None


# ---------------------------------------------------------------------------
# Scraper
# ---------------------------------------------------------------------------


async def scrape_listing_pages(
    client: httpx.AsyncClient,
    type_ids: list[int],
    province_id: int | None,
    limit: int | None,
) -> list[GhbSearchCard]:
    """
    Phase 1: Paginate HTML search listings to discover property cards.
    Returns list of unique GhbSearchCard objects.
    """
    all_cards: list[GhbSearchCard] = []
    seen: set[int] = set()

    for type_id in type_ids:
        params: dict = {"pt[]": str(type_id), "pg": "1"}
        if province_id:
            params["p"] = str(province_id)

        # Fetch first page to get total count
        r = await client.get(
            f"{BASE_URL}/property-for-sale",
            params=params,
            headers=HTML_HEADERS,
        )
        r.raise_for_status()
        cards, total = parse_search_page(r.text)

        for c in cards:
            if c.property_id not in seen:
                seen.add(c.property_id)
                all_cards.append(c)

        total_pages = max(1, (total + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE)
        type_label = {1: "บ้านเดี่ยว", 2: "บ้านแฝด", 3: "ทาวน์เฮ้าส์", 4: "คอนโด",
                      5: "อาคารพาณิชย์", 6: "ที่ดิน", 7: "แฟลต", 8: "อื่นๆ"}.get(type_id, str(type_id))
        print(f"[Listing] type={type_label}: {total:,} properties, {total_pages:,} pages")

        if limit and len(all_cards) >= limit:
            all_cards = all_cards[:limit]
            print(f"[Listing] Limit reached: {limit}")
            return all_cards

        # Paginate remaining pages
        for page in range(2, total_pages + 1):
            await asyncio.sleep(LISTING_DELAY)
            params["pg"] = str(page)

            try:
                r = await client.get(
                    f"{BASE_URL}/property-for-sale",
                    params=params,
                    headers=HTML_HEADERS,
                )
                r.raise_for_status()
                cards, _ = parse_search_page(r.text)

                new_count = 0
                for c in cards:
                    if c.property_id not in seen:
                        seen.add(c.property_id)
                        all_cards.append(c)
                        new_count += 1

                if page % 50 == 0 or page == total_pages:
                    print(f"  type={type_id} page {page}/{total_pages}: "
                          f"+{new_count} new, {len(all_cards)} total")

                if new_count == 0 and len(cards) == 0:
                    print(f"  type={type_id} page {page}: empty page, stopping")
                    break

                if limit and len(all_cards) >= limit:
                    all_cards = all_cards[:limit]
                    print(f"[Listing] Limit reached: {limit}")
                    return all_cards

            except httpx.HTTPError as e:
                print(f"  type={type_id} page {page}: ERROR {e}")
                continue

    print(f"[Listing] Total unique property IDs: {len(all_cards):,}")
    return all_cards


async def fetch_detail(
    client: httpx.AsyncClient,
    property_id: int,
    semaphore: asyncio.Semaphore,
) -> tuple[GhbDetailPage, dict] | None:
    """Fetch and parse a single property detail page."""
    async with semaphore:
        await asyncio.sleep(DETAIL_DELAY)
        try:
            r = await client.get(
                f"{BASE_URL}/property-{property_id}",
                headers=HTML_HEADERS,
            )
            r.raise_for_status()
            return parse_detail_page(r.text, property_id)
        except httpx.HTTPError as e:
            print(f"  detail {property_id}: ERROR {e}")
            return None


async def scrape_details(
    client: httpx.AsyncClient,
    property_ids: list[int],
    engine,
) -> dict[str, int]:
    """
    Phase 2: Fetch detail pages and update DB.
    Returns counts of detail pages fetched.
    """
    semaphore = asyncio.Semaphore(DETAIL_CONCURRENCY)
    total = len(property_ids)
    fetched = 0
    failed = 0

    # Process in batches
    for batch_start in range(0, total, BATCH_SIZE):
        batch_ids = property_ids[batch_start:batch_start + BATCH_SIZE]
        tasks = [fetch_detail(client, pid, semaphore) for pid in batch_ids]
        results = await asyncio.gather(*tasks)

        # Save batch to DB
        with Session(engine) as session:
            for result in results:
                if result is None:
                    failed += 1
                    continue

                detail, field_map = result
                prop = session.get(GhbProperty, detail.property_id)
                if prop:
                    _merge_detail_to_prop(prop, detail)
                    prop.raw_detail_fields = field_map
                    fetched += 1

            session.commit()

        done = min(batch_start + BATCH_SIZE, total)
        if done % 200 == 0 or done == total:
            print(f"[Detail] {done}/{total}: fetched={fetched}, failed={failed}")

    return {"fetched": fetched, "failed": failed}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


async def run(args: argparse.Namespace) -> None:
    if args.create_tables:
        create_tables()
        return

    engine = create_tables()
    started = datetime.now()
    log = GhbScrapeLog(started_at=started, phase="full" if not args.skip_detail else "listing")

    print(f"=== GHB scraper starting at {started.isoformat()} ===")

    async with httpx.AsyncClient(
        timeout=30,
        follow_redirects=True,
        limits=httpx.Limits(max_connections=20, max_keepalive_connections=10),
    ) as client:

        # Determine which types to scrape
        type_ids = [args.type] if args.type else ALL_TYPE_IDS
        province_id = args.province if args.province else None

        # Phase 1: Discover property IDs
        print("\n--- Phase 1: Listing crawl ---")
        listing_cards = await scrape_listing_pages(client, type_ids, province_id, args.limit)

        if not listing_cards:
            print("No properties found.")
            return

        # Save listing results to DB
        with Session(engine) as session:
            listing_counts = upsert_from_listing(session, listing_cards)
            session.commit()
            print(f"[Listing] DB: new={listing_counts['new']}, updated={listing_counts['updated']}")

        property_ids = [c.property_id for c in listing_cards]
        log.total_pages = len(property_ids) // ITEMS_PER_PAGE
        log.total_properties = len(property_ids)
        log.new_count = listing_counts["new"]
        log.updated_count = listing_counts["updated"]

        # Phase 2: Detail pages
        if not args.skip_detail:
            print(f"\n--- Phase 2: Detail crawl ({len(property_ids):,} properties) ---")
            detail_counts = await scrape_details(client, property_ids, engine)
            log.failed_details = detail_counts["failed"]

    finished = datetime.now()
    log.finished_at = finished
    elapsed = (finished - started).total_seconds()

    with Session(engine) as session:
        session.add(log)
        session.commit()

    print(f"\n=== GHB scraper finished at {finished.isoformat()} ===")
    print(f"Elapsed: {elapsed:.0f}s")
    print(f"Properties discovered: {len(property_ids):,}")
    if not args.skip_detail:
        print(f"Detail pages: fetched={detail_counts['fetched']}, failed={detail_counts['failed']}")


def main():
    parser = argparse.ArgumentParser(description="GHB NPA Property Scraper")
    parser.add_argument("--type", type=int, choices=ALL_TYPE_IDS,
                        help="Property type ID (4=condo, 1=house, 3=townhouse, etc.)")
    parser.add_argument("--province", type=int,
                        help="Province ID (3001=Bangkok)")
    parser.add_argument("--limit", type=int,
                        help="Max properties to scrape (for testing)")
    parser.add_argument("--skip-detail", action="store_true",
                        help="Skip detail page fetching (listing only)")
    parser.add_argument("--create-tables", action="store_true",
                        help="Create DB tables and exit")
    args = parser.parse_args()
    asyncio.run(run(args))


if __name__ == "__main__":
    main()

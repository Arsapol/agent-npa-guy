"""
LH Bank NPA Scraper -- Production scraper.

Fetches all ~33 properties from a single listing page, then fetches
each detail page for GPS, images, and full descriptions.

Usage:
    python scraper.py                    # Full scrape
    python scraper.py --create-tables    # Create DB tables only
    python scraper.py --limit 5          # Scrape only first N properties
    python scraper.py --list-only        # Listing page only, skip details
"""

from __future__ import annotations

import argparse
import asyncio
import re
import sys
from datetime import datetime

import httpx
from selectolax.parser import HTMLParser
from sqlalchemy.orm import Session

from database import create_tables, get_engine, upsert_properties
from models import LHDetail, LHListItem, LHScrapeLog

BASE_URL = "https://www.lhbank.co.th"
LISTING_URL = f"{BASE_URL}/th/property-for-sale/asset-for-sale/"
DETAIL_URL = f"{BASE_URL}/th/property-for-sale/detail/"
HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}

SEMAPHORE = asyncio.Semaphore(5)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _parse_price(text: str) -> int | None:
    digits = re.sub(r"[^\d]", "", text)
    return int(digits) if digits else None


def _abs_url(path: str) -> str:
    if not path or path.startswith("http"):
        return path
    return BASE_URL + path


# ---------------------------------------------------------------------------
# Listing page parser
# ---------------------------------------------------------------------------


def parse_listing_cards(html: str) -> list[LHListItem]:
    """Parse all property cards from the listing page."""
    tree = HTMLParser(html)
    items: list[LHListItem] = []

    for card in tree.css(".item.asset-for-sale-bank"):
        detail_div = card.css_first(".item-detail-asset-for-sale")
        onclick = detail_div.attributes.get("onclick", "") if detail_div else ""

        url_match = re.search(r"href='([^']+)'", onclick)
        detail_url = _abs_url(url_match.group(1).replace("&amp;", "&")) if url_match else ""

        code_match = re.search(r"AssetCode=(\w+)", onclick)
        asset_code = code_match.group(1) if code_match else ""

        asset_match = re.search(r"Asset=(\d+)", onclick)
        asset_param = asset_match.group(1) if asset_match else "1"

        asset_type = ""
        area_text = ""
        for row in card.css(".grid-cards-text .row"):
            cols = row.css("div[class*='col-']")
            if len(cols) >= 2:
                label = cols[0].text(strip=True)
                value = cols[1].text(strip=True)
                if "ประเภท" in label:
                    asset_type = value
                elif "เนื้อที่" in label:
                    area_text = value

        addr_el = card.css_first(".text-address-asset")
        address = addr_el.text(strip=True) if addr_el else ""

        price_el = card.css_first(".font-size-price")
        price = _parse_price(price_el.text(strip=True)) if price_el else None

        img_el = card.css_first(".card-img img")
        thumbnail = _abs_url(img_el.attributes.get("src", "")) if img_el else ""

        items.append(LHListItem(
            asset_code=asset_code,
            asset_param=asset_param,
            asset_type=asset_type,
            area_text=area_text,
            price=price,
            address=address,
            thumbnail=thumbnail,
            detail_url=detail_url,
        ))

    return items


# ---------------------------------------------------------------------------
# Detail page parser
# ---------------------------------------------------------------------------


def parse_detail_page(html: str) -> LHDetail:
    """Parse a property detail page."""
    tree = HTMLParser(html)
    fields: dict[str, str] = {}

    desc = tree.css_first(".assets-for-sale-description")
    if desc:
        for row in desc.css("div.d-table"):
            label_el = row.css_first("div.d-table-cell.label")
            cells = row.css("div.d-table-cell")
            value_el = cells[1] if len(cells) >= 2 else None
            if label_el and value_el:
                label = label_el.text(strip=True).rstrip(":")
                value = value_el.text(strip=True)
                fields[label] = value

    h1 = tree.css_first(".assets-for-sale-description h1")
    h1_text = h1.text(strip=True) if h1 else ""
    code_match = re.search(r"[A-Z]+\d+\w*", h1_text)
    asset_code = code_match.group(0) if code_match else ""

    hidden: dict[str, str] = {}
    for inp in tree.css("input[type='hidden']"):
        name = inp.attributes.get("name", "") or ""
        value = inp.attributes.get("value", "") or ""
        key = name.split("$")[-1] if "$" in name else name
        if key in ("hdfLatitude", "hdfLongitude", "hdfMap", "hdfPDF", "hdfAssetCode"):
            hidden[key] = value

    lat = lon = None
    if hidden.get("hdfLatitude"):
        try:
            lat = float(hidden["hdfLatitude"])
        except ValueError:
            pass
    if hidden.get("hdfLongitude"):
        try:
            lon = float(hidden["hdfLongitude"])
        except ValueError:
            pass

    image_urls: list[str] = []
    gallery = tree.css_first(".assets-for-sale-gallery")
    if gallery:
        for img in gallery.css("img"):
            src = img.attributes.get("src", "")
            if src and "/getmedia/" in src:
                image_urls.append(_abs_url(src))

    return LHDetail(
        asset_code=asset_code or hidden.get("hdfAssetCode", ""),
        asking_price=_parse_price(fields.get("ราคาประกาศขาย", "")),
        case_info=fields.get("ข้อมูลคดี", ""),
        status_desc=fields.get("สถานะ", ""),
        asset_type=fields.get("ประเภทสินทรัพย์", ""),
        location=fields.get("ที่ตั้งสินทรัพย์", ""),
        area_text=fields.get("เนื้อที่/พื้นที่ใช้สอย", ""),
        record_date=fields.get("วันที่บันทึก", ""),
        latitude=lat,
        longitude=lon,
        map_image_url=_abs_url(hidden.get("hdfMap", "")),
        pdf_url=_abs_url(hidden.get("hdfPDF", "")),
        image_urls=image_urls,
    )


# ---------------------------------------------------------------------------
# Async fetchers
# ---------------------------------------------------------------------------


async def fetch_listing(client: httpx.AsyncClient) -> list[LHListItem]:
    """Fetch and parse the single listing page."""
    print("Fetching listing page...")
    r = await client.get(LISTING_URL)
    r.raise_for_status()
    cards = parse_listing_cards(r.text)
    print(f"  Found {len(cards)} properties")
    return cards


async def fetch_detail(
    client: httpx.AsyncClient, card: LHListItem
) -> LHDetail | None:
    """Fetch and parse a single detail page with semaphore."""
    async with SEMAPHORE:
        try:
            r = await client.get(
                DETAIL_URL,
                params={"AssetCode": card.asset_code, "Asset": card.asset_param},
            )
            r.raise_for_status()
            detail = parse_detail_page(r.text)
            gps = "GPS" if detail.latitude else "no-GPS"
            imgs = len(detail.image_urls)
            print(f"  {card.asset_code}: {gps}, {imgs} images, {detail.asking_price or 0:,} THB")
            return detail
        except Exception as e:
            print(f"  {card.asset_code}: FAILED - {e}")
            return None


# ---------------------------------------------------------------------------
# Main scrape
# ---------------------------------------------------------------------------


async def scrape(
    limit: int | None = None,
    list_only: bool = False,
) -> None:
    engine = get_engine()
    log = LHScrapeLog(started_at=datetime.now())

    async with httpx.AsyncClient(
        timeout=30, follow_redirects=True, headers=HEADERS
    ) as client:
        cards = await fetch_listing(client)
        log.total_listing = len(cards)

        if limit:
            cards = cards[:limit]
            print(f"  Limited to {limit} properties")

        details: list[LHDetail | None] = []
        if not list_only:
            print(f"\nFetching {len(cards)} detail pages...")
            tasks = [fetch_detail(client, card) for card in cards]
            details = await asyncio.gather(*tasks)
            log.total_detail = sum(1 for d in details if d is not None)
            log.failed_details = sum(1 for d in details if d is None)
        else:
            details = [None] * len(cards)
            log.total_detail = 0
            log.failed_details = 0

    # Upsert to database
    total_listing = log.total_listing
    total_detail = log.total_detail or 0
    failed_details = log.failed_details or 0

    pairs = list(zip(cards, details))
    with Session(engine) as session:
        counts = upsert_properties(session, pairs)
        log.new_count = counts["new"]
        log.updated_count = counts["updated"]
        log.price_changed_count = counts["price_changed"]
        log.finished_at = datetime.now()
        session.add(log)
        session.commit()

    print(f"\n=== LH Bank scrape complete ===")
    print(f"  Listing: {total_listing} properties")
    print(f"  Details: {total_detail} fetched, {failed_details} failed")
    print(f"  New: {counts['new']}, Updated: {counts['updated']}, Price changed: {counts['price_changed']}")


def main() -> None:
    parser = argparse.ArgumentParser(description="LH Bank NPA Scraper")
    parser.add_argument("--create-tables", action="store_true", help="Create DB tables and exit")
    parser.add_argument("--limit", type=int, help="Limit to N properties")
    parser.add_argument("--list-only", action="store_true", help="Listing page only, skip details")
    args = parser.parse_args()

    if args.create_tables:
        create_tables()
        return

    asyncio.run(scrape(limit=args.limit, list_only=args.list_only))


if __name__ == "__main__":
    main()

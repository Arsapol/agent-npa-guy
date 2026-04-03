"""
SAM NPA Scraper — Step 2: Scrape property list pages (async)
Usage: python scrape_list.py [--db-uri ...] [--start-page 1] [--max-pages 0] [--delay 2]

Scrapes all listing pages via POST to page_list.php, parses each property card,
and upserts into sam_properties table. Fetches 200 items/page with max 10 concurrent requests.
"""

import argparse
import asyncio
import os
import re
import sys
from datetime import datetime

import httpx
from selectolax.parser import HTMLParser, Node

from html_utils import (
    create_http_client,
    find_span_after_label,
    text_of,
    attr_of,
)
from models import (
    Base,
    SAMListProperty,
    SamProperty,
    SamScrapeLog,
    parse_land_size,
    parse_sqm_size,
)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DEFAULT_DB_URI = "postgresql://arsapolm@localhost:5432/npa_kb"
LIST_URL = "https://sam.or.th/site/npa/page_list.php"
PAGE_SIZE = 200


def parse_property_card(card: Node) -> SAMListProperty | None:
    """Parse a single .full_blog card from list page into a SAMListProperty."""
    try:
        # Status badge
        status_span = card.css_first("span[class*='icon_status_']")
        status = text_of(status_span) if status_span else "Unknown"

        # SAM ID from onclick='gotoDetail(XXXXX)'
        onclick_el = card.css_first("[onclick*='gotoDetail']")
        if not onclick_el:
            return None
        onclick_text = attr_of(onclick_el, "onclick")
        id_match = re.search(r"gotoDetail\((\d+)", onclick_text)
        if not id_match:
            return None
        sam_id = int(id_match.group(1))

        # Property code
        code = find_span_after_label(card, r"รหัสทรัพย์สิน")

        # Type
        type_name = find_span_after_label(card, r"ประเภททรัพย์สิน")

        # Location
        district = ""
        province = ""
        loc_text = find_span_after_label(card, r"สถานที่ตั้ง")
        if loc_text:
            prov_m = re.search(r"จ\.(.+)", loc_text)
            dist_m = re.search(r"อ\.(.+?)(?:\s+จ\.|$)", loc_text)
            if prov_m:
                province = prov_m.group(1).strip()
            if dist_m:
                district = dist_m.group(1).strip()

        # Size
        size_text = find_span_after_label(card, r"พื้นที่/เนื้อที่")

        # Floor (condo only)
        floor = None
        floor_text = find_span_after_label(card, r"ชั้นที่")
        if floor_text:
            try:
                floor = int(floor_text)
            except ValueError:
                pass

        # Price
        price_baht = None
        price_span = card.css_first("div.btn-price span")
        if price_span:
            price_text = text_of(price_span)
            pm = re.search(r"([\d,]+)", price_text)
            if pm:
                price_baht = int(pm.group(1).replace(",", ""))

        # Thumbnail
        thumbnail_url = ""
        card_img = card.css_first("div.card-img img")
        if card_img:
            thumbnail_url = attr_of(card_img, "src")

        return SAMListProperty(
            sam_id=sam_id,
            code=code,
            type_name=type_name,
            district=district,
            province=province,
            size_text=size_text,
            price_baht=price_baht,
            status=status,
            floor=floor,
            thumbnail_url=thumbnail_url,
        )
    except Exception as e:
        print(f"   Warning: Error parsing card: {e}", file=sys.stderr)
        return None


async def fetch_list_page(
    client: httpx.AsyncClient,
    page: int = 1,
    filters: dict | None = None,
) -> tuple[list[SAMListProperty], int]:
    """Fetch one page of listings. Returns (properties_list, total_count)."""
    data = {
        "layout": "list",
        "limit": str(PAGE_SIZE),
        "sort": "",
        "order": "",
        "page": str(page),
        "s_product_type": "",
        "s_province": "",
        "s_district": "",
        "s_status_id": "",
        "keyword": "",
        "product_code": "",
        "province": "",
        "start_price": "",
        "end_price": "",
        "key_search": "",
    }
    if filters:
        data.update(filters)

    resp = await client.post(LIST_URL, data=data)
    resp.raise_for_status()
    resp.encoding = "utf-8"

    tree = HTMLParser(resp.text)

    # Total count from: "ผลการค้นหา 4,707 รายการ"
    total = 0
    for h5 in tree.css("h5"):
        h5_text = text_of(h5)
        if "รายการ" in h5_text:
            total_match = re.search(r"([\d,]+)\s*รายการ", h5_text)
            if total_match:
                total = int(total_match.group(1).replace(",", ""))
                break

    # Parse property cards
    cards = tree.css("div.full_blog")
    properties: list[SAMListProperty] = []
    for card in cards:
        parsed = parse_property_card(card)
        if parsed:
            properties.append(parsed)

    return properties, total


async def fetch_list_page_with_retry(
    client: httpx.AsyncClient,
    page: int,
    filters: dict | None,
    semaphore: asyncio.Semaphore,
    delay: float,
    max_retries: int = 3,
) -> tuple[int, list[SAMListProperty] | None]:
    """Fetch a list page with semaphore, delay, and retry. Returns (page_num, results)."""
    async with semaphore:
        await asyncio.sleep(delay)
        for attempt in range(max_retries):
            try:
                props, _ = await fetch_list_page(client, page, filters)
                return (page, props)
            except httpx.TransportError:
                wait = (attempt + 1) * 5
                print(f"   Page {page}: transport error, retry in {wait}s...")
                await asyncio.sleep(wait)
            except Exception as e:
                if attempt < max_retries - 1:
                    await asyncio.sleep(3)
                else:
                    print(f"   Page {page}: failed after {max_retries} attempts: {e}", file=sys.stderr)
                    return (page, None)
        return (page, None)


def upsert_properties(
    properties: list[SAMListProperty], db_session
) -> tuple[int, int]:
    """Upsert parsed properties into sam_properties. Returns (new, updated)."""
    new_count = 0
    updated_count = 0

    for prop in properties:
        existing = (
            db_session.query(SamProperty)
            .filter_by(sam_id=prop.sam_id)
            .first()
        )
        if existing is None:
            db_session.add(
                SamProperty(
                    sam_id=prop.sam_id,
                    code=prop.code,
                    type_name=prop.type_name,
                    district=prop.district,
                    province=prop.province,
                    size_text=prop.size_text,
                    price_baht=prop.price_baht,
                    status=prop.status,
                    floor=prop.floor,
                    thumbnail_url=prop.thumbnail_url or None,
                    is_active=True,
                )
            )
            new_count += 1
        else:
            changed = False
            if prop.code and existing.code != prop.code:
                existing.code = prop.code
                changed = True
            if prop.price_baht is not None and existing.price_baht != prop.price_baht:
                existing.price_baht = prop.price_baht
                changed = True
            if prop.status and existing.status != prop.status:
                existing.status = prop.status
                changed = True
            if prop.type_name and existing.type_name != prop.type_name:
                existing.type_name = prop.type_name
                changed = True
            if changed:
                existing.updated_at = datetime.now()
                updated_count += 1

    db_session.commit()
    return new_count, updated_count


async def main():
    parser = argparse.ArgumentParser(description="Scrape SAM NPA property listings")
    parser.add_argument("--db-uri", default=os.getenv("POSTGRES_URI", DEFAULT_DB_URI))
    parser.add_argument("--start-page", type=int, default=1)
    parser.add_argument("--max-pages", type=int, default=0, help="0 = all pages")
    parser.add_argument("--delay", type=float, default=2.0, help="Seconds between requests")
    parser.add_argument(
        "--filter-status",
        default="",
        help="Status filter: '' (all), '1' (direct sale), '2' (auction)",
    )
    args = parser.parse_args()

    engine = create_engine(args.db_uri)
    Base.metadata.create_all(
        engine,
        tables=[SamProperty.__table__, SamScrapeLog.__table__],
    )
    Session = sessionmaker(bind=engine)

    log = SamScrapeLog(
        scrape_type="list",
        started_at=datetime.now(),
    )

    filters = {}
    if args.filter_status:
        filters["s_status_id"] = args.filter_status

    all_props: list[SAMListProperty] = []
    new_total = 0
    upd_total = 0
    pages_done = 0

    async with create_http_client() as client:
        # Initialize session
        print("Initializing session...")
        await client.get(LIST_URL)

        # Phase 1: Fetch page 1 to get total count
        print("Fetching page 1...")
        props, total = await fetch_list_page(client, page=1, filters=filters)
        total_pages = (total + PAGE_SIZE - 1) // PAGE_SIZE

        print(f"   Total properties: {total:,} ({total_pages} pages of {PAGE_SIZE})")

        all_props.extend(props)
        pages_done = 1

        with Session() as db:
            n, u = upsert_properties(props, db)
            new_total += n
            upd_total += u
        print(f"   Page 1: {len(props)} parsed, {n} new, {u} updated")

        # Phase 2: Fan-out remaining pages
        max_pages = args.max_pages if args.max_pages > 0 else total_pages
        remaining_pages = list(range(2, min(max_pages, total_pages) + 1))

        if remaining_pages:
            semaphore = asyncio.Semaphore(10)
            tasks = [
                fetch_list_page_with_retry(client, page, filters, semaphore, args.delay)
                for page in remaining_pages
            ]
            print(f"Fetching {len(remaining_pages)} pages concurrently (max 10)...")
            results = await asyncio.gather(*tasks)

            # Phase 3: Fan-in — sequential DB writes
            for page_num, page_props in sorted(results, key=lambda x: x[0]):
                if page_props is None:
                    print(f"   Skipped page {page_num}")
                    continue
                all_props.extend(page_props)
                pages_done += 1
                with Session() as db:
                    n, u = upsert_properties(page_props, db)
                    new_total += n
                    upd_total += u
                print(f"   Page {page_num}: {len(page_props)} parsed, {n} new, {u} updated")

    with Session() as db:
        db.add(SamScrapeLog(
            scrape_type="list",
            started_at=log.started_at,
            finished_at=datetime.now(),
            pages_scraped=pages_done,
            items_parsed=len(all_props),
            items_new=new_total,
            items_updated=upd_total,
        ))
        db.commit()

    print(
        f"\nDone: {pages_done} pages, {len(all_props)} properties, "
        f"{new_total} new, {upd_total} updated"
    )


if __name__ == "__main__":
    asyncio.run(main())

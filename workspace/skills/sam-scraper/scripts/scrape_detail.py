"""
SAM NPA Scraper — Step 3: Scrape detail pages (async)
Usage: python scrape_detail.py [--db-uri ...] [--limit 0] [--delay 3] [--only-missing]

For each sam_property that has no detail_fetched_at, fetch its detail page
and parse all fields. Fetches with max 10 concurrent requests, processes in chunks of 100.
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
    SAMImageInfo,
    SAMPropertyDetail,
    SamProperty,
    SamPropertyImage,
    SamScrapeLog,
    parse_address,
    parse_land_size,
    parse_price_per_unit,
    parse_sqm_size,
)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DEFAULT_DB_URI = "postgresql://arsapolm@localhost:5432/npa_kb"
DETAIL_URL = "https://sam.or.th/site/npa/detail.php"
CHUNK_SIZE = 100


def parse_detail_page(sam_id: int, html: str) -> SAMPropertyDetail | None:
    """
    Parse a SAM detail page HTML into a SAMPropertyDetail.
    Handles both land and condo layouts.
    """
    tree = HTMLParser(html)

    # === Section: detail_sec01_detail ===
    sec01 = tree.css_first("div.detail_sec01_detail")
    if not sec01:
        return None

    # --- Property Code ---
    code = ""
    h3 = sec01.css_first("h3")
    if h3:
        m = re.search(r"รหัสทรัพย์สิน\s*:\s*(.+)", text_of(h3))
        if m:
            code = m.group(1).strip()

    # --- Key-value pairs in <p> ---
    info_p = sec01.css_first("p")
    if not info_p:
        info_p = sec01

    # Type
    type_name = find_span_after_label(info_p, r"ประเภททรัพย์สิน")

    # Title deed type + numbers
    title_deed_type = None
    title_deed_numbers = None
    deed_text = find_span_after_label(info_p, r"ประเภทเอกสารสิทธิ์")
    if deed_text:
        deed_m = re.match(r"(.+?)\s*:\s*(.+)", deed_text)
        if deed_m:
            title_deed_type = deed_m.group(1).strip()
            title_deed_numbers = deed_m.group(2).strip()
        else:
            title_deed_type = deed_text

    # Deed count
    deed_count = None
    deed_count_text = find_span_after_label(info_p, r"จำนวนเอกสารสิทธิ์")
    if deed_count_text:
        try:
            deed_count = int(deed_count_text)
        except ValueError:
            pass

    # Size (two formats: land vs condo)
    size_text = find_span_after_label(info_p, r"เนื้อที่")
    if not size_text:
        size_text = find_span_after_label(info_p, r"พื้นที่")

    size_sqm = None
    size_rai = None
    size_ngan = None
    size_wa = None
    land = parse_land_size(size_text) if size_text else None
    if land:
        size_rai, size_ngan, size_wa = land
        size_sqm = land[0] * 1600 + land[1] * 400 + land[2] * 4
    else:
        sqm = parse_sqm_size(size_text) if size_text else None
        if sqm:
            size_sqm = sqm

    # Address
    addr_text = find_span_after_label(info_p, r"ที่ตั้ง")
    address_full = addr_text or None
    house_number = None
    project_name = None
    road = None
    subdistrict = None
    district = None
    province = None
    if addr_text:
        addr_parts = parse_address(addr_text)
        house_number = addr_parts.get("house_number")
        project_name = addr_parts.get("project_name")
        road = addr_parts.get("road")
        subdistrict = addr_parts.get("subdistrict")
        district = addr_parts.get("district")
        province = addr_parts.get("province")

    # Zone color
    zone_color = find_span_after_label(info_p, r"เขตพื้นที่\s*\(สี\)") or None

    # Floor (condo only)
    floor = None
    floor_text = find_span_after_label(info_p, r"ชั้นที่")
    if floor_text:
        try:
            floor = int(floor_text)
        except ValueError:
            pass

    # Price per unit
    price_per_unit = None
    price_unit = None
    ppu_text = find_span_after_label(info_p, r"ราคาต่อตาราง")
    if ppu_text:
        ppu = parse_price_per_unit(ppu_text)
        if ppu:
            price_per_unit, price_unit = ppu

    # Price
    price_baht = None
    price_div = sec01.css_first("div.btn-success")
    if price_div:
        price_span = price_div.css_first("span")
        if price_span:
            price_text = text_of(price_span).replace(",", "")
            try:
                price_baht = int(price_text)
            except ValueError:
                pass

    # --- Coordinates ---
    lat = None
    lng = None
    map_link = tree.css_first("a[href*='show_map.php?lat=']")
    if map_link:
        href = attr_of(map_link, "href")
        lat_m = re.search(r"lat=([\d.]+)", href)
        lng_m = re.search(r"lng=([\d.]+)", href)
        if lat_m:
            lat = float(lat_m.group(1))
        if lng_m:
            lng = float(lng_m.group(1))

    # --- Map image ---
    map_image_url = None
    map_div = tree.css_first("div.map")
    if map_div:
        map_img = map_div.css_first("img")
        if map_img:
            map_image_url = attr_of(map_img, "src") or None

    # --- Gallery images ---
    images: list[SAMImageInfo] = []
    gallery_links = sec01.css("a.gallery")
    for link in gallery_links:
        href = attr_of(link, "href")
        if not href:
            continue
        filename = href.split("/")[-1]
        name_part = re.sub(r"^\d+_", "", filename.replace(".JPG", "").replace(".jpg", ""))
        if re.search(r"[CM]\d*$", name_part.split("_")[0]):
            img_type = "certificate"
        elif re.search(r"P\d*$", name_part.split("_")[0]):
            img_type = "photo"
        else:
            img_type = "photo"
        images.append(SAMImageInfo(url=href, image_type=img_type))

    # --- Promotion links ---
    promotion_links: list[str] = []
    promo_section = sec01.css_first("div.detail_sec01")
    if promo_section:
        for a in promo_section.css("a[target='_blank']"):
            href = attr_of(a, "href")
            if href and "promotion" in href:
                promotion_links.append(href)

    # === Tab contents ===

    # Tab 03: Description
    description = None
    remarks = None
    related_properties: list[str] = []

    tab03 = tree.css_first("div#tab03")
    if tab03:
        desc_p = tab03.css_first("p")
        if desc_p:
            description = text_of(desc_p) or None

        # Remarks
        remark_div = tab03.css_first("div.remark")
        if remark_div is None:
            for div in tab03.css("div"):
                div_text = text_of(div)
                if div_text and "หมายเหตุ" in div_text:
                    remark_div = div
                    break
        if remark_div:
            remarks = text_of(remark_div) or None

        # Related properties
        all_text = text_of(tab03)
        related = re.findall(r"\b(\d{0,2}[A-Z]{1,3}\d{3,6})\b", all_text)
        if related:
            own_code = code
            related_properties = list(set(r for r in related if r != own_code))

    # Tab 01: Status/Auction — parse structured fields
    status = ""
    announcement_start_date = None
    registration_end_date = None
    submission_date = None
    auction_method_text = None
    tab01 = tree.css_first("div#tab01")
    if tab01:
        status_span = tab01.css_first("span[class*='icon_status_']")
        status = text_of(status_span) if status_span else ""

        tab01_html = tab01.html or ""
        m = re.search(r"วันที่เริ่มประกาศขาย\s*:\s*(.+?)(?:<br|$)", tab01_html)
        if m:
            val = m.group(1).strip()
            if val and val != "-":
                announcement_start_date = val
        m = re.search(r"วันที่สิ้นสุดการลงทะเบียน\s*:\s*(.+?)(?:<br|$)", tab01_html)
        if m:
            val = m.group(1).strip()
            if val and val != "-":
                registration_end_date = val
        m = re.search(r"วันที่ยื่นซอง\s*:\s*(.+?)(?:<br|$)", tab01_html)
        if m:
            val = m.group(1).strip()
            if val and val != "-":
                submission_date = val
        m = re.search(r"สถานที่ประมูล\s*:\s*(.+?)(?:</p>|$)", tab01_html, re.DOTALL)
        if m:
            val = re.sub(r"<[^>]+>", "", m.group(1)).strip()
            if val:
                auction_method_text = val

    # Tab 02: Access
    access_directions = None
    tab02 = tree.css_first("div#tab02")
    if tab02:
        access_table = tab02.css_first("table")
        if access_table:
            access_directions = text_of(access_table) or None
        else:
            access_directions = text_of(tab02) or None

    return SAMPropertyDetail(
        sam_id=sam_id,
        code=code,
        type_name=type_name,
        title_deed_type=title_deed_type,
        title_deed_numbers=title_deed_numbers,
        deed_count=deed_count,
        size_text=size_text or None,
        size_sqm=size_sqm,
        size_rai=size_rai,
        size_ngan=size_ngan,
        size_wa=size_wa,
        address_full=address_full,
        house_number=house_number,
        project_name=project_name,
        road=road,
        subdistrict=subdistrict,
        district=district,
        province=province,
        zone_color=zone_color,
        floor=floor,
        price_baht=price_baht,
        price_per_unit=price_per_unit,
        price_unit=price_unit,
        status=status,
        announcement_start_date=announcement_start_date,
        registration_end_date=registration_end_date,
        submission_date=submission_date,
        auction_method_text=auction_method_text,
        lat=lat,
        lng=lng,
        images=images,
        map_image_url=map_image_url,
        description=description,
        remarks=remarks,
        access_directions=access_directions,
        promotion_links=promotion_links,
        related_properties=related_properties,
    )


def update_property_from_detail(
    db_session, sam_prop: SamProperty, detail: SAMPropertyDetail
):
    """Update a SamProperty ORM object with parsed detail data."""
    for field in [
        "code", "type_name", "title_deed_type", "title_deed_numbers",
        "deed_count", "size_text", "size_sqm", "size_rai", "size_ngan",
        "size_wa", "address_full", "house_number", "project_name", "road", "subdistrict",
        "district", "province", "zone_color", "floor", "price_baht",
        "price_per_unit", "price_unit", "status",
        "announcement_start_date", "registration_end_date",
        "submission_date", "auction_method_text",
        "lat", "lng", "map_image_url",
        "description", "remarks", "access_directions",
    ]:
        val = getattr(detail, field, None)
        if val is not None:
            setattr(sam_prop, field, val)

    # ARRAY fields
    if detail.related_properties:
        sam_prop.related_property_codes = detail.related_properties
    if detail.promotion_links:
        sam_prop.promotion_links = detail.promotion_links

    # Source URL
    sam_prop.source_url = f"{DETAIL_URL}?id={sam_prop.sam_id}&keyref="
    sam_prop.detail_fetched_at = datetime.now()

    # Images: delete old, insert new
    db_session.query(SamPropertyImage).filter_by(sam_id=sam_prop.sam_id).delete()
    for idx, img in enumerate(detail.images):
        db_session.add(
            SamPropertyImage(
                sam_id=sam_prop.sam_id,
                image_type=img.image_type,
                image_url=img.url,
                image_order=idx,
                is_primary=(idx == 0),
            )
        )

    db_session.add(sam_prop)


async def fetch_detail(
    client: httpx.AsyncClient,
    sam_id: int,
    semaphore: asyncio.Semaphore,
    delay: float,
) -> tuple[int, str | None]:
    """Fetch one detail page with semaphore + delay. Returns (sam_id, html_or_None)."""
    async with semaphore:
        await asyncio.sleep(delay)
        url = f"{DETAIL_URL}?id={sam_id}&keyref="
        try:
            resp = await client.get(url)
            resp.raise_for_status()
            resp.encoding = "utf-8"
            return (sam_id, resp.text)
        except Exception as e:
            print(f"    Error fetching SAM ID {sam_id}: {e}", file=sys.stderr)
            return (sam_id, None)


async def main():
    parser = argparse.ArgumentParser(description="Scrape SAM NPA property detail pages")
    parser.add_argument("--db-uri", default=os.getenv("POSTGRES_URI", DEFAULT_DB_URI))
    parser.add_argument("--limit", type=int, default=0, help="Max properties to scrape (0=all)")
    parser.add_argument("--delay", type=float, default=3.0, help="Seconds between requests")
    parser.add_argument("--only-missing", action="store_true", help="Only scrape properties without details")
    parser.add_argument("--sam-ids", type=str, default="", help="Comma-separated SAM IDs to scrape")
    args = parser.parse_args()

    engine = create_engine(args.db_uri)
    Base.metadata.create_all(
        engine,
        tables=[SamProperty.__table__, SamPropertyImage.__table__, SamScrapeLog.__table__],
    )
    Session = sessionmaker(bind=engine)

    log = SamScrapeLog(
        scrape_type="detail",
        started_at=datetime.now(),
    )

    # Get properties to scrape
    with Session() as db:
        query = db.query(SamProperty).filter_by(is_active=True)
        if args.only_missing:
            query = query.filter(SamProperty.detail_fetched_at.is_(None))
        if args.sam_ids:
            ids = [int(x.strip()) for x in args.sam_ids.split(",")]
            query = query.filter(SamProperty.sam_id.in_(ids))
        if args.limit > 0:
            query = query.limit(args.limit)
        sam_ids = [row.sam_id for row in query.all()]

    print(f"{len(sam_ids)} properties to scrape")

    updated_count = 0
    errors: list[str] = []
    semaphore = asyncio.Semaphore(10)

    async with create_http_client() as client:
        # Initialize session
        print("Initializing session...")
        await client.get("https://sam.or.th/site/npa/page_list.php")

        # Process in chunks
        for chunk_start in range(0, len(sam_ids), CHUNK_SIZE):
            chunk = sam_ids[chunk_start:chunk_start + CHUNK_SIZE]
            chunk_num = chunk_start // CHUNK_SIZE + 1
            total_chunks = (len(sam_ids) + CHUNK_SIZE - 1) // CHUNK_SIZE

            print(f"Chunk {chunk_num}/{total_chunks}: fetching {len(chunk)} details...")

            # Fan-out: fetch all detail pages in this chunk
            tasks = [
                fetch_detail(client, sid, semaphore, args.delay)
                for sid in chunk
            ]
            results = await asyncio.gather(*tasks)

            # Fan-in: parse + save sequentially
            chunk_updated = 0
            with Session() as db:
                for sam_id, html in results:
                    if html is None:
                        errors.append(f"SAM {sam_id}: fetch failed")
                        continue

                    detail = parse_detail_page(sam_id, html)
                    if detail is None:
                        print(f"    Warning: Could not parse SAM ID {sam_id}")
                        continue

                    prop = db.query(SamProperty).filter_by(sam_id=sam_id).first()
                    if prop:
                        update_property_from_detail(db, prop, detail)
                        chunk_updated += 1
                    else:
                        print(f"    Warning: SAM ID {sam_id} not in DB")

                db.commit()

            updated_count += chunk_updated
            print(f"   {chunk_updated} updated, {len([r for r in results if r[1] is None])} errors")

    with Session() as db:
        db.add(SamScrapeLog(
            scrape_type="detail",
            started_at=log.started_at,
            finished_at=datetime.now(),
            pages_scraped=len(sam_ids),
            items_parsed=len(sam_ids),
            items_updated=updated_count,
            error_message="\n".join(errors[:20]) if errors else None,
        ))
        db.commit()

    print(f"\nDone: {updated_count} updated, {len(errors)} errors")


if __name__ == "__main__":
    asyncio.run(main())

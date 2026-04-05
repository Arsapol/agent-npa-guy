#!/usr/bin/env python3
"""
ZMyHome project market data lookup.

Usage:
  python zmyhome_lookup.py "circle condominium"
  python zmyhome_lookup.py "เซอร์เคิล คอนโดมิเนียม"
  python zmyhome_lookup.py --id 12971

Outputs:
  - Price range (buy/rent/sold/rented)
  - Current active listings with per-unit prices + sqm
  - Government appraisal values (กรมธนารักษ์)
  - Project details (year built, units, floors)
"""

import argparse
import json
import re
import sys
from typing import Optional

import httpx
from pydantic import BaseModel, Field
from selectolax.parser import HTMLParser

UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
BASE = "https://zmyhome.com"


class ListingCard(BaseModel):
    property_id: str
    project_id: Optional[str] = None
    project_name: Optional[str] = None
    price_thb: Optional[int] = None
    price_psm: Optional[int] = None
    size_sqm: Optional[float] = None
    bedrooms: Optional[str] = None
    bathrooms: Optional[str] = None
    floor: Optional[str] = None
    direction: Optional[str] = None
    broker_ok: Optional[bool] = None


class ProjectSummary(BaseModel):
    project_id: str
    project_code: str
    name: str
    developer: Optional[str] = None
    year_built: Optional[str] = None
    total_units: Optional[int] = None
    num_floors: Optional[str] = None
    common_area_fee: Optional[str] = None
    # Listing type summaries: {type: {count, price_min, price_max, last_date}}
    listing_summary: dict = Field(default_factory=dict)
    # Sale listings
    sale_listings: list[ListingCard] = Field(default_factory=list)
    # Rent listings
    rent_listings: list[ListingCard] = Field(default_factory=list)
    # Government appraisal: list of {building, floor, price_psm, unit_type}
    gov_appraisal: list[dict] = Field(default_factory=list)


def make_client() -> httpx.Client:
    return httpx.Client(
        headers={"User-Agent": UA},
        follow_redirects=True,
        timeout=20,
    )


def search_project(client: httpx.Client, term: str) -> list[dict]:
    """Return projects matching search term via autocomplete API.

    Requires X-Requested-With: XMLHttpRequest header — without it the
    endpoint returns an empty response (Yii2 AJAX detection).
    """
    r = client.get(
        f"{BASE}/search/load-point",
        params={"term": term},
        headers={"X-Requested-With": "XMLHttpRequest"},
    )
    r.raise_for_status()
    if not r.text.strip():
        return []
    return [x for x in r.json() if x.get("namemodel") == "Project"]


def parse_price_raw(raw: str) -> tuple[Optional[int], Optional[int]]:
    """Parse '3,609,000107,699 ฿/ม2' into (price_thb, price_psm).

    The site concatenates total price + price/sqm without any separator.
    Split heuristic: find the rightmost point where total % 1000 == 0
    (Thai property prices are always rounded to at least 100 or 1000 THB),
    and psm falls in plausible range [100, 999999].
    """
    raw = raw.replace("\xa0", "").strip()
    baht_pos = raw.find("฿")
    if baht_pos < 0:
        return None, None
    combined = re.sub(r"[^\d]", "", raw[:baht_pos])
    if not combined:
        return None, None

    for modulo in [1000, 500, 100]:
        for split_pos in range(len(combined) - 2, 3, -1):
            total_c = int(combined[:split_pos])
            psm_c = int(combined[split_pos:])
            if total_c >= 5000 and total_c % modulo == 0 and 100 <= psm_c <= 999999:
                return total_c, psm_c

    return None, None


def parse_size_raw(raw: str) -> tuple[Optional[float], Optional[bool]]:
    """Parse '33.51  ม2ไม่รับนายหน้า' into (size_sqm, broker_ok)."""
    raw = raw.replace("\xa0", "").strip()
    m = re.match(r"([\d.]+)\s*ม2", raw)
    size = float(m.group(1)) if m else None
    broker_ok = "รับนายหน้า" in raw and "ไม่รับ" not in raw
    return size, broker_ok


def parse_listing_cards(html: str) -> list[ListingCard]:
    tree = HTMLParser(html)
    cards = []
    for article in tree.css("article.card-property__item--article"):
        link = article.css_first('a[href^="/property/"]')
        prop_id = link.attrs["href"].split("/")[-1] if link else ""

        # Extract project info from project link
        proj_link = article.css_first('a[href*="/project/"]')
        proj_id = None
        proj_name = None
        if proj_link:
            href = proj_link.attrs.get("href", "")
            # href like /project/V663 or https://zmyhome.com/project/V663
            parts = href.rstrip("/").split("/")
            proj_id = parts[-1] if parts else None
            proj_name = proj_link.text(strip=True) or None

        price_node = article.css_first(".card-property__price-room--priceRoom")
        price_raw = price_node.text(strip=True) if price_node else ""
        price_thb, price_psm = parse_price_raw(price_raw)

        unit_node = article.css_first(".card-property__price-room--unitRoom")
        unit_raw = unit_node.text(strip=True) if unit_node else ""
        size_sqm, broker_ok = parse_size_raw(unit_raw)

        meta_items = [
            m.text(strip=True)
            for m in article.css(".card-property__meta-info__size-list li")
        ]
        bedrooms = meta_items[0] if len(meta_items) > 0 else None
        bathrooms = meta_items[1] if len(meta_items) > 1 else None
        floor_str = meta_items[2] if len(meta_items) > 2 else None
        direction = meta_items[3] if len(meta_items) > 3 else None

        cards.append(
            ListingCard(
                property_id=prop_id,
                project_id=proj_id,
                project_name=proj_name,
                price_thb=price_thb,
                price_psm=price_psm,
                size_sqm=size_sqm,
                bedrooms=bedrooms,
                bathrooms=bathrooms,
                floor=floor_str,
                direction=direction,
                broker_ok=broker_ok,
            )
        )
    return cards


def fetch_project_page(client: httpx.Client, project_id: str) -> ProjectSummary:
    r = client.get(f"{BASE}/project/V{project_id}")
    r.raise_for_status()
    html = r.text
    tree = HTMLParser(html)

    # Project name from h2
    h2 = tree.css_first("h2")
    name = h2.text(strip=True) if h2 else ""

    # Listing summary from #nav_announce
    listing_summary = {}
    for item in tree.css("#nav_announce .nav-announce__item"):
        link = item.css_first("a")
        href = link.attrs.get("href", "") if link else ""
        listing_type_raw = (item.css_first("strong") or item).text(strip=True)
        counter = item.css_first(".counter")
        count_text = counter.text(strip=True).strip("()") if counter else "0"
        price_range_node = item.css_first(".nav-announce__item__meta-price")
        price_range = price_range_node.text(strip=True) if price_range_node else ""
        last_date_node = item.css_first(".nav-announce__item__meta-date")
        last_date = last_date_node.text(strip=True) if last_date_node else ""

        # Extract min/max from "ช่วงราคา X - Y บาท"
        pm = re.search(r"([\d,]+)\s*-\s*([\d,]+)\s*บาท", price_range)
        price_min = int(pm.group(1).replace(",", "")) if pm else None
        price_max = int(pm.group(2).replace(",", "")) if pm else None

        listing_summary[listing_type_raw] = {
            "count": int(count_text) if count_text.isdigit() else 0,
            "price_min": price_min,
            "price_max": price_max,
            "last_date": last_date,
            "href": href,
        }

    # Project info from li items
    developer = year_built = total_units = num_floors = common_fee = None
    for li in tree.css("li"):
        text = li.text(strip=True)
        if "ผู้พัฒนา" in text:
            developer = re.sub(r"ผู้พัฒนา\s*:\s*", "", text).strip()
        elif "ปีที่สร้างเสร็จ" in text:
            m = re.search(r"(\d{4})", text)
            year_built = m.group(1) if m else text
        elif "ยูนิตทั้งหมด" in text:
            m = re.search(r"([\d,]+)", text)
            if m:
                total_units = int(m.group(1).replace(",", ""))
        elif "จำนวนชั้น" in text:
            num_floors = re.sub(r"จำนวนชั้น\s*", "", text).strip()
        elif "ค่าส่วนกลาง" in text:
            common_fee = re.sub(r"ค่าส่วนกลาง\s*", "", text).strip()

    # Government appraisal from first table
    gov_appraisal = []
    tables = tree.css("table")
    if tables:
        for row in tables[0].css("tr"):
            cells = [td.text(strip=True) for td in row.css("td")]
            if len(cells) >= 3:
                gov_appraisal.append(
                    {
                        "building": cells[0],
                        "floor": cells[1],
                        "price_psm": cells[2],
                        "unit_type": cells[3] if len(cells) > 3 else "",
                    }
                )

    return ProjectSummary(
        project_id=project_id,
        project_code=f"V{project_id}",
        name=name,
        developer=developer,
        year_built=year_built,
        total_units=total_units,
        num_floors=num_floors,
        common_area_fee=common_fee,
        listing_summary=listing_summary,
        gov_appraisal=gov_appraisal,
    )


def fetch_listings(
    client: httpx.Client, project_id: str, listing_type: str = "buy"
) -> list[ListingCard]:
    """listing_type: buy | rent | sold | rented"""
    r = client.get(f"{BASE}/{listing_type}/condo/project-list/{project_id}")
    r.raise_for_status()
    return parse_listing_cards(r.text)


def print_summary(summary: ProjectSummary) -> None:
    print(f"\n{'=' * 60}")
    print(f"Project: {summary.name}")
    print(f"Code: {summary.project_code} | ID: {summary.project_id}")
    print(f"Developer: {summary.developer or 'N/A'}")
    print(f"Year built: {summary.year_built or 'N/A'}")
    print(f"Total units: {summary.total_units or 'N/A'}")
    print(f"Floors: {summary.num_floors or 'N/A'}")
    print(f"Common fee: {summary.common_area_fee or 'N/A'}")
    print()

    print("--- Listing Summary ---")
    for ltype, data in summary.listing_summary.items():
        mn = f"{data['price_min']:,}" if data["price_min"] else "N/A"
        mx = f"{data['price_max']:,}" if data["price_max"] else "N/A"
        print(f"  {ltype} ({data['count']}): {mn} - {mx} THB | {data['last_date']}")
    print()

    if summary.sale_listings:
        print("--- Sale Listings ---")
        for c in summary.sale_listings:
            price = f"{c.price_thb:,}" if c.price_thb else "N/A"
            psm = f"{c.price_psm:,}" if c.price_psm else "N/A"
            print(
                f"  {c.property_id}: {price} THB | {psm} ฿/m² | {c.size_sqm}m² | {c.bedrooms} | {c.floor} | {c.direction}"
            )
    print()

    if summary.rent_listings:
        print("--- Rental Listings ---")
        for c in summary.rent_listings:
            price = f"{c.price_thb:,}" if c.price_thb else "N/A"
            psm = f"{c.price_psm:,}" if c.price_psm else "N/A"
            print(
                f"  {c.property_id}: {price}/mo | {psm} ฿/m²/mo | {c.size_sqm}m² | {c.bedrooms} | {c.floor}"
            )
    print()

    if summary.gov_appraisal:
        print("--- Government Appraisal (กรมธนารักษ์) ---")
        for row in summary.gov_appraisal[:10]:
            print(
                f"  Bldg {row['building']} Fl {row['floor']}: {row['price_psm']} THB/m² ({row['unit_type'][:30]})"
            )
        if len(summary.gov_appraisal) > 10:
            print(f"  ... +{len(summary.gov_appraisal) - 10} more rows")
    print()


def lookup(
    project_name: Optional[str] = None, project_id: Optional[str] = None
) -> ProjectSummary:
    with make_client() as client:
        # Initialize session
        client.get(BASE)

        if not project_id:
            results = search_project(client, project_name)
            if not results:
                raise ValueError(f"No projects found for: {project_name!r}")
            if len(results) > 1:
                print(f"Multiple matches, using first: {results[0]['label']}")
                for r in results:
                    print(f"  id={r['id']}, label={r['label']}")
            project_id = results[0]["id"]

        summary = fetch_project_page(client, project_id)
        summary.sale_listings = fetch_listings(client, project_id, "buy")
        summary.rent_listings = fetch_listings(client, project_id, "rent")

    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="ZMyHome project market lookup")
    parser.add_argument("name", nargs="?", help="Project name to search")
    parser.add_argument(
        "--id", dest="project_id", help="Project numeric ID (skip search)"
    )
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    if not args.name and not args.project_id:
        parser.print_help()
        sys.exit(1)

    summary = lookup(project_name=args.name, project_id=args.project_id)

    if args.json:
        print(json.dumps(summary.model_dump(), ensure_ascii=False, indent=2))
    else:
        print_summary(summary)


if __name__ == "__main__":
    main()

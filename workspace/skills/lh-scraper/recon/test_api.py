"""
LH Bank NPA Scraper - Recon Test Script
Validates listing page parsing and detail page field extraction.

Site: https://www.lhbank.co.th/th/property-for-sale/asset-for-sale/
Method: Server-rendered HTML (ASP.NET WebForms / Kentico CMS)
All properties are pre-rendered in a single HTML page with client-side JS pagination.
Detail pages have GPS coordinates in hidden inputs.

Usage:
    python test_api.py                    # Full test: listings + detail + GPS check
    python test_api.py --detail LH031A    # Fetch specific detail page only
"""

import argparse
import asyncio
import re

import httpx
from pydantic import BaseModel, Field
from selectolax.parser import HTMLParser

BASE_URL = "https://www.lhbank.co.th"
LISTING_URL = f"{BASE_URL}/th/property-for-sale/asset-for-sale/"
DETAIL_URL = f"{BASE_URL}/th/property-for-sale/detail/"
HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class LHListItem(BaseModel):
    asset_code: str
    asset_param: str = "1"
    asset_type: str = ""
    area_text: str = ""
    price: int | None = None
    address: str = ""
    thumbnail: str = ""
    detail_url: str = ""


class LHDetail(BaseModel):
    asset_code: str = ""
    asking_price: int | None = None
    case_info: str = ""           # ข้อมูลคดี (e.g. "สินทรัพย์ธนาคาร")
    status_desc: str = ""         # สถานะ (free-text: bedrooms, condition, etc.)
    asset_type: str = ""          # ประเภทสินทรัพย์
    location: str = ""            # ที่ตั้งสินทรัพย์
    area_text: str = ""           # เนื้อที่/พื้นที่ใช้สอย
    record_date: str = ""         # วันที่บันทึก
    latitude: float | None = None
    longitude: float | None = None
    map_image_url: str = ""
    pdf_url: str = ""
    image_urls: list[str] = Field(default_factory=list)


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
# Listing page parsing
# ---------------------------------------------------------------------------

def parse_listing_cards(html: str) -> list[LHListItem]:
    """Parse all property cards from the listing page.

    Cards live inside `.item.asset-for-sale-bank` divs.
    All properties (currently 33) are pre-rendered; JS paginates client-side
    in `.content[data-id]` containers of 9 cards each.
    """
    tree = HTMLParser(html)
    items: list[LHListItem] = []

    for card in tree.css(".item.asset-for-sale-bank"):
        # Detail URL from onclick on .item-detail-asset-for-sale
        detail_div = card.css_first(".item-detail-asset-for-sale")
        onclick = detail_div.attributes.get("onclick", "") if detail_div else ""

        url_match = re.search(r"href='([^']+)'", onclick)
        detail_url = _abs_url(url_match.group(1).replace("&amp;", "&")) if url_match else ""

        code_match = re.search(r"AssetCode=(\w+)", onclick)
        asset_code = code_match.group(1) if code_match else ""

        asset_match = re.search(r"Asset=(\d+)", onclick)
        asset_param = asset_match.group(1) if asset_match else "1"

        # Field rows in .grid-cards-text
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

        # Address from .text-address-asset
        addr_el = card.css_first(".text-address-asset")
        address = addr_el.text(strip=True) if addr_el else ""

        # Price from .font-size-price
        price_el = card.css_first(".font-size-price")
        price = _parse_price(price_el.text(strip=True)) if price_el else None

        # Thumbnail image
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
# Detail page parsing
# ---------------------------------------------------------------------------

# Label text -> model field mapping
_DETAIL_LABEL_MAP = {
    "ราคาประกาศขาย": "asking_price",
    "ข้อมูลคดี": "case_info",
    "สถานะ": "status_desc",
    "ประเภทสินทรัพย์": "asset_type",
    "ที่ตั้งสินทรัพย์": "location",
    "เนื้อที่/พื้นที่ใช้สอย": "area_text",
    "วันที่บันทึก": "record_date",
}


def parse_detail_page(html: str) -> LHDetail:
    """Parse a property detail page.

    CSS structure:
      .page-detail.assets-for-sale-detail
        .assets-for-sale-gallery  -> images
        .assets-for-sale-description
          h1  -> "รหัสสินทรัพย์:LH031A"
          div.d-table
            div.d-table-cell.label  -> field label
            div.d-table-cell        -> field value

    Hidden inputs (name ends with):
      hdfAssetCode  -> asset code
      hdfLatitude   -> GPS latitude
      hdfLongitude  -> GPS longitude
      hdfMap        -> map image path
      hdfPDF        -> PDF attachment path
    """
    tree = HTMLParser(html)
    fields: dict[str, str] = {}

    # Parse label-value pairs from .assets-for-sale-description
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

    # Asset code from H1
    h1 = tree.css_first(".assets-for-sale-description h1")
    h1_text = h1.text(strip=True) if h1 else ""
    code_match = re.search(r"[A-Z]+\d+\w*", h1_text)
    asset_code = code_match.group(0) if code_match else ""

    # Hidden inputs (GPS, map, PDF)
    hidden: dict[str, str] = {}
    for inp in tree.css("input[type='hidden']"):
        name = inp.attributes.get("name", "") or ""
        value = inp.attributes.get("value", "") or ""
        # Use the last segment after $ as key
        key = name.split("$")[-1] if "$" in name else name
        if key in ("hdfLatitude", "hdfLongitude", "hdfMap", "hdfPDF", "hdfAssetCode"):
            hidden[key] = value

    # Parse GPS
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

    # Images from gallery
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
# Main test
# ---------------------------------------------------------------------------

async def main(detail_code: str | None = None):
    async with httpx.AsyncClient(
        timeout=30, follow_redirects=True, headers=HEADERS
    ) as client:

        if detail_code:
            print(f"Fetching detail: {detail_code}")
            r = await client.get(DETAIL_URL, params={"AssetCode": detail_code, "Asset": "1"})
            detail = parse_detail_page(r.text)
            print(detail.model_dump_json(indent=2))
            return

        # --- Listing page ---
        print("=" * 60)
        print("LISTING PAGE TEST")
        print("=" * 60)
        r = await client.get(LISTING_URL)
        cards = parse_listing_cards(r.text)
        print(f"Total properties: {len(cards)}")

        type_counts: dict[str, int] = {}
        for c in cards:
            t = c.asset_type
            type_counts[t] = type_counts.get(t, 0) + 1

        print("\nType distribution:")
        for t, count in sorted(type_counts.items(), key=lambda x: -x[1]):
            print(f"  {t or '(empty)'}: {count}")

        print("\nAll properties:")
        for c in cards:
            print(f"  {c.asset_code:10s} | {c.asset_type:25s} | {c.price or 0:>12,} | {c.address[:50]}")

        # --- Detail page (condo sample) ---
        condos = [c for c in cards if "คอนโด" in c.asset_type]
        sample = condos[0] if condos else cards[0]

        print(f"\n{'=' * 60}")
        print(f"DETAIL PAGE TEST ({sample.asset_code})")
        print("=" * 60)
        r2 = await client.get(DETAIL_URL, params={"AssetCode": sample.asset_code, "Asset": "1"})
        detail = parse_detail_page(r2.text)
        print(detail.model_dump_json(indent=2))

        # --- GPS availability check (first 10) ---
        print(f"\n{'=' * 60}")
        print("GPS AVAILABILITY CHECK (first 10)")
        print("=" * 60)
        gps_count = 0
        for c in cards[:10]:
            r_d = await client.get(DETAIL_URL, params={"AssetCode": c.asset_code, "Asset": "1"})
            d = parse_detail_page(r_d.text)
            has_gps = d.latitude is not None and d.longitude is not None
            if has_gps:
                gps_count += 1
            gps_info = f" ({d.latitude}, {d.longitude})" if has_gps else ""
            print(f"  {c.asset_code}: GPS={'YES' if has_gps else 'NO'}{gps_info}")

        print(f"\nGPS availability: {gps_count}/10 checked")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LH Bank NPA Recon")
    parser.add_argument("--detail", type=str, help="Fetch detail for specific asset code")
    args = parser.parse_args()
    asyncio.run(main(detail_code=args.detail))

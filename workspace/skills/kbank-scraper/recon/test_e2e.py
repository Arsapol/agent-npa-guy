"""
KBank NPA Scraper — End-to-end test script.
Tests both list API (httpx) and detail page extraction (Playwright + selectolax).
"""

import asyncio
import json
import re
import time
from pathlib import Path

import httpx
from playwright.async_api import async_playwright
from playwright_stealth import Stealth
from selectolax.parser import HTMLParser

stealth = Stealth()

OUTPUT_DIR = Path(__file__).parent

# ─── List API ────────────────────────────────────────────────────────

LIST_URL = "https://www.kasikornbank.com/Custom/KWEB2020/NPA2023Backend13.aspx/GetProperties"
LIST_HEADERS = {
    "Content-Type": "application/json",
    "Accept": "*/*",
    "X-Requested-With": "XMLHttpRequest",
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/146.0.0.0 Safari/537.36"
    ),
    "Referer": "https://www.kasikornbank.com/th/propertyforsale/search/pages/index.aspx",
    "Origin": "https://www.kasikornbank.com",
}


async def test_list_api() -> list[dict]:
    """Test list API: pagination, filters, and field extraction."""
    print("=" * 60)
    print("TEST 1: List API (GetProperties)")
    print("=" * 60)

    async with httpx.AsyncClient(timeout=60.0) as client:

        async def fetch_list(filter_obj: dict) -> dict:
            r = await client.post(LIST_URL, headers=LIST_HEADERS, json={"filter": filter_obj})
            assert r.status_code == 200, f"HTTP {r.status_code}"
            return json.loads(json.loads(r.text)["d"])

        # 1a. Basic fetch
        print("\n[1a] Basic fetch (PageSize=5, Page 1)...")
        p1 = await fetch_list({
            "PageSize": 5,
            "CurrentPageIndex": 1,
            "SearchPurposes": ["AllProperties"],
        })
        assert p1["Success"], "API returned Success=false"
        total = p1["Data"]["TotalRows"]
        items1 = p1["Data"]["Items"]
        ids1 = [i["PropertyID"] for i in items1]
        print(f"  Total properties: {total}")
        print(f"  Page 1 IDs: {ids1}")
        assert len(items1) == 5, f"Expected 5 items, got {len(items1)}"
        print("  PASS")

        await asyncio.sleep(1)

        # 1b. Pagination
        print("\n[1b] Pagination (Page 2)...")
        p2 = await fetch_list({
            "PageSize": 5,
            "CurrentPageIndex": 2,
            "SearchPurposes": ["AllProperties"],
        })
        ids2 = [i["PropertyID"] for i in p2["Data"]["Items"]]
        print(f"  Page 2 IDs: {ids2}")
        assert ids1 != ids2, "Page 1 and 2 returned same items!"
        assert len(set(ids1) & set(ids2)) == 0, "Overlap between pages!"
        print("  PASS — pages are distinct")

        await asyncio.sleep(1)

        # 1c. Province filter
        print("\n[1c] Province filter (BKK=10)...")
        bkk = await fetch_list({
            "PageSize": 5,
            "CurrentPageIndex": 1,
            "Provinces": [10],
            "SearchPurposes": ["AllProperties"],
        })
        bkk_total = bkk["Data"]["TotalRows"]
        bkk_provinces = [i["ProvinceName"] for i in bkk["Data"]["Items"]]
        print(f"  BKK total: {bkk_total} (vs {total} all)")
        print(f"  Provinces: {bkk_provinces}")
        assert bkk_total < total, "Filter didn't reduce results"
        assert all(p == "กรุงเทพมหานคร" for p in bkk_provinces), "Non-BKK result!"
        print("  PASS")

        await asyncio.sleep(1)

        # 1d. Property type filter
        print("\n[1d] PropertyType filter (05=Condo)...")
        condo = await fetch_list({
            "PageSize": 5,
            "CurrentPageIndex": 1,
            "PropertyTypes": ["05"],
            "SearchPurposes": ["AllProperties"],
        })
        condo_total = condo["Data"]["TotalRows"]
        condo_types = [i["PropertyTypeName"] for i in condo["Data"]["Items"]]
        print(f"  Condo total: {condo_total}")
        print(f"  Types: {condo_types}")
        assert condo_total < total, "Filter didn't reduce results"
        assert all("คอนโด" in t for t in condo_types), "Non-condo result!"
        print("  PASS")

        await asyncio.sleep(1)

        # 1e. Field completeness check
        print("\n[1e] Field completeness check...")
        sample = items1[0]
        expected_fields = [
            "PropertyID", "PropertyIDFormat", "SellPrice", "PromotionPrice",
            "AdjustPrice", "PropertyTypeName", "ProvinceName", "AmphurName",
            "TambonName", "VillageTH", "SoiTH", "RoadTH", "Latitude",
            "Longtitude", "Bedroom", "Bathroom", "BuildingAge", "UseableArea",
            "Rai", "Ngan", "SquareArea", "AreaValue", "Area",
            "PropertyMediaes", "IsNew", "IsHot", "IsReserve", "IsSoldOut",
            "PMMaintenanceStatus", "SourceSaleType", "SourceCode", "AIFlag",
            "PromotionName", "PromotionRemark",
        ]
        present = [f for f in expected_fields if f in sample]
        missing = [f for f in expected_fields if f not in sample]
        print(f"  Present: {len(present)}/{len(expected_fields)}")
        if missing:
            print(f"  Missing: {missing}")
        print(f"  All API keys: {sorted(sample.keys())}")
        print("  PASS" if not missing else "  PARTIAL — some fields missing")

        # 1f. PageSize=50 stress test
        print("\n[1f] Full page fetch (PageSize=50)...")
        full = await fetch_list({
            "PageSize": 50,
            "CurrentPageIndex": 1,
            "SearchPurposes": ["AllProperties"],
        })
        assert len(full["Data"]["Items"]) == 50, f"Got {len(full['Data']['Items'])} items"
        print(f"  Got 50 items. Estimated pages for full scrape: {(total + 49) // 50}")
        print("  PASS")

    return items1


# ─── Detail Page ─────────────────────────────────────────────────────

DETAIL_BASE = "https://www.kasikornbank.com/th/propertyforsale/detail"


def parse_detail_html(html: str) -> dict:
    """Extract title deed, nearby places, and full address from detail HTML."""
    tree = HTMLParser(html)
    result = {}

    # 1. Full address — .location-container p
    addr_node = tree.css_first(".location-container p")
    if addr_node:
        result["full_address"] = addr_node.text(strip=True)

    # 2. Title deed — look in .property-info / .property-table rows
    for row in tree.css(".property-info .property-row, .property-table .property-row"):
        cells = row.css(".property-td")
        if len(cells) >= 2:
            label = cells[0].text(strip=True)
            value = cells[1].text(strip=True)
            if "โฉนด" in label or "เอกสารสิทธิ์" in label:
                result["deed_type"] = value
            if "เลขที่" in label and "เอกสารสิทธิ์" in label:
                result["deed_number"] = value

    # Fallback: regex search for deed number
    if "deed_number" not in result:
        deed_match = re.search(r'โฉนด[^<]*?(\d+)', html)
        if deed_match:
            result["deed_number"] = deed_match.group(1)

    # 3. Nearby places — .place-nearby table rows
    nearby = []
    for tr in tree.css(".place-nearby table tbody tr, .place-nearby table tr"):
        cells = tr.css("td")
        if len(cells) >= 2:
            name_node = cells[0].css_first("span.list")
            name = name_node.text(strip=True) if name_node else cells[0].text(strip=True)
            distance = cells[1].text(strip=True)
            if name and distance:
                nearby.append({"name": name, "distance": distance})
    if nearby:
        result["nearby_places"] = nearby

    # 4. JSON-LD (bonus — structured data)
    for script in tree.css('script[type="application/ld+json"]'):
        text = (script.text() or "").replace("\n", " ").replace("\r", " ")
        try:
            ld = json.loads(text)
            if isinstance(ld, dict) and ld.get("@type") in ("Product", "Accommodation"):
                result["json_ld_product"] = ld
            if isinstance(ld, list):
                for item in ld:
                    if isinstance(item, dict) and item.get("@type") in ("Product", "Accommodation"):
                        result["json_ld_product"] = item
        except json.JSONDecodeError:
            pass

    return result


async def test_detail_page(property_ids: list[str]) -> None:
    """Test detail page extraction using Playwright + selectolax."""
    print("\n" + "=" * 60)
    print("TEST 2: Detail Page (Playwright + selectolax)")
    print("=" * 60)

    test_id = property_ids[0]
    detail_url = f"{DETAIL_BASE}/{test_id}.html"
    print(f"\n[2a] Fetching detail page for {test_id}...")
    print(f"  URL: {detail_url}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
        )
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/131.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1440, "height": 900},
            locale="th-TH",
        )
        await stealth.apply_stealth_async(context)
        page = await context.new_page()

        # Visit search page first to get session
        print("  Establishing session via search page...")
        await page.goto(
            "https://www.kasikornbank.com/th/propertyforsale/search/pages/index.aspx",
            wait_until="domcontentloaded",
            timeout=30000,
        )
        await page.wait_for_timeout(3000)

        # Fetch detail page
        print("  Loading detail page...")
        await page.goto(detail_url, wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(5000)
        html = await page.content()
        await browser.close()

    html_size = len(html)
    print(f"  HTML size: {html_size:,} bytes")

    # Check for bot challenge
    if "bm-verify" in html and html_size < 5000:
        print("  FAIL — got Akamai bot challenge page")
        return

    # Save HTML
    out_path = OUTPUT_DIR / f"detail_test_{test_id}.html"
    out_path.write_text(html, encoding="utf-8")
    print(f"  Saved to: {out_path}")

    # Parse
    print("\n[2b] Parsing extracted fields...")
    data = parse_detail_html(html)

    # Check title deed
    print(f"\n  Full address:  {data.get('full_address', 'NOT FOUND')}")
    print(f"  Deed type:     {data.get('deed_type', 'NOT FOUND')}")
    print(f"  Deed number:   {data.get('deed_number', 'NOT FOUND')}")

    # Check nearby places
    nearby = data.get("nearby_places", [])
    print(f"\n  Nearby places: {len(nearby)} found")
    for place in nearby[:5]:
        print(f"    - {place['name']}: {place['distance']}")
    if len(nearby) > 5:
        print(f"    ... and {len(nearby) - 5} more")

    # Check JSON-LD
    ld = data.get("json_ld_product")
    if ld:
        print(f"\n  JSON-LD Product ID: {ld.get('productID', 'N/A')}")
        offers = ld.get("offers", {})
        print(f"  JSON-LD Price: {offers.get('price', 'N/A')}")

    # Validation
    checks = {
        "full_address": data.get("full_address") is not None,
        "deed_number": data.get("deed_number") is not None,
        "nearby_places": len(nearby) > 0,
    }
    print("\n  Validation:")
    all_pass = True
    for check, passed in checks.items():
        status = "PASS" if passed else "FAIL"
        if not passed:
            all_pass = False
        print(f"    {check}: {status}")

    if all_pass:
        print("\n  ALL CHECKS PASSED")
    else:
        print("\n  SOME CHECKS FAILED — selectors may need adjustment")

    # Save parsed data
    parsed_path = OUTPUT_DIR / f"detail_parsed_{test_id}.json"
    parsed_path.write_text(json.dumps(data, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print(f"\n  Parsed data saved to: {parsed_path}")


# ─── Main ────────────────────────────────────────────────────────────

async def main() -> None:
    print("KBank NPA Scraper — End-to-End Test")
    print("=" * 60)

    # Test list API
    items = await test_list_api()
    property_ids = [i["PropertyID"] for i in items]

    # Test detail page
    await test_detail_page(property_ids)

    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

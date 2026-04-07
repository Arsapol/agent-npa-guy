"""
BAY/Krungsri (krungsriproperty.com) API test script.

Tests the two-step scraping strategy:
1. Discover property codes from search-result HTML
2. Fetch full details via /Helpers/GetProperties JSON API
"""

import re
import json
import sys
from pathlib import Path

import httpx

BASE_URL = "https://www.krungsriproperty.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}
API_HEADERS = {
    **HEADERS,
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": f"{BASE_URL}/home",
}

CODE_PATTERN = re.compile(r"[A-Z]{1,3}[XYZ]\d{3,5}(?:_[A-Z]+\d+)?")


def test_discover_codes() -> list[str]:
    """Step 1: Discover all property codes from search-result page."""
    print("=" * 60)
    print("TEST 1: Discover property codes from search-result HTML")
    print("=" * 60)

    resp = httpx.get(
        f"{BASE_URL}/search-result",
        params={"keyWord": ""},
        headers=HEADERS,
        follow_redirects=True,
        timeout=30,
    )
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"

    # Extract total from JS pagination
    total_match = re.findall(r"_convertDatasource\((\d+)\)", resp.text)
    total = int(total_match[0]) if total_match else 0
    print(f"  Declared total: {total}")

    # Extract all codes
    codes = sorted(set(CODE_PATTERN.findall(resp.text)))
    print(f"  Unique codes extracted: {len(codes)}")
    print(f"  Sample codes: {codes[:5]}")

    assert len(codes) > 1000, f"Expected >1000 codes, got {len(codes)}"
    print("  PASS")
    return codes


def test_discover_by_category() -> dict[str, int]:
    """Test category-filtered search totals."""
    print("\n" + "=" * 60)
    print("TEST 2: Category filter totals")
    print("=" * 60)

    categories = {"A": "บ้านเดี่ยว", "B": "ทาวน์เฮาส์", "C": "คอนโดมิเนียม", "D": "อาคารพาณิชย์", "E": "ที่ดินเปล่า", "F": "อื่นๆ"}
    totals = {}

    for cat_code, cat_name in categories.items():
        resp = httpx.get(
            f"{BASE_URL}/search-result",
            params={"keyWord": "", "category": cat_code},
            headers=HEADERS,
            follow_redirects=True,
            timeout=30,
        )
        total_match = re.findall(r"_convertDatasource\((\d+)\)", resp.text)
        total = int(total_match[0]) if total_match else 0
        totals[cat_code] = total
        print(f"  Category {cat_code} ({cat_name}): {total}")

    assert totals.get("A", 0) > 0, "Expected category A to have properties"
    print("  PASS")
    return totals


def test_get_properties_single(code: str = "AX1185") -> dict:
    """Test GetProperties with a single known code."""
    print("\n" + "=" * 60)
    print(f"TEST 3: GetProperties single code ({code})")
    print("=" * 60)

    resp = httpx.get(
        f"{BASE_URL}/Helpers/GetProperties",
        params={"listCodes": code, "pageNumber": "1", "pageSize": "1", "orderBy": ""},
        headers=API_HEADERS,
        follow_redirects=True,
        timeout=30,
    )
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    assert "application/json" in resp.headers.get("content-type", ""), "Expected JSON response"

    data = resp.json()
    assert isinstance(data, list), "Expected list response"
    assert len(data) == 1, f"Expected 1 result, got {len(data)}"

    prop = data[0]
    print(f"  Code: {prop['code']}")
    print(f"  Project: {prop['project']}")
    print(f"  Type: {prop['propertyTypeName']}")
    print(f"  Location: {prop['district']}, {prop['province']}")
    print(f"  GPS: {prop['lati']}, {prop['long']}")
    print(f"  Sale: {prop['salePrice']:,.0f} THB")
    print(f"  Promo: {prop['promoPrice']:,.0f} THB")
    print(f"  Discount: {prop['discount']}%")
    print(f"  Deed: {prop['deedNo']}")
    print(f"  Beds/Baths/Park: {prop['bedCount']}/{prop['bathCount']}/{prop['parkCount']}")
    print(f"  Land: {prop['sizeText']}")
    print(f"  Cover image: {prop['coverImageUrl']}")
    print(f"  Fields count: {len(prop.keys())}")

    # Validate key fields exist
    required_fields = [
        "code", "project", "propertyTypeName", "lati", "long",
        "salePrice", "promoPrice", "deedNo", "district", "province",
        "bedCount", "bathCount", "coverImageUrl", "isCondo",
    ]
    for field in required_fields:
        assert field in prop, f"Missing field: {field}"

    print("  PASS")
    return prop


def test_get_properties_batch(codes: list[str]) -> list[dict]:
    """Test GetProperties with a batch of codes."""
    print("\n" + "=" * 60)
    print(f"TEST 4: GetProperties batch ({len(codes)} codes)")
    print("=" * 60)

    batch = codes[:50]
    codes_str = ",".join(batch)

    resp = httpx.get(
        f"{BASE_URL}/Helpers/GetProperties",
        params={"listCodes": codes_str, "pageNumber": "1", "pageSize": "100", "orderBy": ""},
        headers=API_HEADERS,
        follow_redirects=True,
        timeout=30,
    )
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"

    data = resp.json()
    print(f"  Requested: {len(batch)} codes")
    print(f"  Returned: {len(data)} properties")
    assert len(data) > 0, "Expected at least some results"

    # Check type distribution
    types = {}
    for d in data:
        t = d.get("propertyTypeName", "?")
        types[t] = types.get(t, 0) + 1
    print(f"  Type distribution: {types}")

    # Check all have GPS
    with_gps = sum(1 for d in data if d.get("lati") and d.get("long"))
    print(f"  With GPS: {with_gps}/{len(data)}")

    print("  PASS")
    return data


def test_image_endpoint():
    """Test image URL patterns."""
    print("\n" + "=" * 60)
    print("TEST 5: Image endpoints")
    print("=" * 60)

    # AX1185 itemGUID = a97f6220-9d9f-41c6-9725-143267bfdb30
    guid = "a97f62209d9f41c69725143267bfdb30"

    for label, path in [("thumbnail", "00/01"), ("full cover", "01/01")]:
        url = f"{BASE_URL}/images/{guid}/{path}"
        resp = httpx.get(url, headers=HEADERS, follow_redirects=True, timeout=15)
        ct = resp.headers.get("content-type", "?")
        size = len(resp.content)
        print(f"  {label} ({path}): status={resp.status_code}, type={ct}, size={size:,}")
        assert resp.status_code == 200, f"Expected 200 for {label}"
        if path == "01/01":
            assert size > 10000, f"Expected cover image >10KB, got {size}"

    print("  PASS")


def test_detail_page():
    """Test detail page loads and contains property info."""
    print("\n" + "=" * 60)
    print("TEST 6: Detail page HTML")
    print("=" * 60)

    resp = httpx.get(
        f"{BASE_URL}/detail",
        params={"code": "AX1185"},
        headers=HEADERS,
        follow_redirects=True,
        timeout=30,
    )
    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    assert "AX1185" in resp.text, "Expected code in page"

    from selectolax.parser import HTMLParser
    tree = HTMLParser(resp.text)
    h1_text = (tree.css_first("h1").text() or "").strip() if tree.css_first("h1") else ""
    has_project = "กรีนเนอรี่" in h1_text
    has_deed = "โฉนด" in resp.text

    assert has_project, f"Expected project name in h1, got: {h1_text[:100]}"
    assert has_deed, "Expected deed number (โฉนด) in page"

    print(f"  Page size: {len(resp.text):,} bytes")
    print(f"  Contains code: True")
    print(f"  H1 project name: {h1_text}")
    print(f"  Contains deed info: True")
    print("  PASS")


def main():
    print("BAY/Krungsri API Test Suite")
    print("=" * 60)

    try:
        codes = test_discover_codes()
        test_discover_by_category()
        test_get_properties_single()
        test_get_properties_batch(codes)
        test_image_endpoint()
        test_detail_page()

        print("\n" + "=" * 60)
        print("ALL TESTS PASSED")
        print("=" * 60)
    except AssertionError as e:
        print(f"\nTEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\nERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

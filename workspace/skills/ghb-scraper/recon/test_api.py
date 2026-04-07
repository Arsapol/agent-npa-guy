"""
GHB HomCenter API Recon — Test Script
Demonstrates all discovered endpoints for ghbhomecenter.com

Architecture:
  - Primary data source: Server-rendered HTML (search + detail pages)
  - Secondary data source: REST API at /v3/property/api (location, saved properties)
  - Auth: Anonymous JWT embedded in page HTML (rotates, ~7 day TTL)
  - No dedicated search API — search is GET form submission to /property-for-sale
"""
import asyncio
import json
import re
from pathlib import Path

import httpx
from selectolax.parser import HTMLParser

BASE_URL = "https://www.ghbhomecenter.com"
API_BASE = f"{BASE_URL}/v3/property/api"

HTML_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Accept": "text/html",
}


def _get_jwt_from_page(html: str) -> str | None:
    """Extract the anonymous JWT token from any GHB page's inline JS."""
    match = re.search(r'var\s+accessToken\s*=\s*"([^"]+)"', html)
    return match.group(1) if match else None


def _api_headers(jwt: str) -> dict:
    return {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        "Accept": "application/json",
        "Authorization": f"Bearer {jwt}",
        "token": jwt,
        "source": "mobile",
    }


# ──────────────────────────────────────
# 1. JWT Token Extraction
# ──────────────────────────────────────
async def test_jwt_extraction(client: httpx.AsyncClient) -> str:
    """Fetch homepage and extract the anonymous JWT."""
    r = await client.get(BASE_URL, headers=HTML_HEADERS)
    jwt = _get_jwt_from_page(r.text)
    print(f"[JWT] Extracted token: {jwt[:50]}..." if jwt else "[JWT] FAILED - no token found")
    return jwt or ""


# ──────────────────────────────────────
# 2. Location API (provinces, districts, sub-districts)
# ──────────────────────────────────────
async def test_location_api(client: httpx.AsyncClient, jwt: str):
    """Test the location hierarchy endpoints."""
    hdrs = _api_headers(jwt)

    # Provinces
    r = await client.get(f"{API_BASE}/location/province", headers=hdrs)
    provinces = r.json()
    assert provinces["code"] == 200
    print(f"[Location] Provinces: {len(provinces['data'])} total")

    # Find Bangkok
    bkk = next(p for p in provinces["data"] if p["code"] == "10")
    print(f"  Bangkok: provinceId={bkk['provinceId']} code={bkk['code']}")

    # Districts (amphur) for Bangkok
    r = await client.get(f"{API_BASE}/location/amphur/{bkk['provinceId']}", headers=hdrs)
    amphurs = r.json()
    assert amphurs["code"] == 200
    print(f"  Bangkok districts: {len(amphurs['data'])}")

    # Sub-districts (tumbon) for first amphur
    first_amphur = amphurs["data"][0]
    r = await client.get(f"{API_BASE}/location/tumbon/{first_amphur['amphurId']}", headers=hdrs)
    tumbons = r.json()
    print(f"  Tumbons for {first_amphur['nameTh']}: {len(tumbons.get('data') or [])}")

    return bkk["provinceId"]


# ──────────────────────────────────────
# 3. Keyword Autocomplete (ProxyAPI)
# ──────────────────────────────────────
async def test_keyword_search(client: httpx.AsyncClient):
    """Test the keyword autocomplete endpoint."""
    r = await client.get(
        f"{BASE_URL}/ProxyAPI/search/keyword/สุขุมวิท",
        headers=HTML_HEADERS,
    )
    results = r.json()
    print(f"[Keyword] 'สุขุมวิท' results: {len(results)}")
    if results:
        print(f"  First: {json.dumps(results[0], ensure_ascii=False)[:200]}")


# ──────────────────────────────────────
# 4. HTML Search (Server-Rendered Listing)
# ──────────────────────────────────────
async def test_html_search(client: httpx.AsyncClient):
    """Search via GET request to the listing page (server-rendered HTML)."""
    # Bangkok condos, page 1, sorted by price ascending
    r = await client.get(
        f"{BASE_URL}/property-foryou-for-sale",
        params={"p": "3001", "pt[]": "3", "pg": "1", "st": "PriceAsc"},
        headers=HTML_HEADERS,
    )
    tree = HTMLParser(r.text)

    # Extract total count
    total_text = ""
    for el in tree.css("*"):
        t = (el.text() or "").strip()
        if "รายการ" in t and "ค้นพบ" in t and len(t) < 100:
            total_text = t
            break

    total_match = re.search(r"([\d,]+)\s*รายการ", total_text)
    total = int(total_match.group(1).replace(",", "")) if total_match else 0
    print(f"[HTML Search] Total: {total} properties")

    # Extract property IDs from cards
    ids = set()
    for a in tree.css("a[href*='/property-']"):
        href = a.attributes.get("href") or ""
        m = re.search(r"/property-(\d+)$", href)
        if m:
            ids.add(m.group(1))

    print(f"  Page 1: {len(ids)} properties")
    print(f"  IDs: {sorted(ids)}")

    # Verify page 2 has different data
    r2 = await client.get(
        f"{BASE_URL}/property-foryou-for-sale",
        params={"p": "3001", "pt[]": "3", "pg": "2", "st": "PriceAsc"},
        headers=HTML_HEADERS,
    )
    tree2 = HTMLParser(r2.text)
    ids2 = set()
    for a in tree2.css("a[href*='/property-']"):
        href = a.attributes.get("href") or ""
        m = re.search(r"/property-(\d+)$", href)
        if m:
            ids2.add(m.group(1))
    overlap = ids & ids2
    print(f"  Page 2: {len(ids2)} properties, overlap: {len(overlap)}")

    return sorted(ids)[0] if ids else None


# ──────────────────────────────────────
# 5. HTML Detail Page Parsing
# ──────────────────────────────────────
async def test_html_detail(client: httpx.AsyncClient, property_id: str):
    """Parse a property detail page for all available fields."""
    r = await client.get(f"{BASE_URL}/property-{property_id}", headers=HTML_HEADERS)
    tree = HTMLParser(r.text)
    html = r.text

    detail = {}

    # Title from h1
    for h1 in tree.css("h1"):
        t = (h1.text() or "").strip()
        if t and len(t) < 100:
            detail["title"] = t
            break

    # Price from h3.text-price
    for h3 in tree.css("h3.text-price"):
        t = (h3.text() or "").strip()
        if t:
            detail["price"] = t
            break

    # Key-value pairs from .row > .col layout
    for row in tree.css(".row"):
        cols = row.css("[class*='col-']")
        if len(cols) >= 2:
            label = (cols[0].text() or "").strip()
            value = (cols[1].text() or "").strip()
            if label and value and len(label) < 60 and len(value) < 100:
                if not any(k in label + value for k in ["function", "var ", "$(", "document"]):
                    detail[label] = value

    # GPS from Google Maps link
    gps = re.findall(r"daddr=([\d.]+),([\d.]+)", html)
    if gps:
        detail["gps_lat"] = float(gps[0][0])
        detail["gps_lon"] = float(gps[0][1])

    # GPS from JS variables (alternative)
    geo_lat = re.search(r"var\s+geoLat\s*=\s*([\d.]+)", html)
    geo_lon = re.search(r"var\s+geoLong\s*=\s*([\d.]+)", html)
    if geo_lat:
        detail["gps_lat"] = float(geo_lat.group(1))
    if geo_lon:
        detail["gps_lon"] = float(geo_lon.group(1))

    # Images
    media_ids = sorted(set(re.findall(r"/v3/property/api/Media/(\d+)(?!-)", html)))
    detail["images"] = [f"{BASE_URL}/v3/property/api/Media/{mid}" for mid in media_ids]

    # Meta tags
    for meta in tree.css("meta"):
        name = meta.attributes.get("name") or meta.attributes.get("property") or ""
        content = meta.attributes.get("content") or ""
        if name in ("description", "og:title", "og:description", "og:image"):
            detail[f"meta_{name}"] = content

    print(f"[Detail] Property {property_id}:")
    for k, v in detail.items():
        if k != "images":
            print(f"  {k}: {v}")
    print(f"  images: {len(detail.get('images', []))} photos")

    return detail


# ──────────────────────────────────────
# Main
# ──────────────────────────────────────
async def main():
    async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
        print("=" * 60)
        print("GHB HomCenter API Recon")
        print("=" * 60)

        # 1. Extract JWT
        jwt = await test_jwt_extraction(client)
        print()

        # 2. Location API
        await test_location_api(client, jwt)
        print()

        # 3. Keyword autocomplete
        await test_keyword_search(client)
        print()

        # 4. HTML search
        first_id = await test_html_search(client)
        print()

        # 5. Detail page
        if first_id:
            await test_html_detail(client, first_id)

        print()
        print("=" * 60)
        print("Recon complete!")


if __name__ == "__main__":
    asyncio.run(main())

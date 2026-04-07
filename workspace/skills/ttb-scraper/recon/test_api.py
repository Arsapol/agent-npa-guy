"""
TTB/PAMCO Property API — Recon & Test Script
=============================================
Site: https://property.pamco.co.th/
API:  https://property-api-prod.automer.io/

No Camoufox needed — plain httpx with browser User-Agent works.
The site is a Next.js SSR app behind CloudFront. Without User-Agent
it returns HTTP 500; with browser-like headers it returns 200.

Usage:
    python test_api.py                    # Run all tests
    python test_api.py --list             # List all properties (paginated)
    python test_api.py --detail <slug>    # Get detail for a property
    python test_api.py --count            # Just count total properties
"""

import argparse
import json
import re
import sys

import httpx

API_BASE = "https://property-api-prod.automer.io/"
SITE_BASE = "https://property.pamco.co.th"
S3_MEDIA = "https://media.pamco.co.th/"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "th-TH,th;q=0.9,en;q=0.7",
    "Origin": SITE_BASE,
    "Referer": f"{SITE_BASE}/",
}


def get_build_id(client: httpx.Client) -> str:
    """Extract current Next.js buildId from homepage."""
    r = client.get(
        f"{SITE_BASE}/",
        headers={**HEADERS, "Accept": "text/html"},
    )
    r.raise_for_status()
    m = re.search(
        r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
        r.text,
    )
    if not m:
        raise RuntimeError("Could not find __NEXT_DATA__ in homepage")
    data = json.loads(m.group(1))
    return data["buildId"]


def list_properties(
    client: httpx.Client,
    *,
    page: int = 1,
    limit: int = 100,
    province: int | None = None,
    district: str | None = None,
    subdistrict: str | None = None,
    category: int | None = None,
) -> dict:
    """
    List properties from the API.

    Args:
        page: Page number (1-indexed)
        limit: Items per page (max tested: 200)
        province: Province code (e.g. 10 = Bangkok)
        district: District code (e.g. "1001")
        subdistrict: Sub-district code (e.g. "100101")
        category: Property category (1=บ้านเดี่ยว, 2=ทาวน์เฮ้าส์,
                  3=อาคารพาณิชย์, 4=คอนโด, 5=ที่ดินเปล่า,
                  6=โรงงาน, 7=สำนักงาน)

    Returns:
        {"total": int, "list": [...]}
    """
    params = {"page": page, "limit": limit}
    if province is not None:
        params["province"] = province
    if district is not None:
        params["district"] = district
    if subdistrict is not None:
        params["subdistrict"] = subdistrict
    if category is not None:
        params["type"] = category

    r = client.get(f"{API_BASE}property-new/display", params=params)
    r.raise_for_status()
    return r.json()


def get_detail(client: httpx.Client, slug: str, build_id: str) -> dict:
    """
    Get full property detail via Next.js SSR data endpoint.

    The property type determines the route:
      - type 3 (PAMCO source) -> /assets/pamco/{slug}
      - type 4 (TTB source)   -> /assets/ttb/{slug}

    Since we may not know the type upfront, we try pamco first,
    then ttb if not found.
    """
    for route in ["pamco", "ttb", "auctions", "consignments"]:
        url = f"{SITE_BASE}/_next/data/{build_id}/assets/{route}/{slug}.json"
        r = client.get(
            url,
            headers={**HEADERS, "Accept": "application/json"},
        )
        if r.status_code == 200:
            data = r.json()
            page_props = data.get("pageProps", {})
            if page_props.get("propertys"):
                return page_props
    raise RuntimeError(f"Detail not found for slug={slug}")


def get_province_dropdown(client: httpx.Client) -> list[dict]:
    """Get province list with districts and sub-districts."""
    r = client.get(
        f"{SITE_BASE}/",
        headers={**HEADERS, "Accept": "text/html"},
    )
    m = re.search(
        r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
        r.text,
    )
    data = json.loads(m.group(1))
    return data["props"]["pageProps"]["drop"]


def run_all_tests():
    """Run comprehensive API tests."""
    client = httpx.Client(headers=HEADERS, timeout=15, follow_redirects=True)

    print("=" * 60)
    print("TTB/PAMCO API Recon Tests")
    print("=" * 60)

    # Test 1: Build ID
    print("\n[1] Extracting buildId...")
    build_id = get_build_id(client)
    print(f"    buildId: {build_id}")

    # Test 2: List all (count)
    print("\n[2] Counting total properties...")
    data = list_properties(client, page=1, limit=1)
    total = data["total"]
    print(f"    Total: {total}")

    # Test 3: Province filter
    print("\n[3] Bangkok properties...")
    bkk = list_properties(client, province=10, limit=3)
    print(f"    Bangkok total: {bkk['total']}")
    for p in bkk["list"]:
        price = p["lowprice"][0]["lowprice"] if p.get("lowprice") else "N/A"
        print(
            f"    - [{p['slug']}] {p['npaProductTitle'][:40]} "
            f"| type={p['type']} | {float(price)/1e6:.1f}M THB"
        )

    # Test 4: Category filter
    print("\n[4] Category filter (4=คอนโด)...")
    condos = list_properties(client, category=4, limit=3)
    print(f"    Condo total: {condos['total']}")

    # Test 5: Pagination
    print("\n[5] Pagination (limit=200)...")
    page1 = list_properties(client, limit=200)
    print(f"    Page 1: {len(page1['list'])} items")

    # Test 6: Detail
    print("\n[6] Property detail...")
    slug = bkk["list"][0]["slug"]
    detail = get_detail(client, slug, build_id)
    prop = detail["propertys"]
    print(f"    Slug: {slug}")
    print(f"    Title: {prop['npaProductTitle']}")
    print(f"    GPS: {prop['npaProductLatitude']}, {prop['npaProductLongitude']}")
    print(f"    Area: {prop['npaProductArea']} sqw / Useable: {prop['useableArea']} sqm")
    print(f"    Land ID: {prop['landid']}")
    print(f"    Contact: {prop['telAO']}")
    print(f"    Images: {len(prop.get('illustration', []))} illustration(s)")

    # Test 7: Province dropdown
    print("\n[7] Province dropdown...")
    provinces = get_province_dropdown(client)
    print(f"    {len(provinces)} provinces available")
    bkk_prov = [p for p in provinces if p["provinceCd"] == 10]
    if bkk_prov:
        print(f"    Bangkok: code={bkk_prov[0]['provinceCd']}, "
              f"region={bkk_prov[0]['Region']['reg']}")

    # Test 8: District dropdown
    print("\n[8] District dropdown (Bangkok)...")
    r = client.post(
        f"{API_BASE}dropdown/province",
        json={"province": 10, "district": None},
        headers={**HEADERS, "Content-Type": "application/json"},
    )
    districts = r.json()
    if districts:
        d_list = districts[0].get("District", [])
        print(f"    {len(d_list)} districts in Bangkok")
        if d_list:
            print(f"    First: {d_list[0].get('districtNameTh', '?')}")

    print("\n" + "=" * 60)
    print("All tests passed!")
    print("=" * 60)

    client.close()


def main():
    parser = argparse.ArgumentParser(description="TTB/PAMCO API tester")
    parser.add_argument("--list", action="store_true", help="List properties")
    parser.add_argument("--detail", type=str, help="Get detail by slug")
    parser.add_argument("--count", action="store_true", help="Count total")
    parser.add_argument("--province", type=int, help="Province filter")
    parser.add_argument("--category", type=int, help="Category filter (1-7)")
    parser.add_argument("--page", type=int, default=1)
    parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args()

    if not any([args.list, args.detail, args.count]):
        run_all_tests()
        return

    client = httpx.Client(headers=HEADERS, timeout=15, follow_redirects=True)

    if args.count:
        data = list_properties(client, page=1, limit=1)
        print(f"Total properties: {data['total']}")

    elif args.list:
        data = list_properties(
            client,
            page=args.page,
            limit=args.limit,
            province=args.province,
            category=args.category,
        )
        print(f"Total: {data['total']}, Page: {args.page}, Got: {len(data['list'])}")
        for p in data["list"]:
            price = p["lowprice"][0]["lowprice"] if p.get("lowprice") else "N/A"
            print(
                f"  [{p['slug']}] type={p['type']} | "
                f"{p['npaProductTitle'][:50]} | "
                f"{float(price)/1e6:.2f}M THB | "
                f"GPS: {p.get('npaProductLatitude')},{p.get('npaProductLongitude')}"
            )

    elif args.detail:
        build_id = get_build_id(client)
        detail = get_detail(client, args.detail, build_id)
        print(json.dumps(detail["propertys"], indent=2, ensure_ascii=False))

    client.close()


if __name__ == "__main__":
    main()

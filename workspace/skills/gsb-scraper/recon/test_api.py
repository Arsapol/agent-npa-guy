"""
GSB NPA API test script — validates all discovered endpoints.
Run: python workspace/skills/gsb-scraper/recon/test_api.py
"""

import asyncio
import json
import re
import sys
from pathlib import Path

import httpx


BASE = "https://npa-assets.gsb.or.th"
API = f"{BASE}/apipr"

# Relevant asset types for NPA property investment
ASSET_TYPES = {
    341: "ที่ดิน",
    342: "ที่ดินพร้อมสิ่งปลูกสร้าง",
    343: "คอนโด/อาคารชุด/ห้องชุด",
}


async def get_build_id(client: httpx.AsyncClient) -> str:
    """Extract Next.js buildId from homepage HTML."""
    r = await client.get(f"{BASE}/asset/npa/all")
    r.raise_for_status()
    m = re.search(
        r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
        r.text,
        re.DOTALL,
    )
    if not m:
        raise RuntimeError("Could not find __NEXT_DATA__ in homepage")
    data = json.loads(m.group(1))
    build_id = data["buildId"]
    print(f"[OK] buildId: {build_id}")
    return build_id


async def test_lookup_endpoints(client: httpx.AsyncClient) -> None:
    """Test metadata/lookup endpoints."""
    print("\n--- Lookup Endpoints ---")

    # Asset types
    r = await client.get(f"{API}/npa/asset_type")
    r.raise_for_status()
    d = r.json()
    assert d["status"] == 200
    assert d["count"] == 9
    print(f"[OK] /npa/asset_type: {d['count']} types")

    # Asset subtypes
    r = await client.get(f"{API}/npa/asset_subtype")
    r.raise_for_status()
    d = r.json()
    assert d["status"] == 200
    assert d["count"] >= 11
    print(f"[OK] /npa/asset_subtype: {d['count']} subtypes")

    # Provinces
    r = await client.get(f"{API}/npa/province")
    r.raise_for_status()
    d = r.json()
    assert d["status"] == 200
    assert d["count"] >= 77
    print(f"[OK] /npa/province: {d['count']} provinces")

    # Districts for Bangkok
    r = await client.get(f"{API}/npa/district", params={"province_code": "10"})
    r.raise_for_status()
    d = r.json()
    assert d["status"] == 200
    assert d["count"] >= 50
    print(f"[OK] /npa/district?province_code=10: {d['count']} districts")

    # Sub-districts
    r = await client.get(
        f"{API}/npa/sub_district",
        params={"province_code": "10", "district_code": "22"},
    )
    r.raise_for_status()
    d = r.json()
    assert d["status"] == 200
    assert d["count"] >= 1
    print(f"[OK] /npa/sub_district: {d['count']} sub-districts")

    # Events
    r = await client.get(f"{API}/npa/event")
    r.raise_for_status()
    d = r.json()
    assert d["status"] == 200
    print(f"[OK] /npa/event: {d['count']} active events")


async def test_list_endpoint(client: httpx.AsyncClient) -> dict:
    """Test the main list/search endpoint and return a sample item."""
    print("\n--- List Endpoint ---")

    # All NPA (no filter)
    r = await client.get(
        f"{API}/npa/asset",
        params={"asset_type_dev": "npa", "page": 1, "page_size": 12},
    )
    r.raise_for_status()
    d = r.json()
    assert d["status"] == 200
    total = sum(g["asset_type_count"] for g in d["data"])
    print(f"[OK] All NPA: {total} total across {len(d['data'])} type groups")

    # Filter by type (condos)
    r = await client.get(
        f"{API}/npa/asset",
        params={
            "asset_type_dev": "npa",
            "asset_type_id": 343,
            "page": 1,
            "page_size": 12,
        },
    )
    r.raise_for_status()
    d = r.json()
    assert d["status"] == 200
    assert len(d["data"]) == 1
    condo_group = d["data"][0]
    condo_count = condo_group["asset_type_count"]
    items = condo_group["asset_list"]
    print(f"[OK] Condos only: {condo_count} items (returned {len(items)} in response)")

    # Filter by province (Bangkok condos)
    r = await client.get(
        f"{API}/npa/asset",
        params={
            "asset_type_dev": "npa",
            "asset_type_id": 343,
            "province_code": "10",
            "page": 1,
            "page_size": 12,
        },
    )
    r.raise_for_status()
    d = r.json()
    bkk_count = d["data"][0]["asset_type_count"] if d["data"] else 0
    print(f"[OK] Bangkok condos: {bkk_count} items")

    # Search by name
    r = await client.get(
        f"{API}/npa/asset",
        params={
            "asset_type_dev": "npa",
            "asset_name_or_id": "ฮอไรซอน",
            "page": 1,
            "page_size": 12,
        },
    )
    r.raise_for_status()
    d = r.json()
    search_total = sum(g["asset_type_count"] for g in d["data"])
    print(f"[OK] Search 'ฮอไรซอน': {search_total} results")

    # Search by NPA ID
    sample_id = items[0]["asset_group_id_npa"] if items else "BKK620093"
    r = await client.get(
        f"{API}/npa/asset",
        params={
            "asset_type_dev": "npa",
            "asset_name_or_id": sample_id,
            "page": 1,
            "page_size": 12,
        },
    )
    r.raise_for_status()
    d = r.json()
    id_total = sum(g["asset_type_count"] for g in d["data"])
    print(f"[OK] Search by ID '{sample_id}': {id_total} results")

    # Price range filter
    r = await client.get(
        f"{API}/npa/asset",
        params={
            "asset_type_dev": "npa",
            "asset_type_id": 343,
            "price_range": 1,
            "page": 1,
            "page_size": 12,
        },
    )
    r.raise_for_status()
    d = r.json()
    pr1_count = d["data"][0]["asset_type_count"] if d["data"] else 0
    print(f"[OK] Condos price_range=1 (<1.5M): {pr1_count} items")

    # Sort order
    r = await client.get(
        f"{API}/npa/asset",
        params={
            "asset_type_dev": "npa",
            "asset_type_id": 343,
            "province_code": "10",
            "filter": "asc",
            "page": 1,
            "page_size": 12,
        },
    )
    r.raise_for_status()
    d = r.json()
    asc_items = d["data"][0]["asset_list"] if d["data"] else []
    if len(asc_items) >= 2:
        first_price = asc_items[0]["current_offer_price"]
        last_price = asc_items[-1]["current_offer_price"]
        assert first_price <= last_price, f"Sort asc failed: {first_price} > {last_price}"
        print(f"[OK] Sort asc: {first_price:,} -> {last_price:,}")

    # Validate list item fields
    sample = items[0] if items else asc_items[0]
    required_list_fields = [
        "asset_id", "asset_group_id", "asset_group_id_npa", "asset_type_id",
        "asset_type_desc", "current_offer_price", "image_id",
        "province_name", "district_name", "sub_district_name",
        "xprice_normal", "xprice", "xtype", "deed_info",
    ]
    missing = [f for f in required_list_fields if f not in sample]
    assert not missing, f"Missing list fields: {missing}"
    print(f"[OK] List item has all {len(required_list_fields)} required fields")

    return sample


async def test_detail_endpoint(
    client: httpx.AsyncClient, build_id: str, sample: dict
) -> dict:
    """Test the detail endpoint by parsing __NEXT_DATA__ from HTML page.

    The Next.js data route (/_next/data/{buildId}/...) is unreliable because
    buildId can differ between listing and detail pages during partial deploys.
    Parsing __NEXT_DATA__ from the HTML is always reliable.
    """
    print("\n--- Detail Endpoint ---")

    npa_id = sample["asset_group_id_npa"]
    type_id = sample["asset_type_id"]

    r = await client.get(
        f"{BASE}/asset/npa",
        params={
            "id": npa_id,
            "asset_type_id": type_id,
            "type_id": "asset_group_id_npa",
        },
    )
    r.raise_for_status()
    m = re.search(
        r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
        r.text,
        re.DOTALL,
    )
    assert m, "Could not find __NEXT_DATA__ in detail page"
    d = json.loads(m.group(1))
    info = d["props"]["pageProps"]["info"]

    # Validate detail-only fields
    detail_fields = [
        "latitude", "longitude", "building_no", "road",
        "asset_image", "asset_map", "deed_info",
        "current_offer_price", "xprice_normal", "events",
    ]
    missing = [f for f in detail_fields if f not in info]
    assert not missing, f"Missing detail fields: {missing}"
    print(f"[OK] Detail for {npa_id}: all {len(detail_fields)} detail fields present")

    # GPS
    lat = info.get("latitude")
    lng = info.get("longitude")
    if lat and lng:
        print(f"[OK] GPS: {lat}, {lng}")
    else:
        print(f"[WARN] No GPS for {npa_id}")

    # Images
    images = info.get("asset_image", [])
    maps = info.get("asset_map", [])
    print(f"[OK] Images: {len(images)} photos, {len(maps)} maps")

    # Buildings
    buildings = info.get("buildings", [])
    if buildings:
        b = buildings[0]
        print(
            f"[OK] Building: {b.get('asset_subtype_desc')}, "
            f"{b.get('number_floor')} floor(s), "
            f"{b.get('square_meter')} sqm, "
            f"bed={b.get('bedroom_no')}, bath={b.get('bathroom_no')}"
        )

    # Events/promotions
    events = info.get("events", [])
    if events:
        ev = events[0]
        print(
            f"[OK] Promotion: {ev.get('promotion_name', '')[:50]}..., "
            f"sell={ev.get('sell_price'):,}, special={ev.get('special_price'):,}"
        )

    # Price summary
    print(
        f"[OK] Price: normal={info['xprice_normal']:,}, "
        f"current={info['current_offer_price']:,}, "
        f"type={info['xtype']}"
    )

    return info


async def test_image_endpoint(
    client: httpx.AsyncClient, info: dict
) -> None:
    """Test image download."""
    print("\n--- Image Endpoint ---")

    images = info.get("asset_image", [])
    if not images:
        print("[SKIP] No images to test")
        return

    image_id = images[0]["id"]
    type_id = info["asset_type_id"]

    r = await client.head(
        f"{API}/npa/image",
        params={"id": image_id, "asset_type_id": type_id},
    )
    assert r.status_code == 200
    ct = r.headers.get("content-type", "")
    assert "image" in ct
    print(f"[OK] Image {image_id}: {ct}")

    # Test PDF (via same image endpoint)
    pdf_id = info.get("asset_pdf")
    if pdf_id:
        r = await client.head(
            f"{API}/npa/image",
            params={"id": pdf_id, "asset_type_id": type_id},
        )
        print(f"[OK] PDF {pdf_id}: {r.status_code} {r.headers.get('content-type', '')}")


async def test_pagination_behavior(client: httpx.AsyncClient) -> None:
    """Verify that page_size does NOT limit actual results."""
    print("\n--- Pagination Behavior ---")

    results = {}
    for ps in [2, 12, 100]:
        r = await client.get(
            f"{API}/npa/asset",
            params={
                "asset_type_dev": "npa",
                "asset_type_id": 343,
                "province_code": "10",
                "page": 1,
                "page_size": ps,
            },
        )
        d = r.json()
        count = len(d["data"][0]["asset_list"]) if d["data"] else 0
        total_page = d["data"][0]["total_page"] if d["data"] else 0
        results[ps] = count
        print(f"  page_size={ps:3d}: returned {count} items, total_page={total_page}")

    # All page_sizes should return same count (API ignores page_size for actual data)
    counts = list(results.values())
    if len(set(counts)) == 1:
        print(f"[OK] Confirmed: page_size has NO effect on returned items ({counts[0]} each)")
    else:
        print(f"[WARN] page_size affects results: {results}")


async def save_samples(info: dict) -> None:
    """Save sample responses for reference."""
    out_dir = Path(__file__).parent
    sample_path = out_dir / "sample_detail.json"
    sample_path.write_text(json.dumps(info, ensure_ascii=False, indent=2))
    print(f"\n[OK] Saved sample detail to {sample_path}")


async def main() -> None:
    print("=" * 60)
    print("GSB NPA API Test Suite")
    print("=" * 60)

    async with httpx.AsyncClient(
        follow_redirects=True,
        timeout=30,
        headers={"User-Agent": "Mozilla/5.0 (npa-guy-bot)"},
    ) as client:
        build_id = await get_build_id(client)
        await test_lookup_endpoints(client)
        sample = await test_list_endpoint(client)
        info = await test_detail_endpoint(client, build_id, sample)
        await test_image_endpoint(client, info)
        await test_pagination_behavior(client)
        await save_samples(info)

    print("\n" + "=" * 60)
    print("All tests passed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

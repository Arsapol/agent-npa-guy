"""
SCB HOME.SCB API Recon — Test Script
Demonstrates all discovered endpoints for asset.home.scb

Architecture:
  - Primary data source: JSON API at /api/project/cmd (command-based RPC)
  - Detail page: Server-rendered HTML at /project/{slug}
  - Auth: None required (anonymous access, optional csrf_token)
  - All endpoints are GET with query parameters
"""
import asyncio
import json

import httpx
from selectolax.parser import HTMLParser

BASE_URL = "https://asset.home.scb"

API_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Accept": "application/json",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": f"{BASE_URL}/",
}

HTML_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Accept": "text/html",
}


async def test_location_api(client: httpx.AsyncClient) -> None:
    """Test the location hierarchy endpoints."""
    r = await client.get(
        f"{BASE_URL}/api/project/cmd",
        params={"command": "get_province"},
        headers=API_HEADERS,
    )
    provinces = r.json()
    assert provinces["s"] == "y"
    print(f"[Location] Provinces: {len(provinces['d'])}")

    bkk = next(p for p in provinces["d"] if p["province_id"] == 1)
    print(f"  Bangkok: province_id={bkk['province_id']} area={bkk['area']}")

    r2 = await client.get(
        f"{BASE_URL}/api/project/cmd",
        params={"command": "get_district", "province_id": "1"},
        headers=API_HEADERS,
    )
    districts = r2.json()
    assert districts["s"] == "y"
    print(f"  Bangkok districts: {len(districts['d'])}")


async def test_search_api(client: httpx.AsyncClient) -> str | None:
    """Test the main property search endpoint with filters."""
    r = await client.get(
        f"{BASE_URL}/api/project/cmd",
        params={"command": "get_project", "page": 1, "limit": 15, "type": "project"},
        headers=API_HEADERS,
    )
    data = r.json()
    assert data["s"] == "y"
    total = data["total"]
    print(f"[Search] Total all properties: {total}")
    print(f"  Page 1: {len(data['d'])} items")

    r2 = await client.get(
        f"{BASE_URL}/api/project/cmd",
        params={
            "command": "get_project",
            "page": 1,
            "limit": 15,
            "type": "project",
            "asset-type": "condominiums",
        },
        headers=API_HEADERS,
    )
    data2 = r2.json()
    print(f"  Condos: {data2.get('total', '?')} total")

    r3 = await client.get(
        f"{BASE_URL}/api/project/cmd",
        params={"command": "get_project", "page": 2, "limit": 15, "type": "project"},
        headers=API_HEADERS,
    )
    data3 = r3.json()
    ids_p1 = {p["project_id"] for p in data["d"]}
    ids_p2 = {p["project_id"] for p in data3["d"]}
    print(f"  Page 2: {len(data3['d'])} items, overlap: {len(ids_p1 & ids_p2)}")

    if data["d"]:
        item = data["d"][0]
        print(f"\n  Sample: {item['project_title']}")
        print(f"    type={item['project_type']} price={item['price']} area_sqm={item['area_sqm']}")
        print(f"    GPS=({item['latitude']}, {item['longitude']})")
        print(f"    slug={item['slug']}")

    return data["d"][0]["slug"] if data["d"] else None


async def test_map_listing(client: httpx.AsyncClient) -> None:
    """Get all properties with GPS coordinates in one call."""
    r = await client.get(
        f"{BASE_URL}/api/project/cmd",
        params={"command": "get_list_map"},
        headers=API_HEADERS,
    )
    data = r.json()
    assert data["s"] == "y"
    print(f"[Map] Total properties with GPS: {len(data['d'])}")
    if data["d"]:
        item = data["d"][0]
        print(f"  Fields per item: {sorted(item.keys())}")


async def test_detail_page(client: httpx.AsyncClient, slug: str) -> None:
    """Parse a property detail page for all fields from hidden inputs."""
    r = await client.get(f"{BASE_URL}/project/{slug}", headers=HTML_HEADERS)
    assert r.status_code == 200

    tree = HTMLParser(r.text)
    detail: dict[str, str | list[str]] = {}

    for inp in tree.css("input[type='hidden']"):
        name = inp.attributes.get("name") or inp.attributes.get("id") or ""
        val = inp.attributes.get("value") or ""
        if name and val and name != "csrf_token":
            detail[name] = val

    images = []
    for img in tree.css("img"):
        src = img.attributes.get("src") or img.attributes.get("data-src") or ""
        if "stocks" in src:
            images.append(src)
    detail["images"] = images

    print(f"[Detail] {detail.get('txt-project-name', '?')}")
    print(f"  project_id={detail.get('pid')} code={detail.get('txt-project-code')}")
    print(f"  type={detail.get('pjt')} GPS=({detail.get('lat')}, {detail.get('lng')})")
    print(f"  images={len(images)} sold_out={detail.get('chk-sold-out')}")


async def test_home_api(client: httpx.AsyncClient) -> None:
    """Test homepage API for featured/hot projects."""
    r = await client.get(
        f"{BASE_URL}/api/home/cmd",
        params={
            "type": "project",
            "badge": "hot",
            "page": 1,
            "limit": 10,
            "command": "get_home_project",
        },
        headers=API_HEADERS,
    )
    data = r.json()
    assert data["s"] == "y"
    print(f"[Home] Hot projects: {len(data['d'])}")


async def main() -> None:
    async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
        print("=" * 60)
        print("SCB HOME.SCB API Recon")
        print("=" * 60)

        await test_location_api(client)
        print()
        slug = await test_search_api(client)
        print()
        await test_map_listing(client)
        print()
        if slug:
            await test_detail_page(client, slug)
        print()
        await test_home_api(client)
        print()
        print("=" * 60)
        print("Recon complete!")


if __name__ == "__main__":
    asyncio.run(main())

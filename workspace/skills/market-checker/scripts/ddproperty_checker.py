"""
DDProperty Market Price Checker
Looks up current sale & rental listings for a condo project by name.

Usage:
    python ddproperty_checker.py "triple y residence samyan"
    python ddproperty_checker.py "inspire place abac"
    python ddproperty_checker.py "15 sukhumvit residences"

Output: JSON with sale/rent listings, price/sqm stats, and project metadata.

Architecture:
  - Camoufox (headless Firefox) for cookie acquisition (bypasses Cloudflare)
  - httpx for all subsequent API calls (fast, lightweight)
  - Two API layers:
      1. /api/consumer/project?name=... → project metadata (id, units, year built)
      2. /_next/data/{BUILD_ID}/en/condo-for-sale.json?freetext=... → listings
"""

import asyncio
import json
import statistics
import sys
from typing import Optional

import httpx
from pydantic import BaseModel, Field

# ── Config ────────────────────────────────────────────────────────────────────

BASE_URL = "https://www.ddproperty.com"

# Build ID changes when DDProperty deploys a new frontend version.
# Run fetch_build_id() to refresh it.
BUILD_ID = "eSYGxg6TJlYl4EPdcSFiR"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": f"{BASE_URL}/en/condo-for-sale",
}


# ── Data models ───────────────────────────────────────────────────────────────


class ListingSummary(BaseModel):
    listing_id: int
    price_thb: int
    sqm: Optional[float]
    price_per_sqm: Optional[int]
    bedrooms: int
    bathrooms: int
    url: str


class ProjectInfo(BaseModel):
    project_id: int  # internal DDProperty project ID (used in SRP)
    name: str
    completion_year: Optional[int]
    total_units: Optional[int]
    starting_price: Optional[int]


class MarketData(BaseModel):
    project: Optional[ProjectInfo]
    sale_listings: list[ListingSummary] = Field(default_factory=list)
    rent_listings: list[ListingSummary] = Field(default_factory=list)
    sale_count: int = 0
    rent_count: int = 0

    def sale_psm_stats(self) -> dict:
        vals = [x.price_per_sqm for x in self.sale_listings if x.price_per_sqm]
        if not vals:
            return {}
        return {
            "min": min(vals),
            "max": max(vals),
            "median": int(statistics.median(vals)),
            "mean": int(statistics.mean(vals)),
            "count": len(vals),
        }

    def rent_stats(self) -> dict:
        prices = [x.price_thb for x in self.rent_listings]
        if not prices:
            return {}
        return {
            "min": min(prices),
            "max": max(prices),
            "median": int(statistics.median(prices)),
            "mean": int(statistics.mean(prices)),
            "count": len(prices),
        }


# ── Cookie acquisition ────────────────────────────────────────────────────────


async def get_cf_cookies() -> dict[str, str]:
    """Use Camoufox to bypass Cloudflare and acquire session cookies."""
    try:
        from camoufox.async_api import AsyncCamoufox
    except ImportError:
        raise RuntimeError(
            "camoufox not installed. Run: pip install 'camoufox[geoip]' && python -m camoufox fetch"
        )

    async with AsyncCamoufox(headless=True, humanize=True) as browser:
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto(f"{BASE_URL}/en", wait_until="domcontentloaded", timeout=60_000)
        await asyncio.sleep(2)
        cookies = await context.cookies()
        await context.close()

    return {
        c["name"]: c["value"]
        for c in cookies
        if "ddproperty" in c["domain"] or c["domain"].startswith(".ddproperty")
    }


# ── Build ID refresh ──────────────────────────────────────────────────────────


async def fetch_build_id(cookies: dict[str, str]) -> str:
    """Fetch the current Next.js BUILD_ID from the homepage HTML."""
    import re

    async with httpx.AsyncClient(
        timeout=30.0,
        follow_redirects=True,
        headers={**HEADERS, "Accept": "text/html"},
        cookies=cookies,
    ) as client:
        resp = await client.get(f"{BASE_URL}/en")
        match = re.search(r'"buildId"\s*:\s*"([^"]+)"', resp.text)
        if match:
            return match.group(1)
    return BUILD_ID


# ── API calls ─────────────────────────────────────────────────────────────────


async def lookup_project(
    name: str,
    client: httpx.AsyncClient,
) -> Optional[ProjectInfo]:
    """Find a project by name via /api/consumer/project?name=..."""
    resp = await client.get(
        f"{BASE_URL}/api/consumer/project",
        params={"locale": "en", "region": "th", "size": 5, "name": name},
    )
    if resp.status_code != 200:
        return None

    data = resp.json()
    projects = data.get("data", [])
    if not projects:
        return None

    # Take first match
    p = projects[0]
    starting = p.get("starting_price", {}) or {}
    return ProjectInfo(
        project_id=p.get("property_id"),  # This is the project_id used in SRP filter
        name=p.get("name", ""),
        completion_year=p.get("completion_year"),
        total_units=p.get("total_units"),
        starting_price=starting.get("value") if isinstance(starting, dict) else None,
    )


async def fetch_listings(
    freetext: str,
    listing_type: str,  # "sale" or "rent"
    build_id: str,
    client: httpx.AsyncClient,
    page: int = 1,
    max_pages: int = 5,
) -> tuple[list[ListingSummary], int]:
    """
    Fetch listings via the Next.js _next/data API.
    Returns (listings, result_count).

    listing_type: "sale" → /en/condo-for-sale.json
                  "rent" → /en/condo-for-rent.json
    """
    slug = "condo-for-sale" if listing_type == "sale" else "condo-for-rent"
    url = f"{BASE_URL}/_next/data/{build_id}/en/{slug}.json"

    all_listings: list[ListingSummary] = []
    total_count = 0

    for p in range(1, max_pages + 1):
        resp = await client.get(
            url,
            params={
                "freetext": freetext,
                "listingType": listing_type,
                "page": p,
            },
        )
        if resp.status_code != 200:
            break

        data = resp.json()
        page_data = data.get("pageProps", {}).get("pageData", {})
        data_node = page_data.get("data", {})
        listings_raw = data_node.get("listingsData", [])
        pagination = data_node.get("paginationData", {})

        if p == 1:
            total_count = page_data.get("resultCount") or len(listings_raw)

        for item in listings_raw:
            ld = item.get("listingData", {})
            price_info = ld.get("price", {}) or {}
            price_val = price_info.get("value")
            sqm = ld.get("floorArea")
            psm = round(price_val / sqm) if price_val and sqm else None

            all_listings.append(
                ListingSummary(
                    listing_id=ld.get("id"),
                    price_thb=price_val,
                    sqm=sqm,
                    price_per_sqm=psm,
                    bedrooms=ld.get("bedrooms", 0),
                    bathrooms=ld.get("bathrooms", 0),
                    url=ld.get("url", ""),
                )
            )

        total_pages = pagination.get("totalPages", 1) or 1
        if p >= total_pages:
            break
        await asyncio.sleep(0.5)  # polite delay

    return all_listings, total_count


# ── Main entry point ──────────────────────────────────────────────────────────


async def check_market(project_name: str, refresh_build_id: bool = False) -> MarketData:
    """
    Main function: look up a condo project and return sale + rental market data.

    Args:
        project_name: Natural-language project name (e.g. "triple y residence samyan")
        refresh_build_id: Set True if you get 404 errors (BUILD_ID expired)
    """
    print("[1/4] Acquiring Cloudflare cookies via Camoufox...")
    cookies = await get_cf_cookies()
    print(f"      Got {len(cookies)} cookies: {list(cookies.keys())}")

    async with httpx.AsyncClient(
        timeout=30.0,
        follow_redirects=True,
        headers=HEADERS,
        cookies=cookies,
    ) as client:
        build_id = BUILD_ID
        if refresh_build_id:
            print("[1b] Refreshing BUILD_ID...")
            build_id = await fetch_build_id(cookies)
            print(f"     BUILD_ID: {build_id}")

        print(f"[2/4] Looking up project: '{project_name}'...")
        project = await lookup_project(project_name, client)
        if project:
            print(
                f"      Found: {project.name} (id={project.project_id}, "
                f"units={project.total_units}, built={project.completion_year})"
            )
        else:
            print(f"      No project found for '{project_name}'")

        print("[3/4] Fetching SALE listings...")
        sale_listings, sale_count = await fetch_listings(
            freetext=project_name,
            listing_type="sale",
            build_id=build_id,
            client=client,
        )
        print(f"      {sale_count} total, {len(sale_listings)} fetched")

        print("[4/4] Fetching RENT listings...")
        rent_listings, rent_count = await fetch_listings(
            freetext=project_name,
            listing_type="rent",
            build_id=build_id,
            client=client,
        )
        print(f"      {rent_count} total, {len(rent_listings)} fetched")

    return MarketData(
        project=project,
        sale_listings=sale_listings,
        rent_listings=rent_listings,
        sale_count=sale_count,
        rent_count=rent_count,
    )


def print_report(data: MarketData, project_name: str) -> None:
    """Pretty-print the market data report."""
    print("\n" + "=" * 60)
    print(f"DDProperty Market Report: {project_name}")
    print("=" * 60)

    if data.project:
        p = data.project
        print(f"\nProject:        {p.name}")
        print(f"Completed:      {p.completion_year or 'N/A'}")
        print(f"Total Units:    {p.total_units or 'N/A'}")
        if p.starting_price:
            print(f"Starting Price: ฿{p.starting_price:,}")

    print("\nActive Listings:")
    print(f"  For Sale:  {data.sale_count}")
    print(f"  For Rent:  {data.rent_count}")

    sale_stats = data.sale_psm_stats()
    if sale_stats:
        print("\nSale Price/sqm:")
        print(f"  Min:    ฿{sale_stats['min']:,}/sqm")
        print(f"  Median: ฿{sale_stats['median']:,}/sqm")
        print(f"  Max:    ฿{sale_stats['max']:,}/sqm")
        print(f"  Mean:   ฿{sale_stats['mean']:,}/sqm")

    rent_stats = data.rent_stats()
    if rent_stats:
        print("\nRent/month:")
        print(f"  Min:    ฿{rent_stats['min']:,}/mo")
        print(f"  Median: ฿{rent_stats['median']:,}/mo")
        print(f"  Max:    ฿{rent_stats['max']:,}/mo")

    if data.sale_listings:
        print("\nSample Sale Listings:")
        for listing in data.sale_listings[:5]:
            psm_str = (
                f" = ฿{listing.price_per_sqm:,}/sqm" if listing.price_per_sqm else ""
            )
            sqm_str = f", {listing.sqm}sqm" if listing.sqm else ""
            print(
                f"  ฿{listing.price_thb:,}{sqm_str}{psm_str} | {listing.bedrooms}bd/{listing.bathrooms}ba"
            )

    if data.rent_listings:
        print("\nSample Rent Listings:")
        for listing in data.rent_listings[:5]:
            sqm_str = f", {listing.sqm}sqm" if listing.sqm else ""
            print(
                f"  ฿{listing.price_thb:,}/mo{sqm_str} | {listing.bedrooms}bd/{listing.bathrooms}ba"
            )

    print()


async def main() -> None:
    project_name = (
        " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "triple y residence samyan"
    )
    refresh = "--refresh-build-id" in sys.argv

    data = await check_market(project_name, refresh_build_id=refresh)
    print_report(data, project_name)

    # Also save JSON
    output = {
        "project_name_query": project_name,
        "project": {
            "id": data.project.project_id if data.project else None,
            "name": data.project.name if data.project else None,
            "completion_year": data.project.completion_year if data.project else None,
            "total_units": data.project.total_units if data.project else None,
        }
        if data.project
        else None,
        "sale": {
            "count": data.sale_count,
            "price_per_sqm_stats": data.sale_psm_stats(),
            "listings": [
                {
                    "id": x.listing_id,
                    "price_thb": x.price_thb,
                    "sqm": x.sqm,
                    "price_per_sqm": x.price_per_sqm,
                    "bedrooms": x.bedrooms,
                    "bathrooms": x.bathrooms,
                    "url": x.url,
                }
                for x in data.sale_listings
            ],
        },
        "rent": {
            "count": data.rent_count,
            "rent_stats": data.rent_stats(),
            "listings": [
                {
                    "id": x.listing_id,
                    "price_thb": x.price_thb,
                    "sqm": x.sqm,
                    "bedrooms": x.bedrooms,
                    "bathrooms": x.bathrooms,
                    "url": x.url,
                }
                for x in data.rent_listings
            ],
        },
    }

    out_path = f"/tmp/ddproperty_{project_name.replace(' ', '_')}.json"
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"JSON saved to: {out_path}")


if __name__ == "__main__":
    asyncio.run(main())

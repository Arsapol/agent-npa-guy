"""
PropertyHub.in.th market price checker.

Looks up a condo project by name, returns:
  - Sale listings: price, sqm, price/sqm
  - Rental listings: rent/month, sqm
  - Project metadata: year built, total units, developer, facilities

API: GraphQL at https://api.propertyhub.in.th/graphql (no auth required)
"""

from __future__ import annotations

import statistics
from dataclasses import dataclass, field
from typing import Optional

import httpx


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

GQL_URL = "https://api.propertyhub.in.th/graphql"
SITE_URL = "https://propertyhub.in.th"

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Origin": SITE_URL,
    "Referer": SITE_URL + "/",
}

# ---------------------------------------------------------------------------
# GraphQL query strings
# ---------------------------------------------------------------------------

_GLOBAL_SEARCH_GQL = """
query globalSearch($name: String, $locale: LocaleType, $size: Int, $page: Int, $propertyType: PropertyTypeItem) {
  globalSearch(name: $name, locale: $locale, size: $size, page: $page, propertyType: $propertyType) {
    status
    error { message }
    result {
      projects {
        id
        name
        nameEnglish
        slug
        projectType
        address
        listingCountByPostType {
          FOR_RENT { listingCount }
          FOR_SALE { listingCount }
        }
      }
      projectPagination { page perPage totalCount }
    }
  }
}
"""

_PROJECT_DETAIL_GQL = """
query ($projectId: ID!, $locale: LocaleType) {
  project(projectId: $projectId, locale: $locale) {
    status
    error { message }
    result {
      id
      slug
      name
      nameEnglish
      description
      address
      location { lat lng }
      projectType
      facilities
      projectInfo
      developer { id name }
      unitType
      provinceCode
      districtCode
      createdAt
      updatedAt
      listingCountByPostType {
        FOR_RENT { listingCount }
        FOR_SALE { listingCount }
      }
    }
  }
}
"""

_LISTINGS_GQL = """
query listings(
  $locale: LocaleType
  $page: Int
  $perPage: Int
  $listingAttributes: ListingSearchForConsumerAttributes
) {
  listings(
    locale: $locale
    page: $page
    perPage: $perPage
    ListingSearchForConsumerAttributes: $listingAttributes
  ) {
    status
    error { message }
    pagination { page perPage totalCount totalPages }
    result {
      id
      postType
      title
      price {
        forRent { monthly { type price } }
        forSale { type price }
      }
      roomInformation {
        numberOfBed
        numberOfBath
        roomArea
        onFloor
        roomType
      }
      createdAt
      updatedAt
    }
  }
}
"""


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class SaleListing:
    listing_id: str
    price_thb: int
    area_sqm: float
    price_per_sqm: float
    beds: Optional[int]
    baths: Optional[int]
    floor: Optional[str]
    room_type: Optional[str]
    updated_at: Optional[str]


@dataclass
class RentListing:
    listing_id: str
    rent_monthly_thb: int
    area_sqm: Optional[float]
    beds: Optional[int]
    baths: Optional[int]
    floor: Optional[str]
    room_type: Optional[str]
    updated_at: Optional[str]


@dataclass
class ProjectInfo:
    project_id: str
    name_en: str
    slug: str
    address: str
    lat: Optional[float]
    lng: Optional[float]
    completed_year: Optional[str]
    total_units: Optional[str]
    floors: Optional[str]
    buildings: Optional[str]
    developer: Optional[str]
    utility_fee: Optional[str]
    listing_count_sale: int
    listing_count_rent: int
    facilities: dict


@dataclass
class ProjectResult:
    project: ProjectInfo
    sale_listings: list[SaleListing] = field(default_factory=list)
    rent_listings: list[RentListing] = field(default_factory=list)

    # ---------- computed summaries ----------

    def sale_price_sqm_stats(self) -> dict:
        prices = [l.price_per_sqm for l in self.sale_listings if l.price_per_sqm > 0]
        if not prices:
            return {}
        return {
            "count": len(prices),
            "min": int(min(prices)),
            "avg": int(statistics.mean(prices)),
            "median": int(statistics.median(prices)),
            "max": int(max(prices)),
        }

    def rent_stats(self) -> dict:
        rents = [l.rent_monthly_thb for l in self.rent_listings if l.rent_monthly_thb > 0]
        if not rents:
            return {}
        return {
            "count": len(rents),
            "min": int(min(rents)),
            "avg": int(statistics.mean(rents)),
            "median": int(statistics.median(rents)),
            "max": int(max(rents)),
        }

    def implied_yield_pct(self) -> Optional[float]:
        """Rough gross yield: median_annual_rent / avg_price * 100."""
        ss = self.sale_price_sqm_stats()
        rs = self.rent_stats()
        if not ss or not rs:
            return None
        # Need avg area to estimate a typical unit price
        areas = [l.area_sqm for l in self.sale_listings if l.area_sqm]
        if not areas:
            return None
        avg_area = statistics.mean(areas)
        avg_price = ss["avg"] * avg_area
        annual_rent = rs["avg"] * 12
        return round(annual_rent / avg_price * 100, 2)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _gql_post(client: httpx.Client, query: str, variables: dict) -> dict:
    resp = client.post(GQL_URL, json={"query": query, "variables": variables})
    resp.raise_for_status()
    data = resp.json()
    if "errors" in data and data["errors"]:
        raise RuntimeError(f"GraphQL error: {data['errors'][0]['message']}")
    return data.get("data", {})


def _parse_sale_listing(raw: dict) -> Optional[SaleListing]:
    price_node = raw.get("price", {}).get("forSale", {})
    price = price_node.get("price")
    ri = raw.get("roomInformation") or {}
    area = ri.get("roomArea")
    if not price or not area or area <= 0:
        return None
    return SaleListing(
        listing_id=raw["id"],
        price_thb=int(price),
        area_sqm=float(area),
        price_per_sqm=round(price / area, 2),
        beds=ri.get("numberOfBed"),
        baths=ri.get("numberOfBath"),
        floor=ri.get("onFloor"),
        room_type=ri.get("roomType"),
        updated_at=raw.get("updatedAt"),
    )


def _parse_rent_listing(raw: dict) -> Optional[RentListing]:
    monthly_node = raw.get("price", {}).get("forRent", {}).get("monthly") or {}
    rent = monthly_node.get("price")
    if not rent:
        return None
    ri = raw.get("roomInformation") or {}
    return RentListing(
        listing_id=raw["id"],
        rent_monthly_thb=int(rent),
        area_sqm=float(ri["roomArea"]) if ri.get("roomArea") else None,
        beds=ri.get("numberOfBed"),
        baths=ri.get("numberOfBath"),
        floor=ri.get("onFloor"),
        room_type=ri.get("roomType"),
        updated_at=raw.get("updatedAt"),
    )


def _fetch_all_listings(
    client: httpx.Client,
    project_id: str,
    post_type: str,
    per_page: int = 100,
) -> list[dict]:
    """Page through all listings for a project/post-type."""
    results: list[dict] = []
    page = 1
    while True:
        data = _gql_post(
            client,
            _LISTINGS_GQL,
            {
                "locale": "EN",
                "page": page,
                "perPage": per_page,
                "listingAttributes": {
                    "projectId": project_id,
                    "postType": post_type,
                },
            },
        )
        node = data.get("listings", {})
        if node.get("status") != "SUCCESS":
            break
        results.extend(node.get("result") or [])
        pg = node.get("pagination", {})
        if page >= (pg.get("totalPages") or 1):
            break
        page += 1
    return results


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def search_project(
    keyword: str,
    client: Optional[httpx.Client] = None,
) -> list[dict]:
    """
    Search for projects by keyword.

    Returns a list of matching project dicts with keys:
      id, name, nameEnglish, slug, address, listingCountByPostType
    """
    own_client = client is None
    if own_client:
        client = httpx.Client(headers=_HEADERS, follow_redirects=True, timeout=30)
        client.get(SITE_URL)  # warm session cookie

    try:
        data = _gql_post(
            client,
            _GLOBAL_SEARCH_GQL,
            {
                "name": keyword,
                "locale": "EN",
                "size": 10,
                "page": 1,
                "propertyType": "CONDO",
            },
        )
        return data.get("globalSearch", {}).get("result", {}).get("projects", [])
    finally:
        if own_client:
            client.close()


def get_project_detail(
    project_id: str,
    client: Optional[httpx.Client] = None,
) -> Optional[ProjectInfo]:
    """Fetch detailed metadata for a project by its numeric ID."""
    own_client = client is None
    if own_client:
        client = httpx.Client(headers=_HEADERS, follow_redirects=True, timeout=30)
        client.get(SITE_URL)

    try:
        data = _gql_post(
            client,
            _PROJECT_DETAIL_GQL,
            {"projectId": project_id, "locale": "EN"},
        )
        r = data.get("project", {}).get("result")
        if not r:
            return None

        pi = r.get("projectInfo") or {}
        loc = r.get("location") or {}
        cnt = r.get("listingCountByPostType") or {}
        dev = r.get("developer") or {}

        return ProjectInfo(
            project_id=r["id"],
            name_en=r.get("nameEnglish") or r.get("name", ""),
            slug=r.get("slug", ""),
            address=r.get("address", ""),
            lat=loc.get("lat"),
            lng=loc.get("lng"),
            completed_year=pi.get("completedYear"),
            total_units=pi.get("totalUnits"),
            floors=pi.get("buildingsFloors"),
            buildings=pi.get("buildingNumbers"),
            developer=dev.get("name") if dev else None,
            utility_fee=pi.get("utilityFee"),
            listing_count_sale=(cnt.get("FOR_SALE") or {}).get("listingCount", 0),
            listing_count_rent=(cnt.get("FOR_RENT") or {}).get("listingCount", 0),
            facilities=r.get("facilities") or {},
        )
    finally:
        if own_client:
            client.close()


def check_project(keyword: str) -> Optional[ProjectResult]:
    """
    Main entry point.

    1. Search by keyword → pick top match.
    2. Fetch project metadata.
    3. Fetch all sale + rental listings.
    4. Return ProjectResult with computed summaries.
    """
    with httpx.Client(headers=_HEADERS, follow_redirects=True, timeout=30) as client:
        # Warm session cookie (PropertyHub sets unleash-session-id etc.)
        client.get(SITE_URL)

        # --- find project ---
        projects = search_project(keyword, client=client)
        if not projects:
            raise ValueError(f"No projects found for keyword: {keyword!r}")

        top = projects[0]
        project_id = top["id"]

        # --- project detail ---
        proj_info = get_project_detail(project_id, client=client)
        if not proj_info:
            raise RuntimeError(f"Could not fetch project detail for id={project_id}")

        # --- sale listings ---
        raw_sale = _fetch_all_listings(client, project_id, "FOR_SALE")
        sale_listings = [
            listing
            for raw in raw_sale
            if (listing := _parse_sale_listing(raw)) is not None
        ]

        # --- rental listings ---
        raw_rent = _fetch_all_listings(client, project_id, "FOR_RENT")
        rent_listings = [
            listing
            for raw in raw_rent
            if (listing := _parse_rent_listing(raw)) is not None
        ]

        return ProjectResult(
            project=proj_info,
            sale_listings=sale_listings,
            rent_listings=rent_listings,
        )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _print_result(result: ProjectResult) -> None:
    p = result.project
    print(f"\n{'='*60}")
    print(f"Project : {p.name_en}")
    print(f"Slug    : {p.slug}")
    print(f"Address : {p.address}")
    print(f"Location: lat={p.lat}, lng={p.lng}")
    print(f"Year    : {p.completed_year or 'N/A'}")
    print(f"Units   : {p.total_units or 'N/A'}")
    print(f"Floors  : {p.floors or 'N/A'} floors, {p.buildings or 'N/A'} buildings")
    print(f"Developer: {p.developer or 'N/A'}")
    print(f"Utility fee: {p.utility_fee or 'N/A'} THB/sqm/mo")
    amenities = [k for k, v in p.facilities.items() if v is True]
    print(f"Facilities: {', '.join(amenities) or 'N/A'}")
    print()

    ss = result.sale_price_sqm_stats()
    if ss:
        print(f"SALE ({ss['count']} listings with area):")
        print(f"  Price/sqm  min={ss['min']:,}  avg={ss['avg']:,}  median={ss['median']:,}  max={ss['max']:,} THB")
    else:
        print(f"SALE: no listings with area data")

    rs = result.rent_stats()
    if rs:
        print(f"RENT ({rs['count']} listings with price):")
        print(f"  Rent/mo    min={rs['min']:,}  avg={rs['avg']:,}  median={rs['median']:,}  max={rs['max']:,} THB")
    else:
        print("RENT: no listings with price data")

    y = result.implied_yield_pct()
    if y:
        print(f"\nImplied gross yield: ~{y}%")
    print(f"{'='*60}")


if __name__ == "__main__":
    import sys

    keywords = sys.argv[1:] or [
        "inspire place abac",
        "15 sukhumvit residences",
        "circle condominium",
        "chateau in town ratchayothin",
    ]

    for kw in keywords:
        try:
            result = check_project(kw)
            if result:
                _print_result(result)
        except (ValueError, RuntimeError) as exc:
            print(f"\nERROR for {kw!r}: {exc}")

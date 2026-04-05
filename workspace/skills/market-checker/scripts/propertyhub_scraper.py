"""
PropertyHub.in.th bulk scraper.

Discovers ALL condo projects via globalSearch pagination, fetches full
project metadata + listings (FOR_SALE / FOR_RENT), and upserts into
PostgreSQL with append-only price history tracking.

Usage:
    python propertyhub_scraper.py                     # full scrape
    python propertyhub_scraper.py --limit 50          # test mode (first 50 projects)
    python propertyhub_scraper.py --create-tables     # init DB tables only
    python propertyhub_scraper.py --zone ZONE_ID      # single zone scrape
"""

from __future__ import annotations

import argparse
import asyncio
import json
import statistics
import sys
import time
from datetime import datetime, timedelta
from typing import Optional

import httpx
import psycopg
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DB_URL = "postgresql://arsapolm@localhost:5432/npa_kb"
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

CONCURRENCY = 10
SEARCH_PAGE_SIZE = 50
LISTING_PAGE_SIZE = 100

# Thai province names for discovery fallback
_THAI_PROVINCES = [
    "กรุงเทพมหานคร", "นนทบุรี", "ปทุมธานี", "สมุทรปราการ", "ชลบุรี",
    "เชียงใหม่", "ภูเก็ต", "นครราชสีมา", "ขอนแก่น", "สงขลา",
    "เชียงราย", "อุดรธานี", "นครปฐม", "ระยอง", "สุราษฎร์ธานี",
    "ประจวบคีรีขันธ์", "กระบี่", "อยุธยา", "สมุทรสาคร", "ลำพูน",
    "หัวหิน", "พัทยา", "สระบุรี", "ลพบุรี", "นครสวรรค์",
    "พิษณุโลก", "อุบลราชธานี", "มหาสารคาม", "บุรีรัมย์", "สุรินทร์",
    "ร้อยเอ็ด", "กาฬสินธุ์", "ศรีสะเกษ", "นครพนม", "สกลนคร",
    "ตรัง", "พังงา", "นครศรีธรรมราช", "สตูล", "ยะลา",
    "ปัตตานี", "นราธิวาส", "ฉะเชิงเทรา", "ปราจีนบุรี", "สระแก้ว",
    "ตราด", "จันทบุรี", "กาญจนบุรี", "ราชบุรี", "เพชรบุรี",
    "สมุทรสงคราม", "สุพรรณบุรี", "อ่างทอง", "ชัยนาท", "อุทัยธานี",
    "นครนายก", "ตาก", "กำแพงเพชร", "สุโขทัย", "พิจิตร",
    "เพชรบูรณ์", "แพร่", "น่าน", "ลำปาง", "อุตรดิตถ์",
    "พะเยา", "แม่ฮ่องสอน", "หนองคาย", "หนองบัวลำภู", "เลย",
    "ชัยภูมิ", "อำนาจเจริญ", "ยโสธร", "มุกดาหาร", "บึงกาฬ",
    "พัทลุง", "ชุมพร", "ระนอง",
]


# ---------------------------------------------------------------------------
# GraphQL queries
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
# Pydantic models
# ---------------------------------------------------------------------------

class SearchProject(BaseModel):
    """Minimal project from globalSearch."""
    id: str
    name: Optional[str] = None
    name_en: Optional[str] = None
    slug: Optional[str] = None
    address: Optional[str] = None
    listing_count_sale: int = 0
    listing_count_rent: int = 0


class ProjectDetail(BaseModel):
    """Full project metadata from project query."""
    id: str
    name: Optional[str] = None
    name_en: Optional[str] = None
    slug: Optional[str] = None
    address: Optional[str] = None
    province_code: Optional[str] = Field(default=None, coerce_numbers_to_str=True)
    district_code: Optional[str] = Field(default=None, coerce_numbers_to_str=True)
    lat: Optional[float] = None
    lng: Optional[float] = None
    completed_year: Optional[str] = None
    total_units: Optional[str] = None
    floors: Optional[str] = None
    buildings: Optional[str] = None
    developer: Optional[str] = None
    utility_fee: Optional[str] = None
    facilities: Optional[dict] = Field(default_factory=dict)
    listing_count_sale: int = 0
    listing_count_rent: int = 0
    raw_json: Optional[dict] = None


class ListingRecord(BaseModel):
    """Parsed listing for DB storage."""
    id: str
    project_id: str
    post_type: str
    title: Optional[str] = None
    price_thb: Optional[float] = None
    area_sqm: Optional[float] = None
    price_per_sqm: Optional[float] = None
    rent_monthly: Optional[float] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    floor: Optional[str] = None
    room_type: Optional[str] = None
    raw_json: Optional[dict] = None


class PriceSnapshot(BaseModel):
    """Computed price aggregate for a project."""
    project_id: str
    sale_median_sqm: Optional[int] = None
    sale_avg_sqm: Optional[int] = None
    sale_min_sqm: Optional[int] = None
    sale_max_sqm: Optional[int] = None
    sale_count: int = 0
    rent_median: Optional[int] = None
    rent_avg: Optional[int] = None
    rent_min: Optional[int] = None
    rent_max: Optional[int] = None
    rent_count: int = 0


class ScrapeStats(BaseModel):
    """Running stats for a scrape run."""
    total_projects: int = 0
    total_listings: int = 0
    new_projects: int = 0
    updated_projects: int = 0
    price_changed: int = 0
    failed_count: int = 0


# ---------------------------------------------------------------------------
# GraphQL helpers
# ---------------------------------------------------------------------------

async def _gql_post(client: httpx.AsyncClient, query: str, variables: dict) -> dict:
    """Execute a GraphQL query and return the data dict."""
    resp = await client.post(
        GQL_URL,
        json={"query": query, "variables": variables},
    )
    resp.raise_for_status()
    body = resp.json()
    if "errors" in body and body["errors"]:
        raise RuntimeError(f"GraphQL error: {body['errors'][0].get('message', body['errors'])}")
    return body.get("data", {})


# ---------------------------------------------------------------------------
# Discovery: find all condo projects
# ---------------------------------------------------------------------------

async def discover_projects_by_search(
    client: httpx.AsyncClient,
    sem: asyncio.Semaphore,
    search_term: str = "คอนโด",
    limit: Optional[int] = None,
) -> dict[str, SearchProject]:
    """Paginate globalSearch to discover condo projects. Returns {id: SearchProject}."""
    found: dict[str, SearchProject] = {}
    page = 1

    while True:
        async with sem:
            data = await _gql_post(client, _GLOBAL_SEARCH_GQL, {
                "name": search_term,
                "locale": "TH",
                "size": SEARCH_PAGE_SIZE,
                "page": page,
                "propertyType": "CONDO",
            })

        gs = data.get("globalSearch", {})
        if gs.get("status") != "SUCCESS":
            print(f"  [warn] globalSearch failed on page {page} for '{search_term}': {gs.get('error')}")
            break

        projects = gs.get("result", {}).get("projects") or []
        pagination = gs.get("result", {}).get("projectPagination") or {}

        for p in projects:
            pid = str(p["id"])
            if pid in found:
                continue
            cnt = p.get("listingCountByPostType") or {}
            found[pid] = SearchProject(
                id=pid,
                name=p.get("name"),
                name_en=p.get("nameEnglish"),
                slug=p.get("slug"),
                address=p.get("address"),
                listing_count_sale=(cnt.get("FOR_SALE") or {}).get("listingCount", 0),
                listing_count_rent=(cnt.get("FOR_RENT") or {}).get("listingCount", 0),
            )

        total_count = pagination.get("totalCount", 0)
        per_page = pagination.get("perPage", SEARCH_PAGE_SIZE)
        total_pages = (total_count + per_page - 1) // per_page if per_page > 0 else 1

        if limit and len(found) >= limit:
            break
        if page >= total_pages or not projects:
            break
        page += 1

    return found


async def discover_all_projects(
    client: httpx.AsyncClient,
    sem: asyncio.Semaphore,
    limit: Optional[int] = None,
) -> dict[str, SearchProject]:
    """
    Multi-strategy project discovery.

    1. Search "คอนโด" (generic condo term) — gets most projects
    2. If under 500 found, try empty string search
    3. Iterate province names to catch regional projects
    """
    print("[discovery] Strategy 1: globalSearch 'คอนโด'")
    all_projects = await discover_projects_by_search(client, sem, "คอนโด", limit)
    print(f"  Found {len(all_projects)} projects")

    if limit and len(all_projects) >= limit:
        return dict(list(all_projects.items())[:limit])

    # Strategy 2: empty string search may return different results
    print("[discovery] Strategy 2: globalSearch ''")
    empty_projects = await discover_projects_by_search(client, sem, "", limit)
    before = len(all_projects)
    all_projects.update(empty_projects)
    print(f"  Found {len(empty_projects)} projects ({len(all_projects) - before} new)")

    if limit and len(all_projects) >= limit:
        return dict(list(all_projects.items())[:limit])

    # Strategy 3: province-by-province search
    print(f"[discovery] Strategy 3: province search ({len(_THAI_PROVINCES)} provinces)")
    for i, province in enumerate(_THAI_PROVINCES):
        if limit and len(all_projects) >= limit:
            break
        remaining = (limit - len(all_projects)) if limit else None
        prov_projects = await discover_projects_by_search(client, sem, province, remaining)
        new_count = sum(1 for pid in prov_projects if pid not in all_projects)
        if new_count > 0:
            print(f"  [{i+1}/{len(_THAI_PROVINCES)}] {province}: {new_count} new")
        all_projects.update(prov_projects)

    print(f"[discovery] Total unique projects: {len(all_projects)}")

    if limit:
        return dict(list(all_projects.items())[:limit])
    return all_projects


# ---------------------------------------------------------------------------
# Project detail + listings fetch
# ---------------------------------------------------------------------------

def _parse_project_detail(raw: dict) -> ProjectDetail:
    """Parse a project query result into ProjectDetail."""
    pi = raw.get("projectInfo") or {}
    loc = raw.get("location") or {}
    cnt = raw.get("listingCountByPostType") or {}
    dev = raw.get("developer") or {}

    return ProjectDetail(
        id=str(raw["id"]),
        name=raw.get("name"),
        name_en=raw.get("nameEnglish"),
        slug=raw.get("slug"),
        address=raw.get("address"),
        province_code=raw.get("provinceCode"),
        district_code=raw.get("districtCode"),
        lat=loc.get("lat"),
        lng=loc.get("lng"),
        completed_year=pi.get("completedYear"),
        total_units=pi.get("totalUnits"),
        floors=pi.get("buildingsFloors"),
        buildings=pi.get("buildingNumbers"),
        developer=dev.get("name") if dev else None,
        utility_fee=pi.get("utilityFee"),
        facilities=raw.get("facilities") or {},
        listing_count_sale=(cnt.get("FOR_SALE") or {}).get("listingCount", 0),
        listing_count_rent=(cnt.get("FOR_RENT") or {}).get("listingCount", 0),
        raw_json=raw,
    )


def _parse_listing(raw: dict, project_id: str) -> Optional[ListingRecord]:
    """Parse a single listing into ListingRecord."""
    post_type = raw.get("postType")
    if not post_type:
        return None

    ri = raw.get("roomInformation") or {}
    area = ri.get("roomArea")

    price_thb: Optional[float] = None
    price_per_sqm: Optional[float] = None
    rent_monthly: Optional[float] = None

    if post_type == "FOR_SALE":
        sale_node = raw.get("price", {}).get("forSale") or {}
        price_thb = sale_node.get("price")
        if price_thb and area and area > 0:
            price_per_sqm = round(price_thb / area, 2)
    elif post_type == "FOR_RENT":
        rent_node = raw.get("price", {}).get("forRent", {}).get("monthly") or {}
        rent_monthly = rent_node.get("price")

    return ListingRecord(
        id=str(raw["id"]),
        project_id=project_id,
        post_type=post_type,
        title=raw.get("title"),
        price_thb=price_thb,
        area_sqm=float(area) if area else None,
        price_per_sqm=price_per_sqm,
        rent_monthly=rent_monthly,
        bedrooms=ri.get("numberOfBed"),
        bathrooms=ri.get("numberOfBath"),
        floor=ri.get("onFloor"),
        room_type=ri.get("roomType"),
        raw_json=raw,
    )


async def fetch_project_detail(
    client: httpx.AsyncClient,
    sem: asyncio.Semaphore,
    project_id: str,
) -> Optional[ProjectDetail]:
    """Fetch full detail for a single project."""
    try:
        async with sem:
            data = await _gql_post(client, _PROJECT_DETAIL_GQL, {
                "projectId": project_id,
                "locale": "TH",
            })
        result = data.get("project", {}).get("result")
        if not result:
            return None
        return _parse_project_detail(result)
    except Exception as exc:
        print(f"  [error] project {project_id} detail: {exc}")
        return None


async def fetch_all_listings(
    client: httpx.AsyncClient,
    sem: asyncio.Semaphore,
    project_id: str,
    post_type: str,
) -> list[ListingRecord]:
    """Fetch all listings for a project + post_type with pagination."""
    listings: list[ListingRecord] = []
    page = 1

    while True:
        try:
            async with sem:
                data = await _gql_post(client, _LISTINGS_GQL, {
                    "locale": "TH",
                    "page": page,
                    "perPage": LISTING_PAGE_SIZE,
                    "listingAttributes": {
                        "projectId": project_id,
                        "postType": post_type,
                    },
                })
        except Exception as exc:
            print(f"  [error] listings {project_id}/{post_type} page {page}: {exc}")
            break

        node = data.get("listings", {})
        if node.get("status") != "SUCCESS":
            break

        raw_results = node.get("result") or []
        for raw in raw_results:
            parsed = _parse_listing(raw, project_id)
            if parsed:
                listings.append(parsed)

        pagination = node.get("pagination") or {}
        total_pages = pagination.get("totalPages", 1)
        if page >= total_pages or not raw_results:
            break
        page += 1

    return listings


def compute_price_snapshot(
    project_id: str,
    sale_listings: list[ListingRecord],
    rent_listings: list[ListingRecord],
) -> PriceSnapshot:
    """Compute price aggregates from listings."""
    sale_prices = [
        int(l.price_per_sqm) for l in sale_listings
        if l.price_per_sqm and l.price_per_sqm > 0
    ]
    rent_prices = [
        int(l.rent_monthly) for l in rent_listings
        if l.rent_monthly and l.rent_monthly > 0
    ]

    snap = PriceSnapshot(project_id=project_id)

    if sale_prices:
        snap.sale_median_sqm = int(statistics.median(sale_prices))
        snap.sale_avg_sqm = int(statistics.mean(sale_prices))
        snap.sale_min_sqm = min(sale_prices)
        snap.sale_max_sqm = max(sale_prices)
        snap.sale_count = len(sale_prices)

    if rent_prices:
        snap.rent_median = int(statistics.median(rent_prices))
        snap.rent_avg = int(statistics.mean(rent_prices))
        snap.rent_min = min(rent_prices)
        snap.rent_max = max(rent_prices)
        snap.rent_count = len(rent_prices)

    return snap


# ---------------------------------------------------------------------------
# Database operations
# ---------------------------------------------------------------------------

def create_tables() -> None:
    """Execute migration SQL to create tables."""
    import pathlib
    migration_path = pathlib.Path(__file__).parent / "migration_002_propertyhub.sql"
    sql = migration_path.read_text()
    with psycopg.connect(DB_URL) as conn:
        conn.execute(sql)
        conn.commit()
    print("[db] Tables created successfully")


def upsert_project(conn: psycopg.Connection, proj: ProjectDetail) -> bool:
    """Upsert a project. Returns True if this is a new project."""
    facilities_json = json.dumps(proj.facilities, ensure_ascii=False) if proj.facilities else None
    raw_json = json.dumps(proj.raw_json, ensure_ascii=False) if proj.raw_json else None

    cur = conn.execute(
        """
        INSERT INTO propertyhub_projects (
            id, name, name_en, slug, address,
            province_code, district_code, lat, lng,
            completed_year, total_units, floors, buildings,
            developer, utility_fee, facilities,
            listing_count_sale, listing_count_rent,
            raw_json, first_seen_at, last_scraped_at
        ) VALUES (
            %(id)s, %(name)s, %(name_en)s, %(slug)s, %(address)s,
            %(province_code)s, %(district_code)s, %(lat)s, %(lng)s,
            %(completed_year)s, %(total_units)s, %(floors)s, %(buildings)s,
            %(developer)s, %(utility_fee)s, %(facilities)s,
            %(listing_count_sale)s, %(listing_count_rent)s,
            %(raw_json)s, now(), now()
        )
        ON CONFLICT (id) DO UPDATE SET
            name = EXCLUDED.name,
            name_en = EXCLUDED.name_en,
            slug = EXCLUDED.slug,
            address = EXCLUDED.address,
            province_code = EXCLUDED.province_code,
            district_code = EXCLUDED.district_code,
            lat = EXCLUDED.lat,
            lng = EXCLUDED.lng,
            completed_year = EXCLUDED.completed_year,
            total_units = EXCLUDED.total_units,
            floors = EXCLUDED.floors,
            buildings = EXCLUDED.buildings,
            developer = EXCLUDED.developer,
            utility_fee = EXCLUDED.utility_fee,
            facilities = EXCLUDED.facilities,
            listing_count_sale = EXCLUDED.listing_count_sale,
            listing_count_rent = EXCLUDED.listing_count_rent,
            raw_json = EXCLUDED.raw_json,
            last_scraped_at = now()
        RETURNING (xmax = 0) AS is_new
        """,
        {
            "id": proj.id,
            "name": proj.name,
            "name_en": proj.name_en,
            "slug": proj.slug,
            "address": proj.address,
            "province_code": proj.province_code,
            "district_code": proj.district_code,
            "lat": proj.lat,
            "lng": proj.lng,
            "completed_year": proj.completed_year,
            "total_units": proj.total_units,
            "floors": proj.floors,
            "buildings": proj.buildings,
            "developer": proj.developer,
            "utility_fee": proj.utility_fee,
            "facilities": facilities_json,
            "listing_count_sale": proj.listing_count_sale,
            "listing_count_rent": proj.listing_count_rent,
            "raw_json": raw_json,
        },
    )
    row = cur.fetchone()
    return row[0] if row else False


def upsert_listing(conn: psycopg.Connection, listing: ListingRecord) -> None:
    """Upsert a single listing."""
    raw_json = json.dumps(listing.raw_json, ensure_ascii=False) if listing.raw_json else None

    conn.execute(
        """
        INSERT INTO propertyhub_listings (
            id, project_id, post_type, title,
            price_thb, area_sqm, price_per_sqm, rent_monthly,
            bedrooms, bathrooms, floor, room_type,
            raw_json, first_seen_at, last_scraped_at, is_active
        ) VALUES (
            %(id)s, %(project_id)s, %(post_type)s, %(title)s,
            %(price_thb)s, %(area_sqm)s, %(price_per_sqm)s, %(rent_monthly)s,
            %(bedrooms)s, %(bathrooms)s, %(floor)s, %(room_type)s,
            %(raw_json)s, now(), now(), true
        )
        ON CONFLICT (id) DO UPDATE SET
            post_type = EXCLUDED.post_type,
            title = EXCLUDED.title,
            price_thb = EXCLUDED.price_thb,
            area_sqm = EXCLUDED.area_sqm,
            price_per_sqm = EXCLUDED.price_per_sqm,
            rent_monthly = EXCLUDED.rent_monthly,
            bedrooms = EXCLUDED.bedrooms,
            bathrooms = EXCLUDED.bathrooms,
            floor = EXCLUDED.floor,
            room_type = EXCLUDED.room_type,
            raw_json = EXCLUDED.raw_json,
            last_scraped_at = now(),
            is_active = true
        """,
        {
            "id": listing.id,
            "project_id": listing.project_id,
            "post_type": listing.post_type,
            "title": listing.title,
            "price_thb": listing.price_thb,
            "area_sqm": listing.area_sqm,
            "price_per_sqm": listing.price_per_sqm,
            "rent_monthly": listing.rent_monthly,
            "bedrooms": listing.bedrooms,
            "bathrooms": listing.bathrooms,
            "floor": listing.floor,
            "room_type": listing.room_type,
            "raw_json": raw_json,
        },
    )


def mark_stale_listings(conn: psycopg.Connection, project_id: str, active_ids: set[str]) -> None:
    """Mark listings not seen this scrape as inactive."""
    if not active_ids:
        conn.execute(
            "UPDATE propertyhub_listings SET is_active = false WHERE project_id = %s",
            (project_id,),
        )
        return

    conn.execute(
        """
        UPDATE propertyhub_listings
        SET is_active = false
        WHERE project_id = %s AND id != ALL(%s) AND is_active = true
        """,
        (project_id, list(active_ids)),
    )


def insert_price_history_if_changed(
    conn: psycopg.Connection,
    snap: PriceSnapshot,
) -> Optional[str]:
    """
    Insert price history row only if values changed vs latest snapshot.
    Returns change_type ('new', 'price_change', 'listing_change') or None if skipped.
    """
    # Check latest snapshot
    row = conn.execute(
        """
        SELECT sale_median_sqm, sale_avg_sqm, sale_count,
               rent_median, rent_avg, rent_count, scraped_at
        FROM propertyhub_price_history
        WHERE project_id = %s
        ORDER BY scraped_at DESC
        LIMIT 1
        """,
        (snap.project_id,),
    ).fetchone()

    if row is None:
        change_type = "new"
    else:
        prev_sale_med, prev_sale_avg, prev_sale_cnt, prev_rent_med, prev_rent_avg, prev_rent_cnt, prev_scraped = row

        # 1-hour dedup: skip if last snapshot is within 1 hour
        if prev_scraped and (datetime.now() - prev_scraped) < timedelta(hours=1):
            return None

        price_changed = (
            prev_sale_med != snap.sale_median_sqm
            or prev_sale_avg != snap.sale_avg_sqm
            or prev_rent_med != snap.rent_median
            or prev_rent_avg != snap.rent_avg
        )
        count_changed = (
            prev_sale_cnt != snap.sale_count
            or prev_rent_cnt != snap.rent_count
        )

        if price_changed:
            change_type = "price_change"
        elif count_changed:
            change_type = "listing_change"
        else:
            return None  # No change

    conn.execute(
        """
        INSERT INTO propertyhub_price_history (
            project_id,
            sale_median_sqm, sale_avg_sqm, sale_min_sqm, sale_max_sqm, sale_count,
            rent_median, rent_avg, rent_min, rent_max, rent_count,
            change_type, scraped_at
        ) VALUES (
            %s,
            %s, %s, %s, %s, %s,
            %s, %s, %s, %s, %s,
            %s, now()
        )
        """,
        (
            snap.project_id,
            snap.sale_median_sqm, snap.sale_avg_sqm, snap.sale_min_sqm, snap.sale_max_sqm, snap.sale_count,
            snap.rent_median, snap.rent_avg, snap.rent_min, snap.rent_max, snap.rent_count,
            change_type,
        ),
    )
    return change_type


def insert_scrape_log(
    conn: psycopg.Connection,
    started_at: datetime,
    stats: ScrapeStats,
    scope: str,
    error: Optional[str] = None,
) -> int:
    """Insert scrape log and return its ID."""
    row = conn.execute(
        """
        INSERT INTO propertyhub_scrape_logs (
            started_at, finished_at,
            total_projects, total_listings,
            new_projects, updated_projects,
            price_changed, failed_count,
            error, scope
        ) VALUES (
            %s, now(),
            %s, %s,
            %s, %s,
            %s, %s,
            %s, %s
        )
        RETURNING id
        """,
        (
            started_at,
            stats.total_projects, stats.total_listings,
            stats.new_projects, stats.updated_projects,
            stats.price_changed, stats.failed_count,
            error, scope,
        ),
    ).fetchone()
    return row[0]


# ---------------------------------------------------------------------------
# Fetch result container
# ---------------------------------------------------------------------------

class FetchResult(BaseModel):
    """Result of fetching one project's data from the API (before DB save)."""
    project_id: str
    detail: Optional[ProjectDetail] = None
    sale_listings: list[ListingRecord] = Field(default_factory=list)
    rent_listings: list[ListingRecord] = Field(default_factory=list)
    failed: bool = False


# ---------------------------------------------------------------------------
# Main scrape pipeline
# ---------------------------------------------------------------------------

async def fetch_single_project(
    client: httpx.AsyncClient,
    sem: asyncio.Semaphore,
    project_id: str,
) -> FetchResult:
    """Fetch detail + listings for one project (no DB writes)."""
    detail = await fetch_project_detail(client, sem, project_id)
    if not detail:
        return FetchResult(project_id=project_id, failed=True)

    # Fetch sale + rent listings concurrently
    sale_task = fetch_all_listings(client, sem, project_id, "FOR_SALE")
    rent_task = fetch_all_listings(client, sem, project_id, "FOR_RENT")
    sale_listings, rent_listings = await asyncio.gather(sale_task, rent_task)

    return FetchResult(
        project_id=project_id,
        detail=detail,
        sale_listings=sale_listings,
        rent_listings=rent_listings,
    )


def save_project_results(
    conn: psycopg.Connection,
    result: FetchResult,
    stats: ScrapeStats,
) -> None:
    """Save one project's fetched data to DB (sequential, safe)."""
    if result.failed or not result.detail:
        stats.failed_count += 1
        return

    all_listings = result.sale_listings + result.rent_listings
    stats.total_listings += len(all_listings)

    is_new = upsert_project(conn, result.detail)
    if is_new:
        stats.new_projects += 1
    else:
        stats.updated_projects += 1

    active_ids: set[str] = set()
    for listing in all_listings:
        upsert_listing(conn, listing)
        active_ids.add(listing.id)

    mark_stale_listings(conn, result.project_id, active_ids)

    snap = compute_price_snapshot(result.project_id, result.sale_listings, result.rent_listings)
    change = insert_price_history_if_changed(conn, snap)
    if change == "price_change":
        stats.price_changed += 1

    conn.commit()
    stats.total_projects += 1


async def run_scraper(
    limit: Optional[int] = None,
    zone_id: Optional[str] = None,
) -> ScrapeStats:
    """Main scraper entry point."""
    started_at = datetime.now()
    scope = f"zone:{zone_id}" if zone_id else "all"
    if limit:
        scope += f" (limit={limit})"

    stats = ScrapeStats()
    sem = asyncio.Semaphore(CONCURRENCY)

    async with httpx.AsyncClient(
        headers=_HEADERS,
        follow_redirects=True,
        timeout=30,
    ) as client:
        # Warm session cookie
        await client.get(SITE_URL)

        # Discovery phase
        print(f"\n{'=' * 60}")
        print(f"PropertyHub Bulk Scraper — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Scope: {scope}")
        print(f"{'=' * 60}\n")

        project_ids: list[str]

        if zone_id:
            print(f"[discovery] Zone mode: {zone_id}")
            found = await discover_projects_by_search(client, sem, zone_id, limit)
            project_ids = list(found.keys())
        else:
            found = await discover_all_projects(client, sem, limit)
            project_ids = list(found.keys())

        total = len(project_ids)
        print(f"\n[scrape] Processing {total} projects...\n")

        # Process in batches: fetch concurrently, then save sequentially
        batch_size = 10
        for batch_start in range(0, total, batch_size):
            batch = project_ids[batch_start : batch_start + batch_size]

            # Parallel HTTP fetch
            fetch_tasks = [
                fetch_single_project(client, sem, pid)
                for pid in batch
            ]
            results = await asyncio.gather(*fetch_tasks)

            # Sequential DB save (one connection, no concurrency issues)
            with psycopg.connect(DB_URL) as conn:
                for result in results:
                    save_project_results(conn, result, stats)

            processed = min(batch_start + batch_size, total)
            if processed % 50 == 0 or processed == total:
                print(
                    f"  [{processed}/{total}] "
                    f"new={stats.new_projects} upd={stats.updated_projects} "
                    f"listings={stats.total_listings} "
                    f"price_chg={stats.price_changed} "
                    f"fail={stats.failed_count}"
                )

    # Log the run
    error_msg = None
    try:
        with psycopg.connect(DB_URL) as conn:
            log_id = insert_scrape_log(conn, started_at, stats, scope, error_msg)
            conn.commit()
        print(f"\n[done] Scrape log id={log_id}")
    except Exception as exc:
        print(f"\n[warn] Failed to write scrape log: {exc}")

    elapsed = (datetime.now() - started_at).total_seconds()
    print(f"\n{'=' * 60}")
    print(f"COMPLETE in {elapsed:.1f}s")
    print(f"  Projects: {stats.total_projects} ({stats.new_projects} new, {stats.updated_projects} updated)")
    print(f"  Listings: {stats.total_listings}")
    print(f"  Price changes: {stats.price_changed}")
    print(f"  Failed: {stats.failed_count}")
    print(f"{'=' * 60}\n")

    return stats


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="PropertyHub.in.th bulk condo scraper",
    )
    parser.add_argument(
        "--limit", type=int, default=None,
        help="Limit number of projects to scrape (test mode)",
    )
    parser.add_argument(
        "--create-tables", action="store_true",
        help="Create DB tables and exit",
    )
    parser.add_argument(
        "--zone", type=str, default=None,
        help="Scrape a single zone by ID/name",
    )
    args = parser.parse_args()

    if args.create_tables:
        create_tables()
        sys.exit(0)

    asyncio.run(run_scraper(limit=args.limit, zone_id=args.zone))


if __name__ == "__main__":
    main()

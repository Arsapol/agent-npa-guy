#!/usr/bin/env python3
"""
hipflat_scraper.py — Bulk scraper for Hipflat project-level market data.

Supports two modes:
1. **Seed mode** — Search Hipflat by project names from DB/file/CLI.
2. **Discover mode** — Crawl Hipflat's province-based project directory
   to find ALL condo projects without any seed list.

Usage:
    # Discover mode: crawl all condo projects by province (~343 requests)
    python hipflat_scraper.py --discover

    # Discover + limit detail fetches
    python hipflat_scraper.py --discover --limit 100

    # Discover specific provinces only
    python hipflat_scraper.py --discover --provinces "bangkok-bm" "nonthaburi-nb"

    # Seed from project_registry + NPA tables
    python hipflat_scraper.py --seed-db

    # Seed from a text file (one project name per line)
    python hipflat_scraper.py --seed-file projects.txt

    # CLI testing with specific names
    python hipflat_scraper.py --names "15 sukhumvit residences" "lumpini suite"

    # Limit to N projects
    python hipflat_scraper.py --seed-db --limit 50

    # Create tables first
    python hipflat_scraper.py --create-tables
"""

import argparse
import hashlib
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import psycopg

# Relative imports from same directory
from hipflat_checker import (
    BASE_HEADERS,
    HIPFLAT_BASE,
    HipflatProject,
    fetch_project_data,
    search_project,
)
from market_checker import _generate_name_variants, _name_similarity
from pydantic import BaseModel

DB_URL = "postgresql://arsapolm@localhost:5432/npa_kb"
MIGRATION_FILE = Path(__file__).parent / "migration_003_hipflat.sql"
DEDUP_WINDOW_SECONDS = 3600  # 1 hour
DISCOVER_FRESHNESS_HOURS = 24  # skip projects scraped within this window

# Hipflat directory URLs
DIRECTORY_BASE = f"{HIPFLAT_BASE}/en/thailand-projects/condo"
PROVINCE_LINK_RE = re.compile(
    r'href="(?:https://www\.hipflat\.co\.th)?/en/thailand-projects/condo/([a-z0-9-]+)"'
)
PROJECT_SLUG_RE = re.compile(
    r'href="(?:https://www\.hipflat\.co\.th)?/en/projects/([a-z0-9-]+)"'
)
DIRECTORY_DELAY = 0.5  # seconds between directory page fetches
DETAIL_DELAY = 0.5  # seconds between project detail fetches


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------


class ScrapeStats(BaseModel):
    """Mutable stats container for a single scraper run."""

    total_searched: int = 0
    total_found: int = 0
    new_count: int = 0
    updated_count: int = 0
    price_changed: int = 0
    not_found_count: int = 0
    failed_count: int = 0


class SeedProject(BaseModel):
    """A project name to search for, with optional metadata."""

    name: str
    source: str = (
        "cli"  # 'project_registry', 'bam', 'jam', 'sam', 'ktb', 'kbank', 'file', 'cli'
    )
    existing_uuid: Optional[str] = None  # if already known from project_registry


class DiscoveredProject(BaseModel):
    """A project found via directory crawl."""

    slug: str
    province_route: str  # e.g. "bangkok-bm"


# ---------------------------------------------------------------------------
# DB helpers
# ---------------------------------------------------------------------------


def create_tables() -> None:
    """Run migration SQL to create hipflat tables."""
    sql = MIGRATION_FILE.read_text()
    with psycopg.connect(DB_URL) as conn:
        conn.execute(sql)
        conn.commit()
    print(f"Tables created from {MIGRATION_FILE.name}")


def _get_existing_project(conn: psycopg.Connection, uuid: str) -> Optional[dict]:
    """Fetch existing hipflat_projects row as dict, or None."""
    cur = conn.execute(
        """
        SELECT uuid, avg_sale_sqm, avg_sold_sqm, units_for_sale, units_for_rent,
               rent_price_min, rent_price_max, yoy_change_pct, district_avg_sale_sqm,
               raw_html_hash
        FROM hipflat_projects WHERE uuid = %s
        """,
        (uuid,),
    )
    row = cur.fetchone()
    if row is None:
        return None
    cols = [
        "uuid",
        "avg_sale_sqm",
        "avg_sold_sqm",
        "units_for_sale",
        "units_for_rent",
        "rent_price_min",
        "rent_price_max",
        "yoy_change_pct",
        "district_avg_sale_sqm",
        "raw_html_hash",
    ]
    return dict(zip(cols, row))


def _has_recent_history(conn: psycopg.Connection, uuid: str) -> bool:
    """Check if a price_history record exists within the dedup window."""
    cur = conn.execute(
        """
        SELECT 1 FROM hipflat_price_history
        WHERE project_uuid = %s
          AND scraped_at > now() - interval '%s seconds'
        LIMIT 1
        """,
        (uuid, DEDUP_WINDOW_SECONDS),
    )
    return cur.fetchone() is not None


def _price_changed(old: dict, proj: HipflatProject) -> bool:
    """Check if any tracked price field changed vs existing row."""
    checks = [
        (old.get("avg_sale_sqm"), proj.avg_sale_sqm_thb),
        (old.get("avg_sold_sqm"), proj.avg_sold_sqm_thb),
        (old.get("rent_price_min"), proj.rent_price_min),
        (old.get("rent_price_max"), proj.rent_price_max),
    ]
    for old_val, new_val in checks:
        if old_val is not None and new_val is not None and old_val != new_val:
            return True
    return False


def _compute_html_hash(proj: HipflatProject) -> str:
    """Deterministic hash of key fields for change detection."""
    parts = [
        str(proj.avg_sale_sqm_thb or ""),
        str(proj.avg_sold_sqm_thb or ""),
        str(proj.units_for_sale or ""),
        str(proj.units_for_rent or ""),
        str(proj.rent_price_min or ""),
        str(proj.rent_price_max or ""),
        str(proj.yoy_change_pct or ""),
    ]
    return hashlib.md5("|".join(parts).encode()).hexdigest()


def _is_recently_scraped(conn: psycopg.Connection, slug: str, hours: int = DISCOVER_FRESHNESS_HOURS) -> bool:
    """Check if a project (by uuid/slug) was scraped within the freshness window."""
    cur = conn.execute(
        """
        SELECT 1 FROM hipflat_projects
        WHERE uuid = %s
          AND last_scraped_at > %s
        LIMIT 1
        """,
        (slug, datetime.now() - timedelta(hours=hours)),
    )
    return cur.fetchone() is not None


def upsert_project(
    conn: psycopg.Connection, proj: HipflatProject, stats: ScrapeStats
) -> None:
    """Upsert a HipflatProject into hipflat_projects + track price history."""
    html_hash = _compute_html_hash(proj)
    existing = _get_existing_project(conn, proj.uuid)

    if existing is None:
        # INSERT new project
        conn.execute(
            """
            INSERT INTO hipflat_projects (
                uuid, name_th, name_en, slug_url, lat, lng,
                avg_sale_sqm, avg_sold_sqm, sale_price_min, sale_price_max,
                rent_price_min, rent_price_max, units_for_sale, units_for_rent,
                sold_below_asking_pct, avg_days_on_market, price_trend, yoy_change_pct,
                year_completed, floors, total_units, service_charge_sqm,
                district_name, district_avg_sale_sqm, district_avg_rent_sqm,
                raw_html_hash, first_seen_at, last_scraped_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s, %s,
                %s, %s, %s,
                %s, now(), now()
            )
            """,
            (
                proj.uuid,
                proj.name_th,
                proj.name_en,
                proj.slug_url,
                proj.lat,
                proj.lng,
                proj.avg_sale_sqm_thb,
                proj.avg_sold_sqm_thb,
                proj.sale_price_min,
                proj.sale_price_max,
                proj.rent_price_min,
                proj.rent_price_max,
                proj.units_for_sale,
                proj.units_for_rent,
                proj.sold_below_asking_pct,
                proj.avg_days_on_market,
                proj.price_trend,
                proj.yoy_change_pct,
                proj.year_completed,
                proj.floors,
                proj.total_units,
                proj.service_charge_sqm,
                proj.district_name,
                proj.district_avg_sale_sqm,
                proj.district_avg_rent_sqm,
                html_hash,
            ),
        )
        stats.new_count += 1

        # Insert 'new' history entry (skip dedup check for new projects)
        conn.execute(
            """
            INSERT INTO hipflat_price_history (
                project_uuid, avg_sale_sqm, avg_sold_sqm,
                units_for_sale, units_for_rent, rent_price_min, rent_price_max,
                yoy_change_pct, district_avg_sale_sqm, change_type, scraped_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'new', now())
            """,
            (
                proj.uuid,
                proj.avg_sale_sqm_thb,
                proj.avg_sold_sqm_thb,
                proj.units_for_sale,
                proj.units_for_rent,
                proj.rent_price_min,
                proj.rent_price_max,
                proj.yoy_change_pct,
                proj.district_avg_sale_sqm,
            ),
        )
    else:
        # UPDATE existing project
        conn.execute(
            """
            UPDATE hipflat_projects SET
                name_th = COALESCE(%s, name_th),
                name_en = COALESCE(%s, name_en),
                slug_url = COALESCE(%s, slug_url),
                lat = COALESCE(%s, lat),
                lng = COALESCE(%s, lng),
                avg_sale_sqm = %s,
                avg_sold_sqm = %s,
                sale_price_min = %s,
                sale_price_max = %s,
                rent_price_min = %s,
                rent_price_max = %s,
                units_for_sale = %s,
                units_for_rent = %s,
                sold_below_asking_pct = %s,
                avg_days_on_market = %s,
                price_trend = %s,
                yoy_change_pct = %s,
                year_completed = COALESCE(%s, year_completed),
                floors = COALESCE(%s, floors),
                total_units = COALESCE(%s, total_units),
                service_charge_sqm = COALESCE(%s, service_charge_sqm),
                district_name = COALESCE(%s, district_name),
                district_avg_sale_sqm = %s,
                district_avg_rent_sqm = %s,
                raw_html_hash = %s,
                last_scraped_at = now()
            WHERE uuid = %s
            """,
            (
                proj.name_th,
                proj.name_en,
                proj.slug_url,
                proj.lat,
                proj.lng,
                proj.avg_sale_sqm_thb,
                proj.avg_sold_sqm_thb,
                proj.sale_price_min,
                proj.sale_price_max,
                proj.rent_price_min,
                proj.rent_price_max,
                proj.units_for_sale,
                proj.units_for_rent,
                proj.sold_below_asking_pct,
                proj.avg_days_on_market,
                proj.price_trend,
                proj.yoy_change_pct,
                proj.year_completed,
                proj.floors,
                proj.total_units,
                proj.service_charge_sqm,
                proj.district_name,
                proj.district_avg_sale_sqm,
                proj.district_avg_rent_sqm,
                html_hash,
                proj.uuid,
            ),
        )
        stats.updated_count += 1

        # Track price changes (with 1-hour dedup window)
        if _price_changed(existing, proj) and not _has_recent_history(conn, proj.uuid):
            conn.execute(
                """
                INSERT INTO hipflat_price_history (
                    project_uuid, avg_sale_sqm, avg_sold_sqm,
                    units_for_sale, units_for_rent, rent_price_min, rent_price_max,
                    yoy_change_pct, district_avg_sale_sqm, change_type, scraped_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'price_change', now())
                """,
                (
                    proj.uuid,
                    proj.avg_sale_sqm_thb,
                    proj.avg_sold_sqm_thb,
                    proj.units_for_sale,
                    proj.units_for_rent,
                    proj.rent_price_min,
                    proj.rent_price_max,
                    proj.yoy_change_pct,
                    proj.district_avg_sale_sqm,
                ),
            )
            stats.price_changed += 1


# ---------------------------------------------------------------------------
# Seed list acquisition
# ---------------------------------------------------------------------------


def _seed_from_db() -> list[SeedProject]:
    """Gather project names from project_registry + NPA tables."""
    seeds: list[SeedProject] = []
    seen_lower: set[str] = set()

    def _add(name: str, source: str, uuid: Optional[str] = None) -> None:
        clean = name.strip()
        if not clean or clean.lower() in seen_lower:
            return
        seen_lower.add(clean.lower())
        seeds.append(SeedProject(name=clean, source=source, existing_uuid=uuid))

    with psycopg.connect(DB_URL) as conn:
        # 1. project_registry — highest quality names, may have hipflat_uuid
        cur = conn.execute(
            "SELECT name_canonical, name_th, name_en, hipflat_uuid FROM project_registry"
        )
        for row in cur.fetchall():
            name_canonical, name_th, name_en, hipflat_uuid = row
            _add(name_canonical, "project_registry", hipflat_uuid)
            if name_th:
                _add(name_th, "project_registry", hipflat_uuid)
            if name_en:
                _add(name_en, "project_registry", hipflat_uuid)

        # 2. BAM — project_th, project_en
        cur = conn.execute(
            "SELECT DISTINCT project_th FROM bam_properties WHERE project_th IS NOT NULL AND project_th != ''"
        )
        for (name,) in cur.fetchall():
            _add(name, "bam")
        cur = conn.execute(
            "SELECT DISTINCT project_en FROM bam_properties WHERE project_en IS NOT NULL AND project_en != ''"
        )
        for (name,) in cur.fetchall():
            _add(name, "bam")

        # 3. JAM — project_th, project_en
        cur = conn.execute(
            "SELECT DISTINCT project_th FROM jam_properties WHERE project_th IS NOT NULL AND project_th != ''"
        )
        for (name,) in cur.fetchall():
            _add(name, "jam")
        cur = conn.execute(
            "SELECT DISTINCT project_en FROM jam_properties WHERE project_en IS NOT NULL AND project_en != ''"
        )
        for (name,) in cur.fetchall():
            _add(name, "jam")

        # 4. SAM — project_name
        cur = conn.execute(
            "SELECT DISTINCT project_name FROM sam_properties WHERE project_name IS NOT NULL AND project_name != ''"
        )
        for (name,) in cur.fetchall():
            _add(name, "sam")

        # 5. KBank — building_th (closest to project name), village_th
        cur = conn.execute(
            "SELECT DISTINCT building_th FROM kbank_properties WHERE building_th IS NOT NULL AND building_th != ''"
        )
        for (name,) in cur.fetchall():
            _add(name, "kbank")
        cur = conn.execute(
            "SELECT DISTINCT village_th FROM kbank_properties WHERE village_th IS NOT NULL AND village_th != ''"
        )
        for (name,) in cur.fetchall():
            _add(name, "kbank")

        # 6. KTB — coll_desc (property description, may contain project name)
        # KTB coll_desc can be long; only use short ones likely to be project names
        cur = conn.execute(
            """
            SELECT DISTINCT coll_desc FROM ktb_properties
            WHERE coll_desc IS NOT NULL AND coll_desc != ''
              AND length(coll_desc) <= 100
            """
        )
        for (name,) in cur.fetchall():
            _add(name, "ktb")

    return seeds


def _seed_from_file(filepath: str) -> list[SeedProject]:
    """Read project names from a text file, one per line."""
    seeds: list[SeedProject] = []
    seen_lower: set[str] = set()
    with open(filepath) as f:
        for line in f:
            name = line.strip()
            if name and not name.startswith("#") and name.lower() not in seen_lower:
                seen_lower.add(name.lower())
                seeds.append(SeedProject(name=name, source="file"))
    return seeds


def _seed_from_names(names: list[str]) -> list[SeedProject]:
    """Create seed list from CLI-provided names."""
    return [SeedProject(name=n.strip(), source="cli") for n in names if n.strip()]


# ---------------------------------------------------------------------------
# Directory discovery (--discover mode)
# ---------------------------------------------------------------------------


def _fetch_directory_page(url: str) -> Optional[str]:
    """Fetch a Hipflat directory page, return HTML string or None on error.

    Uses urllib.request consistent with hipflat_checker.py.
    Returns None on HTTP 500 (end of pagination) or other errors.
    """
    headers = {**BASE_HEADERS, "Accept": "text/html,application/xhtml+xml"}
    req = urllib.request.Request(url, headers=headers)
    try:
        resp = urllib.request.urlopen(req, timeout=15)
        return resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        if e.code == 500:
            return None  # pagination exhausted
        raise
    except (urllib.error.URLError, TimeoutError):
        return None


def _extract_province_routes(html: str) -> list[str]:
    """Extract province sub-route identifiers from the main directory page.

    Looks for links like href="/en/thailand-projects/condo/bangkok-bm" and returns
    the province slug (e.g. "bangkok-bm").
    """
    matches = PROVINCE_LINK_RE.findall(html)
    # Deduplicate while preserving order
    seen: set[str] = set()
    routes: list[str] = []
    for route in matches:
        if route not in seen:
            seen.add(route)
            routes.append(route)
    return routes


def _extract_project_slugs(html: str) -> list[str]:
    """Extract project slugs from a directory listing page.

    Looks for links like href="/en/projects/ratchada-city-18-juszwl"
    and returns the slug part.
    """
    matches = PROJECT_SLUG_RE.findall(html)
    seen: set[str] = set()
    slugs: list[str] = []
    for slug in matches:
        if slug not in seen:
            seen.add(slug)
            slugs.append(slug)
    return slugs


def discover_province_routes(province_filter: Optional[list[str]] = None) -> list[str]:
    """Fetch the main directory and extract province sub-routes.

    Args:
        province_filter: If provided, only return routes whose province
            slug matches one of these values (e.g. ["bangkok-bm", "nonthaburi-nb"]).

    Returns:
        List of province slugs (e.g. ["bangkok-bm", "nonthaburi-nb", ...]).
    """
    print(f"Fetching main directory: {DIRECTORY_BASE}")
    html = _fetch_directory_page(DIRECTORY_BASE)
    if html is None:
        print("  ERROR: Failed to fetch main directory page")
        return []

    routes = _extract_province_routes(html)
    print(f"  Found {len(routes)} province routes")

    if province_filter:
        filter_set = {p.lower() for p in province_filter}
        routes = [r for r in routes if r in filter_set]
        print(f"  Filtered to {len(routes)} provinces: {province_filter}")

    return routes


def discover_province_projects(province_slug: str) -> list[str]:
    """Paginate through a province's directory pages, collecting project slugs.

    Args:
        province_slug: e.g. "bangkok-bm"

    Returns:
        List of unique project slugs found across all pages.
    """
    all_slugs: list[str] = []
    seen: set[str] = set()
    page = 1

    while True:
        url = f"{HIPFLAT_BASE}/en/thailand-projects/condo/{province_slug}?page={page}"
        html = _fetch_directory_page(url)

        if html is None:
            break  # HTTP 500 or error = end of pagination

        slugs = _extract_project_slugs(html)
        if not slugs:
            break  # empty page = no more results

        new_count = 0
        for slug in slugs:
            if slug not in seen:
                seen.add(slug)
                all_slugs.append(slug)
                new_count += 1

        # If no new slugs on this page, we've looped
        if new_count == 0:
            break

        page += 1
        time.sleep(DIRECTORY_DELAY)

    return all_slugs


def discover_projects(
    province_filter: Optional[list[str]] = None,
) -> list[DiscoveredProject]:
    """Crawl Hipflat's province-based directory to discover all condo projects.

    Steps:
    1. Fetch main directory to get all province sub-routes
    2. For each province, paginate to collect all project slugs
    3. Return deduplicated list of DiscoveredProject

    Args:
        province_filter: Optional list of province identifiers to limit crawl.
    """
    routes = discover_province_routes(province_filter)
    if not routes:
        return []

    all_projects: list[DiscoveredProject] = []
    seen_slugs: set[str] = set()

    for i, route in enumerate(routes):
        print(f"  [{i + 1}/{len(routes)}] Crawling {route}...", end=" ", flush=True)

        slugs = discover_province_projects(route)
        new_count = 0
        for slug in slugs:
            if slug not in seen_slugs:
                seen_slugs.add(slug)
                all_projects.append(DiscoveredProject(slug=slug, province_route=route))
                new_count += 1

        print(f"{len(slugs)} found, {new_count} new (total: {len(all_projects)})")
        time.sleep(DIRECTORY_DELAY)

    print(f"\nDirectory crawl complete: {len(all_projects)} unique projects across {len(routes)} provinces")
    return all_projects


def run_discover(
    province_filter: Optional[list[str]] = None,
    limit: Optional[int] = None,
) -> ScrapeStats:
    """Run the full discover pipeline: crawl directory + fetch project details.

    Steps:
    1. Crawl directory to get all project slugs
    2. For each slug, skip if scraped within last 24 hours
    3. Fetch full project data via fetch_project_data(slug)
    4. Upsert to hipflat_projects table
    """
    stats = ScrapeStats()

    # Phase 1: Directory crawl
    print(f"\n{'=' * 60}")
    print("Phase 1: Directory crawl")
    print(f"{'=' * 60}")
    discovered = discover_projects(province_filter)

    if not discovered:
        print("No projects discovered. Exiting.")
        return stats

    work = discovered[:limit] if limit else discovered

    # Phase 2: Fetch project details
    print(f"\n{'=' * 60}")
    print(f"Phase 2: Fetching details for {len(work)} projects")
    print(f"{'=' * 60}")

    # Start scrape log
    log_id: Optional[int] = None
    with psycopg.connect(DB_URL) as conn:
        cur = conn.execute(
            "INSERT INTO hipflat_scrape_logs (started_at, seed_source) VALUES (now(), %s) RETURNING id",
            ("discover",),
        )
        log_id = cur.fetchone()[0]
        conn.commit()

    started_at = datetime.now()
    skipped_fresh = 0

    for i, dp in enumerate(work):
        stats.total_searched += 1

        # Progress every 20 projects
        if i > 0 and i % 20 == 0:
            elapsed = (datetime.now() - started_at).total_seconds()
            rate = i / elapsed if elapsed > 0 else 0
            print(
                f"  [{i}/{len(work)}] "
                f"found={stats.total_found} new={stats.new_count} "
                f"updated={stats.updated_count} skipped_fresh={skipped_fresh} "
                f"failed={stats.failed_count} "
                f"({rate:.1f} proj/s)"
            )

        try:
            # Check freshness — skip if scraped within last 24 hours
            with psycopg.connect(DB_URL) as conn:
                if _is_recently_scraped(conn, dp.slug):
                    skipped_fresh += 1
                    continue

            # Fetch full project data using slug
            proj = fetch_project_data(dp.slug)
            stats.total_found += 1

            # Upsert to DB
            with psycopg.connect(DB_URL) as conn:
                upsert_project(conn, proj, stats)
                conn.commit()

            time.sleep(DETAIL_DELAY)

        except Exception as e:
            stats.failed_count += 1
            print(f"  ERROR [{dp.slug}]: {e}")
            time.sleep(1)

    # Finalize scrape log
    error_msg: Optional[str] = None
    if stats.failed_count > 0:
        error_msg = f"{stats.failed_count} projects failed"

    with psycopg.connect(DB_URL) as conn:
        conn.execute(
            """
            UPDATE hipflat_scrape_logs SET
                finished_at = now(),
                total_searched = %s,
                total_found = %s,
                new_count = %s,
                updated_count = %s,
                price_changed = %s,
                not_found_count = %s,
                failed_count = %s,
                error = %s
            WHERE id = %s
            """,
            (
                stats.total_searched,
                stats.total_found,
                stats.new_count,
                stats.updated_count,
                stats.price_changed,
                skipped_fresh,  # reuse not_found_count column for skipped count
                stats.failed_count,
                error_msg,
                log_id,
            ),
        )
        conn.commit()

    elapsed = (datetime.now() - started_at).total_seconds()
    print(f"\n{'=' * 60}")
    print(f"  Done in {elapsed:.1f}s")
    print(f"  Discovered:    {len(discovered)}")
    print(f"  Processed:     {stats.total_searched}")
    print(f"  Fetched:       {stats.total_found}")
    print(f"  New:           {stats.new_count}")
    print(f"  Updated:       {stats.updated_count}")
    print(f"  Price Δ:       {stats.price_changed}")
    print(f"  Skipped fresh: {skipped_fresh}")
    print(f"  Failed:        {stats.failed_count}")
    print(f"{'=' * 60}\n")

    return stats


# ---------------------------------------------------------------------------
# Smart search: reuse market_checker's variant logic
# ---------------------------------------------------------------------------


def smart_search(name: str) -> Optional[tuple[str, str]]:
    """Try multiple name variants, return (uuid, matched_name) or None.

    Uses the same multi-variant strategy as market_checker._smart_search_hipflat
    but returns only the match info (no fetch yet).
    """
    variants = _generate_name_variants(name)
    best_result: Optional[dict] = None
    best_score = 0.0

    for variant in variants:
        try:
            results = search_project(variant)
        except Exception:
            continue

        if not results:
            continue

        # Single result = trust the platform
        if len(results) == 1:
            best_result = results[0]
            best_score = 1.0
            break

        for r in results[:3]:
            r_name = r.get("name", "")
            score = max(_name_similarity(v, r_name) for v in variants)
            if score > best_score:
                best_score = score
                best_result = r

        if best_score >= 0.5:
            break

        time.sleep(0.3)

    if best_result is None or best_score < 0.15:
        return None

    return best_result["id"], best_result.get("name", "")


# ---------------------------------------------------------------------------
# Main scraper loop
# ---------------------------------------------------------------------------


def run_scraper(
    seeds: list[SeedProject],
    limit: Optional[int] = None,
) -> ScrapeStats:
    """Run the bulk scraper on a seed list. Returns stats."""
    stats = ScrapeStats()
    work = seeds[:limit] if limit else seeds

    print(f"\nHipflat bulk scraper — {len(work)} projects to process")
    print(f"{'=' * 60}")

    # Start scrape log
    log_id: Optional[int] = None
    seed_source = work[0].source if work else "unknown"
    with psycopg.connect(DB_URL) as conn:
        cur = conn.execute(
            "INSERT INTO hipflat_scrape_logs (started_at, seed_source) VALUES (now(), %s) RETURNING id",
            (seed_source,),
        )
        log_id = cur.fetchone()[0]
        conn.commit()

    started_at = datetime.now()

    for i, seed in enumerate(work):
        stats.total_searched += 1

        # Progress every 20 projects
        if i > 0 and i % 20 == 0:
            elapsed = (datetime.now() - started_at).total_seconds()
            rate = i / elapsed if elapsed > 0 else 0
            print(
                f"  [{i}/{len(work)}] "
                f"found={stats.total_found} new={stats.new_count} "
                f"updated={stats.updated_count} price_chg={stats.price_changed} "
                f"not_found={stats.not_found_count} failed={stats.failed_count} "
                f"({rate:.1f} proj/s)"
            )

        try:
            # Step 1: If we already have a UUID (from project_registry), skip search
            uuid: Optional[str] = seed.existing_uuid
            matched_name = seed.name

            if uuid is None:
                match = smart_search(seed.name)
                if match is None:
                    stats.not_found_count += 1
                    continue
                uuid, matched_name = match
                time.sleep(0.5)

            # Step 2: Fetch full project data
            proj = fetch_project_data(uuid)
            stats.total_found += 1

            # Step 3: Upsert to DB
            with psycopg.connect(DB_URL) as conn:
                upsert_project(conn, proj, stats)
                conn.commit()

            time.sleep(0.5)

        except Exception as e:
            stats.failed_count += 1
            print(f"  ERROR [{seed.name}]: {e}")
            time.sleep(1)

    # Finalize scrape log
    error_msg: Optional[str] = None
    if stats.failed_count > 0:
        error_msg = f"{stats.failed_count} projects failed"

    with psycopg.connect(DB_URL) as conn:
        conn.execute(
            """
            UPDATE hipflat_scrape_logs SET
                finished_at = now(),
                total_searched = %s,
                total_found = %s,
                new_count = %s,
                updated_count = %s,
                price_changed = %s,
                not_found_count = %s,
                failed_count = %s,
                error = %s
            WHERE id = %s
            """,
            (
                stats.total_searched,
                stats.total_found,
                stats.new_count,
                stats.updated_count,
                stats.price_changed,
                stats.not_found_count,
                stats.failed_count,
                error_msg,
                log_id,
            ),
        )
        conn.commit()

    elapsed = (datetime.now() - started_at).total_seconds()
    print(f"\n{'=' * 60}")
    print(f"  Done in {elapsed:.1f}s")
    print(f"  Searched: {stats.total_searched}")
    print(f"  Found:    {stats.total_found}")
    print(f"  New:      {stats.new_count}")
    print(f"  Updated:  {stats.updated_count}")
    print(f"  Price Δ:  {stats.price_changed}")
    print(f"  Not found:{stats.not_found_count}")
    print(f"  Failed:   {stats.failed_count}")
    print(f"{'=' * 60}\n")

    return stats


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Hipflat bulk scraper — project-level market data",
        epilog=(
            "Examples:\n"
            "  python hipflat_scraper.py --discover\n"
            "  python hipflat_scraper.py --discover --limit 100\n"
            '  python hipflat_scraper.py --discover --provinces "bangkok-bm" "nonthaburi-nb"\n'
            "  python hipflat_scraper.py --seed-db\n"
            "  python hipflat_scraper.py --seed-db --limit 50\n"
            "  python hipflat_scraper.py --seed-file projects.txt\n"
            '  python hipflat_scraper.py --names "15 sukhumvit residences" "lumpini suite"\n'
            "  python hipflat_scraper.py --create-tables\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--discover",
        action="store_true",
        help="Crawl Hipflat directory by province to discover all condo projects",
    )
    parser.add_argument(
        "--provinces",
        nargs="+",
        help="Limit --discover to specific provinces (e.g. 'bangkok-bm' 'nonthaburi-nb')",
    )
    parser.add_argument(
        "--seed-db",
        action="store_true",
        help="Seed project names from project_registry + NPA tables",
    )
    parser.add_argument(
        "--seed-file",
        type=str,
        help="Path to text file with project names (one per line)",
    )
    parser.add_argument(
        "--names",
        nargs="+",
        help="Project names to search (for CLI testing)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        help="Limit to first N projects (applies to both discover and seed modes)",
    )
    parser.add_argument(
        "--create-tables",
        action="store_true",
        help="Run migration SQL to create hipflat tables",
    )
    args = parser.parse_args()

    if args.create_tables:
        create_tables()
        if not (args.discover or args.seed_db or args.seed_file or args.names):
            return

    # Discover mode — crawl directory
    if args.discover:
        run_discover(province_filter=args.provinces, limit=args.limit)
        return

    if args.provinces and not args.discover:
        parser.error("--provinces requires --discover")

    # Build seed list
    seeds: list[SeedProject] = []

    if args.seed_db:
        seeds = _seed_from_db()
        print(f"Loaded {len(seeds)} project names from DB")
    elif args.seed_file:
        seeds = _seed_from_file(args.seed_file)
        print(f"Loaded {len(seeds)} project names from {args.seed_file}")
    elif args.names:
        seeds = _seed_from_names(args.names)
    else:
        parser.print_help()
        print("\nError: specify --discover, --seed-db, --seed-file, or --names")
        sys.exit(1)

    if not seeds:
        print("No project names to process.")
        sys.exit(0)

    run_scraper(seeds, limit=args.limit)


if __name__ == "__main__":
    main()

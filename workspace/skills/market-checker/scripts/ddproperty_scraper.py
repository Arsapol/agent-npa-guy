#!/usr/bin/env python3
"""
ddproperty_scraper.py — Targeted scraper for DDProperty.com market data.

Two modes:
  1. TARGETED (default) — Camoufox + project-by-name lookup
  2. DISCOVER (--discover) — Bulk crawl ALL condo listings via JSON API

Architecture (both modes):
  - Camoufox (headless Firefox) acquires Cloudflare cookies once
  - httpx for all subsequent API calls (fast, lightweight)
  - Cookies saved to /tmp/ddproperty_cookies.json (reused if fresh)
  - Auto-refresh on 403 (cookie expired)

Discover mode specifics:
  - /_next/data/{BUILD_ID}/en/condo-for-sale.json?page=N  (no freetext)
  - ~57,000 sale listings across ~2,868 pages (~20/page)
  - Concurrent page fetches (5 workers) — ~6 min vs ~24 min sequential
  - Per-page DB upserts for crash resilience
  - Resume support via /tmp/ddproperty_discover_progress.json

Usage:
    # === Targeted mode ===
    python ddproperty_scraper.py --seed-db
    python ddproperty_scraper.py --seed-file projects.txt
    python ddproperty_scraper.py --names "triple y residence" "15 sukhumvit residences"
    python ddproperty_scraper.py --seed-db --limit 50
    python ddproperty_scraper.py --create-tables
    python ddproperty_scraper.py --seed-db --refresh-build-id
    python ddproperty_scraper.py --names "triple y" --skip-camoufox

    # === Discover mode ===
    python ddproperty_scraper.py --discover                     # sale only (resumes if interrupted)
    python ddproperty_scraper.py --discover --discover-rent     # sale + rent
    python ddproperty_scraper.py --discover --limit 10          # first 10 pages only
    python ddproperty_scraper.py --discover --build-id ABC123   # override BUILD_ID
    python ddproperty_scraper.py --discover --start-page 500    # resume from page 500
    python ddproperty_scraper.py --discover --force              # ignore saved progress, start fresh
"""

import argparse
import asyncio
import json
import re
import statistics
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

import httpx
import psycopg
from pydantic import BaseModel, Field

# Relative imports from same directory
from ddproperty_checker import (
    BASE_URL,
    BUILD_ID,
    HEADERS,
    ListingSummary,
    ProjectInfo,
    fetch_build_id,
    fetch_listings,
    get_cf_cookies,
    lookup_project,
)
from market_checker import _generate_name_variants, _name_similarity

DB_URL = "postgresql://arsapolm@localhost:5432/npa_kb"
MIGRATION_FILE = Path(__file__).parent / "migration_005_ddproperty.sql"
COOKIE_FILE = Path("/tmp/ddproperty_cookies.json")
COOKIE_TTL_SECONDS = 25 * 60  # 25 minutes (conservative; actual ~30min)
DEDUP_WINDOW_SECONDS = 3600  # 1 hour
REQUEST_DELAY = 0.5  # seconds between API requests

# Concurrency settings
DISCOVER_CONCURRENCY = 5  # concurrent page fetches in discover mode
TARGETED_CONCURRENCY = 3  # concurrent project lookups in targeted mode
PROGRESS_FILE = Path("/tmp/ddproperty_discover_progress.json")


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------


class ScrapeStats(BaseModel):
    """Stats container for a single scraper run."""

    total_projects: int = 0
    total_listings: int = 0
    new_projects: int = 0
    updated_projects: int = 0
    price_changed: int = 0
    failed_count: int = 0
    cookie_refreshes: int = 0


class SeedProject(BaseModel):
    """A project name to search for, with optional metadata."""

    name: str
    source: str = "cli"
    existing_ddproperty_id: Optional[int] = None


class ScrapedProject(BaseModel):
    """Full scraped data for one project."""

    project: ProjectInfo
    raw_project_json: Optional[dict] = None
    sale_listings: list[ListingSummary] = Field(default_factory=list)
    rent_listings: list[ListingSummary] = Field(default_factory=list)
    sale_count: int = 0
    rent_count: int = 0
    sale_raw: list[dict] = Field(default_factory=list)
    rent_raw: list[dict] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Cookie management
# ---------------------------------------------------------------------------


def _save_cookies(cookies: dict[str, str]) -> None:
    """Save cookies to disk with timestamp."""
    payload = {
        "cookies": cookies,
        "saved_at": datetime.now().isoformat(),
    }
    COOKIE_FILE.write_text(json.dumps(payload, ensure_ascii=False))


def _load_cookies() -> Optional[dict[str, str]]:
    """Load cookies from disk if fresh enough."""
    if not COOKIE_FILE.exists():
        return None

    try:
        payload = json.loads(COOKIE_FILE.read_text())
        saved_at = datetime.fromisoformat(payload["saved_at"])
        age_seconds = (datetime.now() - saved_at).total_seconds()

        if age_seconds > COOKIE_TTL_SECONDS:
            return None

        cookies = payload["cookies"]
        if not cookies:
            return None

        return cookies
    except (KeyError, json.JSONDecodeError, ValueError):
        return None


async def _acquire_cookies(skip_camoufox: bool = False) -> dict[str, str]:
    """Acquire cookies: try saved file first, then Camoufox."""
    saved = _load_cookies()
    if saved is not None:
        print(f"  Reusing saved cookies from {COOKIE_FILE} ({len(saved)} cookies)")
        return saved

    if skip_camoufox:
        raise RuntimeError(
            f"--skip-camoufox specified but no fresh cookies at {COOKIE_FILE}. "
            "Run once without --skip-camoufox to acquire cookies."
        )

    print("  Launching Camoufox to acquire Cloudflare cookies...")
    cookies = await get_cf_cookies()
    print(f"  Got {len(cookies)} cookies: {list(cookies.keys())}")
    _save_cookies(cookies)
    return cookies


# ---------------------------------------------------------------------------
# DB helpers
# ---------------------------------------------------------------------------


def create_tables() -> None:
    """Run migration SQL to create ddproperty tables."""
    sql = MIGRATION_FILE.read_text()
    with psycopg.connect(DB_URL) as conn:
        conn.execute(sql)
        conn.commit()
    print(f"Tables created from {MIGRATION_FILE.name}")


def _get_existing_project(conn: psycopg.Connection, project_id: int) -> Optional[dict]:
    """Fetch existing ddproperty_projects row, or None."""
    cur = conn.execute(
        """
        SELECT id, sale_median_sqm, sale_count, rent_median, rent_count
        FROM ddproperty_projects p
        LEFT JOIN LATERAL (
            SELECT sale_median_sqm, sale_count, rent_median, rent_count
            FROM ddproperty_price_history
            WHERE project_id = p.id
            ORDER BY scraped_at DESC
            LIMIT 1
        ) latest ON true
        WHERE p.id = %s
        """,
        (project_id,),
    )
    row = cur.fetchone()
    if row is None:
        return None
    return {
        "id": row[0],
        "sale_median_sqm": row[1],
        "sale_count": row[2],
        "rent_median": row[3],
        "rent_count": row[4],
    }


def _has_recent_history(conn: psycopg.Connection, project_id: int) -> bool:
    """Check if a price_history record exists within the dedup window."""
    cur = conn.execute(
        """
        SELECT 1 FROM ddproperty_price_history
        WHERE project_id = %s
          AND scraped_at > now() - interval '%s seconds'
        LIMIT 1
        """,
        (project_id, DEDUP_WINDOW_SECONDS),
    )
    return cur.fetchone() is not None


def _compute_price_stats(
    sale_listings: list[ListingSummary],
    rent_listings: list[ListingSummary],
) -> dict:
    """Compute median/avg stats from listings."""
    sale_psm = [x.price_per_sqm for x in sale_listings if x.price_per_sqm]
    rent_prices = [x.price_thb for x in rent_listings if x.price_thb]

    return {
        "sale_median_sqm": int(statistics.median(sale_psm)) if sale_psm else None,
        "sale_avg_sqm": int(statistics.mean(sale_psm)) if sale_psm else None,
        "sale_count": len(sale_psm),
        "rent_median": int(statistics.median(rent_prices)) if rent_prices else None,
        "rent_avg": int(statistics.mean(rent_prices)) if rent_prices else None,
        "rent_count": len(rent_prices),
    }


def _price_changed(old: dict, new_stats: dict) -> bool:
    """Check if any tracked price field changed vs existing snapshot."""
    checks = [
        (old.get("sale_median_sqm"), new_stats.get("sale_median_sqm")),
        (old.get("rent_median"), new_stats.get("rent_median")),
        (old.get("sale_count"), new_stats.get("sale_count")),
        (old.get("rent_count"), new_stats.get("rent_count")),
    ]
    for old_val, new_val in checks:
        if old_val is not None and new_val is not None and old_val != new_val:
            return True
    return False


def upsert_project(
    conn: psycopg.Connection,
    scraped: ScrapedProject,
    stats: ScrapeStats,
) -> None:
    """Upsert project + listings into ddproperty tables, track price history."""
    proj = scraped.project
    existing = _get_existing_project(conn, proj.project_id)
    price_stats = _compute_price_stats(scraped.sale_listings, scraped.rent_listings)

    raw_json_str = (
        json.dumps(scraped.raw_project_json, ensure_ascii=False)
        if scraped.raw_project_json
        else None
    )

    if existing is None:
        # INSERT new project
        conn.execute(
            """
            INSERT INTO ddproperty_projects (
                id, name, completion_year, total_units,
                starting_price, max_price, developer_name,
                property_type_code, tenure_code, postcode,
                adm_level1, adm_level2, raw_json,
                first_seen_at, last_scraped_at
            ) VALUES (
                %s, %s, %s, %s,
                %s, %s, %s,
                %s, %s, %s,
                %s, %s, %s,
                now(), now()
            )
            """,
            (
                proj.project_id,
                proj.name,
                proj.completion_year,
                proj.total_units,
                proj.starting_price,
                _extract_field(scraped.raw_project_json, "max_price"),
                _extract_field(scraped.raw_project_json, "developer_name"),
                _extract_field(scraped.raw_project_json, "property_type_code"),
                _extract_field(scraped.raw_project_json, "tenure_code"),
                _extract_field(scraped.raw_project_json, "postcode"),
                _extract_field(scraped.raw_project_json, "adm_level1"),
                _extract_field(scraped.raw_project_json, "adm_level2"),
                raw_json_str,
            ),
        )
        stats.new_projects += 1

        # Insert 'new' history entry
        conn.execute(
            """
            INSERT INTO ddproperty_price_history (
                project_id, sale_median_sqm, sale_avg_sqm, sale_count,
                rent_median, rent_avg, rent_count,
                change_type, scraped_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, 'new', now())
            """,
            (
                proj.project_id,
                price_stats["sale_median_sqm"],
                price_stats["sale_avg_sqm"],
                price_stats["sale_count"],
                price_stats["rent_median"],
                price_stats["rent_avg"],
                price_stats["rent_count"],
            ),
        )
    else:
        # UPDATE existing project
        conn.execute(
            """
            UPDATE ddproperty_projects SET
                name = COALESCE(%s, name),
                completion_year = COALESCE(%s, completion_year),
                total_units = COALESCE(%s, total_units),
                starting_price = COALESCE(%s, starting_price),
                max_price = COALESCE(%s, max_price),
                developer_name = COALESCE(%s, developer_name),
                property_type_code = COALESCE(%s, property_type_code),
                tenure_code = COALESCE(%s, tenure_code),
                postcode = COALESCE(%s, postcode),
                adm_level1 = COALESCE(%s, adm_level1),
                adm_level2 = COALESCE(%s, adm_level2),
                raw_json = COALESCE(%s::jsonb, raw_json),
                last_scraped_at = now()
            WHERE id = %s
            """,
            (
                proj.name,
                proj.completion_year,
                proj.total_units,
                proj.starting_price,
                _extract_field(scraped.raw_project_json, "max_price"),
                _extract_field(scraped.raw_project_json, "developer_name"),
                _extract_field(scraped.raw_project_json, "property_type_code"),
                _extract_field(scraped.raw_project_json, "tenure_code"),
                _extract_field(scraped.raw_project_json, "postcode"),
                _extract_field(scraped.raw_project_json, "adm_level1"),
                _extract_field(scraped.raw_project_json, "adm_level2"),
                raw_json_str,
                proj.project_id,
            ),
        )
        stats.updated_projects += 1

        # Track price changes (with 1-hour dedup window)
        if _price_changed(existing, price_stats) and not _has_recent_history(
            conn, proj.project_id
        ):
            conn.execute(
                """
                INSERT INTO ddproperty_price_history (
                    project_id, sale_median_sqm, sale_avg_sqm, sale_count,
                    rent_median, rent_avg, rent_count,
                    change_type, scraped_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, 'price_change', now())
                """,
                (
                    proj.project_id,
                    price_stats["sale_median_sqm"],
                    price_stats["sale_avg_sqm"],
                    price_stats["sale_count"],
                    price_stats["rent_median"],
                    price_stats["rent_avg"],
                    price_stats["rent_count"],
                ),
            )
            stats.price_changed += 1

    # Upsert listings
    listing_count = 0
    for listing_type, listings, raws in [
        ("sale", scraped.sale_listings, scraped.sale_raw),
        ("rent", scraped.rent_listings, scraped.rent_raw),
    ]:
        raw_lookup = {r.get("listingData", {}).get("id"): r for r in raws}
        for listing in listings:
            raw_item = raw_lookup.get(listing.listing_id)
            raw_str = (
                json.dumps(raw_item, ensure_ascii=False) if raw_item else None
            )

            ld = raw_item.get("listingData", {}) if raw_item else {}

            conn.execute(
                """
                INSERT INTO ddproperty_listings (
                    id, project_id, listing_type, price_thb, sqm, price_per_sqm,
                    bedrooms, bathrooms, url, status_code, is_verified,
                    full_address, raw_json,
                    first_seen_at, last_scraped_at, is_active
                ) VALUES (
                    %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s,
                    now(), now(), true
                )
                ON CONFLICT (id) DO UPDATE SET
                    price_thb = EXCLUDED.price_thb,
                    sqm = EXCLUDED.sqm,
                    price_per_sqm = EXCLUDED.price_per_sqm,
                    bedrooms = EXCLUDED.bedrooms,
                    bathrooms = EXCLUDED.bathrooms,
                    url = EXCLUDED.url,
                    status_code = EXCLUDED.status_code,
                    is_verified = EXCLUDED.is_verified,
                    full_address = EXCLUDED.full_address,
                    raw_json = COALESCE(EXCLUDED.raw_json, ddproperty_listings.raw_json),
                    last_scraped_at = now(),
                    is_active = true
                """,
                (
                    listing.listing_id,
                    proj.project_id,
                    listing_type,
                    listing.price_thb,
                    listing.sqm,
                    listing.price_per_sqm,
                    listing.bedrooms,
                    listing.bathrooms,
                    listing.url,
                    ld.get("statusCode"),
                    ld.get("isVerified"),
                    ld.get("fullAddress"),
                    raw_str,
                ),
            )
            listing_count += 1

    stats.total_listings += listing_count


def _extract_field(raw_json: Optional[dict], field: str) -> Optional[str | int]:
    """Safely extract a field from the raw project JSON."""
    if raw_json is None:
        return None
    value = raw_json.get(field)
    if value is None or value == "":
        return None
    return value


# ---------------------------------------------------------------------------
# Seed list acquisition
# ---------------------------------------------------------------------------


def _seed_from_db() -> list[SeedProject]:
    """Gather project names from project_registry + NPA tables."""
    seeds: list[SeedProject] = []
    seen_lower: set[str] = set()

    def _add(
        name: str,
        source: str,
        ddproperty_id: Optional[int] = None,
    ) -> None:
        clean = name.strip()
        if not clean or clean.lower() in seen_lower:
            return
        seen_lower.add(clean.lower())
        seeds.append(
            SeedProject(name=clean, source=source, existing_ddproperty_id=ddproperty_id)
        )

    with psycopg.connect(DB_URL) as conn:
        # 1. project_registry — highest quality names, may have ddproperty_id
        cur = conn.execute(
            "SELECT name_canonical, name_th, name_en, ddproperty_id FROM project_registry"
        )
        for row in cur.fetchall():
            name_canonical, name_th, name_en, dd_id = row
            dd_id_int = int(dd_id) if dd_id else None
            _add(name_canonical, "project_registry", dd_id_int)
            if name_th:
                _add(name_th, "project_registry", dd_id_int)
            if name_en:
                _add(name_en, "project_registry", dd_id_int)

        # 2. BAM — project_th, project_en
        cur = conn.execute(
            "SELECT DISTINCT project_th FROM bam_properties "
            "WHERE project_th IS NOT NULL AND project_th != ''"
        )
        for (name,) in cur.fetchall():
            _add(name, "bam")
        cur = conn.execute(
            "SELECT DISTINCT project_en FROM bam_properties "
            "WHERE project_en IS NOT NULL AND project_en != ''"
        )
        for (name,) in cur.fetchall():
            _add(name, "bam")

        # 3. JAM — project_th, project_en
        cur = conn.execute(
            "SELECT DISTINCT project_th FROM jam_properties "
            "WHERE project_th IS NOT NULL AND project_th != ''"
        )
        for (name,) in cur.fetchall():
            _add(name, "jam")
        cur = conn.execute(
            "SELECT DISTINCT project_en FROM jam_properties "
            "WHERE project_en IS NOT NULL AND project_en != ''"
        )
        for (name,) in cur.fetchall():
            _add(name, "jam")

        # 4. SAM — project_name
        cur = conn.execute(
            "SELECT DISTINCT project_name FROM sam_properties "
            "WHERE project_name IS NOT NULL AND project_name != ''"
        )
        for (name,) in cur.fetchall():
            _add(name, "sam")

        # 5. KBank — building_th, village_th
        cur = conn.execute(
            "SELECT DISTINCT building_th FROM kbank_properties "
            "WHERE building_th IS NOT NULL AND building_th != ''"
        )
        for (name,) in cur.fetchall():
            _add(name, "kbank")
        cur = conn.execute(
            "SELECT DISTINCT village_th FROM kbank_properties "
            "WHERE village_th IS NOT NULL AND village_th != ''"
        )
        for (name,) in cur.fetchall():
            _add(name, "kbank")

        # 6. KTB — short coll_desc
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
# Smart search: multi-variant project lookup
# ---------------------------------------------------------------------------


async def smart_lookup(
    name: str,
    client: httpx.AsyncClient,
) -> Optional[tuple[ProjectInfo, dict]]:
    """Try multiple name variants via lookup_project, return best match.

    Returns (ProjectInfo, raw_json_dict) or None.
    """
    variants = _generate_name_variants(name)
    best_project: Optional[ProjectInfo] = None
    best_raw: Optional[dict] = None
    best_score = 0.0

    for variant in variants:
        try:
            resp = await client.get(
                f"{BASE_URL}/api/consumer/project",
                params={"locale": "en", "region": "th", "size": 5, "name": variant},
            )
            if resp.status_code != 200:
                continue

            data = resp.json()
            projects = data.get("data", [])
            if not projects:
                continue

            # Single result = trust the platform
            if len(projects) == 1:
                p = projects[0]
                best_project = _parse_project_info(p)
                best_raw = p
                best_score = 1.0
                break

            for p in projects[:5]:
                p_name = p.get("name", "")
                score = max(_name_similarity(v, p_name) for v in variants)
                if score > best_score:
                    best_score = score
                    best_project = _parse_project_info(p)
                    best_raw = p

            if best_score >= 0.5:
                break

        except Exception:
            continue

        await asyncio.sleep(0.3)

    if best_project is None or best_score < 0.15:
        return None

    return best_project, best_raw


def _parse_project_info(p: dict) -> ProjectInfo:
    """Parse a raw project dict from the API into ProjectInfo."""
    starting = p.get("starting_price", {}) or {}
    return ProjectInfo(
        project_id=p.get("property_id"),
        name=p.get("name", ""),
        completion_year=p.get("completion_year"),
        total_units=p.get("total_units"),
        starting_price=starting.get("value") if isinstance(starting, dict) else None,
    )


# ---------------------------------------------------------------------------
# Enhanced fetch_listings that also returns raw JSON
# ---------------------------------------------------------------------------


async def _fetch_listings_with_raw(
    freetext: str,
    listing_type: str,
    build_id: str,
    client: httpx.AsyncClient,
    max_pages: int = 5,
) -> tuple[list[ListingSummary], int, list[dict]]:
    """Fetch listings and also return raw listing dicts for DB storage.

    Returns (listings, result_count, raw_items).
    """
    slug = "condo-for-sale" if listing_type == "sale" else "condo-for-rent"
    url = f"{BASE_URL}/_next/data/{build_id}/en/{slug}.json"

    all_listings: list[ListingSummary] = []
    all_raw: list[dict] = []
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
            all_raw.append(item)

        total_pages = pagination.get("totalPages", 1) or 1
        if p >= total_pages:
            break
        await asyncio.sleep(REQUEST_DELAY)

    return all_listings, total_count, all_raw


# ---------------------------------------------------------------------------
# Main scraper loop
# ---------------------------------------------------------------------------


async def _process_single_project(
    seed: SeedProject,
    client: httpx.AsyncClient,
    build_id: str,
    stats: ScrapeStats,
    stats_lock: asyncio.Lock,
    semaphore: asyncio.Semaphore,
    cookie_acquired_at_ref: list[float],
    skip_camoufox: bool,
) -> None:
    """Process a single project: lookup + parallel sale/rent fetch + DB upsert.

    Runs under the semaphore to limit concurrency to TARGETED_CONCURRENCY.
    """
    async with semaphore:
        async with stats_lock:
            stats.total_projects += 1

        # Check if cookies need refresh (25min TTL)
        cookie_age = time.monotonic() - cookie_acquired_at_ref[0]
        if cookie_age > COOKIE_TTL_SECONDS:
            print(f"  Cookie expired ({cookie_age:.0f}s), refreshing...")
            try:
                fresh = await _acquire_cookies(skip_camoufox=False)
                cookie_acquired_at_ref[0] = time.monotonic()
                async with stats_lock:
                    stats.cookie_refreshes += 1
                client.cookies.clear()
                for k, v in fresh.items():
                    client.cookies.set(k, v)
            except Exception as e:
                print(f"  Cookie refresh failed: {e}")

        try:
            # Step 1: Look up project
            match = await smart_lookup(seed.name, client)

            if match is None:
                return

            project_info, raw_project = match

            # Step 2: Fetch sale + rent listings IN PARALLEL
            sale_task = _fetch_listings_with_raw(
                freetext=seed.name,
                listing_type="sale",
                build_id=build_id,
                client=client,
            )
            rent_task = _fetch_listings_with_raw(
                freetext=seed.name,
                listing_type="rent",
                build_id=build_id,
                client=client,
            )
            (sale_listings, sale_count, sale_raw), (
                rent_listings,
                rent_count,
                rent_raw,
            ) = await asyncio.gather(sale_task, rent_task)

            scraped = ScrapedProject(
                project=project_info,
                raw_project_json=raw_project,
                sale_listings=sale_listings,
                rent_listings=rent_listings,
                sale_count=sale_count,
                rent_count=rent_count,
                sale_raw=sale_raw,
                rent_raw=rent_raw,
            )

            # Step 3: Upsert to DB (sync, but fast)
            with psycopg.connect(DB_URL) as conn:
                upsert_project(conn, scraped, stats)
                conn.commit()

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 403:
                print(f"  403 on [{seed.name}] — refreshing cookies...")
                try:
                    fresh = await _acquire_cookies(skip_camoufox=False)
                    cookie_acquired_at_ref[0] = time.monotonic()
                    async with stats_lock:
                        stats.cookie_refreshes += 1
                    client.cookies.clear()
                    for k, v in fresh.items():
                        client.cookies.set(k, v)
                except Exception as re_err:
                    print(f"  Cookie refresh failed: {re_err}")
                async with stats_lock:
                    stats.failed_count += 1
            else:
                async with stats_lock:
                    stats.failed_count += 1
                print(f"  HTTP {e.response.status_code} [{seed.name}]: {e}")
        except Exception as e:
            async with stats_lock:
                stats.failed_count += 1
            print(f"  ERROR [{seed.name}]: {e}")


async def run_scraper(
    seeds: list[SeedProject],
    limit: Optional[int] = None,
    refresh_build_id: bool = False,
    skip_camoufox: bool = False,
) -> ScrapeStats:
    """Run the targeted scraper on a seed list. Returns stats.

    Processes up to TARGETED_CONCURRENCY projects in parallel.
    Each project runs: lookup + parallel sale/rent fetch + DB upsert.
    """
    stats = ScrapeStats()
    stats_lock = asyncio.Lock()
    work = seeds[:limit] if limit else seeds

    print(f"\nDDProperty targeted scraper — {len(work)} projects to process")
    print(f"  Concurrency: {TARGETED_CONCURRENCY} projects in parallel")
    print("=" * 60)

    # Start scrape log
    log_id: Optional[int] = None
    seed_source = work[0].source if work else "unknown"
    with psycopg.connect(DB_URL) as conn:
        cur = conn.execute(
            "INSERT INTO ddproperty_scrape_logs (started_at, seed_source) "
            "VALUES (now(), %s) RETURNING id",
            (seed_source,),
        )
        log_id = cur.fetchone()[0]
        conn.commit()

    started_at = datetime.now()

    # Acquire cookies
    print("[1] Acquiring cookies...")
    cookies = await _acquire_cookies(skip_camoufox=skip_camoufox)
    cookie_acquired_at_ref = [time.monotonic()]  # mutable ref for workers

    # Optionally refresh BUILD_ID
    build_id = BUILD_ID
    if refresh_build_id:
        print("[2] Refreshing BUILD_ID...")
        build_id = await fetch_build_id(cookies)
        print(f"    BUILD_ID: {build_id}")
    else:
        print(f"[2] Using BUILD_ID: {build_id}")

    semaphore = asyncio.Semaphore(TARGETED_CONCURRENCY)

    async with httpx.AsyncClient(
        timeout=30.0,
        follow_redirects=True,
        headers=HEADERS,
        cookies=cookies,
    ) as client:

        # Process projects in batches to allow progress reporting
        batch_size = TARGETED_CONCURRENCY * 3
        for batch_start in range(0, len(work), batch_size):
            batch = work[batch_start : batch_start + batch_size]

            tasks = [
                _process_single_project(
                    seed=seed,
                    client=client,
                    build_id=build_id,
                    stats=stats,
                    stats_lock=stats_lock,
                    semaphore=semaphore,
                    cookie_acquired_at_ref=cookie_acquired_at_ref,
                    skip_camoufox=skip_camoufox,
                )
                for seed in batch
            ]
            await asyncio.gather(*tasks, return_exceptions=True)

            # Progress report after each batch
            i = min(batch_start + batch_size, len(work))
            elapsed = (datetime.now() - started_at).total_seconds()
            rate = i / elapsed if elapsed > 0 else 0
            print(
                f"  [{i}/{len(work)}] "
                f"new={stats.new_projects} upd={stats.updated_projects} "
                f"price_chg={stats.price_changed} fail={stats.failed_count} "
                f"listings={stats.total_listings} "
                f"({rate:.1f} proj/s, {stats.cookie_refreshes} cookie refreshes)"
            )

    # Finalize scrape log
    error_msg: Optional[str] = None
    if stats.failed_count > 0:
        error_msg = f"{stats.failed_count} projects failed"

    with psycopg.connect(DB_URL) as conn:
        conn.execute(
            """
            UPDATE ddproperty_scrape_logs SET
                finished_at = now(),
                total_projects = %s,
                total_listings = %s,
                new_projects = %s,
                updated_projects = %s,
                price_changed = %s,
                failed_count = %s,
                error = %s,
                cookie_refreshes = %s
            WHERE id = %s
            """,
            (
                stats.total_projects,
                stats.total_listings,
                stats.new_projects,
                stats.updated_projects,
                stats.price_changed,
                stats.failed_count,
                error_msg,
                stats.cookie_refreshes,
                log_id,
            ),
        )
        conn.commit()

    elapsed = (datetime.now() - started_at).total_seconds()
    print(f"\n{'=' * 60}")
    print(f"  Done in {elapsed:.1f}s")
    print(f"  Projects processed: {stats.total_projects}")
    print(f"  Listings stored:    {stats.total_listings}")
    print(f"  New projects:       {stats.new_projects}")
    print(f"  Updated projects:   {stats.updated_projects}")
    print(f"  Price changes:      {stats.price_changed}")
    print(f"  Failed:             {stats.failed_count}")
    print(f"  Cookie refreshes:   {stats.cookie_refreshes}")
    print(f"{'=' * 60}\n")

    return stats


# ---------------------------------------------------------------------------
# Discover mode — bulk crawl via JSON API, no Camoufox
# ---------------------------------------------------------------------------

# Headers for discover mode — browser UA + JSON accept, no cookies needed
DISCOVER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9",
}

DISCOVER_DELAY = 0.1  # seconds stagger between workers acquiring semaphore


class CookieRefresh403(Exception):
    """Raised when a 403 is encountered and cookies need refreshing."""


class DiscoveredListing(BaseModel):
    """A single listing from the bulk discover crawl."""

    listing_id: int
    project_id: Optional[int] = None
    project_name: Optional[str] = None
    listing_type: str  # "sale" or "rent"
    price_thb: Optional[int] = None
    sqm: Optional[float] = None
    price_per_sqm: Optional[int] = None
    bedrooms: int = 0
    bathrooms: int = 0
    url: str = ""
    full_address: Optional[str] = None
    status_code: Optional[str] = None
    is_verified: Optional[bool] = None


class DiscoverStats(BaseModel):
    """Stats for a discover run."""

    pages_fetched: int = 0
    total_listings: int = 0
    sale_listings: int = 0
    rent_listings: int = 0
    projects_created: int = 0
    listings_upserted: int = 0
    errors: int = 0
    cookie_refreshes: int = 0


def _extract_project_id_from_url(url: str) -> Optional[int]:
    """Extract project_id from DDProperty listing URL hash.

    URL format: /property/project/sansa-ari-rama-6-...-11916991#3743
    The #3743 is the project_id.
    """
    match = re.search(r"#(\d+)$", url)
    if match:
        return int(match.group(1))
    return None


def _extract_listing_id_from_url(url: str) -> Optional[int]:
    """Extract listing_id from DDProperty listing URL slug.

    URL format: /property/project/sansa-ari-rama-6-...-11916991#3743
    The 11916991 at the end of the slug (before #) is the listing_id.
    """
    match = re.search(r"-(\d+)(?:#\d+)?$", url)
    if match:
        return int(match.group(1))
    return None


def _extract_project_name_from_url(url: str) -> Optional[str]:
    """Extract a rough project name from the URL slug.

    URL format: /property/project/sansa-ari-rama-6-...-for-sale-11916991#3743
    We take the slug part between /project/ and the trailing -ID#ID,
    strip listing type suffixes, then replace hyphens with spaces.
    """
    match = re.search(r"/property/[^/]+/([^?]+?)(?:-\d+)?(?:#\d+)?$", url)
    if match:
        slug = match.group(1)
        # Remove trailing listing ID pattern
        slug = re.sub(r"-\d+$", "", slug)
        # Remove listing-type suffixes
        slug = re.sub(r"-for-(?:sale|rent)$", "", slug)
        return slug.replace("-", " ").strip().title()
    return None


async def _fetch_discover_build_id(client: httpx.AsyncClient) -> Optional[str]:
    """Fetch BUILD_ID from DDProperty homepage HTML without cookies.

    Cloudflare may 403 the first 1-2 requests; we retry up to 3 times
    with a short sleep between attempts.
    """
    url = f"{BASE_URL}/en"
    headers = {**DISCOVER_HEADERS, "Accept": "text/html"}

    for attempt in range(3):
        try:
            resp = await client.get(url, headers=headers)
            if resp.status_code == 403:
                await asyncio.sleep(1.0)
                continue
            if resp.status_code != 200:
                return None
            match = re.search(r'"buildId"\s*:\s*"([^"]+)"', resp.text)
            if match:
                return match.group(1)
        except Exception:
            await asyncio.sleep(1.0)
            continue

    return None


async def _fetch_discover_page(
    client: httpx.AsyncClient,
    build_id: str,
    listing_type: str,
    page: int,
    is_first_request: bool = False,
    raise_on_403: bool = False,
) -> Optional[dict]:
    """Fetch a single page of discover listings.

    Cloudflare may 403 the first few requests per session.
    We retry up to 3 times on 403 with short sleeps.
    On 404 the BUILD_ID is stale — return None immediately.

    When raise_on_403=True (concurrent mode), raises CookieRefresh403
    after exhausting retries so the coordinator can refresh cookies.
    """
    slug = "condo-for-sale" if listing_type == "sale" else "condo-for-rent"
    url = f"{BASE_URL}/_next/data/{build_id}/en/{slug}.json"

    max_attempts = 3 if is_first_request else 2
    for attempt in range(max_attempts):
        try:
            resp = await client.get(url, params={"page": page})
            if resp.status_code == 404:
                return None  # BUILD_ID is stale
            if resp.status_code == 403:
                await asyncio.sleep(1.0)
                continue  # Cloudflare warming — retry
            if resp.status_code != 200:
                return None
            return resp.json()
        except Exception:
            await asyncio.sleep(1.0)
            continue

    if raise_on_403:
        raise CookieRefresh403(f"403 on page {page} after {max_attempts} retries")
    return None


def _parse_discovered_listing(
    item: dict,
    listing_type: str,
) -> Optional[DiscoveredListing]:
    """Parse a single raw listing item into DiscoveredListing."""
    ld = item.get("listingData", {})
    if not ld:
        return None

    listing_id = ld.get("id")
    if listing_id is None:
        return None

    price_info = ld.get("price", {}) or {}
    price_val = price_info.get("value")
    sqm = ld.get("floorArea")
    psm = round(price_val / sqm) if price_val and sqm else None

    url = ld.get("url", "")
    project_id = _extract_project_id_from_url(url)
    project_name = _extract_project_name_from_url(url)

    return DiscoveredListing(
        listing_id=listing_id,
        project_id=project_id,
        project_name=project_name,
        listing_type=listing_type,
        price_thb=price_val,
        sqm=sqm,
        price_per_sqm=psm,
        bedrooms=ld.get("bedrooms", 0),
        bathrooms=ld.get("bathrooms", 0),
        url=url,
        full_address=ld.get("fullAddress"),
        status_code=ld.get("statusCode"),
        is_verified=ld.get("isVerified"),
    )


def _upsert_discovered_batch(
    conn: psycopg.Connection,
    listings: list[DiscoveredListing],
) -> tuple[int, int]:
    """Upsert a batch of discovered listings into the DB.

    Returns (projects_touched, listings_upserted) counts.
    Thread-safe: does not mutate shared stats — caller applies counts.
    """
    projects_touched = 0
    listings_upserted = 0

    # First, ensure minimal project rows exist for all project_ids
    project_ids_seen: set[int] = set()
    for listing in listings:
        if listing.project_id and listing.project_id not in project_ids_seen:
            project_ids_seen.add(listing.project_id)
            conn.execute(
                """
                INSERT INTO ddproperty_projects (id, name, first_seen_at, last_scraped_at)
                VALUES (%s, %s, now(), now())
                ON CONFLICT (id) DO UPDATE SET
                    name = COALESCE(NULLIF(ddproperty_projects.name, ''), EXCLUDED.name),
                    last_scraped_at = now()
                """,
                (listing.project_id, listing.project_name),
            )
            projects_touched += 1

    # Upsert listings
    for listing in listings:
        conn.execute(
            """
            INSERT INTO ddproperty_listings (
                id, project_id, listing_type, price_thb, sqm, price_per_sqm,
                bedrooms, bathrooms, url, status_code, is_verified,
                full_address,
                first_seen_at, last_scraped_at, is_active
            ) VALUES (
                %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s,
                %s,
                now(), now(), true
            )
            ON CONFLICT (id) DO UPDATE SET
                project_id = COALESCE(EXCLUDED.project_id, ddproperty_listings.project_id),
                listing_type = EXCLUDED.listing_type,
                price_thb = EXCLUDED.price_thb,
                sqm = EXCLUDED.sqm,
                price_per_sqm = EXCLUDED.price_per_sqm,
                bedrooms = EXCLUDED.bedrooms,
                bathrooms = EXCLUDED.bathrooms,
                url = EXCLUDED.url,
                status_code = EXCLUDED.status_code,
                is_verified = EXCLUDED.is_verified,
                full_address = EXCLUDED.full_address,
                last_scraped_at = now(),
                is_active = true
            """,
            (
                listing.listing_id,
                listing.project_id,
                listing.listing_type,
                listing.price_thb,
                listing.sqm,
                listing.price_per_sqm,
                listing.bedrooms,
                listing.bathrooms,
                listing.url,
                listing.status_code,
                listing.is_verified,
                listing.full_address,
            ),
        )
        listings_upserted += 1

    return projects_touched, listings_upserted


def _save_progress(listing_type: str, last_page: int, build_id: str) -> None:
    """Save discover progress to disk for resume on crash."""
    payload = {
        "listing_type": listing_type,
        "last_page": last_page,
        "build_id": build_id,
        "saved_at": datetime.now().isoformat(),
    }
    PROGRESS_FILE.write_text(json.dumps(payload, ensure_ascii=False))


def _load_progress() -> Optional[dict]:
    """Load saved discover progress, or None if no valid state."""
    if not PROGRESS_FILE.exists():
        return None
    try:
        payload = json.loads(PROGRESS_FILE.read_text())
        # Validate required keys
        if all(k in payload for k in ("listing_type", "last_page", "build_id")):
            return payload
    except (json.JSONDecodeError, ValueError):
        pass
    return None


def _clear_progress() -> None:
    """Remove progress file after successful completion."""
    if PROGRESS_FILE.exists():
        PROGRESS_FILE.unlink()


async def discover_listings(
    include_rent: bool = False,
    max_pages: Optional[int] = None,
    build_id_override: Optional[str] = None,
    skip_camoufox: bool = False,
    start_page: Optional[int] = None,
    force: bool = False,
) -> DiscoverStats:
    """Bulk-discover ALL condo listings via the JSON API.

    Uses Camoufox to acquire Cloudflare cookies, then httpx for all
    subsequent paginated requests. Cookies are cached for reuse.

    Concurrency: fetches up to DISCOVER_CONCURRENCY pages in parallel.
    On 403, all workers pause while cookies are refreshed via Camoufox.

    Resume: progress is saved per-page to PROGRESS_FILE. On restart,
    automatically resumes from the last committed page unless --force.

    Args:
        include_rent: Also crawl rent listings (default: sale only).
        max_pages: Cap max pages per listing type (None = all pages).
        build_id_override: Use this BUILD_ID instead of the module constant.
        skip_camoufox: Use cached cookies only (error if none exist).
        start_page: Manually set starting page number.
        force: Ignore saved progress, start from page 1.
    """
    stats = DiscoverStats()
    started_at = datetime.now()

    # --- Resume logic ---
    resume_page: Optional[int] = None
    resume_listing_type: Optional[str] = None
    resume_build_id: Optional[str] = None

    if start_page is not None:
        resume_page = start_page
        print(f"[Resume] Starting from page {start_page} (--start-page)")
    elif not force:
        saved = _load_progress()
        if saved:
            resume_page = saved["last_page"] + 1
            resume_listing_type = saved["listing_type"]
            resume_build_id = saved["build_id"]
            print(
                f"[Resume] Found interrupted run: {resume_listing_type} "
                f"page {saved['last_page']} at {saved['saved_at']}"
            )
            print(f"  Resuming from page {resume_page}")
            print(f"  Use --force to ignore and start fresh")

    if force:
        _clear_progress()

    # Acquire cookies (same flow as targeted mode)
    print("[1] Acquiring Cloudflare cookies...")
    cookies = await _acquire_cookies(skip_camoufox=skip_camoufox)
    print(f"    Got {len(cookies)} cookies")

    # Shared state for coordinated cookie refresh across concurrent tasks
    cookie_refresh_lock = asyncio.Lock()
    cookie_refreshing = asyncio.Event()
    cookie_refreshing.set()  # Not refreshing initially — workers proceed

    async def _refresh_cookies_once(client: httpx.AsyncClient) -> None:
        """Refresh cookies, ensuring only one refresh happens at a time."""
        async with cookie_refresh_lock:
            # Double-check: another worker may have already refreshed
            saved_cookies = _load_cookies()
            if saved_cookies is not None:
                # Cookies were just refreshed by another worker
                client.cookies.clear()
                for k, v in saved_cookies.items():
                    client.cookies.set(k, v)
                return

            cookie_refreshing.clear()  # Signal workers to pause
            try:
                print("  [Cookie] 403 detected — refreshing via Camoufox...")
                fresh = await _acquire_cookies(skip_camoufox=False)
                stats.cookie_refreshes += 1
                client.cookies.clear()
                for k, v in fresh.items():
                    client.cookies.set(k, v)
                print(f"  [Cookie] Refreshed — {len(fresh)} cookies")
            finally:
                cookie_refreshing.set()  # Unblock workers

    semaphore = asyncio.Semaphore(DISCOVER_CONCURRENCY)

    # Track the highest successfully committed page per listing_type
    committed_pages: dict[str, int] = {}
    committed_lock = asyncio.Lock()

    # Track if we hit a fatal error (404 = stale BUILD_ID)
    stop_event = asyncio.Event()

    def _sync_upsert_batch(
        page_batch: list[DiscoveredListing],
    ) -> tuple[int, int]:
        """Sync DB upsert — runs inside asyncio.to_thread to avoid blocking.

        Returns (projects_touched, listings_upserted).
        """
        with psycopg.connect(DB_URL) as conn:
            result = _upsert_discovered_batch(conn, page_batch)
            conn.commit()
        return result

    async def _fetch_and_upsert_page(
        client: httpx.AsyncClient,
        build_id: str,
        lt: str,
        page_num: int,
        effective_max: int,
    ) -> tuple[int, bool]:
        """Fetch one page and upsert to DB. Returns (listing_count, is_empty).

        Coordinates with cookie_refreshing event to pause on 403.
        DB writes run in a thread to avoid blocking the event loop.
        """
        if stop_event.is_set():
            return 0, True

        async with semaphore:
            # Small stagger between concurrent workers
            await asyncio.sleep(DISCOVER_DELAY)

            # Wait if cookies are being refreshed
            await cookie_refreshing.wait()

            try:
                page_data_resp = await _fetch_discover_page(
                    client, build_id, lt, page=page_num, raise_on_403=True,
                )
            except CookieRefresh403:
                # Trigger cookie refresh (only one worker does the actual refresh)
                await _refresh_cookies_once(client)
                # Retry the page after refresh
                try:
                    page_data_resp = await _fetch_discover_page(
                        client, build_id, lt, page=page_num, raise_on_403=True,
                    )
                except CookieRefresh403:
                    stats.errors += 1
                    print(f"  ERROR: Still 403 on page {page_num} after cookie refresh")
                    return 0, False

            if page_data_resp is None:
                stats.errors += 1
                print(f"  ERROR on page {page_num} — BUILD_ID may be stale")
                stop_event.set()
                return 0, True

            pd = page_data_resp.get("pageProps", {}).get("pageData", {})
            dn = pd.get("data", {})
            raw_items = dn.get("listingsData", [])

            page_batch: list[DiscoveredListing] = []
            for item in raw_items:
                parsed = _parse_discovered_listing(item, lt)
                if parsed:
                    page_batch.append(parsed)

            count = len(page_batch)
            projects_touched = 0
            if page_batch:
                # Run sync DB write in a thread to avoid blocking event loop
                projects_touched, _ = await asyncio.to_thread(
                    _sync_upsert_batch, page_batch,
                )

            # Update stats + committed page tracker (single async context = safe)
            async with committed_lock:
                stats.projects_created += projects_touched
                stats.listings_upserted += count
                stats.pages_fetched += 1
                if lt == "sale":
                    stats.sale_listings += count
                else:
                    stats.rent_listings += count
                stats.total_listings += count

                prev = committed_pages.get(lt, 0)
                if page_num > prev:
                    committed_pages[lt] = page_num
                    _save_progress(lt, page_num, build_id)

            # Per-page progress
            print(
                f"  [DB] page {page_num}/{effective_max}: "
                f"{count} listings saved (total: {stats.total_listings:,})"
            )

            return count, len(raw_items) == 0

    async with httpx.AsyncClient(
        timeout=30.0,
        follow_redirects=True,
        headers=DISCOVER_HEADERS,
        cookies=cookies,
    ) as client:

        # Resolve BUILD_ID
        build_id = resume_build_id or build_id_override or BUILD_ID
        if not build_id_override and not resume_build_id:
            print("[2] Resolving BUILD_ID from homepage...")
            fetched_id = await _fetch_discover_build_id(client)
            if fetched_id:
                build_id = fetched_id
                print(f"    BUILD_ID: {build_id}")
            else:
                print(f"    Could not fetch BUILD_ID, using hardcoded: {build_id}")
        else:
            print(f"[2] Using BUILD_ID: {build_id}")

        listing_types = ["sale"]
        if include_rent:
            listing_types.append("rent")

        is_first_request = True

        for lt in listing_types:
            # If resuming a specific listing_type, skip ones already completed
            if resume_listing_type and resume_listing_type == "rent" and lt == "sale":
                print(f"\n[Discover] Skipping condo-for-{lt} (already completed)")
                continue

            print(f"\n[Discover] Crawling condo-for-{lt}...")
            stop_event.clear()

            # Determine starting page for this listing_type
            lt_start_page = 1
            if resume_page and (resume_listing_type is None or resume_listing_type == lt):
                lt_start_page = resume_page
                resume_page = None  # Only apply once

            # Fetch page 1 (or first page) to get total_pages
            if lt_start_page == 1:
                data = await _fetch_discover_page(
                    client, build_id, lt, page=1, is_first_request=is_first_request,
                )
                is_first_request = False

                if data is None:
                    print(f"  ERROR: Could not fetch page 1 for {lt}. BUILD_ID may be stale.")
                    print(f"  Try: --build-id <ID> or check BUILD_ID manually.")
                    stats.errors += 1
                    continue

                page_data = data.get("pageProps", {}).get("pageData", {})
                data_node = page_data.get("data", {})
                pagination = data_node.get("paginationData", {})
                total_pages = pagination.get("totalPages", 1) or 1
                result_count = page_data.get("resultCount", 0)

                effective_max = min(total_pages, max_pages) if max_pages else total_pages
                print(f"  Total: {result_count:,} listings across {total_pages:,} pages")
                if max_pages and max_pages < total_pages:
                    print(f"  Capped to {effective_max} pages (--limit)")

                # Parse & upsert page 1
                page_batch: list[DiscoveredListing] = []
                listings_raw = data_node.get("listingsData", [])
                for item in listings_raw:
                    parsed = _parse_discovered_listing(item, lt)
                    if parsed:
                        page_batch.append(parsed)

                page1_count = len(page_batch)
                if page_batch:
                    p_touched, _ = await asyncio.to_thread(
                        _sync_upsert_batch, page_batch,
                    )
                    stats.projects_created += p_touched
                    stats.listings_upserted += page1_count
                    if lt == "sale":
                        stats.sale_listings += page1_count
                    else:
                        stats.rent_listings += page1_count
                    stats.total_listings += page1_count
                stats.pages_fetched += 1
                _save_progress(lt, 1, build_id)
                print(
                    f"  [DB] page 1/{effective_max}: "
                    f"{page1_count} listings saved (total: {stats.total_listings:,})"
                )

                pages_start = 2
            else:
                # Resuming: probe page 1 just to get total_pages
                probe = await _fetch_discover_page(
                    client, build_id, lt, page=1, is_first_request=is_first_request,
                )
                is_first_request = False
                if probe is None:
                    print(f"  ERROR: Could not probe page 1 for {lt}.")
                    stats.errors += 1
                    continue
                page_data = probe.get("pageProps", {}).get("pageData", {})
                data_node = page_data.get("data", {})
                pagination = data_node.get("paginationData", {})
                total_pages = pagination.get("totalPages", 1) or 1
                result_count = page_data.get("resultCount", 0)

                # When resuming, --limit means "fetch N more pages from resume point"
                if max_pages:
                    effective_max = min(total_pages, lt_start_page + max_pages - 1)
                else:
                    effective_max = total_pages
                print(
                    f"  Total: {result_count:,} listings across {total_pages:,} pages "
                    f"(resuming from page {lt_start_page}, "
                    f"up to page {effective_max})"
                )
                pages_start = lt_start_page

            # --- Concurrent page fetches ---
            remaining_pages = list(range(pages_start, effective_max + 1))
            if not remaining_pages:
                continue

            print(
                f"  Fetching pages {pages_start}-{effective_max} "
                f"({len(remaining_pages)} pages, {DISCOVER_CONCURRENCY} workers)"
            )

            # Fire all tasks at once — semaphore controls actual concurrency.
            # Stagger is handled inside _fetch_and_upsert_page via DISCOVER_DELAY.
            # Large batches (50 pages) keep the pipeline full without gather barriers.
            batch_size = 50
            for batch_start in range(0, len(remaining_pages), batch_size):
                if stop_event.is_set():
                    break

                batch = remaining_pages[batch_start : batch_start + batch_size]
                tasks = [
                    _fetch_and_upsert_page(
                        client, build_id, lt, page_num, effective_max,
                    )
                    for page_num in batch
                ]

                results = await asyncio.gather(*tasks, return_exceptions=True)

                # Check for fatal errors
                for r in results:
                    if isinstance(r, Exception):
                        stats.errors += 1
                        print(f"  ERROR in batch: {r}")

                # Batch summary
                current_page = batch[-1] if batch else pages_start
                elapsed = (datetime.now() - started_at).total_seconds()
                rate = stats.pages_fetched / elapsed if elapsed > 0 else 0
                print(
                    f"  --- [{lt}] batch done ~{current_page}/{effective_max} | "
                    f"{stats.total_listings:,} listings | "
                    f"{rate:.1f} pages/s | "
                    f"errors={stats.errors} ---"
                )

    # Successful completion — clear progress file
    _clear_progress()

    elapsed = (datetime.now() - started_at).total_seconds()
    print(f"\n{'=' * 60}")
    print(f"  Discover complete in {elapsed:.1f}s")
    print(f"  Pages fetched:     {stats.pages_fetched}")
    print(f"  Total listings:    {stats.total_listings:,}")
    print(f"  Sale listings:     {stats.sale_listings:,}")
    print(f"  Rent listings:     {stats.rent_listings:,}")
    print(f"  Projects touched:  {stats.projects_created}")
    print(f"  Listings upserted: {stats.listings_upserted:,}")
    print(f"  Errors:            {stats.errors}")
    print(f"  Cookie refreshes:  {stats.cookie_refreshes}")
    print(f"{'=' * 60}\n")

    return stats


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="DDProperty scraper — targeted (Camoufox) or discover (bulk JSON API)",
        epilog=(
            "Examples:\n"
            "  # Targeted mode (Camoufox, 3 concurrent projects)\n"
            "  python ddproperty_scraper.py --seed-db\n"
            "  python ddproperty_scraper.py --seed-db --limit 50\n"
            "  python ddproperty_scraper.py --seed-file projects.txt\n"
            '  python ddproperty_scraper.py --names "triple y residence" "15 sukhumvit"\n'
            "  python ddproperty_scraper.py --create-tables\n"
            "  python ddproperty_scraper.py --seed-db --refresh-build-id\n"
            '  python ddproperty_scraper.py --names "triple y" --skip-camoufox\n'
            "\n"
            "  # Discover mode (5 concurrent pages, auto-resume)\n"
            "  python ddproperty_scraper.py --discover\n"
            "  python ddproperty_scraper.py --discover --discover-rent\n"
            "  python ddproperty_scraper.py --discover --limit 10\n"
            "  python ddproperty_scraper.py --discover --build-id ABC123\n"
            "  python ddproperty_scraper.py --discover --start-page 500\n"
            "  python ddproperty_scraper.py --discover --force\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Discover mode flags
    parser.add_argument(
        "--discover",
        action="store_true",
        help="Bulk-discover ALL condo listings via JSON API (5 concurrent pages)",
    )
    parser.add_argument(
        "--discover-rent",
        action="store_true",
        help="Also crawl rent listings in discover mode (default: sale only)",
    )
    parser.add_argument(
        "--build-id",
        type=str,
        help="Override the Next.js BUILD_ID (for discover mode)",
    )
    parser.add_argument(
        "--start-page",
        type=int,
        help="Resume discover mode from this page number",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Ignore saved progress, start discover from page 1",
    )

    # Targeted mode flags
    parser.add_argument(
        "--seed-db",
        action="store_true",
        help="Seed project names from project_registry + NPA tables (3 concurrent)",
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
        help="Limit to first N projects (targeted) or N pages (discover)",
    )
    parser.add_argument(
        "--create-tables",
        action="store_true",
        help="Run migration SQL to create ddproperty tables",
    )
    parser.add_argument(
        "--refresh-build-id",
        action="store_true",
        help="Fetch fresh BUILD_ID from DDProperty homepage (targeted mode)",
    )
    parser.add_argument(
        "--skip-camoufox",
        action="store_true",
        help="Skip Camoufox launch, use pre-saved cookies from /tmp/ddproperty_cookies.json",
    )
    args = parser.parse_args()

    if args.create_tables:
        create_tables()
        if not (args.seed_db or args.seed_file or args.names or args.discover):
            return

    # --- Discover mode ---
    if args.discover:
        asyncio.run(
            discover_listings(
                include_rent=args.discover_rent,
                max_pages=args.limit,
                build_id_override=args.build_id,
                skip_camoufox=args.skip_camoufox,
                start_page=args.start_page,
                force=args.force,
            )
        )
        return

    # --- Targeted mode ---
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

    asyncio.run(
        run_scraper(
            seeds,
            limit=args.limit,
            refresh_build_id=args.refresh_build_id,
            skip_camoufox=args.skip_camoufox,
        )
    )


if __name__ == "__main__":
    main()

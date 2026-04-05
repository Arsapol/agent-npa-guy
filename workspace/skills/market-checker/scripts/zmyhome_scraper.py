#!/usr/bin/env python3
"""
zmyhome_scraper.py -- Bulk scraper for ZMyHome project data.

Two modes:
  1. **Seed mode** (--seed-db / --seed-file / --names): Searches ZMyHome
     autocomplete for known project names and scrapes project pages,
     listings, and government appraisals.
  2. **Discover mode** (--discover): Crawls ZMyHome's paginated browse pages
     (/buy/condo, /rent/condo) to collect ALL individual listings without
     needing seed names. Fast bulk collection (~3.5 min for 13k buy listings).

Usage:
    # --- Discover mode (primary) ---
    python zmyhome_scraper.py --discover
    python zmyhome_scraper.py --discover --discover-rent
    python zmyhome_scraper.py --discover --province 1
    python zmyhome_scraper.py --discover --province 1 --discover-rent --limit 50

    # --- Seed mode ---
    python zmyhome_scraper.py --seed-db
    python zmyhome_scraper.py --seed-db --limit 50
    python zmyhome_scraper.py --seed-file projects.txt
    python zmyhome_scraper.py --names "circle condominium" "lumpini suite"

    # Create tables first
    python zmyhome_scraper.py --create-tables

    # Also scrape sold/rented listing tabs
    python zmyhome_scraper.py --seed-db --include-sold
"""

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

import httpx
import psycopg
from pydantic import BaseModel

from market_checker import _generate_name_variants, _name_similarity
from zmyhome_lookup import (
    BASE,
    ListingCard,
    ProjectSummary,
    fetch_listings,
    fetch_project_page,
    make_client,
    parse_listing_cards,
    search_project,
)

DB_URL = "postgresql://arsapolm@localhost:5432/npa_kb"
MIGRATION_FILE = Path(__file__).parent / "migration_004_zmyhome.sql"
DEDUP_WINDOW_SECONDS = 3600  # 1 hour


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
    appraisals_count: int = 0
    not_found_count: int = 0
    failed_count: int = 0


class SeedProject(BaseModel):
    """A project name to search for, with optional metadata."""

    name: str
    source: str = "cli"
    existing_zmyhome_id: Optional[str] = None


class DiscoverStats(BaseModel):
    """Stats container for a discover crawl run."""

    pages_crawled: int = 0
    listings_found: int = 0
    new_count: int = 0
    updated_count: int = 0
    empty_pages: int = 0
    failed_pages: int = 0


# ---------------------------------------------------------------------------
# DB helpers
# ---------------------------------------------------------------------------


def create_tables() -> None:
    """Run migration SQL to create zmyhome tables."""
    sql = MIGRATION_FILE.read_text()
    with psycopg.connect(DB_URL) as conn:
        conn.execute(sql)
        conn.commit()
    print(f"Tables created from {MIGRATION_FILE.name}")


def _get_existing_project(conn: psycopg.Connection, project_id: str) -> Optional[dict]:
    """Fetch existing zmyhome_projects row as dict, or None."""
    cur = conn.execute(
        """
        SELECT id, listing_summary
        FROM zmyhome_projects WHERE id = %s
        """,
        (project_id,),
    )
    row = cur.fetchone()
    if row is None:
        return None
    return {"id": row[0], "listing_summary": row[1]}


def _has_recent_history(conn: psycopg.Connection, project_id: str) -> bool:
    """Check if a price_history record exists within the dedup window."""
    cur = conn.execute(
        """
        SELECT 1 FROM zmyhome_price_history
        WHERE project_id = %s
          AND scraped_at > now() - interval '%s seconds'
        LIMIT 1
        """,
        (project_id, DEDUP_WINDOW_SECONDS),
    )
    return cur.fetchone() is not None


def _compute_listing_medians(
    sale_listings: list[ListingCard],
    rent_listings: list[ListingCard],
) -> dict:
    """Compute median sale/sqm and rent prices from listing cards."""
    sale_psms = [c.price_psm for c in sale_listings if c.price_psm]
    sale_median = int(sorted(sale_psms)[len(sale_psms) // 2]) if sale_psms else None

    rent_prices = [c.price_thb for c in rent_listings if c.price_thb]
    rent_median = int(sorted(rent_prices)[len(rent_prices) // 2]) if rent_prices else None

    return {
        "sale_median_sqm": sale_median,
        "sale_count": len(sale_listings),
        "rent_median": rent_median,
        "rent_count": len(rent_listings),
    }


def _listing_price_changed(
    old_summary: Optional[dict],
    new_medians: dict,
) -> bool:
    """Detect price changes by comparing listing medians against old summary.

    old_summary is the JSONB listing_summary from the DB row. We compare
    median sale/rent counts and values to decide if prices shifted.
    """
    if old_summary is None:
        return False

    # Simple heuristic: if sale_median_sqm or rent_median differs from what
    # we can infer from the old listing_summary, call it a change.
    # Since listing_summary stores per-type {count, price_min, price_max},
    # we compare counts as a proxy.
    old_buy = old_summary.get("ขาย") or old_summary.get("buy") or {}
    old_rent = old_summary.get("เช่า") or old_summary.get("rent") or {}

    old_buy_count = old_buy.get("count", 0)
    old_rent_count = old_rent.get("count", 0)

    new_sale_count = new_medians.get("sale_count", 0)
    new_rent_count = new_medians.get("rent_count", 0)

    return old_buy_count != new_sale_count or old_rent_count != new_rent_count


def upsert_project(
    conn: psycopg.Connection,
    summary: ProjectSummary,
    lat: Optional[float],
    lng: Optional[float],
    sale_listings: list[ListingCard],
    rent_listings: list[ListingCard],
    stats: ScrapeStats,
) -> None:
    """Upsert project, listings, appraisals, and price history."""
    project_id = summary.project_id
    existing = _get_existing_project(conn, project_id)
    medians = _compute_listing_medians(sale_listings, rent_listings)
    listing_summary_json = json.dumps(summary.listing_summary, ensure_ascii=False)
    raw_json = json.dumps(summary.model_dump(), ensure_ascii=False, default=str)

    if existing is None:
        # INSERT new project
        conn.execute(
            """
            INSERT INTO zmyhome_projects (
                id, project_code, name, developer, year_built,
                total_units, num_floors, common_area_fee,
                lat, lng, listing_summary, raw_json,
                first_seen_at, last_scraped_at
            ) VALUES (
                %s, %s, %s, %s, %s,
                %s, %s, %s,
                %s, %s, %s, %s,
                now(), now()
            )
            """,
            (
                project_id,
                summary.project_code,
                summary.name,
                summary.developer,
                summary.year_built,
                summary.total_units,
                summary.num_floors,
                summary.common_area_fee,
                lat,
                lng,
                listing_summary_json,
                raw_json,
            ),
        )
        stats.new_count += 1

        # Insert 'new' price history (skip dedup for new projects)
        conn.execute(
            """
            INSERT INTO zmyhome_price_history (
                project_id, sale_median_sqm, sale_count,
                rent_median, rent_count, change_type, scraped_at
            ) VALUES (%s, %s, %s, %s, %s, 'new', now())
            """,
            (
                project_id,
                medians["sale_median_sqm"],
                medians["sale_count"],
                medians["rent_median"],
                medians["rent_count"],
            ),
        )
    else:
        # UPDATE existing project
        conn.execute(
            """
            UPDATE zmyhome_projects SET
                project_code    = COALESCE(%s, project_code),
                name            = COALESCE(%s, name),
                developer       = COALESCE(%s, developer),
                year_built      = COALESCE(%s, year_built),
                total_units     = COALESCE(%s, total_units),
                num_floors      = COALESCE(%s, num_floors),
                common_area_fee = COALESCE(%s, common_area_fee),
                lat             = COALESCE(%s, lat),
                lng             = COALESCE(%s, lng),
                listing_summary = %s,
                raw_json        = %s,
                last_scraped_at = now()
            WHERE id = %s
            """,
            (
                summary.project_code,
                summary.name,
                summary.developer,
                summary.year_built,
                summary.total_units,
                summary.num_floors,
                summary.common_area_fee,
                lat,
                lng,
                listing_summary_json,
                raw_json,
                project_id,
            ),
        )
        stats.updated_count += 1

        # Track price changes (1-hour dedup)
        old_summary = existing.get("listing_summary") or {}
        if _listing_price_changed(old_summary, medians) and not _has_recent_history(
            conn, project_id
        ):
            conn.execute(
                """
                INSERT INTO zmyhome_price_history (
                    project_id, sale_median_sqm, sale_count,
                    rent_median, rent_count, change_type, scraped_at
                ) VALUES (%s, %s, %s, %s, %s, 'price_change', now())
                """,
                (
                    project_id,
                    medians["sale_median_sqm"],
                    medians["sale_count"],
                    medians["rent_median"],
                    medians["rent_count"],
                ),
            )
            stats.price_changed += 1

    # --- Upsert listings ---
    all_listings: list[tuple[str, ListingCard]] = []
    for card in sale_listings:
        all_listings.append(("buy", card))
    for card in rent_listings:
        all_listings.append(("rent", card))

    for listing_type, card in all_listings:
        if not card.property_id:
            continue
        conn.execute(
            """
            INSERT INTO zmyhome_listings (
                property_id, project_id, listing_type,
                price_thb, price_psm, size_sqm,
                bedrooms, bathrooms, floor, direction, broker_ok,
                first_seen_at, last_scraped_at, is_active
            ) VALUES (
                %s, %s, %s,
                %s, %s, %s,
                %s, %s, %s, %s, %s,
                now(), now(), true
            )
            ON CONFLICT (property_id) DO UPDATE SET
                listing_type    = EXCLUDED.listing_type,
                price_thb       = EXCLUDED.price_thb,
                price_psm       = EXCLUDED.price_psm,
                size_sqm        = EXCLUDED.size_sqm,
                bedrooms        = EXCLUDED.bedrooms,
                bathrooms       = EXCLUDED.bathrooms,
                floor           = EXCLUDED.floor,
                direction       = EXCLUDED.direction,
                broker_ok       = EXCLUDED.broker_ok,
                last_scraped_at = now(),
                is_active       = true
            """,
            (
                card.property_id,
                project_id,
                listing_type,
                card.price_thb,
                card.price_psm,
                card.size_sqm,
                card.bedrooms,
                card.bathrooms,
                card.floor,
                card.direction,
                card.broker_ok,
            ),
        )

    # --- Upsert appraisals ---
    for appraisal in summary.gov_appraisal:
        building = appraisal.get("building", "")
        floor_val = appraisal.get("floor", "")
        price_psm = appraisal.get("price_psm", "")
        unit_type = appraisal.get("unit_type", "")

        conn.execute(
            """
            INSERT INTO zmyhome_appraisals (
                project_id, building, floor, price_psm, unit_type, scraped_at
            ) VALUES (%s, %s, %s, %s, %s, now())
            ON CONFLICT (project_id, building, floor, unit_type) DO UPDATE SET
                price_psm  = EXCLUDED.price_psm,
                scraped_at = now()
            """,
            (project_id, building, floor_val, price_psm, unit_type),
        )
        stats.appraisals_count += 1


# ---------------------------------------------------------------------------
# Discover mode — crawl browse pages
# ---------------------------------------------------------------------------


def _build_browse_url(
    listing_type: str,
    page: int,
    province_id: Optional[int] = None,
) -> str:
    """Build a ZMyHome browse URL for the given listing type and page.

    listing_type: 'buy' or 'rent'
    """
    per_page = 35
    if province_id is not None:
        return (
            f"{BASE}/{listing_type}/condo/province/{province_id}"
            f"?page={page}&per-page={per_page}"
        )
    return f"{BASE}/{listing_type}/condo?page={page}&per-page={per_page}"


def _upsert_discovered_listing(
    conn: psycopg.Connection,
    card: ListingCard,
    listing_type: str,
    discover_source: str,
) -> bool:
    """Upsert a single discovered listing. Returns True if INSERT (new)."""
    if not card.property_id:
        return False

    cur = conn.execute(
        """
        INSERT INTO zmyhome_listings (
            property_id, project_id, listing_type,
            price_thb, price_psm, size_sqm,
            bedrooms, bathrooms, floor, direction, broker_ok,
            discover_source,
            first_seen_at, last_scraped_at, is_active
        ) VALUES (
            %s, NULL, %s,
            %s, %s, %s,
            %s, %s, %s, %s, %s,
            %s,
            now(), now(), true
        )
        ON CONFLICT (property_id) DO UPDATE SET
            listing_type    = EXCLUDED.listing_type,
            price_thb       = EXCLUDED.price_thb,
            price_psm       = EXCLUDED.price_psm,
            size_sqm        = EXCLUDED.size_sqm,
            bedrooms        = EXCLUDED.bedrooms,
            bathrooms       = EXCLUDED.bathrooms,
            floor           = EXCLUDED.floor,
            direction       = EXCLUDED.direction,
            broker_ok       = EXCLUDED.broker_ok,
            discover_source = COALESCE(zmyhome_listings.discover_source, EXCLUDED.discover_source),
            last_scraped_at = now(),
            is_active       = true
        RETURNING (xmax = 0) AS is_insert
        """,
        (
            card.property_id,
            listing_type,
            card.price_thb,
            card.price_psm,
            card.size_sqm,
            card.bedrooms,
            card.bathrooms,
            card.floor,
            card.direction,
            card.broker_ok,
            discover_source,
        ),
    )
    row = cur.fetchone()
    return bool(row and row[0])


def _crawl_listing_type(
    client: httpx.Client,
    conn: psycopg.Connection,
    listing_type: str,
    province_id: Optional[int],
    max_pages: Optional[int],
    stats: DiscoverStats,
) -> None:
    """Crawl all pages for a single listing type (buy or rent)."""
    discover_source = (
        f"province:{province_id}" if province_id is not None else "browse"
    )
    page = 1
    consecutive_empty = 0
    max_consecutive_empty = 3

    label = listing_type.upper()
    if province_id is not None:
        label += f" province={province_id}"

    print(f"\n  Crawling {label} ...")

    while True:
        if max_pages is not None and page > max_pages:
            break

        url = _build_browse_url(listing_type, page, province_id)

        try:
            resp = client.get(url)
            resp.raise_for_status()
        except Exception as e:
            stats.failed_pages += 1
            print(f"    page {page} FAILED: {e}")
            if stats.failed_pages > 10:
                print("    Too many failures, stopping.")
                break
            time.sleep(1)
            page += 1
            continue

        cards = parse_listing_cards(resp.text)
        stats.pages_crawled += 1

        if not cards:
            consecutive_empty += 1
            stats.empty_pages += 1
            if consecutive_empty >= max_consecutive_empty:
                break
            page += 1
            time.sleep(0.5)
            continue

        consecutive_empty = 0
        stats.listings_found += len(cards)

        for card in cards:
            is_new = _upsert_discovered_listing(
                conn, card, listing_type, discover_source
            )
            if is_new:
                stats.new_count += 1
            else:
                stats.updated_count += 1

        conn.commit()

        # Progress every 10 pages
        if page % 10 == 0:
            print(
                f"    [{label}] page {page}: "
                f"{stats.listings_found} listings "
                f"(new={stats.new_count}, updated={stats.updated_count})"
            )

        page += 1
        time.sleep(0.5)


def discover_listings(
    include_rent: bool = False,
    province_id: Optional[int] = None,
    max_pages: Optional[int] = None,
) -> DiscoverStats:
    """Crawl ZMyHome browse pages to discover all condo listings.

    Args:
        include_rent: Also crawl /rent/condo pages (default: buy only).
        province_id: Limit to a single province ID (e.g. 1 = Bangkok).
        max_pages: Max pages to crawl per listing type (None = all).

    Returns:
        DiscoverStats with totals.
    """
    stats = DiscoverStats()
    started_at = datetime.now()

    source_label = "discover"
    if province_id is not None:
        source_label = f"discover:province:{province_id}"
    if include_rent:
        source_label += "+rent"

    print(f"\nZMyHome discover mode")
    print(f"  Province: {province_id or 'ALL'}")
    print(f"  Listing types: buy{' + rent' if include_rent else ''}")
    print(f"  Max pages/type: {max_pages or 'unlimited'}")
    print(f"{'=' * 60}")

    # Start scrape log
    log_id: Optional[int] = None
    with psycopg.connect(DB_URL) as conn:
        cur = conn.execute(
            "INSERT INTO zmyhome_scrape_logs (started_at, seed_source) "
            "VALUES (now(), %s) RETURNING id",
            (source_label,),
        )
        log_id = cur.fetchone()[0]
        conn.commit()

    client = make_client()
    try:
        # Initialize session
        client.get(BASE)

        with psycopg.connect(DB_URL) as conn:
            # Always crawl buy
            _crawl_listing_type(
                client, conn, "buy", province_id, max_pages, stats
            )

            if include_rent:
                _crawl_listing_type(
                    client, conn, "rent", province_id, max_pages, stats
                )

    except KeyboardInterrupt:
        print("\n  Interrupted by user, saving progress...")
    except Exception as e:
        print(f"\n  FATAL: {e}")
    finally:
        client.close()

    # Finalize scrape log
    elapsed = (datetime.now() - started_at).total_seconds()
    error_msg: Optional[str] = None
    if stats.failed_pages > 0:
        error_msg = f"{stats.failed_pages} pages failed"

    with psycopg.connect(DB_URL) as conn:
        conn.execute(
            """
            UPDATE zmyhome_scrape_logs SET
                finished_at    = now(),
                total_searched = %s,
                total_found    = %s,
                new_count      = %s,
                updated_count  = %s,
                failed_count   = %s,
                error          = %s
            WHERE id = %s
            """,
            (
                stats.pages_crawled,
                stats.listings_found,
                stats.new_count,
                stats.updated_count,
                stats.failed_pages,
                error_msg,
                log_id,
            ),
        )
        conn.commit()

    print(f"\n{'=' * 60}")
    print(f"  Done in {elapsed:.1f}s")
    print(f"  Pages crawled: {stats.pages_crawled}")
    print(f"  Listings found: {stats.listings_found}")
    print(f"  New:            {stats.new_count}")
    print(f"  Updated:        {stats.updated_count}")
    print(f"  Empty pages:    {stats.empty_pages}")
    print(f"  Failed pages:   {stats.failed_pages}")
    print(f"{'=' * 60}\n")

    return stats


# ---------------------------------------------------------------------------
# Seed list acquisition
# ---------------------------------------------------------------------------


def _seed_from_db() -> list[SeedProject]:
    """Gather project names from project_registry + NPA tables."""
    seeds: list[SeedProject] = []
    seen_lower: set[str] = set()

    def _add(
        name: str, source: str, zmyhome_id: Optional[str] = None
    ) -> None:
        clean = name.strip()
        if not clean or clean.lower() in seen_lower:
            return
        seen_lower.add(clean.lower())
        seeds.append(
            SeedProject(name=clean, source=source, existing_zmyhome_id=zmyhome_id)
        )

    with psycopg.connect(DB_URL) as conn:
        # 1. project_registry -- highest quality names, may have zmyhome_id
        cur = conn.execute(
            "SELECT name_canonical, name_th, name_en, zmyhome_id FROM project_registry"
        )
        for row in cur.fetchall():
            name_canonical, name_th, name_en, zmyhome_id = row
            _add(name_canonical, "project_registry", zmyhome_id)
            if name_th:
                _add(name_th, "project_registry", zmyhome_id)
            if name_en:
                _add(name_en, "project_registry", zmyhome_id)

        # 2. BAM -- project_th, project_en
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

        # 3. JAM -- project_th, project_en
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

        # 4. SAM -- project_name
        cur = conn.execute(
            "SELECT DISTINCT project_name FROM sam_properties "
            "WHERE project_name IS NOT NULL AND project_name != ''"
        )
        for (name,) in cur.fetchall():
            _add(name, "sam")

        # 5. KBank -- building_th, village_th
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

        # 6. KTB -- coll_desc (short entries likely to be project names)
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
# Smart search: multi-variant with similarity scoring
# ---------------------------------------------------------------------------


def smart_search(
    client: object,
    name: str,
) -> Optional[tuple[str, str, Optional[float], Optional[float]]]:
    """Try multiple name variants on ZMyHome autocomplete.

    Returns (project_id, matched_name, lat, lng) or None.
    """
    variants = _generate_name_variants(name)
    best_result: Optional[dict] = None
    best_score = 0.0

    for variant in variants:
        try:
            results = search_project(client, variant)
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
            r_name = r.get("label", "")
            score = max(_name_similarity(v, r_name) for v in variants)
            if score > best_score:
                best_score = score
                best_result = r

        if best_score >= 0.5:
            break

        time.sleep(0.3)

    if best_result is None or best_score < 0.15:
        return None

    lat_raw = best_result.get("lat")
    lng_raw = best_result.get("lng")
    lat = float(lat_raw) if lat_raw else None
    lng = float(lng_raw) if lng_raw else None

    return best_result["id"], best_result.get("label", ""), lat, lng


# ---------------------------------------------------------------------------
# Main scraper loop
# ---------------------------------------------------------------------------


def run_scraper(
    seeds: list[SeedProject],
    limit: Optional[int] = None,
    include_sold: bool = False,
) -> ScrapeStats:
    """Run the bulk scraper on a seed list. Returns stats."""
    stats = ScrapeStats()
    work = seeds[:limit] if limit else seeds

    print(f"\nZMyHome bulk scraper -- {len(work)} projects to process")
    if include_sold:
        print("  (including sold/rented tabs)")
    print(f"{'=' * 60}")

    # Start scrape log
    log_id: Optional[int] = None
    seed_source = work[0].source if work else "unknown"
    with psycopg.connect(DB_URL) as conn:
        cur = conn.execute(
            "INSERT INTO zmyhome_scrape_logs (started_at, seed_source) "
            "VALUES (now(), %s) RETURNING id",
            (seed_source,),
        )
        log_id = cur.fetchone()[0]
        conn.commit()

    started_at = datetime.now()

    # Shared httpx client for the entire run
    client = make_client()
    try:
        # Initialize session
        client.get("https://zmyhome.com")

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
                    f"appraisals={stats.appraisals_count} "
                    f"not_found={stats.not_found_count} failed={stats.failed_count} "
                    f"({rate:.1f} proj/s)"
                )

            try:
                # Step 1: Resolve project ID via search
                project_id: Optional[str] = seed.existing_zmyhome_id
                lat: Optional[float] = None
                lng: Optional[float] = None

                if project_id is None:
                    match = smart_search(client, seed.name)
                    if match is None:
                        stats.not_found_count += 1
                        continue
                    project_id, _matched_name, lat, lng = match
                    time.sleep(0.5)

                # Step 2: Fetch project page (metadata + appraisals)
                summary = fetch_project_page(client, project_id)

                # Step 3: Fetch listings
                sale_listings = fetch_listings(client, project_id, "buy")
                time.sleep(0.3)
                rent_listings = fetch_listings(client, project_id, "rent")

                if include_sold:
                    time.sleep(0.3)
                    sold_listings = fetch_listings(client, project_id, "sold")
                    time.sleep(0.3)
                    rented_listings = fetch_listings(client, project_id, "rented")
                else:
                    sold_listings = []
                    rented_listings = []

                stats.total_found += 1

                # Step 4: Upsert to DB
                with psycopg.connect(DB_URL) as conn:
                    upsert_project(
                        conn,
                        summary,
                        lat,
                        lng,
                        sale_listings,
                        rent_listings,
                        stats,
                    )

                    # Upsert sold/rented listings separately
                    for listing_type, cards in [
                        ("sold", sold_listings),
                        ("rented", rented_listings),
                    ]:
                        for card in cards:
                            if not card.property_id:
                                continue
                            conn.execute(
                                """
                                INSERT INTO zmyhome_listings (
                                    property_id, project_id, listing_type,
                                    price_thb, price_psm, size_sqm,
                                    bedrooms, bathrooms, floor, direction, broker_ok,
                                    first_seen_at, last_scraped_at, is_active
                                ) VALUES (
                                    %s, %s, %s,
                                    %s, %s, %s,
                                    %s, %s, %s, %s, %s,
                                    now(), now(), false
                                )
                                ON CONFLICT (property_id) DO UPDATE SET
                                    listing_type    = EXCLUDED.listing_type,
                                    price_thb       = EXCLUDED.price_thb,
                                    price_psm       = EXCLUDED.price_psm,
                                    size_sqm        = EXCLUDED.size_sqm,
                                    bedrooms        = EXCLUDED.bedrooms,
                                    bathrooms       = EXCLUDED.bathrooms,
                                    floor           = EXCLUDED.floor,
                                    direction       = EXCLUDED.direction,
                                    broker_ok       = EXCLUDED.broker_ok,
                                    last_scraped_at = now(),
                                    is_active       = false
                                """,
                                (
                                    card.property_id,
                                    project_id,
                                    listing_type,
                                    card.price_thb,
                                    card.price_psm,
                                    card.size_sqm,
                                    card.bedrooms,
                                    card.bathrooms,
                                    card.floor,
                                    card.direction,
                                    card.broker_ok,
                                ),
                            )

                    conn.commit()

                time.sleep(0.5)

            except Exception as e:
                stats.failed_count += 1
                print(f"  ERROR [{seed.name}]: {e}")
                time.sleep(1)

    finally:
        client.close()

    # Finalize scrape log
    error_msg: Optional[str] = None
    if stats.failed_count > 0:
        error_msg = f"{stats.failed_count} projects failed"

    with psycopg.connect(DB_URL) as conn:
        conn.execute(
            """
            UPDATE zmyhome_scrape_logs SET
                finished_at      = now(),
                total_searched   = %s,
                total_found      = %s,
                new_count        = %s,
                updated_count    = %s,
                price_changed    = %s,
                appraisals_count = %s,
                not_found_count  = %s,
                failed_count     = %s,
                error            = %s
            WHERE id = %s
            """,
            (
                stats.total_searched,
                stats.total_found,
                stats.new_count,
                stats.updated_count,
                stats.price_changed,
                stats.appraisals_count,
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
    print(f"  Searched:    {stats.total_searched}")
    print(f"  Found:       {stats.total_found}")
    print(f"  New:         {stats.new_count}")
    print(f"  Updated:     {stats.updated_count}")
    print(f"  Price chg:   {stats.price_changed}")
    print(f"  Appraisals:  {stats.appraisals_count}")
    print(f"  Not found:   {stats.not_found_count}")
    print(f"  Failed:      {stats.failed_count}")
    print(f"{'=' * 60}\n")

    return stats


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="ZMyHome bulk scraper -- project data + govt appraisals",
        epilog=(
            "Examples:\n"
            "  # Discover mode (primary — crawl browse pages)\n"
            "  python zmyhome_scraper.py --discover\n"
            "  python zmyhome_scraper.py --discover --discover-rent\n"
            "  python zmyhome_scraper.py --discover --province 1\n"
            "  python zmyhome_scraper.py --discover --province 1 --limit 50\n"
            "\n"
            "  # Seed mode (search by project name)\n"
            "  python zmyhome_scraper.py --seed-db\n"
            "  python zmyhome_scraper.py --seed-db --limit 50\n"
            "  python zmyhome_scraper.py --seed-file projects.txt\n"
            '  python zmyhome_scraper.py --names "circle condominium" "lumpini suite"\n'
            "  python zmyhome_scraper.py --create-tables\n"
            "  python zmyhome_scraper.py --seed-db --include-sold\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Discover mode flags
    parser.add_argument(
        "--discover",
        action="store_true",
        help="Crawl ZMyHome browse pages to discover all condo listings",
    )
    parser.add_argument(
        "--discover-rent",
        action="store_true",
        help="Also crawl /rent/condo pages (default: buy only). Requires --discover",
    )
    parser.add_argument(
        "--province",
        type=int,
        help="Limit discover to a single province ID (e.g. 1=Bangkok). Requires --discover",
    )

    # Seed mode flags
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

    # Common flags
    parser.add_argument(
        "--limit",
        type=int,
        help="Limit to first N projects (seed mode) or N pages per type (discover mode)",
    )
    parser.add_argument(
        "--create-tables",
        action="store_true",
        help="Run migration SQL to create zmyhome tables",
    )
    parser.add_argument(
        "--include-sold",
        action="store_true",
        help="Also scrape sold/rented listing tabs (seed mode only)",
    )
    args = parser.parse_args()

    if args.create_tables:
        create_tables()
        if not (args.discover or args.seed_db or args.seed_file or args.names):
            return

    # Validate discover-only flags
    if args.discover_rent and not args.discover:
        print("Error: --discover-rent requires --discover")
        sys.exit(1)
    if args.province is not None and not args.discover:
        print("Error: --province requires --discover")
        sys.exit(1)

    # --- Discover mode ---
    if args.discover:
        discover_listings(
            include_rent=args.discover_rent,
            province_id=args.province,
            max_pages=args.limit,
        )
        return

    # --- Seed mode ---
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

    run_scraper(seeds, limit=args.limit, include_sold=args.include_sold)


if __name__ == "__main__":
    main()

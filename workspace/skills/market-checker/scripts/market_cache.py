"""
market_cache.py — PostgreSQL-backed caching layer for market_checker.py

Provides:
- Project registry (canonical identity + source IDs)
- Append-only price snapshot storage (builds history over time)
- Freshness checks per source
- NPA provider linkage
"""

import json
from datetime import datetime, timezone
from typing import Optional

import psycopg
from pydantic import BaseModel, Field

DB_URL = "postgresql://arsapolm@localhost:5432/npa_kb"

# ---------------------------------------------------------------------------
# Provider table/column mapping
# ---------------------------------------------------------------------------
_PROVIDER_MAP: dict[str, tuple[str, str]] = {
    "bam":   ("bam_properties",   "asset_no"),
    "jam":   ("jam_properties",   "asset_id"),
    "sam":   ("sam_properties",   "sam_id"),
    "ktb":   ("ktb_properties",   "coll_grp_id"),
    "kbank": ("kbank_properties", "property_id"),
    "led":   ("led_properties",   "id"),
}

# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class ProjectRegistryEntry(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    name_canonical: str
    name_th: Optional[str] = None
    name_en: Optional[str] = None
    aliases: list[str] = Field(default_factory=list)
    hipflat_uuid: Optional[str] = None
    zmyhome_id: Optional[str] = None
    propertyhub_id: Optional[str] = None
    ddproperty_id: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    year_built: Optional[int] = None
    total_units: Optional[int] = None
    developer: Optional[str] = None
    cam_fee_sqm: Optional[float] = None


class CachedPrice(BaseModel):
    model_config = {"from_attributes": True}

    project_id: int
    source: str
    matched_name: Optional[str] = None
    sale_price_sqm: Optional[int] = None
    sale_count: Optional[int] = None
    sold_price_sqm: Optional[int] = None
    last_sold_date: Optional[str] = None
    rent_median: Optional[int] = None
    rent_min: Optional[int] = None
    rent_max: Optional[int] = None
    rent_count: Optional[int] = None
    last_rental_date: Optional[str] = None
    yoy_change_pct: Optional[float] = None
    govt_appraisal_sqm: Optional[int] = None
    checked_at: Optional[datetime] = None
    ttl_days: int = 30
    is_fresh: bool = False


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _row_to_registry(row: tuple) -> ProjectRegistryEntry:
    """Map a DB row (all columns in SELECT order) to ProjectRegistryEntry."""
    (
        id_, name_canonical, name_th, name_en, aliases,
        hipflat_uuid, zmyhome_id, propertyhub_id, ddproperty_id,
        lat, lng, year_built, total_units, developer, cam_fee_sqm,
    ) = row
    return ProjectRegistryEntry(
        id=id_,
        name_canonical=name_canonical,
        name_th=name_th,
        name_en=name_en,
        aliases=aliases or [],
        hipflat_uuid=hipflat_uuid,
        zmyhome_id=zmyhome_id,
        propertyhub_id=propertyhub_id,
        ddproperty_id=ddproperty_id,
        lat=float(lat) if lat is not None else None,
        lng=float(lng) if lng is not None else None,
        year_built=year_built,
        total_units=total_units,
        developer=developer,
        cam_fee_sqm=float(cam_fee_sqm) if cam_fee_sqm is not None else None,
    )


_REGISTRY_COLS = """
    id, name_canonical, name_th, name_en, aliases,
    hipflat_uuid, zmyhome_id, propertyhub_id, ddproperty_id,
    lat, lng, year_built, total_units, developer, cam_fee_sqm
"""


def _row_to_cached_price(row: tuple) -> CachedPrice:
    """Map a DB row to CachedPrice, computing is_fresh."""
    (
        project_id, source, matched_name,
        sale_price_sqm, sale_count, sold_price_sqm, last_sold_date,
        rent_median, rent_min, rent_max, rent_count, last_rental_date,
        yoy_change_pct, govt_appraisal_sqm,
        checked_at, ttl_days,
    ) = row

    now = datetime.now(timezone.utc)
    is_fresh = False
    if checked_at is not None:
        # Ensure tz-aware comparison
        ca = checked_at if checked_at.tzinfo else checked_at.replace(tzinfo=timezone.utc)
        age_days = (now - ca).total_seconds() / 86400
        is_fresh = age_days < (ttl_days or 30)

    return CachedPrice(
        project_id=project_id,
        source=source,
        matched_name=matched_name,
        sale_price_sqm=sale_price_sqm,
        sale_count=sale_count,
        sold_price_sqm=sold_price_sqm,
        last_sold_date=str(last_sold_date) if last_sold_date else None,
        rent_median=rent_median,
        rent_min=rent_min,
        rent_max=rent_max,
        rent_count=rent_count,
        last_rental_date=str(last_rental_date) if last_rental_date else None,
        yoy_change_pct=float(yoy_change_pct) if yoy_change_pct is not None else None,
        govt_appraisal_sqm=govt_appraisal_sqm,
        checked_at=checked_at,
        ttl_days=ttl_days or 30,
        is_fresh=is_fresh,
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def find_registry(search_term: str) -> Optional[ProjectRegistryEntry]:
    """Find a project in registry by name_canonical, name_th, name_en, or aliases.

    Search order:
    1. Exact match on name_canonical (case-insensitive)
    2. Exact match on name_th or name_en
    3. Any alias contains search_term (array @> check)
    """
    with psycopg.connect(DB_URL) as conn:
        with conn.cursor() as cur:
            # 1. name_canonical ILIKE
            cur.execute(
                f"SELECT {_REGISTRY_COLS} FROM project_registry WHERE name_canonical ILIKE %s LIMIT 1",
                (search_term,),
            )
            row = cur.fetchone()
            if row:
                return _row_to_registry(row)

            # 2. name_th or name_en exact (ILIKE)
            cur.execute(
                f"SELECT {_REGISTRY_COLS} FROM project_registry "
                "WHERE name_th ILIKE %s OR name_en ILIKE %s LIMIT 1",
                (search_term, search_term),
            )
            row = cur.fetchone()
            if row:
                return _row_to_registry(row)

            # 3. Any alias contains search_term (array @> ARRAY[value])
            cur.execute(
                f"SELECT {_REGISTRY_COLS} FROM project_registry "
                "WHERE aliases @> ARRAY[%s]::TEXT[] LIMIT 1",
                (search_term.lower(),),
            )
            row = cur.fetchone()
            if row:
                return _row_to_registry(row)

    return None


def create_or_update_registry(
    name_canonical: str,
    name_th: Optional[str] = None,
    name_en: Optional[str] = None,
    aliases: Optional[list[str]] = None,
    hipflat_uuid: Optional[str] = None,
    zmyhome_id: Optional[str] = None,
    propertyhub_id: Optional[str] = None,
    ddproperty_id: Optional[str] = None,
    lat: Optional[float] = None,
    lng: Optional[float] = None,
    year_built: Optional[int] = None,
    total_units: Optional[int] = None,
    developer: Optional[str] = None,
    cam_fee_sqm: Optional[float] = None,
) -> ProjectRegistryEntry:
    """Create or update a project registry entry.

    If name_canonical already exists, UPDATE non-null fields (COALESCE preserves existing).
    Aliases are APPENDED (merged with existing) and deduplicated — never replaced.
    Source IDs are only updated if the new value is not None.

    Returns the created/updated entry.
    """
    new_aliases = [a.lower() for a in (aliases or [])]

    with psycopg.connect(DB_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                INSERT INTO project_registry (
                    name_canonical, name_th, name_en, aliases,
                    hipflat_uuid, zmyhome_id, propertyhub_id, ddproperty_id,
                    lat, lng, year_built, total_units, developer, cam_fee_sqm,
                    updated_at
                ) VALUES (
                    %s, %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s,
                    now()
                )
                ON CONFLICT (name_canonical) DO UPDATE SET
                    name_th           = COALESCE(%s, project_registry.name_th),
                    name_en           = COALESCE(%s, project_registry.name_en),
                    aliases           = (
                        SELECT ARRAY(
                            SELECT DISTINCT unnest(
                                project_registry.aliases || EXCLUDED.aliases
                            )
                        )
                    ),
                    hipflat_uuid      = COALESCE(%s, project_registry.hipflat_uuid),
                    zmyhome_id        = COALESCE(%s, project_registry.zmyhome_id),
                    propertyhub_id    = COALESCE(%s, project_registry.propertyhub_id),
                    ddproperty_id     = COALESCE(%s, project_registry.ddproperty_id),
                    lat               = COALESCE(%s, project_registry.lat),
                    lng               = COALESCE(%s, project_registry.lng),
                    year_built        = COALESCE(%s, project_registry.year_built),
                    total_units       = COALESCE(%s, project_registry.total_units),
                    developer         = COALESCE(%s, project_registry.developer),
                    cam_fee_sqm       = COALESCE(%s, project_registry.cam_fee_sqm),
                    updated_at        = now()
                RETURNING {_REGISTRY_COLS}
                """,
                (
                    # INSERT values
                    name_canonical, name_th, name_en, new_aliases,
                    hipflat_uuid, zmyhome_id, propertyhub_id, ddproperty_id,
                    lat, lng, year_built, total_units, developer, cam_fee_sqm,
                    # UPDATE COALESCE values
                    name_th, name_en,
                    hipflat_uuid, zmyhome_id, propertyhub_id, ddproperty_id,
                    lat, lng, year_built, total_units, developer, cam_fee_sqm,
                ),
            )
            row = cur.fetchone()
            conn.commit()
    return _row_to_registry(row)


def get_cached_prices(project_id: int) -> list[CachedPrice]:
    """Get latest cached price per source for a project.

    Returns one CachedPrice per source (latest checked_at per source).
    Sets is_fresh = True if checked_at + ttl_days > now().
    """
    with psycopg.connect(DB_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT DISTINCT ON (source)
                    project_id, source, matched_name,
                    sale_price_sqm, sale_count, sold_price_sqm, last_sold_date,
                    rent_median, rent_min, rent_max, rent_count, last_rental_date,
                    yoy_change_pct, govt_appraisal_sqm,
                    checked_at, ttl_days
                FROM market_price_cache
                WHERE project_id = %s
                ORDER BY source, checked_at DESC
                """,
                (project_id,),
            )
            rows = cur.fetchall()

    return [_row_to_cached_price(r) for r in rows]


def get_stale_sources(project_id: int) -> list[str]:
    """Return list of sources that are stale or missing for a project.

    A source is stale if:
    - No cache entry exists for this project+source
    - Latest entry has checked_at + ttl_days <= now()
    """
    all_sources = list(_PROVIDER_MAP.keys()) + ["hipflat", "ddproperty", "zmyhome", "propertyhub"]
    cached = get_cached_prices(project_id)
    fresh_sources = {c.source for c in cached if c.is_fresh}
    return [s for s in all_sources if s not in fresh_sources]


def insert_price_snapshot(
    project_id: int,
    source: str,
    matched_name: Optional[str] = None,
    sale_price_sqm: Optional[int] = None,
    sale_count: Optional[int] = None,
    sold_price_sqm: Optional[int] = None,
    last_sold_date: Optional[str] = None,
    rent_median: Optional[int] = None,
    rent_min: Optional[int] = None,
    rent_max: Optional[int] = None,
    rent_count: Optional[int] = None,
    last_rental_date: Optional[str] = None,
    yoy_change_pct: Optional[float] = None,
    govt_appraisal_sqm: Optional[int] = None,
    raw_data: Optional[dict] = None,
    ttl_days: int = 30,
) -> int:
    """Insert a new price snapshot. Returns the new row id.

    Always INSERT (never update) — this builds price history over time.
    """
    raw_json = json.dumps(raw_data, ensure_ascii=False) if raw_data is not None else None

    with psycopg.connect(DB_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO market_price_cache (
                    project_id, source, matched_name,
                    sale_price_sqm, sale_count, sold_price_sqm, last_sold_date,
                    rent_median, rent_min, rent_max, rent_count, last_rental_date,
                    yoy_change_pct, govt_appraisal_sqm,
                    raw_data, ttl_days, checked_at
                ) VALUES (
                    %s, %s, %s,
                    %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s,
                    %s, %s, now()
                )
                RETURNING id
                """,
                (
                    project_id, source, matched_name,
                    sale_price_sqm, sale_count, sold_price_sqm, last_sold_date,
                    rent_median, rent_min, rent_max, rent_count, last_rental_date,
                    yoy_change_pct, govt_appraisal_sqm,
                    raw_json, ttl_days,
                ),
            )
            row_id: int = cur.fetchone()[0]
            conn.commit()

    return row_id


def link_npa_property(
    provider: str,
    property_id: str,
    registry_id: int,
) -> None:
    """Set market_registry_id on an NPA provider table.

    provider: "bam" | "jam" | "sam" | "ktb" | "kbank" | "led"
    property_id: the business key (asset_no for BAM, asset_id for JAM, etc.)
    registry_id: project_registry.id
    """
    if provider not in _PROVIDER_MAP:
        raise ValueError(f"Unknown provider '{provider}'. Valid: {list(_PROVIDER_MAP)}")

    table, id_col = _PROVIDER_MAP[provider]
    # Table/column names are from a fixed internal map — not user input — safe to interpolate.
    sql = f"UPDATE {table} SET market_registry_id = %s WHERE {id_col} = %s"

    with psycopg.connect(DB_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (registry_id, property_id))
            conn.commit()


def get_unlinked_count() -> dict[str, int]:
    """Count NPA properties without market_registry_id per provider.

    Returns: {"bam": 1854, "jam": 11663, ...}
    """
    result: dict[str, int] = {}
    with psycopg.connect(DB_URL) as conn:
        with conn.cursor() as cur:
            for provider, (table, _) in _PROVIDER_MAP.items():
                try:
                    cur.execute(
                        f"SELECT COUNT(*) FROM {table} WHERE market_registry_id IS NULL"
                    )
                    count: int = cur.fetchone()[0]
                    result[provider] = count
                except Exception:
                    # Table may not exist or column not yet added — skip gracefully
                    result[provider] = -1
    return result


def get_price_history(
    project_id: int,
    source: Optional[str] = None,
) -> list[CachedPrice]:
    """Get all price snapshots for a project, optionally filtered by source.

    Ordered by checked_at ASC (chronological).
    """
    with psycopg.connect(DB_URL) as conn:
        with conn.cursor() as cur:
            if source is not None:
                cur.execute(
                    """
                    SELECT
                        project_id, source, matched_name,
                        sale_price_sqm, sale_count, sold_price_sqm, last_sold_date,
                        rent_median, rent_min, rent_max, rent_count, last_rental_date,
                        yoy_change_pct, govt_appraisal_sqm,
                        checked_at, ttl_days
                    FROM market_price_cache
                    WHERE project_id = %s AND source = %s
                    ORDER BY checked_at ASC
                    """,
                    (project_id, source),
                )
            else:
                cur.execute(
                    """
                    SELECT
                        project_id, source, matched_name,
                        sale_price_sqm, sale_count, sold_price_sqm, last_sold_date,
                        rent_median, rent_min, rent_max, rent_count, last_rental_date,
                        yoy_change_pct, govt_appraisal_sqm,
                        checked_at, ttl_days
                    FROM market_price_cache
                    WHERE project_id = %s
                    ORDER BY checked_at ASC
                    """,
                    (project_id,),
                )
            rows = cur.fetchall()

    return [_row_to_cached_price(r) for r in rows]


# ---------------------------------------------------------------------------
# CLI smoke-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    # Test registry create
    entry = create_or_update_registry(
        name_canonical="Inspire Place ABAC-Rama IX",
        name_th="อินสไปร์เพลส เอแบค พระราม 9",
        name_en="Inspire Place ABAC-Rama IX",
        aliases=["inspire place abac", "inspire place abac rama 9"],
        year_built=2006,
        total_units=636,
    )
    print(f"Registry: {entry}")

    # Test find
    found = find_registry("inspire place abac")
    print(f"Found: {found}")

    # Test insert price
    row_id = insert_price_snapshot(
        project_id=entry.id,
        source="hipflat",
        sale_price_sqm=44793,
        rent_median=9450,
    )
    print(f"Inserted price snapshot: id={row_id}")

    # Test get cached
    cached = get_cached_prices(entry.id)
    for c in cached:
        print(f"  {c.source}: {c.sale_price_sqm}/sqm, fresh={c.is_fresh}")

    # Test stale
    stale = get_stale_sources(entry.id)
    print(f"Stale sources: {stale}")

    # Test unlinked
    unlinked = get_unlinked_count()
    print(f"Unlinked: {unlinked}")

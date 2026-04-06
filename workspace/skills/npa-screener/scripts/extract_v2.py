"""
Multi-type NPA property extraction for Screener v2.

Queries all 6 NPA providers for ALL property types (or a filtered subset),
adds NPA vintage (months on market) and auction_round for LED.

Usage:
    from extract_v2 import extract_all_properties
    candidates = extract_all_properties(conn, provinces=["กรุงเทพมหานคร"])
"""

import os
from typing import Optional

import psycopg2
import psycopg2.extras

from models_v2 import NpaCandidate, PropertyType

# ---------------------------------------------------------------------------
# Property type mappings per provider
# ---------------------------------------------------------------------------

SAM_TYPE_MAP: dict[str, PropertyType] = {
    "ห้องชุดพักอาศัย": PropertyType.CONDO,
    "บ้านเดี่ยว": PropertyType.HOUSE,
    "ทาวน์เฮาส์": PropertyType.TOWNHOUSE,
    "ที่ดินเปล่า": PropertyType.LAND,
    "บ้านพร้อมที่ดิน": PropertyType.HOUSE_AND_LAND,
}

BAM_TYPE_MAP: dict[str, PropertyType] = {
    "ห้องชุดพักอาศัย": PropertyType.CONDO,
    "บ้านเดี่ยว": PropertyType.HOUSE,
    "ทาวน์เฮาส์": PropertyType.TOWNHOUSE,
    "ที่ดินเปล่า": PropertyType.LAND,
    "บ้านพร้อมที่ดิน": PropertyType.HOUSE_AND_LAND,
}

JAM_TYPE_MAP: dict[str, PropertyType] = {
    "คอนโดมิเนียม": PropertyType.CONDO,
    "บ้านเดี่ยว": PropertyType.HOUSE,
    "ทาวน์เฮาส์": PropertyType.TOWNHOUSE,
    "ที่ดิน": PropertyType.LAND,
}

KTB_TYPE_MAP: dict[str, PropertyType] = {
    "คอนโดมีเนียม/ห้องชุด": PropertyType.CONDO,
    "บ้านเดี่ยว": PropertyType.HOUSE,
    "ทาวน์เฮ้าส์/ทาวน์โฮม": PropertyType.TOWNHOUSE,
    "ที่ดินเปล่า": PropertyType.LAND,
}

KBANK_CODE_MAP: dict[str, PropertyType] = {
    "05": PropertyType.CONDO,
    "01": PropertyType.HOUSE,
    "02": PropertyType.TOWNHOUSE,
    "09": PropertyType.LAND,
}

LED_TYPE_MAP: dict[str, PropertyType] = {
    "ห้องชุด": PropertyType.CONDO,
    "บ้าน": PropertyType.HOUSE,
    "ที่ดิน": PropertyType.LAND,
}


def _resolve_property_type(raw: str | None, type_map: dict[str, PropertyType]) -> PropertyType:
    """Return mapped PropertyType or CONDO as fallback for unknown values."""
    if raw is None:
        return PropertyType.CONDO
    for key, ptype in type_map.items():
        if key in raw:
            return ptype
    return PropertyType.CONDO


def _row_to_candidate(row: dict, property_type: PropertyType) -> NpaCandidate:
    price = float(row["price_baht"]) if row.get("price_baht") else 0.0
    sqm = float(row["size_sqm"]) if row.get("size_sqm") else None
    lat = float(row["latitude"]) if row.get("latitude") else None
    lon = float(row["longitude"]) if row.get("longitude") else None
    price_sqm = price / sqm if (sqm and sqm > 0 and price > 0) else None
    vintage_raw = row.get("npa_vintage_months")
    vintage = int(round(float(vintage_raw))) if vintage_raw is not None else None
    auction_round_raw = row.get("auction_round")
    auction_round = int(auction_round_raw) if auction_round_raw is not None else None

    return NpaCandidate(
        source=row["source"],
        source_id=str(row["source_id"]),
        property_type=property_type,
        project_name=row.get("project_name") or "",
        province=row.get("province") or "",
        district=row.get("district") or "",
        subdistrict=row.get("subdistrict") or "",
        price_baht=price,
        size_sqm=sqm,
        lat=lat,
        lon=lon,
        bedroom=int(row["bedroom"]) if row.get("bedroom") else None,
        bathroom=int(row["bathroom"]) if row.get("bathroom") else None,
        floor=str(row["floor"]) if row.get("floor") else None,
        building_age=int(row["building_age"]) if row.get("building_age") else None,
        price_sqm=price_sqm,
        npa_vintage_months=vintage,
        auction_round=auction_round,
    )


def _type_filter_clause(
    col: str,
    allowed_types: set[PropertyType],
    type_map: dict[str, PropertyType],
) -> tuple[str, list]:
    """Build a SQL IN clause for provider type strings matching allowed_types."""
    matching_keys = [k for k, v in type_map.items() if v in allowed_types]
    if not matching_keys:
        # No matching types → return impossible condition
        return " AND FALSE", []
    placeholders = ", ".join(["%s"] * len(matching_keys))
    return f" AND {col} = ANY(%s)", [matching_keys]


def _kbank_code_filter_clause(
    allowed_types: set[PropertyType],
) -> tuple[str, list]:
    """Build a SQL IN clause for KBank property_type_code."""
    matching_codes = [k for k, v in KBANK_CODE_MAP.items() if v in allowed_types]
    if not matching_codes:
        return " AND FALSE", []
    return " AND kb.property_type_code = ANY(%s)", [matching_codes]


def _led_type_filter_clause(
    allowed_types: set[PropertyType],
) -> tuple[str, list]:
    """Build a SQL LIKE clause for LED property_type (partial match)."""
    matching_keys = [k for k, v in LED_TYPE_MAP.items() if v in allowed_types]
    if not matching_keys:
        return " AND FALSE", []
    # LED uses LIKE '%%ห้องชุด%%' pattern; build OR of LIKE clauses
    conditions = " OR ".join([f"p.property_type LIKE %s"] * len(matching_keys))
    params = [f"%{k}%" for k in matching_keys]
    return f" AND ({conditions})", params


def extract_all_properties(
    conn,
    provinces: list[str],
    max_price: float | None = None,
    property_types: list[str] | None = None,
) -> list[NpaCandidate]:
    """
    Extract NPA properties from all 6 providers.

    Args:
        conn: psycopg2 connection
        provinces: list of Thai province names to filter on
        max_price: optional upper price bound in baht
        property_types: optional list of PropertyType values (e.g. ["condo", "house"]).
                        Pass None to extract ALL types.

    Returns:
        list of NpaCandidate
    """
    allowed_types: set[PropertyType] | None = None
    if property_types is not None:
        allowed_types = {PropertyType(pt) for pt in property_types}

    candidates: list[NpaCandidate] = []
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    # --- SAM ---
    pc, pp = ("", [])
    if max_price:
        pc = " AND s.price_baht <= %s"
        pp = [max_price]
    tc, tp = ("", [])
    if allowed_types is not None:
        tc, tp = _type_filter_clause("s.type_name", allowed_types, SAM_TYPE_MAP)
    cur.execute(
        f"""
        SELECT 'SAM' as source, s.sam_id::text as source_id,
               s.type_name as raw_type,
               s.project_name, s.province, s.district,
               COALESCE(s.subdistrict, '') as subdistrict,
               s.price_baht, s.size_sqm, s.lat as latitude, s.lng as longitude,
               NULL::int as bedroom, NULL::int as bathroom, s.floor::text as floor,
               NULL::int as building_age,
               EXTRACT(EPOCH FROM (now() - s.first_seen_at)) / 86400.0 / 30.0 AS npa_vintage_months,
               NULL::int as auction_round
        FROM sam_properties s
        WHERE s.province = ANY(%s)
          AND s.price_baht > 0
          {pc}{tc}
        """,
        [provinces] + pp + tp,
    )
    for row in cur.fetchall():
        ptype = _resolve_property_type(row.get("raw_type"), SAM_TYPE_MAP)
        candidates.append(_row_to_candidate(row, ptype))

    # --- BAM ---
    pc, pp = ("", [])
    if max_price:
        pc = " AND COALESCE(b.discount_price, b.sell_price) <= %s"
        pp = [max_price]
    tc, tp = ("", [])
    if allowed_types is not None:
        tc, tp = _type_filter_clause("b.asset_type", allowed_types, BAM_TYPE_MAP)
    cur.execute(
        f"""
        SELECT 'BAM' as source, b.asset_no::text as source_id,
               b.asset_type as raw_type,
               b.project_th as project_name, b.province, b.district,
               COALESCE(b.sub_district, '') as subdistrict,
               COALESCE(b.discount_price, b.sell_price) as price_baht,
               b.usable_area as size_sqm, b.lat as latitude, b.lon as longitude,
               b.bedroom, b.bathroom, NULL::text as floor,
               NULL::int as building_age,
               EXTRACT(EPOCH FROM (now() - b.first_seen_at)) / 86400.0 / 30.0 AS npa_vintage_months,
               NULL::int as auction_round
        FROM bam_properties b
        WHERE b.province = ANY(%s)
          AND COALESCE(b.discount_price, b.sell_price) > 0
          {pc}{tc}
        """,
        [provinces] + pp + tp,
    )
    for row in cur.fetchall():
        ptype = _resolve_property_type(row.get("raw_type"), BAM_TYPE_MAP)
        candidates.append(_row_to_candidate(row, ptype))

    # --- JAM ---
    pc, pp = ("", [])
    if max_price:
        pc = " AND COALESCE(j.discount, j.selling) <= %s"
        pp = [max_price]
    tc, tp = ("", [])
    if allowed_types is not None:
        tc, tp = _type_filter_clause("j.type_asset_th", allowed_types, JAM_TYPE_MAP)
    cur.execute(
        f"""
        SELECT 'JAM' as source, j.asset_id::text as source_id,
               j.type_asset_th as raw_type,
               j.project_th as project_name, j.province_name as province,
               j.amphur_name as district,
               COALESCE(j.district_name, '') as subdistrict,
               COALESCE(j.discount, j.selling) as price_baht,
               j.meter as size_sqm, j.lat as latitude, j.lon as longitude,
               j.bedroom, j.bathroom, j.floor,
               NULL::int as building_age,
               EXTRACT(EPOCH FROM (now() - j.first_seen_at)) / 86400.0 / 30.0 AS npa_vintage_months,
               NULL::int as auction_round
        FROM jam_properties j
        WHERE j.province_name = ANY(%s)
          AND COALESCE(j.discount, j.selling) > 0
          {pc}{tc}
        """,
        [provinces] + pp + tp,
    )
    for row in cur.fetchall():
        ptype = _resolve_property_type(row.get("raw_type"), JAM_TYPE_MAP)
        candidates.append(_row_to_candidate(row, ptype))

    # --- KTB ---
    pc, pp = ("", [])
    if max_price:
        pc = " AND COALESCE(k.nml_price, k.price) <= %s"
        pp = [max_price]
    tc, tp = ("", [])
    if allowed_types is not None:
        tc, tp = _type_filter_clause("k.coll_type_name", allowed_types, KTB_TYPE_MAP)
    cur.execute(
        f"""
        SELECT 'KTB' as source, k.coll_grp_id::text as source_id,
               k.coll_type_name as raw_type,
               NULL::text as project_name, k.province, k.amphur as district,
               COALESCE(k.tambon, '') as subdistrict,
               COALESCE(k.nml_price, k.price) as price_baht,
               k.sum_area_num as size_sqm, k.lat as latitude, k.lon as longitude,
               k.bedroom_num as bedroom, k.bathroom_num as bathroom,
               NULL::text as floor, NULL::int as building_age,
               EXTRACT(EPOCH FROM (now() - k.first_seen_at)) / 86400.0 / 30.0 AS npa_vintage_months,
               NULL::int as auction_round
        FROM ktb_properties k
        WHERE k.province = ANY(%s)
          AND COALESCE(k.nml_price, k.price) > 0
          {pc}{tc}
        """,
        [provinces] + pp + tp,
    )
    for row in cur.fetchall():
        ptype = _resolve_property_type(row.get("raw_type"), KTB_TYPE_MAP)
        candidates.append(_row_to_candidate(row, ptype))

    # --- KBank ---
    pc, pp = ("", [])
    if max_price:
        pc = " AND COALESCE(kb.promotion_price, kb.sell_price) <= %s"
        pp = [max_price]
    tc, tp = ("", [])
    if allowed_types is not None:
        tc, tp = _kbank_code_filter_clause(allowed_types)
    cur.execute(
        f"""
        SELECT 'KBANK' as source, kb.property_id::text as source_id,
               kb.property_type_code as raw_type,
               COALESCE(kb.building_th, kb.village_th) as project_name,
               kb.province_name as province, kb.amphur_name as district,
               COALESCE(kb.tambon_name, '') as subdistrict,
               COALESCE(kb.promotion_price, kb.sell_price) as price_baht,
               kb.useable_area as size_sqm, kb.lat as latitude, kb.lon as longitude,
               kb.bedroom, kb.bathroom, NULL::text as floor,
               kb.building_age,
               EXTRACT(EPOCH FROM (now() - kb.first_seen_at)) / 86400.0 / 30.0 AS npa_vintage_months,
               NULL::int as auction_round
        FROM kbank_properties kb
        WHERE kb.province_name = ANY(%s)
          AND COALESCE(kb.promotion_price, kb.sell_price) > 0
          {pc}{tc}
        """,
        [provinces] + pp + tp,
    )
    for row in cur.fetchall():
        ptype = _resolve_property_type(row.get("raw_type"), KBANK_CODE_MAP)
        candidates.append(_row_to_candidate(row, ptype))

    # --- LED ---
    pc, pp = ("", [])
    if max_price:
        pc = " AND p.primary_price_satang <= %s"
        pp = [max_price * 100]  # convert baht to satang
    tc, tp = ("", [])
    if allowed_types is not None:
        tc, tp = _led_type_filter_clause(allowed_types)
    cur.execute(
        f"""
        SELECT 'LED' as source, p.asset_id::text as source_id,
               p.property_type as raw_type,
               NULL::text as project_name, p.province, p.ampur as district,
               COALESCE(p.tumbol, '') as subdistrict,
               p.primary_price_satang / 100.0 as price_baht,
               NULL::float as size_sqm, NULL::float as latitude, NULL::float as longitude,
               NULL::int as bedroom, NULL::int as bathroom, NULL::text as floor,
               NULL::int as building_age,
               EXTRACT(EPOCH FROM (now() - p.created_at)) / 86400.0 / 30.0 AS npa_vintage_months,
               p.total_auction_count as auction_round
        FROM properties p
        JOIN led_properties lp ON p.asset_id = lp.asset_id
        WHERE p.province = ANY(%s)
          AND p.primary_price_satang > 0
          {pc}{tc}
        """,
        [provinces] + pp + tp,
    )
    for row in cur.fetchall():
        ptype = _resolve_property_type(row.get("raw_type"), LED_TYPE_MAP)
        candidates.append(_row_to_candidate(row, ptype))

    cur.close()
    return candidates

"""Unified NPA adapter — queries all provider tables, normalizes to NpaProperty.

Each provider keeps its own table. This layer reads from all of them
and returns a common shape. No writes, no schema changes.

Provider tables:
  LED  → properties + led_properties  (price in SATANG)
  SAM  → sam_properties               (price in BAHT)
  BAM  → bam_properties               (price in BAHT)
  JAM  → jam_properties               (price in BAHT)
  KTB  → ktb_properties               (price in BAHT)
  KBANK→ kbank_properties             (price in BAHT)
"""

from __future__ import annotations

import os
from typing import Any

import psycopg2
import psycopg2.extras

from models import NpaProperty, ProviderStats, SearchFilters, Source

POSTGRES_URI = os.getenv("POSTGRES_URI", "postgresql://arsapolm@localhost:5432/npa_kb")


def _conn():
    return psycopg2.connect(POSTGRES_URI)


def _safe_float(v: Any) -> float | None:
    if v is None:
        return None
    try:
        return float(v)
    except (ValueError, TypeError):
        return None


def _safe_int(v: Any) -> int | None:
    if v is None:
        return None
    try:
        return int(v)
    except (ValueError, TypeError):
        return None


# ---------------------------------------------------------------------------
# Per-provider query builders
# ---------------------------------------------------------------------------

def _where_clause(
    filters: SearchFilters,
    province_col: str,
    district_col: str,
    subdistrict_col: str,
    price_col: str,
    type_col: str,
    keyword_cols: list[str] | None = None,
) -> tuple[str, list[Any]]:
    """Build WHERE clause + params from unified filters."""
    conditions: list[str] = ["1=1"]
    params: list[Any] = []

    if filters.province:
        conditions.append(f"{province_col} ILIKE %s")
        params.append(f"%{filters.province}%")
    if filters.district:
        conditions.append(f"{district_col} ILIKE %s")
        params.append(f"%{filters.district}%")
    if filters.subdistrict:
        conditions.append(f"{subdistrict_col} ILIKE %s")
        params.append(f"%{filters.subdistrict}%")
    if filters.property_type:
        conditions.append(f"{type_col} ILIKE %s")
        params.append(f"%{filters.property_type}%")
    if keyword_cols and filters.keyword:
        kw_conds = [f"{c} ILIKE %s" for c in keyword_cols]
        conditions.append(f"({' OR '.join(kw_conds)})")
        params.extend([f"%{filters.keyword}%"] * len(keyword_cols))

    return " AND ".join(conditions), params


def _price_filter(
    price_col: str,
    filters: SearchFilters,
    multiplier: float = 1.0,
) -> tuple[str, list[Any]]:
    """Build min/max price conditions. multiplier=100 for satang→baht."""
    conditions: list[str] = []
    params: list[Any] = []
    if filters.min_price is not None:
        conditions.append(f"{price_col} >= %s")
        params.append(filters.min_price * multiplier)
    if filters.max_price is not None:
        conditions.append(f"{price_col} <= %s")
        params.append(filters.max_price * multiplier)
    return " AND ".join(conditions) if conditions else "", params


def _order_clause(price_col: str, filters: SearchFilters) -> str:
    direction = "DESC" if filters.sort_desc else "ASC"
    col_map = {
        "price": price_col,
        "province": "province",
        "newest": "first_seen_at",
    }
    col = col_map.get(filters.sort_by, price_col)
    return f"{col} {direction} NULLS LAST"


# ---------------------------------------------------------------------------
# LED
# ---------------------------------------------------------------------------

def _query_led(filters: SearchFilters) -> list[NpaProperty]:
    where, params = _where_clause(
        filters,
        province_col="p.province",
        district_col="p.ampur",
        subdistrict_col="p.tumbol",
        price_col="p.property_type",  # dummy — overridden below
        type_col="p.property_type",
        keyword_cols=["p.address", "l.remark"],
    )

    price_where, price_params = _price_filter(
        "p.primary_price_satang", filters, multiplier=100.0,
    )
    if price_where:
        where += f" AND {price_where}"
        params.extend(price_params)

    order = "p.primary_price_satang"
    if filters.sort_by == "province":
        order = "p.province"
    elif filters.sort_by == "newest":
        order = "p.created_at"
    direction = "DESC" if filters.sort_desc else "ASC"

    sql = f"""
        SELECT
            p.asset_id, p.property_type, p.address,
            p.province, p.ampur, p.tumbol,
            p.size_rai, p.size_ngan, p.size_wa,
            p.primary_price_satang,
            p.appraisal_price_satang,
            p.sale_status,
            p.next_auction_date, p.total_auction_count,
            p.source_url,
            l.case_number, l.court, l.deed_type
        FROM properties p
        LEFT JOIN led_properties l ON p.asset_id = l.asset_id
        WHERE {where}
        ORDER BY {order} {direction} NULLS LAST
        LIMIT %s OFFSET %s
    """
    params.extend([filters.limit, filters.offset])

    conn = _conn()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()
    finally:
        conn.close()

    results: list[NpaProperty] = []
    for r in rows:
        price = _safe_float(r["primary_price_satang"])
        price_baht = price / 100.0 if price else None
        appraisal = _safe_float(r["appraisal_price_satang"])
        appraisal_baht = appraisal / 100.0 if appraisal else None

        ptype = r["property_type"] or ""
        is_condo = "ห้องชุด" in ptype or "คอนโด" in ptype
        size_wa = _safe_float(r["size_wa"])

        discount = None
        if price_baht and appraisal_baht and appraisal_baht > 0:
            discount = round((1 - price_baht / appraisal_baht) * 100, 1)

        results.append(NpaProperty(
            source=Source.LED,
            source_id=r["asset_id"] or "",
            property_type=ptype,
            province=r["province"] or "",
            district=r["ampur"] or "",
            subdistrict=r["tumbol"] or "",
            price_baht=price_baht,
            appraisal_baht=appraisal_baht,
            discount_pct=discount,
            size_rai=_safe_float(r["size_rai"]),
            size_ngan=_safe_float(r["size_ngan"]),
            size_wa=None if is_condo else size_wa,
            size_sqm=size_wa if is_condo else None,
            status=r["sale_status"] or "",
            next_auction_date=r["next_auction_date"],
            total_auction_count=_safe_int(r["total_auction_count"]) or 0,
            address=r["address"],
            source_url=r["source_url"],
            extra={
                "case_number": r["case_number"],
                "court": r["court"],
                "deed_type": r["deed_type"],
            },
        ))
    return results


# ---------------------------------------------------------------------------
# SAM
# ---------------------------------------------------------------------------

def _query_sam(filters: SearchFilters) -> list[NpaProperty]:
    where, params = _where_clause(
        filters,
        province_col="province",
        district_col="district",
        subdistrict_col="subdistrict",
        price_col="price_baht",
        type_col="type_name",
        keyword_cols=["address_full", "project_name", "remarks"],
    )

    price_where, price_params = _price_filter("price_baht", filters)
    if price_where:
        where += f" AND {price_where}"
        params.extend(price_params)

    where += " AND is_active = true"

    order_map = {
        "price": "price_baht",
        "province": "province",
        "newest": "first_seen_at",
    }
    order = order_map.get(filters.sort_by, "price_baht")
    direction = "DESC" if filters.sort_desc else "ASC"

    sql = f"""
        SELECT
            sam_id, code, type_name,
            province, district, subdistrict,
            price_baht, price_per_unit, price_unit,
            size_rai, size_ngan, size_wa, size_sqm,
            lat, lng,
            status, project_name, address_full,
            source_url, thumbnail_url,
            floor, title_deed_type,
            announcement_start_date, submission_date
        FROM sam_properties
        WHERE {where}
        ORDER BY {order} {direction} NULLS LAST
        LIMIT %s OFFSET %s
    """
    params.extend([filters.limit, filters.offset])

    conn = _conn()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()
    finally:
        conn.close()

    results: list[NpaProperty] = []
    for r in rows:
        price = _safe_float(r["price_baht"])
        results.append(NpaProperty(
            source=Source.SAM,
            source_id=str(r["sam_id"]),
            property_type=r["type_name"] or "",
            province=r["province"] or "",
            district=r["district"] or "",
            subdistrict=r["subdistrict"] or "",
            price_baht=price,
            size_rai=_safe_float(r["size_rai"]),
            size_ngan=_safe_float(r["size_ngan"]),
            size_wa=_safe_float(r["size_wa"]),
            size_sqm=_safe_float(r["size_sqm"]),
            lat=_safe_float(r["lat"]),
            lon=_safe_float(r["lng"]),
            status=r["status"] or "",
            project_name=r["project_name"],
            address=r["address_full"],
            source_url=r["source_url"],
            thumbnail_url=r["thumbnail_url"],
            extra={
                "code": r["code"],
                "floor": r["floor"],
                "deed_type": r["title_deed_type"],
                "submission_date": r["submission_date"],
                "price_per_unit": _safe_float(r["price_per_unit"]),
                "price_unit": r["price_unit"],
            },
        ))
    return results


# ---------------------------------------------------------------------------
# BAM
# ---------------------------------------------------------------------------

def _query_bam(filters: SearchFilters) -> list[NpaProperty]:
    where, params = _where_clause(
        filters,
        province_col="province",
        district_col="district",
        subdistrict_col="sub_district",
        price_col="sell_price",
        type_col="asset_type",
        keyword_cols=["property_location", "project_th", "property_detail"],
    )

    price_where, price_params = _price_filter("sell_price", filters)
    if price_where:
        where += f" AND {price_where}"
        params.extend(price_params)

    order_map = {
        "price": "sell_price",
        "province": "province",
        "newest": "first_seen_at",
    }
    order = order_map.get(filters.sort_by, "sell_price")
    direction = "DESC" if filters.sort_desc else "ASC"

    sql = f"""
        SELECT
            id, asset_no, asset_type, asset_state,
            province, district, sub_district, property_location,
            sell_price, evaluate_amt, discount_price, shock_price,
            rai, ngan, wa, area_meter, usable_area,
            bedroom, bathroom,
            lat, lon,
            project_th, grade,
            is_hot_deal, is_shock_price
        FROM bam_properties
        WHERE {where}
        ORDER BY {order} {direction} NULLS LAST
        LIMIT %s OFFSET %s
    """
    params.extend([filters.limit, filters.offset])

    conn = _conn()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()
    finally:
        conn.close()

    results: list[NpaProperty] = []
    for r in rows:
        price = _safe_float(r["sell_price"])
        appraisal = _safe_float(r["evaluate_amt"])
        discount = None
        if price and appraisal and appraisal > 0:
            discount = round((1 - price / appraisal) * 100, 1)

        results.append(NpaProperty(
            source=Source.BAM,
            source_id=str(r["id"]),
            property_type=r["asset_type"] or "",
            province=r["province"] or "",
            district=r["district"] or "",
            subdistrict=r["sub_district"] or "",
            price_baht=price,
            appraisal_baht=appraisal,
            discount_pct=discount,
            size_rai=_safe_float(r["rai"]),
            size_ngan=_safe_float(r["ngan"]),
            size_wa=_safe_float(r["wa"]),
            size_sqm=_safe_float(r["area_meter"]) or _safe_float(r["usable_area"]),
            bedroom=_safe_int(r["bedroom"]),
            bathroom=_safe_int(r["bathroom"]),
            lat=_safe_float(r["lat"]),
            lon=_safe_float(r["lon"]),
            status=r["asset_state"] or "",
            project_name=r["project_th"],
            address=r["property_location"],
            extra={
                "asset_no": r["asset_no"],
                "grade": r["grade"],
                "discount_price": _safe_float(r["discount_price"]),
                "shock_price": _safe_float(r["shock_price"]),
                "is_hot_deal": r["is_hot_deal"],
                "is_shock_price": r["is_shock_price"],
            },
        ))
    return results


# ---------------------------------------------------------------------------
# JAM
# ---------------------------------------------------------------------------

def _query_jam(filters: SearchFilters) -> list[NpaProperty]:
    where, params = _where_clause(
        filters,
        province_col="province_name",
        district_col="amphur_name",
        subdistrict_col="district_name",
        price_col="selling",
        type_col="type_asset_th",
        keyword_cols=["project_th", "project_en", "soi", "road"],
    )

    price_where, price_params = _price_filter("selling", filters)
    if price_where:
        where += f" AND {price_where}"
        params.extend(price_params)

    # Exclude sold-out by default
    where += " AND (status_soldout = false OR status_soldout IS NULL)"

    order_map = {
        "price": "selling",
        "province": "province_name",
        "newest": "first_seen_at",
    }
    order = order_map.get(filters.sort_by, "selling")
    direction = "DESC" if filters.sort_desc else "ASC"

    sql = f"""
        SELECT
            asset_id, borr_code, asset_no,
            type_asset_th, type_sale_th,
            province_name, amphur_name, district_name,
            selling, discount, rental,
            wah, meter,
            bedroom, bathroom, floor,
            lat, lon,
            project_th,
            status_soldout, status_hotdeal, is_flash_sale,
            images_main_web
        FROM jam_properties
        WHERE {where}
        ORDER BY {order} {direction} NULLS LAST
        LIMIT %s OFFSET %s
    """
    params.extend([filters.limit, filters.offset])

    conn = _conn()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()
    finally:
        conn.close()

    results: list[NpaProperty] = []
    for r in rows:
        price = _safe_float(r["selling"])
        results.append(NpaProperty(
            source=Source.JAM,
            source_id=str(r["asset_id"]),
            property_type=r["type_asset_th"] or "",
            province=r["province_name"] or "",
            district=r["amphur_name"] or "",
            subdistrict=r["district_name"] or "",
            price_baht=price,
            size_wa=_safe_float(r["wah"]),
            size_sqm=_safe_float(r["meter"]),
            bedroom=_safe_int(r["bedroom"]),
            bathroom=_safe_int(r["bathroom"]),
            lat=_safe_float(r["lat"]),
            lon=_safe_float(r["lon"]),
            status=r["type_sale_th"] or "",
            is_sold=bool(r["status_soldout"]),
            project_name=r["project_th"],
            thumbnail_url=r["images_main_web"],
            extra={
                "borr_code": r["borr_code"],
                "asset_no": r["asset_no"],
                "discount": _safe_float(r["discount"]),
                "rental": _safe_float(r["rental"]),
                "floor": r["floor"],
                "is_hot_deal": r["status_hotdeal"],
                "is_flash_sale": r["is_flash_sale"],
            },
        ))
    return results


# ---------------------------------------------------------------------------
# KTB
# ---------------------------------------------------------------------------

def _query_ktb(filters: SearchFilters) -> list[NpaProperty]:
    where, params = _where_clause(
        filters,
        province_col="province",
        district_col="amphur",
        subdistrict_col="tambon",
        price_col="price",
        type_col="coll_cate_name",
        keyword_cols=["addr", "coll_desc"],
    )

    price_where, price_params = _price_filter("price", filters)
    if price_where:
        where += f" AND {price_where}"
        params.extend(price_params)

    order_map = {
        "price": "price",
        "province": "province",
        "newest": "first_seen_at",
    }
    order = order_map.get(filters.sort_by, "price")
    direction = "DESC" if filters.sort_desc else "ASC"

    sql = f"""
        SELECT
            coll_grp_id, coll_code,
            coll_cate_name, coll_type_name, cate_name,
            province, amphur, tambon, addr,
            price, nml_price,
            rai, ngan, wah, sum_area_num,
            bedroom_num, bathroom_num,
            lat, lon,
            share_url,
            is_speedy, is_new_asset, is_promotion, lodge
        FROM ktb_properties
        WHERE {where}
        ORDER BY {order} {direction} NULLS LAST
        LIMIT %s OFFSET %s
    """
    params.extend([filters.limit, filters.offset])

    conn = _conn()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()
    finally:
        conn.close()

    results: list[NpaProperty] = []
    for r in rows:
        price = _safe_float(r["price"])
        nml = _safe_float(r["nml_price"])
        discount = None
        if price and nml and nml > 0:
            discount = round((1 - price / nml) * 100, 1)

        results.append(NpaProperty(
            source=Source.KTB,
            source_id=str(r["coll_grp_id"]),
            property_type=r["coll_cate_name"] or r["coll_type_name"] or "",
            province=r["province"] or "",
            district=r["amphur"] or "",
            subdistrict=r["tambon"] or "",
            price_baht=price,
            appraisal_baht=nml,
            discount_pct=discount,
            size_rai=_safe_float(r["rai"]),
            size_ngan=_safe_float(r["ngan"]),
            size_wa=_safe_float(r["wah"]),
            size_sqm=_safe_float(r["sum_area_num"]),
            bedroom=_safe_int(r["bedroom_num"]),
            bathroom=_safe_int(r["bathroom_num"]),
            lat=_safe_float(r["lat"]),
            lon=_safe_float(r["lon"]),
            status=r["cate_name"] or "",
            address=r["addr"],
            source_url=r["share_url"],
            extra={
                "coll_code": r["coll_code"],
                "is_speedy": r["is_speedy"],
                "is_new_asset": r["is_new_asset"],
                "is_promotion": r["is_promotion"],
                "lodge": r["lodge"],
            },
        ))
    return results


# ---------------------------------------------------------------------------
# KBANK
# ---------------------------------------------------------------------------

def _query_kbank(filters: SearchFilters) -> list[NpaProperty]:
    where, params = _where_clause(
        filters,
        province_col="province_name",
        district_col="amphur_name",
        subdistrict_col="tambon_name",
        price_col="sell_price",
        type_col="property_type_name",
        keyword_cols=["full_address", "village_th", "asset_info_th"],
    )

    price_where, price_params = _price_filter("sell_price", filters)
    if price_where:
        where += f" AND {price_where}"
        params.extend(price_params)

    where += " AND (is_sold_out = false OR is_sold_out IS NULL)"

    order_map = {
        "price": "sell_price",
        "province": "province_name",
        "newest": "first_seen_at",
    }
    order = order_map.get(filters.sort_by, "sell_price")
    direction = "DESC" if filters.sort_desc else "ASC"

    sql = f"""
        SELECT
            property_id, property_id_format,
            property_type_name, source_code,
            province_name, amphur_name, tambon_name,
            sell_price, promotion_price, adjust_price,
            rai, ngan, square_area, useable_area,
            bedroom, bathroom,
            lat, lon,
            village_th, full_address,
            is_sold_out, is_new, is_hot, is_reserve,
            promotion_name
        FROM kbank_properties
        WHERE {where}
        ORDER BY {order} {direction} NULLS LAST
        LIMIT %s OFFSET %s
    """
    params.extend([filters.limit, filters.offset])

    conn = _conn()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()
    finally:
        conn.close()

    results: list[NpaProperty] = []
    for r in rows:
        price = _safe_float(r["sell_price"])
        results.append(NpaProperty(
            source=Source.KBANK,
            source_id=r["property_id"] or "",
            property_type=r["property_type_name"] or "",
            province=r["province_name"] or "",
            district=r["amphur_name"] or "",
            subdistrict=r["tambon_name"] or "",
            price_baht=price,
            size_rai=_safe_float(r["rai"]),
            size_ngan=_safe_float(r["ngan"]),
            size_wa=_safe_float(r["square_area"]),
            size_sqm=_safe_float(r["useable_area"]),
            bedroom=_safe_int(r["bedroom"]),
            bathroom=_safe_int(r["bathroom"]),
            lat=_safe_float(r["lat"]),
            lon=_safe_float(r["lon"]),
            status="sold" if r["is_sold_out"] else "active",
            is_sold=bool(r["is_sold_out"]),
            project_name=r["village_th"],
            address=r["full_address"],
            extra={
                "source_code": r["source_code"],
                "promotion_price": _safe_float(r["promotion_price"]),
                "adjust_price": _safe_float(r["adjust_price"]),
                "promotion_name": r["promotion_name"],
                "is_new": r["is_new"],
                "is_hot": r["is_hot"],
            },
        ))
    return results


# ---------------------------------------------------------------------------
# Dispatcher map
# ---------------------------------------------------------------------------

_PROVIDERS: dict[Source, Any] = {
    Source.LED: _query_led,
    Source.SAM: _query_sam,
    Source.BAM: _query_bam,
    Source.JAM: _query_jam,
    Source.KTB: _query_ktb,
    Source.KBANK: _query_kbank,
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def search(filters: SearchFilters) -> list[NpaProperty]:
    """Search across all (or selected) providers, merge results."""
    sources = filters.sources or list(Source)
    all_results: list[NpaProperty] = []

    for src in sources:
        query_fn = _PROVIDERS.get(src)
        if query_fn is None:
            continue
        try:
            all_results.extend(query_fn(filters))
        except Exception as e:
            # Provider table might not exist yet — skip gracefully
            import sys
            print(f"[WARN] {src.value}: {e}", file=sys.stderr)

    # Re-sort merged results
    if filters.sort_by == "price":
        all_results.sort(
            key=lambda p: p.price_baht if p.price_baht is not None else float("inf"),
            reverse=filters.sort_desc,
        )
    elif filters.sort_by == "province":
        all_results.sort(key=lambda p: p.province, reverse=filters.sort_desc)

    return all_results


def stats() -> list[ProviderStats]:
    """Get summary stats per provider."""
    queries: dict[Source, str] = {
        Source.LED: """
            SELECT COUNT(*) as total,
                   MIN(primary_price_satang)/100.0 as min_price,
                   MAX(primary_price_satang)/100.0 as max_price,
                   AVG(primary_price_satang)/100.0 as avg_price
            FROM properties WHERE primary_price_satang > 0
        """,
        Source.SAM: """
            SELECT COUNT(*) as total,
                   MIN(price_baht) as min_price,
                   MAX(price_baht) as max_price,
                   AVG(price_baht) as avg_price
            FROM sam_properties WHERE is_active = true AND price_baht > 0
        """,
        Source.BAM: """
            SELECT COUNT(*) as total,
                   MIN(sell_price) as min_price,
                   MAX(sell_price) as max_price,
                   AVG(sell_price) as avg_price
            FROM bam_properties WHERE sell_price > 0
        """,
        Source.JAM: """
            SELECT COUNT(*) as total,
                   MIN(selling) as min_price,
                   MAX(selling) as max_price,
                   AVG(selling) as avg_price
            FROM jam_properties WHERE (status_soldout = false OR status_soldout IS NULL) AND selling > 0
        """,
        Source.KTB: """
            SELECT COUNT(*) as total,
                   MIN(price) as min_price,
                   MAX(price) as max_price,
                   AVG(price) as avg_price
            FROM ktb_properties WHERE price > 0
        """,
        Source.KBANK: """
            SELECT COUNT(*) as total,
                   MIN(sell_price) as min_price,
                   MAX(sell_price) as max_price,
                   AVG(sell_price) as avg_price
            FROM kbank_properties WHERE (is_sold_out = false OR is_sold_out IS NULL) AND sell_price > 0
        """,
    }

    province_queries: dict[Source, str] = {
        Source.LED: "SELECT province, COUNT(*) as cnt FROM properties GROUP BY province ORDER BY cnt DESC LIMIT 10",
        Source.SAM: "SELECT province, COUNT(*) as cnt FROM sam_properties WHERE is_active = true GROUP BY province ORDER BY cnt DESC LIMIT 10",
        Source.BAM: "SELECT province, COUNT(*) as cnt FROM bam_properties GROUP BY province ORDER BY cnt DESC LIMIT 10",
        Source.JAM: "SELECT province_name as province, COUNT(*) as cnt FROM jam_properties WHERE (status_soldout = false OR status_soldout IS NULL) GROUP BY province_name ORDER BY cnt DESC LIMIT 10",
        Source.KTB: "SELECT province, COUNT(*) as cnt FROM ktb_properties GROUP BY province ORDER BY cnt DESC LIMIT 10",
        Source.KBANK: "SELECT province_name as province, COUNT(*) as cnt FROM kbank_properties WHERE (is_sold_out = false OR is_sold_out IS NULL) GROUP BY province_name ORDER BY cnt DESC LIMIT 10",
    }

    results: list[ProviderStats] = []
    conn = _conn()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            for src, sql in queries.items():
                try:
                    cur.execute(sql)
                    row = cur.fetchone()
                    if row is None or row["total"] == 0:
                        continue

                    # Province breakdown
                    provinces: list[dict[str, Any]] = []
                    prov_sql = province_queries.get(src)
                    if prov_sql:
                        cur.execute(prov_sql)
                        provinces = [dict(r) for r in cur.fetchall()]

                    results.append(ProviderStats(
                        source=src,
                        total=int(row["total"]),
                        min_price=_safe_float(row["min_price"]),
                        max_price=_safe_float(row["max_price"]),
                        avg_price=_safe_float(row["avg_price"]),
                        provinces=provinces,
                    ))
                except Exception as e:
                    import sys
                    print(f"[WARN] stats {src.value}: {e}", file=sys.stderr)
    finally:
        conn.close()

    return results


def summary() -> dict[str, Any]:
    """Cross-provider summary: total counts, grand totals."""
    provider_stats = stats()
    grand_total = sum(s.total for s in provider_stats)

    return {
        "grand_total": grand_total,
        "providers": [
            {
                "source": s.source.value,
                "total": s.total,
                "min_price": s.min_price,
                "max_price": s.max_price,
                "avg_price": round(s.avg_price, 0) if s.avg_price else None,
                "top_provinces": s.provinces[:5],
            }
            for s in provider_stats
        ],
    }

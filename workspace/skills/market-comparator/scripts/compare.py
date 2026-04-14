"""Market comparator: compare NPA auction prices against DDProperty/PropertyHub/Hipflat."""

import argparse
import json
import os
import statistics
import sys

from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy import create_engine, text

DB_URL = os.getenv("DATABASE_URL", "postgresql://arsapolm@localhost:5432/npa_kb")

# --- Provider configs ---
# (name, table, id_expr, lat_col, lon_col, price_expr, type_expr)
BANK_PROVIDERS = [
    ("BAM", "bam_properties", "asset_no", "lat", "lon", "sell_price::numeric", "col_typedesc"),
    ("KBank", "kbank_properties", "property_id", "lat", "lon", "adjust_price::numeric", "property_type_name"),
    ("GHB", "ghb_properties", "property_id::text", "lat", "lon", "selling_price::numeric", "area_txt"),
    ("JAM", "jam_properties", "asset_id::text", "lat", "lon", "price::numeric", "type_asset_th"),
    ("SCB", "scb_properties", "project_id::text", "lat", "lon", "price::numeric", "project_type_name"),
    ("GSB", "gsb_properties", "npa_id", "lat", "lon", "current_offer_price::numeric", "asset_type_desc"),
    ("TTB", "ttb_properties", "id_property::text", "lat", "lon", "price::numeric", "NULL"),
    ("BAY", "bay_properties", "code", "lat", "lon", "sale_price::numeric", "property_type_name"),
    ("LH", "lh_properties", "property_id", "lat", "lon", "sale_price::numeric", "asset_type"),
    ("KTB", "ktb_properties", "coll_grp_id::text", "lat", "lon", "price::numeric", "coll_type_name"),
    ("SAM", "sam_properties", "sam_id::text", "lat", "lng", "price_baht::numeric", "NULL"),
]


# --- Models ---

class NpaProperty(BaseModel):
    model_config = ConfigDict(ser_json_inf_nan="constants")
    source: str
    asset_id: str
    price_baht: float | None = None
    property_type: str = "unknown"
    area_sqw: float | None = None
    area_sqm: float | None = None
    lat: float
    lon: float
    dist_m: float
    price_per_unit: float | None = None
    unit: str = ""


class MarketComp(BaseModel):
    source: str
    listing_id: str
    price_baht: float | None = None
    area_sqm: float | None = None
    area_sqw: float | None = None
    property_type: str = "unknown"
    bedrooms: int | None = None
    dist_m: float | None = None
    address: str = ""
    price_per_unit: float | None = None
    unit: str = ""


class ComparisonResult(BaseModel):
    npa: NpaProperty
    market_count: int = 0
    market_min: float | None = None
    market_median: float | None = None
    market_max: float | None = None
    discount_pct: float | None = None
    rating: str = "NO_COMP"


# --- Engine ---

_eng = None

def _engine():
    global _eng
    if _eng is None:
        _eng = create_engine(DB_URL)
    return _eng


# --- GPS Resolution ---

def resolve_gps_from_asset(asset_id: str, source: str | None = None) -> tuple[float, float] | None:
    """Resolve GPS from an asset_id. Tries LED land parcels first, then bank tables."""
    with _engine().connect() as conn:
        # LED: via led_land_parcels
        row = conn.execute(text("""
            SELECT lp.lat, lp.lon FROM led_land_parcels lp
            WHERE lp.asset_id = :aid AND lp.lat IS NOT NULL
            LIMIT 1
        """), {"aid": asset_id}).mappings().first()
        if row:
            return (row["lat"], row["lon"])

        # Bank tables: try each until found
        for name, table, id_expr, lat_col, lon_col, *_ in BANK_PROVIDERS:
            if source and source.upper() != name:
                continue
            id_col = id_expr.split("::")[0]
            try:
                row = conn.execute(text(f"""
                    SELECT {lat_col}::float AS lat, {lon_col}::float AS lon
                    FROM {table} WHERE {id_col}::text = :aid
                    AND {lat_col} IS NOT NULL LIMIT 1
                """), {"aid": asset_id}).mappings().first()
                if row:
                    return (row["lat"], row["lon"])
            except Exception:
                continue
    return None


def resolve_road_geometry(road_name: str):
    """Get road geometry from osm_roads for spatial queries."""
    with _engine().connect() as conn:
        row = conn.execute(text("""
            SELECT ST_Union(way) AS geom
            FROM osm_roads
            WHERE name_th LIKE :pattern AND highway IN ('motorway','trunk','primary','secondary')
        """), {"pattern": f"%{road_name}%"}).mappings().first()
        if row and row["geom"]:
            return row["geom"]
    return None


# --- NPA Queries ---

def find_npa_nearby_point(lat: float, lon: float, radius_m: float = 2000) -> list[NpaProperty]:
    """Find NPA properties from all providers within radius of a GPS point."""
    results: list[NpaProperty] = []
    results.extend(_query_led_nearby(lat, lon, radius_m))
    results.extend(_query_banks_nearby(lat, lon, radius_m))
    results.sort(key=lambda r: r.dist_m)
    return results


def find_npa_near_road(road_name: str, radius_m: float = 500) -> list[NpaProperty]:
    """Find NPA properties near a named road."""
    results: list[NpaProperty] = []
    results.extend(_query_led_near_road(road_name, radius_m))
    results.extend(_query_banks_near_road(road_name, radius_m))
    results.sort(key=lambda r: r.dist_m)
    return results


def _query_led_nearby(lat: float, lon: float, radius_m: float) -> list[NpaProperty]:
    query = text("""
        SELECT p.asset_id, p.property_type, p.primary_price_satang / 100.0 AS price_baht,
               lp.lat, lp.lon, lp.rai, lp.ngan, lp.wa,
               round(ST_Distance(
                   ST_MakePoint(lp.lon, lp.lat)::geography,
                   ST_MakePoint(:lon, :lat)::geography
               )::numeric, 1) AS dist_m
        FROM properties p
        JOIN led_land_parcels lp ON lp.asset_id = p.asset_id
        WHERE p.source_name LIKE 'LED_%'
          AND lp.lat IS NOT NULL AND lp.lon IS NOT NULL
          AND ST_DWithin(
              ST_MakePoint(lp.lon, lp.lat)::geography,
              ST_MakePoint(:lon, :lat)::geography, :radius)
        ORDER BY dist_m LIMIT 50
    """)
    with _engine().connect() as conn:
        rows = conn.execute(query, {"lat": lat, "lon": lon, "radius": radius_m}).mappings().all()
    return [_led_row_to_npa(r) for r in rows]


def _query_led_near_road(road_name: str, radius_m: float) -> list[NpaProperty]:
    query = text("""
        WITH road AS (
            SELECT ST_Union(way) AS geom FROM osm_roads
            WHERE name_th LIKE :pattern AND highway IN ('motorway','trunk','primary','secondary')
        )
        SELECT p.asset_id, p.property_type, p.primary_price_satang / 100.0 AS price_baht,
               lp.lat, lp.lon, lp.rai, lp.ngan, lp.wa,
               round(ST_Distance(
                   ST_MakePoint(lp.lon, lp.lat)::geography, road.geom::geography
               )::numeric, 1) AS dist_m
        FROM properties p
        JOIN led_land_parcels lp ON lp.asset_id = p.asset_id
        CROSS JOIN road
        WHERE p.source_name LIKE 'LED_%'
          AND lp.lat IS NOT NULL AND lp.lon IS NOT NULL
          AND road.geom IS NOT NULL
          AND ST_DWithin(
              ST_MakePoint(lp.lon, lp.lat)::geography, road.geom::geography, :radius)
        ORDER BY dist_m LIMIT 50
    """)
    with _engine().connect() as conn:
        rows = conn.execute(query, {"pattern": f"%{road_name}%", "radius": radius_m}).mappings().all()
    return [_led_row_to_npa(r) for r in rows]


def _led_row_to_npa(r) -> NpaProperty:
    rai = r["rai"] or 0
    ngan = r["ngan"] or 0
    wa = r["wa"] or 0
    area_sqw = rai * 400 + ngan * 100 + wa
    price = float(r["price_baht"]) if r["price_baht"] else None
    ptype = _classify_type(r["property_type"] or "")
    unit = "sqm" if ptype == "condo" else "sqw"
    area_for_calc = area_sqw if unit == "sqw" else (area_sqw * 4 if area_sqw else None)
    ppu = round(price / area_for_calc, 0) if price and area_for_calc else None
    return NpaProperty(
        source="LED", asset_id=str(r["asset_id"]),
        price_baht=price, property_type=ptype,
        area_sqw=area_sqw if area_sqw else None,
        area_sqm=area_sqw * 4 if area_sqw else None,
        lat=float(r["lat"]), lon=float(r["lon"]),
        dist_m=float(r["dist_m"]),
        price_per_unit=ppu, unit=unit,
    )


def _query_banks_nearby(lat: float, lon: float, radius_m: float) -> list[NpaProperty]:
    results = []
    for prov in BANK_PROVIDERS:
        results.extend(_query_single_bank(prov, "point", lat=lat, lon=lon, radius_m=radius_m))
    return results


def _query_banks_near_road(road_name: str, radius_m: float) -> list[NpaProperty]:
    results = []
    for prov in BANK_PROVIDERS:
        results.extend(_query_single_bank(prov, "road", road_name=road_name, radius_m=radius_m))
    return results


def _query_single_bank(prov: tuple, mode: str, **kwargs) -> list[NpaProperty]:
    name, table, id_expr, lat_col, lon_col, price_expr, type_expr = prov

    if mode == "point":
        where = f"""ST_DWithin(
            ST_MakePoint(t.{lon_col}::float, t.{lat_col}::float)::geography,
            ST_MakePoint(:lon, :lat)::geography, :radius)"""
        dist = f"""round(ST_Distance(
            ST_MakePoint(t.{lon_col}::float, t.{lat_col}::float)::geography,
            ST_MakePoint(:lon, :lat)::geography)::numeric, 1)"""
        params = {"lat": kwargs["lat"], "lon": kwargs["lon"], "radius": kwargs["radius_m"]}
    else:
        where = f"""ST_DWithin(
            ST_MakePoint(t.{lon_col}::float, t.{lat_col}::float)::geography,
            road.geom::geography, :radius)"""
        dist = f"""round(ST_Distance(
            ST_MakePoint(t.{lon_col}::float, t.{lat_col}::float)::geography,
            road.geom::geography)::numeric, 1)"""
        params = {"pattern": f"%{kwargs['road_name']}%", "radius": kwargs["radius_m"]}

    road_cte = ""
    road_join = ""
    if mode == "road":
        road_cte = """WITH road AS (
            SELECT ST_Union(way) AS geom FROM osm_roads
            WHERE name_th LIKE :pattern AND highway IN ('motorway','trunk','primary','secondary')
        )"""
        road_join = "CROSS JOIN road"

    sql = f"""
        {road_cte}
        SELECT {id_expr} AS asset_id,
               {price_expr} AS price_baht,
               {type_expr} AS ptype,
               t.{lat_col}::float AS lat, t.{lon_col}::float AS lon,
               {dist} AS dist_m
        FROM {table} t {road_join}
        WHERE t.{lat_col} IS NOT NULL AND t.{lon_col} IS NOT NULL
          AND {where}
        ORDER BY dist_m LIMIT 50
    """

    try:
        with _engine().connect() as conn:
            rows = conn.execute(text(sql), params).mappings().all()
    except Exception:
        return []

    results = []
    for r in rows:
        price = float(r["price_baht"]) if r["price_baht"] else None
        ptype = _classify_type(str(r["ptype"] or ""))
        results.append(NpaProperty(
            source=name, asset_id=str(r["asset_id"]),
            price_baht=price, property_type=ptype,
            lat=float(r["lat"]), lon=float(r["lon"]),
            dist_m=float(r["dist_m"]),
            unit="sqm" if ptype == "condo" else "sqw",
        ))
    return results


# --- Market Queries ---

def find_market_comps(lat: float, lon: float, radius_m: float = 2000,
                      area_keywords: list[str] | None = None) -> list[MarketComp]:
    """Find market listings from DDProperty, PropertyHub, Hipflat."""
    results: list[MarketComp] = []
    results.extend(_query_ddproperty(lat, lon, radius_m, area_keywords))
    results.extend(_query_propertyhub(lat, lon, radius_m))
    results.extend(_query_hipflat(lat, lon, radius_m))
    return results


def _query_ddproperty(lat: float, lon: float, radius_m: float,
                      area_keywords: list[str] | None = None) -> list[MarketComp]:
    """Query DDProperty listings — GPS first, address text fallback."""
    results = []

    # Try GPS-based query first
    with _engine().connect() as conn:
        rows = conn.execute(text("""
            SELECT dl.id, dl.price_thb, dl.sqm, dl.price_per_sqm,
                   dl.bedrooms, dl.full_address, dl.latitude, dl.longitude,
                   round(ST_Distance(
                       ST_MakePoint(dl.longitude, dl.latitude)::geography,
                       ST_MakePoint(:lon, :lat)::geography
                   )::numeric, 1) AS dist_m
            FROM ddproperty_listings dl
            WHERE dl.is_active = true AND dl.listing_type = 'sale'
              AND dl.latitude IS NOT NULL AND dl.longitude IS NOT NULL
              AND ST_DWithin(
                  ST_MakePoint(dl.longitude, dl.latitude)::geography,
                  ST_MakePoint(:lon, :lat)::geography, :radius)
            ORDER BY dist_m LIMIT 50
        """), {"lat": lat, "lon": lon, "radius": radius_m}).mappings().all()
        results.extend(_dd_rows_to_comps(rows))

    # Fallback: address text matching if GPS gave < 5 results
    if len(results) < 5 and area_keywords:
        conditions = " OR ".join([f"dl.full_address ILIKE :kw{i}" for i in range(len(area_keywords))])
        params = {f"kw{i}": f"%{kw}%" for i, kw in enumerate(area_keywords)}
        with _engine().connect() as conn:
            rows = conn.execute(text(f"""
                SELECT dl.id, dl.price_thb, dl.sqm, dl.price_per_sqm,
                       dl.bedrooms, dl.full_address, dl.latitude, dl.longitude,
                       NULL::numeric AS dist_m
                FROM ddproperty_listings dl
                WHERE dl.is_active = true AND dl.listing_type = 'sale'
                  AND ({conditions})
                ORDER BY dl.price_thb LIMIT 50
            """), params).mappings().all()
            existing_ids = {r.listing_id for r in results}
            for comp in _dd_rows_to_comps(rows):
                if comp.listing_id not in existing_ids:
                    results.append(comp)
    return results


def _dd_rows_to_comps(rows) -> list[MarketComp]:
    comps = []
    for r in rows:
        price = float(r["price_thb"]) if r["price_thb"] else None
        sqm = float(r["sqm"]) if r["sqm"] else None
        addr = r["full_address"] or ""
        ptype = _classify_market_listing(addr, sqm, r.get("bedrooms"))
        unit = "sqm" if ptype == "condo" else "sqw"
        area_sqw = round(sqm / 4, 1) if sqm and ptype != "condo" else None
        ppu = None
        if price and sqm and ptype == "condo":
            ppu = round(price / sqm, 0)
        elif price and area_sqw and ptype != "condo":
            ppu = round(price / area_sqw, 0)
        comps.append(MarketComp(
            source="DDProperty", listing_id=str(r["id"]),
            price_baht=price, area_sqm=sqm, area_sqw=area_sqw,
            property_type=ptype, bedrooms=r.get("bedrooms"),
            dist_m=float(r["dist_m"]) if r["dist_m"] else None,
            address=addr, price_per_unit=ppu, unit=unit,
        ))
    return comps


def _query_propertyhub(lat: float, lon: float, radius_m: float) -> list[MarketComp]:
    try:
        with _engine().connect() as conn:
            rows = conn.execute(text("""
                SELECT pl.id, pp.name, pl.price_thb, pl.area_sqm, pl.price_per_sqm,
                       pl.bedrooms, pl.bathrooms, pl.post_type,
                       pp.lat, pp.lng,
                       round(ST_Distance(
                           ST_MakePoint(pp.lng, pp.lat)::geography,
                           ST_MakePoint(:lon, :lat)::geography
                       )::numeric, 1) AS dist_m
                FROM propertyhub_listings pl
                JOIN propertyhub_projects pp ON pp.id = pl.project_id
                WHERE pl.is_active = true AND pl.post_type = 'FOR_SALE'
                  AND pp.lat IS NOT NULL AND pp.lng IS NOT NULL
                  AND ST_DWithin(
                      ST_MakePoint(pp.lng, pp.lat)::geography,
                      ST_MakePoint(:lon, :lat)::geography, :radius)
                ORDER BY dist_m LIMIT 50
            """), {"lat": lat, "lon": lon, "radius": radius_m}).mappings().all()
    except Exception:
        return []

    comps = []
    for r in rows:
        price = float(r["price_thb"]) if r["price_thb"] else None
        sqm = float(r["area_sqm"]) if r["area_sqm"] else None
        name = r["name"] or ""
        ptype = _classify_market_listing(name, sqm, r.get("bedrooms"))
        unit = "sqm" if ptype == "condo" else "sqw"
        area_sqw = round(sqm / 4, 1) if sqm and ptype != "condo" else None
        ppu = None
        if price and sqm and ptype == "condo":
            ppu = round(price / sqm, 0)
        elif price and area_sqw:
            ppu = round(price / area_sqw, 0)
        comps.append(MarketComp(
            source="PropertyHub", listing_id=str(r["id"]),
            price_baht=price, area_sqm=sqm, area_sqw=area_sqw,
            property_type=ptype, bedrooms=r.get("bedrooms"),
            dist_m=float(r["dist_m"]) if r["dist_m"] else None,
            address=name, price_per_unit=ppu, unit=unit,
        ))
    return comps


def _query_hipflat(lat: float, lon: float, radius_m: float) -> list[MarketComp]:
    try:
        with _engine().connect() as conn:
            rows = conn.execute(text("""
                SELECT hp.uuid, hp.name_th, hp.avg_sale_sqm,
                       hp.sale_price_min, hp.sale_price_max,
                       hp.lat, hp.lng,
                       round(ST_Distance(
                           ST_MakePoint(hp.lng, hp.lat)::geography,
                           ST_MakePoint(:lon, :lat)::geography
                       )::numeric, 1) AS dist_m
                FROM hipflat_projects hp
                WHERE hp.lat IS NOT NULL AND hp.lng IS NOT NULL
                  AND hp.sale_price_min IS NOT NULL
                  AND ST_DWithin(
                      ST_MakePoint(hp.lng, hp.lat)::geography,
                      ST_MakePoint(:lon, :lat)::geography, :radius)
                ORDER BY dist_m LIMIT 30
            """), {"lat": lat, "lon": lon, "radius": radius_m}).mappings().all()
    except Exception:
        return []

    comps = []
    for r in rows:
        price_min = float(r["sale_price_min"]) if r["sale_price_min"] else None
        price_max = float(r["sale_price_max"]) if r["sale_price_max"] else None
        mid = (price_min + price_max) / 2 if price_min and price_max else price_min
        name = r["name_th"] or ""
        ptype = _classify_market_listing(name, None, None)
        comps.append(MarketComp(
            source="Hipflat", listing_id=str(r["uuid"]),
            price_baht=mid, property_type=ptype,
            dist_m=float(r["dist_m"]) if r["dist_m"] else None,
            address=name, unit="project",
        ))
    return comps


# --- Classification ---

CONDO_KEYWORDS = ("ห้องชุด", "คอนโด", "condo", "อาคารชุด", "ดีคอนโด", "เอสเซ็นท์", "ลุมพินี",
                  "ศุภาลัย", "แอสปาย", "ไลฟ์", "เดอะไลน์", "ไอดีโอ", "นิช", "พลัม")
LAND_KEYWORDS = ("ที่ดิน", "ที่ดินเปล่า", "land")


def _classify_type(type_text: str) -> str:
    t = type_text.lower()
    for kw in CONDO_KEYWORDS:
        if kw.lower() in t:
            return "condo"
    for kw in LAND_KEYWORDS:
        if kw.lower() in t and "สิ่งปลูกสร้าง" not in t:
            return "land"
    if "สิ่งปลูกสร้าง" in t or "บ้าน" in t or "อาคาร" in t or "ทาวน์" in t:
        return "land_building"
    return "land_building"


def _classify_market_listing(text: str, sqm: float | None, bedrooms: int | None) -> str:
    t = text.lower()
    for kw in CONDO_KEYWORDS:
        if kw.lower() in t:
            return "condo"
    if "บ้าน" in t or "ทาวน์" in t or "house" in t.lower():
        return "land_building"
    if "ที่ดิน" in t or "land" in t:
        return "land"
    # Size-based heuristic: small units with few bedrooms = condo
    if sqm and sqm <= 60 and bedrooms and bedrooms <= 2:
        return "condo"
    if sqm and sqm >= 80:
        return "land_building"
    # No clear signal — default to land_building (safer for provincial markets)
    return "land_building"


# --- Comparison ---

def compare_npa_vs_market(npa_list: list[NpaProperty],
                          market_list: list[MarketComp]) -> list[ComparisonResult]:
    """Compare NPA properties against market comps, grouped by property type."""
    # Group market by type and compute stats
    market_by_type: dict[str, list[float]] = {}
    for m in market_list:
        if m.price_baht and m.price_baht > 0:
            market_by_type.setdefault(m.property_type, []).append(m.price_baht)

    results = []
    for npa in npa_list:
        ptype = npa.property_type
        prices = market_by_type.get(ptype, [])
        # Also try broader match
        if not prices and ptype == "land_building":
            prices = market_by_type.get("land_building", []) or market_by_type.get("land", [])
        if not prices and ptype == "condo":
            prices = market_by_type.get("condo", [])

        if prices and npa.price_baht:
            med = statistics.median(prices)
            discount = round((med - npa.price_baht) / med * 100, 1) if med > 0 else None
            rating = _rate_discount(discount)
            results.append(ComparisonResult(
                npa=npa, market_count=len(prices),
                market_min=min(prices), market_median=round(med, 0),
                market_max=max(prices),
                discount_pct=discount, rating=rating,
            ))
        else:
            results.append(ComparisonResult(npa=npa))

    results.sort(key=lambda r: r.discount_pct or -999, reverse=True)
    return results


def _rate_discount(discount: float | None) -> str:
    if discount is None:
        return "NO_COMP"
    if discount >= 40:
        return "DEEP_DISCOUNT"
    if discount >= 20:
        return "GOOD_DEAL"
    if discount >= 0:
        return "FAIR"
    return "OVERPRICED"


# --- Output ---

def _fmt_price(v: float | None) -> str:
    if v is None:
        return "-"
    if v >= 1_000_000:
        return f"{v / 1_000_000:.2f}M"
    if v >= 1_000:
        return f"{v / 1_000:.0f}K"
    return f"{v:.0f}"


def _fmt_area(npa: NpaProperty) -> str:
    if npa.property_type == "condo" and npa.area_sqm:
        return f"{npa.area_sqm:.0f}sqm"
    if npa.area_sqw:
        return f"{npa.area_sqw:.0f}sqw"
    return "-"


def format_table(results: list[ComparisonResult], market_list: list[MarketComp]) -> str:
    lines = []

    # Header
    lines.append("=" * 120)
    lines.append("NPA vs MARKET COMPARISON")
    lines.append("=" * 120)

    # Market summary
    by_source: dict[str, int] = {}
    for m in market_list:
        by_source[m.source] = by_source.get(m.source, 0) + 1
    market_summary = ", ".join(f"{s}: {c}" for s, c in sorted(by_source.items()))
    lines.append(f"Market comps: {len(market_list)} listings ({market_summary})")
    lines.append("")

    # Table header
    hdr = f"{'Src':<6} {'Asset ID':<12} {'Type':<14} {'Price':>10} {'Area':>10} {'฿/unit':>10} {'Dist':>7} {'Mkt Med':>10} {'Mkt Range':>20} {'Disc%':>7} {'Rating':<14}"
    lines.append(hdr)
    lines.append("-" * 120)

    for r in results:
        n = r.npa
        mkt_range = f"{_fmt_price(r.market_min)}-{_fmt_price(r.market_max)}" if r.market_min else "-"
        disc = f"{r.discount_pct:+.1f}%" if r.discount_pct is not None else "-"
        ppu_str = f"{n.price_per_unit:,.0f}" if n.price_per_unit else "-"

        line = (f"{n.source:<6} {n.asset_id:<12} {n.property_type:<14} "
                f"{_fmt_price(n.price_baht):>10} {_fmt_area(n):>10} {ppu_str:>10} "
                f"{n.dist_m:>6.0f}m {_fmt_price(r.market_median):>10} "
                f"{mkt_range:>20} {disc:>7} {r.rating:<14}")
        lines.append(line)

    lines.append("-" * 120)
    lines.append(f"Total: {len(results)} NPA properties compared")

    # Highlights
    deep = [r for r in results if r.rating == "DEEP_DISCOUNT"]
    good = [r for r in results if r.rating == "GOOD_DEAL"]
    if deep or good:
        lines.append("")
        lines.append("HIGHLIGHTS:")
        for r in deep[:5]:
            lines.append(f"  ** {r.npa.source} {r.npa.asset_id}: {_fmt_price(r.npa.price_baht)} "
                         f"({r.discount_pct:+.1f}% vs market median {_fmt_price(r.market_median)}) "
                         f"— DEEP DISCOUNT")
        for r in good[:5]:
            lines.append(f"  -> {r.npa.source} {r.npa.asset_id}: {_fmt_price(r.npa.price_baht)} "
                         f"({r.discount_pct:+.1f}% vs market median {_fmt_price(r.market_median)}) "
                         f"— Good deal")

    return "\n".join(lines)


def format_json(results: list[ComparisonResult], market_list: list[MarketComp]) -> str:
    return json.dumps({
        "comparisons": [r.model_dump() for r in results],
        "market_comps": [m.model_dump() for m in market_list],
        "summary": {
            "npa_count": len(results),
            "market_count": len(market_list),
            "deep_discounts": len([r for r in results if r.rating == "DEEP_DISCOUNT"]),
            "good_deals": len([r for r in results if r.rating == "GOOD_DEAL"]),
            "fair": len([r for r in results if r.rating == "FAIR"]),
            "overpriced": len([r for r in results if r.rating == "OVERPRICED"]),
            "no_comp": len([r for r in results if r.rating == "NO_COMP"]),
        },
    }, ensure_ascii=False, indent=2, default=str)


# --- Main ---

def run_comparison(lat: float | None = None, lon: float | None = None,
                   asset_id: str | None = None, source: str | None = None,
                   road: str | None = None, radius_m: float = 2000,
                   fmt: str = "table") -> str:
    """Main entry point for comparison. Returns formatted output."""

    # Resolve GPS / query mode
    if road:
        npa_list = find_npa_near_road(road, radius_m)
        if not npa_list:
            return f"No NPA properties found within {radius_m}m of road '{road}'"
        avg_lat = statistics.mean(n.lat for n in npa_list)
        avg_lon = statistics.mean(n.lon for n in npa_list)
        area_keywords = _extract_area_keywords_from_npa(npa_list, avg_lat, avg_lon)
        area_keywords.append(road)
    elif asset_id:
        gps = resolve_gps_from_asset(asset_id, source)
        if not gps:
            return f"Cannot resolve GPS for asset_id={asset_id}"
        lat, lon = gps
        npa_list = find_npa_nearby_point(lat, lon, radius_m)
        area_keywords = None
    elif lat is not None and lon is not None:
        npa_list = find_npa_nearby_point(lat, lon, radius_m)
        area_keywords = None
    else:
        return "Error: provide --lat/--lon, --asset-id, or --road"

    if not npa_list:
        return f"No NPA properties found within {radius_m}m"

    # Extract area keywords from NPA results for DDProperty text fallback
    if not area_keywords:
        area_keywords = _extract_area_keywords(lat, lon)

    # Find market comps
    search_lat = lat if lat else statistics.mean(n.lat for n in npa_list)
    search_lon = lon if lon else statistics.mean(n.lon for n in npa_list)
    market_list = find_market_comps(search_lat, search_lon, radius_m, area_keywords)

    # Compare
    results = compare_npa_vs_market(npa_list, market_list)

    if fmt == "json":
        return format_json(results, market_list)
    return format_table(results, market_list)


def _extract_area_keywords_from_npa(npa_list: list[NpaProperty],
                                     lat: float, lon: float) -> list[str]:
    """Extract district/province keywords from NPA results + nearby context."""
    keywords = set()

    # From LED properties table (has ampur/province)
    asset_ids = [n.asset_id for n in npa_list if n.source == "LED"]
    if asset_ids:
        placeholders = ",".join(f":a{i}" for i in range(min(len(asset_ids), 20)))
        params = {f"a{i}": aid for i, aid in enumerate(asset_ids[:20])}
        with _engine().connect() as conn:
            rows = conn.execute(text(f"""
                SELECT DISTINCT p.ampur, p.source_name
                FROM properties p
                WHERE p.asset_id IN ({placeholders})
            """), params).mappings().all()
            for r in rows:
                if r["ampur"]:
                    keywords.add(r["ampur"])
                sn = r["source_name"] or ""
                if sn.startswith("LED_"):
                    prov = sn[4:].split()[0].strip()
                    keywords.add(prov)

    # From led_land_parcels (has amphur_name)
    if asset_ids:
        with _engine().connect() as conn:
            rows = conn.execute(text(f"""
                SELECT DISTINCT amphur_name, province_name
                FROM led_land_parcels
                WHERE asset_id IN ({placeholders})
                  AND amphur_name IS NOT NULL
            """), params).mappings().all()
            for r in rows:
                if r["amphur_name"]:
                    keywords.add(r["amphur_name"])
                if r["province_name"]:
                    keywords.add(r["province_name"])

    # From led_land_parcels by GPS proximity (always works regardless of NPA list)
    with _engine().connect() as conn:
        rows = conn.execute(text("""
            SELECT DISTINCT amphur_name, province_name
            FROM led_land_parcels
            WHERE lat IS NOT NULL
              AND ST_DWithin(
                  ST_MakePoint(lon, lat)::geography,
                  ST_MakePoint(:lon, :lat)::geography, 5000)
            LIMIT 10
        """), {"lat": lat, "lon": lon}).mappings().all()
        for r in rows:
            if r["amphur_name"]:
                keywords.add(r["amphur_name"])
            if r["province_name"]:
                keywords.add(r["province_name"])

    # From nearest main road name
    with _engine().connect() as conn:
        row = conn.execute(text("""
            SELECT name_th FROM osm_roads
            WHERE highway IN ('motorway','trunk','primary','secondary')
              AND name_th IS NOT NULL
              AND ST_DWithin(way::geography, ST_MakePoint(:lon, :lat)::geography, 2000)
            ORDER BY ST_Distance(way::geography, ST_MakePoint(:lon, :lat)::geography)
            LIMIT 1
        """), {"lat": lat, "lon": lon}).mappings().first()
        if row and row["name_th"]:
            rn = row["name_th"].replace("ถนน", "").strip()
            keywords.add(rn)

    return list(keywords) if keywords else []


def _extract_area_keywords(lat: float, lon: float) -> list[str]:
    """Extract area keywords from GPS point (for non-road modes)."""
    npa = find_npa_nearby_point(lat, lon, radius_m=5000)[:20]
    return _extract_area_keywords_from_npa(npa, lat, lon)


def main():
    parser = argparse.ArgumentParser(description="Compare NPA prices vs market listings")

    # Input modes
    parser.add_argument("--lat", type=float, help="Latitude")
    parser.add_argument("--lon", type=float, help="Longitude")
    parser.add_argument("--asset-id", help="Resolve GPS from asset ID")
    parser.add_argument("--source", help="Provider name for asset-id lookup (LED, BAM, etc)")
    parser.add_argument("--road", help="Road name to search near (Thai)")

    # Options
    parser.add_argument("--radius", type=float, default=2000, help="Search radius in meters")
    parser.add_argument("--format", choices=["table", "json"], default="table", help="Output format")

    args = parser.parse_args()
    print(run_comparison(
        lat=args.lat, lon=args.lon,
        asset_id=args.asset_id, source=args.source,
        road=args.road, radius_m=args.radius, fmt=args.format,
    ))


if __name__ == "__main__":
    main()

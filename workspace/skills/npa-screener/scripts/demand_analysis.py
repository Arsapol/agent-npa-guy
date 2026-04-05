"""
Area Demand Analysis — Spatial demand/supply assessment around NPA candidates.

For each candidate, queries:
1. Nearby market projects within 1km (Hipflat/PropertyHub)
2. NPA concentration from all 6 providers within 1km
3. Rent-to-sale ratio, YoY trends, supply pressure at area level

Usage:
    python demand_analysis.py                    # Analyze all BUY candidates from latest screening
    python demand_analysis.py --lat 13.76 --lon 100.57 --name "Test"  # Single point
"""

import json
import math
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

import psycopg2
import psycopg2.extras

DB_URL = os.getenv("DATABASE_URL", "postgresql://arsapolm@localhost:5432/npa_kb")
RADIUS_M = 1000  # 1km radius


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6_371_000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


# Approximate bounding box for SQL pre-filter (faster than computing haversine on all rows)
def bbox(lat: float, lon: float, radius_m: float) -> tuple[float, float, float, float]:
    """Returns (min_lat, max_lat, min_lon, max_lon) for a bounding box."""
    dlat = radius_m / 111_320
    dlon = radius_m / (111_320 * math.cos(math.radians(lat)))
    return (lat - dlat, lat + dlat, lon - dlon, lon + dlon)


@dataclass
class AreaDemand:
    name: str
    lat: float
    lon: float
    radius_m: int = RADIUS_M

    # Nearby market projects (Hipflat)
    hipflat_projects_count: int = 0
    hipflat_total_units: int = 0
    hipflat_total_for_sale: int = 0
    hipflat_total_for_rent: int = 0
    hipflat_avg_sale_sqm: Optional[float] = None
    hipflat_avg_yoy_pct: Optional[float] = None
    hipflat_trend_up: int = 0
    hipflat_trend_down: int = 0
    hipflat_trend_flat: int = 0

    # PropertyHub nearby
    ph_projects_count: int = 0
    ph_total_for_sale: int = 0
    ph_total_for_rent: int = 0

    # Area-level metrics
    area_supply_pressure_pct: Optional[float] = None  # total_for_sale / total_units
    area_rent_to_sale_ratio: Optional[float] = None    # total_for_rent / total_for_sale
    area_rental_saturation_pct: Optional[float] = None  # total_for_rent / total_units

    # NPA concentration (all 6 providers)
    npa_condos_nearby: int = 0
    npa_by_provider: dict = field(default_factory=dict)
    npa_total_value: float = 0

    # Verdict
    demand_signal: str = ""  # STRONG / MODERATE / WEAK / DEAD
    demand_reasons: list = field(default_factory=list)


def analyze_area(conn, lat: float, lon: float, name: str, radius_m: int = RADIUS_M) -> AreaDemand:
    result = AreaDemand(name=name, lat=lat, lon=lon, radius_m=radius_m)
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    min_lat, max_lat, min_lon, max_lon = bbox(lat, lon, radius_m)

    # --- 1. Hipflat nearby projects ---
    cur.execute("""
        SELECT name_th, name_en, lat, lng,
               total_units, units_for_sale, units_for_rent,
               avg_sale_sqm, yoy_change_pct, price_trend,
               year_completed
        FROM hipflat_projects
        WHERE lat BETWEEN %s AND %s
          AND lng BETWEEN %s AND %s
          AND lat IS NOT NULL AND lng IS NOT NULL
    """, (min_lat, max_lat, min_lon, max_lon))

    hipflat_rows = []
    for row in cur.fetchall():
        dist = haversine_m(lat, lon, float(row["lat"]), float(row["lng"]))
        if dist <= radius_m:
            hipflat_rows.append({**dict(row), "dist_m": dist})

    result.hipflat_projects_count = len(hipflat_rows)
    if hipflat_rows:
        result.hipflat_total_units = sum(r.get("total_units") or 0 for r in hipflat_rows)
        result.hipflat_total_for_sale = sum(r.get("units_for_sale") or 0 for r in hipflat_rows)
        result.hipflat_total_for_rent = sum(r.get("units_for_rent") or 0 for r in hipflat_rows)

        sale_prices = [r["avg_sale_sqm"] for r in hipflat_rows if r.get("avg_sale_sqm")]
        if sale_prices:
            result.hipflat_avg_sale_sqm = sum(sale_prices) / len(sale_prices)

        yoy_vals = [float(r["yoy_change_pct"]) for r in hipflat_rows if r.get("yoy_change_pct") is not None]
        if yoy_vals:
            result.hipflat_avg_yoy_pct = sum(yoy_vals) / len(yoy_vals)

        for r in hipflat_rows:
            trend = (r.get("price_trend") or "").lower()
            if "ขึ้น" in trend or "up" in trend:
                result.hipflat_trend_up += 1
            elif "ลง" in trend or "down" in trend:
                result.hipflat_trend_down += 1
            else:
                result.hipflat_trend_flat += 1

    # --- 2. PropertyHub nearby projects ---
    cur.execute("""
        SELECT name, lat, lng,
               listing_count_sale, listing_count_rent
        FROM propertyhub_projects
        WHERE lat::numeric BETWEEN %s AND %s
          AND lng::numeric BETWEEN %s AND %s
          AND lat IS NOT NULL AND lng IS NOT NULL
    """, (min_lat, max_lat, min_lon, max_lon))

    ph_rows = []
    for row in cur.fetchall():
        try:
            rlat, rlng = float(row["lat"]), float(row["lng"])
        except (TypeError, ValueError):
            continue
        dist = haversine_m(lat, lon, rlat, rlng)
        if dist <= radius_m:
            ph_rows.append({**dict(row), "dist_m": dist})

    result.ph_projects_count = len(ph_rows)
    if ph_rows:
        result.ph_total_for_sale = sum(r.get("listing_count_sale") or 0 for r in ph_rows)
        result.ph_total_for_rent = sum(r.get("listing_count_rent") or 0 for r in ph_rows)

    # --- 3. NPA concentration (all providers with GPS) ---
    npa_queries = [
        ("SAM", """
            SELECT 'SAM' as src, sam_id::text as id, price_baht as price
            FROM sam_properties
            WHERE type_name = 'ห้องชุดพักอาศัย'
              AND lat BETWEEN %s AND %s AND lng BETWEEN %s AND %s
        """, "lat", "lng"),
        ("BAM", """
            SELECT 'BAM' as src, asset_no::text as id, COALESCE(discount_price, sell_price) as price
            FROM bam_properties
            WHERE asset_type = 'ห้องชุดพักอาศัย'
              AND lat BETWEEN %s AND %s AND lon BETWEEN %s AND %s
        """, "lat", "lon"),
        ("JAM", """
            SELECT 'JAM' as src, asset_id::text as id, COALESCE(discount, selling) as price
            FROM jam_properties
            WHERE type_asset_th = 'คอนโดมิเนียม'
              AND lat BETWEEN %s AND %s AND lon BETWEEN %s AND %s
        """, "lat", "lon"),
        ("KTB", """
            SELECT 'KTB' as src, coll_grp_id::text as id, COALESCE(nml_price, price) as price
            FROM ktb_properties
            WHERE coll_type_name = 'คอนโดมีเนียม/ห้องชุด'
              AND lat BETWEEN %s AND %s AND lon BETWEEN %s AND %s
        """, "lat", "lon"),
        ("KBANK", """
            SELECT 'KBANK' as src, property_id::text as id, COALESCE(promotion_price, sell_price) as price
            FROM kbank_properties
            WHERE property_type_code = '05'
              AND lat BETWEEN %s AND %s AND lon BETWEEN %s AND %s
        """, "lat", "lon"),
    ]

    npa_nearby = []
    for provider, query, lat_col, lon_col in npa_queries:
        cur.execute(query, (min_lat, max_lat, min_lon, max_lon))
        for row in cur.fetchall():
            npa_nearby.append(dict(row))

    result.npa_condos_nearby = len(npa_nearby)
    result.npa_total_value = sum(float(r.get("price") or 0) for r in npa_nearby)
    for r in npa_nearby:
        src = r["src"]
        result.npa_by_provider[src] = result.npa_by_provider.get(src, 0) + 1

    # --- 4. Compute area metrics ---
    total_units = result.hipflat_total_units
    total_for_sale = result.hipflat_total_for_sale + result.ph_total_for_sale
    total_for_rent = result.hipflat_total_for_rent + result.ph_total_for_rent

    if total_units > 0:
        result.area_supply_pressure_pct = result.hipflat_total_for_sale / total_units * 100
        result.area_rental_saturation_pct = result.hipflat_total_for_rent / total_units * 100

    if total_for_sale > 0:
        result.area_rent_to_sale_ratio = total_for_rent / total_for_sale

    # --- 5. Demand verdict ---
    reasons = []

    # YoY trend (BKK condo market typically -5% to +5%)
    if result.hipflat_avg_yoy_pct is not None:
        if result.hipflat_avg_yoy_pct > 3:
            reasons.append(f"STRONG: area prices rising +{result.hipflat_avg_yoy_pct:.1f}% YoY")
        elif result.hipflat_avg_yoy_pct > 0:
            reasons.append(f"OK: area prices stable +{result.hipflat_avg_yoy_pct:.1f}% YoY")
        elif result.hipflat_avg_yoy_pct > -5:
            reasons.append(f"WEAK: area prices softening {result.hipflat_avg_yoy_pct:.1f}% YoY")
        else:
            reasons.append(f"BAD: area prices falling sharply {result.hipflat_avg_yoy_pct:.1f}% YoY")

    # Rent-to-sale ratio
    if result.area_rent_to_sale_ratio is not None:
        if result.area_rent_to_sale_ratio >= 3:
            reasons.append(f"STRONG: rent-to-sale ratio {result.area_rent_to_sale_ratio:.1f}x (rental market active)")
        elif result.area_rent_to_sale_ratio >= 1.5:
            reasons.append(f"OK: rent-to-sale ratio {result.area_rent_to_sale_ratio:.1f}x")
        elif result.area_rent_to_sale_ratio >= 0.5:
            reasons.append(f"WEAK: rent-to-sale ratio {result.area_rent_to_sale_ratio:.1f}x (more sellers than renters)")
        else:
            reasons.append(f"BAD: rent-to-sale ratio {result.area_rent_to_sale_ratio:.1f}x (owners dumping)")

    # Area supply pressure
    if result.area_supply_pressure_pct is not None:
        if result.area_supply_pressure_pct <= 5:
            reasons.append(f"STRONG: area supply pressure {result.area_supply_pressure_pct:.1f}% (tight)")
        elif result.area_supply_pressure_pct <= 10:
            reasons.append(f"OK: area supply pressure {result.area_supply_pressure_pct:.1f}%")
        elif result.area_supply_pressure_pct <= 15:
            reasons.append(f"WEAK: area supply pressure {result.area_supply_pressure_pct:.1f}% (oversupplied)")
        else:
            reasons.append(f"BAD: area supply pressure {result.area_supply_pressure_pct:.1f}% (glut)")

    # NPA concentration (calibrated to BKK avg ~214 per 1km circle)
    if result.npa_condos_nearby > 400:
        reasons.append(f"BAD: {result.npa_condos_nearby} NPA condos within 1km (hotspot, 2x avg)")
    elif result.npa_condos_nearby > 250:
        reasons.append(f"WEAK: {result.npa_condos_nearby} NPA condos within 1km (above avg)")
    elif result.npa_condos_nearby > 100:
        reasons.append(f"OK: {result.npa_condos_nearby} NPA condos within 1km (normal BKK density)")
    else:
        reasons.append(f"STRONG: only {result.npa_condos_nearby} NPA condos within 1km (below avg)")

    # Trend direction
    if result.hipflat_projects_count > 0:
        up_pct = result.hipflat_trend_up / result.hipflat_projects_count * 100
        down_pct = result.hipflat_trend_down / result.hipflat_projects_count * 100
        if up_pct >= 60:
            reasons.append(f"STRONG: {result.hipflat_trend_up}/{result.hipflat_projects_count} projects trending up")
        elif down_pct >= 60:
            reasons.append(f"BAD: {result.hipflat_trend_down}/{result.hipflat_projects_count} projects trending down")

    result.demand_reasons = reasons

    # Overall signal
    strong = sum(1 for r in reasons if r.startswith("STRONG"))
    bad = sum(1 for r in reasons if r.startswith("BAD"))
    weak = sum(1 for r in reasons if r.startswith("WEAK"))

    if bad >= 2:
        result.demand_signal = "DEAD"
    elif bad >= 1 or weak >= 2:
        result.demand_signal = "WEAK"
    elif strong >= 3:
        result.demand_signal = "STRONG"
    else:
        result.demand_signal = "MODERATE"

    cur.close()
    return result


def format_demand_report(analyses: list[AreaDemand]) -> str:
    lines = [
        f"# Area Demand Analysis — {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "## Summary",
        "",
        "| Property | Demand | Area Supply | Rent:Sale | YoY | NPA Nearby | Projects (1km) | Total Units |",
        "|----------|--------|-------------|-----------|-----|------------|----------------|-------------|",
    ]

    for a in analyses:
        sp = f"{a.area_supply_pressure_pct:.0f}%" if a.area_supply_pressure_pct is not None else "?"
        rs = f"{a.area_rent_to_sale_ratio:.1f}x" if a.area_rent_to_sale_ratio is not None else "?"
        yoy = f"{a.hipflat_avg_yoy_pct:+.1f}%" if a.hipflat_avg_yoy_pct is not None else "?"
        lines.append(
            f"| {a.name} | **{a.demand_signal}** | {sp} | {rs} | {yoy} | "
            f"{a.npa_condos_nearby} | {a.hipflat_projects_count} | {a.hipflat_total_units:,} |"
        )

    lines += ["", "## Detail", ""]

    for a in analyses:
        lines += [
            f"### {a.name}",
            f"- **Demand signal:** {a.demand_signal}",
            f"- **GPS:** {a.lat}, {a.lon} (radius {a.radius_m}m)",
            "",
            "**Market Projects Nearby (Hipflat)**",
            f"- Projects: {a.hipflat_projects_count}",
            f"- Total units: {a.hipflat_total_units:,}",
            f"- For sale: {a.hipflat_total_for_sale:,}",
            f"- For rent: {a.hipflat_total_for_rent:,}",
            f"- Avg sale price: ฿{a.hipflat_avg_sale_sqm:,.0f}/sqm" if a.hipflat_avg_sale_sqm else "- Avg sale price: N/A",
            f"- Avg YoY: {a.hipflat_avg_yoy_pct:+.1f}%" if a.hipflat_avg_yoy_pct is not None else "- Avg YoY: N/A",
            f"- Trends: {a.hipflat_trend_up} up / {a.hipflat_trend_flat} flat / {a.hipflat_trend_down} down",
            "",
            "**PropertyHub Nearby**",
            f"- Projects: {a.ph_projects_count}",
            f"- For sale: {a.ph_total_for_sale:,}",
            f"- For rent: {a.ph_total_for_rent:,}",
            "",
            "**Area Metrics**",
            f"- Supply pressure: {a.area_supply_pressure_pct:.1f}%" if a.area_supply_pressure_pct is not None else "- Supply pressure: N/A",
            f"- Rent-to-sale ratio: {a.area_rent_to_sale_ratio:.1f}x" if a.area_rent_to_sale_ratio is not None else "- Rent-to-sale ratio: N/A",
            f"- Rental saturation: {a.area_rental_saturation_pct:.1f}%" if a.area_rental_saturation_pct is not None else "- Rental saturation: N/A",
            "",
            "**NPA Concentration**",
            f"- Total NPA condos within 1km: {a.npa_condos_nearby}",
            f"- By provider: {a.npa_by_provider}" if a.npa_by_provider else "- By provider: none",
            f"- Total NPA value: ฿{a.npa_total_value:,.0f}" if a.npa_total_value > 0 else "- Total NPA value: ฿0",
            "",
            "**Demand Signals**",
        ]
        for r in a.demand_reasons:
            lines.append(f"- {r}")
        lines.append("")

    return "\n".join(lines)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Area Demand Analysis")
    parser.add_argument("--lat", type=float, help="Latitude")
    parser.add_argument("--lon", type=float, help="Longitude")
    parser.add_argument("--name", type=str, help="Property name")
    parser.add_argument("--radius", type=int, default=RADIUS_M, help="Radius in meters")
    parser.add_argument("--from-screening", type=str, help="Path to screening JSON")
    args = parser.parse_args()

    conn = psycopg2.connect(DB_URL)
    analyses = []

    if args.lat and args.lon:
        result = analyze_area(conn, args.lat, args.lon, args.name or "Custom", args.radius)
        analyses.append(result)
    else:
        # Load BUY candidates from latest screening
        screening_path = args.from_screening or str(
            Path(__file__).parent.parent.parent.parent / "output" / "npa-screening-2026-04-05.json"
        )
        with open(screening_path) as f:
            data = json.load(f)

        buys = [d for d in data if d["verdict"] in ("BUY", "WATCH") and d.get("score", 0) >= 60]
        # Deduplicate by project name (take highest score)
        seen = set()
        unique_buys = []
        for b in buys:
            key = b.get("project_name", "")[:30]
            if key not in seen and b.get("lat") and b.get("lon"):
                seen.add(key)
                unique_buys.append(b)

        print(f"Analyzing demand for {len(unique_buys)} candidates...\n")
        for b in unique_buys:
            name = b.get("project_name", b.get("source_id", "?"))
            if len(name) > 40:
                name = name[:40]
            print(f"  → {name}...", flush=True)
            result = analyze_area(conn, b["lat"], b["lon"], name, args.radius)
            analyses.append(result)

    # Output
    report = format_demand_report(analyses)
    output_dir = Path(__file__).parent.parent.parent.parent / "output"
    date_str = datetime.now().strftime("%Y-%m-%d")
    report_path = output_dir / f"demand-analysis-{date_str}.md"
    report_path.write_text(report)
    print(f"\n✓ Report: {report_path}")

    # Print summary to stdout
    print("\n" + "=" * 70)
    for a in analyses:
        sp = f"{a.area_supply_pressure_pct:.0f}%" if a.area_supply_pressure_pct is not None else "?"
        rs = f"{a.area_rent_to_sale_ratio:.1f}x" if a.area_rent_to_sale_ratio is not None else "?"
        print(f"  {a.demand_signal:8s} | {a.name[:35]:35s} | supply:{sp:>4s} | rent:sale:{rs:>5s} | NPA:{a.npa_condos_nearby:>3d}")
    print("=" * 70)

    conn.close()


if __name__ == "__main__":
    main()

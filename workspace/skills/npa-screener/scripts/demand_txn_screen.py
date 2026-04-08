"""
Transaction-Velocity NPA Screener — Find NPA in districts where properties ACTUALLY SELL.

Uses LED auction "ขายแล้ว" (sold) data to identify districts with highest sell-through rates,
then finds available NPA inventory across ALL providers and property types in those districts.

This surfaces affordable houses/townhouses in outer BKK that the condo-focused screener misses.

Demand signals:
  - LED sell-through rate (% of auctions that resulted in sale)
  - Transaction volume (absolute number of sales)
  - Recent transaction velocity (sales in last 12 months)
  - Price band analysis (which price ranges actually sell)

Usage:
    python demand_txn_screen.py
    python demand_txn_screen.py --min-sell-pct 10 --min-sold 5
    python demand_txn_screen.py --property-types townhouse,house --json
    python demand_txn_screen.py --max-price 5000000 --province กรุงเทพมหานคร
"""

import argparse
import json
import math
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

import psycopg2
import psycopg2.extras

DB_URL = os.getenv("DATABASE_URL", "postgresql://arsapolm@localhost:5432/npa_kb")

VERIFIED_SALE_MULTIPLIER = 0.92
TARGET_PROVINCES = ["กรุงเทพมหานคร", "ปทุมธานี", "สมุทรปราการ", "นนทบุรี"]


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------


@dataclass
class HotDistrict:
    """A district with high transaction velocity from LED auction data."""
    province: str
    district: str
    sold_total: int
    sold_recent: int  # last 12 months
    unsold: int
    total: int
    sell_through_pct: float
    # Price band breakdown
    sold_under_1m: int = 0
    sold_1m_3m: int = 0
    sold_3m_5m: int = 0
    sold_5m_10m: int = 0
    sold_over_10m: int = 0
    # Property type breakdown
    sold_condo: int = 0
    sold_house: int = 0
    sold_townhouse: int = 0
    sold_land: int = 0
    sold_other: int = 0


@dataclass
class NpaInHotDistrict:
    """An NPA property in a high-transaction district."""
    source: str
    source_id: str
    property_type: str
    project_name: str
    price: float
    size_sqm: Optional[float]
    size_wa: Optional[float]
    bedroom: Optional[int]
    bathroom: Optional[int]
    lat: Optional[float]
    lon: Optional[float]
    province: str
    district: str
    subdistrict: str
    # District context
    hot_district: HotDistrict
    # Computed
    price_sqm: Optional[float] = None
    price_wa: Optional[float] = None
    # Market comparison (if available from Hipflat)
    market_price_sqm: Optional[int] = None
    discount_pct: Optional[float] = None


# ---------------------------------------------------------------------------
# Step 1: Find hot districts from LED transaction data
# ---------------------------------------------------------------------------


def find_hot_districts(
    conn,
    provinces: list[str],
    min_sell_pct: float = 8.0,
    min_sold: int = 3,
) -> list[HotDistrict]:
    """Find districts with highest transaction velocity.

    Combines sold data from 3 providers:
    - LED: sale_status = 'ขายแล้ว' (court auction sales)
    - JAM: status_soldout = true (JAM confirmed sold)
    - KBank: is_sold_out = true (KBank API flag)
    """
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    # Union all sold signals into one temp table
    cur.execute("""
        CREATE TEMP TABLE _sold_properties AS
        -- LED sold
        SELECT p.province, p.ampur as district,
               p.primary_price_satang / 100.0 as price,
               p.property_type as ptype,
               p.updated_at as sold_date,
               'LED' as src
        FROM properties p
        WHERE p.sale_status = 'ขายแล้ว'
          AND p.province = ANY(%s)

        UNION ALL

        -- JAM sold
        SELECT j.province_name, j.amphur_name,
               COALESCE(j.discount, j.selling) as price,
               j.type_asset_th as ptype,
               j.soldout_date::timestamptz as sold_date,
               'JAM' as src
        FROM jam_properties j
        WHERE j.status_soldout = true
          AND j.province_name = ANY(%s)

        UNION ALL

        -- KBank sold
        SELECT kb.province_name, kb.amphur_name,
               COALESCE(kb.promotion_price, kb.sell_price) as price,
               kb.property_type_name as ptype,
               kb.last_scraped_at as sold_date,
               'KBANK' as src
        FROM kbank_properties kb
        WHERE kb.is_sold_out = true
          AND kb.province_name = ANY(%s)
    """, [provinces, provinces, provinces])

    # Also count total inventory per district (LED unsold + JAM active + KBank active)
    cur.execute("""
        WITH sold AS (
            SELECT district, count(*) as sold_total,
                   count(*) FILTER (WHERE sold_date >= now() - interval '12 months') as sold_recent,
                   count(*) FILTER (WHERE price < 1000000) as sold_under_1m,
                   count(*) FILTER (WHERE price BETWEEN 1000000 AND 3000000) as sold_1m_3m,
                   count(*) FILTER (WHERE price BETWEEN 3000001 AND 5000000) as sold_3m_5m,
                   count(*) FILTER (WHERE price BETWEEN 5000001 AND 10000000) as sold_5m_10m,
                   count(*) FILTER (WHERE price > 10000000) as sold_over_10m,
                   count(*) FILTER (WHERE ptype LIKE '%%ห้องชุด%%' OR ptype LIKE '%%คอนโด%%') as sold_condo,
                   count(*) FILTER (WHERE ptype LIKE '%%บ้าน%%' OR ptype LIKE '%%เดี่ยว%%') as sold_house,
                   count(*) FILTER (WHERE ptype LIKE '%%ทาวน์%%') as sold_townhouse,
                   count(*) FILTER (WHERE ptype LIKE '%%ที่ดิน%%' OR ptype LIKE '%%ว่าง%%') as sold_land
            FROM _sold_properties
            GROUP BY district
        ),
        inventory AS (
            -- LED total
            SELECT p.ampur as district, count(*) as cnt
            FROM properties p WHERE p.province = ANY(%s) GROUP BY p.ampur
            UNION ALL
            -- JAM total (not sold)
            SELECT j.amphur_name, count(*) FROM jam_properties j
            WHERE j.province_name = ANY(%s) AND (j.status_soldout IS NULL OR j.status_soldout = false)
            GROUP BY j.amphur_name
            UNION ALL
            -- KBank total (not sold)
            SELECT kb.amphur_name, count(*) FROM kbank_properties kb
            WHERE kb.province_name = ANY(%s) AND (kb.is_sold_out IS NULL OR kb.is_sold_out = false)
            GROUP BY kb.amphur_name
        ),
        inv_agg AS (
            SELECT district, sum(cnt) as total_inventory FROM inventory GROUP BY district
        )
        SELECT s.district,
               COALESCE((SELECT province FROM _sold_properties WHERE district = s.district LIMIT 1), '') as province,
               s.sold_total, s.sold_recent,
               COALESCE(i.total_inventory, 0) as unsold,
               s.sold_total + COALESCE(i.total_inventory, 0) as total,
               s.sold_under_1m, s.sold_1m_3m, s.sold_3m_5m, s.sold_5m_10m, s.sold_over_10m,
               s.sold_condo, s.sold_house, s.sold_townhouse, s.sold_land
        FROM sold s
        LEFT JOIN inv_agg i ON i.district = s.district
        WHERE s.sold_total >= %s
        ORDER BY s.sold_total::float / NULLIF(s.sold_total + COALESCE(i.total_inventory, 0), 0) DESC
    """, [provinces, provinces, provinces, min_sold])

    rows = cur.fetchall()

    # Drop temp table
    cur.execute("DROP TABLE IF EXISTS _sold_properties")

    districts = []
    for row in rows:
        total = row["total"] or 1
        sold = row["sold_total"] or 0
        sell_pct = sold / total * 100

        if sell_pct < min_sell_pct:
            continue

        districts.append(HotDistrict(
            province=row["province"],
            district=row["district"],
            sold_total=sold,
            sold_recent=row["sold_recent"] or 0,
            unsold=row["unsold"] or 0,
            total=total,
            sell_through_pct=sell_pct,
            sold_under_1m=row["sold_under_1m"] or 0,
            sold_1m_3m=row["sold_1m_3m"] or 0,
            sold_3m_5m=row["sold_3m_5m"] or 0,
            sold_5m_10m=row["sold_5m_10m"] or 0,
            sold_over_10m=row["sold_over_10m"] or 0,
            sold_condo=row["sold_condo"] or 0,
            sold_house=row["sold_house"] or 0,
            sold_townhouse=row["sold_townhouse"] or 0,
            sold_land=row["sold_land"] or 0,
            sold_other=sold - (row["sold_condo"] or 0) - (row["sold_house"] or 0)
                       - (row["sold_townhouse"] or 0) - (row["sold_land"] or 0),
        ))

    cur.close()
    return districts


# ---------------------------------------------------------------------------
# Step 2: Find available NPA in hot districts
# ---------------------------------------------------------------------------


from adapter_bridge import search_district as _adapter_search_district, PropertyCategory, ALL_SOURCES

# PropertyCategory → screener type string mapping
_CAT_TO_TYPE = {
    PropertyCategory.CONDO: "condo",
    PropertyCategory.HOUSE: "house",
    PropertyCategory.TOWNHOUSE: "townhouse",
    PropertyCategory.LAND: "land",
    PropertyCategory.COMMERCIAL: "commercial",
    PropertyCategory.FACTORY: "commercial",
    PropertyCategory.OTHER: "other",
}


def find_npa_in_hot_districts(
    conn,
    districts: list[HotDistrict],
    max_price: Optional[float] = None,
    property_types: Optional[list[str]] = None,
) -> list[NpaInHotDistrict]:
    results = []

    district_map = {}
    for d in districts:
        district_map[d.district] = d

    # Query adapter per district (typically 10-20 hot districts)
    seen = set()
    for district_name, hd in district_map.items():
        npa_props = _adapter_search_district(
            district=district_name,
            max_price=max_price,
            sources=ALL_SOURCES,
        )

        for p in npa_props:
            ptype = _CAT_TO_TYPE.get(p.category, "other")
            if property_types and ptype not in property_types:
                continue

            key = f"{p.source.value}-{p.source_id}"
            if key in seen:
                continue
            seen.add(key)

            price = p.best_price_baht or 0
            if price <= 0:
                continue

            sqm = p.size_sqm
            price_sqm = price / sqm if sqm and sqm > 0 else None

            r = NpaInHotDistrict(
                source=p.source.value,
                source_id=p.source_id,
                property_type=ptype,
                project_name=p.project_name or "",
                price=price,
                size_sqm=sqm,
                size_wa=p.size_wa,
                bedroom=p.bedroom,
                bathroom=p.bathroom,
                lat=p.lat,
                lon=p.lon,
                province=p.province or "",
                district=p.district or "",
                subdistrict=p.subdistrict or "",
                hot_district=hd,
                price_sqm=price_sqm,
            )
            # Compute price per wa if land size available
            if p.size_wa and p.size_wa > 0:
                r.price_wa = price / p.size_wa
            results.append(r)

    return results


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------


def format_report(
    districts: list[HotDistrict],
    results: list[NpaInHotDistrict],
    args,
) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    lines = [
        f"# Transaction-Velocity NPA Screening — {now}",
        "",
        "## Approach",
        "Find districts where properties **actually sell** (LED ขายแล้ว data),",
        "then find available NPA inventory in those districts.",
        "",
        "## Parameters",
        f"- Min sell-through: {args.min_sell_pct}%",
        f"- Min sold count: {args.min_sold}",
        f"- Max price: {'฿{:,.0f}'.format(args.max_price) if args.max_price else 'unlimited'}",
        f"- Property types: {args.property_types or 'all'}",
        f"- Provinces: {', '.join(args.provinces)}",
        "",
        "## Hot Districts (by LED sell-through rate)",
        "",
        "| # | Province | District | Sold | Total | Sell% | Recent | <1M | 1-3M | 3-5M | 5-10M | >10M | Condo | House | TH | Land |",
        "|---|----------|----------|------|-------|-------|--------|-----|------|------|-------|------|-------|-------|----|------|",
    ]

    for i, d in enumerate(districts, 1):
        lines.append(
            f"| {i} | {d.province[:8]} | {d.district} | {d.sold_total} | {d.total} | "
            f"**{d.sell_through_pct:.1f}%** | {d.sold_recent} | "
            f"{d.sold_under_1m} | {d.sold_1m_3m} | {d.sold_3m_5m} | {d.sold_5m_10m} | {d.sold_over_10m} | "
            f"{d.sold_condo} | {d.sold_house} | {d.sold_townhouse} | {d.sold_land} |"
        )

    # Group results by district and property type
    by_district: dict[str, list[NpaInHotDistrict]] = {}
    for r in results:
        key = r.district
        by_district.setdefault(key, []).append(r)

    lines += [
        "",
        f"## Available NPA in Hot Districts ({len(results)} total)",
        "",
    ]

    # Summary by district × type
    lines += [
        "### Inventory Summary",
        "",
        "| District | Sell% | Condo | House | Townhouse | Land | Commercial | Total | Avg Price |",
        "|----------|-------|-------|-------|-----------|------|------------|-------|-----------|",
    ]

    for d in districts:
        props = by_district.get(d.district, [])
        if not props:
            continue
        by_type: dict[str, list] = {}
        for p in props:
            by_type.setdefault(p.property_type, []).append(p)

        avg_price = sum(p.price for p in props) / len(props) if props else 0
        lines.append(
            f"| {d.district} | {d.sell_through_pct:.1f}% | "
            f"{len(by_type.get('condo', []))} | {len(by_type.get('house', []))} | "
            f"{len(by_type.get('townhouse', []))} | {len(by_type.get('land', []))} | "
            f"{len(by_type.get('commercial', []))} | {len(props)} | ฿{avg_price:,.0f} |"
        )

    # Best deals per district: sorted by price (cheapest first within type)
    lines += [
        "",
        "### Best Deals by District",
        "",
    ]

    for d in districts:
        props = by_district.get(d.district, [])
        if not props:
            continue

        # Focus on the SELLING types: match LED's sold type distribution
        best_types = []
        if d.sold_townhouse > 0:
            best_types.append("townhouse")
        if d.sold_house > 0:
            best_types.append("house")
        if d.sold_condo > 0:
            best_types.append("condo")
        if d.sold_land > 0:
            best_types.append("land")
        if not best_types:
            best_types = ["townhouse", "house", "condo"]

        relevant = [p for p in props if p.property_type in best_types]
        relevant.sort(key=lambda p: p.price)

        if not relevant:
            continue

        lines += [
            f"#### {d.district} (sell-through {d.sell_through_pct:.1f}%, {d.sold_total} sold)",
            f"LED sold breakdown: condo={d.sold_condo}, house={d.sold_house}, "
            f"townhouse={d.sold_townhouse}, land={d.sold_land}",
            f"Best price bands: <1M={d.sold_under_1m}, 1-3M={d.sold_1m_3m}, "
            f"3-5M={d.sold_3m_5m}, 5-10M={d.sold_5m_10m}",
            "",
            "| # | Src | ID | Type | Project | Price | Size | BR | District |",
            "|---|-----|----|------|---------|-------|------|----|----------|",
        ]

        for j, p in enumerate(relevant[:15], 1):
            size_s = f"{p.size_sqm:.0f}sqm" if p.size_sqm else f"{p.size_wa:.0f}wa" if p.size_wa else "?"
            br = str(p.bedroom) if p.bedroom else "?"
            proj = (p.project_name or p.source_id)[:30]
            lines.append(
                f"| {j} | {p.source} | {p.source_id} | {p.property_type} | "
                f"{proj} | ฿{p.price:,.0f} | {size_s} | {br} | {p.subdistrict[:15]} |"
            )

        lines.append("")

    return "\n".join(lines)


def export_json(results: list[NpaInHotDistrict], path: str) -> None:
    import decimal

    def _conv(v):
        if isinstance(v, decimal.Decimal):
            return float(v)
        return v

    data = []
    for r in results:
        data.append({
            "source": r.source,
            "source_id": r.source_id,
            "property_type": r.property_type,
            "project_name": r.project_name,
            "price": _conv(r.price),
            "size_sqm": _conv(r.size_sqm),
            "size_wa": _conv(r.size_wa),
            "bedroom": r.bedroom,
            "bathroom": r.bathroom,
            "lat": _conv(r.lat),
            "lon": _conv(r.lon),
            "province": r.province,
            "district": r.district,
            "subdistrict": r.subdistrict,
            "price_sqm": round(_conv(r.price_sqm)) if r.price_sqm else None,
            "price_wa": round(_conv(r.price_wa)) if r.price_wa else None,
            "district_sell_through_pct": r.hot_district.sell_through_pct,
            "district_sold_total": r.hot_district.sold_total,
            "district_sold_recent": r.hot_district.sold_recent,
        })
    import decimal

    class DecimalEncoder(json.JSONEncoder):
        def default(self, o):
            if isinstance(o, decimal.Decimal):
                return float(o)
            return super().default(o)

    with open(path, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, cls=DecimalEncoder)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(description="Transaction-Velocity NPA Screener")
    parser.add_argument("--min-sell-pct", type=float, default=8.0,
                        help="Min LED sell-through %% (default 8)")
    parser.add_argument("--min-sold", type=int, default=3,
                        help="Min sold count per district")
    parser.add_argument("--max-price", type=float, default=None,
                        help="Max NPA price in baht")
    parser.add_argument("--property-types", type=str, default=None,
                        help="Comma-separated: condo,house,townhouse,land,commercial")
    parser.add_argument("--province", type=str, default=None,
                        help="Single province filter")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    args.provinces = [args.province] if args.province else TARGET_PROVINCES
    ptypes = args.property_types.split(",") if args.property_types else None

    conn = psycopg2.connect(DB_URL)

    print("=== Transaction-Velocity NPA Screener ===", flush=True)
    print(f"Sell-through >= {args.min_sell_pct}% | Min sold: {args.min_sold}", flush=True)
    print(f"Price cap: {'฿{:,.0f}'.format(args.max_price) if args.max_price else 'none'}", flush=True)
    print(f"Types: {ptypes or 'all'}", flush=True)
    print()

    # Step 1
    print("Step 1: Finding hot districts (LED sell-through data)...", flush=True)
    districts = find_hot_districts(
        conn, args.provinces, args.min_sell_pct, args.min_sold
    )
    print(f"  → {len(districts)} hot districts found", flush=True)
    for d in districts:
        print(f"    {d.district:15} | sell:{d.sell_through_pct:5.1f}% | "
              f"sold:{d.sold_total:>3} | TH:{d.sold_townhouse} H:{d.sold_house} "
              f"C:{d.sold_condo} L:{d.sold_land}", flush=True)
    print()

    # Step 2
    print("Step 2: Finding available NPA in hot districts...", flush=True)
    results = find_npa_in_hot_districts(
        conn, districts, args.max_price, ptypes
    )
    print(f"  → {len(results)} NPA properties found", flush=True)

    # Type breakdown
    by_type: dict[str, int] = {}
    for r in results:
        by_type[r.property_type] = by_type.get(r.property_type, 0) + 1
    for t, c in sorted(by_type.items(), key=lambda x: -x[1]):
        print(f"    {t:15}: {c}", flush=True)
    print()

    # Step 3: Report
    output_dir = Path(__file__).parent.parent.parent.parent / "output"
    date_str = datetime.now().strftime("%Y-%m-%d")

    report = format_report(districts, results, args)
    report_path = output_dir / f"txn-velocity-screen-{date_str}.md"
    report_path.write_text(report)
    print(f"✓ Report: {report_path}", flush=True)

    if args.json:
        json_path = output_dir / f"txn-velocity-screen-{date_str}.json"
        export_json(results, str(json_path))
        print(f"✓ JSON: {json_path}", flush=True)

    conn.close()


if __name__ == "__main__":
    main()

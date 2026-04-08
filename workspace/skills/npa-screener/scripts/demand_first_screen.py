"""
Demand-First NPA Screener — Find NPA properties in HIGH-DEMAND areas.

Inverts the typical approach: instead of finding cheap NPA and hoping
demand exists, we first identify WHERE demand is strongest, then check
if any NPA properties exist there.

Demand signals:
  - Rent-to-sale ratio (R:S >= 3x = tenants competing for units)
  - Supply pressure < 15% (not being dumped)
  - Rental activity (units_for_rent / total_units)
  - YoY price trend (positive = area holding value)

Usage:
    python demand_first_screen.py
    python demand_first_screen.py --min-rs 2.5 --max-sp 20 --radius 500
    python demand_first_screen.py --province กรุงเทพมหานคร --json
"""

import argparse
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

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

VERIFIED_SALE_MULTIPLIER = 0.92
VERIFIED_RENT_BARE = 0.85
CAM_DEFAULT_SQM = 55
PROPERTY_TAX_RATE = 0.0002
INSURANCE_RATE = 0.005
VACANCY_MONTHS = 1
AGENT_FEE_RATE = 0.08
INCOME_TAX_RATE = 0.10


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6_371_000
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def bbox(lat: float, lon: float, radius_m: float):
    dlat = radius_m / 111_320
    dlon = radius_m / (111_320 * math.cos(math.radians(lat)))
    return (lat - dlat, lat + dlat, lon - dlon, lon + dlon)


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------


@dataclass
class DemandBuilding:
    """A building with strong rental demand signals from Hipflat."""
    name_th: str
    name_en: str
    lat: float
    lng: float
    year_completed: Optional[int]
    total_units: int
    units_for_sale: int
    units_for_rent: int
    rent_sale_ratio: float
    supply_pressure_pct: float
    rental_activity_pct: float
    avg_sale_sqm: Optional[int]
    avg_sold_sqm: Optional[int]
    rent_min: Optional[int]
    rent_max: Optional[int]
    yoy_change_pct: Optional[float]
    price_trend: Optional[str]
    district: str


@dataclass
class NpaInDemandArea:
    """An NPA property found near a high-demand building."""
    # NPA identity
    source: str
    source_id: str
    npa_project: str
    price: float
    sqm: float
    bedroom: Optional[int]
    bathroom: Optional[int]
    building_age: Optional[int]
    lat: float
    lon: float
    # Matched demand building
    demand_building: DemandBuilding
    distance_m: float
    # Computed metrics
    npa_sqm: float
    market_sqm: float
    verified_market_sqm: float
    discount_pct: float
    rent_estimate: float  # unit-size adjusted
    rent_verified: float  # after bare haircut
    gry_pct: float
    annual_net: float
    nry_pct: float
    # Demand context
    rent_sale_ratio: float
    supply_pressure_pct: float
    yoy_pct: Optional[float]


# ---------------------------------------------------------------------------
# Step 1: Find high-demand buildings
# ---------------------------------------------------------------------------


def find_demand_buildings(
    conn,
    min_rs: float = 3.0,
    max_sp: float = 15.0,
    min_units: int = 100,
    min_rentals: int = 20,
    min_year: int = 2008,
    max_year: int = 2022,
) -> list[DemandBuilding]:
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(
        """
        SELECT name_th, name_en, lat, lng, total_units,
               units_for_sale, units_for_rent,
               avg_sale_sqm, avg_sold_sqm,
               rent_price_min, rent_price_max,
               year_completed, yoy_change_pct, price_trend,
               district_name
        FROM hipflat_projects
        WHERE lat IS NOT NULL AND lng IS NOT NULL
          AND total_units >= %s
          AND units_for_rent >= %s
          AND year_completed >= %s AND year_completed <= %s
          AND units_for_sale > 0
          AND (units_for_rent::float / units_for_sale) >= %s
          AND (units_for_sale::float / total_units * 100) < %s
        ORDER BY (units_for_rent::float / units_for_sale) DESC
        """,
        (min_units, min_rentals, min_year, max_year, min_rs, max_sp),
    )

    buildings = []
    for row in cur.fetchall():
        total = row["total_units"] or 1
        sale = row["units_for_sale"] or 0
        rent = row["units_for_rent"] or 0
        buildings.append(DemandBuilding(
            name_th=row["name_th"] or "",
            name_en=row["name_en"] or "",
            lat=float(row["lat"]),
            lng=float(row["lng"]),
            year_completed=row["year_completed"],
            total_units=total,
            units_for_sale=sale,
            units_for_rent=rent,
            rent_sale_ratio=rent / sale if sale > 0 else 0,
            supply_pressure_pct=sale / total * 100,
            rental_activity_pct=rent / total * 100,
            avg_sale_sqm=row.get("avg_sale_sqm"),
            avg_sold_sqm=row.get("avg_sold_sqm"),
            rent_min=row.get("rent_price_min"),
            rent_max=row.get("rent_price_max"),
            yoy_change_pct=float(row["yoy_change_pct"]) if row.get("yoy_change_pct") is not None else None,
            price_trend=row.get("price_trend"),
            district=row.get("district_name") or "",
        ))
    cur.close()
    return buildings


# ---------------------------------------------------------------------------
# Step 2: Find NPA properties near demand buildings
# ---------------------------------------------------------------------------

from adapter_bridge import search_bbox, PropertyCategory


def estimate_rent_by_size(
    sqm: float, rent_min: Optional[int], rent_max: Optional[int]
) -> float:
    """Estimate rent based on unit size using building's rent range.

    Small units (<35sqm) → 15th percentile of range
    Medium (35-60sqm) → 40th percentile
    Large (60+sqm) → 70th percentile
    """
    if not rent_min or rent_min <= 0:
        return 0
    if not rent_max or rent_max <= rent_min:
        return rent_min

    if sqm < 35:
        pct = 0.15
    elif sqm < 60:
        pct = 0.40
    else:
        pct = 0.70

    return rent_min + (rent_max - rent_min) * pct


def compute_net_yield(
    price: float, sqm: float, rent_verified: float
) -> tuple[float, float]:
    """Compute annual net income and NRY.

    Returns (annual_net, nry_pct).
    """
    annual_gross = rent_verified * 12
    cam = CAM_DEFAULT_SQM * sqm * 12
    prop_tax = price * PROPERTY_TAX_RATE
    insurance = price * INSURANCE_RATE
    vacancy = annual_gross / 12 * VACANCY_MONTHS
    agent = annual_gross * AGENT_FEE_RATE
    income_tax = annual_gross * INCOME_TAX_RATE

    annual_net = annual_gross - cam - prop_tax - insurance - vacancy - agent - income_tax
    nry = annual_net / price * 100 if price > 0 else 0

    return annual_net, nry


def find_npa_near_demand(
    conn,
    buildings: list[DemandBuilding],
    radius_m: int = 300,
    min_discount: float = 15.0,
) -> list[NpaInDemandArea]:
    results = []
    seen = set()

    for bld in buildings:
        market_sqm = bld.avg_sale_sqm or bld.avg_sold_sqm
        if not market_sqm or market_sqm <= 0:
            continue

        # Query all GPS-enabled providers via adapter
        npa_props = search_bbox(bld.lat, bld.lng, radius_m)
        condos = [p for p in npa_props if p.category == PropertyCategory.CONDO]

        for p in condos:
            key = f"{p.source.value}-{p.source_id}"
            if key in seen:
                continue
            if not p.lat or not p.lon:
                continue

            dist = haversine_m(bld.lat, bld.lng, p.lat, p.lon)
            if dist > radius_m:
                continue

            price = p.best_price_baht or 0
            sqm = p.size_sqm or 0
            if sqm <= 0 or sqm > 300 or price <= 0:
                continue

            npa_sqm = price / sqm
            verified_market = market_sqm * VERIFIED_SALE_MULTIPLIER
            discount = (verified_market - npa_sqm) / verified_market * 100

            if discount < min_discount:
                continue

            rent_est = estimate_rent_by_size(sqm, bld.rent_min, bld.rent_max)
            if rent_est <= 0:
                continue

            rent_verified = rent_est * VERIFIED_RENT_BARE
            gry = rent_verified * 12 / price * 100
            annual_net, nry = compute_net_yield(price, sqm, rent_verified)

            building_age = p.extra.get("building_age")
            seen.add(key)
            results.append(NpaInDemandArea(
                source=p.source.value,
                source_id=p.source_id,
                npa_project=p.project_name or "",
                price=price,
                sqm=sqm,
                bedroom=p.bedroom,
                bathroom=p.bathroom,
                building_age=int(building_age) if building_age else None,
                lat=p.lat,
                lon=p.lon,
                demand_building=bld,
                distance_m=dist,
                npa_sqm=npa_sqm,
                market_sqm=market_sqm,
                verified_market_sqm=verified_market,
                discount_pct=discount,
                rent_estimate=rent_est,
                rent_verified=rent_verified,
                gry_pct=gry,
                annual_net=annual_net,
                nry_pct=nry,
                rent_sale_ratio=bld.rent_sale_ratio,
                supply_pressure_pct=bld.supply_pressure_pct,
                yoy_pct=bld.yoy_change_pct,
            ))

    return results


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------


def format_report(
    buildings: list[DemandBuilding],
    results: list[NpaInDemandArea],
    args,
) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Sort results by NRY desc
    ranked = sorted(results, key=lambda r: r.nry_pct, reverse=True)

    lines = [
        f"# Demand-First NPA Screening — {now}",
        "",
        "## Approach",
        "1. Find buildings with **strongest rental demand** (R:S ratio, low supply pressure)",
        "2. Check if any NPA properties exist **within those buildings or nearby**",
        "3. Compute unit-size-specific rent + honest yield",
        "",
        "## Parameters",
        f"- Min rent:sale ratio: {args.min_rs}x",
        f"- Max supply pressure: {args.max_sp}%",
        f"- Search radius: {args.radius}m around each demand building",
        f"- Min discount: {args.min_discount}%",
        "",
        "## Demand Buildings Found",
        "",
        f"**{len(buildings)} buildings** with R:S >= {args.min_rs}x, SP < {args.max_sp}%, 100+ units, 20+ rentals",
        "",
        "| # | Building | District | Year | Units | Sale | Rent | R:S | SP | YoY | Trend |",
        "|---|----------|----------|------|-------|------|------|-----|-----|-----|-------|",
    ]

    for i, b in enumerate(buildings[:30], 1):
        name = (b.name_th or b.name_en)[:35]
        yoy = f"{b.yoy_change_pct:+.1f}%" if b.yoy_change_pct is not None else "?"
        trend = b.price_trend or "?"
        lines.append(
            f"| {i} | {name} | {b.district[:12]} | {b.year_completed or '?'} | "
            f"{b.total_units} | {b.units_for_sale} | {b.units_for_rent} | "
            f"{b.rent_sale_ratio:.1f}x | {b.supply_pressure_pct:.0f}% | {yoy} | {trend} |"
        )

    lines += [
        "",
        "## NPA Properties in Demand Areas",
        "",
        f"**{len(results)} NPA units** found near high-demand buildings (discount >= {args.min_discount}%)",
        "",
        "| # | Src | ID | NPA Project | Demand Building | Price | sqm | Disc | Rent/mo | GRY | NRY | R:S | SP | YoY | Dist |",
        "|---|-----|-----|------------|----------------|-------|-----|------|---------|-----|-----|-----|----|-----|------|",
    ]

    for i, r in enumerate(ranked[:50], 1):
        npa_proj = (r.npa_project or r.source_id)[:25]
        demand_name = (r.demand_building.name_th or r.demand_building.name_en)[:25]
        yoy = f"{r.yoy_pct:+.1f}%" if r.yoy_pct is not None else "?"
        lines.append(
            f"| {i} | {r.source} | {r.source_id} | {npa_proj} | {demand_name} | "
            f"฿{r.price:,.0f} | {r.sqm:.0f} | {r.discount_pct:.0f}% | "
            f"฿{r.rent_verified:,.0f} | {r.gry_pct:.1f}% | {r.nry_pct:.1f}% | "
            f"{r.rent_sale_ratio:.1f}x | {r.supply_pressure_pct:.0f}% | {yoy} | {r.distance_m:.0f}m |"
        )

    # Detailed cards for top 10
    lines += ["", "## Top 10 — Detailed Analysis", ""]

    for i, r in enumerate(ranked[:10], 1):
        bld = r.demand_building
        lines += [
            f"### #{i} — {r.source} {r.source_id}",
            f"- **NPA Project:** {r.npa_project or 'N/A'}",
            f"- **Price:** ฿{r.price:,.0f} ({r.sqm:.0f}sqm = ฿{r.npa_sqm:,.0f}/sqm)",
            f"- **Bedroom/Bathroom:** {r.bedroom or '?'}/{r.bathroom or '?'}",
            f"- **Building age:** {r.building_age or 'unknown'} years",
            f"- **GPS:** {r.lat}, {r.lon}",
            "",
            f"**Market Data (from {bld.name_th or bld.name_en}):**",
            f"- Market price: ฿{r.market_sqm:,}/sqm → verified (×0.92): ฿{r.verified_market_sqm:,.0f}/sqm",
            f"- **Real discount: {r.discount_pct:.1f}%**",
            f"- Distance to demand building: {r.distance_m:.0f}m",
            "",
            f"**Demand Signals:**",
            f"- Rent:Sale ratio: **{r.rent_sale_ratio:.1f}x** ({bld.units_for_rent} rent / {bld.units_for_sale} sale)",
            f"- Supply pressure: **{r.supply_pressure_pct:.0f}%** ({bld.units_for_sale}/{bld.total_units} units)",
            f"- YoY price trend: **{r.yoy_pct:+.1f}%**" if r.yoy_pct is not None else f"- YoY: unknown",
            f"- Rental activity: {bld.rental_activity_pct:.0f}% of units listed for rent",
            f"- Building: {bld.year_completed or '?'} built, {bld.total_units} total units",
            "",
            f"**Yield (unit-size adjusted, honest):**",
            f"- Rent estimate ({r.sqm:.0f}sqm): ฿{r.rent_estimate:,.0f}/mo",
            f"- Rent verified (×0.85): ฿{r.rent_verified:,.0f}/mo",
            f"- GRY: {r.gry_pct:.1f}%",
            f"- Annual net: ฿{r.annual_net:,.0f}",
            f"- **NRY: {r.nry_pct:.1f}%**",
            "",
        ]

    return "\n".join(lines)


def export_json(results: list[NpaInDemandArea], path: str) -> None:
    data = []
    ranked = sorted(results, key=lambda r: r.nry_pct, reverse=True)
    for r in ranked:
        bld = r.demand_building
        data.append({
            "source": r.source,
            "source_id": r.source_id,
            "npa_project": r.npa_project,
            "price": r.price,
            "sqm": r.sqm,
            "npa_sqm": round(r.npa_sqm),
            "bedroom": r.bedroom,
            "bathroom": r.bathroom,
            "building_age": r.building_age,
            "lat": r.lat,
            "lon": r.lon,
            "demand_building": bld.name_th or bld.name_en,
            "demand_building_year": bld.year_completed,
            "distance_m": round(r.distance_m),
            "market_sqm": r.market_sqm,
            "verified_market_sqm": round(r.verified_market_sqm),
            "discount_pct": round(r.discount_pct, 1),
            "rent_estimate": round(r.rent_estimate),
            "rent_verified": round(r.rent_verified),
            "gry_pct": round(r.gry_pct, 1),
            "annual_net": round(r.annual_net),
            "nry_pct": round(r.nry_pct, 1),
            "rent_sale_ratio": round(r.rent_sale_ratio, 1),
            "supply_pressure_pct": round(r.supply_pressure_pct, 1),
            "yoy_pct": round(r.yoy_pct, 1) if r.yoy_pct is not None else None,
            "total_units": bld.total_units,
            "units_for_sale": bld.units_for_sale,
            "units_for_rent": bld.units_for_rent,
        })
    with open(path, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(description="Demand-First NPA Screener")
    parser.add_argument("--min-rs", type=float, default=3.0, help="Minimum rent:sale ratio")
    parser.add_argument("--max-sp", type=float, default=15.0, help="Maximum supply pressure %%")
    parser.add_argument("--radius", type=int, default=300, help="Search radius (m) around demand buildings")
    parser.add_argument("--min-discount", type=float, default=15.0, help="Minimum discount %%")
    parser.add_argument("--min-units", type=int, default=100, help="Minimum building units")
    parser.add_argument("--min-rentals", type=int, default=20, help="Minimum rental listings")
    parser.add_argument("--min-year", type=int, default=2008, help="Minimum building year")
    parser.add_argument("--max-year", type=int, default=2022, help="Maximum building year")
    parser.add_argument("--json", action="store_true", help="Export JSON")
    args = parser.parse_args()

    conn = psycopg2.connect(DB_URL)

    print("=== Demand-First NPA Screener ===", flush=True)
    print(f"R:S >= {args.min_rs}x | SP < {args.max_sp}% | radius {args.radius}m | discount >= {args.min_discount}%", flush=True)
    print()

    # Step 1: Find high-demand buildings
    print("Step 1: Finding high-demand buildings...", flush=True)
    buildings = find_demand_buildings(
        conn,
        min_rs=args.min_rs,
        max_sp=args.max_sp,
        min_units=args.min_units,
        min_rentals=args.min_rentals,
        min_year=args.min_year,
        max_year=args.max_year,
    )
    print(f"  → {len(buildings)} demand buildings found", flush=True)

    # Step 2: Find NPA near demand
    print("Step 2: Searching NPA providers near demand buildings...", flush=True)
    results = find_npa_near_demand(
        conn, buildings, radius_m=args.radius, min_discount=args.min_discount
    )
    print(f"  → {len(results)} NPA units found in demand areas", flush=True)

    # Step 3: Report
    output_dir = Path(__file__).parent.parent.parent.parent / "output"
    date_str = datetime.now().strftime("%Y-%m-%d")

    report = format_report(buildings, results, args)
    report_path = output_dir / f"demand-first-screen-{date_str}.md"
    report_path.write_text(report)
    print(f"\n✓ Report: {report_path}", flush=True)

    if args.json:
        json_path = output_dir / f"demand-first-screen-{date_str}.json"
        export_json(results, str(json_path))
        print(f"✓ JSON: {json_path}", flush=True)

    # Summary
    positive_yoy = [r for r in results if r.yoy_pct is not None and r.yoy_pct > 0]
    high_nry = [r for r in results if r.nry_pct >= 4]

    print(f"\n{'='*60}")
    print(f"  Total demand buildings:    {len(buildings)}")
    print(f"  NPA units in demand areas: {len(results)}")
    print(f"  With NRY >= 4%:            {len(high_nry)}")
    print(f"  In positive YoY areas:     {len(positive_yoy)}")
    print(f"{'='*60}")

    # Print top 10
    ranked = sorted(results, key=lambda r: r.nry_pct, reverse=True)
    print(f"\nTop 10:")
    for i, r in enumerate(ranked[:10], 1):
        name = (r.npa_project or r.source_id)[:25]
        yoy = f"{r.yoy_pct:+.1f}%" if r.yoy_pct is not None else "?"
        print(
            f"  {i:>2}. {r.source:5} {name:25} | ฿{r.price:>10,.0f} | {r.sqm:>4.0f}sqm | "
            f"disc:{r.discount_pct:>3.0f}% | rent:฿{r.rent_verified:>6,.0f} | "
            f"NRY:{r.nry_pct:>4.1f}% | R:S:{r.rent_sale_ratio:.1f}x | YoY:{yoy}"
        )

    conn.close()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Automated property analysis pipeline for NPA properties.

Pulls property data from PostgreSQL, runs location intel, flood check,
financial calculations, and queries KB for comparables + macro context.
Outputs a structured markdown analysis report to stdout.

Usage:
    python3 analyze_property.py --source sam --id 3066
    python3 analyze_property.py --source led --asset_id LED-xxx --json
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime

# ---------------------------------------------------------------------------
# Paths to sibling skill scripts (add to sys.path so we can import)
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SKILLS_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, "..", ".."))

sys.path.insert(0, os.path.join(SKILLS_DIR, "location-intel", "scripts"))
sys.path.insert(0, os.path.join(SKILLS_DIR, "flood-check", "scripts"))
sys.path.insert(0, os.path.join(SKILLS_DIR, "property-calc", "scripts"))
sys.path.insert(0, os.path.join(SKILLS_DIR, "kb", "scripts"))

from location import find_nearest_stations, overpass_query, haversine  # noqa: E402
from flood_check import check_flood_risk, FLOOD_ZONES  # noqa: E402
from calc import (  # noqa: E402
    acquisition_cost,
    rental_yield,
    price_per_area,
    to_sqm,
    format_thb,
)

# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------
PG_URI = os.environ.get("POSTGRES_URI", "postgresql://localhost/npa_kb")
ADA_PG_URI = os.environ.get("ADA_POSTGRES_URI", "postgresql://localhost/ada_kb")


def psql(pg_uri, sql, fetch=True):
    """Run psql, return stdout text or raise."""
    cmd = ["psql", pg_uri, "-t", "-A", "-F", "\t", "-c", sql]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    if r.returncode != 0:
        raise RuntimeError(f"psql failed: {r.stderr.strip()[:300]}")
    if not fetch:
        return None
    return r.stdout.strip()


def psql_json(pg_uri, sql):
    """Run psql with JSON output."""
    sql_wrapped = f"SELECT json_agg(t) FROM ({sql}) t;"
    out = psql(pg_uri, sql_wrapped)
    if not out or out == "NULL":
        return []
    return json.loads(out)


# ---------------------------------------------------------------------------
# Step 1: Pull property data from DB
# ---------------------------------------------------------------------------
def fetch_sam_property(prop_id):
    """Fetch a SAM property by id."""
    return psql_json(
        PG_URI,
        f"""
        SELECT id, sam_id, code, type_name, title_deed_type, title_deed_numbers,
               size_text, size_sqm, size_rai, size_ngan, size_wa,
               address_full, project_name, road, subdistrict, district, province,
               zone_color, floor, price_baht, price_per_unit, price_unit,
               status, lat, lng, description, remarks, access_directions,
               source_url, is_active,
               announcement_start_date, registration_end_date, submission_date,
               auction_method_text
        FROM sam_properties
        WHERE id = {int(prop_id)}
        """,
    )


def fetch_led_property(asset_id):
    """Fetch a LED property by asset_id."""
    rows = psql_json(
        PG_URI,
        f"""
        SELECT p.asset_id, p.asset_type, p.source_name, p.source_id,
               p.property_type, p.address, p.province, p.ampur, p.tumbol,
               p.size_rai, p.size_ngan, p.size_wa,
               p.primary_price_satang, p.appraisal_price_satang,
               p.sale_status, p.sale_type,
               p.next_auction_date, p.next_auction_status,
               p.last_auction_date, p.last_auction_status,
               p.total_auction_count, p.source_url,
               l.case_number, l.lot_number, l.court,
               l.plaintiff, l.defendant, l.owner_suit_name,
               l.deed_type, l.deed_number,
               l.enforcement_officer_price_satang,
               l.department_appraisal_price_satang,
               l.committee_determined_price_satang,
               l.deposit_amount_satang,
               l.sale_location, l.sale_time,
               l.contact_office, l.contact_phone,
               l.occupant, l.remark
        FROM properties p
        JOIN led_properties l ON l.asset_id = p.asset_id
        WHERE p.asset_id = '{asset_id.replace("'", "''")}'
        """,
    )
    return rows


# ---------------------------------------------------------------------------
# Step 2: Location intelligence (if GPS coords available)
# ---------------------------------------------------------------------------
def run_location_intel(lat, lon, radius=2000):
    """Run location intel: transit + Overpass amenities."""
    result = {"coordinates": {"lat": lat, "lon": lon}}

    # Transit from hardcoded data
    stations = find_nearest_stations(lat, lon, max_distance=radius)
    result["transit"] = stations

    if stations:
        dist = stations[0]["distance_m"]
        if dist <= 500:
            result["transit_rating"] = "PREMIUM"
        elif dist <= 1000:
            result["transit_rating"] = "GOOD"
        elif dist <= 2000:
            result["transit_rating"] = "MODERATE"
        else:
            result["transit_rating"] = "FAR"
    else:
        result["transit_rating"] = "NO_STATION"

    # Overpass amenities (with timeout tolerance)
    for cat in ["school", "hospital", "shopping"]:
        try:
            result[cat] = overpass_query(lat, lon, radius, cat)[:8]
        except Exception as e:
            result[cat] = []
            result[f"{cat}_error"] = str(e)

    return result


# ---------------------------------------------------------------------------
# Step 3: Flood risk assessment
# ---------------------------------------------------------------------------
def run_flood_check(lat, lon, province=None):
    """Run flood risk check."""
    return check_flood_risk(lat, lon, province=province)


# ---------------------------------------------------------------------------
# Step 4: Financial calculations
# ---------------------------------------------------------------------------
def run_financials(price, appraised, sqm=0, rai=0, ngan=0, wah=0,
                   rent=None, common_fee=0, renovation=0):
    """Run full financial analysis."""
    result = {}

    # Acquisition costs
    result["acquisition"] = acquisition_cost(
        price,
        appraised_value=appraised,
        renovation_cost=renovation,
    )

    # Price per area
    total_sqm = to_sqm(rai, ngan, wah, max(0, sqm))
    if total_sqm > 0:
        result["area"] = price_per_area(price, rai=rai, ngan=ngan, wah=wah, sqm=sqm)

    # Rental yield (if rent estimate available)
    if rent and rent > 0:
        result["rental"] = rental_yield(
            result["acquisition"]["total_acquisition_cost"],
            rent,
            common_fee_monthly=common_fee,
        )

    return result


# ---------------------------------------------------------------------------
# Step 5: KB area comparables
# ---------------------------------------------------------------------------
def query_npa_kb(area_name):
    """Query NPA KB metadata for area comparables."""
    if not area_name:
        return []
    safe_area = area_name.replace("'", "''")
    return psql_json(
        PG_URI,
        f"""
        SELECT category, area, source, summary,
               ingested_at::text, valid_until::text,
               (valid_until > NOW() AND NOT stale) as is_fresh
        FROM kb_metadata
        WHERE area ILIKE '%{safe_area}%'
        ORDER BY
            CASE WHEN category = 'pricing' THEN 1
                 WHEN category = 'rental' THEN 2
                 WHEN category = 'area' THEN 3
                 ELSE 4 END,
            ingested_at DESC
        LIMIT 10
        """,
    )


# ---------------------------------------------------------------------------
# Step 6: Ada KB macro context
# ---------------------------------------------------------------------------
def query_ada_macro():
    """Query Ada's KB for macro/real-estate/REIT related context."""
    results = []

    # 1. Check sc_alerts for relevant financial alerts
    try:
        alerts = psql_json(
            ADA_PG_URI,
            """
            SELECT ticker, event, severity, created_at::text
            FROM sc_alerts
            WHERE event ILIKE '%real estate%'
               OR event ILIKE '%property%'
               OR event ILIKE '%NPL%'
               OR event ILIKE '%REIT%'
               OR event ILIKE '%interest rate%'
               OR event ILIKE '%bank lending%'
               OR event ILIKE '%BOJ%'
               OR event ILIKE '%MPC%'
               OR event ILIKE '%GDP%'
            ORDER BY created_at DESC
            LIMIT 5
            """,
        )
        if alerts:
            results.append({"type": "alerts", "data": alerts})
    except Exception:
        pass

    # 2. Check lightrag docs for macro research
    try:
        docs = psql_json(
            ADA_PG_URI,
            """
            SELECT doc_name, LEFT(content, 300) as snippet, create_time::text
            FROM lightrag_doc_full
            WHERE content ILIKE '%real estate%'
               OR content ILIKE '%property%'
               OR content ILIKE '%NPL%'
               OR content ILIKE '%REIT%'
               OR content ILIKE '%interest rate%'
               OR content ILIKE '%housing%'
               OR content ILIKE '%condo%'
            ORDER BY create_time DESC
            LIMIT 3
            """,
        )
        if docs:
            results.append({"type": "research", "data": docs})
    except Exception:
        pass

    return results


# ---------------------------------------------------------------------------
# Step 7: Markdown output using AGENTS.md template
# ---------------------------------------------------------------------------
def format_location_section(loc):
    """Format location intel as markdown lines."""
    lines = []

    if not loc:
        return ["⚠️ No GPS coordinates available — location analysis skipped"]

    rating = loc.get("transit_rating", "N/A")
    lines.append(f"- Transit Rating: **{rating}**")

    for s in loc.get("transit", [])[:3]:
        lines.append(f"  - {s['name']} ({s['line']}) — {s['distance_m']}m (~{s['walk_min']} min walk)")

    for cat, label in [("school", "Schools"), ("hospital", "Hospitals"), ("shopping", "Shopping")]:
        items = loc.get(cat, [])
        if items:
            lines.append(f"- {label}: {', '.join(i['name'] + ' (' + str(i['distance_m']) + 'm)' for i in items[:3])}")
        else:
            lines.append(f"- {label}: None found within 2km")

    return lines


def format_flood_section(flood):
    """Format flood check as markdown."""
    risk = flood.get("risk", "UNKNOWN")
    emoji = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢", "UNKNOWN": "⚪"}.get(risk, "⚪")
    lines = [f"- Flood Risk: {emoji} **{risk}**"]

    if flood.get("zone_match"):
        lines.append(f"  - Zone: {flood['zone_match']}")
    for r in flood.get("reasons", []):
        lines.append(f"  - {r}")
    for rec in flood.get("recommendations", [])[:2]:
        lines.append(f"  - 💡 {rec}")

    return lines


def format_financial_section(fin):
    """Format financial analysis as markdown."""
    lines = []
    acq = fin.get("acquisition", {})
    area = fin.get("area", {})
    rental = fin.get("rental", {})

    lines.append(f"- Purchase Price: {format_thb(acq.get('purchase_price'))}")
    if acq.get("appraised_value"):
        lines.append(f"- Appraised Value: {format_thb(acq['appraised_value'])}")
        lines.append(f"- Discount: **{acq.get('discount_pct', 0)}%** below appraisal")
    lines.append(f"- Transfer Fee (2%): {format_thb(acq.get('transfer_fee'))}")
    lines.append(f"- WHT (1%): {format_thb(acq.get('withholding_tax'))}")
    if acq.get("renovation_cost", 0) > 0:
        lines.append(f"- Renovation: {format_thb(acq['renovation_cost'])}")
    lines.append(f"- **Total Acquisition: {format_thb(acq.get('total_acquisition_cost'))}**")

    if area:
        lines.append(f"- Area: {area.get('total_sqm', 0):.1f} sqm ({area.get('total_wah', 0):.1f} wah)")
        if "price_per_sqm" in area:
            lines.append(f"- Price/sqm: {format_thb(area['price_per_sqm'])}")
        if "price_per_wah" in area:
            lines.append(f"- Price/wah: {format_thb(area['price_per_wah'])}")
        if "price_per_rai" in area:
            lines.append(f"- Price/rai: {format_thb(area['price_per_rai'])}")

    if rental:
        lines.append(f"- Est. Rent: {format_thb(rental['monthly_rent'])}/month")
        lines.append(f"- Gross Yield: **{rental['gross_yield_pct']}%**")
        lines.append(f"- Net Yield: **{rental['net_yield_pct']}%**")
        be = rental.get("break_even_years")
        lines.append(f"- Break-even: {f'{be} years' if be else 'N/A'}")
        lines.append(f"- Monthly Cash Flow: {format_thb(rental['monthly_cash_flow'])}")

    return lines


def format_kb_section(kb_entries):
    """Format KB comparables as markdown."""
    lines = []
    if not kb_entries:
        lines.append("- No KB data found for this area")
        return lines

    for entry in kb_entries:
        fresh = "✅" if entry.get("is_fresh") else "⏰"
        lines.append(
            f"- {fresh} [{entry.get('category', '?')}] {entry.get('summary', 'N/A')[:100]}\n"
            f"  Source: {entry.get('source', '-')} | {entry.get('ingested_at', '-')[:10]}"
        )
    return lines


def format_macro_section(macro_results):
    """Format Ada KB macro context as markdown."""
    lines = []
    if not macro_results:
        lines.append("- No macro data available from Ada KB")
        return lines

    for section in macro_results:
        stype = section.get("type")
        data = section.get("data", [])
        if stype == "alerts" and data:
            lines.append("- **Recent Alerts:**")
            for a in data[:3]:
                sev = a.get("severity", "?").upper()
                lines.append(f"  - [{sev}] {a.get('ticker', '-')}: {a.get('event', 'N/A')[:80]}")
        elif stype == "research" and data:
            lines.append("- **Ada Research:**")
            for d in data[:2]:
                lines.append(f"  - {d.get('doc_name', '-')} ({d.get('create_time', '-')[:10]})")
                snippet = d.get("snippet", "")
                if snippet:
                    lines.append(f"    > {snippet[:120]}...")

    return lines


def generate_markdown(prop, source, location, flood, financial, kb_entries, macro, rent_estimate):
    """Generate full property analysis markdown using AGENTS.md template."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Build header
    if source == "sam":
        title = prop.get("project_name") or prop.get("address_full") or f"SAM-{prop.get('code', '?')}"
        prop_type = prop.get("type_name", "?")
        size_text = prop.get("size_text") or ""
        deed_type = prop.get("title_deed_type") or "?"
        price = float(prop.get("price_baht", 0))
        appraised = float(prop.get("price_baht", 0))  # SAM uses same price
        sqm = float(prop.get("size_sqm") or 0)
        rai = float(prop.get("size_rai") or 0)
        ngan = float(prop.get("size_ngan") or 0)
        wah = float(prop.get("size_wa") or 0)
        address = prop.get("address_full") or f"{prop.get('district', '')}, {prop.get('province', '')}"
        lat = float(prop["lat"]) if prop.get("lat") else None
        lon = float(prop["lng"]) if prop.get("lng") else None
        province = prop.get("province", "")
        district = prop.get("district", "")
        status = prop.get("status", "?")
        url = prop.get("source_url", "")
    else:  # LED
        title = prop.get("address") or f"LED-{prop.get('asset_id', '?')}"
        prop_type = prop.get("property_type", "?")
        size_text = f"{prop.get('size_rai', 0)}-{prop.get('size_ngan', 0)}-{prop.get('size_wa', 0)}"
        deed_type = prop.get("deed_type") or "?"
        price = float(prop.get("primary_price_satang", 0)) / 100  # satang → baht
        appraised_val = float(prop.get("enforcement_officer_price_satang") or prop.get("primary_price_satang", 0)) / 100
        appraised = appraised_val
        sqm = 0
        rai = float(prop.get("size_rai") or 0)
        ngan = float(prop.get("size_ngan") or 0)
        wah = float(prop.get("size_wa") or 0)
        address = prop.get("address") or f"{prop.get('ampur', '')}, {prop.get('province', '')}"
        lat = None
        lon = None
        province = prop.get("province", "")
        district = prop.get("ampur", "")
        status = prop.get("sale_status", "?")
        url = prop.get("source_url", "")

    # Determine area price for price per area
    total_sqm = to_sqm(rai, ngan, wah, max(0, sqm))
    price_per = ""
    if total_sqm > 0:
        price_per = f" ({format_thb(price / total_sqm)}/sqm)"

    # Compute discount
    discount_str = "N/A"
    if appraised and appraised > 0 and price < appraised:
        discount_str = f"{((appraised - price) / appraised * 100):.1f}%"

    # WHY BUY / WHY AVOID — heuristic from data
    buy_reasons = []
    avoid_reasons = []

    # Price discount
    if discount_str != "N/A":
        try:
            disc_val = float(discount_str.replace("%", ""))
            if disc_val >= 20:
                buy_reasons.append(f"Significant discount: **{discount_str}** below appraised value")
            elif disc_val >= 10:
                buy_reasons.append(f"Moderate discount: {discount_str} below appraised value")
        except ValueError:
            pass

    # Transit
    if location:
        rating = location.get("transit_rating", "")
        if rating == "PREMIUM":
            buy_reasons.append("Premium transit location (within 500m of BTS/MRT)")
        elif rating == "GOOD":
            buy_reasons.append("Good transit access (within 1km of BTS/MRT)")
        elif rating in ("FAR", "NO_STATION"):
            avoid_reasons.append("No nearby BTS/MRT station — limited transit access")

    # Flood
    if flood:
        risk = flood.get("risk", "UNKNOWN")
        if risk == "HIGH":
            avoid_reasons.append("🔴 **HIGH flood risk** — deal-breaker for ground floor")
        elif risk == "MEDIUM":
            avoid_reasons.append("🟡 Medium flood risk — check micro-location and building elevation")
        elif risk == "LOW":
            buy_reasons.append("🟢 Low flood risk area")

    # Rental yield
    if financial and financial.get("rental"):
        net_y = financial["rental"].get("net_yield_pct", 0)
        gross_y = financial["rental"].get("gross_yield_pct", 0)
        if gross_y >= 7:
            buy_reasons.append(f"Strong rental yield: **{gross_y}% gross** ({net_y}% net)")
        elif gross_y >= 5:
            buy_reasons.append(f"Decent rental yield: {gross_y}% gross")
        elif gross_y > 0 and gross_y < 4:
            avoid_reasons.append(f"Weak rental yield: {gross_y}% gross — below typical 4-5% threshold")

    # Title deed
    if deed_type and "โฉนด" in deed_type:
        buy_reasons.append(f"Full title deed ({deed_type}) — easier transfer")
    elif deed_type and ("นส.3" in deed_type or "น.ส.3" in deed_type):
        avoid_reasons.append(f"Limited title ({deed_type}) — check upgrade possibility")

    # Default avoids if none
    if not avoid_reasons:
        avoid_reasons.append("Standard NPA risks: verify legal status, property condition, and any occupants")

    if not buy_reasons:
        buy_reasons.append("Price may offer value vs market — verify with comparable sales")

    # Auto-verdict
    score = len(buy_reasons) - len(avoid_reasons)
    has_dealbreaker = any("deal-breaker" in r.lower() for r in avoid_reasons)
    if has_dealbreaker:
        verdict = "⚠️ AVOID"
    elif score >= 2:
        verdict = "✅ BUY"
    elif score >= 0:
        verdict = "👀 WATCH"
    else:
        verdict = "⚠️ AVOID"

    # Assemble markdown
    md = []
    md.append(f"## Property Analysis — {title}")
    md.append("")
    md.append(f"### VERDICT: {verdict}")
    md.append("")
    md.append(f"_Generated: {now} | Source: {source.upper()}_")
    md.append("")

    # Property Details
    md.append("### Property Details")
    md.append(f"- Type: {prop_type}")
    if size_text:
        md.append(f"- Size: {size_text}")
    elif total_sqm > 0:
        md.append(f"- Size: {total_sqm:.1f} sqm")
    md.append(f"- Title: {deed_type}")
    md.append(f"- Source: {source.upper()}")
    md.append(f"- Asking Price: {format_thb(price)}{price_per}")
    if appraised and appraised != price:
        md.append(f"- Appraised Value: {format_thb(appraised)}")
        md.append(f"- Discount: {discount_str} below appraisal")
    md.append(f"- Status: {status}")
    md.append(f"- Address: {address}")
    if url:
        md.append(f"- URL: {url}")
    md.append("")

    # WHY BUY
    md.append("### WHY BUY")
    for r in buy_reasons:
        md.append(f"- {r}")
    md.append("")

    # WHY AVOID
    md.append("### WHY AVOID")
    for r in avoid_reasons:
        md.append(f"- {r}")
    md.append("")

    # Location Score
    md.append("### Location Score")
    if location:
        md.extend(format_location_section(location))
    else:
        md.append("- ⚠️ No GPS coordinates — location analysis not available")
    if flood:
        md.extend(format_flood_section(flood))
    md.append("")

    # Financial Analysis
    md.append("### Financial Analysis")
    if financial:
        md.extend(format_financial_section(financial))
    else:
        md.append("- No financial analysis available")
    md.append("")

    # KB Comparables
    md.append("### Area Comparables (KB)")
    md.extend(format_kb_section(kb_entries))
    md.append("")

    # Macro Context
    md.append("### Macro Context (Ada KB)")
    md.extend(format_macro_section(macro))
    md.append("")

    # Bottom Line
    md.append("### Bottom Line")
    md.append(f"_{verdict}_ — {title} at {format_thb(price)}")
    key_points = []
    if location and location.get("transit_rating"):
        key_points.append(f"transit: {location['transit_rating']}")
    if flood and flood.get("risk"):
        key_points.append(f"flood: {flood['risk']}")
    if discount_str != "N/A":
        key_points.append(f"discount: {discount_str}")
    if financial and financial.get("rental"):
        key_points.append(f"yield: {financial['rental']['gross_yield_pct']}% gross")
    if key_points:
        md.append("Key metrics: " + ", ".join(key_points) + ".")
    md.append("⚠️ _Auto-generated analysis — verify all data points before making decisions._")
    md.append("")

    return "\n".join(md)


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------
def analyze(source, prop_id=None, asset_id=None, rent=None, common_fee=0, renovation=0, json_output=False):
    """Run the full analysis pipeline."""

    # 1. Fetch property
    if source == "sam":
        if not prop_id:
            raise ValueError("--id required for SAM source")
        rows = fetch_sam_property(prop_id)
        if not rows:
            raise ValueError(f"SAM property id={prop_id} not found")
        prop = rows[0]
    elif source == "led":
        if not asset_id:
            raise ValueError("--asset-id required for LED source")
        rows = fetch_led_property(asset_id)
        if not rows:
            raise ValueError(f"LED property asset_id={asset_id} not found")
        prop = rows[0]
    else:
        raise ValueError(f"Unknown source: {source}")

    # Extract common fields
    if source == "sam":
        lat = float(prop["lat"]) if prop.get("lat") else None
        lon = float(prop["lng"]) if prop.get("lng") else None
        price = float(prop.get("price_baht", 0))
        appraised = price  # SAM doesn't have separate appraisal
        sqm = float(prop.get("size_sqm") or 0)
        rai = float(prop.get("size_rai") or 0)
        ngan = float(prop.get("size_ngan") or 0)
        wah = float(prop.get("size_wa") or 0)
        province = prop.get("province", "")
        district = prop.get("district", "")
    else:
        lat = None  # LED properties don't have GPS
        lon = None
        price = float(prop.get("primary_price_satang", 0)) / 100
        appraised = float(prop.get("enforcement_officer_price_satang") or prop.get("primary_price_satang", 0)) / 100
        sqm = 0
        rai = float(prop.get("size_rai") or 0)
        ngan = float(prop.get("size_ngan") or 0)
        wah = float(prop.get("size_wa") or 0)
        province = prop.get("province", "")
        district = prop.get("ampur", "")

    # 2. Location intel (if GPS available)
    location = None
    if lat and lon:
        location = run_location_intel(lat, lon)

    # 3. Flood check
    flood = None
    if lat and lon:
        flood = run_flood_check(lat, lon, province=province)

    # 4. Financial calculations
    financial = run_financials(
        price, appraised,
        sqm=sqm, rai=rai, ngan=ngan, wah=wah,
        rent=rent, common_fee=common_fee, renovation=renovation,
    )

    # 5. KB comparables
    area_name = district or province or ""
    kb_entries = query_npa_kb(area_name)

    # 6. Ada KB macro
    macro = query_ada_macro()

    # 7. Output
    if json_output:
        result = {
            "property": prop,
            "source": source,
            "location": location,
            "flood": flood,
            "financial": financial,
            "kb_comparables": kb_entries,
            "macro_context": macro,
            "generated_at": datetime.now().isoformat(),
        }
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
    else:
        md = generate_markdown(prop, source, location, flood, financial, kb_entries, macro, rent)
        print(md)

    return prop


def main():
    parser = argparse.ArgumentParser(description="Automated NPA property analysis pipeline")
    parser.add_argument("--source", required=True, choices=["led", "sam"], help="Data source")
    parser.add_argument("--id", type=int, help="SAM property id (for --source sam)")
    parser.add_argument("--asset-id", help="LED asset_id (for --source led)")
    parser.add_argument("--rent", type=float, default=0, help="Estimated monthly rent (baht)")
    parser.add_argument("--common-fee", type=float, default=0, help="Monthly common fee (baht)")
    parser.add_argument("--renovation", type=float, default=0, help="Renovation cost estimate (baht)")
    parser.add_argument("--json", action="store_true", help="Output as JSON instead of markdown")

    args = parser.parse_args()

    analyze(
        source=args.source,
        prop_id=args.id,
        asset_id=args.asset_id,
        rent=args.rent if args.rent > 0 else None,
        common_fee=args.common_fee,
        renovation=args.renovation,
        json_output=args.json,
    )


if __name__ == "__main__":
    main()

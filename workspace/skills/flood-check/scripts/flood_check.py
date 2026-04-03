#!/usr/bin/env python3
"""Flood risk assessment for Thai NPA properties.

Uses hardcoded Bangkok flood risk zones + elevation heuristics.
"""

import argparse
import json
import math

# Bangkok flood risk zones (based on historical flood data)
# Risk levels: HIGH, MEDIUM, LOW
# Format: {"name": str, "lat_range": (min, max), "lon_range": (min, max), "risk": str, "reason": str}
FLOOD_ZONES = [
    # HIGH RISK — historically flood-prone areas
    {
        "name": "รังสิต-ธัญบุรี (Rangsit-Thanyaburi)",
        "lat_range": (13.95, 14.10),
        "lon_range": (100.58, 100.75),
        "risk": "HIGH",
        "reason": "Low-lying area, severe flooding in 2011, canal overflow risk",
    },
    {
        "name": "บางบัวทอง (Bang Bua Thong)",
        "lat_range": (13.88, 13.95),
        "lon_range": (100.38, 100.46),
        "risk": "HIGH",
        "reason": "Low elevation, drainage bottleneck, 2011 flood zone",
    },
    {
        "name": "นนทบุรี ฝั่งตะวันตก (Nonthaburi West)",
        "lat_range": (13.82, 13.90),
        "lon_range": (100.42, 100.50),
        "risk": "HIGH",
        "reason": "Low-lying along Chao Phraya, repeated flooding history",
    },
    {
        "name": "ลาดกระบัง-มีนบุรี (Lat Krabang-Min Buri)",
        "lat_range": (13.72, 13.80),
        "lon_range": (100.72, 100.85),
        "risk": "HIGH",
        "reason": "Eastern flood retention area, low elevation",
    },
    {
        "name": "สมุทรปราการ ชายทะเล (Samut Prakan Coast)",
        "lat_range": (13.50, 13.60),
        "lon_range": (100.55, 100.70),
        "risk": "HIGH",
        "reason": "Coastal subsidence, tidal flooding, sea level rise exposure",
    },
    {
        "name": "ดอนเมือง-หลักสี่ (Don Mueang-Lak Si)",
        "lat_range": (13.88, 13.95),
        "lon_range": (100.55, 100.63),
        "risk": "HIGH",
        "reason": "Airport area floods when canal capacity exceeded, 2011 severe",
    },
    # MEDIUM RISK
    {
        "name": "บางเขน-สายไหม (Bang Khen-Sai Mai)",
        "lat_range": (13.85, 13.92),
        "lon_range": (100.60, 100.68),
        "risk": "MEDIUM",
        "reason": "Moderate elevation, some canal overflow during heavy rain",
    },
    {
        "name": "บางกะปิ-บึงกุ่ม (Bang Kapi-Bueng Kum)",
        "lat_range": (13.76, 13.82),
        "lon_range": (100.60, 100.70),
        "risk": "MEDIUM",
        "reason": "Mixed elevation, localized flooding in low spots",
    },
    {
        "name": "ปทุมธานี (Pathum Thani)",
        "lat_range": (14.00, 14.10),
        "lon_range": (100.48, 100.60),
        "risk": "MEDIUM",
        "reason": "Near Rangsit canal system, varies by micro-location",
    },
    {
        "name": "บางพลัด-ตลิ่งชัน (Bang Phlat-Taling Chan)",
        "lat_range": (13.76, 13.82),
        "lon_range": (100.45, 100.51),
        "risk": "MEDIUM",
        "reason": "Canal-adjacent areas, moderate drainage capacity",
    },
    {
        "name": "สมุทรปราการ เหนือ (Samut Prakan North)",
        "lat_range": (13.60, 13.68),
        "lon_range": (100.58, 100.70),
        "risk": "MEDIUM",
        "reason": "Industrial area, moderate drainage, some subsidence",
    },
    # LOW RISK — elevated or well-drained areas
    {
        "name": "สุขุมวิท-สีลม Core (Sukhumvit-Silom Core)",
        "lat_range": (13.72, 13.75),
        "lon_range": (100.52, 100.59),
        "risk": "LOW",
        "reason": "Central Bangkok, good drainage infrastructure, elevated",
    },
    {
        "name": "สาทร-บางรัก (Sathorn-Bang Rak)",
        "lat_range": (13.71, 13.74),
        "lon_range": (100.51, 100.54),
        "risk": "LOW",
        "reason": "Well-maintained drainage, commercial district priority",
    },
    {
        "name": "อารีย์-พหลโยธิน (Ari-Phahon Yothin)",
        "lat_range": (13.77, 13.82),
        "lon_range": (100.54, 100.57),
        "risk": "LOW",
        "reason": "Slightly elevated, good drainage infrastructure",
    },
    {
        "name": "ทองหล่อ-เอกมัย (Thong Lo-Ekkamai)",
        "lat_range": (13.71, 13.73),
        "lon_range": (100.57, 100.60),
        "risk": "LOW",
        "reason": "Good drainage, elevated relative to surroundings",
    },
]

# Provincial flood risk (simplified)
PROVINCIAL_FLOOD_RISK = {
    "ภูเก็ต": {"risk": "LOW", "reason": "Island, good drainage, limited flood history except flash floods in hills"},
    "เชียงใหม่": {"risk": "MEDIUM", "reason": "Ping River flooding possible in rainy season (Aug-Oct), check proximity to river"},
    "กระบี่": {"risk": "LOW", "reason": "Coastal, generally well-drained, minor flash flood risk in monsoon"},
    "สงขลา": {"risk": "MEDIUM", "reason": "Hat Yai area has significant flood history, check specific location"},
    "สุราษฎร์ธานี": {"risk": "MEDIUM", "reason": "Southern monsoon flooding Nov-Jan, varies by district"},
    "แพร่": {"risk": "LOW", "reason": "Northern highland, limited flood risk except near Yom River"},
    "ตรัง": {"risk": "MEDIUM", "reason": "Southern monsoon zone, check proximity to rivers and low areas"},
    "พัทลุง": {"risk": "MEDIUM", "reason": "Thale Noi lake area floods seasonally, check elevation"},
    "นนทบุรี": {"risk": "MEDIUM", "reason": "Along Chao Phraya, risk varies greatly by specific location — check zone data"},
}


def check_flood_risk(lat, lon, province=None):
    """Assess flood risk for given coordinates."""
    result = {
        "coordinates": {"lat": lat, "lon": lon},
        "risk": "UNKNOWN",
        "zone_match": None,
        "reasons": [],
        "recommendations": [],
    }

    # Check hardcoded zones (Bangkok metro)
    for zone in FLOOD_ZONES:
        lat_min, lat_max = zone["lat_range"]
        lon_min, lon_max = zone["lon_range"]

        if lat_min <= lat <= lat_max and lon_min <= lon <= lon_max:
            result["risk"] = zone["risk"]
            result["zone_match"] = zone["name"]
            result["reasons"].append(zone["reason"])
            break

    # If no zone match, check provincial data
    if result["risk"] == "UNKNOWN" and province:
        prov_data = PROVINCIAL_FLOOD_RISK.get(province)
        if prov_data:
            result["risk"] = prov_data["risk"]
            result["reasons"].append(prov_data["reason"])

    # Add recommendations based on risk
    if result["risk"] == "HIGH":
        result["recommendations"] = [
            "DEAL-BREAKER for ground-floor units",
            "Verify flood insurance availability and cost",
            "Check if property was damaged in 2011 floods",
            "Ground-floor: heavy discount needed (30%+ below market)",
            "Upper floors may still be viable but consider resale risk",
            "Visit during rainy season (Aug-Oct) to observe drainage",
        ]
    elif result["risk"] == "MEDIUM":
        result["recommendations"] = [
            "Check specific micro-location (elevation, canal proximity)",
            "Verify building has flood barriers/raised ground floor",
            "Ground-floor discount of 10-15% recommended",
            "Ask neighbors about flooding history",
            "Search web for '[area name] น้ำท่วม' for recent incidents",
        ]
    elif result["risk"] == "LOW":
        result["recommendations"] = [
            "Low flood risk — not a major concern for this location",
            "Standard due diligence still applies",
            "Check for localized drainage issues (ask building management)",
        ]
    else:
        result["recommendations"] = [
            "No flood data available for this location",
            "Search web for '[province/district] น้ำท่วม ประวัติ'",
            "Check government flood maps at flood.gistda.or.th",
            "Ask local residents about flooding history",
        ]

    return result


def print_report(result):
    """Pretty-print flood risk report."""
    risk = result["risk"]
    risk_emoji = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "🟢", "UNKNOWN": "⚪"}.get(risk, "⚪")

    print(f"\n{'='*60}")
    print(f"FLOOD RISK ASSESSMENT")
    print(f"Coordinates: {result['coordinates']['lat']}, {result['coordinates']['lon']}")
    print(f"{'='*60}")

    print(f"\n  Risk Level: {risk_emoji} {risk}")
    if result.get("zone_match"):
        print(f"  Zone: {result['zone_match']}")

    if result["reasons"]:
        print(f"\n  Reasons:")
        for r in result["reasons"]:
            print(f"    - {r}")

    print(f"\n  Recommendations:")
    for r in result["recommendations"]:
        print(f"    - {r}")

    print(f"\n{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(description="Flood risk assessment for Thai properties")
    parser.add_argument("--lat", type=float, required=True, help="Latitude")
    parser.add_argument("--lon", type=float, required=True, help="Longitude")
    parser.add_argument("--province", help="Province name (for fallback lookup)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()
    result = check_flood_risk(args.lat, args.lon, province=args.province)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print_report(result)


if __name__ == "__main__":
    main()

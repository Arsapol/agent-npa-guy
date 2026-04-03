#!/usr/bin/env python3
"""Thai zoning and building control checker.

Based on:
- Bangkok Comprehensive Plan พ.ศ. 2556 (active as of April 2026)
  Source: ASA Excel table at download.asa.or.th/03media/04law/cpa/BMA_LandUse_2556.xls
- Building Control Act พ.ร.บ. ควบคุมอาคาร พ.ศ. 2522
- Ministerial Regulation No. 55 พ.ศ. 2543

Note: The 4th revision (ปรับปรุงครั้งที่ 4) is NOT yet in force — blocked by
Consumer Council lawsuit at Administrative Court (filed 20 Feb 2026).

Official GIS lookup: plludds.dpt.go.th/landuse/ (covers all provinces)
"""

import argparse
import json
import math

# =============================================================================
# Bangkok Comprehensive Plan พ.ศ. 2556 (3rd revision, currently active)
# Zone codes from the official color system.
# FAR/OSR values: confirmed from ASA reference where available,
# approximate (~) where not yet verified against the Excel table.
# =============================================================================

BANGKOK_ZONES = {
    # --- Residential: Yellow (เหลือง) = Low density ---
    "ย.1": {
        "name_th": "ที่อยู่อาศัยหนาแน่นน้อย ย.1",
        "name_en": "Low-Density Residential 1",
        "color": "Yellow (เหลือง)",
        "density": "Very low",
        "max_far": 1.5,
        "min_osr_pct": 20.0,
        "max_height_m": 12,
        "max_floors": 3,
        "permitted": ["บ้านเดี่ยว", "บ้านแฝด"],
        "prohibited": ["คอนโด", "อาคารสูง", "โรงงาน", "ห้างสรรพสินค้า"],
        "notes": "Outer suburbs. Strictest residential zone.",
    },
    "ย.2": {
        "name_th": "ที่อยู่อาศัยหนาแน่นน้อย ย.2",
        "name_en": "Low-Density Residential 2",
        "color": "Yellow (เหลือง)",
        "density": "Very low",
        "max_far": 1.5,
        "min_osr_pct": 20.0,
        "max_height_m": 12,
        "max_floors": 3,
        "permitted": ["บ้านเดี่ยว", "บ้านแฝด", "ทาวน์เฮาส์ (จำกัด)"],
        "prohibited": ["คอนโดสูง", "โรงงาน", "ห้างสรรพสินค้า"],
        "notes": "Suburban. Similar to ย.1 but slightly more flexibility.",
    },
    "ย.3": {
        "name_th": "ที่อยู่อาศัยหนาแน่นน้อย ย.3",
        "name_en": "Low-Density Residential 3",
        "color": "Yellow (เหลือง)",
        "density": "Low",
        "max_far": 2.5,  # Confirmed from ASA
        "min_osr_pct": 12.5,  # Confirmed from ASA
        "max_height_m": 23,
        "max_floors": 8,
        "permitted": ["บ้านเดี่ยว", "บ้านแฝด", "ทาวน์เฮาส์", "อาคารชุด ≤8 ชั้น"],
        "prohibited": ["คอนโดสูง >8 ชั้น", "โรงงาน", "ห้างสรรพสินค้าขนาดใหญ่"],
        "notes": "Transition zone. Max 23m / 8 floors.",
    },
    "ย.4": {
        "name_th": "ที่อยู่อาศัยหนาแน่นน้อย ย.4",
        "name_en": "Low-Density Residential 4",
        "color": "Yellow (เหลือง)",
        "density": "Low",
        "max_far": 2.5,
        "min_osr_pct": 12.5,
        "max_height_m": 23,
        "max_floors": 8,
        "permitted": ["บ้านเดี่ยว", "บ้านแฝด", "ทาวน์เฮาส์", "อาคารชุดขนาดเล็ก"],
        "prohibited": ["คอนโดสูง", "โรงงาน"],
        "notes": "Similar to ย.3 with minor use differences.",
    },
    # --- Residential: Orange (ส้ม) = Medium density ---
    "ย.5": {
        "name_th": "ที่อยู่อาศัยหนาแน่นปานกลาง ย.5",
        "name_en": "Medium-Density Residential 5",
        "color": "Orange (ส้ม)",
        "density": "Medium-low",
        "max_far": 3.5,
        "min_osr_pct": 10.0,
        "max_height_m": None,
        "max_floors": None,
        "permitted": ["บ้านเดี่ยว", "ทาวน์เฮาส์", "คอนโด", "สำนักงานขนาดเล็ก"],
        "prohibited": ["โรงงาน", "คลังสินค้าขนาดใหญ่"],
        "notes": "Medium density. Height controlled by FAR + road width rule.",
    },
    "ย.6": {
        "name_th": "ที่อยู่อาศัยหนาแน่นปานกลาง ย.6",
        "name_en": "Medium-Density Residential 6",
        "color": "Orange (ส้ม)",
        "density": "Medium",
        "max_far": 4.0,
        "min_osr_pct": 7.5,
        "max_height_m": None,
        "max_floors": None,
        "permitted": ["บ้านเดี่ยว", "ทาวน์เฮาส์", "คอนโด", "สำนักงาน", "ร้านค้า"],
        "prohibited": ["โรงงาน"],
        "notes": "Near transit corridors. Mid-rise condos common.",
    },
    "ย.7": {
        "name_th": "ที่อยู่อาศัยหนาแน่นปานกลาง ย.7",
        "name_en": "Medium-Density Residential 7",
        "color": "Orange (ส้ม)",
        "density": "Medium",
        "max_far": 5.0,  # Confirmed from ASA
        "min_osr_pct": 6.0,  # Confirmed from ASA
        "max_height_m": None,
        "max_floors": None,
        "permitted": ["คอนโด", "สำนักงาน", "ร้านค้า", "โรงแรม (จำกัด)"],
        "prohibited": ["โรงงาน"],
        "notes": "Along BTS/MRT lines. High-rise condos common.",
    },
    "ย.8": {
        "name_th": "ที่อยู่อาศัยหนาแน่นปานกลาง ย.8",
        "name_en": "Medium-Density Residential 8",
        "color": "Orange (ส้ม)",
        "density": "Medium-high",
        "max_far": 5.0,
        "min_osr_pct": 6.0,
        "max_height_m": None,
        "max_floors": None,
        "permitted": ["คอนโดสูง", "สำนักงาน", "ร้านค้า", "โรงแรม"],
        "prohibited": ["โรงงาน"],
        "notes": "Inner suburban ring along transit.",
    },
    # --- Residential: Brown (น้ำตาล) = High density ---
    "ย.9": {
        "name_th": "ที่อยู่อาศัยหนาแน่นมาก ย.9",
        "name_en": "High-Density Residential 9",
        "color": "Brown (น้ำตาล)",
        "density": "High",
        "max_far": 7.0,  # Confirmed from ASA
        "min_osr_pct": 4.5,  # Confirmed from ASA
        "max_height_m": None,
        "max_floors": None,
        "permitted": ["คอนโดสูง", "สำนักงาน", "ร้านค้า", "โรงแรม", "ห้างสรรพสินค้า"],
        "prohibited": ["โรงงาน"],
        "notes": "Inner city high-density. Tall high-rises allowed.",
    },
    "ย.10": {
        "name_th": "ที่อยู่อาศัยหนาแน่นมาก ย.10",
        "name_en": "High-Density Residential 10",
        "color": "Brown (น้ำตาล)",
        "density": "High",
        "max_far": 8.0,
        "min_osr_pct": 4.0,
        "max_height_m": None,
        "max_floors": None,
        "permitted": ["คอนโดสูง", "สำนักงาน", "ร้านค้า", "โรงแรม", "ห้างสรรพสินค้า"],
        "prohibited": ["โรงงาน"],
        "notes": "Highest-density residential. Near CBD.",
    },
    # --- Commercial: Red (แดง) ---
    "พ.1": {
        "name_th": "พาณิชยกรรม พ.1",
        "name_en": "Commercial 1",
        "color": "Red (แดง)",
        "density": "Commercial",
        "max_far": 6.0,
        "min_osr_pct": 5.0,
        "max_height_m": None,
        "max_floors": None,
        "permitted": ["ร้านค้า", "สำนักงาน", "โรงแรม", "คอนโด", "ห้างสรรพสินค้า"],
        "prohibited": ["โรงงานขนาดใหญ่"],
        "notes": "Neighborhood commercial center.",
    },
    "พ.2": {
        "name_th": "พาณิชยกรรม พ.2",
        "name_en": "Commercial 2",
        "color": "Red (แดง)",
        "density": "Commercial",
        "max_far": 6.0,
        "min_osr_pct": 5.0,
        "max_height_m": None,
        "max_floors": None,
        "permitted": ["ร้านค้า", "สำนักงาน", "โรงแรม", "คอนโดสูง", "ห้างสรรพสินค้า"],
        "prohibited": ["โรงงานขนาดใหญ่"],
        "notes": "District commercial. Similar to พ.1 with more uses.",
    },
    "พ.3": {
        "name_th": "พาณิชยกรรม พ.3",
        "name_en": "Commercial 3",
        "color": "Red (แดง)",
        "density": "Commercial",
        "max_far": 7.0,
        "min_osr_pct": 4.5,
        "max_height_m": None,
        "max_floors": None,
        "permitted": ["ร้านค้า", "สำนักงานขนาดใหญ่", "โรงแรม", "คอนโดสูง", "ศูนย์การค้า"],
        "prohibited": ["โรงงาน"],
        "notes": "Major commercial areas.",
    },
    "พ.4": {
        "name_th": "พาณิชยกรรม พ.4",
        "name_en": "Commercial 4 (CBD)",
        "color": "Red (แดง)",
        "density": "CBD",
        "max_far": 8.0,
        "min_osr_pct": 4.0,
        "max_height_m": None,
        "max_floors": None,
        "permitted": ["ทุกประเภท (ยกเว้นโรงงาน)", "อาคารสูงพิเศษ"],
        "prohibited": ["โรงงาน"],
        "notes": "CBD. Siam, Silom, Ratchaprasong, Sathorn, Asok.",
    },
    "พ.5": {
        "name_th": "พาณิชยกรรม พ.5",
        "name_en": "Commercial 5",
        "color": "Red (แดง)",
        "density": "Commercial",
        "max_far": 7.0,  # Confirmed from ASA
        "min_osr_pct": 4.5,  # Confirmed from ASA
        "max_height_m": None,
        "max_floors": None,
        "permitted": ["ร้านค้า", "สำนักงาน", "โรงแรม", "คอนโดสูง"],
        "prohibited": ["โรงงาน"],
        "notes": "Secondary commercial. Along major roads.",
    },
    # --- Industrial: Purple (ม่วง) ---
    "อ.1": {
        "name_th": "อุตสาหกรรม อ.1",
        "name_en": "Light Industrial",
        "color": "Purple (ม่วง)",
        "density": "Industrial",
        "max_far": 2.0,
        "min_osr_pct": 15.0,
        "max_height_m": 23,
        "max_floors": None,
        "permitted": ["โรงงานขนาดเล็ก-กลาง", "คลังสินค้า", "ที่อยู่อาศัย (จำกัด)"],
        "prohibited": ["คอนโดสูง", "ห้างสรรพสินค้า", "โรงแรม"],
        "notes": "Light industrial. Limited residential. Check pollution risk.",
    },
    "อ.2": {
        "name_th": "อุตสาหกรรมหนัก อ.2",
        "name_en": "Heavy Industrial",
        "color": "Dark Purple (ม่วงเข้ม)",
        "density": "Heavy Industrial",
        "max_far": 1.5,
        "min_osr_pct": 20.0,
        "max_height_m": 23,
        "max_floors": None,
        "permitted": ["โรงงานขนาดใหญ่", "คลังสินค้า"],
        "prohibited": ["ที่อยู่อาศัย", "โรงเรียน", "โรงพยาบาล"],
        "notes": "Heavy industrial. NO residential. AVOID for housing investment.",
    },
    # --- Agricultural: Green (เขียว) ---
    "ก.1": {
        "name_th": "อนุรักษ์ชนบทและเกษตรกรรม ก.1",
        "name_en": "Agricultural Conservation 1",
        "color": "Green (เขียว)",
        "density": "Very low",
        "max_far": 0.5,
        "min_osr_pct": 50.0,
        "max_height_m": 9,
        "max_floors": 2,
        "permitted": ["เกษตรกรรม", "บ้านเดี่ยว (จำกัด)"],
        "prohibited": ["คอนโด", "โรงงาน", "พาณิชยกรรม", "อาคารสูง"],
        "notes": "Agricultural. Max 2 floors / 9m. Very restricted.",
    },
    "ก.2": {
        "name_th": "ชนบทและเกษตรกรรม ก.2",
        "name_en": "Rural/Agricultural 2",
        "color": "Light Green (เขียวอ่อน)",
        "density": "Very low",
        "max_far": 1.0,
        "min_osr_pct": 40.0,
        "max_height_m": 12,
        "max_floors": 3,
        "permitted": ["เกษตรกรรม", "บ้านเดี่ยว", "บ้านแฝด"],
        "prohibited": ["คอนโดสูง", "โรงงานขนาดใหญ่", "ห้างสรรพสินค้า"],
        "notes": "Rural. Max 3 floors / 12m.",
    },
    # --- Government / Special ---
    "ศ.1": {
        "name_th": "อนุรักษ์ศิลปวัฒนธรรม ศ.1",
        "name_en": "Cultural Conservation 1 (Rattanakosin)",
        "color": "Special",
        "density": "Low",
        "max_far": 4.0,
        "min_osr_pct": 10.0,
        "max_height_m": 16,
        "max_floors": None,
        "permitted": ["ที่อยู่อาศัย", "ร้านค้าขนาดเล็ก", "สถาบัน"],
        "prohibited": ["อาคารสูง", "โรงงาน", "ห้างสรรพสินค้า"],
        "notes": "Rattanakosin area. Strict height limit to protect skyline.",
    },
}

# Building height rule: max height = 2x road width (กฎกระทรวง ฉบับที่ 55)
# Road width < 10m → max 23m regardless
ROAD_WIDTH_HEIGHT_RULE = "Max building height = 2x road width. Road <10m → max 23m."

# EIA thresholds
EIA_THRESHOLDS = {
    "condo_units": 80,
    "condo_area_sqm": 4000,
    "housing_plots": 500,
    "housing_area_rai": 100,
    "note": "EIA triggered by unit count or area, NOT by height. 23m = high-rise classification only.",
}

# FAR Bonus system (current plan + proposed 4th revision)
FAR_BONUS = [
    {"condition": "Low-income housing provision", "bonus_pct": "5-20%"},
    {"condition": "Public open space / parks", "bonus_pct": "Up to 20% (max 5x open space area)"},
    {"condition": "Extra parking within 500m of transit station", "bonus_pct": "Up to 20% (max 30 sqm/space)"},
    {"condition": "Water retention area (min 1 cu.m./50 sqm)", "bonus_pct": "Varies"},
]

# Airport safety zones
AIRPORT_RESTRICTIONS = [
    {
        "name": "สุวรรณภูมิ (Suvarnabhumi)",
        "lat": 13.6900, "lon": 100.7501,
        "zones": [
            {"radius_m": 4000, "max_height_m": 45, "note": "Inner horizontal surface (ICAO)"},
            {"radius_m": 8000, "max_height_m": 60, "note": "Conical surface"},
            {"radius_m": 16000, "max_height_m": 150, "note": "Outer approach surface"},
        ],
        "authority": "CAAT (สำนักงานการบินพลเรือนแห่งประเทศไทย)",
    },
    {
        "name": "ดอนเมือง (Don Mueang)",
        "lat": 13.9133, "lon": 100.6070,
        "zones": [
            {"radius_m": 4610, "max_height_m": 45, "note": "45m restriction zone (~4.61km from runway)"},
            {"radius_m": 8000, "max_height_m": 60, "note": "Conical surface"},
            {"radius_m": 16000, "max_height_m": 150, "note": "Outer approach surface"},
        ],
        "authority": "CAAT",
    },
]

# Approximate area → zone mapping for key Bangkok areas
AREA_ZONE_MAP = [
    # CBD
    {"area": "สยาม-ราชประสงค์", "zone": "พ.4", "lat_range": (13.742, 13.750), "lon_range": (100.530, 100.545)},
    {"area": "สีลม-สาทร", "zone": "พ.4", "lat_range": (13.718, 13.732), "lon_range": (100.518, 100.540)},
    {"area": "สุขุมวิทต้น (1-39)", "zone": "พ.3", "lat_range": (13.734, 13.745), "lon_range": (100.548, 100.570)},
    {"area": "อโศก-เพชรบุรี", "zone": "พ.3", "lat_range": (13.736, 13.752), "lon_range": (100.558, 100.575)},
    {"area": "รัชดาภิเษก-พระราม 9", "zone": "พ.2", "lat_range": (13.755, 13.770), "lon_range": (100.560, 100.575)},
    # High-density residential (Brown)
    {"area": "สุขุมวิทกลาง (39-63)", "zone": "ย.9", "lat_range": (13.720, 13.735), "lon_range": (100.565, 100.590)},
    {"area": "อารีย์-สะพานควาย", "zone": "ย.9", "lat_range": (13.778, 13.800), "lon_range": (100.540, 100.555)},
    {"area": "ทองหล่อ-เอกมัย", "zone": "ย.9", "lat_range": (13.715, 13.730), "lon_range": (100.575, 100.590)},
    # Medium-density (Orange)
    {"area": "อ่อนนุช-บางจาก", "zone": "ย.7", "lat_range": (13.690, 13.710), "lon_range": (100.598, 100.610)},
    {"area": "พระโขนง-บางนา", "zone": "ย.6", "lat_range": (13.660, 13.720), "lon_range": (100.590, 100.610)},
    {"area": "ลาดพร้าว", "zone": "ย.6", "lat_range": (13.800, 13.830), "lon_range": (100.570, 100.590)},
    {"area": "จตุจักร", "zone": "ย.7", "lat_range": (13.795, 13.815), "lon_range": (100.550, 100.575)},
    {"area": "รามคำแหง", "zone": "ย.5", "lat_range": (13.740, 13.770), "lon_range": (100.590, 100.640)},
    {"area": "บางกะปิ", "zone": "ย.5", "lat_range": (13.760, 13.780), "lon_range": (100.610, 100.640)},
    # Low-density (Yellow)
    {"area": "มีนบุรี", "zone": "ย.3", "lat_range": (13.790, 13.830), "lon_range": (100.700, 100.760)},
    {"area": "ลาดกระบัง", "zone": "ย.3", "lat_range": (13.710, 13.740), "lon_range": (100.710, 100.760)},
    {"area": "บางแค-หนองแขม", "zone": "ย.3", "lat_range": (13.700, 13.730), "lon_range": (100.380, 100.420)},
    {"area": "ดอนเมือง-หลักสี่", "zone": "ย.3", "lat_range": (13.880, 13.940), "lon_range": (100.550, 100.630)},
    # Agricultural (Green)
    {"area": "หนองจอก", "zone": "ก.2", "lat_range": (13.830, 13.880), "lon_range": (100.800, 100.870)},
    {"area": "ทุ่งครุ-บางขุนเทียน", "zone": "ก.1", "lat_range": (13.580, 13.640), "lon_range": (100.410, 100.470)},
    # Nonthaburi
    {"area": "นนทบุรีเมือง", "zone": "ย.7", "lat_range": (13.840, 13.870), "lon_range": (100.490, 100.520)},
    {"area": "บางบัวทอง", "zone": "ย.3", "lat_range": (13.880, 13.930), "lon_range": (100.380, 100.440)},
    {"area": "ปากเกร็ด", "zone": "ย.5", "lat_range": (13.880, 13.920), "lon_range": (100.490, 100.540)},
    # Industrial
    {"area": "บางพลี (สมุทรปราการ)", "zone": "อ.1", "lat_range": (13.580, 13.630), "lon_range": (100.680, 100.730)},
]


def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def lookup_zone(lat, lon):
    for area in AREA_ZONE_MAP:
        lat_min, lat_max = area["lat_range"]
        lon_min, lon_max = area["lon_range"]
        if lat_min <= lat <= lat_max and lon_min <= lon <= lon_max:
            zone_code = area["zone"]
            zone_data = BANGKOK_ZONES.get(zone_code, {})
            return {"area_name": area["area"], "zone_code": zone_code, **zone_data}
    return None


def check_airport_restriction(lat, lon):
    restrictions = []
    for airport in AIRPORT_RESTRICTIONS:
        dist = haversine(lat, lon, airport["lat"], airport["lon"])
        for zone in airport["zones"]:
            if dist <= zone["radius_m"]:
                restrictions.append({
                    "airport": airport["name"],
                    "distance_m": round(dist),
                    "max_height_m": zone["max_height_m"],
                    "note": zone["note"],
                    "authority": airport["authority"],
                })
                break
    return restrictions


def check_eia_required(units=None, area_sqm=None, plots=None, area_rai=None):
    """Check if EIA is required."""
    reasons = []
    if units and units >= EIA_THRESHOLDS["condo_units"]:
        reasons.append(f"Condo with {units} units (threshold: {EIA_THRESHOLDS['condo_units']})")
    if area_sqm and area_sqm >= EIA_THRESHOLDS["condo_area_sqm"]:
        reasons.append(f"Usable area {area_sqm:,} sqm (threshold: {EIA_THRESHOLDS['condo_area_sqm']:,})")
    if plots and plots >= EIA_THRESHOLDS["housing_plots"]:
        reasons.append(f"Housing with {plots} plots (threshold: {EIA_THRESHOLDS['housing_plots']})")
    if area_rai and area_rai >= EIA_THRESHOLDS["housing_area_rai"]:
        reasons.append(f"Land area {area_rai} rai (threshold: {EIA_THRESHOLDS['housing_area_rai']})")
    return {"required": len(reasons) > 0, "reasons": reasons}


def zoning_report(lat, lon, property_type=None, road_width_m=None):
    result = {
        "coordinates": {"lat": lat, "lon": lon},
        "plan_version": "ผังเมืองรวมกรุงเทพมหานคร พ.ศ. 2556 (active)",
        "plan_note": "4th revision blocked by court challenge (Feb 2026). 2013 plan remains in force.",
        "zone": None,
        "airport_restrictions": [],
        "building_height_rule": ROAD_WIDTH_HEIGHT_RULE,
        "eia_thresholds": EIA_THRESHOLDS,
        "far_bonus": FAR_BONUS,
        "assessment": [],
    }

    zone = lookup_zone(lat, lon)
    if zone:
        result["zone"] = zone

        if property_type:
            pt_lower = property_type.lower()
            prohibited = [p.lower() for p in zone.get("prohibited", [])]
            permitted = [p.lower() for p in zone.get("permitted", [])]
            is_prohibited = any(pt_lower in p or p in pt_lower for p in prohibited)
            is_permitted = any(pt_lower in p or p in pt_lower for p in permitted)

            if is_prohibited:
                result["assessment"].append(
                    f"⚠️ RESTRICTED: '{property_type}' may be prohibited in zone {zone['zone_code']}"
                )
            elif is_permitted:
                result["assessment"].append(
                    f"✅ PERMITTED: '{property_type}' is allowed in zone {zone['zone_code']}"
                )

        if road_width_m:
            max_h = road_width_m * 2
            if road_width_m < 10:
                max_h = 23
            result["assessment"].append(
                f"📏 Road width {road_width_m}m → max building height {max_h}m (กฎกระทรวง ฉบับที่ 55)"
            )
    else:
        result["assessment"].append(
            "Zone data not available for this exact location. "
            "Use official GIS: plludds.dpt.go.th/landuse/"
        )

    airport_restrictions = check_airport_restriction(lat, lon)
    result["airport_restrictions"] = airport_restrictions
    for ar in airport_restrictions:
        result["assessment"].append(
            f"✈️ AIRPORT: {ar['airport']} — {ar['distance_m']}m away. "
            f"Max height: {ar['max_height_m']}m. Contact: {ar['authority']}"
        )

    return result


def print_report(result):
    print(f"\n{'='*65}")
    print(f"ZONING & BUILDING CONTROL REPORT")
    lat, lon = result["coordinates"]["lat"], result["coordinates"]["lon"]
    print(f"Coordinates: {lat}, {lon}")
    print(f"Plan: {result['plan_version']}")
    print(f"{'='*65}")

    zone = result.get("zone")
    if zone:
        print(f"\n--- Zone: {zone.get('zone_code', '?')} ({zone.get('color', '')}) ---")
        print(f"  {zone.get('name_th', 'N/A')}")
        print(f"  {zone.get('name_en', 'N/A')}")
        print(f"  Area: {zone.get('area_name', 'N/A')}")
        print(f"  Density: {zone.get('density', 'N/A')}")

        print(f"\n  Building Controls:")
        far = zone.get('max_far')
        osr = zone.get('min_osr_pct')
        height = zone.get('max_height_m')
        floors = zone.get('max_floors')
        print(f"    FAR: {far}" if far else "    FAR: See regulations")
        print(f"    OSR: {osr}%" if osr else "    OSR: See regulations")
        print(f"    Max Height: {height}m" if height else "    Max Height: Controlled by FAR + road width rule")
        print(f"    Max Floors: {floors}" if floors else "    Max Floors: Controlled by FAR + height")

        print(f"\n  Permitted:")
        for p in zone.get("permitted", []):
            print(f"    ✅ {p}")
        print(f"  Prohibited:")
        for p in zone.get("prohibited", []):
            print(f"    ❌ {p}")
        if zone.get("notes"):
            print(f"  Notes: {zone['notes']}")
    else:
        print(f"\n  ⚠️ Zone data not available — use official GIS tools below")

    if result["airport_restrictions"]:
        print(f"\n--- Airport Restrictions ---")
        for ar in result["airport_restrictions"]:
            print(f"  ✈️ {ar['airport']}: {ar['distance_m']}m away → max {ar['max_height_m']}m")

    print(f"\n--- Building Height Rule ---")
    print(f"  {result['building_height_rule']}")

    print(f"\n--- EIA Thresholds ---")
    print(f"  Condo: ≥{EIA_THRESHOLDS['condo_units']} units OR ≥{EIA_THRESHOLDS['condo_area_sqm']:,} sqm")
    print(f"  Housing: ≥{EIA_THRESHOLDS['housing_plots']} plots OR ≥{EIA_THRESHOLDS['housing_area_rai']} rai")

    if result["assessment"]:
        print(f"\n--- Assessment ---")
        for a in result["assessment"]:
            print(f"  {a}")

    print(f"\n--- Official Verification ---")
    print(f"  🌐 GIS (all provinces): plludds.dpt.go.th/landuse/")
    print(f"  🌐 Bangkok GIS: cityplangis.bangkok.go.th")
    print(f"  📱 App: 'Check ผังเมือง กทม' (App Store / Google Play)")
    print(f"  📱 App: 'DPT Landuse Plan' (all provinces)")
    print(f"  📊 ASA reference: download.asa.or.th/03media/04law/cpa/BMA_LandUse_2556.xls")
    print(f"  ⚖️ Plan status note: {result['plan_note']}")

    print(f"\n{'='*65}\n")


def main():
    parser = argparse.ArgumentParser(description="Thai zoning & building control checker")
    parser.add_argument("--lat", type=float, required=True, help="Latitude")
    parser.add_argument("--lon", type=float, required=True, help="Longitude")
    parser.add_argument("--type", dest="property_type", help="Property type to check")
    parser.add_argument("--road-width", type=float, help="Road width in meters (for height calc)")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--zone", help="Look up zone code directly (e.g. ย.7, พ.4)")

    args = parser.parse_args()

    if args.zone:
        zone_data = BANGKOK_ZONES.get(args.zone)
        if zone_data:
            if args.json:
                print(json.dumps({"zone_code": args.zone, **zone_data}, ensure_ascii=False, indent=2))
            else:
                print(f"\nZone {args.zone} — {zone_data['color']}")
                print(f"  {zone_data['name_th']}")
                print(f"  FAR: {zone_data['max_far']} | OSR: {zone_data['min_osr_pct']}%")
                h = zone_data['max_height_m']
                print(f"  Max Height: {h}m" if h else "  Max Height: FAR + road width controlled")
                f = zone_data['max_floors']
                print(f"  Max Floors: {f}" if f else "  Max Floors: FAR controlled")
        else:
            print(f"Unknown zone: {args.zone}")
            print(f"Available: {', '.join(sorted(BANGKOK_ZONES.keys()))}")
        return

    result = zoning_report(args.lat, args.lon, property_type=args.property_type, road_width_m=args.road_width)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
    else:
        print_report(result)


if __name__ == "__main__":
    main()

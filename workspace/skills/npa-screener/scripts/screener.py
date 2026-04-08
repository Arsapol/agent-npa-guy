"""
NPA Condo Screener — Multi-provider screening pipeline.

Queries all 6 NPA providers for condos in target provinces,
cross-references with market sources (Hipflat/PropertyHub/DDProperty/ZMyHome),
and applies the 4-gate investment framework from AGENTS.md.

Usage:
    python screener.py                          # Full screening
    python screener.py --province กรุงเทพมหานคร  # Single province
    python screener.py --max-price 3000000       # Price cap
    python screener.py --top 20                  # Top N results
"""

import asyncio
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

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

DB_URL = os.getenv(
    "DATABASE_URL", "postgresql://arsapolm@localhost:5432/npa_kb"
)

TARGET_PROVINCES = [
    "กรุงเทพมหานคร",
    "ปทุมธานี",
    "สมุทรปราการ",
    "นนทบุรี",
]

# Condo type strings per provider
CONDO_TYPES = {
    "sam": ["ห้องชุดพักอาศัย"],
    "bam": ["ห้องชุดพักอาศัย"],
    "jam": ["คอนโดมิเนียม"],
    "ktb": ["คอนโดมีเนียม/ห้องชุด"],
    "kbank": ["05 คอนโดมิเนียม"],
    "led": ["ห้องชุด"],
}

# ---------------------------------------------------------------------------
# Education Anchors (lat, lon, name, type, enrollment_estimate)
# ---------------------------------------------------------------------------

EDUCATION_ANCHORS = [
    # Universities
    (13.8468, 100.5714, "มหาวิทยาลัยเกษตรศาสตร์", "university", 35000),
    (13.7325, 100.5288, "จุฬาลงกรณ์มหาวิทยาลัย", "university", 38000),
    (13.7579, 100.5967, "มหาวิทยาลัยรามคำแหง", "university", 40000),
    (13.7652, 100.5701, "NIDA", "university", 12000),
    (13.7940, 100.5494, "มหาวิทยาลัยธุรกิจบัณฑิตย์", "university", 15000),
    (13.6550, 100.4940, "มหาวิทยาลัยธนบุรี", "university", 8000),
    (13.6520, 100.4960, "มหาวิทยาลัยเทคโนโลยีราชมงคลกรุงเทพ", "university", 12000),
    (13.7506, 100.4950, "มหาวิทยาลัยศิลปากร ท่าพระ", "university", 10000),
    (13.7395, 100.5600, "มหาวิทยาลัยศรีนครินทรวิโรฒ", "university", 25000),
    (13.6500, 100.6400, "ABAC สุวรรณภูมิ", "university", 20000),
    (13.8700, 100.5900, "มหาวิทยาลัยศรีปทุม", "university", 15000),
    (13.8730, 100.5860, "มหาวิทยาลัยกรุงเทพ รังสิต", "university", 27000),
    (13.8900, 100.5100, "มหาวิทยาลัยสุโขทัยธรรมาธิราช", "university", 10000),
    (13.9600, 100.5340, "มหาวิทยาลัยรังสิต", "university", 30000),
    (13.8820, 100.5660, "มหาวิทยาลัยธรรมศาสตร์ รังสิต", "university", 35000),
    # International Schools
    (13.7395, 100.5545, "NIST สุขุมวิท 15", "intl_school", 1700),
    (13.7160, 100.5240, "St.Andrews Sathorn", "intl_school", 1200),
    (13.7350, 100.5650, "Anglo Singapore สุขุมวิท 31", "intl_school", 800),
    (13.6870, 100.6165, "Bangkok Patana สุขุมวิท 105", "intl_school", 2600),
    (13.9110, 100.5110, "ISB ปากเกร็ด", "intl_school", 1900),
    (13.7080, 100.4965, "Shrewsbury เจริญนคร", "intl_school", 1800),
    (13.6550, 100.6750, "VERSO บางนา", "intl_school", 600),
    (13.7050, 100.6480, "Wells International On Nut", "intl_school", 500),
    (13.6480, 100.6470, "Concordian บางนา กม.7", "intl_school", 1200),
    (13.6740, 100.6230, "St.Andrews สุขุมวิท 107", "intl_school", 800),
    (13.6930, 100.5030, "KIS International", "intl_school", 700),
    (13.7810, 100.5210, "St.Andrews Dusit", "intl_school", 500),
    # Thai Schools
    (13.7284, 100.5345, "อัสสัมชัญคอนแวนต์ สีลม", "thai_school", 3000),
    (13.7395, 100.5600, "สาธิต มศว ประสานมิตร", "thai_school", 3500),
    (13.7284, 100.5280, "กรุงเทพคริสเตียน สีลม", "thai_school", 4000),
    (13.8030, 100.5600, "หอวัง จตุจักร", "thai_school", 4000),
    (13.7400, 100.5900, "บดินทรเดชา สุขุมวิท", "thai_school", 5000),
    (13.7450, 100.5290, "สาธิตปทุมวัน", "thai_school", 2500),
    (13.8468, 100.5714, "สาธิตเกษตร", "thai_school", 3000),
    (13.7260, 100.5220, "อัสสัมชัญ บางรัก", "thai_school", 5000),
    (13.7340, 100.5288, "สาธิตจุฬาฯ", "thai_school", 2500),
    (13.7360, 100.5280, "เตรียมอุดมศึกษา ปทุมวัน", "thai_school", 4000),
    (13.7700, 100.5500, "สตรีวิทยา ดินแดง", "thai_school", 4000),
    (13.7810, 100.5130, "เซนต์คาเบรียล สามเสน", "thai_school", 3000),
    (13.7480, 100.4930, "ราชินี ท่าเตียน", "thai_school", 2000),
    (13.7284, 100.5340, "เซนต์โยเซฟคอนเวนต์ สีลม", "thai_school", 2000),
]

# ---------------------------------------------------------------------------
# BTS/MRT Stations (lat, lon, name)
# ---------------------------------------------------------------------------

TRANSIT_STATIONS = [
    # BTS Sukhumvit
    (13.9326, 100.6469, "คูคต"),
    (13.8768, 100.6062, "สะพานใหม่"),
    (13.8027, 100.5536, "หมอชิต"),
    (13.7939, 100.5494, "สะพานควาย"),
    (13.7797, 100.5447, "อารีย์"),
    (13.7720, 100.5417, "สนามเป้า"),
    (13.7627, 100.5374, "อนุสาวรีย์"),
    (13.7565, 100.5347, "พญาไท"),
    (13.7517, 100.5318, "ราชเทวี"),
    (13.7454, 100.5341, "สยาม"),
    (13.7440, 100.5430, "ชิดลม"),
    (13.7439, 100.5480, "เพลินจิต"),
    (13.7404, 100.5554, "นานา"),
    (13.7369, 100.5606, "อโศก"),
    (13.7303, 100.5696, "พร้อมพงษ์"),
    (13.7248, 100.5783, "ทองหล่อ"),
    (13.7194, 100.5855, "เอกมัย"),
    (13.7152, 100.5913, "พระโขนง"),
    (13.7059, 100.6012, "อ่อนนุช"),
    (13.6965, 100.6045, "บางจาก"),
    (13.6893, 100.6102, "ปุณณวิถี"),
    (13.6798, 100.6098, "อุดมสุข"),
    (13.6685, 100.6048, "บางนา"),
    (13.6600, 100.6011, "แบริ่ง"),
    (13.6458, 100.5955, "สำโรง"),
    (13.5932, 100.6393, "เคหะฯ"),
    # BTS Silom
    (13.7463, 100.5290, "สนามกีฬา"),
    (13.7405, 100.5394, "ราชดำริ"),
    (13.7284, 100.5345, "ศาลาแดง"),
    (13.7231, 100.5290, "ช่องนนทรี"),
    (13.7191, 100.5193, "สุรศักดิ์"),
    (13.7186, 100.5141, "สะพานตากสิน"),
    (13.7208, 100.5032, "กรุงธนบุรี"),
    (13.7213, 100.4943, "วงเวียนใหญ่"),
    (13.7207, 100.4573, "บางหว้า"),
    # MRT Blue
    (13.7258, 100.4665, "ท่าพระ"),
    (13.7375, 100.5168, "หัวลำโพง"),
    (13.7325, 100.5288, "สามย่าน"),
    (13.7291, 100.5360, "สีลม"),
    (13.7256, 100.5435, "ลุมพินี"),
    (13.7372, 100.5607, "สุขุมวิท MRT"),
    (13.7482, 100.5636, "เพชรบุรี"),
    (13.7578, 100.5652, "พระราม 9"),
    (13.7652, 100.5701, "ศูนย์วัฒนธรรม"),
    (13.7783, 100.5741, "ห้วยขวาง"),
    (13.7897, 100.5741, "สุทธิสาร"),
    (13.7977, 100.5743, "รัชดาภิเษก"),
    (13.8061, 100.5736, "ลาดพร้าว"),
    (13.8130, 100.5620, "พหลโยธิน"),
    (13.8022, 100.5537, "จตุจักร"),
    (13.8064, 100.5377, "บางซื่อ"),
    (13.8646, 100.4161, "ตลาดบางใหญ่"),
    # ARL
    (13.7539, 100.5401, "ราชปรารภ"),
    (13.7506, 100.5571, "มักกะสัน"),
    (13.7579, 100.5967, "รามคำแหง ARL"),
    (13.7383, 100.6357, "หัวหมาก"),
    (13.7263, 100.6636, "บ้านทับช้าง"),
    (13.7277, 100.7236, "ลาดกระบัง"),
]

# ---------------------------------------------------------------------------
# Known developer tiers (for scoring)
# ---------------------------------------------------------------------------

TIER1_DEVELOPERS = {
    "sansiri", "แสนสิริ",
    "ap", "เอพี", "ap (thailand)",
    "lpn", "แอลพีเอ็น", "lumpini", "ลุมพินี",
    "origin", "ออริจิ้น",
    "ananda", "อนันดา",
}

TIER2_DEVELOPERS = {
    "pruksa", "พฤกษา",
    "supalai", "ศุภาลัย",
    "major", "เมเจอร์",
    "noble", "โนเบิล",
    "sc asset", "เอสซี",
    "property perfect", "พร็อพเพอร์ตี้ เพอร์เฟค",
    "land and houses", "แลนด์ แอนด์ เฮ้าส์",
    "quality houses", "ควอลิตี้ เฮ้าส์",
    "grand unity", "แกรนด์ ยูนิตี้",
    "raimon land", "ไรมอน แลนด์",
    "singha estate", "สิงห์ เอสเตท",
    "siamese", "ไซมิส",
    "knightsbridge",
    "life", "ไลฟ์",
}

# ---------------------------------------------------------------------------
# Haversine distance (meters)
# ---------------------------------------------------------------------------


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6_371_000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------


@dataclass
class NpaCandidate:
    source: str
    source_id: str
    project_name: str
    province: str
    district: str
    subdistrict: str
    price_baht: float
    size_sqm: Optional[float]
    lat: Optional[float]
    lon: Optional[float]
    bedroom: Optional[int] = None
    bathroom: Optional[int] = None
    floor: Optional[str] = None
    address: Optional[str] = None
    building_age: Optional[int] = None  # KBank only
    # Enriched fields
    price_sqm: Optional[float] = None
    market_price_sqm: Optional[int] = None
    market_confidence: str = "none"
    market_year_built: Optional[int] = None
    market_total_units: Optional[int] = None
    market_developer: Optional[str] = None
    market_rent_median: Optional[int] = None
    market_units_for_sale: Optional[int] = None
    market_units_for_rent: Optional[int] = None
    market_project_name: Optional[str] = None
    # Proximity
    nearest_anchor_name: Optional[str] = None
    nearest_anchor_type: Optional[str] = None
    nearest_anchor_dist_m: Optional[float] = None
    nearest_anchor_enrollment: Optional[int] = None
    nearest_bts_name: Optional[str] = None
    nearest_bts_dist_m: Optional[float] = None
    # Supply pressure
    supply_pressure_pct: Optional[float] = None  # units_for_sale / total_units
    # Screening results
    bts_tier: str = ""
    real_discount_pct: Optional[float] = None
    gross_yield_pct: Optional[float] = None
    effective_yield_pct: Optional[float] = None
    score: float = 0.0
    verdict: str = ""
    reject_reasons: list = field(default_factory=list)
    pass_gates: bool = False


# ---------------------------------------------------------------------------
# Phase 1: Extract condos from all providers
# ---------------------------------------------------------------------------


def extract_all_condos(
    conn, provinces: list[str], max_price: Optional[float] = None
) -> list[NpaCandidate]:
    """Extract condo NPA properties from all providers via adapter bridge."""
    from adapter_bridge import extract_candidates, ALL_SOURCES

    v2_candidates = extract_candidates(
        provinces=provinces,
        max_price=max_price,
        property_types=["condo"],
        sources=ALL_SOURCES,
    )

    # Convert v2 NpaCandidate (Pydantic) to v1 NpaCandidate (dataclass)
    candidates = []
    for c in v2_candidates:
        candidates.append(NpaCandidate(
            source=c.source,
            source_id=c.source_id,
            project_name=c.project_name,
            province=c.province,
            district=c.district,
            subdistrict=c.subdistrict,
            price_baht=c.price_baht,
            size_sqm=c.size_sqm,
            lat=c.lat,
            lon=c.lon,
            bedroom=c.bedroom,
            bathroom=c.bathroom,
            floor=c.floor,
            building_age=c.building_age,
            price_sqm=c.price_sqm,
        ))
    return candidates


# ---------------------------------------------------------------------------
# Phase 2: Enrich with market data (DB-level fuzzy match)
# ---------------------------------------------------------------------------


def enrich_with_market_data(conn, candidates: list[NpaCandidate]) -> None:
    """Batch-match NPA project names to market sources using trigram similarity.

    Delegates to market_adapter.batch_match_market (via adapter_bridge) which
    manages its own DB connection. The conn parameter is retained for API
    compatibility but is no longer used for market queries.
    """
    from adapter_bridge import batch_match_market

    # Collect unique non-empty project names, preserving name→candidates mapping
    name_to_candidates: dict[str, list[NpaCandidate]] = {}
    for c in candidates:
        if c.project_name and len(c.project_name.strip()) >= 3:
            key = c.project_name.strip()
            name_to_candidates.setdefault(key, []).append(c)

    unique_names = list(name_to_candidates.keys())
    if not unique_names:
        return

    print(f"       Matching {len(unique_names)} unique project names...", flush=True)

    market_results = batch_match_market(unique_names)

    print(
        f"       Market matches: {sum(1 for m in market_results.values() if m.market_matches)} "
        f"of {len(unique_names)} names matched",
        flush=True,
    )

    # Distribute results to candidates
    for name, cands in name_to_candidates.items():
        match = market_results.get(name)
        if not match or not match.market_matches:
            continue

        # Pick best match (first in list — highest similarity)
        best = match.market_matches[0]

        market_price_sqm = int(match.median_price_sqm) if match.median_price_sqm else None
        if market_price_sqm is None and best.avg_price_sqm:
            market_price_sqm = int(best.avg_price_sqm)

        year_built: Optional[int] = None
        total_units: Optional[int] = None
        units_for_sale: Optional[int] = None
        units_for_rent: Optional[int] = None
        ref_lat: Optional[float] = None
        ref_lng: Optional[float] = None

        for mp in match.market_matches:
            if year_built is None and mp.completion_year:
                year_built = mp.completion_year
            if total_units is None and mp.units_total:
                total_units = mp.units_total
            if units_for_sale is None and mp.units_for_sale:
                units_for_sale = mp.units_for_sale
            if units_for_rent is None and mp.units_for_rent:
                units_for_rent = mp.units_for_rent
            if ref_lat is None and mp.lat and mp.lon:
                ref_lat, ref_lng = mp.lat, mp.lon

        project_name = best.project_name or None

        sources_found = len(match.market_matches)
        if sources_found >= 3:
            confidence = "high"
        elif sources_found >= 2:
            confidence = "medium"
        elif sources_found >= 1:
            confidence = "low"
        else:
            confidence = "none"

        for c in cands:
            # Geo-verify: skip if candidate GPS is >2km from market project GPS
            if market_price_sqm and c.lat and c.lon and ref_lat and ref_lng:
                dist = haversine_m(c.lat, c.lon, ref_lat, ref_lng)
                if dist > 2000:
                    continue

            c.market_price_sqm = market_price_sqm
            c.market_confidence = confidence
            if year_built:
                try:
                    c.market_year_built = int(year_built)
                except (ValueError, TypeError):
                    pass
            if total_units:
                try:
                    c.market_total_units = int(total_units)
                except (ValueError, TypeError):
                    pass
            c.market_developer = None
            c.market_rent_median = None
            c.market_units_for_sale = int(units_for_sale) if units_for_sale else None
            c.market_units_for_rent = int(units_for_rent) if units_for_rent else None
            c.market_project_name = project_name


# ---------------------------------------------------------------------------
# Phase 3: Compute proximity
# ---------------------------------------------------------------------------


def compute_proximity(candidates: list[NpaCandidate]) -> None:
    for c in candidates:
        if not c.lat or not c.lon:
            continue

        # Nearest education anchor
        best_dist = float("inf")
        for alat, alon, aname, atype, enroll in EDUCATION_ANCHORS:
            d = haversine_m(c.lat, c.lon, alat, alon)
            if d < best_dist:
                best_dist = d
                c.nearest_anchor_name = aname
                c.nearest_anchor_type = atype
                c.nearest_anchor_dist_m = d
                c.nearest_anchor_enrollment = enroll

        # Nearest BTS/MRT
        best_dist = float("inf")
        for slat, slon, sname in TRANSIT_STATIONS:
            d = haversine_m(c.lat, c.lon, slat, slon)
            if d < best_dist:
                best_dist = d
                c.nearest_bts_name = sname
                c.nearest_bts_dist_m = d


# ---------------------------------------------------------------------------
# Phase 4: Apply Gates
# ---------------------------------------------------------------------------


def apply_gates(candidates: list[NpaCandidate]) -> None:
    current_year = datetime.now().year

    for c in candidates:
        c.reject_reasons = []
        c.pass_gates = True

        # --- Compute discount & yield & supply pressure ---
        if c.price_sqm and c.market_price_sqm and c.market_price_sqm > 0:
            c.real_discount_pct = (
                (c.market_price_sqm - c.price_sqm) / c.market_price_sqm * 100
            )

        if c.market_rent_median and c.price_baht > 0:
            c.gross_yield_pct = c.market_rent_median * 12 / c.price_baht * 100

        # Supply pressure: % of total units listed for sale
        if c.market_units_for_sale and c.market_total_units and c.market_total_units > 0:
            c.supply_pressure_pct = c.market_units_for_sale / c.market_total_units * 100

        # --- BTS Tier ---
        if c.nearest_anchor_dist_m is not None and c.nearest_anchor_dist_m <= 800:
            if c.nearest_bts_dist_m is not None and c.nearest_bts_dist_m <= 800:
                c.bts_tier = "A"
            elif c.nearest_bts_dist_m is not None and c.nearest_bts_dist_m <= 1500:
                c.bts_tier = "B"
            else:
                c.bts_tier = "C"
        else:
            c.bts_tier = "C"

        # === GATE 1: Auto-Reject ===

        # Building age > 20 years
        year_built = c.market_year_built
        if c.building_age is not None:
            year_built = current_year - c.building_age
        if year_built and year_built < (current_year - 20):
            c.reject_reasons.append(f"building_age: built {year_built} ({current_year - year_built}yr)")
            c.pass_gates = False

        # NPA price >= market
        if c.real_discount_pct is not None and c.real_discount_pct <= 0:
            c.reject_reasons.append(f"npa_above_market: {c.real_discount_pct:.1f}%")
            c.pass_gates = False

        # Supply pressure > 25% = severe oversupply (auto-reject)
        if c.supply_pressure_pct is not None and c.supply_pressure_pct > 25:
            c.reject_reasons.append(
                f"oversupply: {c.supply_pressure_pct:.0f}% of units for sale"
            )
            c.pass_gates = False

        # Unit size filter (if known)
        if c.size_sqm is not None:
            if c.nearest_anchor_type == "university" and (c.size_sqm < 22 or c.size_sqm > 50):
                c.reject_reasons.append(f"wrong_size_university: {c.size_sqm}sqm")
                c.pass_gates = False
            elif c.nearest_anchor_type == "intl_school" and (c.size_sqm < 45 or c.size_sqm > 150):
                c.reject_reasons.append(f"wrong_size_intl: {c.size_sqm}sqm")
                c.pass_gates = False
            elif c.nearest_anchor_type == "thai_school" and (c.size_sqm < 30 or c.size_sqm > 100):
                c.reject_reasons.append(f"wrong_size_thai: {c.size_sqm}sqm")
                c.pass_gates = False

        # === GATE 2: Minimum Thresholds ===

        if c.pass_gates:
            # Discount threshold
            min_discount = {"A": 15, "B": 20, "C": 25}.get(c.bts_tier, 20)
            if c.real_discount_pct is None:
                c.reject_reasons.append("no_market_data")
                # Don't hard-reject — flag as unverified
            elif c.real_discount_pct < min_discount:
                c.reject_reasons.append(
                    f"discount_low: {c.real_discount_pct:.1f}% < {min_discount}%"
                )
                c.pass_gates = False

            # Yield threshold
            min_yield = {"A": 6.0, "B": 7.0, "C": 8.0}.get(c.bts_tier, 7.0)
            if c.gross_yield_pct is not None and c.gross_yield_pct < min_yield:
                c.reject_reasons.append(
                    f"yield_low: {c.gross_yield_pct:.1f}% < {min_yield}%"
                )
                c.pass_gates = False

            # Education anchor distance
            if c.nearest_anchor_dist_m is not None and c.nearest_anchor_dist_m > 800:
                c.reject_reasons.append(
                    f"anchor_far: {c.nearest_anchor_dist_m:.0f}m > 800m"
                )
                c.pass_gates = False

            # Liquidity
            total_listings = (c.market_units_for_sale or 0) + (c.market_units_for_rent or 0)
            if c.market_units_for_sale is not None and c.market_units_for_sale < 3:
                c.reject_reasons.append(
                    f"low_liquidity: {c.market_units_for_sale} listings"
                )
                # Soft reject for low liquidity
                if total_listings < 3:
                    c.pass_gates = False

        # === GATE 3: Summer vacancy (Tier C university) ===
        if c.bts_tier == "C" and c.nearest_anchor_type == "university":
            if c.gross_yield_pct is not None:
                c.effective_yield_pct = c.gross_yield_pct * 0.75
                if c.effective_yield_pct < 8.0:
                    c.reject_reasons.append(
                        f"summer_vacancy: effective {c.effective_yield_pct:.1f}% < 8%"
                    )
                    c.pass_gates = False
            else:
                c.effective_yield_pct = None
        else:
            c.effective_yield_pct = c.gross_yield_pct

        # === GATE 4: Score ===
        c.score = _compute_score(c, current_year)

        # === Verdict ===
        if not c.pass_gates:
            c.verdict = "AVOID"
        elif c.score >= 80 and (c.real_discount_pct or 0) >= 30 and (c.effective_yield_pct or 0) >= 7:
            c.verdict = "STRONG BUY"
        elif c.score >= 60 and (c.real_discount_pct or 0) >= min_discount:
            c.verdict = "BUY"
        elif c.score >= 40:
            c.verdict = "WATCH"
        else:
            c.verdict = "AVOID"


def _compute_score(c: NpaCandidate, current_year: int) -> float:
    # Discount score (25%)
    d = c.real_discount_pct or 0
    if d >= 35:
        discount_s = 100
    elif d >= 20:
        discount_s = 60
    elif d > 0:
        discount_s = 30
    else:
        discount_s = 0

    # Age score (15%)
    yb = c.market_year_built
    if c.building_age:
        yb = current_year - c.building_age
    if yb is None:
        age_s = 50  # unknown = neutral
    elif 2015 <= yb <= 2018:
        age_s = 100
    elif 2008 <= yb <= 2014:
        age_s = 70
    elif 2019 <= yb:
        age_s = 85
    elif 2006 <= yb <= 2007:
        age_s = 40
    else:
        age_s = 0

    # BTS score (15%)
    bd = c.nearest_bts_dist_m
    if bd is None:
        bts_s = 0
    elif bd < 400:
        bts_s = 100
    elif bd < 600:
        bts_s = 70
    elif bd < 800:
        bts_s = 50
    elif bd < 1500:
        bts_s = 30
    else:
        bts_s = 0

    # Anchor distance score (10%)
    ad = c.nearest_anchor_dist_m
    if ad is None:
        anchor_s = 0
    elif ad < 400:
        anchor_s = 100
    elif ad < 600:
        anchor_s = 70
    elif ad <= 800:
        anchor_s = 40
    else:
        anchor_s = 0

    # Yield score (10%)
    y = c.effective_yield_pct or c.gross_yield_pct or 0
    if y >= 9:
        yield_s = 100
    elif y >= 7:
        yield_s = 70
    elif y >= 6:
        yield_s = 40
    else:
        yield_s = 0

    # Developer score (10%)
    dev = (c.market_developer or "").lower().strip()
    if any(t in dev for t in TIER1_DEVELOPERS):
        dev_s = 100
    elif any(t in dev for t in TIER2_DEVELOPERS):
        dev_s = 60
    elif dev:
        dev_s = 30
    else:
        dev_s = 20  # unknown

    # Building size score (5%)
    units = c.market_total_units
    if units is None:
        bld_s = 40
    elif units >= 200:
        bld_s = 100
    elif units >= 50:
        bld_s = 60
    elif units >= 30:
        bld_s = 30
    else:
        bld_s = 10

    # Anchor type score (5%)
    atype = c.nearest_anchor_type
    if atype == "intl_school":
        atype_s = 100
    elif atype == "university" and (c.nearest_anchor_enrollment or 0) >= 25000:
        atype_s = 90
    elif atype == "thai_school":
        atype_s = 70
    elif atype == "university":
        atype_s = 60
    else:
        atype_s = 0

    # Supply pressure score (5%) — lower pressure = better
    # Measures % of total units listed for sale (oversupply signal)
    sp = c.supply_pressure_pct
    if sp is None:
        supply_s = 50  # unknown = neutral
    elif sp <= 5:
        supply_s = 100  # healthy — few units for sale
    elif sp <= 10:
        supply_s = 70  # moderate
    elif sp <= 15:
        supply_s = 40  # concerning
    elif sp <= 25:
        supply_s = 20  # high oversupply
    else:
        supply_s = 0  # severe — auto-rejected in Gate 1

    # Listing liquidity score (5%) — need minimum listings to confirm market exists
    ls = (c.market_units_for_sale or 0) + (c.market_units_for_rent or 0)
    if ls >= 30:
        list_s = 100
    elif ls >= 10:
        list_s = 70
    elif ls >= 3:
        list_s = 40
    else:
        list_s = 0

    return (
        discount_s * 0.20
        + age_s * 0.15
        + bts_s * 0.15
        + anchor_s * 0.10
        + yield_s * 0.10
        + dev_s * 0.10
        + bld_s * 0.05
        + atype_s * 0.05
        + supply_s * 0.05
        + list_s * 0.05
    )


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------


def format_report(candidates: list[NpaCandidate], top_n: int = 50) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    # Sort by score desc, then discount desc
    ranked = sorted(
        candidates,
        key=lambda c: (
            0 if c.verdict == "AVOID" else 1,
            c.score,
            c.real_discount_pct or 0,
        ),
        reverse=True,
    )

    # Stats
    total = len(candidates)
    by_verdict = {}
    for c in candidates:
        by_verdict[c.verdict] = by_verdict.get(c.verdict, 0) + 1
    by_source = {}
    for c in candidates:
        by_source[c.source] = by_source.get(c.source, 0) + 1
    has_market = sum(1 for c in candidates if c.market_price_sqm)

    lines = [
        f"# NPA Condo Screening Report — {now}",
        "",
        "## Summary",
        "",
        f"- **Total condos extracted:** {total}",
        f"- **Market data matched:** {has_market} ({has_market*100//max(total,1)}%)",
        f"- **Provinces:** {', '.join(TARGET_PROVINCES)}",
        "",
        "### By Provider",
        "| Provider | Count |",
        "|----------|-------|",
    ]
    for src in ["JAM", "SAM", "BAM", "KTB", "KBANK", "LED"]:
        lines.append(f"| {src} | {by_source.get(src, 0)} |")

    lines += [
        "",
        "### By Verdict",
        "| Verdict | Count |",
        "|---------|-------|",
    ]
    for v in ["STRONG BUY", "BUY", "WATCH", "AVOID"]:
        lines.append(f"| {v} | {by_verdict.get(v, 0)} |")

    # Top candidates
    top = [c for c in ranked if c.verdict != "AVOID"][:top_n]

    lines += [
        "",
        f"## Top {len(top)} Candidates",
        "",
        "| # | Verdict | Score | Source | Project | Province/District | Price (฿) | Size | ฿/sqm | Market ฿/sqm | Discount | Yield | BTS Tier | Nearest BTS | Anchor | Anchor Dist |",
        "|---|---------|-------|--------|---------|-------------------|-----------|------|-------|-------------|----------|-------|----------|-------------|--------|-------------|",
    ]

    for i, c in enumerate(top, 1):
        price_str = f"{c.price_baht:,.0f}"
        size_str = f"{c.size_sqm:.1f}" if c.size_sqm else "?"
        psqm_str = f"{c.price_sqm:,.0f}" if c.price_sqm else "?"
        mpsqm_str = f"{c.market_price_sqm:,}" if c.market_price_sqm else "?"
        disc_str = f"{c.real_discount_pct:.1f}%" if c.real_discount_pct is not None else "?"
        yield_str = f"{c.gross_yield_pct:.1f}%" if c.gross_yield_pct is not None else "?"
        bts_str = f"{c.nearest_bts_name} ({c.nearest_bts_dist_m:.0f}m)" if c.nearest_bts_name else "?"
        anchor_str = c.nearest_anchor_name or "?"
        anchor_d = f"{c.nearest_anchor_dist_m:.0f}m" if c.nearest_anchor_dist_m is not None else "?"
        loc = f"{c.province}/{c.district}"

        lines.append(
            f"| {i} | **{c.verdict}** | {c.score:.0f} | {c.source} | "
            f"{c.project_name or c.source_id} | {loc} | {price_str} | "
            f"{size_str} | {psqm_str} | {mpsqm_str} | {disc_str} | {yield_str} | "
            f"{c.bts_tier} | {bts_str} | {anchor_str} | {anchor_d} |"
        )

    # Detailed cards for top 20
    lines += ["", "## Detailed Analysis — Top 20", ""]
    for i, c in enumerate(top[:20], 1):
        lines += _format_card(i, c)

    return "\n".join(lines)


def _format_card(rank: int, c: NpaCandidate) -> list[str]:
    lines = [
        f"### #{rank} — {c.project_name or c.source_id} ({c.source} {c.source_id})",
        "",
        f"- **Verdict:** {c.verdict} (Score: {c.score:.0f}/100)",
        f"- **Price:** ฿{c.price_baht:,.0f}" + (f" ({c.size_sqm:.1f} sqm = ฿{c.price_sqm:,.0f}/sqm)" if c.price_sqm else ""),
        f"- **Market price:** ฿{c.market_price_sqm:,}/sqm ({c.market_confidence} confidence)" if c.market_price_sqm else "- **Market price:** no data",
        f"- **Real discount:** {c.real_discount_pct:.1f}%" if c.real_discount_pct is not None else "- **Real discount:** unverified",
        f"- **Gross yield:** {c.gross_yield_pct:.1f}%" if c.gross_yield_pct is not None else "- **Gross yield:** no rental data",
    ]
    if c.effective_yield_pct and c.effective_yield_pct != c.gross_yield_pct:
        lines.append(f"- **Effective yield (vacancy adj):** {c.effective_yield_pct:.1f}%")
    lines += [
        f"- **Location:** {c.province} > {c.district} > {c.subdistrict}",
        f"- **BTS Tier:** {c.bts_tier} — {c.nearest_bts_name} ({c.nearest_bts_dist_m:.0f}m)" if c.nearest_bts_name else f"- **BTS Tier:** {c.bts_tier}",
        f"- **Education anchor:** {c.nearest_anchor_name} ({c.nearest_anchor_type}, {c.nearest_anchor_dist_m:.0f}m)" if c.nearest_anchor_name else "- **Education anchor:** none within range",
    ]
    if c.market_year_built:
        age = datetime.now().year - c.market_year_built
        lines.append(f"- **Year built:** {c.market_year_built} ({age} years old)")
    elif c.building_age:
        lines.append(f"- **Building age:** {c.building_age} years")
    if c.market_developer:
        lines.append(f"- **Developer:** {c.market_developer}")
    if c.market_total_units:
        lines.append(f"- **Total units:** {c.market_total_units}")
    if c.market_units_for_sale is not None:
        supply_str = ""
        if c.supply_pressure_pct is not None:
            level = "LOW" if c.supply_pressure_pct <= 5 else "MODERATE" if c.supply_pressure_pct <= 10 else "HIGH" if c.supply_pressure_pct <= 15 else "SEVERE"
            supply_str = f" | **Supply pressure: {c.supply_pressure_pct:.0f}% ({level})**"
        lines.append(f"- **Active listings:** {c.market_units_for_sale} sale, {c.market_units_for_rent or 0} rent{supply_str}")
    if c.market_rent_median:
        lines.append(f"- **Rent median:** ฿{c.market_rent_median:,}/mo")
    if c.reject_reasons:
        lines.append(f"- **Flags:** {', '.join(c.reject_reasons)}")
    lines.append("")
    return lines


def export_json(candidates: list[NpaCandidate], path: str) -> None:
    ranked = sorted(
        candidates,
        key=lambda c: (
            0 if c.verdict == "AVOID" else 1,
            c.score,
            c.real_discount_pct or 0,
        ),
        reverse=True,
    )
    data = []
    for c in ranked:
        if c.verdict == "AVOID":
            continue
        data.append({
            "source": c.source,
            "source_id": c.source_id,
            "project_name": c.project_name,
            "province": c.province,
            "district": c.district,
            "price_baht": c.price_baht,
            "size_sqm": c.size_sqm,
            "price_sqm": c.price_sqm,
            "market_price_sqm": c.market_price_sqm,
            "market_confidence": c.market_confidence,
            "real_discount_pct": round(c.real_discount_pct, 1) if c.real_discount_pct else None,
            "gross_yield_pct": round(c.gross_yield_pct, 1) if c.gross_yield_pct else None,
            "effective_yield_pct": round(c.effective_yield_pct, 1) if c.effective_yield_pct else None,
            "bts_tier": c.bts_tier,
            "nearest_bts": c.nearest_bts_name,
            "nearest_bts_m": round(c.nearest_bts_dist_m) if c.nearest_bts_dist_m else None,
            "nearest_anchor": c.nearest_anchor_name,
            "nearest_anchor_type": c.nearest_anchor_type,
            "nearest_anchor_m": round(c.nearest_anchor_dist_m) if c.nearest_anchor_dist_m else None,
            "year_built": c.market_year_built,
            "developer": c.market_developer,
            "total_units": c.market_total_units,
            "units_for_sale": c.market_units_for_sale,
            "supply_pressure_pct": round(c.supply_pressure_pct, 1) if c.supply_pressure_pct else None,
            "score": round(c.score, 1),
            "verdict": c.verdict,
            "flags": c.reject_reasons,
            "lat": c.lat,
            "lon": c.lon,
        })
    with open(path, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    import argparse

    parser = argparse.ArgumentParser(description="NPA Condo Screener")
    parser.add_argument("--province", help="Single province filter")
    parser.add_argument("--max-price", type=float, help="Max price in baht")
    parser.add_argument("--top", type=int, default=50, help="Top N results")
    parser.add_argument("--json", action="store_true", help="Also export JSON")
    args = parser.parse_args()

    provinces = [args.province] if args.province else TARGET_PROVINCES

    print(f"[1/4] Extracting condos from 6 providers in {', '.join(provinces)}...")
    conn = psycopg2.connect(DB_URL)

    candidates = extract_all_condos(conn, provinces, args.max_price)
    print(f"       → {len(candidates)} condos found")

    print(f"[2/4] Enriching with market data (Hipflat/PropertyHub/ZMyHome)...")
    enrich_with_market_data(conn, candidates)
    matched = sum(1 for c in candidates if c.market_price_sqm)
    print(f"       → {matched} matched to market sources")

    print(f"[3/4] Computing proximity to education anchors + BTS/MRT...")
    compute_proximity(candidates)
    near_anchor = sum(1 for c in candidates if c.nearest_anchor_dist_m and c.nearest_anchor_dist_m <= 800)
    print(f"       → {near_anchor} within 800m of education anchor")

    print(f"[4/4] Applying screening gates...")
    apply_gates(candidates)
    passing = sum(1 for c in candidates if c.pass_gates)
    print(f"       → {passing} pass all gates")

    # Verdict breakdown
    verdicts = {}
    for c in candidates:
        verdicts[c.verdict] = verdicts.get(c.verdict, 0) + 1
    for v in ["STRONG BUY", "BUY", "WATCH", "AVOID"]:
        print(f"       {v}: {verdicts.get(v, 0)}")

    # Output
    output_dir = Path(__file__).parent.parent.parent.parent / "output"
    date_str = datetime.now().strftime("%Y-%m-%d")

    report = format_report(candidates, args.top)
    report_path = output_dir / f"npa-screening-{date_str}.md"
    report_path.write_text(report)
    print(f"\n✓ Report: {report_path}")

    if args.json:
        json_path = output_dir / f"npa-screening-{date_str}.json"
        export_json(candidates, str(json_path))
        print(f"✓ JSON:   {json_path}")

    conn.close()


if __name__ == "__main__":
    main()

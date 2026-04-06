"""
Main CLI entry point for Multi-Strategy NPA Screener v2.

Orchestrates the full pipeline:
  1. Parse args → build InvestorProfile
  2. Extract NPA properties from all providers
  3. Enrich with market data (trigram project matching)
  4. Compute proximity (education anchors, BTS/MRT)
  5. Route and score each candidate
  6. Apply financial overlay
  7. Write report + optional JSON

Usage:
    python screener_v2.py --help
    python screener_v2.py --purchase-mode mortgage --ltv 0.7 --top 100 --json
"""

import argparse
import math
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import psycopg2
import psycopg2.extras

from constants import MORTGAGE_RATE_FIXED
from extract_v2 import extract_all_properties
from financial_overlay import compute_financial_overlay
from models_v2 import InvestorProfile, NpaCandidate, PropertyResult
from report_v2 import export_json_v2, format_report_v2
from strategy_router import route_and_score

DB_URL = "postgresql://arsapolm@localhost:5432/npa_kb"

DEFAULT_PROVINCES = [
    "กรุงเทพมหานคร",
    "ปทุมธานี",
    "สมุทรปราการ",
    "นนทบุรี",
]

# ---------------------------------------------------------------------------
# Education anchors and transit stations (copied from screener.py)
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
# Haversine distance (meters)
# ---------------------------------------------------------------------------


def _haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6_371_000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


# ---------------------------------------------------------------------------
# Market data enrichment (v2 — returns enriched NpaCandidate list)
# ---------------------------------------------------------------------------


def _enrich_candidates(conn, candidates: list[NpaCandidate]) -> list[NpaCandidate]:
    """
    Batch-match NPA project names to market sources using trigram similarity.
    Returns a new list of NpaCandidate with market_* fields populated.
    Since NpaCandidate is frozen Pydantic, we collect enrichment dicts and
    rebuild candidates via model_copy(update=...).
    """
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    try:
        cur.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
        conn.commit()
    except Exception:
        conn.rollback()

    # Group by project name
    name_to_indices: dict[str, list[int]] = {}
    for i, c in enumerate(candidates):
        key = (c.project_name or "").strip()
        if len(key) >= 3:
            name_to_indices.setdefault(key, []).append(i)

    unique_names = list(name_to_indices.keys())
    if not unique_names:
        cur.close()
        return list(candidates)

    print(f"   Matching {len(unique_names)} unique project names against market sources...", flush=True)

    # Temp table for batch trigram matching
    cur.execute("DROP TABLE IF EXISTS _npa_names_v2")
    cur.execute("CREATE TEMP TABLE _npa_names_v2 (name text)")
    cur.execute("CREATE INDEX ON _npa_names_v2 USING gin (name gin_trgm_ops)")
    psycopg2.extras.execute_values(
        cur, "INSERT INTO _npa_names_v2 (name) VALUES %s",
        [(n,) for n in unique_names],
    )

    # Hipflat batch match
    hipflat_matches: dict[str, dict] = {}
    cur.execute("""
        SELECT DISTINCT ON (nn.name)
               nn.name as npa_name,
               h.name_th, h.name_en, h.avg_sale_sqm, h.avg_sold_sqm,
               h.rent_price_min, h.rent_price_max,
               h.year_completed, h.total_units,
               h.units_for_sale, h.units_for_rent,
               h.lat, h.lng,
               GREATEST(
                   similarity(COALESCE(h.name_th, ''), nn.name),
                   similarity(COALESCE(h.name_en, ''), nn.name)
               ) as sim
        FROM _npa_names_v2 nn
        CROSS JOIN LATERAL (
            SELECT *
            FROM hipflat_projects hp
            WHERE hp.name_th % nn.name OR hp.name_en % nn.name
            ORDER BY GREATEST(
                similarity(COALESCE(hp.name_th, ''), nn.name),
                similarity(COALESCE(hp.name_en, ''), nn.name)
            ) DESC
            LIMIT 1
        ) h
        ORDER BY nn.name, sim DESC
    """)
    for row in cur.fetchall():
        hipflat_matches[row["npa_name"]] = dict(row)
    print(f"   Hipflat: {len(hipflat_matches)} matches", flush=True)

    # PropertyHub batch match
    ph_matches: dict[str, dict] = {}
    cur.execute("""
        SELECT DISTINCT ON (nn.name)
               nn.name as npa_name,
               p.id as ph_id, p.name as ph_name, p.name_en,
               p.completed_year, p.total_units, p.developer,
               p.lat, p.lng,
               p.listing_count_sale, p.listing_count_rent,
               GREATEST(
                   similarity(COALESCE(p.name, ''), nn.name),
                   similarity(COALESCE(p.name_en, ''), nn.name)
               ) as sim
        FROM _npa_names_v2 nn
        CROSS JOIN LATERAL (
            SELECT *
            FROM propertyhub_projects pp
            WHERE pp.name % nn.name OR pp.name_en % nn.name
            ORDER BY GREATEST(
                similarity(COALESCE(pp.name, ''), nn.name),
                similarity(COALESCE(pp.name_en, ''), nn.name)
            ) DESC
            LIMIT 1
        ) p
        ORDER BY nn.name, sim DESC
    """)
    for row in cur.fetchall():
        ph_matches[row["npa_name"]] = dict(row)
    print(f"   PropertyHub: {len(ph_matches)} matches", flush=True)

    # PropertyHub listing medians
    ph_prices: dict[str, dict] = {}
    if ph_matches:
        ph_ids = list(set(r["ph_id"] for r in ph_matches.values() if r.get("ph_id")))
        if ph_ids:
            cur.execute("""
                SELECT project_id,
                       percentile_cont(0.5) WITHIN GROUP (ORDER BY price_per_sqm)
                           FILTER (WHERE price_per_sqm > 0) as med_sqm,
                       percentile_cont(0.5) WITHIN GROUP (ORDER BY rent_monthly)
                           FILTER (WHERE rent_monthly > 0) as med_rent
                FROM propertyhub_listings
                WHERE project_id = ANY(%s)
                GROUP BY project_id
            """, [ph_ids])
            for row in cur.fetchall():
                ph_prices[row["project_id"]] = dict(row)

    # ZMyHome batch match
    zm_matches: dict[str, dict] = {}
    cur.execute("""
        SELECT DISTINCT ON (nn.name)
               nn.name as npa_name,
               z.id as zm_id, z.name as zm_name,
               z.year_built, z.total_units, z.developer,
               z.lat, z.lng,
               similarity(COALESCE(z.name, ''), nn.name) as sim
        FROM _npa_names_v2 nn
        CROSS JOIN LATERAL (
            SELECT *
            FROM zmyhome_projects zp
            WHERE zp.name % nn.name
            ORDER BY similarity(COALESCE(zp.name, ''), nn.name) DESC
            LIMIT 1
        ) z
        ORDER BY nn.name, sim DESC
    """)
    for row in cur.fetchall():
        zm_matches[row["npa_name"]] = dict(row)
    print(f"   ZMyHome: {len(zm_matches)} matches", flush=True)

    cur.execute("DROP TABLE IF EXISTS _npa_names_v2")
    conn.commit()
    cur.close()

    # Build enrichment map: index → update dict
    enrichment: dict[int, dict] = {}

    for name, indices in name_to_indices.items():
        h = hipflat_matches.get(name)
        p = ph_matches.get(name)
        z = zm_matches.get(name)

        market_price_sqm: Optional[int] = None
        year_built: Optional[int] = None
        total_units: Optional[int] = None
        developer: Optional[str] = None
        rent_median: Optional[int] = None
        units_for_sale: Optional[int] = None
        units_for_rent: Optional[int] = None
        project_name: Optional[str] = None
        sources_found = 0
        ref_lat: Optional[float] = None
        ref_lng: Optional[float] = None

        if h:
            hprice = h.get("avg_sale_sqm") or h.get("avg_sold_sqm")
            if hprice:
                market_price_sqm = int(hprice)
                sources_found += 1
            year_built = h.get("year_completed")
            total_units = h.get("total_units")
            units_for_sale = h.get("units_for_sale")
            units_for_rent = h.get("units_for_rent")
            project_name = h.get("name_th") or h.get("name_en")
            if h.get("rent_price_min") and h.get("rent_price_max"):
                rent_median = (int(h["rent_price_min"]) + int(h["rent_price_max"])) // 2
            elif h.get("rent_price_min"):
                rent_median = int(h["rent_price_min"])
            if h.get("lat") and h.get("lng"):
                ref_lat, ref_lng = float(h["lat"]), float(h["lng"])

        if p:
            ph_price_data = ph_prices.get(p.get("ph_id"), {})
            if not market_price_sqm and ph_price_data.get("med_sqm"):
                market_price_sqm = int(ph_price_data["med_sqm"])
                sources_found += 1
            elif ph_price_data.get("med_sqm"):
                sources_found += 1
            if not year_built and p.get("completed_year"):
                year_built = p["completed_year"]
            if not total_units and p.get("total_units"):
                total_units = p["total_units"]
            if not developer and p.get("developer"):
                developer = p["developer"]
            if not rent_median and ph_price_data.get("med_rent"):
                rent_median = int(ph_price_data["med_rent"])
            if not units_for_sale and p.get("listing_count_sale"):
                units_for_sale = p["listing_count_sale"]
            if not units_for_rent and p.get("listing_count_rent"):
                units_for_rent = p["listing_count_rent"]
            if not project_name:
                project_name = p.get("ph_name") or p.get("name_en")
            if not ref_lat and p.get("lat") and p.get("lng"):
                ref_lat, ref_lng = float(p["lat"]), float(p["lng"])

        if z:
            sources_found += 1
            if not year_built and z.get("year_built"):
                year_built = z["year_built"]
            if not total_units and z.get("total_units"):
                total_units = z["total_units"]
            if not developer and z.get("developer"):
                developer = z["developer"]

        confidence = (
            "high" if sources_found >= 3
            else "medium" if sources_found >= 2
            else "low" if sources_found >= 1
            else "none"
        )

        for idx in indices:
            c = candidates[idx]
            # Geo-verify: skip if candidate has coords and ref is > 2km away
            if market_price_sqm and c.lat and c.lon and ref_lat and ref_lng:
                dist = _haversine_m(c.lat, c.lon, ref_lat, ref_lng)
                if dist > 2000:
                    continue

            update: dict = {"market_confidence": confidence}
            if market_price_sqm is not None:
                update["market_price_sqm"] = market_price_sqm
            if year_built is not None:
                try:
                    update["market_year_built"] = int(year_built)
                except (ValueError, TypeError):
                    pass
            if total_units is not None:
                try:
                    update["market_total_units"] = int(total_units)
                except (ValueError, TypeError):
                    pass
            if developer is not None:
                update["market_developer"] = developer
            if rent_median is not None:
                update["market_rent_median"] = rent_median
            if units_for_sale is not None:
                update["market_units_for_sale"] = int(units_for_sale)
            if units_for_rent is not None:
                update["market_units_for_rent"] = int(units_for_rent)
            if project_name is not None:
                update["market_project_name"] = project_name
            enrichment[idx] = update

    # Rebuild enriched candidates (immutable model_copy)
    result: list[NpaCandidate] = []
    for i, c in enumerate(candidates):
        upd = enrichment.get(i)
        if upd:
            # Compute derived fields
            price_sqm = c.price_sqm
            real_discount_pct = c.real_discount_pct
            supply_pressure_pct = c.supply_pressure_pct

            mkt_sqm = upd.get("market_price_sqm", c.market_price_sqm)
            if price_sqm and mkt_sqm and mkt_sqm > 0:
                real_discount_pct = (mkt_sqm - price_sqm) / mkt_sqm * 100

            mkt_units_sale = upd.get("market_units_for_sale", c.market_units_for_sale)
            mkt_units_total = upd.get("market_total_units", c.market_total_units)
            if mkt_units_sale and mkt_units_total and mkt_units_total > 0:
                supply_pressure_pct = mkt_units_sale / mkt_units_total * 100

            upd["real_discount_pct"] = real_discount_pct
            upd["supply_pressure_pct"] = supply_pressure_pct

            result.append(c.model_copy(update=upd))
        else:
            result.append(c)

    return result


# ---------------------------------------------------------------------------
# Proximity computation (v2 — returns enriched NpaCandidate list)
# ---------------------------------------------------------------------------


def _compute_proximity(candidates: list[NpaCandidate]) -> list[NpaCandidate]:
    """
    Compute nearest education anchor and BTS/MRT for each candidate.
    Returns a new list with proximity and bts_tier fields set.
    """
    result: list[NpaCandidate] = []
    for c in candidates:
        if not c.lat or not c.lon:
            result.append(c)
            continue

        # Nearest education anchor
        best_anchor_dist = float("inf")
        anchor_name: Optional[str] = None
        anchor_type: Optional[str] = None
        anchor_enrollment: Optional[int] = None
        for alat, alon, aname, atype, enroll in EDUCATION_ANCHORS:
            d = _haversine_m(c.lat, c.lon, alat, alon)
            if d < best_anchor_dist:
                best_anchor_dist = d
                anchor_name = aname
                anchor_type = atype
                anchor_enrollment = enroll

        # Nearest BTS/MRT
        best_bts_dist = float("inf")
        bts_name: Optional[str] = None
        for slat, slon, sname in TRANSIT_STATIONS:
            d = _haversine_m(c.lat, c.lon, slat, slon)
            if d < best_bts_dist:
                best_bts_dist = d
                bts_name = sname

        # BTS tier
        bts_tier = "C"
        if best_anchor_dist <= 800:
            if best_bts_dist <= 800:
                bts_tier = "A"
            elif best_bts_dist <= 1500:
                bts_tier = "B"

        update: dict = {
            "nearest_anchor_name": anchor_name,
            "nearest_anchor_type": anchor_type,
            "nearest_anchor_dist_m": best_anchor_dist if best_anchor_dist < float("inf") else None,
            "nearest_anchor_enrollment": anchor_enrollment,
            "nearest_bts_name": bts_name,
            "nearest_bts_dist_m": best_bts_dist if best_bts_dist < float("inf") else None,
            "bts_tier": bts_tier,
        }
        result.append(c.model_copy(update=update))

    return result


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="NPA Screener v2 — Multi-Strategy Investment Screening"
    )
    parser.add_argument(
        "--purchase-mode",
        choices=["cash", "mortgage"],
        default="cash",
        help="Financing mode (default: cash)",
    )
    parser.add_argument(
        "--ltv",
        type=float,
        default=0.0,
        metavar="0.0-1.0",
        help="Loan-to-value ratio (default: 0.0 for cash)",
    )
    parser.add_argument(
        "--hold-years",
        type=int,
        default=5,
        metavar="1-10",
        help="Hold horizon in years (default: 5)",
    )
    parser.add_argument(
        "--entity",
        choices=["personal", "company"],
        default="personal",
        help="Investor entity type (default: personal)",
    )
    parser.add_argument(
        "--tabien-baan",
        action="store_true",
        help="Flag: registered tabien baan (SBT exemption on sale within 5 years)",
    )
    parser.add_argument(
        "--reno-budget",
        type=float,
        default=0.0,
        metavar="0.0-0.20",
        help="Renovation budget as %% of purchase price (default: 0.0)",
    )
    parser.add_argument(
        "--strategies",
        default="all",
        help='Comma-separated strategies or "all" (default: all). '
             "Options: rent, flip, land_bank, hospitality",
    )
    parser.add_argument(
        "--risk",
        choices=["conservative", "moderate", "aggressive"],
        default="moderate",
        help="Risk tolerance (default: moderate)",
    )
    parser.add_argument(
        "--province",
        default=None,
        help="Single province filter (default: BKK metro 4 provinces)",
    )
    parser.add_argument(
        "--max-price",
        type=float,
        default=None,
        metavar="BAHT",
        help="Maximum price in baht (optional)",
    )
    parser.add_argument(
        "--property-types",
        default=None,
        help="Comma-separated property types: condo,house,townhouse,land,house_and_land,commercial",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=50,
        help="Top N results in report (default: 50)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="export_json",
        help="Also export results to JSON",
    )
    return parser.parse_args()


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------


def main() -> None:
    args = _parse_args()

    # --- Build InvestorProfile ---
    strategies_list = (
        ["all"]
        if args.strategies.strip().lower() == "all"
        else [s.strip().lower() for s in args.strategies.split(",")]
    )

    profile = InvestorProfile(
        purchase_mode=args.purchase_mode,
        ltv_pct=args.ltv,
        mortgage_rate=MORTGAGE_RATE_FIXED,
        hold_horizon_years=args.hold_years,
        entity_type=args.entity,
        tabien_baan=args.tabien_baan,
        renovation_budget_pct=args.reno_budget,
        strategies=strategies_list,
        risk_tolerance=args.risk,
    )

    provinces = [args.province] if args.province else list(DEFAULT_PROVINCES)
    property_types = (
        [pt.strip() for pt in args.property_types.split(",")]
        if args.property_types
        else None
    )

    print("=== NPA Screener v2 ===", flush=True)
    print(f"Provinces: {provinces}", flush=True)
    print(f"Profile: {profile.purchase_mode.upper()} | hold={profile.hold_horizon_years}yr | "
          f"entity={profile.entity_type} | strategies={','.join(profile.strategies)} | "
          f"risk={profile.risk_tolerance}", flush=True)
    if args.max_price:
        print(f"Max price: {args.max_price:,.0f} THB", flush=True)
    if property_types:
        print(f"Property types: {property_types}", flush=True)
    print("", flush=True)

    # --- Connect to DB ---
    print("Connecting to database...", flush=True)
    conn = psycopg2.connect(DB_URL)

    # --- Step 1: Extract ---
    print("Step 1/5 — Extracting NPA properties...", flush=True)
    candidates = extract_all_properties(
        conn,
        provinces=provinces,
        max_price=args.max_price,
        property_types=property_types,
    )
    print(f"   Extracted {len(candidates)} candidates", flush=True)

    if not candidates:
        print("No candidates found. Exiting.", flush=True)
        conn.close()
        sys.exit(0)

    # --- Step 2: Enrich with market data ---
    print("Step 2/5 — Enriching with market data...", flush=True)
    candidates = _enrich_candidates(conn, candidates)
    enriched_count = sum(1 for c in candidates if c.market_price_sqm is not None)
    print(f"   Enriched {enriched_count}/{len(candidates)} candidates", flush=True)

    # --- Step 3: Proximity ---
    print("Step 3/5 — Computing proximity (anchors + BTS/MRT)...", flush=True)
    candidates = _compute_proximity(candidates)
    with_coords = sum(1 for c in candidates if c.lat and c.lon)
    print(f"   Proximity computed for {with_coords} candidates (coords available)", flush=True)

    # --- Step 4: Route and score ---
    print("Step 4/5 — Routing and scoring strategies...", flush=True)
    results: list[PropertyResult] = []
    for c in candidates:
        result = route_and_score(c, profile)
        results.append(result)

    buys = sum(1 for r in results if r.best_strategy and r.best_score >= 55)
    print(f"   {len(results)} scored | {buys} with score >= 55", flush=True)

    # --- Step 5: Financial overlay ---
    print("Step 5/5 — Applying financial overlay...", flush=True)
    final_results: list[PropertyResult] = []
    for r in results:
        if r.prefilter.pass_all:
            financial = compute_financial_overlay(r, profile)
            final_results.append(r.model_copy(update={"financial": financial}))
        else:
            final_results.append(r)

    with_financial = sum(1 for r in final_results if r.financial is not None)
    print(f"   Financial overlay applied to {with_financial} candidates", flush=True)

    conn.close()

    # --- Report ---
    print("", flush=True)
    print("Writing report...", flush=True)
    date_str = datetime.now().strftime("%Y-%m-%d")
    output_dir = Path(__file__).resolve().parents[3] / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    report_path = output_dir / f"npa-screening-v2-{date_str}.md"
    report_text = format_report_v2(final_results, profile, top_n=args.top)
    report_path.write_text(report_text, encoding="utf-8")
    print(f"Report written: {report_path}", flush=True)

    if args.export_json:
        json_path = output_dir / f"npa-screening-v2-{date_str}.json"
        export_json_v2(final_results, str(json_path))
        print(f"JSON exported: {json_path}", flush=True)

    # --- Summary stats ---
    print("", flush=True)
    print("=== Summary ===", flush=True)
    print(f"Total screened:      {len(final_results)}", flush=True)
    prefilter_pass = sum(1 for r in final_results if r.prefilter.pass_all)
    print(f"Pre-filter passed:   {prefilter_pass}", flush=True)
    strong_buys = sum(
        1 for r in final_results
        if r.best_strategy and r.strategy_scores.get(r.best_strategy) is not None
        and r.strategy_scores[r.best_strategy].verdict == "STRONG_BUY"
    )
    buys_count = sum(
        1 for r in final_results
        if r.best_strategy and r.strategy_scores.get(r.best_strategy) is not None
        and r.strategy_scores[r.best_strategy].verdict == "BUY"
    )
    dual = sum(1 for r in final_results if r.is_dual_strategy)
    print(f"STRONG_BUY:          {strong_buys}", flush=True)
    print(f"BUY:                 {buys_count}", flush=True)
    print(f"Dual-strategy:       {dual}", flush=True)


if __name__ == "__main__":
    main()

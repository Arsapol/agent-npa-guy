#!/usr/bin/env python3
"""
NPA Property Alert System
Scans LED + SAM databases for properties matching user criteria.
Can detect newly added properties or find deals matching specific filters.

Usage:
  python alert.py new [--hours 24]              # New properties in last N hours
  python alert.py deals [--max-price 5000000]    # Best deals across both sources
  python alert.py bts [--meters 500]             # Properties near BTS/MRT
  python alert.py upcoming [--days 14]           # Upcoming auctions
  python alert.py report                         # Full daily report
"""

import argparse
import json
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

import psycopg2

# Add parent skills to path for location-intel
SKILLS_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(SKILLS_DIR / "location-intel" / "scripts"))

DB_URL = os.environ.get("NPA_DB_URL", "postgresql://arsapolm@localhost:5432/npa_kb")

# ─── BTS/MRT Station coordinates (subset of Bangkok) ───
# Full data is in location-intel skill; we include top stations here for speed
TRANSIT_STATIONS = [
    ("BTS สยาม", 13.7463, 100.5344),
    ("BTS อโศก", 13.7362, 100.5672),
    ("BTS พร้อมพงษ์", 13.7226, 100.5835),
    ("BTS ทองหล่อ", 13.7172, 100.5961),
    ("BTS เอกมัย", 13.7118, 100.6039),
    ("BTS พระโขนง", 13.7047, 100.6157),
    ("BTS อ่อนนุช", 13.6977, 100.6342),
    ("BTS บางนา", 13.6822, 100.6536),
    ("BTS แบริ่ง", 13.6715, 100.6637),
    ("BTS สมุทรปราการ", 13.6603, 100.6761),
    ("BTS ชิดลม", 13.7482, 100.5281),
    ("BTS สนามเป้า", 13.7563, 100.5301),
    ("BTS อนุสาวรีย์ชัย", 13.7643, 100.5373),
    ("BTS พญาไท", 13.7649, 100.5407),
    ("BTS ราชเทวี", 13.7591, 100.5448),
    ("BTS นานา", 13.7299, 100.5757),
    ("BTS วิภาวดีรังสิต", 13.7788, 100.5368),
    ("BTS หมอชิต", 13.7835, 100.5424),
    ("BTS สะพานควาย", 13.7931, 100.5450),
    ("BTS มหาดไทย", 13.8010, 100.5473),
    ("BTS สายหยุด", 13.8145, 100.5574),
    ("MRT พระราม 9", 13.7542, 100.5690),
    ("MRT ศูนย์วัฒนธรรม", 13.7602, 100.5657),
    ("MRT ห้วยขวาง", 13.7571, 100.5742),
    ("MRT สุทธิสาร", 13.7641, 100.5719),
    ("MRT ลาดพร้าว", 13.7767, 100.5682),
    ("MRT พหลโยธิน", 13.7870, 100.5640),
    ("MRT สวนจตุจักร", 13.7971, 100.5610),
    ("MRT กำแพงเพชร", 13.8068, 100.5565),
    ("MRT บางซื่อ", 13.8062, 100.5393),
    ("MRT เพชรบุรี", 13.7469, 100.5731),
    ("MRT สุขุมวิท", 13.7363, 100.5674),
    ("MRT สีลม", 13.7285, 100.5345),
    ("MRT สามย่าน", 13.7301, 100.5254),
    ("MRT ลุมพินี", 13.7331, 100.5411),
    ("MRT ดินแดง", 13.7574, 100.5572),
    ("BTS กรุงธนบุรี", 13.7182, 100.5018),
    ("BTS วงแหวน", 13.7099, 100.4918),
    ("BTS ตลาดพลู", 13.7048, 100.4888),
    ("BTS วัดพระแก้ว", 13.6987, 100.4839),
    ("BRT ราชเทวี", 13.7591, 100.5448),
    ("BTS บางหว้า", 13.6949, 100.4759),
    ("BTS เพชรเกล้า", 13.6926, 100.4643),
    ("BTS สำโรง", 13.6451, 100.6906),
]


def haversine_meters(lat1, lon1, lat2, lon2):
    """Calculate distance between two GPS points in meters."""
    from math import radians, cos, sin, asin, sqrt
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    return 6371000 * 2 * asin(sqrt(a))


def nearest_station(lat, lng, max_meters=None):
    """Find nearest BTS/MRT station. Returns (name, distance_m) or None."""
    best = None
    for name, slat, slng in TRANSIT_STATIONS:
        d = haversine_meters(lat, lng, slat, slng)
        if max_meters and d > max_meters:
            continue
        if best is None or d < best[1]:
            best = (name, d)
    return best


def get_conn():
    return psycopg2.connect(DB_URL)


def fmt_price(satang_or_baht, is_satang=True):
    """Format price nicely."""
    if satang_or_baht is None:
        return "N/A"
    val = satang_or_baht / 100.0 if is_satang else float(satang_or_baht)
    if val >= 1_000_000:
        return f"฿{val/1_000_000:.2f}M"
    return f"฿{val:,.0f}"


def fmt_baht(val):
    """Format baht value."""
    if val is None:
        return "N/A"
    val = float(val)
    if val >= 1_000_000:
        return f"฿{val/1_000_000:.2f}M"
    return f"฿{val:,.0f}"


# ─── ALERT: New Properties ───

def alert_new_properties(hours=24, source="all"):
    """Find properties added in the last N hours across ALL providers."""
    conn = get_conn()
    cur = conn.cursor()
    since = datetime.now() - timedelta(hours=hours)
    results = []

    # LED new properties
    if source in ("all", "led"):
        cur.execute("""
            SELECT p.asset_id, p.property_type, p.ampur, p.province,
                   p.primary_price_satang, p.appraisal_price_satang,
                   p.sale_status, p.next_auction_date, p.address,
                   p.size_rai, p.size_ngan, p.size_wa, p.created_at
            FROM properties p
            WHERE p.created_at >= %s
              AND p.primary_price_satang IS NOT NULL
            ORDER BY p.created_at DESC
            LIMIT 100
        """, (since,))
        for row in cur.fetchall():
            price = row[4]
            appraisal = row[5]
            discount = None
            if price and appraisal and appraisal > 0:
                discount = round((1 - price / appraisal) * 100, 1)
            results.append({
                "source": "LED",
                "asset_id": row[0],
                "type": row[1],
                "district": row[2],
                "province": row[3],
                "price": fmt_price(price),
                "price_raw": price,
                "appraisal": fmt_price(appraisal),
                "discount_pct": discount,
                "status": row[6],
                "auction_date": str(row[7]) if row[7] else None,
                "address": row[8],
                "size": f"{row[9] or 0}R {row[10] or 0}N {row[11] or 0}W",
                "created_at": str(row[12]),
            })

    # SAM new properties
    if source in ("all", "sam"):
        cur.execute("""
            SELECT code, type_name, district, province,
                   price_baht, size_sqm, status, lat, lng,
                   first_seen_at, address_full
            FROM sam_properties
            WHERE first_seen_at >= %s
              AND price_baht IS NOT NULL
            ORDER BY first_seen_at DESC
            LIMIT 100
        """, (since,))
        for row in cur.fetchall():
            station_info = None
            if row[7] and row[8]:
                ns = nearest_station(float(row[7]), float(row[8]))
                if ns:
                    station_info = f"{ns[0]} ({ns[1]:.0f}m)"
            results.append({
                "source": "SAM",
                "code": row[0],
                "type": row[1],
                "district": row[2],
                "province": row[3],
                "price": fmt_baht(row[4]),
                "price_raw": int(row[4]) if row[4] else None,
                "size_sqm": row[5],
                "status": row[6],
                "station": station_info,
                "first_seen": str(row[9]),
                "address": row[10],
            })

    # BAM new properties
    if source in ("all", "bam"):
        cur.execute("""
            SELECT asset_no, col_sub_typedesc, district, province,
                   discount_price, sell_price, shock_price, area_meter,
                   lat, lon, project_th, grade, first_seen_at,
                   asset_state
            FROM bam_properties
            WHERE first_seen_at >= %s
              AND discount_price IS NOT NULL
            ORDER BY first_seen_at DESC
            LIMIT 100
        """, (since,))
        for row in cur.fetchall():
            price = row[4] if row[4] else row[5]
            station_info = None
            if row[8] and row[9]:
                ns = nearest_station(float(row[8]), float(row[9]))
                if ns:
                    station_info = f"{ns[0]} ({ns[1]:.0f}m)"
            psqm = None
            if price and row[7] and float(row[7]) > 0:
                psqm = round(float(price) / float(row[7]))
            results.append({
                "source": "BAM",
                "asset_id": row[0],
                "type": row[1],
                "district": row[2],
                "province": row[3],
                "price": fmt_baht(price),
                "price_raw": int(float(price)) if price else None,
                "sell_price": fmt_baht(row[5]),
                "shock_price": fmt_baht(row[6]),
                "size_sqm": float(row[7]) if row[7] else None,
                "price_per_sqm": psqm,
                "station": station_info,
                "project": row[10],
                "grade": row[11],
                "first_seen": str(row[12]),
                "status": row[13],
            })

    # JAM new properties
    if source in ("all", "jam"):
        cur.execute("""
            SELECT asset_no, type_sale_th, amphur_name, province_name,
                   discount, selling, meter, lat, lon,
                   project_th, first_seen_at, type_asset_th,
                   status_hotdeal, is_flash_sale
            FROM jam_properties
            WHERE first_seen_at >= %s
              AND type_sale_th = 'ขาย'
              AND discount IS NOT NULL
            ORDER BY first_seen_at DESC
            LIMIT 100
        """, (since,))
        for row in cur.fetchall():
            price = row[4] if row[4] else row[5]
            station_info = None
            if row[7] and row[8]:
                ns = nearest_station(float(row[7]), float(row[8]))
                if ns:
                    station_info = f"{ns[0]} ({ns[1]:.0f}m)"
            psqm = None
            if price and row[6] and float(row[6]) > 0:
                psqm = round(float(price) / float(row[6]))
            tags = []
            if row[12]: tags.append("🔥HOT")
            if row[13]: tags.append("⚡FLASH")
            results.append({
                "source": "JAM",
                "asset_id": row[0],
                "type": row[1],
                "district": row[2],
                "province": row[3],
                "price": fmt_baht(price),
                "price_raw": int(float(price)) if price else None,
                "selling_price": fmt_baht(row[5]),
                "size_sqm": float(row[6]) if row[6] else None,
                "price_per_sqm": psqm,
                "station": station_info,
                "project": row[9],
                "first_seen": str(row[10]),
                "asset_type": row[11],
                "tags": tags,
            })

    # KTB new properties
    if source in ("all", "ktb"):
        cur.execute("""
            SELECT coll_mono_code, coll_type_name, amphur, province,
                   price, nml_price, area, lat, lon,
                   coll_desc, first_seen_at, is_new_asset, is_promotion
            FROM ktb_properties
            WHERE first_seen_at >= %s
              AND price IS NOT NULL
            ORDER BY first_seen_at DESC
            LIMIT 100
        """, (since,))
        for row in cur.fetchall():
            station_info = None
            if row[7] and row[8]:
                ns = nearest_station(float(row[7]), float(row[8]))
                if ns:
                    station_info = f"{ns[0]} ({ns[1]:.0f}m)"
            discount_pct = None
            if row[4] and row[5] and float(row[5]) > 0:
                discount_pct = round((1 - float(row[4]) / float(row[5])) * 100, 1)
            tags = []
            if row[11]: tags.append("🆕NEW")
            if row[12]: tags.append("🏷️PROMO")
            results.append({
                "source": "KTB",
                "asset_id": row[0],
                "type": row[1],
                "district": row[2],
                "province": row[3],
                "price": fmt_baht(row[4]),
                "price_raw": int(float(row[4])) if row[4] else None,
                "appraisal": fmt_baht(row[5]),
                "discount_pct": discount_pct,
                "area_text": row[6],
                "station": station_info,
                "description": row[9],
                "first_seen": str(row[10]),
                "tags": tags,
            })

    # KBANK new properties
    if source in ("all", "kbank"):
        cur.execute("""
            SELECT property_id, property_type_name, amphur_name, province_name,
                   sell_price, promotion_price, adjust_price, useable_area,
                   lat, lon, building_th, first_seen_at,
                   is_new, is_hot
            FROM kbank_properties
            WHERE first_seen_at >= %s
              AND sell_price IS NOT NULL
            ORDER BY first_seen_at DESC
            LIMIT 100
        """, (since,))
        for row in cur.fetchall():
            price = row[5] if row[5] else row[4]  # prefer promo price
            station_info = None
            if row[8] and row[9]:
                ns = nearest_station(float(row[8]), float(row[9]))
                if ns:
                    station_info = f"{ns[0]} ({ns[1]:.0f}m)"
            psqm = None
            if price and row[7] and float(row[7]) > 0:
                psqm = round(float(price) / float(row[7]))
            discount_pct = None
            if row[5] and row[4] and float(row[4]) > 0:
                discount_pct = round((1 - float(row[5]) / float(row[4])) * 100, 1)
            tags = []
            if row[12]: tags.append("🆕NEW")
            if row[13]: tags.append("🔥HOT")
            results.append({
                "source": "KBANK",
                "asset_id": row[0],
                "type": row[1],
                "district": row[2],
                "province": row[3],
                "price": fmt_baht(price),
                "price_raw": int(float(price)) if price else None,
                "sell_price": fmt_baht(row[4]),
                "promo_price": fmt_baht(row[5]),
                "discount_pct": discount_pct,
                "size_sqm": float(row[7]) if row[7] else None,
                "price_per_sqm": psqm,
                "station": station_info,
                "building": row[10],
                "first_seen": str(row[11]),
                "tags": tags,
            })

    conn.close()
    return results


# ─── ALERT: Best Deals (biggest discount below appraisal) ───

def alert_deals(max_price_satang=None, min_discount_pct=20, limit=20):
    """Find properties with biggest discount vs appraisal.
    
    Includes phantom-discount protection:
    - If enforcement_officer_price > 20x asking price → discount marked UNVERIFIED, capped at -95%
    - If enforcement_officer_price > 10x asking price → flagged STALE_APPRAISAL
      (likely multiple failed auctions drove price down but appraisal was never updated)
    """
    conn = get_conn()
    cur = conn.cursor()
    results = []

    max_price = max_price_satang  # in satang

    # Thresholds for appraisal sanity
    STALE_RATIO = 10       # appraisal > 10x price → stale flag
    UNVERIFIED_RATIO = 20  # appraisal > 20x price → unverified discount
    MAX_DISPLAY_DISCOUNT = 95.0  # cap displayed discount for unverified

    cur.execute("""
        SELECT p.asset_id, p.property_type, p.ampur, p.province,
               p.primary_price_satang, lp.enforcement_officer_price_satang as appraisal,
               p.sale_status, p.next_auction_date, p.address,
               ROUND(CAST((1 - p.primary_price_satang::float / NULLIF(lp.enforcement_officer_price_satang, 0)) * 100 AS numeric), 1) as discount_pct,
               ROUND(lp.enforcement_officer_price_satang::numeric / NULLIF(p.primary_price_satang, 0), 1) as price_ratio
        FROM properties p
        JOIN led_properties lp ON p.id = lp.id
        WHERE p.primary_price_satang IS NOT NULL
          AND lp.enforcement_officer_price_satang IS NOT NULL
          AND lp.enforcement_officer_price_satang > 0
          AND p.sale_status = 'ยังไม่ขาย'
          AND (1 - p.primary_price_satang::float / lp.enforcement_officer_price_satang) >= %s / 100.0
          AND (%s IS NULL OR p.primary_price_satang <= %s)
        ORDER BY discount_pct DESC
        LIMIT %s
    """, (min_discount_pct, max_price, max_price, limit))

    for row in cur.fetchall():
        raw_discount = float(row[9]) if row[9] else 0
        ratio = float(row[10]) if row[10] else 1.0

        # Phantom-discount sanity checks
        is_unverified = ratio > UNVERIFIED_RATIO
        is_stale = ratio > STALE_RATIO
        display_discount = min(raw_discount, MAX_DISPLAY_DISCOUNT) if is_unverified else raw_discount

        results.append({
            "source": "LED",
            "asset_id": row[0],
            "type": row[1],
            "district": row[2],
            "province": row[3],
            "price": fmt_price(row[4]),
            "appraisal": fmt_price(row[5]),
            "discount_pct": display_discount,
            "raw_discount_pct": raw_discount,
            "price_ratio": ratio,
            "stale_appraisal": is_stale,
            "discount_unverified": is_unverified,
            "status": row[6],
            "auction_date": str(row[7]) if row[7] else None,
            "address": row[8],
        })

    conn.close()
    return results


# ─── ALERT: Near BTS/MRT ───

def alert_near_transit(max_meters=500, max_price_baht=None, source="all", limit=30):
    """Find properties near BTS/MRT stations across ALL providers with GPS."""
    conn = get_conn()
    cur = conn.cursor()
    results = []

    # SAM properties with coordinates
    if source in ("all", "sam"):
        cur.execute("""
            SELECT code, type_name, district, province,
                   price_baht, size_sqm, status, lat, lng,
                   address_full, price_per_unit
            FROM sam_properties
            WHERE lat IS NOT NULL AND lng IS NOT NULL
              AND price_baht IS NOT NULL
              AND is_active = true
              AND (%s IS NULL OR price_baht <= %s)
        """, (max_price_baht, max_price_baht))

        for row in cur.fetchall():
            lat, lng = float(row[7]), float(row[8])
            ns = nearest_station(lat, lng, max_meters)
            if ns:
                results.append({
                    "source": "SAM",
                    "code": row[0],
                    "type": row[1],
                    "district": row[2],
                    "province": row[3],
                    "price": fmt_baht(row[4]),
                    "price_raw": int(row[4]) if row[4] else None,
                    "size_sqm": row[5],
                    "status": row[6],
                    "station": ns[0],
                    "distance_m": round(ns[1]),
                    "address": row[9],
                    "price_per_unit": row[10],
                })

    # BAM properties with coordinates
    if source in ("all", "bam"):
        cur.execute("""
            SELECT asset_no, col_sub_typedesc, district, province,
                   discount_price, sell_price, area_meter, lat, lon,
                   project_th, grade
            FROM bam_properties
            WHERE lat IS NOT NULL AND lon IS NOT NULL
              AND discount_price IS NOT NULL
              AND (%s IS NULL OR discount_price <= %s)
        """, (max_price_baht, max_price_baht))
        for row in cur.fetchall():
            lat, lng = float(row[7]), float(row[8])
            ns = nearest_station(lat, lng, max_meters)
            if ns:
                psqm = None
                if row[4] and row[6] and float(row[6]) > 0:
                    psqm = round(float(row[4]) / float(row[6]))
                results.append({
                    "source": "BAM",
                    "code": row[0],
                    "type": row[1],
                    "district": row[2],
                    "province": row[3],
                    "price": fmt_baht(row[4]),
                    "price_raw": int(float(row[4])) if row[4] else None,
                    "size_sqm": float(row[6]) if row[6] else None,
                    "status": "active",
                    "station": ns[0],
                    "distance_m": round(ns[1]),
                    "address": row[9],
                    "price_per_unit": psqm,
                    "grade": row[10],
                })

    # JAM properties with coordinates
    if source in ("all", "jam"):
        cur.execute("""
            SELECT asset_no, type_sale_th, amphur_name, province_name,
                   discount, meter, lat, lon, project_th
            FROM jam_properties
            WHERE lat IS NOT NULL AND lon IS NOT NULL
              AND discount IS NOT NULL
              AND type_sale_th = 'ขาย'
              AND (%s IS NULL OR discount <= %s)
        """, (max_price_baht, max_price_baht))
        for row in cur.fetchall():
            lat, lng = float(row[6]), float(row[7])
            ns = nearest_station(lat, lng, max_meters)
            if ns:
                psqm = None
                if row[4] and row[5] and float(row[5]) > 0:
                    psqm = round(float(row[4]) / float(row[5]))
                results.append({
                    "source": "JAM",
                    "code": row[0],
                    "type": row[1],
                    "district": row[2],
                    "province": row[3],
                    "price": fmt_baht(row[4]),
                    "price_raw": int(float(row[4])) if row[4] else None,
                    "size_sqm": float(row[5]) if row[5] else None,
                    "status": "active",
                    "station": ns[0],
                    "distance_m": round(ns[1]),
                    "address": row[8],
                    "price_per_unit": psqm,
                })

    # KTB properties with coordinates
    if source in ("all", "ktb"):
        cur.execute("""
            SELECT coll_mono_code, coll_type_name, amphur, province,
                   price, nml_price, area, lat, lon, coll_desc
            FROM ktb_properties
            WHERE lat IS NOT NULL AND lon IS NOT NULL
              AND price IS NOT NULL
              AND (%s IS NULL OR price <= %s)
        """, (max_price_baht, max_price_baht))
        for row in cur.fetchall():
            lat, lng = float(row[7]), float(row[8])
            ns = nearest_station(lat, lng, max_meters)
            if ns:
                results.append({
                    "source": "KTB",
                    "code": row[0],
                    "type": row[1],
                    "district": row[2],
                    "province": row[3],
                    "price": fmt_baht(row[4]),
                    "price_raw": int(float(row[4])) if row[4] else None,
                    "size_sqm": row[6],
                    "status": "active",
                    "station": ns[0],
                    "distance_m": round(ns[1]),
                    "address": row[9],
                    "price_per_unit": None,
                })

    # KBANK properties with coordinates
    if source in ("all", "kbank"):
        cur.execute("""
            SELECT property_id, property_type_name, amphur_name, province_name,
                   promotion_price, sell_price, useable_area, lat, lon,
                   building_th
            FROM kbank_properties
            WHERE lat IS NOT NULL AND lon IS NOT NULL
              AND sell_price IS NOT NULL
              AND (%s IS NULL OR COALESCE(promotion_price, sell_price) <= %s)
        """, (max_price_baht, max_price_baht))
        for row in cur.fetchall():
            lat, lng = float(row[7]), float(row[8])
            ns = nearest_station(lat, lng, max_meters)
            if ns:
                price = row[4] if row[4] else row[5]
                psqm = None
                if price and row[6] and float(row[6]) > 0:
                    psqm = round(float(price) / float(row[6]))
                results.append({
                    "source": "KBANK",
                    "code": row[0],
                    "type": row[1],
                    "district": row[2],
                    "province": row[3],
                    "price": fmt_baht(price),
                    "price_raw": int(float(price)) if price else None,
                    "size_sqm": float(row[6]) if row[6] else None,
                    "status": "active",
                    "station": ns[0],
                    "distance_m": round(ns[1]),
                    "address": row[9],
                    "price_per_unit": psqm,
                })

    # Sort by distance
    results.sort(key=lambda x: x.get("distance_m", 9999))
    return results[:limit]


# ─── ALERT: Upcoming Auctions ───

def alert_upcoming_auctions(days=14, province=None, limit=30):
    """Find LED properties with upcoming auction dates."""
    conn = get_conn()
    cur = conn.cursor()
    soon = datetime.now() + timedelta(days=days)
    now = datetime.now()

    query = """
        SELECT p.asset_id, p.property_type, p.ampur, p.province,
               p.primary_price_satang, p.appraisal_price_satang,
               p.next_auction_date, p.next_auction_status, p.address,
               p.total_auction_count, p.sale_status
        FROM properties p
        WHERE p.next_auction_date IS NOT NULL
          AND p.next_auction_date::date >= %s
          AND p.next_auction_date::date <= %s
          AND p.sale_status = 'ยังไม่ขาย'
    """
    params = [now.date(), soon.date()]
    if province:
        query += " AND p.province LIKE %s"
        params.append(f"%{province}%")
    query += " ORDER BY p.next_auction_date ASC LIMIT %s"
    params.append(limit)

    cur.execute(query, params)
    results = []
    for row in cur.fetchall():
        discount = None
        # primary_price is in satang, need to compare with enforcement officer price
        if row[4] and row[5] and row[5] > 0:
            discount = round((1 - row[4] / row[5]) * 100, 1)
        results.append({
            "source": "LED",
            "asset_id": row[0],
            "type": row[1],
            "district": row[2],
            "province": row[3],
            "price": fmt_price(row[4]),
            "appraisal": fmt_price(row[5]),
            "discount_pct": discount,
            "auction_date": str(row[6]),
            "auction_status": row[7],
            "address": row[8],
            "auction_count": row[9],
            "status": row[10],
        })

    conn.close()
    return results


# ─── ALERT: Price Changes ───

def alert_price_changes(hours=24, min_drop_pct=5, limit=30):
    """Find properties with price drops across all providers with price_history tables."""
    conn = get_conn()
    cur = conn.cursor()
    since = datetime.now() - timedelta(hours=hours)
    results = []

    # SAM price changes (has structured sam_price_history)
    cur.execute("""
        SELECT ph.property_code, ph.old_price_baht, ph.new_price_baht,
               ph.price_drop_pct, ph.size_sqm, ph.old_price_per_sqm,
               ph.new_price_per_sqm, ph.district, ph.province,
               ph.property_type, ph.created_at
        FROM sam_price_history ph
        WHERE ph.created_at >= %s
          AND ph.price_drop_pct >= %s
          AND ph.validation_status != 'invalid'
        ORDER BY ph.price_drop_pct DESC
        LIMIT %s
    """, (since, min_drop_pct, limit))
    for row in cur.fetchall():
        results.append({
            "source": "SAM",
            "code": row[0],
            "old_price": fmt_baht(row[1]),
            "new_price": fmt_baht(row[2]),
            "drop_pct": float(row[3]) if row[3] else 0,
            "size_sqm": row[4],
            "old_psqm": round(float(row[5])) if row[5] else None,
            "new_psqm": round(float(row[6])) if row[6] else None,
            "district": row[7],
            "province": row[8],
            "type": row[9],
            "changed_at": str(row[10]),
        })

    # BAM price drops (compare current vs previous in bam_price_history)
    cur.execute("""
        SELECT bp.asset_no, bp.col_sub_typedesc, bp.district, bp.province,
               bp.discount_price, bp.area_meter, bp.project_th,
               ph_old.discount_price as old_discount,
               ph_old.scraped_at as old_scraped
        FROM bam_properties bp
        JOIN LATERAL (
            SELECT discount_price, scraped_at
            FROM bam_price_history
            WHERE asset_id = bp.id AND change_type = 'price_drop'
              AND scraped_at >= %s
            ORDER BY scraped_at DESC LIMIT 1
        ) ph_old ON true
        WHERE ph_old.discount_price IS NOT NULL
          AND bp.discount_price IS NOT NULL
          AND ph_old.discount_price > bp.discount_price
          AND ((ph_old.discount_price - bp.discount_price) / ph_old.discount_price * 100) >= %s
        ORDER BY (ph_old.discount_price - bp.discount_price) / ph_old.discount_price DESC
        LIMIT %s
    """, (since, min_drop_pct, limit))
    for row in cur.fetchall():
        old_p = float(row[7])
        new_p = float(row[4])
        drop = round((1 - new_p / old_p) * 100, 1)
        psqm = round(new_p / float(row[5])) if row[5] and float(row[5]) > 0 else None
        results.append({
            "source": "BAM",
            "code": row[0],
            "type": row[1],
            "district": row[2],
            "province": row[3],
            "old_price": fmt_baht(old_p),
            "new_price": fmt_baht(new_p),
            "drop_pct": drop,
            "size_sqm": float(row[5]) if row[5] else None,
            "old_psqm": round(old_p / float(row[5])) if row[5] and float(row[5]) > 0 else None,
            "new_psqm": psqm,
            "project": row[6],
            "changed_at": str(row[8]),
        })

    # JAM price drops
    cur.execute("""
        SELECT jp.asset_no, jp.type_asset_th, jp.amphur_name, jp.province_name,
               jp.discount, jp.meter, jp.project_th,
               ph_old.discount as old_discount,
               ph_old.scraped_at as old_scraped
        FROM jam_properties jp
        JOIN LATERAL (
            SELECT discount, scraped_at
            FROM jam_price_history
            WHERE asset_id = jp.asset_id AND change_type = 'price_drop'
              AND scraped_at >= %s
            ORDER BY scraped_at DESC LIMIT 1
        ) ph_old ON true
        WHERE ph_old.discount IS NOT NULL
          AND jp.discount IS NOT NULL
          AND ph_old.discount > jp.discount
          AND ((ph_old.discount - jp.discount) / ph_old.discount * 100) >= %s
        ORDER BY (ph_old.discount - jp.discount) / ph_old.discount DESC
        LIMIT %s
    """, (since, min_drop_pct, limit))
    for row in cur.fetchall():
        old_p = float(row[7])
        new_p = float(row[4])
        drop = round((1 - new_p / old_p) * 100, 1)
        psqm = round(new_p / float(row[5])) if row[5] and float(row[5]) > 0 else None
        results.append({
            "source": "JAM",
            "code": row[0],
            "type": row[1],
            "district": row[2],
            "province": row[3],
            "old_price": fmt_baht(old_p),
            "new_price": fmt_baht(new_p),
            "drop_pct": drop,
            "size_sqm": float(row[5]) if row[5] else None,
            "old_psqm": round(old_p / float(row[5])) if row[5] and float(row[5]) > 0 else None,
            "new_psqm": psqm,
            "project": row[6],
            "changed_at": str(row[8]),
        })

    # KTB price drops
    cur.execute("""
        SELECT kp.coll_mono_code, kp.coll_type_name, kp.amphur, kp.province,
               kp.price, kp.area, kp.coll_desc,
               ph_old.price as old_price,
               ph_old.scraped_at as old_scraped
        FROM ktb_properties kp
        JOIN LATERAL (
            SELECT price, scraped_at
            FROM ktb_price_history
            WHERE coll_grp_id = kp.coll_grp_id AND change_type = 'price_drop'
              AND scraped_at >= %s
            ORDER BY scraped_at DESC LIMIT 1
        ) ph_old ON true
        WHERE ph_old.price IS NOT NULL
          AND kp.price IS NOT NULL
          AND ph_old.price > kp.price
          AND ((ph_old.price - kp.price) / ph_old.price * 100) >= %s
        ORDER BY (ph_old.price - kp.price) / ph_old.price DESC
        LIMIT %s
    """, (since, min_drop_pct, limit))
    for row in cur.fetchall():
        old_p = float(row[7])
        new_p = float(row[4])
        drop = round((1 - new_p / old_p) * 100, 1)
        results.append({
            "source": "KTB",
            "code": row[0],
            "type": row[1],
            "district": row[2],
            "province": row[3],
            "old_price": fmt_baht(old_p),
            "new_price": fmt_baht(new_p),
            "drop_pct": drop,
            "size_sqm": row[5],
            "old_psqm": None,
            "new_psqm": None,
            "project": row[6],
            "changed_at": str(row[8]),
        })

    # KBANK price drops
    cur.execute("""
        SELECT kp.property_id, kp.property_type_name, kp.amphur_name, kp.province_name,
               COALESCE(kp.promotion_price, kp.sell_price),
               kp.useable_area, kp.building_th,
               ph_old.sell_price as old_price,
               ph_old.scraped_at as old_scraped
        FROM kbank_properties kp
        JOIN LATERAL (
            SELECT sell_price, scraped_at
            FROM kbank_price_history
            WHERE property_id = kp.property_id AND change_type = 'price_drop'
              AND scraped_at >= %s
            ORDER BY scraped_at DESC LIMIT 1
        ) ph_old ON true
        WHERE ph_old.sell_price IS NOT NULL
          AND kp.sell_price IS NOT NULL
          AND ph_old.sell_price > COALESCE(kp.promotion_price, kp.sell_price)
          AND ((ph_old.sell_price - COALESCE(kp.promotion_price, kp.sell_price)) / ph_old.sell_price * 100) >= %s
        ORDER BY (ph_old.sell_price - COALESCE(kp.promotion_price, kp.sell_price)) / ph_old.sell_price DESC
        LIMIT %s
    """, (since, min_drop_pct, limit))
    for row in cur.fetchall():
        old_p = float(row[7])
        new_p = float(row[4])
        drop = round((1 - new_p / old_p) * 100, 1)
        psqm = round(new_p / float(row[5])) if row[5] and float(row[5]) > 0 else None
        results.append({
            "source": "KBANK",
            "code": row[0],
            "type": row[1],
            "district": row[2],
            "province": row[3],
            "old_price": fmt_baht(old_p),
            "new_price": fmt_baht(new_p),
            "drop_pct": drop,
            "size_sqm": float(row[5]) if row[5] else None,
            "old_psqm": round(old_p / float(row[5])) if row[5] and float(row[5]) > 0 else None,
            "new_psqm": psqm,
            "project": row[6],
            "changed_at": str(row[8]),
        })

    # Sort by drop percentage
    results.sort(key=lambda x: x.get("drop_pct", 0), reverse=True)
    conn.close()
    return results[:limit]


# ─── ALERT: Price Increases ───

def alert_price_increases(hours=24, min_increase_pct=5, limit=30):
    """Find properties with price increases — unusual for NPA, worth investigating."""
    conn = get_conn()
    cur = conn.cursor()
    since = datetime.now() - timedelta(hours=hours)
    results = []

    # SAM price increases (structured sam_price_history has negative drop_pct for increases)
    cur.execute("""
        SELECT ph.property_code, ph.old_price_baht, ph.new_price_baht,
               ph.price_drop_pct, ph.size_sqm, ph.old_price_per_sqm,
               ph.new_price_per_sqm, ph.district, ph.province,
               ph.property_type, ph.created_at
        FROM sam_price_history ph
        WHERE ph.created_at >= %s
          AND ph.price_drop_pct <= -%s
          AND ph.validation_status != 'invalid'
        ORDER BY ph.price_drop_pct ASC
        LIMIT %s
    """, (since, min_increase_pct, limit))
    for row in cur.fetchall():
        increase_pct = abs(float(row[3])) if row[3] else 0
        results.append({
            "source": "SAM",
            "code": row[0],
            "old_price": fmt_baht(row[1]),
            "new_price": fmt_baht(row[2]),
            "increase_pct": increase_pct,
            "size_sqm": row[4],
            "old_psqm": round(float(row[5])) if row[5] else None,
            "new_psqm": round(float(row[6])) if row[6] else None,
            "district": row[7],
            "province": row[8],
            "type": row[9],
            "changed_at": str(row[10]),
        })

    # BAM price increases (try change_type first, then compare first vs current)
    # Approach: compare earliest price_history entry to current price
    cur.execute("""
        SELECT bp.asset_no, bp.col_sub_typedesc, bp.district, bp.province,
               bp.discount_price, bp.area_meter, bp.project_th,
               ph_first.discount_price as first_discount,
               ph_first.scraped_at as first_scraped
        FROM bam_properties bp
        JOIN LATERAL (
            SELECT discount_price, scraped_at
            FROM bam_price_history
            WHERE asset_id = bp.id
            ORDER BY scraped_at ASC LIMIT 1
        ) ph_first ON true
        WHERE ph_first.discount_price IS NOT NULL
          AND bp.discount_price IS NOT NULL
          AND bp.discount_price > ph_first.discount_price
          AND ((bp.discount_price - ph_first.discount_price) / ph_first.discount_price * 100) >= %s
          AND ph_first.scraped_at >= %s
        ORDER BY (bp.discount_price - ph_first.discount_price) / ph_first.discount_price DESC
        LIMIT %s
    """, (min_increase_pct, since, limit))
    for row in cur.fetchall():
        old_p = float(row[7])
        new_p = float(row[4])
        increase = round((new_p / old_p - 1) * 100, 1)
        psqm = round(new_p / float(row[5])) if row[5] and float(row[5]) > 0 else None
        results.append({
            "source": "BAM",
            "code": row[0],
            "type": row[1],
            "district": row[2],
            "province": row[3],
            "old_price": fmt_baht(old_p),
            "new_price": fmt_baht(new_p),
            "increase_pct": increase,
            "size_sqm": float(row[5]) if row[5] else None,
            "old_psqm": round(old_p / float(row[5])) if row[5] and float(row[5]) > 0 else None,
            "new_psqm": psqm,
            "project": row[6],
            "changed_at": str(row[8]),
        })

    # JAM price increases
    cur.execute("""
        SELECT jp.asset_no, jp.type_asset_th, jp.amphur_name, jp.province_name,
               jp.discount, jp.meter, jp.project_th,
               ph_first.discount as first_discount,
               ph_first.scraped_at as first_scraped
        FROM jam_properties jp
        JOIN LATERAL (
            SELECT discount, scraped_at
            FROM jam_price_history
            WHERE asset_id = jp.asset_id
            ORDER BY scraped_at ASC LIMIT 1
        ) ph_first ON true
        WHERE ph_first.discount IS NOT NULL
          AND jp.discount IS NOT NULL
          AND jp.discount > ph_first.discount
          AND ((jp.discount - ph_first.discount) / ph_first.discount * 100) >= %s
          AND ph_first.scraped_at >= %s
        ORDER BY (jp.discount - ph_first.discount) / ph_first.discount DESC
        LIMIT %s
    """, (min_increase_pct, since, limit))
    for row in cur.fetchall():
        old_p = float(row[7])
        new_p = float(row[4])
        increase = round((new_p / old_p - 1) * 100, 1)
        psqm = round(new_p / float(row[5])) if row[5] and float(row[5]) > 0 else None
        results.append({
            "source": "JAM",
            "code": row[0],
            "type": row[1],
            "district": row[2],
            "province": row[3],
            "old_price": fmt_baht(old_p),
            "new_price": fmt_baht(new_p),
            "increase_pct": increase,
            "size_sqm": float(row[5]) if row[5] else None,
            "old_psqm": round(old_p / float(row[5])) if row[5] and float(row[5]) > 0 else None,
            "new_psqm": psqm,
            "project": row[6],
            "changed_at": str(row[8]),
        })

    # KTB price increases
    cur.execute("""
        SELECT kp.coll_mono_code, kp.coll_type_name, kp.amphur, kp.province,
               kp.price, kp.area, kp.coll_desc,
               ph_first.price as first_price,
               ph_first.scraped_at as first_scraped
        FROM ktb_properties kp
        JOIN LATERAL (
            SELECT price, scraped_at
            FROM ktb_price_history
            WHERE coll_grp_id = kp.coll_grp_id
            ORDER BY scraped_at ASC LIMIT 1
        ) ph_first ON true
        WHERE ph_first.price IS NOT NULL
          AND kp.price IS NOT NULL
          AND kp.price > ph_first.price
          AND ((kp.price - ph_first.price) / ph_first.price * 100) >= %s
          AND ph_first.scraped_at >= %s
        ORDER BY (kp.price - ph_first.price) / ph_first.price DESC
        LIMIT %s
    """, (min_increase_pct, since, limit))
    for row in cur.fetchall():
        old_p = float(row[7])
        new_p = float(row[4])
        increase = round((new_p / old_p - 1) * 100, 1)
        results.append({
            "source": "KTB",
            "code": row[0],
            "type": row[1],
            "district": row[2],
            "province": row[3],
            "old_price": fmt_baht(old_p),
            "new_price": fmt_baht(new_p),
            "increase_pct": increase,
            "size_sqm": row[5],
            "old_psqm": None,
            "new_psqm": None,
            "project": row[6],
            "changed_at": str(row[8]),
        })

    # KBANK price increases
    cur.execute("""
        SELECT kp.property_id, kp.property_type_name, kp.amphur_name, kp.province_name,
               COALESCE(kp.promotion_price, kp.sell_price),
               kp.useable_area, kp.building_th,
               ph_first.sell_price as first_price,
               ph_first.scraped_at as first_scraped
        FROM kbank_properties kp
        JOIN LATERAL (
            SELECT sell_price, scraped_at
            FROM kbank_price_history
            WHERE property_id = kp.property_id
            ORDER BY scraped_at ASC LIMIT 1
        ) ph_first ON true
        WHERE ph_first.sell_price IS NOT NULL
          AND kp.sell_price IS NOT NULL
          AND COALESCE(kp.promotion_price, kp.sell_price) > ph_first.sell_price
          AND ((COALESCE(kp.promotion_price, kp.sell_price) - ph_first.sell_price) / ph_first.sell_price * 100) >= %s
          AND ph_first.scraped_at >= %s
        ORDER BY (COALESCE(kp.promotion_price, kp.sell_price) - ph_first.sell_price) / ph_first.sell_price DESC
        LIMIT %s
    """, (min_increase_pct, since, limit))
    for row in cur.fetchall():
        old_p = float(row[7])
        new_p = float(row[4])
        increase = round((new_p / old_p - 1) * 100, 1)
        psqm = round(new_p / float(row[5])) if row[5] and float(row[5]) > 0 else None
        results.append({
            "source": "KBANK",
            "code": row[0],
            "type": row[1],
            "district": row[2],
            "province": row[3],
            "old_price": fmt_baht(old_p),
            "new_price": fmt_baht(new_p),
            "increase_pct": increase,
            "size_sqm": float(row[5]) if row[5] else None,
            "old_psqm": round(old_p / float(row[5])) if row[5] and float(row[5]) > 0 else None,
            "new_psqm": psqm,
            "project": row[6],
            "changed_at": str(row[8]),
        })

    # Sort by increase percentage (largest first)
    results.sort(key=lambda x: x.get("increase_pct", 0), reverse=True)
    conn.close()
    return results[:limit]


# ─── REPORT: Full Daily Report ───

def generate_report():
    """Generate a comprehensive daily alert report."""
    lines = ["🏠 **NPA Daily Alert Report**", f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}", ""]

    # 1. New properties
    new = alert_new_properties(hours=24)
    # Count by source
    by_source = {}
    for p in new:
        s = p["source"]
        by_source[s] = by_source.get(s, 0) + 1
    source_str = " | ".join(f"{s}: {c}" for s, c in sorted(by_source.items()))
    lines.append(f"**🆕 New Properties (last 24h): {len(new)}**")
    if source_str:
        lines.append(f"  {source_str}")
    for p in new[:15]:
        if p["source"] == "LED":
            disc = f" (-{p['discount_pct']}%)" if p.get("discount_pct") else ""
            lines.append(f"  LED {p['asset_id']}: {p['price']}{disc} — {p['type']}, {p['district']}, {p['province']}")
        elif p["source"] == "SAM":
            st = f" 🚇{p['station']}" if p.get("station") else ""
            lines.append(f"  SAM {p['code']}: {p['price']} — {p['type']}, {p['district']}{st}")
        elif p["source"] == "BAM":
            st = f" 🚇{p['station']}" if p.get("station") else ""
            gr = f" [{p['grade']}]" if p.get("grade") else ""
            psqm = f" ฿{p['price_per_sqm']:,}/sqm" if p.get("price_per_sqm") else ""
            lines.append(f"  BAM {p['asset_id']}: {p['price']}{psqm}{gr} — {p.get('project','?')}, {p['district']}{st}")
        elif p["source"] == "JAM":
            st = f" 🚇{p['station']}" if p.get("station") else ""
            tags = f" {' '.join(p['tags'])}" if p.get('tags') else ""
            psqm = f" ฿{p['price_per_sqm']:,}/sqm" if p.get("price_per_sqm") else ""
            lines.append(f"  JAM {p['asset_id']}: {p['price']}{psqm}{tags} — {p.get('project','?')}, {p['district']}{st}")
        elif p["source"] == "KTB":
            st = f" 🚇{p['station']}" if p.get("station") else ""
            disc = f" (-{p['discount_pct']}%)" if p.get("discount_pct") else ""
            tags = f" {' '.join(p['tags'])}" if p.get('tags') else ""
            lines.append(f"  KTB {p['asset_id']}: {p['price']}{disc}{tags} — {p['district']}{st}")
        elif p["source"] == "KBANK":
            st = f" 🚇{p['station']}" if p.get("station") else ""
            disc = f" (-{p['discount_pct']}% promo)" if p.get("discount_pct") else ""
            tags = f" {' '.join(p['tags'])}" if p.get('tags') else ""
            psqm = f" ฿{p['price_per_sqm']:,}/sqm" if p.get("price_per_sqm") else ""
            lines.append(f"  KBANK {p['asset_id']}: {p['price']}{psqm}{disc}{tags} — {p.get('building','?')}, {p['district']}{st}")
    if len(new) > 15:
        lines.append(f"  ... and {len(new) - 15} more")
    lines.append("")

    # 2. Price drops
    drops = alert_price_changes(hours=24, min_drop_pct=5, limit=15)
    lines.append(f"**📉 Price Drops (last 24h, ≥5% drop): {len(drops)}**")
    for p in drops[:10]:
        psqm_str = ""
        if p.get("new_psqm"):
            psqm_str = f" (฿{p['new_psqm']:,}/sqm)"
        lines.append(f"  {p['source']} {p['code']}: {p['old_price']} → {p['new_price']} (-{p['drop_pct']}%){psqm_str}")
        proj = p.get("project", "")
        if proj:
            lines.append(f"    {proj}, {p['district']}")
    lines.append("")

    # 2b. Price increases — unusual for NPA, worth investigating
    increases = alert_price_increases(hours=24, min_increase_pct=5, limit=15)
    lines.append(f"**📈 Price Increases (last 24h, ≥5% up): {len(increases)}** ⚠️ unusual — investigate why")
    for p in increases[:10]:
        psqm_str = ""
        if p.get("new_psqm"):
            psqm_str = f" (฿{p['new_psqm']:,}/sqm)"
        lines.append(f"  {p['source']} {p['code']}: {p['old_price']} → {p['new_price']} (+{p['increase_pct']}%){psqm_str}")
        proj = p.get("project", "")
        if proj:
            lines.append(f"    {proj}, {p['district']}")
    lines.append("")

    # 3. Best deals
    deals = alert_deals(min_discount_pct=30, limit=10)
    unv = sum(1 for p in deals if p.get("discount_unverified"))
    stale = sum(1 for p in deals if p.get("stale_appraisal"))
    lines.append(f"**💰 Best Deals (>30% below appraisal): {len(deals)}**")
    if stale:
        lines.append(f"  ⚠️ {stale} have stale appraisals, {unv} unverified discounts capped at -95%")
    for p in deals[:10]:
        flag = " ⚠️" if p.get("discount_unverified") or p.get("stale_appraisal") else ""
        lines.append(f"  LED {p['asset_id']}: {p['price']} (appraised {p['appraisal']}, -{p['discount_pct']}%){flag} — {p['district']}, {p['province']}")
    lines.append("")

    # 4. Near BTS/MRT
    transit = alert_near_transit(max_meters=500, limit=10)
    lines.append(f"**🚇 Near BTS/MRT (<500m): {len(transit)}**")
    for p in transit[:10]:
        psqm = f" ({fmt_baht(p['price_per_unit'])}/sqm)" if p.get("price_per_unit") else ""
        lines.append(f"  {p['source']} {p['code']}: {p['price']}{psqm} — {p['station']} ({p['distance_m']}m), {p['district']}")
    lines.append("")

    # 5. Upcoming auctions
    upcoming = alert_upcoming_auctions(days=30, limit=10)
    lines.append(f"**📅 Upcoming Auctions (30 days): {len(upcoming)}**")
    for p in upcoming[:10]:
        disc = f" (-{p['discount_pct']}%)" if p.get("discount_pct") else ""
        lines.append(f"  LED {p['asset_id']}: {p['price']}{disc} — {p['auction_date']}, {p['district']}, {p['province']}")
    lines.append("")

    return "\n".join(lines)


# ─── MAIN ───

def main():
    parser = argparse.ArgumentParser(description="NPA Property Alerts")
    sub = parser.add_subparsers(dest="command")

    # new
    p_new = sub.add_parser("new", help="New properties in last N hours")
    p_new.add_argument("--hours", type=int, default=24)
    p_new.add_argument("--source", choices=["all", "led", "sam", "bam", "jam", "ktb", "kbank"], default="all")
    p_new.add_argument("--json", action="store_true")

    # deals
    p_deals = sub.add_parser("deals", help="Best deals (biggest discount)")
    p_deals.add_argument("--max-price", type=int, help="Max price in baht")
    p_deals.add_argument("--min-discount", type=int, default=20, help="Min discount %%")
    p_deals.add_argument("--limit", type=int, default=20)
    p_deals.add_argument("--json", action="store_true")

    # bts
    p_bts = sub.add_parser("bts", help="Properties near BTS/MRT")
    p_bts.add_argument("--meters", type=int, default=500)
    p_bts.add_argument("--max-price", type=int, help="Max price in baht")
    p_bts.add_argument("--source", choices=["all", "sam", "bam", "jam", "ktb", "kbank"], default="all")
    p_bts.add_argument("--limit", type=int, default=30)
    p_bts.add_argument("--json", action="store_true")

    # upcoming
    p_up = sub.add_parser("upcoming", help="Upcoming auctions")
    p_up.add_argument("--days", type=int, default=14)
    p_up.add_argument("--province", type=str, default=None)
    p_up.add_argument("--limit", type=int, default=30)
    p_up.add_argument("--json", action="store_true")

    # drops (new)
    p_drops = sub.add_parser("drops", help="Price drops across all providers")
    p_drops.add_argument("--hours", type=int, default=24, help="Look back N hours")
    p_drops.add_argument("--min-drop", type=int, default=5, help="Min drop %%")
    p_drops.add_argument("--limit", type=int, default=30)
    p_drops.add_argument("--json", action="store_true")

    # increases (new)
    p_up = sub.add_parser("increases", help="Price increases — unusual for NPA, worth investigating")
    p_up.add_argument("--hours", type=int, default=24, help="Look back N hours")
    p_up.add_argument("--min-increase", type=int, default=5, help="Min increase %%")
    p_up.add_argument("--limit", type=int, default=30)
    p_up.add_argument("--json", action="store_true")

    # report
    sub.add_parser("report", help="Full daily report")

    args = parser.parse_args()

    if args.command == "new":
        results = alert_new_properties(args.hours, args.source)
        if args.json:
            print(json.dumps(results, ensure_ascii=False, indent=2))
        else:
            by_source = {}
            for p in results:
                s = p["source"]
                by_source[s] = by_source.get(s, 0) + 1
            source_str = " | ".join(f"{s}: {c}" for s, c in sorted(by_source.items()))
            print(f"🆕 New Properties (last {args.hours}h): {len(results)} found")
            if source_str:
                print(f"   {source_str}\n")
            for p in results[:30]:
                if p["source"] == "LED":
                    disc = f" (-{p['discount_pct']}%)" if p.get("discount_pct") else ""
                    print(f"  LED {p['asset_id']}: {p['price']}{disc} — {p['type']}, {p['district']}, {p['province']}")
                elif p["source"] == "SAM":
                    st = f" 🚇{p['station']}" if p.get("station") else ""
                    print(f"  SAM {p['code']}: {p['price']} — {p['type']}, {p['district']}{st}")
                elif p["source"] == "BAM":
                    st = f" 🚇{p['station']}" if p.get("station") else ""
                    gr = f" [{p['grade']}]" if p.get("grade") else ""
                    psqm = f" ฿{p['price_per_sqm']:,}/sqm" if p.get("price_per_sqm") else ""
                    print(f"  BAM {p['asset_id']}: {p['price']}{psqm}{gr} — {p.get('project','?')}, {p['district']}{st}")
                elif p["source"] == "JAM":
                    st = f" 🚇{p['station']}" if p.get("station") else ""
                    tags = f" {' '.join(p['tags'])}" if p.get("tags") else ""
                    psqm = f" ฿{p['price_per_sqm']:,}/sqm" if p.get("price_per_sqm") else ""
                    print(f"  JAM {p['asset_id']}: {p['price']}{psqm}{tags} — {p.get('project','?')}, {p['district']}{st}")
                elif p["source"] == "KTB":
                    st = f" 🚇{p['station']}" if p.get("station") else ""
                    disc = f" (-{p['discount_pct']}%)" if p.get("discount_pct") else ""
                    tags = f" {' '.join(p['tags'])}" if p.get("tags") else ""
                    print(f"  KTB {p['asset_id']}: {p['price']}{disc}{tags} — {p['district']}{st}")
                elif p["source"] == "KBANK":
                    st = f" 🚇{p['station']}" if p.get("station") else ""
                    disc = f" (-{p['discount_pct']}% promo)" if p.get("discount_pct") else ""
                    tags = f" {' '.join(p['tags'])}" if p.get("tags") else ""
                    psqm = f" ฿{p['price_per_sqm']:,}/sqm" if p.get("price_per_sqm") else ""
                    print(f"  KBANK {p['asset_id']}: {p['price']}{psqm}{disc}{tags} — {p.get('building','?')}, {p['district']}{st}")
            if len(results) > 30:
                print(f"\n  ... and {len(results) - 30} more")

    elif args.command == "deals":
        max_satang = args.max_price * 100 if args.max_price else None
        results = alert_deals(max_satang, args.min_discount, args.limit)
        if args.json:
            print(json.dumps(results, ensure_ascii=False, indent=2))
        else:
            unverified_count = sum(1 for p in results if p.get("discount_unverified"))
            stale_count = sum(1 for p in results if p.get("stale_appraisal"))
            print(f"💰 Best Deals (>{args.min_discount}% below appraisal): {len(results)} found")
            if stale_count:
                print(f"   ⚠️  {stale_count} have stale appraisals (asking price << original appraisal)")
            if unverified_count:
                print(f"   🔍 {unverified_count} have unverified discounts (capped at -95%)")
            print()
            for p in results:
                flags = ""
                if p.get("discount_unverified"):
                    raw = p.get("raw_discount_pct", 0)
                    flags = f" [UNVERIFIED raw=-{raw}%]"
                elif p.get("stale_appraisal"):
                    flags = " [STALE APPRAISAL]"
                print(f"  LED {p['asset_id']}: {p['price']} (appraised {p['appraisal']}, -{p['discount_pct']}%){flags}")
                print(f"    {p['type']}, {p['district']}, {p['province']} | Auction: {p.get('auction_date', 'TBD')}")

    elif args.command == "bts":
        results = alert_near_transit(args.meters, args.max_price, args.source, args.limit)
        if args.json:
            print(json.dumps(results, ensure_ascii=False, indent=2))
        else:
            print(f"🚇 Near BTS/MRT (<{args.meters}m): {len(results)} found\n")
            for p in results:
                psqm = f" ({fmt_baht(p['price_per_unit'])}/sqm)" if p.get("price_per_unit") else ""
                print(f"  {p['source']} {p['code']}: {p['price']}{psqm} — {p['station']} ({p['distance_m']}m)")
                print(f"    {p.get('type','?')}, {p['district']}, {p.get('status','')}")

    elif args.command == "drops":
        results = alert_price_changes(args.hours, args.min_drop, args.limit)
        if args.json:
            print(json.dumps(results, ensure_ascii=False, indent=2))
        else:
            print(f"📉 Price Drops (last {args.hours}h, ≥{args.min_drop}% drop): {len(results)} found\n")
            for p in results:
                psqm_str = ""
                if p.get("new_psqm"):
                    psqm_str = f" (฿{p['new_psqm']:,}/sqm)"
                print(f"  {p['source']} {p['code']}: {p['old_price']} → {p['new_price']} (-{p['drop_pct']}%){psqm_str}")
                proj = p.get("project", "")
                dist = p.get("district", "")
                if proj or dist:
                    print(f"    {proj}, {dist}")

    elif args.command == "increases":
        results = alert_price_increases(args.hours, args.min_increase, args.limit)
        if args.json:
            print(json.dumps(results, ensure_ascii=False, indent=2))
        else:
            print(f"📈 Price Increases (last {args.hours}h, ≥{args.min_increase}% up): {len(results)} found")
            print(f"   ⚠️ Price increases on NPA are unusual — investigate why!\n")
            for p in results:
                psqm_str = ""
                if p.get("new_psqm"):
                    psqm_str = f" (฿{p['new_psqm']:,}/sqm)"
                print(f"  {p['source']} {p['code']}: {p['old_price']} → {p['new_price']} (+{p['increase_pct']}%){psqm_str}")
                proj = p.get("project", "")
                dist = p.get("district", "")
                if proj or dist:
                    print(f"    {proj}, {dist}")

    elif args.command == "upcoming":
        results = alert_upcoming_auctions(args.days, args.province, args.limit)
        if args.json:
            print(json.dumps(results, ensure_ascii=False, indent=2))
        else:
            prov = f" in {args.province}" if args.province else ""
            print(f"📅 Upcoming Auctions (next {args.days} days){prov}: {len(results)} found\n")
            for p in results:
                disc = f" (-{p['discount_pct']}%)" if p.get("discount_pct") else ""
                count = f" [{p['auction_count']}th auction]" if p.get("auction_count") else ""
                print(f"  LED {p['asset_id']}: {p['price']}{disc}{count}")
                print(f"    {p['type']}, {p['district']}, {p['province']} | Date: {p['auction_date']}")

    elif args.command == "report":
        print(generate_report())

    else:
        parser.print_help()


if __name__ == "__main__":
    main()

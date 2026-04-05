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
    """Find properties added in the last N hours."""
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
    """Find SAM/LED properties near BTS/MRT stations."""
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

    # LED doesn't have coordinates in current schema, skip for now

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


# ─── REPORT: Full Daily Report ───

def generate_report():
    """Generate a comprehensive daily alert report."""
    lines = ["🏠 **NPA Daily Alert Report**", f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}", ""]

    # 1. New properties
    new = alert_new_properties(hours=24)
    lines.append(f"**🆕 New Properties (last 24h): {len(new)}**")
    for p in new[:10]:
        if p["source"] == "LED":
            disc = f" (-{p['discount_pct']}%)" if p.get("discount_pct") else ""
            lines.append(f"  LED {p['asset_id']}: {p['price']}{disc} — {p['type']}, {p['district']}, {p['province']}")
        else:
            st = f" 🚇{p['station']}" if p.get("station") else ""
            lines.append(f"  SAM {p['code']}: {p['price']} — {p['type']}, {p['district']}{st}")
    if len(new) > 10:
        lines.append(f"  ... and {len(new) - 10} more")
    lines.append("")

    # 2. Best deals
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

    # 3. Near BTS/MRT
    transit = alert_near_transit(max_meters=500, limit=10)
    lines.append(f"**🚇 Near BTS/MRT (<500m): {len(transit)}**")
    for p in transit[:10]:
        psqm = f" ({fmt_baht(p['price_per_unit'])}/sqm)" if p.get("price_per_unit") else ""
        lines.append(f"  SAM {p['code']}: {p['price']}{psqm} — {p['station']} ({p['distance_m']}m), {p['district']}")
    lines.append("")

    # 4. Upcoming auctions
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
    p_new.add_argument("--source", choices=["all", "led", "sam"], default="all")
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
    p_bts.add_argument("--source", choices=["all", "sam"], default="all")
    p_bts.add_argument("--limit", type=int, default=30)
    p_bts.add_argument("--json", action="store_true")

    # upcoming
    p_up = sub.add_parser("upcoming", help="Upcoming auctions")
    p_up.add_argument("--days", type=int, default=14)
    p_up.add_argument("--province", type=str, default=None)
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
            print(f"🆕 New Properties (last {args.hours}h): {len(results)} found\n")
            for p in results[:30]:
                if p["source"] == "LED":
                    disc = f" (-{p['discount_pct']}%)" if p.get("discount_pct") else ""
                    print(f"  LED {p['asset_id']}: {p['price']}{disc} — {p['type']}, {p['district']}, {p['province']}")
                else:
                    st = f" 🚇{p['station']}" if p.get("station") else ""
                    print(f"  SAM {p['code']}: {p['price']} — {p['type']}, {p['district']}{st}")
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
                print(f"  SAM {p['code']}: {p['price']}{psqm} — {p['station']} ({p['distance_m']}m)")
                print(f"    {p['type']}, {p['district']}, {p['status']}")

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

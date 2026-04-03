#!/usr/bin/env python3
"""Query LED NPA properties from local PostgreSQL database.

IMPORTANT: In the properties table, the column `size_wa` has different units
depending on property type:
  - ห้องชุด (condo): size_wa stores ตร.ม. (square meters), NOT ตร.วา
  - ที่ดิน (land) and other types: size_wa stores ตร.วา (square wah) as expected

This is because LED labels the field as "ขนาด" without specifying units.
For condos, the value is always in sq.m.
"""

import argparse
import json
import os
import sys

import psycopg2
import psycopg2.extras

POSTGRES_URI = os.getenv("POSTGRES_URI", "postgresql://arsapolm@localhost:5432/npa_kb")


def get_conn():
    return psycopg2.connect(POSTGRES_URI)


def search_properties(
    province=None, district=None, sub_district=None,
    min_price=None, max_price=None,
    property_type=None, sale_status=None,
    keyword=None,
    limit=20, offset=0,
    sort_by="primary_price_satang", sort_order="ASC",
):
    """Search properties with filters."""
    conditions = ["1=1"]
    params = []

    if province:
        conditions.append("p.province ILIKE %s")
        params.append(f"%{province}%")
    if district:
        conditions.append("p.ampur ILIKE %s")
        params.append(f"%{district}%")
    if sub_district:
        conditions.append("p.tumbol ILIKE %s")
        params.append(f"%{sub_district}%")
    if min_price is not None:
        conditions.append("p.primary_price_satang >= %s")
        params.append(int(min_price * 100))
    if max_price is not None:
        conditions.append("p.primary_price_satang <= %s")
        params.append(int(max_price * 100))
    if property_type:
        conditions.append("p.property_type ILIKE %s")
        params.append(f"%{property_type}%")
    if sale_status:
        conditions.append("p.sale_status ILIKE %s")
        params.append(f"%{sale_status}%")
    if keyword:
        conditions.append("(p.address ILIKE %s OR l.remark ILIKE %s)")
        params.append(f"%{keyword}%")
        params.append(f"%{keyword}%")

    allowed_sorts = {
        "price": "p.primary_price_satang",
        "province": "p.province",
        "auction_date": "p.next_auction_date",
        "created": "p.created_at",
    }
    order_col = allowed_sorts.get(sort_by, "p.primary_price_satang")
    order_dir = "DESC" if sort_order.upper() == "DESC" else "ASC"

    where = " AND ".join(conditions)
    params.extend([limit, offset])

    sql = f"""
        SELECT
            p.asset_id, p.property_type, p.address, p.province, p.ampur, p.tumbol,
            p.size_rai, p.size_ngan, p.size_wa,
            p.primary_price_satang, p.sale_status,
            p.next_auction_date, p.last_auction_date, p.total_auction_count,
            l.case_number, l.court, l.deed_type,
            l.enforcement_officer_price_satang,
            l.committee_determined_price_satang,
            l.plaintiff, l.defendant, l.sale_location, l.contact_phone
        FROM properties p
        LEFT JOIN led_properties l ON p.asset_id = l.asset_id
        WHERE {where}
        ORDER BY {order_col} {order_dir}
        LIMIT %s OFFSET %s
    """

    conn = get_conn()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()

            # Count total
            count_sql = f"""
                SELECT COUNT(*) FROM properties p
                LEFT JOIN led_properties l ON p.asset_id = l.asset_id
                WHERE {where}
            """
            cur.execute(count_sql, params[:-2])
            total = cur.fetchone()["count"]

        return {"total": total, "showing": len(rows), "properties": [dict(r) for r in rows]}
    finally:
        conn.close()


def upcoming_auctions(days=30, province=None, limit=20):
    """Find properties with upcoming auctions."""
    conditions = [
        "p.next_auction_date IS NOT NULL",
        "p.next_auction_date >= CURRENT_DATE",
        f"p.next_auction_date <= CURRENT_DATE + INTERVAL '{int(days)} days'",
    ]
    params = []

    if province:
        conditions.append("p.province ILIKE %s")
        params.append(f"%{province}%")

    where = " AND ".join(conditions)
    params.append(limit)

    sql = f"""
        SELECT
            p.asset_id, p.property_type, p.address, p.province, p.ampur,
            p.primary_price_satang, p.sale_status,
            p.next_auction_date, p.total_auction_count,
            l.case_number, l.court, l.deed_type, l.sale_location
        FROM properties p
        LEFT JOIN led_properties l ON p.asset_id = l.asset_id
        WHERE {where}
        ORDER BY p.next_auction_date ASC
        LIMIT %s
    """

    conn = get_conn()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()
        return {"total": len(rows), "properties": [dict(r) for r in rows]}
    finally:
        conn.close()


def price_stats(province=None, district=None, property_type=None):
    """Get price statistics by area."""
    conditions = ["p.primary_price_satang > 0"]
    params = []

    if province:
        conditions.append("p.province ILIKE %s")
        params.append(f"%{province}%")
    if district:
        conditions.append("p.ampur ILIKE %s")
        params.append(f"%{district}%")
    if property_type:
        conditions.append("p.property_type ILIKE %s")
        params.append(f"%{property_type}%")

    where = " AND ".join(conditions)

    sql = f"""
        SELECT
            p.province,
            p.ampur,
            p.property_type,
            COUNT(*) as count,
            MIN(p.primary_price_satang) / 100.0 as min_price_baht,
            MAX(p.primary_price_satang) / 100.0 as max_price_baht,
            AVG(p.primary_price_satang) / 100.0 as avg_price_baht,
            PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY p.primary_price_satang) / 100.0 as median_price_baht
        FROM properties p
        WHERE {where}
        GROUP BY p.province, p.ampur, p.property_type
        HAVING COUNT(*) >= 3
        ORDER BY COUNT(*) DESC
        LIMIT 30
    """

    conn = get_conn()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, params)
            rows = cur.fetchall()

        for row in rows:
            for key in ["min_price_baht", "max_price_baht", "avg_price_baht", "median_price_baht"]:
                if row[key] is not None:
                    row[key] = round(float(row[key]), 2)

        return {"stats": [dict(r) for r in rows]}
    finally:
        conn.close()


def summary():
    """Get database summary statistics."""
    conn = get_conn()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT COUNT(*) as total FROM properties")
            total = cur.fetchone()["total"]

            cur.execute("""
                SELECT province, COUNT(*) as count
                FROM properties
                GROUP BY province
                ORDER BY count DESC
            """)
            by_province = [dict(r) for r in cur.fetchall()]

            cur.execute("""
                SELECT sale_status, COUNT(*) as count
                FROM properties
                GROUP BY sale_status
                ORDER BY count DESC
            """)
            by_status = [dict(r) for r in cur.fetchall()]

            cur.execute("""
                SELECT property_type, COUNT(*) as count
                FROM properties
                GROUP BY property_type
                ORDER BY count DESC
                LIMIT 15
            """)
            by_type = [dict(r) for r in cur.fetchall()]

        return {
            "total_properties": total,
            "by_province": by_province,
            "by_status": by_status,
            "by_type": by_type,
        }
    finally:
        conn.close()


def format_price(satang):
    """Format satang to readable baht string."""
    if satang is None:
        return "N/A"
    baht = satang / 100
    if baht >= 1_000_000:
        return f"{baht / 1_000_000:.2f}M"
    if baht >= 1_000:
        return f"{baht / 1_000:.1f}K"
    return f"{baht:.0f}"


def print_results(result, verbose=False):
    """Pretty-print query results."""
    if "total_properties" in result:
        # Summary
        print(f"Total properties: {result['total_properties']}")
        print("\nBy Province:")
        for r in result["by_province"]:
            print(f"  {r['province']}: {r['count']}")
        print("\nBy Status:")
        for r in result["by_status"]:
            print(f"  {r['sale_status']}: {r['count']}")
        print("\nBy Type (top 15):")
        for r in result["by_type"]:
            print(f"  {r['property_type']}: {r['count']}")
        return

    if "stats" in result:
        # Price stats
        print(f"Price Statistics ({len(result['stats'])} groups):\n")
        for s in result["stats"]:
            print(f"  {s['province']} > {s['ampur']} | {s['property_type']} ({s['count']} props)")
            print(f"    Min: {s['min_price_baht']:,.0f} | Median: {s['median_price_baht']:,.0f} | "
                  f"Avg: {s['avg_price_baht']:,.0f} | Max: {s['max_price_baht']:,.0f}")
        return

    # Property list
    total = result.get("total", len(result.get("properties", [])))
    props = result.get("properties", [])
    print(f"Found {total} properties (showing {len(props)}):\n")

    for p in props:
        price = format_price(p.get("primary_price_satang"))
        size_parts = []
        ptype = p.get("property_type", "")
        is_condo = "ห้องชุด" in ptype or "คอนโด" in ptype

        if p.get("size_rai"):
            size_parts.append(f"{p['size_rai']:.0f}rai")
        if p.get("size_ngan"):
            size_parts.append(f"{p['size_ngan']:.0f}ngan")
        if p.get("size_wa"):
            # IMPORTANT: For ห้องชุด/condo, size_wa column stores ตร.ม. (sq.m), NOT ตร.วา
            unit = "sqm" if is_condo else "wa"
            size_parts.append(f"{p['size_wa']:.1f}{unit}")
        size = " ".join(size_parts) or "N/A"

        print(f"  [{p.get('asset_id')}] {p.get('property_type', '?')}")
        print(f"    Price: {price} | Size: {size} | Status: {p.get('sale_status')}")
        print(f"    Location: {p.get('province')} > {p.get('ampur')} > {p.get('tumbol')}")
        if p.get("address"):
            print(f"    Address: {p['address'][:100]}")
        if p.get("next_auction_date"):
            print(f"    Next Auction: {p['next_auction_date']} ({p.get('total_auction_count', 0)} total)")
        if p.get("deed_type"):
            print(f"    Deed: {p['deed_type']}")
        if verbose and p.get("case_number"):
            print(f"    Case: {p['case_number']} | Court: {p.get('court')}")
            print(f"    Contact: {p.get('contact_phone')}")
        print()


def main():
    parser = argparse.ArgumentParser(description="Query LED NPA properties from PostgreSQL")
    sub = parser.add_subparsers(dest="command", required=True)

    # search
    s = sub.add_parser("search", help="Search properties")
    s.add_argument("--province", help="Province name (partial match)")
    s.add_argument("--district", help="District/Ampur (partial match)")
    s.add_argument("--sub-district", help="Sub-district/Tumbol (partial match)")
    s.add_argument("--min-price", type=float, help="Min price in baht")
    s.add_argument("--max-price", type=float, help="Max price in baht")
    s.add_argument("--type", dest="property_type", help="Property type (partial match)")
    s.add_argument("--status", help="Sale status (partial match)")
    s.add_argument("--keyword", help="Keyword search in address/remark")
    s.add_argument("--limit", type=int, default=20)
    s.add_argument("--offset", type=int, default=0)
    s.add_argument("--sort", default="price", choices=["price", "province", "auction_date", "created"])
    s.add_argument("--desc", action="store_true")
    s.add_argument("--json", action="store_true", help="Output as JSON")
    s.add_argument("-v", "--verbose", action="store_true")

    # upcoming
    u = sub.add_parser("upcoming", help="Upcoming auctions")
    u.add_argument("--days", type=int, default=30, help="Days ahead (default: 30)")
    u.add_argument("--province", help="Filter by province")
    u.add_argument("--limit", type=int, default=20)
    u.add_argument("--json", action="store_true")
    u.add_argument("-v", "--verbose", action="store_true")

    # stats
    st = sub.add_parser("stats", help="Price statistics by area")
    st.add_argument("--province", help="Filter by province")
    st.add_argument("--district", help="Filter by district")
    st.add_argument("--type", dest="property_type", help="Filter by property type")
    st.add_argument("--json", action="store_true")

    # summary
    sub.add_parser("summary", help="Database summary")

    args = parser.parse_args()

    if args.command == "search":
        result = search_properties(
            province=args.province, district=args.district,
            sub_district=args.sub_district,
            min_price=args.min_price, max_price=args.max_price,
            property_type=args.property_type, sale_status=args.status,
            keyword=args.keyword,
            limit=args.limit, offset=args.offset,
            sort_by=args.sort,
            sort_order="DESC" if args.desc else "ASC",
        )
    elif args.command == "upcoming":
        result = upcoming_auctions(
            days=args.days, province=args.province, limit=args.limit,
        )
    elif args.command == "stats":
        result = price_stats(
            province=args.province, district=args.district,
            property_type=args.property_type,
        )
    elif args.command == "summary":
        result = summary()

    if getattr(args, "json", False):
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
    else:
        print_results(result, verbose=getattr(args, "verbose", False))


if __name__ == "__main__":
    main()

"""
BAM Property Query CLI

Search BAM NPA properties in the local PostgreSQL database.

Usage:
    python query.py search --province กรุงเทพมหานคร
    python query.py search --district ธนบุรี --price-max 3000000
    python query.py search --asset-type ห้องชุดพักอาศัย --grade A
    python query.py search --province กรุงเทพมหานคร --sort price_asc
    python query.py stats
    python query.py detail 154304
"""

import argparse
import json

from sqlalchemy import create_engine, func, select, text
from sqlalchemy.orm import Session

from models import BamPriceHistory, BamProperty

DB_URI = "postgresql://arsapolm@localhost:5432/npa_kb"


def get_session() -> Session:
    engine = create_engine(DB_URI, echo=False)
    return Session(engine)


def search(args: argparse.Namespace) -> None:
    session = get_session()
    stmt = select(BamProperty)

    if args.province:
        stmt = stmt.where(BamProperty.province == args.province)
    if args.district:
        stmt = stmt.where(BamProperty.district == args.district)
    if args.asset_type:
        stmt = stmt.where(BamProperty.asset_type == args.asset_type)
    if args.grade:
        stmt = stmt.where(BamProperty.grade == args.grade)
    if args.price_min:
        stmt = stmt.where(BamProperty.sell_price >= args.price_min)
    if args.price_max:
        stmt = stmt.where(BamProperty.sell_price <= args.price_max)
    if args.has_detail:
        stmt = stmt.where(BamProperty.has_detail.is_(True))

    sort_map = {
        "price_asc": BamProperty.sell_price.asc(),
        "price_desc": BamProperty.sell_price.desc(),
        "newest": BamProperty.first_seen_at.desc(),
        "grade": BamProperty.grade.asc(),
        "evaluate": BamProperty.evaluate_amt.desc(),
    }
    stmt = stmt.order_by(sort_map.get(args.sort, BamProperty.sell_price.asc()))
    stmt = stmt.limit(args.limit)

    results = session.execute(stmt).scalars().all()
    print(f"Found {len(results)} properties:\n")

    for p in results:
        discount_pct = ""
        if p.evaluate_amt and p.sell_price and float(p.evaluate_amt) > 0:
            pct = (1 - float(p.sell_price) / float(p.evaluate_amt)) * 100
            discount_pct = f" ({pct:+.0f}% vs appraised)"

        print(f"  ID: {p.id} | {p.asset_no}")
        print(f"  Type: {p.asset_type} | Grade: {p.grade or '-'}")
        print(f"  Location: {p.sub_district}, {p.district}, {p.province}")
        print(f"  Project: {p.project_th or '-'}")
        print(f"  Price: ฿{float(p.sell_price or 0):,.0f}{discount_pct}")
        if p.evaluate_amt:
            print(f"  Appraised: ฿{float(p.evaluate_amt):,.0f}")
        if p.area_meter and float(p.area_meter) > 0:
            print(f"  Area: {float(p.area_meter):.2f} sqm")
        elif p.wa and float(p.wa) > 0:
            land = f"{float(p.rai or 0):.0f}-{float(p.ngan or 0):.0f}-{float(p.wa):.1f} ไร่-งาน-วา"
            print(f"  Land: {land}")
        if p.bedroom or p.bathroom:
            print(f"  Rooms: {p.bedroom or 0}BR / {p.bathroom or 0}BA")
        print()

    session.close()


def detail(args: argparse.Namespace) -> None:
    session = get_session()
    prop = session.get(BamProperty, args.asset_id)
    if not prop:
        print(f"Asset {args.asset_id} not found in database.")
        session.close()
        return

    print(f"=== BAM Asset {prop.id} ({prop.asset_no}) ===\n")
    print(f"State: {prop.asset_state}")
    print(f"Type: {prop.asset_type} ({prop.col_sub_typedesc or '-'})")
    print(f"Grade: {prop.grade or '-'}")
    print(f"Location: {prop.property_location}")
    print(f"Area: {prop.sub_district}, {prop.district}, {prop.province}")
    print(f"Physical Zone: {prop.physical_zone or '-'}")
    if prop.lat and prop.lon:
        print(f"GPS: {prop.lat}, {prop.lon}")
    print(f"\nProject: {prop.project_th or '-'}")
    print(f"License: {prop.license_number or '-'}")

    print(f"\n--- Pricing ---")
    print(f"Sell Price: ฿{float(prop.sell_price or 0):,.0f}")
    if prop.evaluate_amt:
        print(f"Appraised: ฿{float(prop.evaluate_amt):,.0f} (date: {prop.evaluate_date})")
    if prop.cost_asset_amt:
        print(f"BAM Cost: ���{float(prop.cost_asset_amt):,.0f}")
    if prop.sale_price_spc and float(prop.sale_price_spc) > 0:
        print(f"Special Price: ฿{float(prop.sale_price_spc):,.0f} ({prop.sale_price_spc_from} to {prop.sale_price_spc_to})")
    if prop.discount_price and float(prop.discount_price) > 0:
        print(f"Discount: ฿{float(prop.discount_price):,.0f}")

    print(f"\n--- Size ---")
    if prop.area_meter and float(prop.area_meter) > 0:
        print(f"Area: {float(prop.area_meter):.2f} sqm")
    if prop.usable_area and float(prop.usable_area) > 0:
        print(f"Usable: {float(prop.usable_area):.2f} sqm")
    if prop.wa and float(prop.wa) > 0:
        print(f"Land: {float(prop.rai or 0):.0f}-{float(prop.ngan or 0):.0f}-{float(prop.wa):.1f} ไร่-งาน-วา")
    if prop.size_build:
        print(f"Build: {prop.size_build}")
    rooms = []
    if prop.bedroom:
        rooms.append(f"{prop.bedroom}BR")
    if prop.bathroom:
        rooms.append(f"{prop.bathroom}BA")
    if prop.studio:
        rooms.append("Studio")
    if rooms:
        print(f"Rooms: {', '.join(rooms)}")

    if prop.property_detail:
        print(f"\n--- Description ---")
        print(prop.property_detail[:500])

    # Price history
    stmt = (
        select(BamPriceHistory)
        .where(BamPriceHistory.asset_id == prop.id)
        .order_by(BamPriceHistory.scraped_at.desc())
        .limit(10)
    )
    history = session.execute(stmt).scalars().all()
    if history:
        print(f"\n--- Price History ({len(history)} records) ---")
        for h in history:
            print(f"  {h.scraped_at}: {h.change_type} sell=฿{float(h.sell_price or 0):,.0f}")

    print(f"\n--- Admin ---")
    print(f"Department: {prop.department_name}")
    print(f"Contact: {prop.admin_name} ({prop.work_phone} ext {prop.work_phone_nxt})")
    print(f"Scraped: {prop.last_scraped_at} (detail: {prop.has_detail})")

    session.close()


def stats(args: argparse.Namespace) -> None:
    session = get_session()

    total = session.scalar(select(func.count(BamProperty.id)))
    with_detail = session.scalar(
        select(func.count(BamProperty.id)).where(BamProperty.has_detail.is_(True))
    )

    print(f"=== BAM Database Stats ===\n")
    print(f"Total properties: {total:,}")
    print(f"With detail: {with_detail:,}")

    # By province (top 10)
    stmt = (
        select(BamProperty.province, func.count(BamProperty.id).label("cnt"))
        .group_by(BamProperty.province)
        .order_by(text("cnt DESC"))
        .limit(10)
    )
    print(f"\nTop provinces:")
    for row in session.execute(stmt):
        print(f"  {row.province}: {row.cnt:,}")

    # By asset type
    stmt = (
        select(BamProperty.asset_type, func.count(BamProperty.id).label("cnt"))
        .group_by(BamProperty.asset_type)
        .order_by(text("cnt DESC"))
        .limit(10)
    )
    print(f"\nTop asset types:")
    for row in session.execute(stmt):
        print(f"  {row.asset_type}: {row.cnt:,}")

    # By grade
    stmt = (
        select(BamProperty.grade, func.count(BamProperty.id).label("cnt"))
        .group_by(BamProperty.grade)
        .order_by(BamProperty.grade)
    )
    print(f"\nBy grade:")
    for row in session.execute(stmt):
        print(f"  {row.grade or 'N/A'}: {row.cnt:,}")

    # Price stats
    avg_price = session.scalar(select(func.avg(BamProperty.sell_price)))
    min_price = session.scalar(select(func.min(BamProperty.sell_price)))
    max_price = session.scalar(select(func.max(BamProperty.sell_price)))
    print(f"\nPrice range: ฿{float(min_price or 0):,.0f} - ฿{float(max_price or 0):,.0f}")
    print(f"Average: ฿{float(avg_price or 0):,.0f}")

    session.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="BAM Property Query")
    sub = parser.add_subparsers(dest="command")

    # search
    sp = sub.add_parser("search", help="Search properties")
    sp.add_argument("--province", type=str)
    sp.add_argument("--district", type=str)
    sp.add_argument("--asset-type", type=str)
    sp.add_argument("--grade", type=str)
    sp.add_argument("--price-min", type=float)
    sp.add_argument("--price-max", type=float)
    sp.add_argument("--has-detail", action="store_true")
    sp.add_argument("--sort", type=str, default="price_asc",
                    choices=["price_asc", "price_desc", "newest", "grade", "evaluate"])
    sp.add_argument("--limit", type=int, default=20)

    # detail
    dp = sub.add_parser("detail", help="Show property detail")
    dp.add_argument("asset_id", type=int)

    # stats
    sub.add_parser("stats", help="Database statistics")

    args = parser.parse_args()
    if args.command == "search":
        search(args)
    elif args.command == "detail":
        detail(args)
    elif args.command == "stats":
        stats(args)
    else:
        parser.print_help()

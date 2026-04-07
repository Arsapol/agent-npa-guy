"""
BAY Property Query CLI

Search BAY/Krungsri NPA properties in the local PostgreSQL database.

Usage:
    python query.py search --province กรุงเทพมหานคร
    python query.py search --district ปากเกร็ด --price-max 3000000
    python query.py search --condo --sort price_asc
    python query.py stats
    python query.py detail AX1185
"""

import argparse

from sqlalchemy import create_engine, func, select, text
from sqlalchemy.orm import Session

from models import BayPriceHistory, BayPropertyDB

DB_URI = "postgresql://arsapolm@localhost:5432/npa_kb"


def get_session() -> Session:
    engine = create_engine(DB_URI, echo=False)
    return Session(engine)


def search(args: argparse.Namespace) -> None:
    session = get_session()
    stmt = select(BayPropertyDB)

    if args.province:
        stmt = stmt.where(BayPropertyDB.province == args.province)
    if args.district:
        stmt = stmt.where(BayPropertyDB.district == args.district)
    if args.property_type:
        stmt = stmt.where(BayPropertyDB.property_type_name == args.property_type)
    if args.category:
        stmt = stmt.where(BayPropertyDB.category_code == args.category)
    if args.condo:
        stmt = stmt.where(BayPropertyDB.is_condo.is_(True))
    if args.price_min:
        stmt = stmt.where(BayPropertyDB.sale_price >= args.price_min)
    if args.price_max:
        stmt = stmt.where(BayPropertyDB.sale_price <= args.price_max)

    sort_map = {
        "price_asc": BayPropertyDB.sale_price.asc(),
        "price_desc": BayPropertyDB.sale_price.desc(),
        "newest": BayPropertyDB.first_seen_at.desc(),
        "discount": BayPropertyDB.discount_pct.desc(),
    }
    stmt = stmt.order_by(sort_map.get(args.sort, BayPropertyDB.sale_price.asc()))
    stmt = stmt.limit(args.limit)

    results = session.execute(stmt).scalars().all()
    print(f"Found {len(results)} properties:\n")

    for p in results:
        discount_str = ""
        if p.discount_pct and float(p.discount_pct) > 0:
            discount_str = f" (-{float(p.discount_pct):.0f}%)"

        print(f"  Code: {p.code}")
        print(f"  Type: {p.property_type_name} | Category: {p.category_code}")
        print(f"  Condo: {p.is_condo}")
        print(f"  Location: {p.subdistrict}, {p.district}, {p.province}")
        print(f"  Project: {p.project or '-'}")
        print(f"  Sale: ฿{float(p.sale_price or 0):,.0f}")
        if p.promo_price and float(p.promo_price) > 0:
            print(f"  Promo: ฿{float(p.promo_price):,.0f}{discount_str}")
        if p.size_sq_meter and float(p.size_sq_meter) > 0:
            print(f"  Area: {float(p.size_sq_meter):.2f} sqm")
        elif p.size_text:
            print(f"  Land: {p.size_text}")
        if p.bed_count or p.bath_count:
            print(f"  Rooms: {p.bed_count or 0}BR / {p.bath_count or 0}BA / {p.park_count or 0}P")
        if p.deed_no:
            print(f"  Deed: {p.deed_no}")
        print()

    session.close()


def detail(args: argparse.Namespace) -> None:
    session = get_session()
    prop = session.get(BayPropertyDB, args.code)
    if not prop:
        print(f"Property {args.code} not found in database.")
        session.close()
        return

    print(f"=== BAY Property {prop.code} ===\n")
    print(f"Type: {prop.property_type_name} (category {prop.category_code})")
    print(f"Condo: {prop.is_condo}")
    print(f"Project: {prop.project or '-'} ({prop.project_en or '-'})")
    print(f"Location: {prop.subdistrict}, {prop.district}, {prop.province}")
    if prop.lat and prop.lon:
        print(f"GPS: {prop.lat}, {prop.lon}")

    print(f"\n--- Pricing ---")
    print(f"Sale Price: ฿{float(prop.sale_price or 0):,.0f}")
    if prop.promo_price and float(prop.promo_price) > 0:
        print(f"Promo Price: ฿{float(prop.promo_price):,.0f}")
    if prop.final_price and float(prop.final_price) > 0:
        print(f"Final Price: ฿{float(prop.final_price):,.0f}")
    if prop.discount_pct and float(prop.discount_pct) > 0:
        print(f"Discount: {float(prop.discount_pct):.1f}%")

    print(f"\n--- Size ---")
    if prop.size_sq_meter and float(prop.size_sq_meter) > 0:
        print(f"Area: {float(prop.size_sq_meter):.2f} sqm")
    if prop.size_text:
        print(f"Land: {prop.size_text}")
    rooms = []
    if prop.bed_count:
        rooms.append(f"{prop.bed_count}BR")
    if prop.bath_count:
        rooms.append(f"{prop.bath_count}BA")
    if prop.park_count:
        rooms.append(f"{prop.park_count}P")
    if rooms:
        print(f"Rooms: {', '.join(rooms)}")

    print(f"\n--- Title ---")
    print(f"Deed: {prop.deed_no or '-'}")
    print(f"Owner: {prop.owner or '-'}")

    print(f"\n--- Facilities ---")
    facilities = []
    if prop.flag_fitness:
        facilities.append("Fitness")
    if prop.flag_swim:
        facilities.append("Pool")
    if prop.flag_security:
        facilities.append("Security")
    if prop.flag_shop:
        facilities.append("Shop")
    if prop.flag_lift:
        facilities.append("Elevator")
    print(f"Facilities: {', '.join(facilities) if facilities else '-'}")

    if prop.detail:
        print(f"\n--- Description ---")
        print(prop.detail[:500])

    # Price history
    stmt = (
        select(BayPriceHistory)
        .where(BayPriceHistory.property_code == prop.code)
        .order_by(BayPriceHistory.scraped_at.desc())
        .limit(10)
    )
    history = session.execute(stmt).scalars().all()
    if history:
        print(f"\n--- Price History ({len(history)} records) ---")
        for h in history:
            print(
                f"  {h.scraped_at}: {h.change_type} "
                f"sale=฿{float(h.sale_price or 0):,.0f} "
                f"promo=฿{float(h.promo_price or 0):,.0f}"
            )

    print(f"\n--- Contact ---")
    print(f"Name: {prop.sale_name or '-'}")
    print(f"Phone: {prop.sale_contact or '-'}")
    print(f"Scraped: {prop.last_scraped_at}")

    session.close()


def stats(args: argparse.Namespace) -> None:
    session = get_session()

    total = session.scalar(select(func.count(BayPropertyDB.code)))
    condos = session.scalar(
        select(func.count(BayPropertyDB.code)).where(BayPropertyDB.is_condo.is_(True))
    )

    print(f"=== BAY Database Stats ===\n")
    print(f"Total properties: {total:,}")
    print(f"Condos: {condos:,}")

    # By province (top 10)
    stmt = (
        select(BayPropertyDB.province, func.count(BayPropertyDB.code).label("cnt"))
        .group_by(BayPropertyDB.province)
        .order_by(text("cnt DESC"))
        .limit(10)
    )
    print(f"\nTop provinces:")
    for row in session.execute(stmt):
        print(f"  {row.province}: {row.cnt:,}")

    # By category
    stmt = (
        select(BayPropertyDB.category_code, func.count(BayPropertyDB.code).label("cnt"))
        .group_by(BayPropertyDB.category_code)
        .order_by(text("cnt DESC"))
    )
    print(f"\nBy category:")
    for row in session.execute(stmt):
        print(f"  {row.category_code or 'N/A'}: {row.cnt:,}")

    # By property type
    stmt = (
        select(BayPropertyDB.property_type_name, func.count(BayPropertyDB.code).label("cnt"))
        .group_by(BayPropertyDB.property_type_name)
        .order_by(text("cnt DESC"))
        .limit(10)
    )
    print(f"\nTop property types:")
    for row in session.execute(stmt):
        print(f"  {row.property_type_name}: {row.cnt:,}")

    # Price stats
    avg_price = session.scalar(select(func.avg(BayPropertyDB.sale_price)))
    min_price = session.scalar(select(func.min(BayPropertyDB.sale_price)))
    max_price = session.scalar(select(func.max(BayPropertyDB.sale_price)))
    print(f"\nPrice range: ฿{float(min_price or 0):,.0f} - ฿{float(max_price or 0):,.0f}")
    print(f"Average: ฿{float(avg_price or 0):,.0f}")

    session.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="BAY Property Query")
    sub = parser.add_subparsers(dest="command")

    # search
    sp = sub.add_parser("search", help="Search properties")
    sp.add_argument("--province", type=str)
    sp.add_argument("--district", type=str)
    sp.add_argument("--property-type", type=str)
    sp.add_argument("--category", type=str,
                    choices=["A", "B", "C", "D", "E", "F"])
    sp.add_argument("--condo", action="store_true")
    sp.add_argument("--price-min", type=float)
    sp.add_argument("--price-max", type=float)
    sp.add_argument("--sort", type=str, default="price_asc",
                    choices=["price_asc", "price_desc", "newest", "discount"])
    sp.add_argument("--limit", type=int, default=20)

    # detail
    dp = sub.add_parser("detail", help="Show property detail")
    dp.add_argument("code", type=str)

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

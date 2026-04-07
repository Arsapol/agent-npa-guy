"""
LH Bank Property Query CLI

Search LH Bank NPA properties in the local PostgreSQL database.

Usage:
    python query.py search --asset-type "คอนโด (ห้องชุด)"
    python query.py search --price-max 3000000
    python query.py search --sort price_asc
    python query.py stats
    python query.py detail LH031A
"""

import argparse

from sqlalchemy import create_engine, func, select, text
from sqlalchemy.orm import Session

from models import LHPriceHistory, LHProperty

DB_URI = "postgresql://arsapolm@localhost:5432/npa_kb"


def get_session() -> Session:
    engine = create_engine(DB_URI, echo=False)
    return Session(engine)


def search(args: argparse.Namespace) -> None:
    session = get_session()
    stmt = select(LHProperty)

    if args.asset_type:
        stmt = stmt.where(LHProperty.asset_type.ilike(f"%{args.asset_type}%"))
    if args.price_min:
        stmt = stmt.where(LHProperty.sale_price >= args.price_min)
    if args.price_max:
        stmt = stmt.where(LHProperty.sale_price <= args.price_max)
    if args.has_gps:
        stmt = stmt.where(LHProperty.lat.isnot(None))

    sort_map = {
        "price_asc": LHProperty.sale_price.asc(),
        "price_desc": LHProperty.sale_price.desc(),
        "newest": LHProperty.first_seen_at.desc(),
    }
    stmt = stmt.order_by(sort_map.get(args.sort, LHProperty.sale_price.asc()))
    stmt = stmt.limit(args.limit)

    results = session.execute(stmt).scalars().all()
    print(f"Found {len(results)} properties:\n")

    for p in results:
        print(f"  ID: {p.property_id}")
        print(f"  Type: {p.asset_type}")
        print(f"  Price: ฿{float(p.sale_price or 0):,.0f}")
        print(f"  Area: {p.area_text or '-'}")
        print(f"  Address: {p.address or p.location_text or '-'}")
        if p.lat and p.lon:
            print(f"  GPS: {p.lat}, {p.lon}")
        print()

    session.close()


def detail(args: argparse.Namespace) -> None:
    session = get_session()
    prop = session.get(LHProperty, args.property_id)
    if not prop:
        print(f"Property {args.property_id} not found in database.")
        session.close()
        return

    print(f"=== LH Bank Asset {prop.property_id} ===\n")
    print(f"Type: {prop.asset_type}")
    print(f"Case: {prop.case_info or '-'}")
    print(f"Price: ฿{float(prop.sale_price or 0):,.0f}")
    print(f"Area: {prop.area_text} ({float(prop.area_sqm or 0):.2f} sqm)")
    print(f"Address: {prop.address}")
    if prop.lat and prop.lon:
        print(f"GPS: {prop.lat}, {prop.lon}")
    if prop.description:
        print(f"\n--- Description ---")
        print(prop.description[:500])
    print(f"\nPost date: {prop.post_date or '-'}")

    # Price history
    stmt = (
        select(LHPriceHistory)
        .where(LHPriceHistory.property_id == prop.property_id)
        .order_by(LHPriceHistory.scraped_at.desc())
        .limit(10)
    )
    history = session.execute(stmt).scalars().all()
    if history:
        print(f"\n--- Price History ({len(history)} records) ---")
        for h in history:
            print(f"  {h.scraped_at}: {h.change_type} ฿{float(h.sale_price or 0):,.0f}")

    print(f"\nImages: {len(prop.images) if prop.images else 0}")
    print(f"Scraped: {prop.last_scraped_at} (detail: {prop.has_detail})")

    session.close()


def stats(args: argparse.Namespace) -> None:
    session = get_session()

    total = session.scalar(select(func.count(LHProperty.property_id)))
    with_detail = session.scalar(
        select(func.count(LHProperty.property_id)).where(LHProperty.has_detail.is_(True))
    )
    with_gps = session.scalar(
        select(func.count(LHProperty.property_id)).where(LHProperty.lat.isnot(None))
    )

    print(f"=== LH Bank Database Stats ===\n")
    print(f"Total properties: {total}")
    print(f"With detail: {with_detail}")
    print(f"With GPS: {with_gps}")

    # By asset type
    stmt = (
        select(LHProperty.asset_type, func.count(LHProperty.property_id).label("cnt"))
        .group_by(LHProperty.asset_type)
        .order_by(text("cnt DESC"))
    )
    print(f"\nBy asset type:")
    for row in session.execute(stmt):
        print(f"  {row.asset_type or '(empty)'}: {row.cnt}")

    # Price stats
    avg_price = session.scalar(select(func.avg(LHProperty.sale_price)))
    min_price = session.scalar(select(func.min(LHProperty.sale_price)))
    max_price = session.scalar(select(func.max(LHProperty.sale_price)))
    if min_price is not None:
        print(f"\nPrice range: ฿{float(min_price):,.0f} - ฿{float(max_price or 0):,.0f}")
        print(f"Average: ฿{float(avg_price or 0):,.0f}")

    session.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LH Bank Property Query")
    sub = parser.add_subparsers(dest="command")

    sp = sub.add_parser("search", help="Search properties")
    sp.add_argument("--asset-type", type=str)
    sp.add_argument("--price-min", type=float)
    sp.add_argument("--price-max", type=float)
    sp.add_argument("--has-gps", action="store_true")
    sp.add_argument("--sort", type=str, default="price_asc",
                    choices=["price_asc", "price_desc", "newest"])
    sp.add_argument("--limit", type=int, default=20)

    dp = sub.add_parser("detail", help="Show property detail")
    dp.add_argument("property_id", type=str)

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

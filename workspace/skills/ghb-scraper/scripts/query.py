"""
GHB Property Query CLI

Search GHB NPA properties in the local PostgreSQL database.

Usage:
    python query.py search --province กรุงเทพมหานคร
    python query.py search --type-id 3 --price-max 3000000
    python query.py search --district ธนบุรี
    python query.py stats
    python query.py detail 987980
"""

import argparse
import json

from sqlalchemy import create_engine, func, select, text
from sqlalchemy.orm import Session

from models import GhbPriceHistory, GhbProperty

DB_URI = "postgresql://arsapolm@localhost:5432/npa_kb"


def get_session() -> Session:
    engine = create_engine(DB_URI, echo=False)
    return Session(engine)


def search(args: argparse.Namespace) -> None:
    session = get_session()
    stmt = select(GhbProperty)

    if args.province:
        stmt = stmt.where(GhbProperty.province == args.province)
    if args.district:
        stmt = stmt.where(GhbProperty.district == args.district)
    if args.type_id:
        stmt = stmt.where(GhbProperty.type_id == args.type_id)
    if args.property_type:
        stmt = stmt.where(GhbProperty.property_type == args.property_type)
    if args.price_min:
        stmt = stmt.where(GhbProperty.price_amt >= args.price_min)
    if args.price_max:
        stmt = stmt.where(GhbProperty.price_amt <= args.price_max)
    if args.has_detail:
        stmt = stmt.where(GhbProperty.has_detail.is_(True))
    if args.promotion:
        stmt = stmt.where(GhbProperty.promotion_id == args.promotion)

    sort_map = {
        "price_asc": GhbProperty.price_amt.asc(),
        "price_desc": GhbProperty.price_amt.desc(),
        "newest": GhbProperty.first_seen_at.desc(),
        "modified": GhbProperty.ghb_modified_date.desc(),
    }
    stmt = stmt.order_by(sort_map.get(args.sort, GhbProperty.price_amt.asc()))
    stmt = stmt.limit(args.limit)

    results = session.execute(stmt).scalars().all()
    print(f"Found {len(results)} properties:\n")

    for p in results:
        type_label = p.property_type or f"type_id={p.type_id}"
        print(f"  ID: {p.property_id} | No: {p.property_no or '-'}")
        print(f"  Type: {type_label}")
        print(f"  Location: {p.sub_district or '-'}, {p.district or '-'}, {p.province or '-'}")
        print(f"  Project: {p.village_name or '-'}")
        print(f"  Price: ฿{int(p.price_amt or 0):,}")
        if p.promotion_price_amt and int(p.promotion_price_amt) != int(p.price_amt or 0):
            print(f"  Promo Price: ฿{int(p.promotion_price_amt):,}")
        if p.area_txt:
            print(f"  Area: {p.area_txt}")
        if p.bedrooms or p.bathrooms:
            print(f"  Rooms: {p.bedrooms or 0}BR / {p.bathrooms or 0}BA")
        if p.promotion_name:
            print(f"  Promotion: {p.promotion_name}")
        print()

    session.close()


def detail(args: argparse.Namespace) -> None:
    session = get_session()
    prop = session.get(GhbProperty, args.property_id)
    if not prop:
        print(f"Property {args.property_id} not found in database.")
        session.close()
        return

    print(f"=== GHB Property {prop.property_id} ({prop.property_no}) ===\n")
    print(f"Type: {prop.property_type} (type_id={prop.type_id})")
    print(f"Name: {prop.property_name or '-'}")
    print(f"Project: {prop.village_name or '-'}")
    print(f"Location: {prop.sub_district}, {prop.district}, {prop.province}")
    if prop.lat and prop.lon:
        print(f"GPS: {prop.lat}, {prop.lon}")
    print(f"Address: {prop.house_no or '-'} ซ.{prop.soi or '-'} ถ.{prop.road or '-'}")
    print(f"Deed No: {prop.deed_no or '-'}")

    print(f"\n--- Pricing ---")
    print(f"Price: ฿{int(prop.price_amt or 0):,}")
    if prop.promotion_price_amt:
        print(f"Promotion Price: ฿{int(prop.promotion_price_amt):,}")
    if prop.begin_auction_price:
        print(f"Auction Start: ฿{int(prop.begin_auction_price):,}")
    if prop.sale_price and int(prop.sale_price) > 0:
        print(f"Sale Price: ฿{int(prop.sale_price):,}")

    print(f"\n--- Size ---")
    if prop.area_txt:
        print(f"Area: {prop.area_txt}")
    if prop.usage_area_txt and prop.usage_area_txt != "-":
        print(f"Usable: {prop.usage_area_txt}")
    if prop.floor_info:
        print(f"Floor: {prop.floor_info}")
    elif prop.floor or prop.floors:
        print(f"Floor: {prop.floor or '-'} / {prop.floors or '-'} floors")
    rooms = []
    if prop.bedrooms:
        rooms.append(f"{prop.bedrooms}BR")
    if prop.bathrooms:
        rooms.append(f"{prop.bathrooms}BA")
    if prop.parking_lot:
        rooms.append(f"{prop.parking_lot}P")
    if rooms:
        print(f"Rooms: {', '.join(rooms)}")

    if prop.description:
        print(f"\n--- Description ---")
        print(prop.description[:500])

    # Price history
    stmt = (
        select(GhbPriceHistory)
        .where(GhbPriceHistory.property_id == prop.property_id)
        .order_by(GhbPriceHistory.scraped_at.desc())
        .limit(10)
    )
    history = session.execute(stmt).scalars().all()
    if history:
        print(f"\n--- Price History ({len(history)} records) ---")
        for h in history:
            print(f"  {h.scraped_at}: {h.change_type} price=฿{int(h.price_amt or 0):,}")

    print(f"\n--- Status ---")
    print(f"Active: {prop.property_active_flag} | Status: {prop.property_status}")
    if prop.promotion_name:
        print(f"Promotion: {prop.promotion_name} (id={prop.promotion_id})")
    print(f"Contact: {prop.contact_person or '-'}")
    print(f"Tel: {prop.contact_tel_no or '-'}")
    print(f"GHB Created: {prop.ghb_created_date}")
    print(f"GHB Modified: {prop.ghb_modified_date}")
    print(f"Scraped: {prop.last_scraped_at} (detail: {prop.has_detail})")

    session.close()


def stats(args: argparse.Namespace) -> None:
    session = get_session()

    total = session.scalar(select(func.count(GhbProperty.property_id)))
    with_detail = session.scalar(
        select(func.count(GhbProperty.property_id)).where(GhbProperty.has_detail.is_(True))
    )

    print(f"=== GHB Database Stats ===\n")
    print(f"Total properties: {total:,}")
    print(f"With detail: {with_detail:,}")

    # By province (top 10)
    stmt = (
        select(GhbProperty.province, func.count(GhbProperty.property_id).label("cnt"))
        .where(GhbProperty.province.isnot(None))
        .group_by(GhbProperty.province)
        .order_by(text("cnt DESC"))
        .limit(10)
    )
    print(f"\nTop provinces:")
    for row in session.execute(stmt):
        print(f"  {row.province}: {row.cnt:,}")

    # By property type
    stmt = (
        select(GhbProperty.property_type, func.count(GhbProperty.property_id).label("cnt"))
        .where(GhbProperty.property_type.isnot(None))
        .group_by(GhbProperty.property_type)
        .order_by(text("cnt DESC"))
    )
    print(f"\nBy property type:")
    for row in session.execute(stmt):
        print(f"  {row.property_type}: {row.cnt:,}")

    # By promotion
    stmt = (
        select(GhbProperty.promotion_name, func.count(GhbProperty.property_id).label("cnt"))
        .where(GhbProperty.promotion_name.isnot(None))
        .group_by(GhbProperty.promotion_name)
        .order_by(text("cnt DESC"))
        .limit(10)
    )
    print(f"\nBy promotion:")
    for row in session.execute(stmt):
        print(f"  {row.promotion_name}: {row.cnt:,}")

    # Price stats
    avg_price = session.scalar(select(func.avg(GhbProperty.price_amt)))
    min_price = session.scalar(
        select(func.min(GhbProperty.price_amt)).where(GhbProperty.price_amt > 0)
    )
    max_price = session.scalar(select(func.max(GhbProperty.price_amt)))
    print(f"\nPrice range: ฿{int(min_price or 0):,} - ฿{int(max_price or 0):,}")
    print(f"Average: ฿{int(avg_price or 0):,}")

    session.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GHB Property Query")
    sub = parser.add_subparsers(dest="command")

    # search
    sp = sub.add_parser("search", help="Search properties")
    sp.add_argument("--province", type=str)
    sp.add_argument("--district", type=str)
    sp.add_argument("--type-id", type=int)
    sp.add_argument("--property-type", type=str)
    sp.add_argument("--price-min", type=float)
    sp.add_argument("--price-max", type=float)
    sp.add_argument("--has-detail", action="store_true")
    sp.add_argument("--promotion", type=int, help="Promotion ID")
    sp.add_argument("--sort", type=str, default="price_asc",
                    choices=["price_asc", "price_desc", "newest", "modified"])
    sp.add_argument("--limit", type=int, default=20)

    # detail
    dp = sub.add_parser("detail", help="Show property detail")
    dp.add_argument("property_id", type=int)

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

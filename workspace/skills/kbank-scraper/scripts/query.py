"""
KBank NPA Scraper — CLI for querying local database.

Usage:
    python query.py stats                                    # overview
    python query.py search --province กรุงเทพ                 # by province
    python query.py search --type 05 --max-price 3000000     # condos under 3M
    python query.py search --province กรุงเทพ --has-promo     # promos only
    python query.py detail 028818655                          # single property
    python query.py price-history 028818655                   # price changes
"""

import argparse
import json

from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from database import get_engine
from models import KbankPriceHistory, KbankProperty


def cmd_stats(engine):
    """Print overview statistics."""
    with Session(engine) as session:
        total = session.scalar(select(func.count()).select_from(KbankProperty))
        enriched = session.scalar(
            select(func.count()).select_from(KbankProperty).where(KbankProperty.has_detail == True)
        )
        sold = session.scalar(
            select(func.count()).select_from(KbankProperty).where(KbankProperty.is_sold_out == True)
        )
        reserved = session.scalar(
            select(func.count()).select_from(KbankProperty).where(KbankProperty.is_reserve == True)
        )
        with_promo = session.scalar(
            select(func.count()).select_from(KbankProperty).where(KbankProperty.promotion_price.isnot(None))
        )

        print(f"Total properties:  {total:,}")
        print(f"With detail:       {enriched:,}")
        print(f"With promotion:    {with_promo:,}")
        print(f"Sold out:          {sold:,}")
        print(f"Reserved:          {reserved:,}")

        # By province (top 10)
        print(f"\nTop 10 provinces:")
        stmt = (
            select(KbankProperty.province_name, func.count().label("cnt"))
            .group_by(KbankProperty.province_name)
            .order_by(text("cnt DESC"))
            .limit(10)
        )
        for row in session.execute(stmt):
            print(f"  {row.province_name}: {row.cnt:,}")

        # By property type
        print(f"\nBy property type:")
        stmt = (
            select(KbankProperty.property_type_name, func.count().label("cnt"))
            .group_by(KbankProperty.property_type_name)
            .order_by(text("cnt DESC"))
        )
        for row in session.execute(stmt):
            print(f"  {row.property_type_name}: {row.cnt:,}")

        # Price changes
        changes = session.scalar(select(func.count()).select_from(KbankPriceHistory))
        price_changes = session.scalar(
            select(func.count()).select_from(KbankPriceHistory)
            .where(KbankPriceHistory.change_type == "price_change")
        )
        print(f"\nPrice history records: {changes:,}")
        print(f"Price changes:         {price_changes:,}")


def cmd_search(engine, province=None, prop_type=None, min_price=None, max_price=None, has_promo=False, limit=20):
    """Search properties with filters."""
    with Session(engine) as session:
        stmt = select(KbankProperty).where(KbankProperty.is_sold_out != True)

        if province:
            stmt = stmt.where(KbankProperty.province_name.contains(province))
        if prop_type:
            stmt = stmt.where(KbankProperty.property_type_code == prop_type)
        if min_price:
            stmt = stmt.where(KbankProperty.sell_price >= min_price)
        if max_price:
            stmt = stmt.where(KbankProperty.sell_price <= max_price)
        if has_promo:
            stmt = stmt.where(KbankProperty.promotion_price.isnot(None))

        stmt = stmt.order_by(KbankProperty.sell_price.asc()).limit(limit)
        results = session.execute(stmt).scalars().all()

        print(f"Found {len(results)} properties:\n")
        for p in results:
            promo = f" → promo {p.promotion_price:,.0f}" if p.promotion_price else ""
            area_info = f"{p.area_value or 0:.1f} sqw" if p.area_value else ""
            rooms = f"{p.bedroom or 0}BR/{p.bathroom or 0}BA" if p.bedroom else ""
            detail = " [enriched]" if p.has_detail else ""

            print(f"  {p.property_id} | {p.property_type_name}")
            print(f"    {p.sell_price:>12,.0f} baht{promo}")
            print(f"    {p.province_name} > {p.amphur_name} > {p.tambon_name}")
            if p.village_th and p.village_th != "-":
                print(f"    Village: {p.village_th}")
            print(f"    {area_info}  {rooms}  age={p.building_age or '?'}y{detail}")
            print()


def cmd_detail(engine, property_id: str):
    """Show detailed info for a single property."""
    with Session(engine) as session:
        prop = session.get(KbankProperty, property_id)
        if not prop:
            print(f"Property {property_id} not found.")
            return

        print(f"Property: {prop.property_id} ({prop.property_id_format})")
        print(f"Type:     {prop.property_type_name}")
        print(f"Price:    {prop.sell_price:,.0f} baht" if prop.sell_price else "Price: N/A")
        if prop.promotion_price:
            print(f"Promo:    {prop.promotion_price:,.0f} baht ({prop.promotion_name})")
        print(f"Location: {prop.province_name} > {prop.amphur_name} > {prop.tambon_name}")
        if prop.full_address:
            print(f"Address:  {prop.full_address}")
        if prop.village_th and prop.village_th != "-":
            print(f"Village:  {prop.village_th}")
        print(f"Area:     {prop.area} ({prop.area_value} sqw)")
        print(f"Useable:  {prop.useable_area} sqm")
        print(f"Rooms:    {prop.bedroom or 0}BR / {prop.bathroom or 0}BA")
        print(f"Age:      {prop.building_age} years")
        if prop.lat and prop.lon:
            print(f"GPS:      {prop.lat}, {prop.lon}")
        if prop.deed_number:
            print(f"Deed:     {prop.deed_type} #{prop.deed_number}")
        print(f"Status:   sold={prop.is_sold_out} reserve={prop.is_reserve}")
        print(f"Flags:    new={prop.is_new} hot={prop.is_hot} AI={prop.ai_flag}")
        print(f"Scraped:  {prop.last_scraped_at}")

        if prop.nearby_places:
            print(f"\nNearby places:")
            for place in prop.nearby_places:
                print(f"  - {place['name']}: {place['distance']}")


def cmd_price_history(engine, property_id: str):
    """Show price history for a property."""
    with Session(engine) as session:
        stmt = (
            select(KbankPriceHistory)
            .where(KbankPriceHistory.property_id == property_id)
            .order_by(KbankPriceHistory.scraped_at.asc())
        )
        rows = session.execute(stmt).scalars().all()

        if not rows:
            print(f"No price history for {property_id}")
            return

        print(f"Price history for {property_id}:\n")
        for r in rows:
            promo = f" promo={r.promotion_price:,.0f}" if r.promotion_price else ""
            print(f"  {r.scraped_at:%Y-%m-%d %H:%M}  [{r.change_type:>14}]  sell={r.sell_price:>12,.0f}{promo}")


def main():
    parser = argparse.ArgumentParser(description="KBank NPA Query CLI")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("stats")

    search_p = sub.add_parser("search")
    search_p.add_argument("--province", help="Province name (partial match)")
    search_p.add_argument("--type", dest="prop_type", help="Type code (e.g. 05)")
    search_p.add_argument("--min-price", type=int)
    search_p.add_argument("--max-price", type=int)
    search_p.add_argument("--has-promo", action="store_true")
    search_p.add_argument("--limit", type=int, default=20)

    detail_p = sub.add_parser("detail")
    detail_p.add_argument("property_id")

    history_p = sub.add_parser("price-history")
    history_p.add_argument("property_id")

    args = parser.parse_args()
    engine = get_engine()

    if args.command == "stats":
        cmd_stats(engine)
    elif args.command == "search":
        cmd_search(
            engine,
            province=args.province,
            prop_type=args.prop_type,
            min_price=args.min_price,
            max_price=args.max_price,
            has_promo=args.has_promo,
            limit=args.limit,
        )
    elif args.command == "detail":
        cmd_detail(engine, args.property_id)
    elif args.command == "price-history":
        cmd_price_history(engine, args.property_id)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

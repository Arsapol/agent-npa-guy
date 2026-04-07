"""
TTB/PAMCO NPA — Query tool for local property database.

Usage:
    python query.py search --province "กรุงเทพ"
    python query.py search --province "กรุงเทพ" --category 4
    python query.py search --source pamco
    python query.py search --min-price 1000000 --max-price 5000000
    python query.py stats
    python query.py get <id_market>
"""

import argparse
import json
import sys
from decimal import Decimal

from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from database import get_engine
from models import TtbPriceHistory, TtbProperty


def _conv(obj):
    """JSON serializer for Decimal."""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


SOURCE_MAP = {3: "PAMCO", 4: "TTB"}


def search(args):
    engine = get_engine()
    with Session(engine) as session:
        stmt = select(TtbProperty)

        if args.province:
            stmt = stmt.where(TtbProperty.province_name.ilike(f"%{args.province}%"))
        if args.district:
            stmt = stmt.where(TtbProperty.district_name.ilike(f"%{args.district}%"))
        if args.category:
            stmt = stmt.where(TtbProperty.id_category == args.category)
        if args.source:
            source_type = 3 if args.source.lower() == "pamco" else 4
            stmt = stmt.where(TtbProperty.source_type == source_type)
        if args.min_price:
            stmt = stmt.where(TtbProperty.price >= args.min_price)
        if args.max_price:
            stmt = stmt.where(TtbProperty.price <= args.max_price)
        if args.keyword:
            stmt = stmt.where(TtbProperty.title.ilike(f"%{args.keyword}%"))

        stmt = stmt.order_by(TtbProperty.price.asc().nulls_last())
        stmt = stmt.limit(args.limit or 20)

        rows = session.execute(stmt).scalars().all()
        print(f"Found {len(rows)} properties:\n")

        for r in rows:
            source = SOURCE_MAP.get(r.source_type, "?")
            price_str = f"{float(r.price) / 1e6:.2f}M" if r.price else "N/A"
            sp_str = f" (SP: {float(r.special_price) / 1e6:.2f}M)" if r.special_price else ""
            area_str = f"{float(r.useable_area)} sqm" if r.useable_area else f"{r.area_sqw} sqw"
            print(
                f"  [{r.id_market}] ({source}) {r.title}\n"
                f"    Price: {price_str}{sp_str} | Area: {area_str}\n"
                f"    Location: {r.province_name} > {r.district_name} > {r.sub_district_name}\n"
                f"    GPS: {r.lat}, {r.lon} | Floor: {r.floor}\n"
                f"    Contact: {r.tel_ao}\n"
            )


def get_property(args):
    engine = get_engine()
    with Session(engine) as session:
        stmt = select(TtbProperty).where(
            TtbProperty.id_market.ilike(f"%{args.id_market}%")
        )
        prop = session.execute(stmt).scalars().first()
        if not prop:
            print(f"Not found: {args.id_market}")
            return

        data = {
            "id_property": prop.id_property,
            "id_market": prop.id_market,
            "slug": prop.slug,
            "source": SOURCE_MAP.get(prop.source_type, "?"),
            "title": prop.title,
            "detail_name": prop.detail_name,
            "price": float(prop.price) if prop.price else None,
            "special_price": float(prop.special_price) if prop.special_price else None,
            "province": prop.province_name,
            "district": prop.district_name,
            "sub_district": prop.sub_district_name,
            "lat": prop.lat,
            "lon": prop.lon,
            "area_sqw": float(prop.area_sqw) if prop.area_sqw else None,
            "useable_area": float(prop.useable_area) if prop.useable_area else None,
            "floor": prop.floor,
            "land_id": prop.land_id,
            "house_id": prop.house_id,
            "tel_ao": prop.tel_ao,
            "nearby": prop.nearby,
        }
        print(json.dumps(data, indent=2, ensure_ascii=False, default=_conv))

        # Price history
        hist_stmt = (
            select(TtbPriceHistory)
            .where(TtbPriceHistory.property_id == prop.id_property)
            .order_by(TtbPriceHistory.scraped_at.desc())
            .limit(10)
        )
        history = session.execute(hist_stmt).scalars().all()
        if history:
            print(f"\nPrice history ({len(history)} records):")
            for h in history:
                price_str = f"{float(h.price) / 1e6:.2f}M" if h.price else "N/A"
                sp_str = f" SP:{float(h.special_price) / 1e6:.2f}M" if h.special_price else ""
                print(f"  [{h.change_type}] {h.scraped_at:%Y-%m-%d %H:%M} — {price_str}{sp_str}")


def stats(args):
    engine = get_engine()
    with Session(engine) as session:
        total = session.execute(select(func.count(TtbProperty.id_property))).scalar()
        pamco = session.execute(
            select(func.count(TtbProperty.id_property))
            .where(TtbProperty.source_type == 3)
        ).scalar()
        ttb = session.execute(
            select(func.count(TtbProperty.id_property))
            .where(TtbProperty.source_type == 4)
        ).scalar()

        print(f"Total properties: {total}")
        print(f"  PAMCO (type=3): {pamco}")
        print(f"  TTB   (type=4): {ttb}")

        # By category
        cat_stmt = (
            select(TtbProperty.detail_name, func.count(TtbProperty.id_property))
            .group_by(TtbProperty.detail_name)
            .order_by(func.count(TtbProperty.id_property).desc())
        )
        print("\nBy category:")
        for name, cnt in session.execute(cat_stmt).all():
            print(f"  {name or 'N/A'}: {cnt}")

        # By province (top 10)
        prov_stmt = (
            select(TtbProperty.province_name, func.count(TtbProperty.id_property))
            .group_by(TtbProperty.province_name)
            .order_by(func.count(TtbProperty.id_property).desc())
            .limit(10)
        )
        print("\nTop provinces:")
        for name, cnt in session.execute(prov_stmt).all():
            print(f"  {name or 'N/A'}: {cnt}")

        # Price stats
        price_stmt = select(
            func.min(TtbProperty.price),
            func.avg(TtbProperty.price),
            func.max(TtbProperty.price),
        ).where(TtbProperty.price.is_not(None))
        row = session.execute(price_stmt).first()
        if row and row[0]:
            print(f"\nPrice range: {float(row[0])/1e6:.2f}M - {float(row[2])/1e6:.2f}M (avg {float(row[1])/1e6:.2f}M)")

        # Price history count
        ph_count = session.execute(select(func.count(TtbPriceHistory.id))).scalar()
        print(f"Price history records: {ph_count}")


def export_json(args):
    engine = get_engine()
    with Session(engine) as session:
        stmt = select(TtbProperty)
        if args.province:
            stmt = stmt.where(TtbProperty.province_name.ilike(f"%{args.province}%"))
        if args.category:
            stmt = stmt.where(TtbProperty.id_category == args.category)

        rows = session.execute(stmt).scalars().all()
        result = []
        for r in rows:
            result.append({
                "id_property": r.id_property,
                "id_market": r.id_market,
                "source": SOURCE_MAP.get(r.source_type, "?"),
                "title": r.title,
                "detail_name": r.detail_name,
                "price": float(r.price) if r.price else None,
                "special_price": float(r.special_price) if r.special_price else None,
                "province": r.province_name,
                "district": r.district_name,
                "sub_district": r.sub_district_name,
                "lat": r.lat,
                "lon": r.lon,
                "useable_area": float(r.useable_area) if r.useable_area else None,
            })
        print(json.dumps(result, indent=2, ensure_ascii=False, default=_conv))


def main():
    parser = argparse.ArgumentParser(description="TTB/PAMCO NPA query tool")
    sub = parser.add_subparsers(dest="command")

    # search
    sp = sub.add_parser("search", help="Search properties")
    sp.add_argument("--province", type=str)
    sp.add_argument("--district", type=str)
    sp.add_argument("--category", type=int, help="1=house, 2=townhouse, 3=commercial, 4=condo, 5=land")
    sp.add_argument("--source", type=str, help="pamco or ttb")
    sp.add_argument("--min-price", type=float)
    sp.add_argument("--max-price", type=float)
    sp.add_argument("--keyword", type=str)
    sp.add_argument("--limit", type=int, default=20)

    # get
    gp = sub.add_parser("get", help="Get property by id_market")
    gp.add_argument("id_market", type=str)

    # stats
    sub.add_parser("stats", help="Show database statistics")

    # export
    ep = sub.add_parser("export", help="Export to JSON")
    ep.add_argument("--province", type=str)
    ep.add_argument("--category", type=int)

    args = parser.parse_args()

    if args.command == "search":
        search(args)
    elif args.command == "get":
        get_property(args)
    elif args.command == "stats":
        stats(args)
    elif args.command == "export":
        export_json(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

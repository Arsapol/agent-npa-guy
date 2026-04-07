"""GSB NPA Property Query CLI — Search local PostgreSQL database."""

from __future__ import annotations

import argparse
import os

from sqlalchemy import create_engine, func, select, text
from sqlalchemy.orm import Session

from models import Base, GsbPriceHistory, GsbProperty, GsbScrapeLog

DB_URI = os.environ.get("POSTGRES_URI", "postgresql://arsapolm@localhost:5432/npa_kb")


def get_session() -> Session:
    engine = create_engine(DB_URI, echo=False, pool_pre_ping=True)
    return Session(engine)


def cmd_stats(session: Session) -> None:
    total = session.scalar(select(func.count(GsbProperty.npa_id)))
    with_detail = session.scalar(
        select(func.count(GsbProperty.npa_id)).where(GsbProperty.has_detail.is_(True))
    )
    print(f"Total properties: {total:,}")
    print(f"With detail: {with_detail:,}")

    print("\nBy province (top 15):")
    stmt = (
        select(GsbProperty.province_name, func.count().label("cnt"))
        .group_by(GsbProperty.province_name)
        .order_by(text("cnt DESC"))
        .limit(15)
    )
    for row in session.execute(stmt):
        print(f"  {row.province_name}: {row.cnt:,}")

    print("\nBy asset type:")
    stmt = (
        select(GsbProperty.asset_type_desc, func.count().label("cnt"))
        .where(GsbProperty.asset_type_desc.isnot(None))
        .group_by(GsbProperty.asset_type_desc)
        .order_by(text("cnt DESC"))
    )
    for row in session.execute(stmt):
        print(f"  {row.asset_type_desc}: {row.cnt:,}")

    print("\nBy subtype (top 10):")
    stmt = (
        select(GsbProperty.asset_subtype_desc, func.count().label("cnt"))
        .where(GsbProperty.asset_subtype_desc.isnot(None))
        .group_by(GsbProperty.asset_subtype_desc)
        .order_by(text("cnt DESC"))
        .limit(10)
    )
    for row in session.execute(stmt):
        print(f"  {row.asset_subtype_desc}: {row.cnt:,}")

    print("\nBy price type (xtype):")
    stmt = (
        select(GsbProperty.xtype, func.count().label("cnt"))
        .group_by(GsbProperty.xtype)
        .order_by(text("cnt DESC"))
    )
    for row in session.execute(stmt):
        print(f"  {row.xtype or 'NULL'}: {row.cnt:,}")

    print("\nRecent scrape logs:")
    logs = session.execute(
        select(GsbScrapeLog).order_by(GsbScrapeLog.id.desc()).limit(5)
    ).scalars().all()
    for log in logs:
        duration = ""
        if log.finished_at and log.started_at:
            secs = (log.finished_at - log.started_at).total_seconds()
            duration = f" ({secs:.0f}s)"
        print(
            f"  {log.started_at:%Y-%m-%d %H:%M}{duration}: "
            f"search={log.total_search}, detail={log.total_detail}, "
            f"new={log.new_count}, updated={log.updated_count}, "
            f"price_changed={log.price_changed_count}"
        )


def cmd_search(
    session: Session,
    province: str | None = None,
    district: str | None = None,
    asset_type: int | None = None,
    name: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    limit: int = 20,
) -> None:
    stmt = select(GsbProperty)

    if province:
        stmt = stmt.where(GsbProperty.province_name.ilike(f"%{province}%"))
    if district:
        stmt = stmt.where(GsbProperty.district_name.ilike(f"%{district}%"))
    if asset_type:
        stmt = stmt.where(GsbProperty.asset_type_id == asset_type)
    if name:
        stmt = stmt.where(
            GsbProperty.asset_name.ilike(f"%{name}%")
            | GsbProperty.village_head.ilike(f"%{name}%")
            | GsbProperty.npa_id.ilike(f"%{name}%")
        )
    if min_price is not None:
        stmt = stmt.where(GsbProperty.current_offer_price >= min_price)
    if max_price is not None:
        stmt = stmt.where(GsbProperty.current_offer_price <= max_price)

    stmt = stmt.order_by(GsbProperty.current_offer_price.asc()).limit(limit)
    rows = session.execute(stmt).scalars().all()

    if not rows:
        print("No results found.")
        return

    print(f"Found {len(rows)} properties:\n")
    for r in rows:
        price_str = f"{int(r.current_offer_price):,}" if r.current_offer_price else "N/A"
        normal_str = f"{int(r.xprice_normal):,}" if r.xprice_normal else "N/A"
        discount = ""
        if r.current_offer_price and r.xprice_normal and int(r.xprice_normal) > 0:
            pct = (1 - int(r.current_offer_price) / int(r.xprice_normal)) * 100
            if pct > 0:
                discount = f" (-{pct:.0f}%)"
        area_str = f"{float(r.square_meter):.1f} sqm" if r.square_meter else r.rai_ngan_wa or "N/A"
        print(f"  [{r.npa_id}] {r.asset_type_desc or '?'} — {r.asset_subtype_desc or ''}")
        print(f"    {r.province_name} > {r.district_name} > {r.sub_district_name}")
        if r.asset_name:
            print(f"    Project: {r.asset_name}")
        if r.village_head:
            print(f"    Village: {r.village_head}")
        print(f"    Price: {price_str} / Normal: {normal_str}{discount}")
        print(f"    Area: {area_str}")
        if r.builded_year:
            print(f"    Built: {r.builded_year} (พ.ศ.)")
        print(f"    Type: {r.xtype} | Recommend: {r.is_recommend} | Deed: {r.deed_info}")
        if r.lat and r.lon:
            print(f"    GPS: {r.lat}, {r.lon}")
        print()


def cmd_price_history(session: Session, npa_id: str) -> None:
    prop = session.get(GsbProperty, npa_id)
    if not prop:
        print(f"Property {npa_id} not found.")
        return

    price_str = f"{int(prop.current_offer_price):,}" if prop.current_offer_price else "N/A"
    print(f"Property: {prop.asset_type_desc} — {prop.province_name} {prop.district_name}")
    print(f"Current price: {price_str}")
    print()

    history = session.execute(
        select(GsbPriceHistory)
        .where(GsbPriceHistory.npa_id == npa_id)
        .order_by(GsbPriceHistory.scraped_at.desc())
    ).scalars().all()

    if not history:
        print("No price history records.")
        return

    print("Price history:")
    for h in history:
        offer = f"{int(h.current_offer_price):,}" if h.current_offer_price else "N/A"
        normal = f"{int(h.xprice_normal):,}" if h.xprice_normal else "N/A"
        print(
            f"  {h.scraped_at:%Y-%m-%d %H:%M} | {h.change_type:15s} | "
            f"offer={offer} normal={normal} type={h.xtype}"
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GSB NPA Property Query")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("stats", help="Show database statistics")

    sp = sub.add_parser("search", help="Search properties")
    sp.add_argument("--province", type=str, help="Province name (partial match)")
    sp.add_argument("--district", type=str, help="District name (partial match)")
    sp.add_argument("--type", type=int, dest="asset_type", help="Asset type ID (341/342/343)")
    sp.add_argument("--name", type=str, help="Project/village name or NPA ID (partial match)")
    sp.add_argument("--min-price", type=float, help="Minimum price (baht)")
    sp.add_argument("--max-price", type=float, help="Maximum price (baht)")
    sp.add_argument("--limit", type=int, default=20, help="Max results")

    hp = sub.add_parser("history", help="Show price history for a property")
    hp.add_argument("npa_id", type=str, help="Property NPA ID (e.g. BKK620093)")

    args = parser.parse_args()

    with get_session() as session:
        if args.command == "stats":
            cmd_stats(session)
        elif args.command == "search":
            cmd_search(
                session,
                province=args.province,
                district=args.district,
                asset_type=args.asset_type,
                name=args.name,
                min_price=args.min_price,
                max_price=args.max_price,
                limit=args.limit,
            )
        elif args.command == "history":
            cmd_price_history(session, args.npa_id)
        else:
            parser.print_help()

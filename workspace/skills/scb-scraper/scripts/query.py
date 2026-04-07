"""SCB NPA Property Query CLI — Search local PostgreSQL database."""

from __future__ import annotations

import argparse
import os

from sqlalchemy import create_engine, func, select, text
from sqlalchemy.orm import Session

from models import ScbPriceHistory, ScbProperty, ScbScrapeLog

DB_URI = os.environ.get("POSTGRES_URI", "postgresql://arsapolm@localhost:5432/npa_kb")


def get_session() -> Session:
    engine = create_engine(DB_URI, echo=False, pool_pre_ping=True)
    return Session(engine)


def cmd_stats(session: Session) -> None:
    total = session.scalar(select(func.count(ScbProperty.project_id)))
    with_detail = session.scalar(
        select(func.count(ScbProperty.project_id)).where(ScbProperty.has_detail.is_(True))
    )
    print(f"Total properties: {total:,}")
    print(f"With detail: {with_detail:,}")

    print("\nBy type (top 15):")
    stmt = (
        select(ScbProperty.project_type_name, func.count().label("cnt"))
        .where(ScbProperty.project_type_name.isnot(None))
        .group_by(ScbProperty.project_type_name)
        .order_by(text("cnt DESC"))
        .limit(15)
    )
    for row in session.execute(stmt):
        print(f"  {row.project_type_name}: {row.cnt:,}")

    print("\nBy province_id (top 15):")
    stmt = (
        select(ScbProperty.province_id, func.count().label("cnt"))
        .where(ScbProperty.province_id.isnot(None))
        .group_by(ScbProperty.province_id)
        .order_by(text("cnt DESC"))
        .limit(15)
    )
    for row in session.execute(stmt):
        print(f"  province_id={row.province_id}: {row.cnt:,}")

    print("\nSold out status:")
    stmt = (
        select(ScbProperty.project_sold_out, func.count().label("cnt"))
        .group_by(ScbProperty.project_sold_out)
        .order_by(text("cnt DESC"))
    )
    for row in session.execute(stmt):
        print(f"  {row.project_sold_out or 'NULL'}: {row.cnt:,}")

    print("\nRecent scrape logs:")
    logs = session.execute(
        select(ScbScrapeLog).order_by(ScbScrapeLog.id.desc()).limit(5)
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
    province_id: int | None = None,
    prop_type: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    keyword: str | None = None,
    limit: int = 20,
) -> None:
    stmt = select(ScbProperty)

    if province_id is not None:
        stmt = stmt.where(ScbProperty.province_id == province_id)
    if prop_type:
        stmt = stmt.where(ScbProperty.project_type.ilike(f"%{prop_type}%"))
    if min_price is not None:
        stmt = stmt.where(ScbProperty.price >= min_price)
    if max_price is not None:
        stmt = stmt.where(ScbProperty.price <= max_price)
    if keyword:
        stmt = stmt.where(
            ScbProperty.project_title.ilike(f"%{keyword}%")
            | ScbProperty.project_address.ilike(f"%{keyword}%")
            | ScbProperty.project_address_detail.ilike(f"%{keyword}%")
        )

    stmt = stmt.order_by(ScbProperty.price.asc().nulls_last()).limit(limit)
    rows = session.execute(stmt).scalars().all()

    if not rows:
        print("No results found.")
        return

    print(f"Found {len(rows)} properties:\n")
    for r in rows:
        price_str = f"{r.price:,.0f}" if r.price else "N/A"
        discount_str = ""
        if r.price_discount:
            discount_str = f" (discount: {r.price_discount:,.0f})"
        print(f"  [{r.project_id}] {r.project_title or '?'}")
        print(f"    Type: {r.project_type_name or r.project_type}")
        print(f"    Price: {price_str}{discount_str}")
        if r.area_use:
            print(f"    Area: {r.area_use} sqm")
        if r.project_address_detail:
            print(f"    Address: {r.project_address_detail}")
        if r.bedrooms or r.bathrooms:
            print(f"    Beds: {r.bedrooms} | Baths: {r.bathrooms} | Parking: {r.parking}")
        if r.title_deed:
            print(f"    Title deed: {r.title_deed}")
        sold = "Yes" if r.project_sold_out == "T" else "No"
        print(f"    Sold: {sold} | GPS: ({r.lat}, {r.lon})")
        print(f"    URL: {BASE_URL}/project/{r.slug}")
        print()


BASE_URL = "https://asset.home.scb"


def cmd_price_history(session: Session, project_id: int) -> None:
    prop = session.get(ScbProperty, project_id)
    if not prop:
        print(f"Property {project_id} not found.")
        return

    print(f"Property: {prop.project_title}")
    print(f"Type: {prop.project_type_name}")
    print(f"Current price: {prop.price:,.0f}" if prop.price else "Current price: N/A")
    print()

    history = session.execute(
        select(ScbPriceHistory)
        .where(ScbPriceHistory.project_id == project_id)
        .order_by(ScbPriceHistory.scraped_at.desc())
    ).scalars().all()

    if not history:
        print("No price history records.")
        return

    print("Price history:")
    for h in history:
        price_str = f"{h.price:,.0f}" if h.price else "N/A"
        discount_str = f" (disc: {h.price_discount:,.0f})" if h.price_discount else ""
        print(f"  {h.scraped_at:%Y-%m-%d %H:%M} | {h.change_type:15s} | {price_str}{discount_str}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SCB NPA Property Query")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("stats", help="Show database statistics")

    sp = sub.add_parser("search", help="Search properties")
    sp.add_argument("--province-id", type=int, help="Province ID (SCB custom, 1=Bangkok)")
    sp.add_argument("--type", type=str, dest="prop_type", help="Property type (partial match)")
    sp.add_argument("--min-price", type=float, help="Minimum price (baht)")
    sp.add_argument("--max-price", type=float, help="Maximum price (baht)")
    sp.add_argument("--keyword", type=str, help="Search title/address")
    sp.add_argument("--limit", type=int, default=20, help="Max results")

    hp = sub.add_parser("history", help="Show price history for a property")
    hp.add_argument("project_id", type=int, help="Property project_id")

    args = parser.parse_args()

    with get_session() as session:
        if args.command == "stats":
            cmd_stats(session)
        elif args.command == "search":
            cmd_search(
                session,
                province_id=args.province_id,
                prop_type=args.prop_type,
                min_price=args.min_price,
                max_price=args.max_price,
                keyword=args.keyword,
                limit=args.limit,
            )
        elif args.command == "history":
            cmd_price_history(session, args.project_id)
        else:
            parser.print_help()

"""KTB NPA Property Query CLI — Search local PostgreSQL database."""

from __future__ import annotations

import argparse
import os

from sqlalchemy import create_engine, func, select, text
from sqlalchemy.orm import Session

from models import Base, KtbPriceHistory, KtbProperty, KtbScrapeLog

DB_URI = os.environ.get("POSTGRES_URI", "postgresql://arsapolm@localhost:5432/npa_kb")


def get_session() -> Session:
    engine = create_engine(DB_URI, echo=False, pool_pre_ping=True)
    return Session(engine)


def cmd_stats(session: Session) -> None:
    total = session.scalar(select(func.count(KtbProperty.coll_grp_id)))
    with_detail = session.scalar(
        select(func.count(KtbProperty.coll_grp_id)).where(KtbProperty.has_detail.is_(True))
    )
    print(f"Total properties: {total:,}")
    print(f"With detail: {with_detail:,}")

    print("\nBy province (top 15):")
    stmt = (
        select(KtbProperty.province, func.count().label("cnt"))
        .group_by(KtbProperty.province)
        .order_by(text("cnt DESC"))
        .limit(15)
    )
    for row in session.execute(stmt):
        print(f"  {row.province}: {row.cnt:,}")

    print("\nBy property type:")
    stmt = (
        select(KtbProperty.coll_cate_name, func.count().label("cnt"))
        .where(KtbProperty.coll_cate_name.isnot(None))
        .group_by(KtbProperty.coll_cate_name)
        .order_by(text("cnt DESC"))
    )
    for row in session.execute(stmt):
        print(f"  {row.coll_cate_name}: {row.cnt:,}")

    print("\nBy sale category:")
    stmt = (
        select(KtbProperty.cate_name, func.count().label("cnt"))
        .group_by(KtbProperty.cate_name)
        .order_by(text("cnt DESC"))
    )
    for row in session.execute(stmt):
        print(f"  {row.cate_name}: {row.cnt:,}")

    print("\nRecent scrape logs:")
    logs = session.execute(
        select(KtbScrapeLog).order_by(KtbScrapeLog.id.desc()).limit(5)
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
    amphur: str | None = None,
    prop_type: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    limit: int = 20,
) -> None:
    stmt = select(KtbProperty)

    if province:
        stmt = stmt.where(KtbProperty.province.ilike(f"%{province}%"))
    if amphur:
        stmt = stmt.where(KtbProperty.amphur.ilike(f"%{amphur}%"))
    if prop_type:
        stmt = stmt.where(KtbProperty.coll_cate_name.ilike(f"%{prop_type}%"))
    if min_price is not None:
        stmt = stmt.where(KtbProperty.price >= min_price)
    if max_price is not None:
        stmt = stmt.where(KtbProperty.price <= max_price)

    stmt = stmt.order_by(KtbProperty.price.asc()).limit(limit)
    rows = session.execute(stmt).scalars().all()

    if not rows:
        print("No results found.")
        return

    print(f"Found {len(rows)} properties:\n")
    for r in rows:
        price_str = f"{r.price:,.0f}" if r.price else "N/A"
        nml_str = f"{r.nml_price:,.0f}" if r.nml_price else "N/A"
        discount = ""
        if r.price and r.nml_price and r.nml_price > 0:
            pct = (1 - r.price / float(r.nml_price)) * 100
            if pct > 0:
                discount = f" (-{pct:.0f}%)"
        print(f"  [{r.coll_grp_id}] {r.coll_cate_name or '?'}")
        print(f"    {r.province} > {r.amphur} > {r.tambon}")
        print(f"    Price: {price_str} / Normal: {nml_str}{discount}")
        print(f"    Area: {r.area} ({r.sum_area_num} sqm)")
        if r.lodge:
            print(f"    Lodge: {r.lodge}")
        print(f"    {r.cate_name} | Speedy: {r.is_speedy} | Promo: {r.is_promotion}")
        print(f"    URL: {r.share_url}")
        print()


def cmd_price_history(session: Session, coll_grp_id: int) -> None:
    prop = session.get(KtbProperty, coll_grp_id)
    if not prop:
        print(f"Property {coll_grp_id} not found.")
        return

    print(f"Property: {prop.coll_cate_name} — {prop.province} {prop.amphur}")
    print(f"Current price: {prop.price:,.0f}" if prop.price else "Current price: N/A")
    print()

    history = session.execute(
        select(KtbPriceHistory)
        .where(KtbPriceHistory.coll_grp_id == coll_grp_id)
        .order_by(KtbPriceHistory.scraped_at.desc())
    ).scalars().all()

    if not history:
        print("No price history records.")
        return

    print("Price history:")
    for h in history:
        price_str = f"{h.price:,.0f}" if h.price else "N/A"
        print(f"  {h.scraped_at:%Y-%m-%d %H:%M} | {h.change_type:15s} | {price_str}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="KTB NPA Property Query")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("stats", help="Show database statistics")

    sp = sub.add_parser("search", help="Search properties")
    sp.add_argument("--province", type=str, help="Province name (partial match)")
    sp.add_argument("--amphur", type=str, help="District name (partial match)")
    sp.add_argument("--type", type=str, dest="prop_type", help="Property type (partial match)")
    sp.add_argument("--min-price", type=float, help="Minimum price (baht)")
    sp.add_argument("--max-price", type=float, help="Maximum price (baht)")
    sp.add_argument("--limit", type=int, default=20, help="Max results")

    hp = sub.add_parser("history", help="Show price history for a property")
    hp.add_argument("coll_grp_id", type=int, help="Property collGrpId")

    args = parser.parse_args()

    with get_session() as session:
        if args.command == "stats":
            cmd_stats(session)
        elif args.command == "search":
            cmd_search(
                session,
                province=args.province,
                amphur=args.amphur,
                prop_type=args.prop_type,
                min_price=args.min_price,
                max_price=args.max_price,
                limit=args.limit,
            )
        elif args.command == "history":
            cmd_price_history(session, args.coll_grp_id)
        else:
            parser.print_help()

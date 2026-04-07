"""JAM Scraper — Database operations with upsert + price history tracking."""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from models import (
    Base,
    JamPriceHistory,
    JamProperty,
    JamPropertyParsed,
    JamScrapeLog,
)

DB_URI = os.environ.get("POSTGRES_URI", "postgresql://arsapolm@localhost:5432/npa_kb")


def get_engine():
    return create_engine(DB_URI, echo=False, pool_pre_ping=True)


def create_tables():
    engine = get_engine()
    Base.metadata.create_all(engine)
    print("Tables created/verified.")
    return engine


def _parse_dt(val: str | None) -> datetime | None:
    if not val:
        return None
    try:
        return datetime.fromisoformat(val.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None


def _load_latest_price_history(
    session: Session, asset_ids: list[int]
) -> dict[int, JamPriceHistory]:
    if not asset_ids:
        return {}
    subq = (
        select(JamPriceHistory.asset_id, func.max(JamPriceHistory.scraped_at).label("max_ts"))
        .where(JamPriceHistory.asset_id.in_(asset_ids))
        .group_by(JamPriceHistory.asset_id)
        .subquery()
    )
    stmt = select(JamPriceHistory).join(
        subq,
        (JamPriceHistory.asset_id == subq.c.asset_id)
        & (JamPriceHistory.scraped_at == subq.c.max_ts),
    )
    return {row.asset_id: row for row in session.execute(stmt).scalars()}


def upsert_properties(
    session: Session,
    properties: list[JamPropertyParsed],
) -> dict[str, int]:
    """
    Upsert properties into jam_properties.
    Detects: new inserts, price changes, sold transitions.
    Returns counts: {new, updated, price_changed, sold, unsold}
    """
    now = datetime.now(timezone.utc)
    counts = {"new": 0, "updated": 0, "price_changed": 0, "sold": 0, "unsold": 0}

    # Load existing properties in bulk
    asset_ids = [p.asset_id for p in properties]
    existing_map: dict[int, JamProperty] = {}
    if asset_ids:
        stmt = select(JamProperty).where(JamProperty.asset_id.in_(asset_ids))
        for row in session.execute(stmt).scalars():
            existing_map[row.asset_id] = row

    latest_history = _load_latest_price_history(session, asset_ids)

    for parsed in properties:
        existing = existing_map.get(parsed.asset_id)
        prev_hist = latest_history.get(parsed.asset_id)

        if existing is None:
            # New property
            prop = JamProperty(
                asset_id=parsed.asset_id,
                borr_code=parsed.borr_code,
                asset_no=parsed.asset_no,
                type_sale_code=parsed.type_sale_code,
                type_sale_th=parsed.type_sale_th,
                type_asset_code=parsed.type_asset_code,
                type_asset_th=parsed.type_asset_th,
                project_th=parsed.project_th,
                project_en=parsed.project_en,
                province=parsed.province,
                district=parsed.district,
                subdistrict=parsed.subdistrict,
                province_name=parsed.province_name,
                amphur_name=parsed.amphur_name,
                district_name=parsed.district_name,
                lat=parsed.lat,
                lon=parsed.lon,
                soi=parsed.soi,
                road=parsed.road,
                wah=parsed.wah,
                meter=parsed.meter,
                bedroom=parsed.bedroom,
                bathroom=parsed.bathroom,
                floor=parsed.floor,
                selling=parsed.selling,
                discount=parsed.discount,
                rental=parsed.rental,
                status_soldout=parsed.status_soldout,
                soldout_date=_parse_dt(parsed.soldout_date),
                status_acution=parsed.status_acution,
                status_hotdeal=parsed.status_hotdeal,
                is_flash_sale=parsed.is_flash_sale,
                company_code=parsed.company_code,
                company_th=parsed.company_th,
                user_code=parsed.user_code,
                images_main_web=parsed.images_main_web,
                image_sold_out=parsed.image_sold_out,
                save_date=_parse_dt(parsed.save_date),
                update_date=_parse_dt(parsed.update_date),
                total_view=parsed.total_view,
                total_like=parsed.total_like,
                total_bookmark=parsed.total_bookmark,
                first_seen_at=now,
                last_scraped_at=now,
                raw_json=parsed.raw_json,
            )
            session.add(prop)
            if prev_hist is None:
                session.add(JamPriceHistory(
                    asset_id=parsed.asset_id,
                    selling=parsed.selling,
                    discount=parsed.discount,
                    rental=parsed.rental,
                    change_type="new",
                    scraped_at=now,
                ))
            counts["new"] += 1
        else:
            # Existing — check for changes
            recent_cutoff = now - timedelta(hours=1)
            already_recorded = prev_hist is not None and prev_hist.scraped_at >= recent_cutoff

            price_changed = (
                float(existing.selling or 0) != float(parsed.selling or 0)
                or float(existing.discount or 0) != float(parsed.discount or 0)
                or float(existing.rental or 0) != float(parsed.rental or 0)
            )
            sold_transition = (
                not existing.status_soldout and parsed.status_soldout
            )
            unsold_transition = (
                existing.status_soldout and not parsed.status_soldout
            )

            # Update fields
            existing.borr_code = parsed.borr_code
            existing.asset_no = parsed.asset_no
            existing.type_sale_code = parsed.type_sale_code
            existing.type_sale_th = parsed.type_sale_th
            existing.type_asset_code = parsed.type_asset_code
            existing.type_asset_th = parsed.type_asset_th
            existing.project_th = parsed.project_th
            existing.project_en = parsed.project_en
            existing.province = parsed.province
            existing.district = parsed.district
            existing.subdistrict = parsed.subdistrict
            existing.province_name = parsed.province_name
            existing.amphur_name = parsed.amphur_name
            existing.district_name = parsed.district_name
            existing.lat = parsed.lat
            existing.lon = parsed.lon
            existing.selling = parsed.selling
            existing.discount = parsed.discount
            existing.rental = parsed.rental
            existing.status_soldout = parsed.status_soldout
            existing.soldout_date = _parse_dt(parsed.soldout_date)
            existing.status_acution = parsed.status_acution
            existing.status_hotdeal = parsed.status_hotdeal
            existing.is_flash_sale = parsed.is_flash_sale
            existing.images_main_web = parsed.images_main_web
            existing.image_sold_out = parsed.image_sold_out
            existing.update_date = _parse_dt(parsed.update_date)
            existing.total_view = parsed.total_view
            existing.total_like = parsed.total_like
            existing.total_bookmark = parsed.total_bookmark
            existing.last_scraped_at = now
            existing.raw_json = parsed.raw_json

            counts["updated"] += 1

            if price_changed and not already_recorded:
                session.add(JamPriceHistory(
                    asset_id=parsed.asset_id,
                    selling=parsed.selling,
                    discount=parsed.discount,
                    rental=parsed.rental,
                    change_type="price_change",
                    scraped_at=now,
                ))
                counts["price_changed"] += 1
            elif price_changed:
                counts["price_changed"] += 1

            if sold_transition and not already_recorded:
                session.add(JamPriceHistory(
                    asset_id=parsed.asset_id,
                    selling=parsed.selling,
                    discount=parsed.discount,
                    rental=parsed.rental,
                    change_type="sold",
                    scraped_at=now,
                ))
                counts["sold"] += 1
            elif sold_transition:
                counts["sold"] += 1

            if unsold_transition and not already_recorded:
                session.add(JamPriceHistory(
                    asset_id=parsed.asset_id,
                    selling=parsed.selling,
                    discount=parsed.discount,
                    rental=parsed.rental,
                    change_type="unsold",
                    scraped_at=now,
                ))
                counts["unsold"] += 1
            elif unsold_transition:
                counts["unsold"] += 1

    return counts

"""SCB Scraper — Database operations with upsert + price history tracking."""

from __future__ import annotations

import os
from datetime import datetime, timedelta

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from models import (
    Base,
    ScbAssetDetail,
    ScbAssetSearch,
    ScbPriceHistory,
    ScbProperty,
    ScbScrapeLog,
)

DB_URI = os.environ.get("POSTGRES_URI", "postgresql://arsapolm@localhost:5432/npa_kb")


def get_engine():
    return create_engine(DB_URI, echo=False, pool_pre_ping=True)


def create_tables():
    engine = get_engine()
    Base.metadata.create_all(engine)
    print("SCB tables created/verified.")
    return engine


def _safe_int(val: str | int | None) -> int | None:
    if val is None:
        return None
    try:
        return int(val)
    except (ValueError, TypeError):
        return None


def _safe_float(val: str | float | None) -> float | None:
    if val is None:
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def _merge_search_to_prop(prop: ScbProperty, search: ScbAssetSearch, now: datetime) -> None:
    """Apply search data to a ScbProperty row."""
    prop.project_id_gen = search.project_id_gen
    prop.project_type = search.project_type
    prop.project_type_name = search.project_type_name
    prop.project_title = search.project_title
    prop.slug = search.slug
    prop.price = search.get_price_baht()
    prop.price_discount = search.get_discount_price_baht()
    prop.province_id = _safe_int(search.province_id)
    prop.district_id = _safe_int(search.district_id)
    prop.project_address = search.project_address
    prop.project_address_detail = search.project_address_detail
    prop.data_location = search.data_location
    prop.lat = search.get_lat()
    prop.lon = search.get_lon()
    prop.area_use = search.get_area_use_sqm()
    prop.land_area = search.get_land_area_sqw()
    prop.area_sqm = _safe_float(search.area_sqm)
    prop.promotion_description = search.promotion_description
    prop.promotion_status = search.promotion_status
    prop.promotion_start_date = search.promotion_start_date
    prop.promotion_end_date = search.promotion_end_date
    prop.project_sold_out = search.project_sold_out
    prop.project_recommended = search.project_recommended
    prop.project_booking = search.project_booking
    prop.project_hide = search.project_hide
    prop.project_new = search.project_new
    prop.total_favorite = _safe_int(search.total_favorite)
    prop.total_booking = _safe_int(search.total_booking)
    prop.image_use = search.image_use
    prop.owner_email = search.owner_email
    prop.scb_create_date = search.create_date
    prop.raw_search_json = search.raw_json
    prop.last_scraped_at = now


def _merge_detail_to_prop(prop: ScbProperty, detail: ScbAssetDetail) -> None:
    """Apply detail-only fields to a ScbProperty row."""
    prop.has_detail = True
    prop.title_deed = detail.title_deed
    prop.bedrooms = detail.bedrooms
    prop.bathrooms = detail.bathrooms
    prop.parking = detail.parking
    prop.description = detail.description
    if detail.images:
        prop.images = detail.images
    if detail.sold_out:
        prop.project_sold_out = detail.sold_out
    prop.raw_detail_json = detail.model_dump(mode="json")


def _load_latest_price_history(
    session: Session, project_ids: list[int]
) -> dict[int, ScbPriceHistory]:
    """Return the most recent ScbPriceHistory row per project_id."""
    if not project_ids:
        return {}
    subq = (
        select(
            ScbPriceHistory.project_id,
            func.max(ScbPriceHistory.scraped_at).label("max_ts"),
        )
        .where(ScbPriceHistory.project_id.in_(project_ids))
        .group_by(ScbPriceHistory.project_id)
        .subquery()
    )
    stmt = select(ScbPriceHistory).join(
        subq,
        (ScbPriceHistory.project_id == subq.c.project_id)
        & (ScbPriceHistory.scraped_at == subq.c.max_ts),
    )
    return {row.project_id: row for row in session.execute(stmt).scalars()}


def upsert_properties(
    session: Session,
    properties: list[tuple[ScbAssetSearch, ScbAssetDetail | None]],
) -> dict[str, int]:
    """
    Upsert SCB properties.
    Each item is (search_data, detail_data_or_None).
    Returns counts: {new, updated, price_changed, state_changed}
    """
    now = datetime.now()
    counts = {"new": 0, "updated": 0, "price_changed": 0, "state_changed": 0}

    pids = [s.project_id for s, _ in properties]
    existing_map: dict[int, ScbProperty] = {}
    if pids:
        stmt = select(ScbProperty).where(ScbProperty.project_id.in_(pids))
        for row in session.execute(stmt).scalars():
            existing_map[row.project_id] = row

    existing_db_ids = list(existing_map.keys())
    latest_history = _load_latest_price_history(session, existing_db_ids)

    for search, detail in properties:
        existing = existing_map.get(search.project_id)
        prev_hist = latest_history.get(search.project_id)

        if existing is None:
            prop = ScbProperty(project_id=search.project_id, first_seen_at=now)
            _merge_search_to_prop(prop, search, now)
            if detail:
                _merge_detail_to_prop(prop, detail)
            session.add(prop)
            if prev_hist is None:
                session.add(ScbPriceHistory(
                    project_id=search.project_id,
                    price=search.get_price_baht(),
                    price_discount=search.get_discount_price_baht(),
                    change_type="new",
                    scraped_at=now,
                ))
            counts["new"] += 1
        else:
            old_price = float(existing.price or 0)
            old_discount = float(existing.price_discount or 0)
            old_sold_out = existing.project_sold_out

            _merge_search_to_prop(existing, search, now)
            if detail:
                _merge_detail_to_prop(existing, detail)

            counts["updated"] += 1

            new_price = float(search.get_price_baht() or 0)
            new_discount = float(search.get_discount_price_baht() or 0)

            price_changed = (
                old_price != new_price or old_discount != new_discount
            )
            state_changed = old_sold_out != search.project_sold_out

            recent_cutoff = now - timedelta(hours=1)
            already_recorded = (
                prev_hist is not None
                and prev_hist.scraped_at.replace(tzinfo=None) >= recent_cutoff
            )

            if price_changed and not already_recorded:
                session.add(ScbPriceHistory(
                    project_id=search.project_id,
                    price=search.get_price_baht(),
                    price_discount=search.get_discount_price_baht(),
                    change_type="price_change",
                    scraped_at=now,
                ))
                counts["price_changed"] += 1
            elif price_changed:
                counts["price_changed"] += 1

            if state_changed and not already_recorded:
                session.add(ScbPriceHistory(
                    project_id=search.project_id,
                    price=search.get_price_baht(),
                    price_discount=search.get_discount_price_baht(),
                    change_type="state_change",
                    scraped_at=now,
                ))
                counts["state_changed"] += 1
            elif state_changed:
                counts["state_changed"] += 1

    return counts

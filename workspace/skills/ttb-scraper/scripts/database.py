"""TTB/PAMCO Scraper — Database operations with upsert + price history tracking."""

from __future__ import annotations

import os
from datetime import datetime, timedelta

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from models import (
    Base,
    TtbPriceHistory,
    TtbProperty,
    TtbPropertyItem,
    TtbScrapeLog,
)

DB_URI = os.environ.get("POSTGRES_URI", "postgresql://arsapolm@localhost:5432/npa_kb")


def get_engine():
    return create_engine(DB_URI, echo=False, pool_pre_ping=True)


def create_tables():
    engine = get_engine()
    Base.metadata.create_all(engine)
    print("TTB tables created/verified.")
    return engine


def _parse_numeric(val: str | None) -> float | None:
    if not val or val == "0.00" or val == "0":
        return None
    try:
        return float(val.replace(",", ""))
    except (ValueError, TypeError):
        return None


def _merge_item_to_prop(prop: TtbProperty, item: TtbPropertyItem, now: datetime) -> None:
    """Apply parsed item data to a TtbProperty row."""
    prop.slug = item.slug
    prop.id_market = item.id_market
    prop.source_type = item.source_type
    prop.title = item.title
    prop.id_detail = item.id_detail
    prop.detail_name = item.detail_name
    prop.id_category = item.id_category
    prop.province_id = item.province_id
    prop.amphur_id = item.amphur_id
    prop.district_id = item.district_id
    prop.province_name = item.province_name
    prop.district_name = item.district_name
    prop.sub_district_name = item.sub_district_name
    prop.region = item.region
    prop.lat = item.get_lat()
    prop.lon = item.get_lon()
    prop.moo = item.moo or None
    prop.soi = item.soi or None
    prop.street = item.street or None
    prop.hgroup = item.hgroup or None
    prop.area_sqw = _parse_numeric(item.area_sqw)
    prop.search_area = _parse_numeric(item.search_area)
    prop.useable_area = _parse_numeric(item.useable_area)
    prop.area_text = item.area_text or None
    prop.floor = item.floor or None
    prop.bedroom = item.bedroom or None
    prop.bathroom = item.bathroom or None
    prop.living_room = item.living_room or None
    prop.kitchen = item.kitchen or None
    prop.parlor = item.parlor or None
    prop.parking = item.parking or None
    prop.land_id = item.land_id or None
    prop.house_id = item.house_id or None
    prop.price = item.price
    prop.no_price = item.no_price
    prop.special_price = item.special_price
    prop.special_price_start = item.special_price_start
    prop.special_price_end = item.special_price_end
    prop.tel_ao = item.tel_ao or None
    prop.comment = item.comment or None
    prop.note_asset = item.note_asset or None
    prop.thumbnail = item.thumbnail
    prop.illustration = item.illustration
    prop.map_images = item.map_images
    prop.video = item.video or None
    prop.nearby = item.nearby
    prop.tag = item.tag or None
    prop.is_approve = item.is_approve
    prop.investment = item.investment or None
    prop.nfr = item.nfr or None
    prop.status_detail = item.status_detail
    prop.start_date = item.start_date
    prop.end_date = item.end_date
    prop.ttb_created_at = item.created_datetime
    prop.ttb_updated_at = item.updated_datetime
    prop.raw_search_json = item.raw_json
    prop.last_scraped_at = now


def _load_latest_price_history(
    session: Session, property_ids: list[int],
) -> dict[int, TtbPriceHistory]:
    """Return the most recent TtbPriceHistory row per property_id."""
    if not property_ids:
        return {}
    subq = (
        select(
            TtbPriceHistory.property_id,
            func.max(TtbPriceHistory.scraped_at).label("max_ts"),
        )
        .where(TtbPriceHistory.property_id.in_(property_ids))
        .group_by(TtbPriceHistory.property_id)
        .subquery()
    )
    stmt = select(TtbPriceHistory).join(
        subq,
        (TtbPriceHistory.property_id == subq.c.property_id)
        & (TtbPriceHistory.scraped_at == subq.c.max_ts),
    )
    return {row.property_id: row for row in session.execute(stmt).scalars()}


def upsert_properties(
    session: Session,
    items: list[TtbPropertyItem],
) -> dict[str, int]:
    """
    Upsert TTB properties.
    Returns counts: {new, updated, price_changed}
    """
    now = datetime.now()
    counts = {"new": 0, "updated": 0, "price_changed": 0}

    prop_ids = [item.id_property for item in items]
    existing_map: dict[int, TtbProperty] = {}
    if prop_ids:
        stmt = select(TtbProperty).where(TtbProperty.id_property.in_(prop_ids))
        for row in session.execute(stmt).scalars():
            existing_map[row.id_property] = row

    existing_db_ids = list(existing_map.keys())
    latest_history = _load_latest_price_history(session, existing_db_ids)

    for item in items:
        existing = existing_map.get(item.id_property)
        prev_hist = latest_history.get(item.id_property) if existing else None

        if existing is None:
            prop = TtbProperty(id_property=item.id_property, first_seen_at=now)
            _merge_item_to_prop(prop, item, now)
            session.add(prop)
            if prev_hist is None:
                session.add(TtbPriceHistory(
                    property_id=item.id_property,
                    price=item.price,
                    special_price=item.special_price,
                    change_type="new",
                    scraped_at=now,
                ))
            counts["new"] += 1
        else:
            old_price = float(existing.price or 0)
            old_special = float(existing.special_price or 0)

            _merge_item_to_prop(existing, item, now)
            counts["updated"] += 1

            price_changed = (
                old_price != float(item.price or 0)
                or old_special != float(item.special_price or 0)
            )

            recent_cutoff = now - timedelta(hours=1)
            already_recorded = (
                prev_hist is not None
                and prev_hist.scraped_at.replace(tzinfo=None) >= recent_cutoff
            )

            if price_changed and not already_recorded:
                session.add(TtbPriceHistory(
                    property_id=item.id_property,
                    price=item.price,
                    special_price=item.special_price,
                    change_type="price_change",
                    scraped_at=now,
                ))
                counts["price_changed"] += 1
            elif price_changed:
                counts["price_changed"] += 1

    return counts

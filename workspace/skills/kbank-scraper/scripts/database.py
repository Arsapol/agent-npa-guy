"""KBank Scraper — Database operations with upsert + price history tracking."""

from __future__ import annotations

import os
from datetime import datetime, timezone

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from models import (
    Base,
    KbankPriceHistory,
    KbankProperty,
    KbankPropertyItem,
    KbankScrapeLog,
)

DB_URI = os.environ.get("POSTGRES_URI", "postgresql://arsapolm@localhost:5432/npa_kb")


def get_engine():
    return create_engine(DB_URI, echo=False, pool_pre_ping=True)


def create_tables():
    engine = get_engine()
    Base.metadata.create_all(engine)
    print("KBank tables created/verified.")
    return engine


def _apply_item_to_prop(prop: KbankProperty, item: KbankPropertyItem, now: datetime) -> None:
    """Apply list API data to a KbankProperty row."""
    prop.property_id_format = item.property_id_format
    prop.source_code = item.source_code
    prop.source_sale_type = item.source_sale_type

    # Location
    prop.province_name = item.province_name
    prop.amphur_name = item.amphur_name
    prop.tambon_name = item.tambon_name
    prop.village_th = item.village_th
    prop.soi_th = item.soi_th
    prop.road_th = item.road_th
    prop.address_no_th = item.address_no_th
    prop.building_th = item.building_th
    prop.floor_th = item.floor_th
    prop.lat = item.get_lat()
    prop.lon = item.get_lon()

    # Property info
    prop.property_type_name = item.property_type_name
    prop.property_type_code = item.get_property_type_code()
    prop.asset_info_th = item.asset_info_th
    prop.bedroom = item.bedroom
    prop.bathroom = item.bathroom
    prop.building_age = item.building_age
    prop.useable_area = item.useable_area

    # Land area
    prop.rai = item.rai
    prop.ngan = item.ngan
    prop.square_area = item.square_area
    prop.area_value = item.area_value
    prop.area = item.area

    # Pricing
    prop.sell_price = item.sell_price
    prop.promotion_price = item.promotion_price
    prop.adjust_price = item.adjust_price
    prop.promotion_name = item.promotion_name
    prop.promotion_remark = item.promotion_remark

    # Status
    prop.is_new = item.is_new
    prop.is_hot = item.is_hot
    prop.is_reserve = item.is_reserve
    prop.is_sold_out = item.is_sold_out
    prop.ai_flag = item.ai_flag
    prop.pm_maintenance_status = item.pm_maintenance_status

    # Media — store only IMAGE-THUMBNAIL paths
    if item.property_mediaes:
        prop.images = [
            m for m in item.property_mediaes
            if m.get("MediaType") in ("IMAGE-THUMBNAIL", "IMAGE-PC")
        ]

    prop.last_scraped_at = now


def upsert_properties(
    session: Session,
    items: list[KbankPropertyItem],
    raw_items: list[dict],
) -> dict[str, int]:
    """
    Upsert KBank properties from list API.
    Returns counts: {new, updated, price_changed, status_changed}
    """
    now = datetime.now(timezone.utc)
    counts = {"new": 0, "updated": 0, "price_changed": 0, "status_changed": 0}

    prop_ids = [item.property_id for item in items]
    existing_map: dict[str, KbankProperty] = {}
    if prop_ids:
        stmt = select(KbankProperty).where(KbankProperty.property_id.in_(prop_ids))
        for row in session.execute(stmt).scalars():
            existing_map[row.property_id] = row

    for item, raw in zip(items, raw_items):
        existing = existing_map.get(item.property_id)

        if existing is None:
            prop = KbankProperty(property_id=item.property_id, first_seen_at=now)
            _apply_item_to_prop(prop, item, now)
            prop.raw_json = raw
            session.add(prop)
            session.add(KbankPriceHistory(
                property_id=item.property_id,
                sell_price=item.sell_price,
                promotion_price=item.promotion_price,
                adjust_price=item.adjust_price,
                change_type="new",
                scraped_at=now,
            ))
            counts["new"] += 1
        else:
            old_sell = float(existing.sell_price or 0)
            old_promo = float(existing.promotion_price or 0)
            old_adjust = float(existing.adjust_price or 0)
            old_sold_out = existing.is_sold_out
            old_reserve = existing.is_reserve

            _apply_item_to_prop(existing, item, now)
            existing.raw_json = raw

            counts["updated"] += 1

            price_changed = (
                old_sell != float(item.sell_price or 0)
                or old_promo != float(item.promotion_price or 0)
                or old_adjust != float(item.adjust_price or 0)
            )

            status_changed = (
                old_sold_out != item.is_sold_out
                or old_reserve != item.is_reserve
            )

            if price_changed:
                session.add(KbankPriceHistory(
                    property_id=item.property_id,
                    sell_price=item.sell_price,
                    promotion_price=item.promotion_price,
                    adjust_price=item.adjust_price,
                    change_type="price_change",
                    scraped_at=now,
                ))
                counts["price_changed"] += 1

            if status_changed:
                session.add(KbankPriceHistory(
                    property_id=item.property_id,
                    sell_price=item.sell_price,
                    promotion_price=item.promotion_price,
                    adjust_price=item.adjust_price,
                    change_type="status_change",
                    scraped_at=now,
                ))
                counts["status_changed"] += 1

    return counts

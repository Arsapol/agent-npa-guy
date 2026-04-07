"""GSB Scraper — Database operations with upsert + price history tracking."""

from __future__ import annotations

import os
from datetime import datetime, timedelta

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from models import (
    Base,
    GsbAssetDetail,
    GsbAssetSearch,
    GsbPriceHistory,
    GsbProperty,
    GsbScrapeLog,
)

DB_URI = os.environ.get("POSTGRES_URI", "postgresql://arsapolm@localhost:5432/npa_kb")


def get_engine():
    return create_engine(DB_URI, echo=False, pool_pre_ping=True)


def create_tables():
    engine = get_engine()
    Base.metadata.create_all(engine)
    print("GSB tables created/verified.")
    return engine


def _parse_float(val: str | float | None) -> float | None:
    if val is None or val == "" or val == 0:
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def _merge_search_to_prop(prop: GsbProperty, search: GsbAssetSearch, now: datetime) -> None:
    """Apply search/list data to a GsbProperty row."""
    prop.asset_id = search.asset_id
    prop.asset_group_id = search.asset_group_id
    prop.asset_type_id = search.asset_type_id
    prop.asset_type_desc = search.asset_type_desc
    prop.asset_subtype_desc = search.asset_subtype_desc
    prop.asset_name = search.asset_name
    prop.province_name = search.province_name
    prop.district_name = search.district_name
    prop.sub_district_name = search.sub_district_name
    prop.village_head = search.village_head
    prop.sum_rai = search.sum_rai
    prop.sum_ngan = search.sum_ngan
    prop.sum_square_wa = search.sum_square_wa
    prop.square_meter = search.square_meter
    prop.rai_ngan_wa = search.rai_ngan_wa
    prop.deed_info = search.deed_info
    prop.image_id = search.image_id
    prop.ind_flag = search.ind_flag
    prop.is_recommend = search.is_recommend
    prop.promo_type = search.promo_type
    prop.promotion_type = search.promotion_type
    prop.current_offer_price = search.current_offer_price
    prop.xprice_normal = search.xprice_normal
    prop.xprice = search.xprice
    prop.xtype = search.xtype
    prop.group_sell_price = search.group_sell_price
    prop.group_special_price = search.group_special_price
    prop.raw_search_json = search.raw_json
    prop.last_scraped_at = now


def _merge_detail_to_prop(prop: GsbProperty, detail: GsbAssetDetail) -> None:
    """Apply detail-only fields to a GsbProperty row."""
    prop.has_detail = True
    prop.lat = _parse_float(detail.latitude)
    prop.lon = _parse_float(detail.longitude)
    prop.building_no = detail.building_no
    prop.floor_no = detail.floor_no
    prop.asset_number = detail.asset_number
    prop.width_meter = detail.width_meter
    prop.depth_meter = detail.depth_meter
    prop.builded_year = detail.builded_year
    prop.road = detail.road
    prop.alley = detail.alley
    prop.remark = detail.remark
    prop.booking_count = detail.booking_count
    prop.count_view = detail.count_view
    prop.asset_pdf = detail.asset_pdf
    prop.buildings = detail.buildings
    prop.events = detail.events
    prop.asset_images = detail.asset_image
    prop.asset_maps = detail.asset_map
    # Update square_meter from detail if available (more accurate)
    if detail.square_meter is not None:
        prop.square_meter = detail.square_meter
    prop.raw_detail_json = detail.model_dump(mode="json")


def _load_latest_price_history(
    session: Session, npa_ids: list[str]
) -> dict[str, GsbPriceHistory]:
    """Return the most recent GsbPriceHistory row per npa_id."""
    if not npa_ids:
        return {}
    from sqlalchemy import func
    subq = (
        select(GsbPriceHistory.npa_id, func.max(GsbPriceHistory.scraped_at).label("max_ts"))
        .where(GsbPriceHistory.npa_id.in_(npa_ids))
        .group_by(GsbPriceHistory.npa_id)
        .subquery()
    )
    stmt = select(GsbPriceHistory).join(
        subq,
        (GsbPriceHistory.npa_id == subq.c.npa_id)
        & (GsbPriceHistory.scraped_at == subq.c.max_ts),
    )
    return {row.npa_id: row for row in session.execute(stmt).scalars()}


def upsert_properties(
    session: Session,
    properties: list[tuple[GsbAssetSearch, GsbAssetDetail | None]],
) -> dict[str, int]:
    """
    Upsert GSB properties.
    Each item is (search_data, detail_data_or_None).
    Returns counts: {new, updated, price_changed}
    """
    now = datetime.now()
    counts = {"new": 0, "updated": 0, "price_changed": 0}

    npa_ids = [s.asset_group_id_npa for s, _ in properties]
    existing_map: dict[str, GsbProperty] = {}
    if npa_ids:
        stmt = select(GsbProperty).where(GsbProperty.npa_id.in_(npa_ids))
        for row in session.execute(stmt).scalars():
            existing_map[row.npa_id] = row

    existing_npa_ids = list(existing_map.keys())
    latest_history = _load_latest_price_history(session, existing_npa_ids)

    for search, detail in properties:
        npa_id = search.asset_group_id_npa
        existing = existing_map.get(npa_id)
        prev_hist = latest_history.get(npa_id)

        if existing is None:
            prop = GsbProperty(npa_id=npa_id, first_seen_at=now)
            _merge_search_to_prop(prop, search, now)
            if detail:
                _merge_detail_to_prop(prop, detail)
            session.add(prop)
            # "new" price history entry
            if prev_hist is None:
                session.add(GsbPriceHistory(
                    npa_id=npa_id,
                    current_offer_price=search.current_offer_price,
                    xprice_normal=search.xprice_normal,
                    xprice=search.xprice,
                    xtype=search.xtype,
                    change_type="new",
                    scraped_at=now,
                ))
            counts["new"] += 1
        else:
            old_offer = int(existing.current_offer_price or 0)
            old_normal = int(existing.xprice_normal or 0)
            old_xprice = int(existing.xprice or 0)
            old_xtype = existing.xtype

            _merge_search_to_prop(existing, search, now)
            if detail:
                _merge_detail_to_prop(existing, detail)

            counts["updated"] += 1

            price_changed = (
                old_offer != int(search.current_offer_price or 0)
                or old_normal != int(search.xprice_normal or 0)
                or old_xprice != int(search.xprice or 0)
                or old_xtype != search.xtype
            )

            # Guard against duplicate history entries within 1h window
            recent_cutoff = now - timedelta(hours=1)
            already_recorded = (
                prev_hist is not None
                and prev_hist.scraped_at.replace(tzinfo=None) >= recent_cutoff
            )

            if price_changed and not already_recorded:
                session.add(GsbPriceHistory(
                    npa_id=npa_id,
                    current_offer_price=search.current_offer_price,
                    xprice_normal=search.xprice_normal,
                    xprice=search.xprice,
                    xtype=search.xtype,
                    change_type="price_change",
                    scraped_at=now,
                ))
                counts["price_changed"] += 1
            elif price_changed:
                counts["price_changed"] += 1  # count it, don't re-insert

    return counts

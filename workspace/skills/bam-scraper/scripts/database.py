"""BAM Scraper — Database operations with upsert + price history tracking."""

from __future__ import annotations

import os
from datetime import datetime, timedelta

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from models import (
    Base,
    BamAssetDetail,
    BamAssetSearch,
    BamPriceHistory,
    BamProperty,
    BamScrapeLog,
)

DB_URI = os.environ.get("POSTGRES_URI", "postgresql://arsapolm@localhost:5432/npa_kb")


def get_engine():
    return create_engine(DB_URI, echo=False, pool_pre_ping=True)


def create_tables():
    engine = get_engine()
    Base.metadata.create_all(engine)
    print("BAM tables created/verified.")
    return engine


def _parse_dt(val: str | None) -> datetime | None:
    if not val or val == "2000-01-01T00:00:00.000Z":
        return None
    try:
        return datetime.fromisoformat(val.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None


def _parse_date(val: str | None) -> datetime | None:
    if not val:
        return None
    try:
        return datetime.fromisoformat(val + "T00:00:00+07:00")
    except (ValueError, AttributeError):
        return None


def _parse_numeric(val: str | None) -> float | None:
    if not val or val == "0.00":
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def _merge_search_to_prop(prop: BamProperty, search: BamAssetSearch, now: datetime) -> None:
    """Apply search data to a BamProperty row."""
    prop.asset_no = search.asset_no
    prop.asset_state = search.asset_state
    prop.province = search.province
    prop.district = search.district
    prop.sub_district = search.sub_district
    prop.project_th = search.project_th
    prop.project_en = search.project_en
    prop.asset_type = search.asset_type
    prop.asset_group = search.asset_group
    prop.asset_code = search.asset_code
    prop.license_number = search.license_number
    prop.property_location = search.property_location
    prop.lat = search.get_lat()
    prop.lon = search.get_lon()
    prop.sell_price = search.sell_price
    prop.discount_price = search.discount_price
    prop.shock_price = search.shock_price
    prop.is_shock_price = search.is_shock_price
    prop.is_hot_deal = search.is_hot_deal
    prop.is_campaign = str(search.is_campaign) if search.is_campaign is not None else None
    prop.campaign_name = (
        ",".join(search.campaign_name) if isinstance(search.campaign_name, list)
        else search.campaign_name
    )
    prop.stars = search.stars
    prop.high_light = search.high_light
    prop.display_price = search.display_price
    prop.display_property = search.display_property
    prop.price_flag = search.price_flag
    prop.bedroom = search.bedroom
    prop.bathroom = search.bathroom
    prop.studio = search.studio
    prop.parking = search.parking
    prop.kitchen = search.kitchen
    prop.rai = _parse_numeric(search.rai)
    prop.ngan = _parse_numeric(search.ngan)
    prop.wa = _parse_numeric(search.wa)
    prop.area_meter = _parse_numeric(search.area_meter)
    prop.usable_area = search.usable_area
    prop.nearby = search.nearby
    prop.album_property = search.album_property
    prop.property_detail = search.property_detail
    prop.invitation_th = search.invitation_th
    prop.note = search.note
    prop.summary = search.summary
    prop.department_code = search.department_code
    prop.department_name = search.department_name
    prop.group_of_department = search.group_of_department
    prop.admin_id = search.admin_id
    prop.admin_name = search.admin_name
    prop.work_phone = search.work_phone
    prop.work_phone_nxt = search.work_phone_nxt
    prop.telephone = search.telephone
    prop.price_package_1 = search.price_package_1
    prop.renovate_price_package_1 = search.renovate_price_package_1
    prop.price_package_2 = search.price_package_2
    prop.renovate_price_package_2 = search.renovate_price_package_2
    prop.price_package_3 = search.price_package_3
    prop.renovate_price_package_3 = search.renovate_price_package_3
    prop.view_count = None  # only from detail
    prop.raw_search_json = search.raw_json
    prop.last_scraped_at = now


def _merge_detail_to_prop(prop: BamProperty, detail: BamAssetDetail) -> None:
    """Apply detail-only fields to a BamProperty row."""
    prop.has_detail = True
    prop.asset_state_code = detail.asset_state_code
    prop.physical_zone = detail.physical_zone
    prop.col_type = detail.col_type
    prop.col_typedesc = detail.col_typedesc
    prop.col_sub_type = detail.col_sub_type
    prop.col_sub_typedesc = detail.col_sub_typedesc
    prop.grade = detail.grade
    prop.evaluate_amt = _parse_numeric(detail.evaluate_amt)
    prop.evaluate_date = _parse_date(detail.evaluate_date)
    prop.cost_asset_amt = _parse_numeric(detail.cost_asset_amt)
    prop.sale_price_spc = _parse_numeric(detail.sale_price_spc_amt)
    prop.sale_price_spc_from = _parse_date(detail.sale_price_spc_from_date)
    prop.sale_price_spc_to = _parse_date(detail.sale_price_spc_to_date)
    prop.size_build = detail.size_build
    prop.livingroom = detail.livingroom
    prop.start_date = _parse_dt(detail.start_date)
    prop.end_date = _parse_dt(detail.end_date)
    prop.sale_date = _parse_dt(detail.sale_date)
    prop.key_date = _parse_dt(detail.key_date)
    prop.bam_update_date = _parse_dt(detail.update_date)
    prop.bam_create_date = _parse_dt(detail.create_date)
    prop.bam_modify_date = _parse_dt(detail.modify_date)
    prop.map_images = detail.image_map
    prop.view_count = detail.view_count
    prop.raw_detail_json = detail.model_dump(mode="json")


def _load_latest_price_history(
    session: Session, asset_ids: list[int]
) -> dict[int, BamPriceHistory]:
    """Return the most recent BamPriceHistory row per asset_id."""
    if not asset_ids:
        return {}
    # Subquery: max scraped_at per asset_id
    from sqlalchemy import func
    subq = (
        select(BamPriceHistory.asset_id, func.max(BamPriceHistory.scraped_at).label("max_ts"))
        .where(BamPriceHistory.asset_id.in_(asset_ids))
        .group_by(BamPriceHistory.asset_id)
        .subquery()
    )
    stmt = select(BamPriceHistory).join(
        subq,
        (BamPriceHistory.asset_id == subq.c.asset_id)
        & (BamPriceHistory.scraped_at == subq.c.max_ts),
    )
    return {row.asset_id: row for row in session.execute(stmt).scalars()}


def upsert_properties(
    session: Session,
    properties: list[tuple[BamAssetSearch, BamAssetDetail | None]],
) -> dict[str, int]:
    """
    Upsert BAM properties.
    Each item is (search_data, detail_data_or_None).
    Returns counts: {new, updated, price_changed, state_changed}
    """
    now = datetime.now()
    counts = {"new": 0, "updated": 0, "price_changed": 0, "state_changed": 0}

    asset_nos = [s.asset_no for s, _ in properties if s.asset_no]
    existing_map: dict[str, BamProperty] = {}
    if asset_nos:
        stmt = select(BamProperty).where(BamProperty.asset_no.in_(asset_nos))
        for row in session.execute(stmt).scalars():
            existing_map[row.asset_no] = row

    existing_db_ids = [row.id for row in existing_map.values()]
    latest_history: dict[int, BamPriceHistory] = _load_latest_price_history(session, existing_db_ids)

    for search, detail in properties:
        existing = existing_map.get(search.asset_no) if search.asset_no else None
        prev_hist = latest_history.get(existing.id) if existing else None

        if existing is None:
            prop = BamProperty(id=search.id, first_seen_at=now)
            _merge_search_to_prop(prop, search, now)
            if detail:
                _merge_detail_to_prop(prop, detail)
            session.add(prop)
            # Only add "new" history if no prior history exists for this asset
            if prev_hist is None:
                session.add(BamPriceHistory(
                    asset_id=search.id,
                    sell_price=search.sell_price,
                    discount_price=search.discount_price,
                    shock_price=search.shock_price,
                    evaluate_amt=_parse_numeric(detail.evaluate_amt) if detail else None,
                    sale_price_spc=_parse_numeric(detail.sale_price_spc_amt) if detail else None,
                    change_type="new",
                    scraped_at=now,
                ))
            counts["new"] += 1
        else:
            old_sell = float(existing.sell_price or 0)
            old_discount = float(existing.discount_price or 0)
            old_shock = float(existing.shock_price or 0)
            old_state = existing.asset_state

            _merge_search_to_prop(existing, search, now)
            if detail:
                _merge_detail_to_prop(existing, detail)

            counts["updated"] += 1

            price_changed = (
                old_sell != float(search.sell_price or 0)
                or old_discount != float(search.discount_price or 0)
                or old_shock != float(search.shock_price or 0)
            )
            state_changed = old_state != search.asset_state

            # Guard against duplicate history entries within the same scrape window (1h)
            recent_cutoff = now - timedelta(hours=1)
            already_recorded_today = (
                prev_hist is not None and prev_hist.scraped_at >= recent_cutoff
            )

            if price_changed and not already_recorded_today:
                session.add(BamPriceHistory(
                    asset_id=existing.id,
                    sell_price=search.sell_price,
                    discount_price=search.discount_price,
                    shock_price=search.shock_price,
                    evaluate_amt=_parse_numeric(detail.evaluate_amt) if detail else None,
                    sale_price_spc=_parse_numeric(detail.sale_price_spc_amt) if detail else None,
                    change_type="price_change",
                    scraped_at=now,
                ))
                counts["price_changed"] += 1
            elif price_changed:
                counts["price_changed"] += 1  # count it, just don't re-insert

            if state_changed and not already_recorded_today:
                session.add(BamPriceHistory(
                    asset_id=existing.id,
                    sell_price=search.sell_price,
                    discount_price=search.discount_price,
                    shock_price=search.shock_price,
                    evaluate_amt=_parse_numeric(detail.evaluate_amt) if detail else None,
                    sale_price_spc=_parse_numeric(detail.sale_price_spc_amt) if detail else None,
                    change_type="state_change",
                    scraped_at=now,
                ))
                counts["state_changed"] += 1
            elif state_changed:
                counts["state_changed"] += 1  # count it, just don't re-insert

    return counts

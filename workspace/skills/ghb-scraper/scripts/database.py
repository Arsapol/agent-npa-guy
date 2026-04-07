"""GHB Scraper — Database operations with upsert + price history tracking."""

from __future__ import annotations

import os
from datetime import datetime, timedelta

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from models import (
    Base,
    GhbApiProperty,
    GhbDetailPage,
    GhbPriceHistory,
    GhbProperty,
    GhbScrapeLog,
)

DB_URI = os.environ.get("POSTGRES_URI", "postgresql://arsapolm@localhost:5432/npa_kb")


def get_engine():
    return create_engine(DB_URI, echo=False, pool_pre_ping=True)


def create_tables():
    engine = get_engine()
    Base.metadata.create_all(engine)
    print("GHB tables created/verified.")
    return engine


def _parse_dt(val: str | None) -> datetime | None:
    """Parse GHB datetime strings like '2021-11-10 14:38:12'."""
    if not val or val.strip() == "":
        return None
    try:
        return datetime.strptime(val.strip(), "%Y-%m-%d %H:%M:%S")
    except (ValueError, AttributeError):
        return None


def _parse_numeric(val: str | None) -> float | None:
    if not val or val == "0":
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def _merge_api_to_prop(prop: GhbProperty, api: GhbApiProperty, now: datetime) -> None:
    """Apply saveproperty API data to a GhbProperty row."""
    prop.property_no = api.property_no
    prop.property_type = api.property_type
    prop.type_id = api.type_id
    prop.property_name = api.property_name
    prop.village_name = api.village_name

    # Pricing
    prop.price_amt = api.price_amt
    prop.promotion_price_amt = api.promotion_price_amt
    prop.begin_auction_price = api.begin_auction_price
    prop.sale_price = api.sale_price

    # Size
    prop.area = api.area
    prop.area_txt = api.area_txt
    prop.usage_area = api.usage_area
    prop.usage_area_txt = api.usage_area_txt
    prop.rai = _parse_numeric(api.rai)
    prop.ngan = _parse_numeric(api.ngan)
    prop.wa = _parse_numeric(api.wa)
    prop.floors = api.floors
    prop.floor = api.floor
    prop.bedrooms = api.bedrooms
    prop.bathrooms = api.bathrooms
    prop.parking_lot = api.parking_lot

    # Location
    prop.sub_district = api.tumbon
    prop.district = api.amphur
    prop.province = api.province
    prop.tumbon_id = api.tumbon_id
    prop.amphur_id = api.amphur_id
    prop.province_id = api.province_id
    prop.lat = api.geo_lat
    prop.lon = api.geo_long

    # Address
    prop.deed_no = api.deed_no
    prop.house_no = api.house_no
    prop.moo = api.moo
    prop.soi = api.soi
    prop.road = api.road

    # Media
    prop.image_url = api.image_url

    # Contact
    prop.contact_person = api.contact_person
    prop.contact_tel_no = api.contact_tel_no
    prop.call_telno = api.call_telno
    prop.branch_code = api.branch_code
    prop.branch_id = api.branch_id

    # Promotion
    prop.promotion_flag = api.promotion_flag
    prop.promotion_id = api.promotion_id
    prop.promotion_name = api.promotion_name

    # Auction
    prop.bid_online_flag = api.bid_online_flag
    prop.bid_date = api.bid_date if api.bid_date else None
    prop.event_type = api.event_type
    prop.booking_flag = api.booking_flag
    prop.booking_url = api.booking_url
    prop.contact_url = api.contact_url
    prop.share_url = api.share_url

    # Status
    prop.property_active_flag = api.property_active_flag
    prop.property_status = api.property_status
    prop.status = api.status

    # Dates
    prop.ghb_created_date = _parse_dt(api.created_date)
    prop.ghb_modified_date = _parse_dt(api.modified_date)

    # Engagement
    prop.view_count = api.view_count
    prop.order_no = api.order_no

    # Raw
    prop.raw_api_json = api.raw_json
    prop.last_scraped_at = now


def _merge_detail_to_prop(prop: GhbProperty, detail: GhbDetailPage) -> None:
    """Apply HTML detail page fields to a GhbProperty row."""
    prop.has_detail = True
    if detail.description:
        prop.description = detail.description
    if detail.floor_info:
        prop.floor_info = detail.floor_info
    if detail.image_ids:
        prop.image_ids = detail.image_ids
    if detail.lat:
        prop.lat = detail.lat
    if detail.lon:
        prop.lon = detail.lon
    # Fill in fields that API might not have
    if detail.property_no and not prop.property_no:
        prop.property_no = detail.property_no
    if detail.property_type and not prop.property_type:
        prop.property_type = detail.property_type
    if detail.project_name and not prop.village_name:
        prop.village_name = detail.project_name
    if detail.deed_no and not prop.deed_no:
        prop.deed_no = detail.deed_no
    if detail.house_no and not prop.house_no:
        prop.house_no = detail.house_no
    if detail.soi and not prop.soi:
        prop.soi = detail.soi
    if detail.road and not prop.road:
        prop.road = detail.road
    if detail.sub_district and not prop.sub_district:
        prop.sub_district = detail.sub_district
    if detail.district and not prop.district:
        prop.district = detail.district
    if detail.province and not prop.province:
        prop.province = detail.province
    if detail.price and not prop.price_amt:
        prop.price_amt = detail.price


def _load_latest_price_history(
    session: Session, property_ids: list[int]
) -> dict[int, GhbPriceHistory]:
    """Return the most recent GhbPriceHistory row per property_id."""
    if not property_ids:
        return {}
    from sqlalchemy import func as sqfunc
    subq = (
        select(
            GhbPriceHistory.property_id,
            sqfunc.max(GhbPriceHistory.scraped_at).label("max_ts"),
        )
        .where(GhbPriceHistory.property_id.in_(property_ids))
        .group_by(GhbPriceHistory.property_id)
        .subquery()
    )
    stmt = select(GhbPriceHistory).join(
        subq,
        (GhbPriceHistory.property_id == subq.c.property_id)
        & (GhbPriceHistory.scraped_at == subq.c.max_ts),
    )
    return {row.property_id: row for row in session.execute(stmt).scalars()}


def upsert_from_api(
    session: Session,
    properties: list[GhbApiProperty],
) -> dict[str, int]:
    """
    Upsert GHB properties from saveproperty API data.
    Returns counts: {new, updated, price_changed, status_changed}
    """
    now = datetime.now()
    counts = {"new": 0, "updated": 0, "price_changed": 0, "status_changed": 0}

    prop_ids = [p.property_id for p in properties]
    existing_map: dict[int, GhbProperty] = {}
    if prop_ids:
        stmt = select(GhbProperty).where(GhbProperty.property_id.in_(prop_ids))
        for row in session.execute(stmt).scalars():
            existing_map[row.property_id] = row

    existing_db_ids = list(existing_map.keys())
    latest_history = _load_latest_price_history(session, existing_db_ids)

    for api_prop in properties:
        existing = existing_map.get(api_prop.property_id)
        prev_hist = latest_history.get(api_prop.property_id) if existing else None

        if existing is None:
            prop = GhbProperty(property_id=api_prop.property_id, first_seen_at=now)
            _merge_api_to_prop(prop, api_prop, now)
            session.add(prop)
            # Only add "new" history if no prior history
            if prev_hist is None:
                session.add(GhbPriceHistory(
                    property_id=api_prop.property_id,
                    price_amt=api_prop.price_amt,
                    promotion_price_amt=api_prop.promotion_price_amt,
                    begin_auction_price=api_prop.begin_auction_price,
                    change_type="new",
                    scraped_at=now,
                ))
            counts["new"] += 1
        else:
            old_price = int(existing.price_amt or 0)
            old_promo = int(existing.promotion_price_amt or 0)
            old_status = existing.property_status

            _merge_api_to_prop(existing, api_prop, now)
            counts["updated"] += 1

            price_changed = (
                old_price != int(api_prop.price_amt or 0)
                or old_promo != int(api_prop.promotion_price_amt or 0)
            )
            status_changed = old_status != api_prop.property_status

            # 1-hour dedup window
            recent_cutoff = now - timedelta(hours=1)
            already_recorded = (
                prev_hist is not None
                and prev_hist.scraped_at.replace(tzinfo=None) >= recent_cutoff
            )

            if price_changed and not already_recorded:
                session.add(GhbPriceHistory(
                    property_id=api_prop.property_id,
                    price_amt=api_prop.price_amt,
                    promotion_price_amt=api_prop.promotion_price_amt,
                    begin_auction_price=api_prop.begin_auction_price,
                    change_type="price_change",
                    scraped_at=now,
                ))
                counts["price_changed"] += 1
            elif price_changed:
                counts["price_changed"] += 1

            if status_changed and not already_recorded:
                session.add(GhbPriceHistory(
                    property_id=api_prop.property_id,
                    price_amt=api_prop.price_amt,
                    promotion_price_amt=api_prop.promotion_price_amt,
                    begin_auction_price=api_prop.begin_auction_price,
                    change_type="status_change",
                    scraped_at=now,
                ))
                counts["status_changed"] += 1
            elif status_changed:
                counts["status_changed"] += 1

    return counts


def upsert_from_listing(
    session: Session,
    cards: list[GhbSearchCard],
) -> dict[str, int]:
    """
    Upsert GHB properties from HTML search listing cards.
    Lighter weight — only property_id and basic info available.
    Returns counts: {new, updated}
    """
    now = datetime.now()
    counts = {"new": 0, "updated": 0}

    prop_ids = [c.property_id for c in cards]
    existing_map: dict[int, GhbProperty] = {}
    if prop_ids:
        stmt = select(GhbProperty).where(GhbProperty.property_id.in_(prop_ids))
        for row in session.execute(stmt).scalars():
            existing_map[row.property_id] = row

    for card in cards:
        existing = existing_map.get(card.property_id)
        if existing is None:
            prop = GhbProperty(
                property_id=card.property_id,
                property_no=card.property_no,
                price_amt=card.price,
                first_seen_at=now,
                last_scraped_at=now,
            )
            session.add(prop)
            counts["new"] += 1
        else:
            existing.last_scraped_at = now
            if card.property_no and not existing.property_no:
                existing.property_no = card.property_no
            counts["updated"] += 1

    return counts

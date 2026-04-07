"""BAY Scraper — Database operations with upsert + price history tracking."""

from __future__ import annotations

import os
from datetime import datetime, timedelta

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from models import (
    Base,
    BayPriceHistory,
    BayProperty,
    BayPropertyDB,
    BayScrapeLog,
)

DB_URI = os.environ.get("POSTGRES_URI", "postgresql://arsapolm@localhost:5432/npa_kb")


def get_engine():
    return create_engine(DB_URI, echo=False, pool_pre_ping=True)


def create_tables():
    engine = get_engine()
    Base.metadata.create_all(engine)
    print("BAY tables created/verified.")
    return engine


def _parse_dt(val: str | None) -> datetime | None:
    if not val or val.startswith("0001-01-01"):
        return None
    try:
        return datetime.fromisoformat(val.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        return None


def _merge_to_db(prop_db: BayPropertyDB, parsed: BayProperty, now: datetime) -> None:
    """Apply parsed BayProperty data to a BayPropertyDB row."""
    prop_db.item_id = parsed.item_id
    prop_db.item_guid = parsed.item_guid
    prop_db.ou = parsed.ou

    # Property details
    prop_db.property_type = parsed.property_type
    prop_db.property_type_name = parsed.property_type_name
    prop_db.category_code = parsed.get_category_code()
    prop_db.project = parsed.project
    prop_db.project_en = parsed.project_en
    prop_db.detail = parsed.detail
    prop_db.detail_en = parsed.detail_en
    prop_db.display_text = parsed.display_text
    prop_db.is_condo = parsed.is_condo

    # Location
    prop_db.province = parsed.province
    prop_db.province_en = parsed.province_en
    prop_db.district = parsed.district
    prop_db.district_en = parsed.district_en
    prop_db.subdistrict = parsed.subdistrict
    prop_db.subdistrict_en = parsed.subdistrict_en
    prop_db.default_address = parsed.default_address
    prop_db.lat = parsed.get_lat()
    prop_db.lon = parsed.get_lon()

    # Size
    prop_db.land_size_rai = parsed.land_size_rai
    prop_db.land_size_ngan = parsed.land_size_ngan
    prop_db.land_size_sq_wa = parsed.land_size_sq_wa
    prop_db.land_size_total_sq_wa = parsed.land_size_total_sq_wa
    prop_db.size_sq_meter = parsed.size_sq_meter
    prop_db.room_width = parsed.room_width
    prop_db.room_depth = parsed.room_deepth
    prop_db.size_text = parsed.size_text

    # Pricing
    prop_db.sale_price = parsed.sale_price
    prop_db.promo_price = parsed.promo_price
    prop_db.final_price = parsed.final_price
    prop_db.discount_pct = parsed.discount

    # Title deed
    prop_db.deed_no = parsed.deed_no
    prop_db.deed_no_en = parsed.deed_no_en
    prop_db.owner = parsed.owner
    prop_db.owner_en = parsed.owner_en

    # Building details
    prop_db.bed_count = parsed.bed_count
    prop_db.bath_count = parsed.bath_count
    prop_db.park_count = parsed.park_count
    prop_db.flag_fitness = parsed.flag_fitness
    prop_db.flag_swim = parsed.flag_swim
    prop_db.flag_security = parsed.flag_security
    prop_db.flag_shop = parsed.flag_shop
    prop_db.flag_lift = parsed.flag_lift

    # Status
    prop_db.sale_status = parsed.sale_status
    prop_db.status_remark = parsed.status_remark
    prop_db.is_public = parsed.public
    prop_db.flag_highlight = parsed.flag_highlight
    prop_db.flag_promo = parsed.flag_promo

    # Contact
    prop_db.sale_name = parsed.sale_name
    prop_db.sale_name_en = parsed.sale_name_en
    prop_db.sale_contact = parsed.sale_contact

    # Images
    prop_db.cover_image_url = parsed.cover_image_url

    # Dates
    prop_db.begin_date = _parse_dt(parsed.begin_date)
    prop_db.end_date = _parse_dt(parsed.end_date)
    prop_db.item_created_when = _parse_dt(parsed.item_created_when)
    prop_db.item_modified_when = _parse_dt(parsed.item_modified_when)

    # Engagement
    prop_db.page_view = parsed.page_view

    # Raw JSON
    prop_db.raw_json = parsed.raw_json

    prop_db.last_scraped_at = now


def _load_latest_price_history(
    session: Session, codes: list[str]
) -> dict[str, BayPriceHistory]:
    """Return the most recent BayPriceHistory row per property_code."""
    if not codes:
        return {}
    from sqlalchemy import func as sqla_func
    subq = (
        select(
            BayPriceHistory.property_code,
            sqla_func.max(BayPriceHistory.scraped_at).label("max_ts"),
        )
        .where(BayPriceHistory.property_code.in_(codes))
        .group_by(BayPriceHistory.property_code)
        .subquery()
    )
    stmt = select(BayPriceHistory).join(
        subq,
        (BayPriceHistory.property_code == subq.c.property_code)
        & (BayPriceHistory.scraped_at == subq.c.max_ts),
    )
    return {row.property_code: row for row in session.execute(stmt).scalars()}


def upsert_properties(
    session: Session,
    properties: list[BayProperty],
) -> dict[str, int]:
    """
    Upsert BAY properties.
    Returns counts: {new, updated, price_changed}
    """
    now = datetime.now()
    counts = {"new": 0, "updated": 0, "price_changed": 0}

    codes = [p.code for p in properties]
    existing_map: dict[str, BayPropertyDB] = {}
    if codes:
        stmt = select(BayPropertyDB).where(BayPropertyDB.code.in_(codes))
        for row in session.execute(stmt).scalars():
            existing_map[row.code] = row

    latest_history = _load_latest_price_history(session, codes)

    for parsed in properties:
        existing = existing_map.get(parsed.code)
        prev_hist = latest_history.get(parsed.code)

        if existing is None:
            prop_db = BayPropertyDB(code=parsed.code, first_seen_at=now)
            _merge_to_db(prop_db, parsed, now)
            session.add(prop_db)

            if prev_hist is None:
                session.add(BayPriceHistory(
                    property_code=parsed.code,
                    sale_price=parsed.sale_price,
                    promo_price=parsed.promo_price,
                    final_price=parsed.final_price,
                    discount_pct=parsed.discount,
                    change_type="new",
                    scraped_at=now,
                ))
            counts["new"] += 1
        else:
            old_sale = float(existing.sale_price or 0)
            old_promo = float(existing.promo_price or 0)
            old_final = float(existing.final_price or 0)

            _merge_to_db(existing, parsed, now)
            counts["updated"] += 1

            price_changed = (
                old_sale != float(parsed.sale_price or 0)
                or old_promo != float(parsed.promo_price or 0)
                or old_final != float(parsed.final_price or 0)
            )

            recent_cutoff = now - timedelta(hours=1)
            already_recorded = (
                prev_hist is not None
                and prev_hist.scraped_at.replace(tzinfo=None) >= recent_cutoff
            )

            if price_changed and not already_recorded:
                session.add(BayPriceHistory(
                    property_code=parsed.code,
                    sale_price=parsed.sale_price,
                    promo_price=parsed.promo_price,
                    final_price=parsed.final_price,
                    discount_pct=parsed.discount,
                    change_type="price_change",
                    scraped_at=now,
                ))
                counts["price_changed"] += 1
            elif price_changed:
                counts["price_changed"] += 1

    return counts

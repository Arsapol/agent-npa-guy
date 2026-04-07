"""LH Bank Scraper -- Database operations with upsert + price history tracking."""

from __future__ import annotations

import os
from datetime import datetime, timedelta

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from models import (
    Base,
    LHDetail,
    LHListItem,
    LHPriceHistory,
    LHProperty,
    LHScrapeLog,
    parse_area_sqm,
)

DB_URI = os.environ.get("POSTGRES_URI", "postgresql://arsapolm@localhost:5432/npa_kb")


def get_engine():
    return create_engine(DB_URI, echo=False, pool_pre_ping=True)


def create_tables():
    engine = get_engine()
    Base.metadata.create_all(engine)
    print("LH Bank tables created/verified.")
    return engine


def _load_latest_price_history(
    session: Session, property_ids: list[str]
) -> dict[str, LHPriceHistory]:
    """Return the most recent LHPriceHistory row per property_id."""
    if not property_ids:
        return {}
    from sqlalchemy import func

    subq = (
        select(
            LHPriceHistory.property_id,
            func.max(LHPriceHistory.scraped_at).label("max_ts"),
        )
        .where(LHPriceHistory.property_id.in_(property_ids))
        .group_by(LHPriceHistory.property_id)
        .subquery()
    )
    stmt = select(LHPriceHistory).join(
        subq,
        (LHPriceHistory.property_id == subq.c.property_id)
        & (LHPriceHistory.scraped_at == subq.c.max_ts),
    )
    return {row.property_id: row for row in session.execute(stmt).scalars()}


def upsert_properties(
    session: Session,
    items: list[tuple[LHListItem, LHDetail | None]],
) -> dict[str, int]:
    """
    Upsert LH Bank properties.
    Each item is (listing_card, detail_or_None).
    Returns counts: {new, updated, price_changed}
    """
    now = datetime.now()
    counts = {"new": 0, "updated": 0, "price_changed": 0}

    prop_ids = [card.asset_code for card, _ in items if card.asset_code]
    existing_map: dict[str, LHProperty] = {}
    if prop_ids:
        stmt = select(LHProperty).where(LHProperty.property_id.in_(prop_ids))
        for row in session.execute(stmt).scalars():
            existing_map[row.property_id] = row

    latest_history = _load_latest_price_history(session, list(existing_map.keys()))

    for card, detail in items:
        if not card.asset_code:
            continue

        existing = existing_map.get(card.asset_code)
        prev_hist = latest_history.get(card.asset_code) if existing else None

        sale_price = detail.asking_price if detail else card.price
        area_text = detail.area_text if detail and detail.area_text else card.area_text
        area_sqm = parse_area_sqm(area_text) if area_text else None

        if existing is None:
            prop = LHProperty(
                property_id=card.asset_code,
                asset_type=detail.asset_type if detail else card.asset_type,
                case_info=detail.case_info if detail else None,
                sale_price=sale_price,
                address=detail.location if detail else card.address,
                location_text=card.address,
                lat=detail.latitude if detail else None,
                lon=detail.longitude if detail else None,
                area_text=area_text,
                area_sqm=area_sqm,
                description=detail.status_desc if detail else None,
                post_date=detail.record_date if detail else None,
                thumbnail_url=card.thumbnail,
                map_image_url=detail.map_image_url if detail else None,
                pdf_url=detail.pdf_url if detail else None,
                images=detail.image_urls if detail else None,
                detail_url=card.detail_url,
                first_seen_at=now,
                last_scraped_at=now,
                has_detail=detail is not None,
                raw_listing=card.model_dump(mode="json"),
                raw_detail=detail.model_dump(mode="json") if detail else None,
            )
            session.add(prop)

            if prev_hist is None:
                session.add(LHPriceHistory(
                    property_id=card.asset_code,
                    sale_price=sale_price,
                    change_type="new",
                    scraped_at=now,
                ))
            counts["new"] += 1
        else:
            old_price = float(existing.sale_price or 0)

            existing.asset_type = detail.asset_type if detail else card.asset_type
            existing.case_info = detail.case_info if detail else existing.case_info
            existing.sale_price = sale_price
            existing.address = detail.location if detail else card.address
            existing.location_text = card.address
            if detail:
                existing.lat = detail.latitude
                existing.lon = detail.longitude
                existing.description = detail.status_desc
                existing.post_date = detail.record_date
                existing.map_image_url = detail.map_image_url
                existing.pdf_url = detail.pdf_url
                existing.images = detail.image_urls
                existing.has_detail = True
                existing.raw_detail = detail.model_dump(mode="json")
            existing.area_text = area_text
            existing.area_sqm = area_sqm
            existing.thumbnail_url = card.thumbnail
            existing.detail_url = card.detail_url
            existing.last_scraped_at = now
            existing.raw_listing = card.model_dump(mode="json")

            counts["updated"] += 1

            price_changed = old_price != float(sale_price or 0)

            recent_cutoff = now - timedelta(hours=1)
            hist_ts = prev_hist.scraped_at.replace(tzinfo=None) if prev_hist and prev_hist.scraped_at else None
            already_recorded = hist_ts is not None and hist_ts >= recent_cutoff

            if price_changed and not already_recorded:
                session.add(LHPriceHistory(
                    property_id=card.asset_code,
                    sale_price=sale_price,
                    change_type="price_change",
                    scraped_at=now,
                ))
                counts["price_changed"] += 1
            elif price_changed:
                counts["price_changed"] += 1

    return counts

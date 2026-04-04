"""KTB Scraper — Database operations with upsert + price history tracking."""

from __future__ import annotations

import os
from datetime import datetime, timedelta

from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session

from models import (
    Base,
    KtbPriceHistory,
    KtbProperty,
    KtbSearchItem,
    KtbScrapeLog,
)

DB_URI = os.environ.get("POSTGRES_URI", "postgresql://arsapolm@localhost:5432/npa_kb")


def get_engine():
    return create_engine(DB_URI, echo=False, pool_pre_ping=True)


def create_tables():
    engine = get_engine()
    Base.metadata.create_all(engine)
    print("KTB tables created/verified.")
    return engine


def _merge_search_to_prop(prop: KtbProperty, item: KtbSearchItem, now: datetime) -> None:
    """Apply search data to a KtbProperty row."""
    prop.province = item.shr_province_name
    prop.amphur = item.shr_amphur_name
    prop.tambon = item.shr_tambon_name
    prop.province_no = item.shr_province_no
    prop.addr = item.addr
    prop.road = item.road
    prop.lat = item.get_lat()
    prop.lon = item.get_lon()
    prop.coll_type_name = item.coll_type_name
    prop.coll_cate_name = item.coll_cate_name
    prop.coll_cate_no = item.coll_cate_no
    prop.coll_desc = item.coll_desc
    prop.asset_type = item.asset_type
    prop.coll_code = item.coll_code
    prop.coll_mono_code = item.coll_mono_code
    prop.coll_mono_code_all = item.coll_mono_code_all
    prop.price = item.get_price_baht()
    prop.nml_price = item.get_nml_price_baht()
    prop.cate_name = item.cate_name
    prop.cate_no = item.cate_no
    prop.price_str_dt = item.price_str_dt
    prop.price_end_dt = item.price_end_dt
    prop.is_speedy = item.is_speedy
    prop.is_new_asset = item.is_new_asset
    prop.is_promotion = item.is_promotion
    prop.is_new_pay = item.is_new_pay

    rai, ngan, wah = item.parse_area()
    prop.area = item.area
    prop.rai = rai
    prop.ngan = ngan
    prop.wah = wah
    prop.sum_area_num = item.sum_area_num
    prop.bedroom_num = item.bedroom_num
    prop.bathroom_num = item.bathroom_num
    prop.file_name = item.file_name
    prop.link_vdo = item.link_vdo
    prop.share_url = item.share_url
    prop.contact_name = item.contact_name
    prop.contact_tel = item.contact_tel
    prop.percent_year = item.percent_year
    prop.percent_year_flag = item.percent_year_flag
    prop.product_count_view = item.product_count_view
    prop.open_bidding_price = item.open_bidding_price
    prop.guarantee_amount = item.guarantee_amount
    prop.raw_search_json = item.raw_json
    prop.last_scraped_at = now


def _merge_detail_to_prop(prop: KtbProperty, detail: KtbSearchItem) -> None:
    """Apply detail-only fields to a KtbProperty row."""
    prop.has_detail = True
    if detail.coll_type_name:
        prop.coll_type_name = detail.coll_type_name
    if detail.coll_desc:
        prop.coll_desc = detail.coll_desc
    if detail.list_img:
        prop.list_img = detail.list_img
    if detail.shr_addrline1:
        prop.addrline1 = detail.shr_addrline1
    if detail.shr_addrline2:
        prop.addrline2 = detail.shr_addrline2
    if detail.lodge:
        prop.lodge = detail.lodge
    if detail.bedroom_num is not None:
        prop.bedroom_num = detail.bedroom_num
    if detail.bathroom_num is not None:
        prop.bathroom_num = detail.bathroom_num
    if detail.near_hospital_name:
        prop.near_hospital_name = detail.near_hospital_name
        prop.near_hospital_dist = detail.near_hospital_dist
    if detail.near_school_name:
        prop.near_school_name = detail.near_school_name
        prop.near_school_dist = detail.near_school_dist
    if detail.near_shop_name:
        prop.near_shop_name = detail.near_shop_name
        prop.near_shop_dist = detail.near_shop_dist
    if detail.shr_price_vos:
        prop.shr_price_vos = detail.shr_price_vos
    prop.raw_detail_json = detail.raw_json


def _load_latest_price_history(
    session: Session, coll_grp_ids: list[int]
) -> dict[int, KtbPriceHistory]:
    if not coll_grp_ids:
        return {}
    subq = (
        select(KtbPriceHistory.coll_grp_id, func.max(KtbPriceHistory.scraped_at).label("max_ts"))
        .where(KtbPriceHistory.coll_grp_id.in_(coll_grp_ids))
        .group_by(KtbPriceHistory.coll_grp_id)
        .subquery()
    )
    stmt = select(KtbPriceHistory).join(
        subq,
        (KtbPriceHistory.coll_grp_id == subq.c.coll_grp_id)
        & (KtbPriceHistory.scraped_at == subq.c.max_ts),
    )
    return {row.coll_grp_id: row for row in session.execute(stmt).scalars()}


def upsert_properties(
    session: Session,
    properties: list[tuple[KtbSearchItem, KtbSearchItem | None]],
) -> dict[str, int]:
    """
    Upsert KTB properties.
    Each item is (search_data, detail_data_or_None).
    Returns counts: {new, updated, price_changed, category_changed}
    """
    now = datetime.now()
    counts = {"new": 0, "updated": 0, "price_changed": 0, "category_changed": 0}

    ids = [s.coll_grp_id for s, _ in properties]
    existing_map: dict[int, KtbProperty] = {}
    if ids:
        stmt = select(KtbProperty).where(KtbProperty.coll_grp_id.in_(ids))
        for row in session.execute(stmt).scalars():
            existing_map[row.coll_grp_id] = row

    latest_history = _load_latest_price_history(session, ids)

    for search, detail in properties:
        existing = existing_map.get(search.coll_grp_id)
        prev_hist = latest_history.get(search.coll_grp_id)

        if existing is None:
            prop = KtbProperty(coll_grp_id=search.coll_grp_id, first_seen_at=now)
            _merge_search_to_prop(prop, search, now)
            if detail:
                _merge_detail_to_prop(prop, detail)
            session.add(prop)
            if prev_hist is None:
                session.add(KtbPriceHistory(
                    coll_grp_id=search.coll_grp_id,
                    price=search.get_price_baht(),
                    nml_price=search.get_nml_price_baht(),
                    cate_no=search.cate_no,
                    cate_name=search.cate_name,
                    change_type="new",
                    scraped_at=now,
                ))
            counts["new"] += 1
        else:
            old_price = float(existing.price or 0)
            old_cate_no = existing.cate_no

            _merge_search_to_prop(existing, search, now)
            if detail:
                _merge_detail_to_prop(existing, detail)

            counts["updated"] += 1

            new_price = float(search.get_price_baht() or 0)
            price_changed = old_price != new_price
            category_changed = old_cate_no != search.cate_no

            recent_cutoff = now - timedelta(hours=1)
            already_recorded = prev_hist is not None and prev_hist.scraped_at >= recent_cutoff

            if price_changed and not already_recorded:
                session.add(KtbPriceHistory(
                    coll_grp_id=search.coll_grp_id,
                    price=search.get_price_baht(),
                    nml_price=search.get_nml_price_baht(),
                    cate_no=search.cate_no,
                    cate_name=search.cate_name,
                    change_type="price_change",
                    scraped_at=now,
                ))
                counts["price_changed"] += 1
            elif price_changed:
                counts["price_changed"] += 1

            if category_changed and not already_recorded:
                session.add(KtbPriceHistory(
                    coll_grp_id=search.coll_grp_id,
                    price=search.get_price_baht(),
                    nml_price=search.get_nml_price_baht(),
                    cate_no=search.cate_no,
                    cate_name=search.cate_name,
                    change_type="state_change",
                    scraped_at=now,
                ))
                counts["category_changed"] += 1
            elif category_changed:
                counts["category_changed"] += 1

    return counts

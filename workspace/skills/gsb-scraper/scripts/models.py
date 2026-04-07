"""
GSB (ออมสิน) NPA Scraper — Pydantic v2 + SQLAlchemy 2.0 models.

Prices stored in whole baht (integer).
Two sources: search API endpoint + detail via __NEXT_DATA__ HTML parsing.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator
from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Float,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


# ---------------------------------------------------------------------------
# Pydantic models (parsing layer)
# ---------------------------------------------------------------------------


class GsbAssetSearch(BaseModel):
    """Parsed property from GSB search/list API."""

    asset_id: str
    asset_group_id: str | None = None
    asset_group_id_npa: str  # primary business key (e.g. "BKK620093")
    asset_type_id: int
    asset_type_desc: str | None = None
    asset_subtype_desc: str | None = None
    asset_name: str | None = None

    # Pricing (whole baht)
    current_offer_price: int | None = None
    xprice_normal: int | None = None
    xprice: int | None = None
    xtype: str | None = None  # "promotion" or "normal"
    group_sell_price: int | None = None
    group_special_price: int | None = None

    # Location
    province_name: str | None = None
    district_name: str | None = None
    sub_district_name: str | None = None
    village_head: str | None = None

    # Land area
    sum_rai: int | None = None
    sum_ngan: int | None = None
    sum_square_wa: float | None = None
    square_meter: float | None = None
    rai_ngan_wa: str | None = None

    # Title / legal
    deed_info: str | None = None

    # Media
    image_id: str | None = None

    # Flags
    ind_flag: str | None = None
    is_recommend: bool | None = None
    promo_type: str | None = None
    promotion_type: str | None = None
    events: str | None = None  # JSON string in list response

    # Raw JSON for future-proofing
    raw_json: dict[str, Any] = Field(default_factory=dict)

    model_config = {"populate_by_name": True}

    @field_validator(
        "current_offer_price", "xprice_normal", "xprice",
        "group_sell_price", "group_special_price",
        mode="before",
    )
    @classmethod
    def parse_price(cls, v: Any) -> int | None:
        if v is None or v == "" or v == 0:
            return None
        if isinstance(v, str):
            return int(v.replace(",", ""))
        return int(v)


class GsbAssetDetail(BaseModel):
    """Extra fields from __NEXT_DATA__ detail page (superset of list)."""

    # GPS
    latitude: str | None = None
    longitude: str | None = None

    # Building details
    building_no: str | None = None
    floor_no: str | None = None
    asset_number: str | None = None  # unit/room number
    square_meter: float | None = None
    square_wa: float | None = None
    width_meter: str | None = None
    depth_meter: str | None = None
    builded_year: str | None = None  # Buddhist era, store as-is

    # Address
    road: str | None = None
    alley: str | None = None
    remark: str | None = None

    # Engagement
    booking_count: int | None = None
    count_view: str | None = None

    # Media
    asset_image: list[dict] | None = None
    asset_map: list[dict] | None = None
    panorama_image: list[dict] | None = None
    asset_pdf: str | None = None

    # Sub-objects
    buildings: list[dict] | None = None
    events: list[dict] | None = None  # parsed objects in detail

    model_config = {"populate_by_name": True}


# ---------------------------------------------------------------------------
# SQLAlchemy models (database layer)
# ---------------------------------------------------------------------------


class Base(DeclarativeBase):
    pass


class GsbProperty(Base):
    """Merged search + detail data for a GSB NPA property."""

    __tablename__ = "gsb_properties"

    # npa_id is the stable business key (asset_group_id_npa)
    npa_id: Mapped[str] = mapped_column(Text, primary_key=True)
    asset_id: Mapped[str | None] = mapped_column(Text)
    asset_group_id: Mapped[str | None] = mapped_column(Text)
    asset_type_id: Mapped[int | None] = mapped_column(Integer)
    asset_type_desc: Mapped[str | None] = mapped_column(Text)
    asset_subtype_desc: Mapped[str | None] = mapped_column(Text)
    asset_name: Mapped[str | None] = mapped_column(Text)

    # Location
    province_name: Mapped[str | None] = mapped_column(Text, index=True)
    district_name: Mapped[str | None] = mapped_column(Text)
    sub_district_name: Mapped[str | None] = mapped_column(Text)
    village_head: Mapped[str | None] = mapped_column(Text)
    road: Mapped[str | None] = mapped_column(Text)
    alley: Mapped[str | None] = mapped_column(Text)

    # GPS (from detail only)
    lat: Mapped[float | None] = mapped_column(Float)
    lon: Mapped[float | None] = mapped_column(Float)

    # Land area
    sum_rai: Mapped[int | None] = mapped_column(Integer)
    sum_ngan: Mapped[int | None] = mapped_column(Integer)
    sum_square_wa: Mapped[float | None] = mapped_column(Numeric(10, 2))
    square_meter: Mapped[float | None] = mapped_column(Numeric(12, 2))
    rai_ngan_wa: Mapped[str | None] = mapped_column(Text)

    # Building (from detail)
    building_no: Mapped[str | None] = mapped_column(Text)
    floor_no: Mapped[str | None] = mapped_column(Text)
    asset_number: Mapped[str | None] = mapped_column(Text)  # unit/room
    width_meter: Mapped[str | None] = mapped_column(Text)
    depth_meter: Mapped[str | None] = mapped_column(Text)
    builded_year: Mapped[str | None] = mapped_column(Text)  # Buddhist era

    # Pricing (whole baht)
    current_offer_price: Mapped[int | None] = mapped_column(Numeric(14, 0))
    xprice_normal: Mapped[int | None] = mapped_column(Numeric(14, 0))
    xprice: Mapped[int | None] = mapped_column(Numeric(14, 0))
    xtype: Mapped[str | None] = mapped_column(Text)
    group_sell_price: Mapped[int | None] = mapped_column(Numeric(14, 0))
    group_special_price: Mapped[int | None] = mapped_column(Numeric(14, 0))

    # Title / legal
    deed_info: Mapped[str | None] = mapped_column(Text)

    # Flags
    ind_flag: Mapped[str | None] = mapped_column(Text)
    is_recommend: Mapped[bool | None] = mapped_column(Boolean)
    promo_type: Mapped[str | None] = mapped_column(Text)
    promotion_type: Mapped[str | None] = mapped_column(Text)

    # Text
    remark: Mapped[str | None] = mapped_column(Text)

    # Engagement (from detail)
    booking_count: Mapped[int | None] = mapped_column(Integer)
    count_view: Mapped[str | None] = mapped_column(Text)

    # Media
    image_id: Mapped[str | None] = mapped_column(Text)
    asset_pdf: Mapped[str | None] = mapped_column(Text)

    # Sub-objects (JSONB)
    buildings: Mapped[dict | None] = mapped_column(JSONB)
    events: Mapped[dict | None] = mapped_column(JSONB)
    asset_images: Mapped[dict | None] = mapped_column(JSONB)
    asset_maps: Mapped[dict | None] = mapped_column(JSONB)

    # Scraper metadata
    first_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    last_scraped_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    has_detail: Mapped[bool] = mapped_column(Boolean, server_default="false")

    # Full API responses
    raw_search_json: Mapped[dict | None] = mapped_column(JSONB)
    raw_detail_json: Mapped[dict | None] = mapped_column(JSONB)

    __table_args__ = (
        Index("ix_gsb_province", "province_name"),
        Index("ix_gsb_asset_type", "asset_type_id"),
        Index("ix_gsb_price", "current_offer_price"),
        Index("ix_gsb_location", "province_name", "district_name"),
    )


class GsbPriceHistory(Base):
    __tablename__ = "gsb_price_history"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    npa_id: Mapped[str] = mapped_column(Text, index=True)

    current_offer_price: Mapped[int | None] = mapped_column(Numeric(14, 0))
    xprice_normal: Mapped[int | None] = mapped_column(Numeric(14, 0))
    xprice: Mapped[int | None] = mapped_column(Numeric(14, 0))
    xtype: Mapped[str | None] = mapped_column(Text)

    # new, price_change, state_change
    change_type: Mapped[str] = mapped_column(String(20))

    scraped_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (
        Index("ix_gsb_ph_npa_date", "npa_id", "scraped_at"),
    )


class GsbScrapeLog(Base):
    __tablename__ = "gsb_scrape_logs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    total_search: Mapped[int | None] = mapped_column(Integer)
    total_detail: Mapped[int | None] = mapped_column(Integer)
    new_count: Mapped[int | None] = mapped_column(Integer)
    updated_count: Mapped[int | None] = mapped_column(Integer)
    price_changed_count: Mapped[int | None] = mapped_column(Integer)
    failed_details: Mapped[int | None] = mapped_column(Integer)
    error: Mapped[str | None] = mapped_column(Text)
    asset_types_scraped: Mapped[str | None] = mapped_column(Text)

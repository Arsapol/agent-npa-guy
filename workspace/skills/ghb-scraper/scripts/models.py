"""
GHB Scraper — Pydantic v2 + SQLAlchemy 2.0 models.

Prices stored in whole baht (Numeric).
Two data sources: HTML detail page + saveproperty API.
Upsert keyed by property_no (public property code).
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


class GhbSearchCard(BaseModel):
    """Parsed property card from HTML search listing."""

    property_id: int
    property_no: str | None = None
    title: str | None = None
    price: int | None = None
    location: str | None = None
    area_text: str | None = None
    order_no: str | None = None
    image_url: str | None = None
    promotion_label: str | None = None

    model_config = {"populate_by_name": True}

    @field_validator("price", mode="before")
    @classmethod
    def parse_price(cls, v: Any) -> int | None:
        if v is None or v == "" or v == 0:
            return None
        if isinstance(v, str):
            cleaned = v.replace(",", "").replace("฿", "").replace("บาท", "").strip()
            try:
                return int(float(cleaned))
            except (ValueError, TypeError):
                return None
        return int(v)


class GhbDetailPage(BaseModel):
    """Parsed property from HTML detail page."""

    property_id: int
    title: str | None = None
    price: int | None = None
    property_no: str | None = None
    property_type: str | None = None
    project_name: str | None = None
    area_text: str | None = None
    floor_info: str | None = None
    deed_no: str | None = None
    house_no: str | None = None
    soi: str | None = None
    road: str | None = None
    sub_district: str | None = None
    district: str | None = None
    province: str | None = None
    lat: float | None = None
    lon: float | None = None
    image_ids: list[str] = Field(default_factory=list)
    description: str | None = None

    model_config = {"populate_by_name": True}

    @field_validator("price", mode="before")
    @classmethod
    def parse_price(cls, v: Any) -> int | None:
        if v is None or v == "" or v == 0:
            return None
        if isinstance(v, str):
            cleaned = v.replace(",", "").replace("฿", "").replace("บาท", "").strip()
            try:
                return int(float(cleaned))
            except (ValueError, TypeError):
                return None
        return int(v)


class GhbApiProperty(BaseModel):
    """Parsed property from saveproperty REST API (richest JSON source)."""

    property_id: int = Field(alias="propertyId")
    property_no: str = Field(alias="propertyNo")
    property_type: str | None = Field(None, alias="propertyType")
    type_id: int | None = Field(None, alias="typeId")
    property_name: str | None = Field(None, alias="propertyName")
    village_name: str | None = Field(None, alias="villageName")

    # Pricing (whole baht)
    price_amt: int | None = Field(None, alias="priceAmt")
    promotion_price_amt: int | None = Field(None, alias="promotionPriceAmt")
    begin_auction_price: int | None = Field(None, alias="beginAuctionPrice")
    sale_price: int | None = Field(None, alias="salePrice")
    auction_price_max: int | None = Field(None, alias="auctionPriceMax")

    # Size
    area: str | None = None
    area_txt: str | None = Field(None, alias="areaTxt")
    usage_area: str | None = Field(None, alias="usageArea")
    usage_area_txt: str | None = Field(None, alias="usageAreaTxt")
    rai: str | None = None
    ngan: str | None = None
    wa: str | None = None
    floors: int | None = None
    floor: int | None = None
    bedrooms: int | None = None
    bathrooms: int | None = None
    parking_lot: int | None = Field(None, alias="parkingLot")

    # Location
    tumbon: str | None = None
    amphur: str | None = None
    province: str | None = None
    tumbon_id: int | None = Field(None, alias="tumbonId")
    amphur_id: int | None = Field(None, alias="amphurId")
    province_id: int | None = Field(None, alias="provinceId")
    geo_lat: float | None = Field(None, alias="geoLat")
    geo_long: float | None = Field(None, alias="geoLong")

    # Address
    deed_no: str | None = Field(None, alias="deedNo")
    house_no: str | None = Field(None, alias="houseNo")
    moo: str | None = None
    soi: str | None = None
    road: str | None = None

    # Media
    image_url: str | None = Field(None, alias="imageUrl")

    # Contact
    contact_person: str | None = Field(None, alias="contactPerson")
    contact_tel_no: str | None = Field(None, alias="contactTelNo")
    call_telno: str | None = Field(None, alias="callTelno")
    branch_code: str | None = Field(None, alias="branchCode")
    branch_id: int | None = Field(None, alias="branchId")

    # Promotion
    promotion_flag: int | None = Field(None, alias="promotionFlag")
    promotion_id: int | None = Field(None, alias="promotionId")
    promotion_name: str | None = Field(None, alias="promotionName")

    # Auction
    bid_online_flag: str | None = Field(None, alias="bidOnlineFlag")
    bid_date: str | None = Field(None, alias="bidDate")
    event_type: str | None = Field(None, alias="eventType")
    booking_flag: str | None = Field(None, alias="bookingFlag")
    booking_url: str | None = Field(None, alias="bookingUrl")
    contact_url: str | None = Field(None, alias="contactUrl")
    share_url: str | None = Field(None, alias="shareUrl")

    # Status
    property_active_flag: int | None = Field(None, alias="propertyActiveFlag")
    property_status: str | None = Field(None, alias="propertyStatus")
    status: int | None = None

    # Dates
    created_date: str | None = Field(None, alias="createdDate")
    modified_date: str | None = Field(None, alias="modifiedDate")

    # Engagement
    view_count: int | None = Field(None, alias="viewCount")
    order_no: int | None = Field(None, alias="orderNo")

    # Raw JSON for future-proofing
    raw_json: dict[str, Any] = Field(default_factory=dict)

    model_config = {"populate_by_name": True}

    @field_validator(
        "price_amt", "promotion_price_amt", "begin_auction_price",
        "sale_price", "auction_price_max",
        mode="before",
    )
    @classmethod
    def parse_price(cls, v: Any) -> int | None:
        if v is None or v == "" or v == 0:
            return None
        if isinstance(v, str):
            return int(float(v.replace(",", "")))
        return int(v)

    @field_validator("village_name", "property_name", mode="before")
    @classmethod
    def clean_null_string(cls, v: Any) -> str | None:
        if v is None or v == "null" or v == "None":
            return None
        return str(v).strip() if v else None


# ---------------------------------------------------------------------------
# SQLAlchemy models (database layer)
# ---------------------------------------------------------------------------


class Base(DeclarativeBase):
    pass


class GhbProperty(Base):
    """GHB NPA property — merged from HTML + API sources."""

    __tablename__ = "ghb_properties"

    property_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    property_no: Mapped[str | None] = mapped_column(Text)

    # Classification
    property_type: Mapped[str | None] = mapped_column(Text)
    type_id: Mapped[int | None] = mapped_column(Integer)
    property_name: Mapped[str | None] = mapped_column(Text)
    village_name: Mapped[str | None] = mapped_column(Text)

    # Pricing (whole baht)
    price_amt: Mapped[int | None] = mapped_column(Numeric(14, 0))
    promotion_price_amt: Mapped[int | None] = mapped_column(Numeric(14, 0))
    begin_auction_price: Mapped[int | None] = mapped_column(Numeric(14, 0))
    sale_price: Mapped[int | None] = mapped_column(Numeric(14, 0))

    # Size
    area: Mapped[str | None] = mapped_column(Text)
    area_txt: Mapped[str | None] = mapped_column(Text)
    usage_area: Mapped[str | None] = mapped_column(Text)
    usage_area_txt: Mapped[str | None] = mapped_column(Text)
    rai: Mapped[float | None] = mapped_column(Numeric(10, 2))
    ngan: Mapped[float | None] = mapped_column(Numeric(10, 2))
    wa: Mapped[float | None] = mapped_column(Numeric(10, 2))
    floors: Mapped[int | None] = mapped_column(Integer)
    floor: Mapped[int | None] = mapped_column(Integer)
    bedrooms: Mapped[int | None] = mapped_column(Integer)
    bathrooms: Mapped[int | None] = mapped_column(Integer)
    parking_lot: Mapped[int | None] = mapped_column(Integer)

    # Location
    sub_district: Mapped[str | None] = mapped_column(Text)
    district: Mapped[str | None] = mapped_column(Text)
    province: Mapped[str | None] = mapped_column(Text, index=True)
    tumbon_id: Mapped[int | None] = mapped_column(Integer)
    amphur_id: Mapped[int | None] = mapped_column(Integer)
    province_id: Mapped[int | None] = mapped_column(Integer)
    lat: Mapped[float | None] = mapped_column(Float)
    lon: Mapped[float | None] = mapped_column(Float)

    # Address
    deed_no: Mapped[str | None] = mapped_column(Text)
    house_no: Mapped[str | None] = mapped_column(Text)
    moo: Mapped[str | None] = mapped_column(Text)
    soi: Mapped[str | None] = mapped_column(Text)
    road: Mapped[str | None] = mapped_column(Text)

    # Media
    image_url: Mapped[str | None] = mapped_column(Text)
    image_ids: Mapped[dict | None] = mapped_column(JSONB)

    # Contact
    contact_person: Mapped[str | None] = mapped_column(Text)
    contact_tel_no: Mapped[str | None] = mapped_column(Text)
    call_telno: Mapped[str | None] = mapped_column(Text)
    branch_code: Mapped[str | None] = mapped_column(Text)
    branch_id: Mapped[int | None] = mapped_column(Integer)

    # Promotion
    promotion_flag: Mapped[int | None] = mapped_column(Integer)
    promotion_id: Mapped[int | None] = mapped_column(Integer)
    promotion_name: Mapped[str | None] = mapped_column(Text)

    # Auction
    bid_online_flag: Mapped[str | None] = mapped_column(Text)
    bid_date: Mapped[str | None] = mapped_column(Text)
    event_type: Mapped[str | None] = mapped_column(Text)
    booking_flag: Mapped[str | None] = mapped_column(Text)
    booking_url: Mapped[str | None] = mapped_column(Text)
    contact_url: Mapped[str | None] = mapped_column(Text)
    share_url: Mapped[str | None] = mapped_column(Text)

    # Status
    property_active_flag: Mapped[int | None] = mapped_column(Integer)
    property_status: Mapped[str | None] = mapped_column(Text)
    status: Mapped[int | None] = mapped_column(Integer)

    # Text
    description: Mapped[str | None] = mapped_column(Text)
    floor_info: Mapped[str | None] = mapped_column(Text)

    # Dates (from API)
    ghb_created_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    ghb_modified_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Engagement
    view_count: Mapped[int | None] = mapped_column(Integer)
    order_no: Mapped[int | None] = mapped_column(Integer)

    # Scraper metadata
    first_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    last_scraped_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    has_detail: Mapped[bool] = mapped_column(Boolean, server_default="false")

    # Full raw responses
    raw_api_json: Mapped[dict | None] = mapped_column(JSONB)
    raw_detail_fields: Mapped[dict | None] = mapped_column(JSONB)

    __table_args__ = (
        UniqueConstraint("property_no", name="uq_ghb_property_no"),
        Index("ix_ghb_province", "province"),
        Index("ix_ghb_property_type", "property_type"),
        Index("ix_ghb_type_id", "type_id"),
        Index("ix_ghb_price_amt", "price_amt"),
        Index("ix_ghb_location", "province", "district"),
        Index("ix_ghb_promotion", "promotion_id"),
    )


class GhbPriceHistory(Base):
    __tablename__ = "ghb_price_history"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    property_id: Mapped[int] = mapped_column(Integer, index=True)

    price_amt: Mapped[int | None] = mapped_column(Numeric(14, 0))
    promotion_price_amt: Mapped[int | None] = mapped_column(Numeric(14, 0))
    begin_auction_price: Mapped[int | None] = mapped_column(Numeric(14, 0))

    # new, price_change, status_change
    change_type: Mapped[str] = mapped_column(String(20))

    scraped_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (
        Index("ix_ghb_ph_prop_date", "property_id", "scraped_at"),
    )


class GhbScrapeLog(Base):
    __tablename__ = "ghb_scrape_logs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    phase: Mapped[str | None] = mapped_column(String(20))  # listing, detail, full
    total_pages: Mapped[int | None] = mapped_column(Integer)
    total_properties: Mapped[int | None] = mapped_column(Integer)
    new_count: Mapped[int | None] = mapped_column(Integer)
    updated_count: Mapped[int | None] = mapped_column(Integer)
    price_changed_count: Mapped[int | None] = mapped_column(Integer)
    status_changed_count: Mapped[int | None] = mapped_column(Integer)
    failed_pages: Mapped[int | None] = mapped_column(Integer)
    failed_details: Mapped[int | None] = mapped_column(Integer)
    error: Mapped[str | None] = mapped_column(Text)
    provinces_scraped: Mapped[str | None] = mapped_column(Text)

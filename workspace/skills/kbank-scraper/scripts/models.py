"""
KBank NPA Scraper — Pydantic v2 + SQLAlchemy 2.0 models.

Prices stored in whole baht (Numeric).
List API provides 40 fields per item. Detail page adds deed/address/nearby.
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
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


# ---------------------------------------------------------------------------
# Pydantic models (parsing layer)
# ---------------------------------------------------------------------------


class KbankPropertyItem(BaseModel):
    """Parsed property from KBank list API (GetProperties)."""

    # Identity
    property_id: str = Field(alias="PropertyID")
    property_id_format: str | None = Field(None, alias="PropertyIDFormat")
    source_code: str | None = Field(None, alias="SourceCode")
    source_sale_type: str | None = Field(None, alias="SourceSaleType")
    source_image_logo: str | None = Field(None, alias="SourceImageLogo")

    # Location
    province_name: str | None = Field(None, alias="ProvinceName")
    amphur_name: str | None = Field(None, alias="AmphurName")
    tambon_name: str | None = Field(None, alias="TambonName")
    village_th: str | None = Field(None, alias="VillageTH")
    soi_th: str | None = Field(None, alias="SoiTH")
    road_th: str | None = Field(None, alias="RoadTH")
    address_no_th: str | None = Field(None, alias="AddressNoTH")
    building_th: str | None = Field(None, alias="BuildingTH")
    floor_th: str | None = Field(None, alias="FloorTH")
    latitude: str | None = Field(None, alias="Latitude")
    longtitude: str | None = Field(None, alias="Longtitude")  # sic — API typo

    # Property info
    property_type_name: str | None = Field(None, alias="PropertyTypeName")
    asset_info_th: str | None = Field(None, alias="AssetInfoTH")
    bedroom: int | None = Field(None, alias="Bedroom")
    bathroom: int | None = Field(None, alias="Bathroom")
    building_age: int | None = Field(None, alias="BuildingAge")
    useable_area: float | None = Field(None, alias="UseableArea")

    # Land area
    rai: int | float | None = Field(None, alias="Rai")
    ngan: int | float | None = Field(None, alias="Ngan")
    square_area: float | None = Field(None, alias="SquareArea")
    area_value: float | None = Field(None, alias="AreaValue")
    area: str | None = Field(None, alias="Area")

    # Pricing (whole baht)
    sell_price: float | None = Field(None, alias="SellPrice")
    promotion_price: float | None = Field(None, alias="PromotionPrice")
    adjust_price: float | None = Field(None, alias="AdjustPrice")
    promotion_name: str | None = Field(None, alias="PromotionName")
    promotion_remark: str | None = Field(None, alias="PromotionRemark")

    # Status flags
    is_new: bool | None = Field(None, alias="IsNew")
    is_hot: bool | None = Field(None, alias="IsHot")
    is_reserve: bool | None = Field(None, alias="IsReserve")
    is_sold_out: bool | None = Field(None, alias="IsSoldOut")
    ai_flag: bool | None = Field(None, alias="AIFlag")
    pm_maintenance_status: str | None = Field(None, alias="PMMaintenanceStatus")
    ga_score: float | str | None = Field(None, alias="GAScore")

    # Media
    property_mediaes: list[dict] | None = Field(None, alias="PropertyMediaes")

    model_config = {"populate_by_name": True}

    @field_validator("sell_price", "promotion_price", "adjust_price", mode="before")
    @classmethod
    def parse_price(cls, v: Any) -> float | None:
        if v is None or v == "" or v == 0:
            return None
        if isinstance(v, str):
            return float(v.replace(",", ""))
        return float(v)

    def get_lat(self) -> float | None:
        if self.latitude:
            try:
                return float(self.latitude)
            except (ValueError, TypeError):
                return None
        return None

    def get_lon(self) -> float | None:
        if self.longtitude:
            try:
                return float(self.longtitude)
            except (ValueError, TypeError):
                return None
        return None

    def get_property_type_code(self) -> str | None:
        """Extract type code from 'XX ชื่อ' format."""
        if self.property_type_name and len(self.property_type_name) >= 2:
            return self.property_type_name[:2]
        return None


class KbankListResponse(BaseModel):
    """Parsed response from GetProperties (after double JSON parse)."""

    success: bool = Field(alias="Success")
    data: KbankListData | None = Field(None, alias="Data")
    error_message: str | None = Field(None, alias="ErrorMessage")
    error_code: str | None = Field(None, alias="ErrorCode")

    model_config = {"populate_by_name": True}


class KbankListData(BaseModel):
    """Data wrapper inside GetProperties response."""

    total_rows: int = Field(0, alias="TotalRows")
    items: list[dict[str, Any]] = Field(default_factory=list, alias="Items")
    current_page_index: int = Field(0, alias="CurrentPageIndex")
    page_size: int = Field(20, alias="PageSize")

    model_config = {"populate_by_name": True}


# ---------------------------------------------------------------------------
# SQLAlchemy models (database layer)
# ---------------------------------------------------------------------------


class Base(DeclarativeBase):
    pass


class KbankProperty(Base):
    """KBank NPA property — list API data + optional detail enrichment."""

    __tablename__ = "kbank_properties"

    property_id: Mapped[str] = mapped_column(Text, primary_key=True)
    property_id_format: Mapped[str | None] = mapped_column(Text)
    source_code: Mapped[str | None] = mapped_column(Text)
    source_sale_type: Mapped[str | None] = mapped_column(Text)

    # Location
    province_name: Mapped[str | None] = mapped_column(Text, index=True)
    amphur_name: Mapped[str | None] = mapped_column(Text)
    tambon_name: Mapped[str | None] = mapped_column(Text)
    village_th: Mapped[str | None] = mapped_column(Text)
    soi_th: Mapped[str | None] = mapped_column(Text)
    road_th: Mapped[str | None] = mapped_column(Text)
    address_no_th: Mapped[str | None] = mapped_column(Text)
    building_th: Mapped[str | None] = mapped_column(Text)
    floor_th: Mapped[str | None] = mapped_column(Text)
    full_address: Mapped[str | None] = mapped_column(Text)  # from detail page
    lat: Mapped[float | None] = mapped_column(Float)
    lon: Mapped[float | None] = mapped_column(Float)

    # Property info
    property_type_name: Mapped[str | None] = mapped_column(Text)
    property_type_code: Mapped[str | None] = mapped_column(Text, index=True)
    asset_info_th: Mapped[str | None] = mapped_column(Text)
    bedroom: Mapped[int | None] = mapped_column(Integer)
    bathroom: Mapped[int | None] = mapped_column(Integer)
    building_age: Mapped[int | None] = mapped_column(Integer)
    useable_area: Mapped[float | None] = mapped_column(Numeric(12, 2))

    # Land area
    rai: Mapped[float | None] = mapped_column(Numeric(10, 2))
    ngan: Mapped[float | None] = mapped_column(Numeric(10, 2))
    square_area: Mapped[float | None] = mapped_column(Numeric(10, 2))
    area_value: Mapped[float | None] = mapped_column(Numeric(12, 2))
    area: Mapped[str | None] = mapped_column(Text)

    # Pricing (whole baht)
    sell_price: Mapped[float | None] = mapped_column(Numeric(14, 2))
    promotion_price: Mapped[float | None] = mapped_column(Numeric(14, 2))
    adjust_price: Mapped[float | None] = mapped_column(Numeric(14, 2))
    promotion_name: Mapped[str | None] = mapped_column(Text)
    promotion_remark: Mapped[str | None] = mapped_column(Text)

    # Status flags
    is_new: Mapped[bool | None] = mapped_column(Boolean)
    is_hot: Mapped[bool | None] = mapped_column(Boolean)
    is_reserve: Mapped[bool | None] = mapped_column(Boolean)
    is_sold_out: Mapped[bool | None] = mapped_column(Boolean)
    ai_flag: Mapped[bool | None] = mapped_column(Boolean)
    pm_maintenance_status: Mapped[str | None] = mapped_column(Text)

    # Detail page enrichment
    deed_type: Mapped[str | None] = mapped_column(Text)
    deed_number: Mapped[str | None] = mapped_column(Text)
    nearby_places: Mapped[dict | None] = mapped_column(JSONB)
    has_detail: Mapped[bool] = mapped_column(Boolean, server_default="false")

    # Media
    images: Mapped[dict | None] = mapped_column(JSONB)

    # Scraper metadata
    first_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    last_scraped_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    detail_scraped_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Raw JSON for future-proofing
    raw_json: Mapped[dict | None] = mapped_column(JSONB)

    __table_args__ = (
        Index("ix_kbank_province", "province_name"),
        Index("ix_kbank_type", "property_type_code"),
        Index("ix_kbank_sell_price", "sell_price"),
        Index("ix_kbank_location", "province_name", "amphur_name"),
        Index("ix_kbank_sold_out", "is_sold_out"),
    )


class KbankPriceHistory(Base):
    __tablename__ = "kbank_price_history"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    property_id: Mapped[str] = mapped_column(Text, index=True)

    sell_price: Mapped[float | None] = mapped_column(Numeric(14, 2))
    promotion_price: Mapped[float | None] = mapped_column(Numeric(14, 2))
    adjust_price: Mapped[float | None] = mapped_column(Numeric(14, 2))

    change_type: Mapped[str] = mapped_column(String(20))  # new, price_change, status_change

    scraped_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (
        Index("ix_kbank_ph_prop_date", "property_id", "scraped_at"),
    )


class KbankScrapeLog(Base):
    __tablename__ = "kbank_scrape_logs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    total_api: Mapped[int | None] = mapped_column(Integer)
    total_pages: Mapped[int | None] = mapped_column(Integer)
    new_count: Mapped[int | None] = mapped_column(Integer)
    updated_count: Mapped[int | None] = mapped_column(Integer)
    price_changed_count: Mapped[int | None] = mapped_column(Integer)
    status_changed_count: Mapped[int | None] = mapped_column(Integer)
    failed_pages: Mapped[int | None] = mapped_column(Integer)
    error: Mapped[str | None] = mapped_column(Text)
    filter_used: Mapped[str | None] = mapped_column(Text)

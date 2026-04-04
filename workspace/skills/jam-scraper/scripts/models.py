"""
JAM Scraper — Pydantic v2 + SQLAlchemy 2.0 models.

Prices stored in whole baht (Numeric), not satang.
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

class JamPropertyParsed(BaseModel):
    """Parsed property from JAM API list endpoint."""

    asset_id: int = Field(alias="Asset_ID")
    borr_code: str | None = Field(None, alias="Borr_Code")
    asset_no: str | None = Field(None, alias="Asset_No")

    # Classification
    type_sale_code: str | None = Field(None, alias="Type_Sale_Code")
    type_sale_th: str | None = Field(None, alias="Type_Sale_TH")
    type_asset_code: str | None = Field(None, alias="Type_Asset_Code")
    type_asset_th: str | None = Field(None, alias="Type_Asset_TH")

    # Project
    project_th: str | None = Field(None, alias="Project_TH")
    project_en: str | None = Field(None, alias="Project_EN")

    # Location
    province: str | None = Field(None, alias="Province")
    district: str | None = Field(None, alias="District")
    subdistrict: str | None = Field(None, alias="SubDistrict")
    province_name: str | None = Field(None, alias="PROVINCE_NAME")
    amphur_name: str | None = Field(None, alias="AMPHUR_NAME")
    district_name: str | None = Field(None, alias="DISTRICT_NAME")
    lat: float | None = Field(None, alias="Lat")
    lon: float | None = Field(None, alias="Lon")
    soi: str | None = Field(None, alias="Soi")
    road: str | None = Field(None, alias="Road")

    # Size
    wah: float | None = Field(None, alias="Wah")
    meter: float | None = Field(None, alias="Meter")
    bedroom: int | None = Field(None, alias="Bedroom")
    bathroom: int | None = Field(None, alias="Bathroom")
    floor: str | None = Field(None, alias="Floor")

    # Pricing (whole baht)
    selling: float | None = Field(None, alias="Selling")
    discount: float | None = Field(None, alias="Discount")
    rental: float | None = Field(None, alias="Rental")

    # Status
    status_soldout: bool | None = Field(None, alias="Status_Soldout")
    soldout_date: str | None = Field(None, alias="Soldout_date")
    status_acution: int | None = Field(None, alias="Status_Acution")
    status_hotdeal: bool | None = Field(None, alias="Status_Hotdeal")
    is_flash_sale: bool | None = Field(None, alias="isFlashSale")

    # Company / Agent
    company_code: str | None = Field(None, alias="Company_Code")
    company_th: str | None = Field(None, alias="Company_TH")
    user_code: str | None = Field(None, alias="User_Code")

    # Images
    images_main_web: str | None = Field(None, alias="Images_Main_Web")
    image_sold_out: str | None = Field(None, alias="Image_Sold_Out")

    # Dates
    save_date: str | None = Field(None, alias="Save_date")
    update_date: str | None = Field(None, alias="Update_date")

    # Engagement
    total_view: int | None = Field(None, alias="TotalView")
    total_like: int | None = Field(None, alias="TotalLike")
    total_bookmark: int | None = Field(None, alias="TotalBookmark")

    # Raw JSON for future-proofing
    raw_json: dict[str, Any] = Field(default_factory=dict)

    model_config = {"populate_by_name": True}

    @field_validator("selling", "discount", "rental", mode="before")
    @classmethod
    def parse_price(cls, v: Any) -> float | None:
        if v is None or v == "" or v == 0:
            return None
        if isinstance(v, str):
            return float(v.replace(",", ""))
        return float(v)

    @field_validator("status_soldout", "status_hotdeal", "is_flash_sale", mode="before")
    @classmethod
    def parse_bool(cls, v: Any) -> bool | None:
        if v is None:
            return None
        if isinstance(v, bool):
            return v
        if isinstance(v, (int, float)):
            return bool(v)
        return None


# ---------------------------------------------------------------------------
# SQLAlchemy models (database layer)
# ---------------------------------------------------------------------------

class Base(DeclarativeBase):
    pass


class JamProperty(Base):
    __tablename__ = "jam_properties"

    asset_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    borr_code: Mapped[str | None] = mapped_column(String(50))
    asset_no: Mapped[str | None] = mapped_column(String(50))

    # Classification
    type_sale_code: Mapped[str | None] = mapped_column(String(10))
    type_sale_th: Mapped[str | None] = mapped_column(String(50))
    type_asset_code: Mapped[str | None] = mapped_column(String(10))
    type_asset_th: Mapped[str | None] = mapped_column(String(100))

    # Project
    project_th: Mapped[str | None] = mapped_column(Text)
    project_en: Mapped[str | None] = mapped_column(Text)

    # Location
    province: Mapped[str | None] = mapped_column(String(10))
    district: Mapped[str | None] = mapped_column(String(10))
    subdistrict: Mapped[str | None] = mapped_column(String(10))
    province_name: Mapped[str | None] = mapped_column(String(100))
    amphur_name: Mapped[str | None] = mapped_column(String(100))
    district_name: Mapped[str | None] = mapped_column(String(100))
    lat: Mapped[float | None] = mapped_column(Float)
    lon: Mapped[float | None] = mapped_column(Float)
    soi: Mapped[str | None] = mapped_column(Text)
    road: Mapped[str | None] = mapped_column(Text)

    # Size
    wah: Mapped[float | None] = mapped_column(Numeric(12, 2))
    meter: Mapped[float | None] = mapped_column(Numeric(12, 2))
    bedroom: Mapped[int | None] = mapped_column(Integer)
    bathroom: Mapped[int | None] = mapped_column(Integer)
    floor: Mapped[str | None] = mapped_column(String(20))

    # Pricing (whole baht)
    selling: Mapped[float | None] = mapped_column(Numeric(14, 2))
    discount: Mapped[float | None] = mapped_column(Numeric(14, 2))
    rental: Mapped[float | None] = mapped_column(Numeric(14, 2))

    # Status
    status_soldout: Mapped[bool | None] = mapped_column(Boolean)
    soldout_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    status_acution: Mapped[int | None] = mapped_column(Integer)
    status_hotdeal: Mapped[bool | None] = mapped_column(Boolean)
    is_flash_sale: Mapped[bool | None] = mapped_column(Boolean)

    # Company
    company_code: Mapped[str | None] = mapped_column(String(10))
    company_th: Mapped[str | None] = mapped_column(String(200))
    user_code: Mapped[str | None] = mapped_column(String(20))

    # Images
    images_main_web: Mapped[str | None] = mapped_column(Text)
    image_sold_out: Mapped[str | None] = mapped_column(Text)

    # Dates from API
    save_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    update_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Engagement
    total_view: Mapped[int | None] = mapped_column(Integer)
    total_like: Mapped[int | None] = mapped_column(Integer)
    total_bookmark: Mapped[int | None] = mapped_column(Integer)

    # Scraper metadata
    first_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    last_scraped_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Full API response for future-proofing
    raw_json: Mapped[dict | None] = mapped_column(JSONB)

    __table_args__ = (
        Index("ix_jam_province", "province"),
        Index("ix_jam_type_asset", "type_asset_code"),
        Index("ix_jam_type_sale", "type_sale_code"),
        Index("ix_jam_soldout", "status_soldout"),
        Index("ix_jam_selling", "selling"),
        Index("ix_jam_location", "province", "district"),
        Index("ix_jam_company", "company_code"),
    )


class JamPriceHistory(Base):
    __tablename__ = "jam_price_history"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    asset_id: Mapped[int] = mapped_column(Integer, index=True)

    selling: Mapped[float | None] = mapped_column(Numeric(14, 2))
    discount: Mapped[float | None] = mapped_column(Numeric(14, 2))
    rental: Mapped[float | None] = mapped_column(Numeric(14, 2))

    # new = first time seen, price_change = price changed, sold = became soldout, unsold = was sold now active
    change_type: Mapped[str] = mapped_column(String(20))

    scraped_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (
        Index("ix_jam_ph_asset_date", "asset_id", "scraped_at"),
    )


class JamScrapeLog(Base):
    __tablename__ = "jam_scrape_logs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    total_api: Mapped[int | None] = mapped_column(Integer)
    new_count: Mapped[int | None] = mapped_column(Integer)
    updated_count: Mapped[int | None] = mapped_column(Integer)
    sold_count: Mapped[int | None] = mapped_column(Integer)
    failed_pages: Mapped[int | None] = mapped_column(Integer)
    error: Mapped[str | None] = mapped_column(Text)

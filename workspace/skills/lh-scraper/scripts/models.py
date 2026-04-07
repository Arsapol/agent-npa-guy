"""
LH Bank NPA Scraper -- Pydantic v2 + SQLAlchemy 2.0 models.

Prices stored in whole baht (Numeric).
Source: HTML scraping from lhbank.co.th (Kentico CMS, no JSON API).
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field
from sqlalchemy import (
    BigInteger,
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


class LHListItem(BaseModel):
    """Parsed property card from the listing page."""

    asset_code: str
    asset_param: str = "1"
    asset_type: str = ""
    area_text: str = ""
    price: int | None = None
    address: str = ""
    thumbnail: str = ""
    detail_url: str = ""


class LHDetail(BaseModel):
    """Parsed property detail page."""

    asset_code: str = ""
    asking_price: int | None = None
    case_info: str = ""
    status_desc: str = ""
    asset_type: str = ""
    location: str = ""
    area_text: str = ""
    record_date: str = ""
    latitude: float | None = None
    longitude: float | None = None
    map_image_url: str = ""
    pdf_url: str = ""
    image_urls: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Area parsing helpers
# ---------------------------------------------------------------------------

_AREA_RE = re.compile(r"(\d+)-(\d+)-([\d.]+)\s*(.*)")


def parse_area_sqm(area_text: str) -> float | None:
    """Parse LH area text to square meters (for condos) or square wah."""
    m = _AREA_RE.match(area_text.strip())
    if not m:
        return None
    rai = int(m.group(1))
    ngan = int(m.group(2))
    wah = float(m.group(3))
    unit = m.group(4).strip()

    if "ตารางเมตร" in unit:
        return wah  # for condos: 0-0-46.50 ตารางเมตร = 46.50 sqm
    # Convert to sq.wah total
    return rai * 400 + ngan * 100 + wah


# ---------------------------------------------------------------------------
# SQLAlchemy models (database layer)
# ---------------------------------------------------------------------------


class Base(DeclarativeBase):
    pass


class LHProperty(Base):
    """LH Bank NPA property."""

    __tablename__ = "lh_properties"

    property_id: Mapped[str] = mapped_column(Text, primary_key=True)  # AssetCode e.g. LH031A

    # Classification
    asset_type: Mapped[str | None] = mapped_column(Text, index=True)
    case_info: Mapped[str | None] = mapped_column(Text)

    # Pricing (whole baht)
    sale_price: Mapped[float | None] = mapped_column(Numeric(14, 2))

    # Location
    address: Mapped[str | None] = mapped_column(Text)
    location_text: Mapped[str | None] = mapped_column(Text)  # short address from card
    lat: Mapped[float | None] = mapped_column(Float)
    lon: Mapped[float | None] = mapped_column(Float)

    # Size
    area_text: Mapped[str | None] = mapped_column(Text)  # raw: 0-0-46.50 ตารางเมตร
    area_sqm: Mapped[float | None] = mapped_column(Numeric(12, 2))  # parsed numeric

    # Description (free text from lbl_Status)
    description: Mapped[str | None] = mapped_column(Text)

    # Dates
    post_date: Mapped[str | None] = mapped_column(Text)  # raw Thai date text

    # Media
    thumbnail_url: Mapped[str | None] = mapped_column(Text)
    map_image_url: Mapped[str | None] = mapped_column(Text)
    pdf_url: Mapped[str | None] = mapped_column(Text)
    images: Mapped[dict | None] = mapped_column(JSONB)  # list of image URLs

    # Detail page URL
    detail_url: Mapped[str | None] = mapped_column(Text)

    # Scraper metadata
    first_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    last_scraped_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    has_detail: Mapped[bool] = mapped_column(default=False)

    # Raw HTML for future-proofing
    raw_listing: Mapped[dict | None] = mapped_column(JSONB)
    raw_detail: Mapped[dict | None] = mapped_column(JSONB)

    __table_args__ = (
        Index("ix_lh_sale_price", "sale_price"),
        Index("ix_lh_asset_type", "asset_type"),
    )


class LHPriceHistory(Base):
    __tablename__ = "lh_price_history"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    property_id: Mapped[str] = mapped_column(Text, index=True)  # FK to lh_properties

    sale_price: Mapped[float | None] = mapped_column(Numeric(14, 2))

    # new, price_change
    change_type: Mapped[str] = mapped_column(String(20))

    scraped_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (
        Index("ix_lh_ph_prop_date", "property_id", "scraped_at"),
    )


class LHScrapeLog(Base):
    __tablename__ = "lh_scrape_logs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    total_listing: Mapped[int | None] = mapped_column(Integer)
    total_detail: Mapped[int | None] = mapped_column(Integer)
    new_count: Mapped[int | None] = mapped_column(Integer)
    updated_count: Mapped[int | None] = mapped_column(Integer)
    price_changed_count: Mapped[int | None] = mapped_column(Integer)
    failed_details: Mapped[int | None] = mapped_column(Integer)
    error: Mapped[str | None] = mapped_column(Text)

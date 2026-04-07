"""
SCB NPA Scraper — Pydantic v2 + SQLAlchemy 2.0 models.

Prices stored in whole baht (Numeric).
Two data sources: JSON search API + HTML detail page.
"""

from __future__ import annotations

import re
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


class ScbAssetSearch(BaseModel):
    """Parsed property from SCB search API (get_project command)."""

    project_id: int
    project_type: str | None = None
    project_title: str | None = None
    price: str | None = None
    price_discount: str | None = None
    project_address_detail: str | None = None
    image_project: str | None = None
    image_project_gen: str | None = None
    project_recommended: str | None = None
    project_sold_out: str | None = None
    project_booking: str | None = None
    project_hide: str | None = None
    project_id_gen: str | None = None
    owner_email: str | None = None
    slug: str | None = None
    promotion_description: str | None = None
    promotion_start_date: str | None = None
    promotion_end_date: str | None = None
    latitude: str | None = None
    longitude: str | None = None
    contact_download_map: str | None = None
    contact_download_map_gen: str | None = None
    category_find_home: str | int | None = None
    category_find_loan: str | int | None = None
    category_find_exchange: str | int | None = None
    create_date: str | None = None
    district_id: int | str | None = None
    province_id: int | str | None = None
    area_use: str | None = None
    land_area: str | None = None
    area_sqm: float | str | None = None
    image_use: str | None = None
    project_type_name: str | None = None
    total_favorite: int | str | None = None
    total_booking: int | str | None = None
    data_location: list | str | None = None
    project_new: str | None = None
    project_address: str | None = None
    promotion_status: str | None = None

    raw_json: dict[str, Any] = Field(default_factory=dict)

    model_config = {"populate_by_name": True}

    def get_price_baht(self) -> float | None:
        return _parse_comma_price(self.price)

    def get_discount_price_baht(self) -> float | None:
        val = _parse_comma_price(self.price_discount)
        return val if val and val > 0 else None

    def get_lat(self) -> float | None:
        return _safe_float(self.latitude)

    def get_lon(self) -> float | None:
        return _safe_float(self.longitude)

    def get_area_use_sqm(self) -> float | None:
        return _safe_float(self.area_use)

    def get_land_area_sqw(self) -> float | None:
        return _safe_float(self.land_area)


class ScbAssetDetail(BaseModel):
    """Parsed property from SCB detail HTML page."""

    project_id: int
    asset_code: str | None = None
    project_type: str | None = None
    title_deed: str | None = None
    land_area_text: str | None = None
    usable_area_text: str | None = None
    bedrooms: int | None = None
    bathrooms: int | None = None
    parking: int | None = None
    description: str | None = None
    sold_out: str | None = None
    images: list[str] = Field(default_factory=list)

    model_config = {"populate_by_name": True}


class ScbSearchResponse(BaseModel):
    """Top-level search API response."""

    s: str = ""
    m: str = ""
    d: list[dict[str, Any]] = Field(default_factory=list)
    total: int = 0

    model_config = {"populate_by_name": True}


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------


def _parse_comma_price(val: str | None) -> float | None:
    if not val:
        return None
    cleaned = val.replace(",", "").strip()
    if not cleaned or cleaned == "0":
        return None
    try:
        return float(cleaned)
    except (ValueError, TypeError):
        return None


def _safe_float(val: str | float | None) -> float | None:
    if val is None:
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def parse_detail_html(html: str, project_id: int) -> ScbAssetDetail:
    """Parse SCB detail page HTML using selectolax."""
    from selectolax.parser import HTMLParser

    tree = HTMLParser(html)
    detail: dict[str, Any] = {"project_id": project_id}

    # Hidden inputs
    for inp in tree.css("input[type='hidden']"):
        name = inp.attributes.get("name") or inp.attributes.get("id") or ""
        val = inp.attributes.get("value") or ""
        if not name or not val:
            continue
        if name == "txt-project-code":
            detail["asset_code"] = val.strip()
        elif name == "pjt":
            detail["project_type"] = val.strip()
        elif name == "chk-sold-out":
            detail["sold_out"] = val.strip()

    # Parse .project_detailed div
    detail_node = tree.css_first(".project_detailed")
    if detail_node:
        text = detail_node.text(separator=" ")

        m = re.search(r"เอกสารสิทธิ์\s*:\s*(.+?)(?:เนื้อที่|$)", text)
        if m:
            detail["title_deed"] = m.group(1).strip()

        m = re.search(r"เนื้อที่\s*:\s*(.+?)(?:พื้นที่ใช้สอย|$)", text)
        if m:
            detail["land_area_text"] = m.group(1).strip()

        m = re.search(r"พื้นที่ใช้สอย\s*:\s*(.+?)(?:ห้องนอน|$)", text)
        if m:
            detail["usable_area_text"] = m.group(1).strip()

        m = re.search(r"ห้องนอน\s*:\s*(\d+)", text)
        if m:
            detail["bedrooms"] = int(m.group(1))

        m = re.search(r"ห้องน้ำ\s*:\s*(\d+)", text)
        if m:
            detail["bathrooms"] = int(m.group(1))

        m = re.search(r"ที่จอดรถ\s*:\s*(\d+)", text)
        if m:
            detail["parking"] = int(m.group(1))

    # Description
    desc_node = tree.css_first(".project-detail-desc")
    if desc_node:
        detail["description"] = desc_node.text(separator="\n").strip()

    # Images
    images: list[str] = []
    for img in tree.css("img"):
        src = img.attributes.get("src") or img.attributes.get("data-src") or ""
        if "stocks/project" in src:
            if src.startswith("/"):
                src = f"https://asset.home.scb{src}"
            images.append(src)
    detail["images"] = images

    return ScbAssetDetail(**detail)


# ---------------------------------------------------------------------------
# SQLAlchemy models (database layer)
# ---------------------------------------------------------------------------


class Base(DeclarativeBase):
    pass


class ScbProperty(Base):
    """Merged search + detail data for an SCB NPA property."""

    __tablename__ = "scb_properties"

    project_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    project_id_gen: Mapped[str | None] = mapped_column(Text)
    project_type: Mapped[str | None] = mapped_column(Text)
    project_type_name: Mapped[str | None] = mapped_column(Text)
    project_title: Mapped[str | None] = mapped_column(Text)
    slug: Mapped[str | None] = mapped_column(Text)

    # Pricing (whole baht)
    price: Mapped[float | None] = mapped_column(Numeric(14, 2))
    price_discount: Mapped[float | None] = mapped_column(Numeric(14, 2))

    # Location
    province_id: Mapped[int | None] = mapped_column(Integer)
    district_id: Mapped[int | None] = mapped_column(Integer)
    project_address: Mapped[str | None] = mapped_column(Text)
    project_address_detail: Mapped[str | None] = mapped_column(Text)
    data_location: Mapped[dict | None] = mapped_column(JSONB)
    lat: Mapped[float | None] = mapped_column(Float)
    lon: Mapped[float | None] = mapped_column(Float)

    # Size
    area_use: Mapped[float | None] = mapped_column(Numeric(12, 2))
    land_area: Mapped[float | None] = mapped_column(Numeric(12, 2))
    area_sqm: Mapped[float | None] = mapped_column(Numeric(12, 2))

    # Detail fields (from HTML)
    title_deed: Mapped[str | None] = mapped_column(Text)
    bedrooms: Mapped[int | None] = mapped_column(Integer)
    bathrooms: Mapped[int | None] = mapped_column(Integer)
    parking: Mapped[int | None] = mapped_column(Integer)
    description: Mapped[str | None] = mapped_column(Text)

    # Promotion
    promotion_description: Mapped[str | None] = mapped_column(Text)
    promotion_status: Mapped[str | None] = mapped_column(Text)
    promotion_start_date: Mapped[str | None] = mapped_column(Text)
    promotion_end_date: Mapped[str | None] = mapped_column(Text)

    # Status flags
    project_sold_out: Mapped[str | None] = mapped_column(Text)
    project_recommended: Mapped[str | None] = mapped_column(Text)
    project_booking: Mapped[str | None] = mapped_column(Text)
    project_hide: Mapped[str | None] = mapped_column(Text)
    project_new: Mapped[str | None] = mapped_column(Text)

    # Engagement
    total_favorite: Mapped[int | None] = mapped_column(Integer)
    total_booking: Mapped[int | None] = mapped_column(Integer)

    # Images
    image_use: Mapped[str | None] = mapped_column(Text)
    images: Mapped[dict | None] = mapped_column(JSONB)

    # Contact
    owner_email: Mapped[str | None] = mapped_column(Text)

    # Dates
    scb_create_date: Mapped[str | None] = mapped_column(Text)

    # Scraper metadata
    first_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    last_scraped_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    has_detail: Mapped[bool] = mapped_column(Boolean, server_default="false")

    # Full API responses for future-proofing
    raw_search_json: Mapped[dict | None] = mapped_column(JSONB)
    raw_detail_json: Mapped[dict | None] = mapped_column(JSONB)

    __table_args__ = (
        Index("ix_scb_province", "province_id"),
        Index("ix_scb_type", "project_type"),
        Index("ix_scb_price", "price"),
        Index("ix_scb_location", "province_id", "district_id"),
        Index("ix_scb_slug", "slug"),
    )


class ScbPriceHistory(Base):
    __tablename__ = "scb_price_history"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(BigInteger, index=True)

    price: Mapped[float | None] = mapped_column(Numeric(14, 2))
    price_discount: Mapped[float | None] = mapped_column(Numeric(14, 2))

    # new, price_change, state_change
    change_type: Mapped[str] = mapped_column(String(20))

    scraped_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (
        Index("ix_scb_ph_project_date", "project_id", "scraped_at"),
    )


class ScbScrapeLog(Base):
    __tablename__ = "scb_scrape_logs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    total_search: Mapped[int | None] = mapped_column(Integer)
    total_detail: Mapped[int | None] = mapped_column(Integer)
    new_count: Mapped[int | None] = mapped_column(Integer)
    updated_count: Mapped[int | None] = mapped_column(Integer)
    price_changed_count: Mapped[int | None] = mapped_column(Integer)
    state_changed_count: Mapped[int | None] = mapped_column(Integer)
    failed_pages: Mapped[int | None] = mapped_column(Integer)
    failed_details: Mapped[int | None] = mapped_column(Integer)
    error: Mapped[str | None] = mapped_column(Text)
    asset_types_scraped: Mapped[str | None] = mapped_column(Text)

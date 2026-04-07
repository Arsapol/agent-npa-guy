"""
TTB/PAMCO Scraper — Pydantic v2 + SQLAlchemy 2.0 models.

Prices stored in whole baht (Numeric).
Two sources: PAMCO (type=3) and TTB (type=4).
List-only architecture — all fields come from the list endpoint.
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


class TtbPropertyItem(BaseModel):
    """Parsed property from TTB/PAMCO list endpoint."""

    id_property: int = Field(alias="idProperty")
    slug: str
    id_market: str = Field(alias="idMarket")
    source_type: int = Field(alias="type")  # 3=PAMCO, 4=TTB

    # Title & classification
    title: str = Field(alias="npaProductTitle")
    id_detail: int | None = Field(None, alias="idDetail")
    detail_name: str | None = None  # parsed from detail.detail
    id_category: int | None = None  # parsed from detail.idCategory

    # Location
    province_id: int | None = Field(None, alias="npaProductProvinceId")
    amphur_id: str | None = Field(None, alias="npaProductAmphurId")
    district_id: str | None = Field(None, alias="npaProductDistrictId")
    province_name: str | None = Field(None, alias="provinceNameTh")
    district_name: str | None = Field(None, alias="districtNameTh")
    sub_district_name: str | None = Field(None, alias="subDistrictNameTh")
    region: str | None = Field(None, alias="Region")

    # GPS
    lat: str | None = Field(None, alias="npaProductLatitude")
    lon: str | None = Field(None, alias="npaProductLongitude")

    # Address
    moo: str | None = None
    soi: str | None = None
    street: str | None = None
    hgroup: str | None = None

    # Size
    area_sqw: str | None = Field(None, alias="npaProductArea")
    search_area: str | None = Field(None, alias="searchArea")
    useable_area: str | None = Field(None, alias="useableArea")
    area_text: str | None = Field(None, alias="area")
    floor: str | None = None

    # Rooms
    bedroom: str | None = Field(None, alias="bedRoom")
    bathroom: str | None = Field(None, alias="bathRoom")
    living_room: str | None = Field(None, alias="livingRoom")
    kitchen: str | None = None
    parlor: str | None = None
    parking: str | None = None

    # Legal
    land_id: str | None = Field(None, alias="landid")
    house_id: str | None = Field(None, alias="houseid")

    # Pricing — extracted from nested arrays
    price: float | None = None  # lowprice[0].lowprice
    no_price: bool = False
    special_price: float | None = None  # idEvent[0].priceSp1
    special_price_start: str | None = None
    special_price_end: str | None = None

    # Contact
    tel_ao: str | None = Field(None, alias="telAO")
    comment: str | None = None
    note_asset: str | None = Field(None, alias="noteAsset")

    # Media
    thumbnail: list[str] | None = None
    illustration: list[str] | None = None
    map_images: list[str] | None = Field(None, alias="map")
    video: str | None = None

    # Nearby
    nearby: list[dict] | None = Field(None, alias="nearBy")

    # Status
    tag: str | None = None
    is_approve: bool | None = Field(None, alias="isApprove")
    investment: str | None = None
    nfr: str | None = None
    status_detail: list[dict] | None = Field(None, alias="statusDetail")

    # Dates
    start_date: str | None = Field(None, alias="startDate")
    end_date: str | None = Field(None, alias="endDate")
    created_datetime: str | None = Field(None, alias="created_datetime")
    updated_datetime: str | None = Field(None, alias="updated_datetime")

    # Raw JSON for future-proofing
    raw_json: dict[str, Any] = Field(default_factory=dict)

    model_config = {"populate_by_name": True}

    @field_validator("price", "special_price", mode="before")
    @classmethod
    def parse_price(cls, v: Any) -> float | None:
        if v is None or v == "" or v == 0:
            return None
        if isinstance(v, str):
            v = v.replace(",", "")
        try:
            return float(v)
        except (ValueError, TypeError):
            return None

    @classmethod
    def from_api(cls, raw: dict[str, Any]) -> TtbPropertyItem:
        """Parse a raw API list item into a TtbPropertyItem."""
        # Extract nested price
        price = None
        no_price = False
        lowprice_list = raw.get("lowprice") or []
        if lowprice_list and isinstance(lowprice_list, list):
            lp = lowprice_list[0]
            if lp.get("noPrice"):
                no_price = True
            else:
                price = lp.get("lowprice")

        # Extract special price from idEvent
        special_price = None
        sp_start = None
        sp_end = None
        events = raw.get("idEvent") or []
        if events and isinstance(events, list):
            ev = events[0]
            if ev.get("active") and ev.get("activePrice"):
                special_price = ev.get("priceSp1")
                sp_start = ev.get("startDate")
                sp_end = ev.get("endDate")

        # Extract detail sub-object
        detail_obj = raw.get("detail") or {}
        detail_name = detail_obj.get("detail")
        id_category = detail_obj.get("idCategory")

        return cls(
            raw_json=raw,
            price=price,
            no_price=no_price,
            special_price=special_price,
            special_price_start=sp_start,
            special_price_end=sp_end,
            detail_name=detail_name,
            id_category=id_category,
            **{k: v for k, v in raw.items()
               if k not in ("lowprice", "idEvent", "detail", "raw_json",
                            "price", "no_price", "special_price",
                            "special_price_start", "special_price_end",
                            "detail_name", "id_category")},
        )

    def get_lat(self) -> float | None:
        if self.lat:
            try:
                return float(self.lat)
            except (ValueError, TypeError):
                pass
        return None

    def get_lon(self) -> float | None:
        if self.lon:
            try:
                return float(self.lon)
            except (ValueError, TypeError):
                pass
        return None


class TtbListResponse(BaseModel):
    """Top-level list API response."""

    total: int = 0
    items: list[dict[str, Any]] = Field(default_factory=list, alias="list")

    model_config = {"populate_by_name": True}


# ---------------------------------------------------------------------------
# SQLAlchemy models (database layer)
# ---------------------------------------------------------------------------


class Base(DeclarativeBase):
    pass


class TtbProperty(Base):
    """TTB/PAMCO NPA property."""

    __tablename__ = "ttb_properties"

    id_property: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(Text)
    id_market: Mapped[str] = mapped_column(Text, unique=True)
    source_type: Mapped[int] = mapped_column(Integer)  # 3=PAMCO, 4=TTB

    # Title & classification
    title: Mapped[str | None] = mapped_column(Text)
    id_detail: Mapped[int | None] = mapped_column(Integer)
    detail_name: Mapped[str | None] = mapped_column(Text)
    id_category: Mapped[int | None] = mapped_column(Integer)

    # Location
    province_id: Mapped[int | None] = mapped_column(Integer)
    amphur_id: Mapped[str | None] = mapped_column(Text)
    district_id: Mapped[str | None] = mapped_column(Text)
    province_name: Mapped[str | None] = mapped_column(Text, index=True)
    district_name: Mapped[str | None] = mapped_column(Text)
    sub_district_name: Mapped[str | None] = mapped_column(Text)
    region: Mapped[str | None] = mapped_column(Text)

    # GPS
    lat: Mapped[float | None] = mapped_column(Float)
    lon: Mapped[float | None] = mapped_column(Float)

    # Address
    moo: Mapped[str | None] = mapped_column(Text)
    soi: Mapped[str | None] = mapped_column(Text)
    street: Mapped[str | None] = mapped_column(Text)
    hgroup: Mapped[str | None] = mapped_column(Text)

    # Size
    area_sqw: Mapped[float | None] = mapped_column(Numeric(12, 2))
    search_area: Mapped[float | None] = mapped_column(Numeric(12, 2))
    useable_area: Mapped[float | None] = mapped_column(Numeric(12, 2))
    area_text: Mapped[str | None] = mapped_column(Text)
    floor: Mapped[str | None] = mapped_column(Text)

    # Rooms
    bedroom: Mapped[str | None] = mapped_column(Text)
    bathroom: Mapped[str | None] = mapped_column(Text)
    living_room: Mapped[str | None] = mapped_column(Text)
    kitchen: Mapped[str | None] = mapped_column(Text)
    parlor: Mapped[str | None] = mapped_column(Text)
    parking: Mapped[str | None] = mapped_column(Text)

    # Legal
    land_id: Mapped[str | None] = mapped_column(Text)
    house_id: Mapped[str | None] = mapped_column(Text)

    # Pricing (whole baht)
    price: Mapped[float | None] = mapped_column(Numeric(14, 2))
    no_price: Mapped[bool] = mapped_column(Boolean, server_default="false")
    special_price: Mapped[float | None] = mapped_column(Numeric(14, 2))
    special_price_start: Mapped[str | None] = mapped_column(Text)
    special_price_end: Mapped[str | None] = mapped_column(Text)

    # Contact
    tel_ao: Mapped[str | None] = mapped_column(Text)
    comment: Mapped[str | None] = mapped_column(Text)
    note_asset: Mapped[str | None] = mapped_column(Text)

    # Media (JSONB)
    thumbnail: Mapped[dict | None] = mapped_column(JSONB)
    illustration: Mapped[dict | None] = mapped_column(JSONB)
    map_images: Mapped[dict | None] = mapped_column(JSONB)
    video: Mapped[str | None] = mapped_column(Text)

    # Nearby (JSONB)
    nearby: Mapped[dict | None] = mapped_column(JSONB)

    # Status
    tag: Mapped[str | None] = mapped_column(Text)
    is_approve: Mapped[bool | None] = mapped_column(Boolean)
    investment: Mapped[str | None] = mapped_column(Text)
    nfr: Mapped[str | None] = mapped_column(Text)
    status_detail: Mapped[dict | None] = mapped_column(JSONB)

    # Dates
    start_date: Mapped[str | None] = mapped_column(Text)
    end_date: Mapped[str | None] = mapped_column(Text)
    ttb_created_at: Mapped[str | None] = mapped_column(Text)
    ttb_updated_at: Mapped[str | None] = mapped_column(Text)

    # Scraper metadata
    first_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    last_scraped_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Full API response for future-proofing
    raw_search_json: Mapped[dict | None] = mapped_column(JSONB)

    __table_args__ = (
        Index("ix_ttb_province", "province_name"),
        Index("ix_ttb_source_type", "source_type"),
        Index("ix_ttb_price", "price"),
        Index("ix_ttb_location", "province_name", "district_name"),
        Index("ix_ttb_id_market", "id_market"),
        Index("ix_ttb_id_category", "id_category"),
    )


class TtbPriceHistory(Base):
    __tablename__ = "ttb_price_history"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    property_id: Mapped[int] = mapped_column(Integer, index=True)

    price: Mapped[float | None] = mapped_column(Numeric(14, 2))
    special_price: Mapped[float | None] = mapped_column(Numeric(14, 2))

    change_type: Mapped[str] = mapped_column(String(20))  # new, price_change

    scraped_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (
        Index("ix_ttb_ph_prop_date", "property_id", "scraped_at"),
    )


class TtbScrapeLog(Base):
    __tablename__ = "ttb_scrape_logs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    total_api: Mapped[int | None] = mapped_column(Integer)
    new_count: Mapped[int | None] = mapped_column(Integer)
    updated_count: Mapped[int | None] = mapped_column(Integer)
    price_changed_count: Mapped[int | None] = mapped_column(Integer)
    failed_pages: Mapped[int | None] = mapped_column(Integer)
    error: Mapped[str | None] = mapped_column(Text)

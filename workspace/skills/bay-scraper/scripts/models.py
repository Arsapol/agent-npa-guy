"""
BAY/Krungsri Scraper — Pydantic v2 + SQLAlchemy 2.0 models.

Prices stored in whole baht (Numeric).
Single API source: /Helpers/GetProperties (74 fields per property).
Property codes: X-suffix (houses), Z-suffix (condos), Y-suffix (land/special).
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


class BayProperty(BaseModel):
    """Parsed property from BAY /Helpers/GetProperties endpoint."""

    # Core identity
    code: str
    item_id: int | None = Field(None, alias="itemID")
    item_guid: str | None = Field(None, alias="itemGUID")
    ou: str | None = None
    ou_name: str | None = Field(None, alias="ouName")

    # Property details
    property_type: str | None = Field(None, alias="propertyType")
    property_type_name: str | None = Field(None, alias="propertyTypeName")
    property_type_object: dict | None = Field(None, alias="propertyTypeObject")
    property_category_object: dict | None = Field(None, alias="propertyCategoryObject")
    project: str | None = None
    project_en: str | None = Field(None, alias="project_EN")
    detail: str | None = None
    detail_en: str | None = Field(None, alias="detail_EN")
    display_text: str | None = Field(None, alias="displayText")
    is_condo: bool = Field(False, alias="isCondo")

    # Location
    lati: str | None = None
    long: str | None = None
    subdistrict: str | None = None
    subdistrict_en: str | None = Field(None, alias="subdistrict_EN")
    district: str | None = None
    district_en: str | None = Field(None, alias="district_EN")
    province: str | None = None
    province_en: str | None = Field(None, alias="province_EN")
    default_address: str | None = Field(None, alias="defaultAddress")

    # Size
    land_size_rai: float | None = Field(None, alias="landSizeRai")
    land_size_ngan: float | None = Field(None, alias="landSizeNgan")
    land_size_sq_wa: float | None = Field(None, alias="landSizeSqWa")
    land_size_total_sq_wa: float | None = Field(None, alias="landSizeTotalSqWa")
    size_sq_meter: float | None = Field(None, alias="sizeSqMeter")
    room_width: float | None = Field(None, alias="roomWidth")
    room_deepth: float | None = Field(None, alias="roomDeepth")
    size_text: str | None = Field(None, alias="sizeText")

    # Pricing (THB)
    sale_price: float | None = Field(None, alias="salePrice")
    promo_price: float | None = Field(None, alias="promoPrice")
    discount: float | None = None
    final_price: float | None = Field(None, alias="finalPrice")

    # Title deed
    deed_no: str | None = Field(None, alias="deedNo")
    deed_no_en: str | None = Field(None, alias="deedNo_EN")
    owner: str | None = None
    owner_en: str | None = Field(None, alias="owner_EN")

    # Building details
    bed_count: int | None = Field(None, alias="bedCount")
    bath_count: int | None = Field(None, alias="bathCount")
    park_count: int | None = Field(None, alias="parkCount")
    flag_fitness: bool | None = Field(None, alias="flagFitness")
    flag_swim: bool | None = Field(None, alias="flagSwim")
    flag_security: bool | None = Field(None, alias="flagSecurity")
    flag_shop: bool | None = Field(None, alias="flagShop")
    flag_lift: bool | None = Field(None, alias="flagLift")

    # Status & dates
    public: bool | None = None
    sale_status: str | None = Field(None, alias="saleStatus")
    status_remark: str | None = Field(None, alias="statusRemark")
    begin_date: str | None = Field(None, alias="beginDate")
    end_date: str | None = Field(None, alias="endDate")
    flag_highlight: bool | None = Field(None, alias="flagHighlight")
    flag_promo: bool | None = Field(None, alias="flagPromo")

    # Contact
    sale_name: str | None = Field(None, alias="saleName")
    sale_name_en: str | None = Field(None, alias="saleName_EN")
    sale_contact: str | None = Field(None, alias="saleContact")

    # Images
    cover_image_url: str | None = Field(None, alias="coverImageUrl")
    list_gallerrry_image: list | None = Field(None, alias="listGallerryImage")
    list_cover_images: list | None = Field(None, alias="listCoverImages")
    list_other_images: list | None = Field(None, alias="listOtherImages")
    list_document_image: list | None = Field(None, alias="listDocumentImage")
    list_map_image: list | None = Field(None, alias="listMapImage")
    vdo_url: str | None = Field(None, alias="vdoURL")

    # Metadata
    page_view: int | None = Field(None, alias="pageView")
    item_created_by: int | None = Field(None, alias="itemCreatedBy")
    item_created_when: str | None = Field(None, alias="itemCreatedWhen")
    item_modified_by: int | None = Field(None, alias="itemModifiedBy")
    item_modified_when: str | None = Field(None, alias="itemModifiedWhen")
    item_order: int | None = Field(None, alias="itemOrder")

    # Raw JSON for future-proofing
    raw_json: dict[str, Any] = Field(default_factory=dict)

    model_config = {"populate_by_name": True}

    @field_validator(
        "sale_price", "promo_price", "final_price", "discount",
        mode="before",
    )
    @classmethod
    def parse_price(cls, v: Any) -> float | None:
        if v is None or v == "" or v == 0:
            return None
        if isinstance(v, str):
            return float(v.replace(",", ""))
        return float(v)

    def get_lat(self) -> float | None:
        if self.lati:
            try:
                return float(self.lati)
            except (ValueError, TypeError):
                return None
        return None

    def get_lon(self) -> float | None:
        if self.long:
            try:
                return float(self.long)
            except (ValueError, TypeError):
                return None
        return None

    def get_category_code(self) -> str | None:
        if self.property_category_object and "code" in self.property_category_object:
            return self.property_category_object["code"]
        return None


# ---------------------------------------------------------------------------
# SQLAlchemy models (database layer)
# ---------------------------------------------------------------------------


class Base(DeclarativeBase):
    pass


class BayPropertyDB(Base):
    """BAY NPA property stored in PostgreSQL."""

    __tablename__ = "bay_properties"

    code: Mapped[str] = mapped_column(Text, primary_key=True)
    item_id: Mapped[int | None] = mapped_column(Integer)
    item_guid: Mapped[str | None] = mapped_column(Text)
    ou: Mapped[str | None] = mapped_column(Text)

    # Property details
    property_type: Mapped[str | None] = mapped_column(Text)
    property_type_name: Mapped[str | None] = mapped_column(Text)
    category_code: Mapped[str | None] = mapped_column(Text)
    project: Mapped[str | None] = mapped_column(Text)
    project_en: Mapped[str | None] = mapped_column(Text)
    detail: Mapped[str | None] = mapped_column(Text)
    detail_en: Mapped[str | None] = mapped_column(Text)
    display_text: Mapped[str | None] = mapped_column(Text)
    is_condo: Mapped[bool] = mapped_column(Boolean, server_default="false")

    # Location
    province: Mapped[str | None] = mapped_column(Text, index=True)
    province_en: Mapped[str | None] = mapped_column(Text)
    district: Mapped[str | None] = mapped_column(Text)
    district_en: Mapped[str | None] = mapped_column(Text)
    subdistrict: Mapped[str | None] = mapped_column(Text)
    subdistrict_en: Mapped[str | None] = mapped_column(Text)
    default_address: Mapped[str | None] = mapped_column(Text)
    lat: Mapped[float | None] = mapped_column(Float)
    lon: Mapped[float | None] = mapped_column(Float)

    # Size
    land_size_rai: Mapped[float | None] = mapped_column(Numeric(10, 2))
    land_size_ngan: Mapped[float | None] = mapped_column(Numeric(10, 2))
    land_size_sq_wa: Mapped[float | None] = mapped_column(Numeric(10, 2))
    land_size_total_sq_wa: Mapped[float | None] = mapped_column(Numeric(10, 2))
    size_sq_meter: Mapped[float | None] = mapped_column(Numeric(12, 2))
    room_width: Mapped[float | None] = mapped_column(Numeric(8, 2))
    room_depth: Mapped[float | None] = mapped_column(Numeric(8, 2))
    size_text: Mapped[str | None] = mapped_column(Text)

    # Pricing (whole baht)
    sale_price: Mapped[float | None] = mapped_column(Numeric(14, 2))
    promo_price: Mapped[float | None] = mapped_column(Numeric(14, 2))
    final_price: Mapped[float | None] = mapped_column(Numeric(14, 2))
    discount_pct: Mapped[float | None] = mapped_column(Numeric(6, 2))

    # Title deed
    deed_no: Mapped[str | None] = mapped_column(Text)
    deed_no_en: Mapped[str | None] = mapped_column(Text)
    owner: Mapped[str | None] = mapped_column(Text)
    owner_en: Mapped[str | None] = mapped_column(Text)

    # Building details
    bed_count: Mapped[int | None] = mapped_column(Integer)
    bath_count: Mapped[int | None] = mapped_column(Integer)
    park_count: Mapped[int | None] = mapped_column(Integer)
    flag_fitness: Mapped[bool | None] = mapped_column(Boolean)
    flag_swim: Mapped[bool | None] = mapped_column(Boolean)
    flag_security: Mapped[bool | None] = mapped_column(Boolean)
    flag_shop: Mapped[bool | None] = mapped_column(Boolean)
    flag_lift: Mapped[bool | None] = mapped_column(Boolean)

    # Status
    sale_status: Mapped[str | None] = mapped_column(Text)
    status_remark: Mapped[str | None] = mapped_column(Text)
    is_public: Mapped[bool | None] = mapped_column(Boolean)
    flag_highlight: Mapped[bool | None] = mapped_column(Boolean)
    flag_promo: Mapped[bool | None] = mapped_column(Boolean)

    # Contact
    sale_name: Mapped[str | None] = mapped_column(Text)
    sale_name_en: Mapped[str | None] = mapped_column(Text)
    sale_contact: Mapped[str | None] = mapped_column(Text)

    # Images
    cover_image_url: Mapped[str | None] = mapped_column(Text)

    # Dates (from API)
    begin_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    end_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    item_created_when: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    item_modified_when: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Engagement
    page_view: Mapped[int | None] = mapped_column(Integer)

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
        Index("ix_bay_province", "province"),
        Index("ix_bay_property_type", "property_type_name"),
        Index("ix_bay_category", "category_code"),
        Index("ix_bay_sale_price", "sale_price"),
        Index("ix_bay_is_condo", "is_condo"),
        Index("ix_bay_location", "province", "district"),
    )


class BayPriceHistory(Base):
    __tablename__ = "bay_price_history"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    property_code: Mapped[str] = mapped_column(Text, index=True)

    sale_price: Mapped[float | None] = mapped_column(Numeric(14, 2))
    promo_price: Mapped[float | None] = mapped_column(Numeric(14, 2))
    final_price: Mapped[float | None] = mapped_column(Numeric(14, 2))
    discount_pct: Mapped[float | None] = mapped_column(Numeric(6, 2))

    change_type: Mapped[str] = mapped_column(String(20))  # new, price_change

    scraped_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (
        Index("ix_bay_ph_code_date", "property_code", "scraped_at"),
    )


class BayScrapeLog(Base):
    __tablename__ = "bay_scrape_logs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    total_codes_discovered: Mapped[int | None] = mapped_column(Integer)
    total_fetched: Mapped[int | None] = mapped_column(Integer)
    new_count: Mapped[int | None] = mapped_column(Integer)
    updated_count: Mapped[int | None] = mapped_column(Integer)
    price_changed_count: Mapped[int | None] = mapped_column(Integer)
    failed_batches: Mapped[int | None] = mapped_column(Integer)
    error: Mapped[str | None] = mapped_column(Text)

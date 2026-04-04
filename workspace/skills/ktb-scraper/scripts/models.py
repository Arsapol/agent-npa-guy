"""
KTB Scraper — Pydantic v2 + SQLAlchemy 2.0 models.

Prices stored in whole baht (Numeric).
Two API sources merged: searchAll + searchSaleDetail.
collGrpId is the primary key (property group ID).
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


class KtbSearchItem(BaseModel):
    """Parsed property from KTB searchAll endpoint."""

    coll_grp_id: int = Field(alias="collGrpId")
    coll_id: int | None = Field(None, alias="collId")

    # Location
    shr_province_name: str | None = Field(None, alias="shrProvinceName")
    shr_amphur_name: str | None = Field(None, alias="shrAmphurName")
    shr_tambon_name: str | None = Field(None, alias="shrTambonName")
    shr_province_no: str | None = Field(None, alias="shrProvinceNo")
    addr: str | None = None
    road: str | None = None
    shr_addrline1: str | None = Field(None, alias="shrAddrline1")
    shr_addrline2: str | None = Field(None, alias="shrAddrline2")
    lat: str | None = None
    lon: str | None = None

    # Classification
    coll_type_name: str | None = Field(None, alias="collTypeName")
    coll_cate_name: str | None = Field(None, alias="collCateName")
    coll_cate_no: int | None = Field(None, alias="collCateNo")
    coll_desc: str | None = Field(None, alias="collDesc")
    asset_type: str | None = Field(None, alias="assetType")
    asset_type_detail: str | None = Field(None, alias="assetTypeDetail")

    # Codes
    coll_code: str | None = Field(None, alias="collCode")
    coll_mono_code: str | None = Field(None, alias="collMonoCode")
    coll_mono_code_all: str | None = Field(None, alias="collMonoCodeAll")
    coll_t_id: str | None = Field(None, alias="collTId")
    ref_code: str | None = Field(None, alias="refCode")
    org_code: str | None = Field(None, alias="orgCode")
    led_mkt_coll_id: str | None = Field(None, alias="ledMktCollId")

    # Pricing (whole baht)
    nml_price: str | None = Field(None, alias="nmlPrice")
    price: str | None = None
    price_number: str | None = Field(None, alias="priceNumber")
    extra_price: str | None = Field(None, alias="extraPrice")
    price_str_dt: str | None = Field(None, alias="priceStrDt")
    price_end_dt: str | None = Field(None, alias="priceEndDt")

    # Sale category
    cate_name: str | None = Field(None, alias="cateName")
    cate_no: int | None = Field(None, alias="cateNo")

    # Flags (API returns int 0/1)
    is_speedy: int | None = Field(None, alias="isSpeedy")
    is_new_asset: int | None = Field(None, alias="isNewAsset")
    is_promotion: int | None = Field(None, alias="isPromotion")
    is_new_pay: int | None = Field(None, alias="isNewPay")
    is_show: str | None = Field(None, alias="isShow")

    # Size
    cal_sum_area_coll_grp_id: str | None = Field(None, alias="calSumAreaCollGrpId")
    area: str | None = None
    sum_area_num: float | None = Field(None, alias="sumAreaNum")
    sum_area_numt: float | None = Field(None, alias="sumAreaNumt")
    bedroom_num: int | None = Field(None, alias="bedroomNum")
    bathroom_num: int | None = Field(None, alias="bathroomNum")

    # Images & media
    file_name: str | None = Field(None, alias="fileName")
    list_img: list[dict] | None = Field(None, alias="listImg")
    link_vdo: str | None = Field(None, alias="linkVdo")
    share_url: str | None = Field(None, alias="shareURL")

    # Occupancy / use
    lodge: str | None = None
    use_for: str | None = Field(None, alias="useFor")
    npl_id: str | None = Field(None, alias="nplId")
    asset_desc: str | None = Field(None, alias="assetDesc")

    # Contact (search-only)
    contact_name: str | None = Field(None, alias="contactName")
    contact_tel: str | None = Field(None, alias="contactTel")

    # Nearby POI (detail-only)
    near_hospital_name: str | None = Field(None, alias="nearHospitalName")
    near_hospital_dist: str | None = Field(None, alias="nearHospitalDist")
    near_school_name: str | None = Field(None, alias="nearSchoolName")
    near_school_dist: str | None = Field(None, alias="nearSchoolDist")
    near_shop_name: str | None = Field(None, alias="nearShopName")
    near_shop_dist: str | None = Field(None, alias="nearShopDist")

    # Price history & analytics
    shr_price_vos: list[dict] | None = Field(None, alias="shrPriceVos")
    percent_year: float | None = Field(None, alias="percentYear")
    percent_year_flag: str | None = Field(None, alias="percentYearFlag")
    percent_min_max: float | None = Field(None, alias="percentMinMax")
    percent_min_max_flag: str | None = Field(None, alias="percentMinMaxFlag")

    # Engagement
    product_count_view: int | None = Field(None, alias="productCountView")
    asset_count: int | None = Field(None, alias="assetCount")

    # LED auction (null for regular NPA)
    open_bidding_price: str | None = Field(None, alias="openBiddingPrice")
    guarantee_amount: str | None = Field(None, alias="guaranteeAmount")

    # Raw JSON for future-proofing
    raw_json: dict[str, Any] = Field(default_factory=dict)

    model_config = {"populate_by_name": True}

    @field_validator("price_number", mode="before")
    @classmethod
    def coerce_price_number(cls, v: Any) -> str | None:
        if v is None:
            return None
        return str(v)

    def get_price_baht(self) -> float | None:
        if not self.price_number:
            return None
        try:
            return float(self.price_number.replace(",", ""))
        except (ValueError, AttributeError):
            return None

    def get_nml_price_baht(self) -> float | None:
        if not self.nml_price:
            return None
        try:
            return float(self.nml_price.replace(",", ""))
        except (ValueError, AttributeError):
            return None

    def get_lat(self) -> float | None:
        if not self.lat:
            return None
        try:
            return float(self.lat)
        except (ValueError, TypeError):
            return None

    def get_lon(self) -> float | None:
        if not self.lon:
            return None
        try:
            return float(self.lon)
        except (ValueError, TypeError):
            return None

    def parse_area(self) -> tuple[float | None, float | None, float | None]:
        """Parse '0-1-35.2' area string into (rai, ngan, wah)."""
        if not self.area:
            return None, None, None
        parts = self.area.split("-")
        if len(parts) != 3:
            return None, None, None
        try:
            return float(parts[0]), float(parts[1]), float(parts[2])
        except ValueError:
            return None, None, None


class KtbSearchResponse(BaseModel):
    """Top-level searchAll API response."""

    data_response: list[dict[str, Any]] = Field(default_factory=list, alias="dataResponse")
    paging: dict[str, Any] = Field(default_factory=dict)

    model_config = {"populate_by_name": True}

    @property
    def total_rows(self) -> int:
        return self.paging.get("totalRows", 0)


# ---------------------------------------------------------------------------
# SQLAlchemy models (database layer)
# ---------------------------------------------------------------------------


class Base(DeclarativeBase):
    pass


class KtbProperty(Base):
    """Merged search + detail data for a KTB NPA property."""

    __tablename__ = "ktb_properties"

    coll_grp_id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # Location
    province: Mapped[str | None] = mapped_column(Text, index=True)
    amphur: Mapped[str | None] = mapped_column(Text)
    tambon: Mapped[str | None] = mapped_column(Text)
    province_no: Mapped[str | None] = mapped_column(Text)
    addr: Mapped[str | None] = mapped_column(Text)
    road: Mapped[str | None] = mapped_column(Text)
    addrline1: Mapped[str | None] = mapped_column(Text)
    addrline2: Mapped[str | None] = mapped_column(Text)
    lat: Mapped[float | None] = mapped_column(Float)
    lon: Mapped[float | None] = mapped_column(Float)

    # Classification
    coll_type_name: Mapped[str | None] = mapped_column(Text)
    coll_cate_name: Mapped[str | None] = mapped_column(Text)
    coll_cate_no: Mapped[int | None] = mapped_column(Integer, index=True)
    coll_desc: Mapped[str | None] = mapped_column(Text)
    asset_type: Mapped[str | None] = mapped_column(Text)

    # Codes
    coll_code: Mapped[str | None] = mapped_column(Text)
    coll_mono_code: Mapped[str | None] = mapped_column(Text)
    coll_mono_code_all: Mapped[str | None] = mapped_column(Text)

    # Pricing (whole baht)
    price: Mapped[float | None] = mapped_column(Numeric(14, 2))
    nml_price: Mapped[float | None] = mapped_column(Numeric(14, 2))

    # Sale category
    cate_name: Mapped[str | None] = mapped_column(Text)
    cate_no: Mapped[int | None] = mapped_column(Integer)

    # Price dates
    price_str_dt: Mapped[str | None] = mapped_column(Text)
    price_end_dt: Mapped[str | None] = mapped_column(Text)

    # Flags
    is_speedy: Mapped[int | None] = mapped_column(Integer)
    is_new_asset: Mapped[int | None] = mapped_column(Integer)
    is_promotion: Mapped[int | None] = mapped_column(Integer)
    is_new_pay: Mapped[int | None] = mapped_column(Integer)

    # Size
    area: Mapped[str | None] = mapped_column(Text)
    rai: Mapped[float | None] = mapped_column(Numeric(10, 2))
    ngan: Mapped[float | None] = mapped_column(Numeric(10, 2))
    wah: Mapped[float | None] = mapped_column(Numeric(10, 2))
    sum_area_num: Mapped[float | None] = mapped_column(Numeric(12, 2))
    bedroom_num: Mapped[int | None] = mapped_column(Integer)
    bathroom_num: Mapped[int | None] = mapped_column(Integer)

    # Images & media
    file_name: Mapped[str | None] = mapped_column(Text)
    list_img: Mapped[dict | None] = mapped_column(JSONB)
    link_vdo: Mapped[str | None] = mapped_column(Text)
    share_url: Mapped[str | None] = mapped_column(Text)

    # Occupancy
    lodge: Mapped[str | None] = mapped_column(Text)

    # Contact
    contact_name: Mapped[str | None] = mapped_column(Text)
    contact_tel: Mapped[str | None] = mapped_column(Text)

    # Nearby POI
    near_hospital_name: Mapped[str | None] = mapped_column(Text)
    near_hospital_dist: Mapped[str | None] = mapped_column(Text)
    near_school_name: Mapped[str | None] = mapped_column(Text)
    near_school_dist: Mapped[str | None] = mapped_column(Text)
    near_shop_name: Mapped[str | None] = mapped_column(Text)
    near_shop_dist: Mapped[str | None] = mapped_column(Text)

    # Price history (year-over-year)
    shr_price_vos: Mapped[dict | None] = mapped_column(JSONB)
    percent_year: Mapped[float | None] = mapped_column(Float)
    percent_year_flag: Mapped[str | None] = mapped_column(Text)

    # Engagement
    product_count_view: Mapped[int | None] = mapped_column(Integer)

    # LED auction fields
    open_bidding_price: Mapped[str | None] = mapped_column(Text)
    guarantee_amount: Mapped[str | None] = mapped_column(Text)

    # Scraper metadata
    has_detail: Mapped[bool] = mapped_column(Boolean, server_default="false")
    first_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    last_scraped_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Full API responses for future-proofing
    raw_search_json: Mapped[dict | None] = mapped_column(JSONB)
    raw_detail_json: Mapped[dict | None] = mapped_column(JSONB)

    __table_args__ = (
        Index("ix_ktb_province", "province"),
        Index("ix_ktb_coll_cate_no", "coll_cate_no"),
        Index("ix_ktb_price", "price"),
        Index("ix_ktb_location", "province", "amphur"),
        Index("ix_ktb_cate_no", "cate_no"),
    )


class KtbPriceHistory(Base):
    __tablename__ = "ktb_price_history"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    coll_grp_id: Mapped[int] = mapped_column(Integer, index=True)

    price: Mapped[float | None] = mapped_column(Numeric(14, 2))
    nml_price: Mapped[float | None] = mapped_column(Numeric(14, 2))
    cate_no: Mapped[int | None] = mapped_column(Integer)
    cate_name: Mapped[str | None] = mapped_column(Text)

    # new, price_change, state_change
    change_type: Mapped[str] = mapped_column(String(20))

    scraped_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (
        Index("ix_ktb_ph_asset_date", "coll_grp_id", "scraped_at"),
    )


class KtbScrapeLog(Base):
    __tablename__ = "ktb_scrape_logs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    total_search: Mapped[int | None] = mapped_column(Integer)
    total_detail: Mapped[int | None] = mapped_column(Integer)
    new_count: Mapped[int | None] = mapped_column(Integer)
    updated_count: Mapped[int | None] = mapped_column(Integer)
    price_changed_count: Mapped[int | None] = mapped_column(Integer)
    category_changed_count: Mapped[int | None] = mapped_column(Integer)
    failed_pages: Mapped[int | None] = mapped_column(Integer)
    failed_details: Mapped[int | None] = mapped_column(Integer)
    error: Mapped[str | None] = mapped_column(Text)

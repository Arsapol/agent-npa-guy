"""
BAM Scraper — Pydantic v2 + SQLAlchemy 2.0 models.

Prices stored in whole baht (Numeric).
Two API sources merged: search endpoint + detail endpoint.
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


class BamAssetSearch(BaseModel):
    """Parsed property from BAM search endpoint."""

    id: int
    asset_no: str | None = Field(None, alias="assetNo")
    asset_state: str | None = Field(None, alias="assetState")

    # Location
    province: str | None = None
    district: str | None = None
    sub_district: str | None = Field(None, alias="subDistrict")

    # Project
    project_th: str | None = Field(None, alias="projectTH")
    project_en: str | None = Field(None, alias="projectEN")

    # Classification
    asset_type: str | None = Field(None, alias="assetType")
    asset_group: str | None = Field(None, alias="assetGroup")
    license_number: str | None = Field(None, alias="licenseNumber")
    mk_code3: str | None = Field(None, alias="mk_code3")
    asset_code: str | None = Field(None, alias="assetCode")

    # Location details
    location: str | None = None
    property_location: str | None = Field(None, alias="propertyLocation")
    nearby: list[str] | None = None

    # Map
    map_data: dict | None = Field(None, alias="map")
    geo_map: dict | None = Field(None, alias="geoMap")

    # Media
    media: dict | None = None

    # Pricing (whole baht)
    sell_price: float | None = Field(None, alias="sellPrice")
    discount_price: float | None = Field(None, alias="discountPrice")
    discount_from_date: str | None = Field(None, alias="discountFromDate")
    discount_to_date: str | None = Field(None, alias="discountToDate")
    display_price: bool | None = Field(None, alias="displayPrice")
    is_shock_price: bool | None = Field(None, alias="isShockPrice")
    shock_price: float | None = Field(None, alias="shockPrice")
    shock_price_condition: str | None = Field(None, alias="shockPriceCondition")
    shock_price_to_date: str | None = Field(None, alias="shockPriceToDate")
    display_speciall_price: bool | None = Field(None, alias="displaySpeciallPrice")
    price_flag: int | None = Field(None, alias="priceFlag")

    # Department / Admin
    department_code: str | None = Field(None, alias="departmentCode")
    department_name: str | None = Field(None, alias="departmentName")
    group_of_department: str | None = Field(None, alias="groupOfDepartment")
    admin_id: str | None = Field(None, alias="adminId")
    admin_name: str | None = Field(None, alias="adminName")
    dept_name: str | None = Field(None, alias="deptName")

    # Conx (concurrent contact)
    admin_id_conx: str | None = Field(None, alias="adminIdConx")
    admin_name_conx: str | None = Field(None, alias="adminNameConx")
    group_of_department_conx: str | None = Field(None, alias="groupOfDepartmentConx")
    department_name_conx: str | None = Field(None, alias="departmentNameConx")
    work_phone_nxt_conx: str | None = Field(None, alias="workPhoneNxtConx")
    work_phone_conx: str | None = Field(None, alias="workPhoneConx")

    # Size
    bedroom: int | None = None
    bathroom: int | None = None
    studio: int | None = None
    parking: int | None = None
    kitchen: int | None = None
    area_meter: str | None = Field(None, alias="areaMeter")
    area_meter_order: float | None = Field(None, alias="areaMeterOrder")
    area_wa: float | None = Field(None, alias="areaWa")
    usable_area: float | None = Field(None, alias="usableArea")
    rai: str | None = None
    ngan: str | None = None
    wa: str | None = None

    # Images
    album_property: list[dict] | None = Field(None, alias="albumProperty")

    # Details
    property_detail: str | None = Field(None, alias="propertyDetail")
    invitation_th: str | None = Field(None, alias="invitationTH")
    favorite: bool | None = None
    display_property: bool | None = Field(None, alias="displayProperty")
    stars: str | None = None
    stars_order: int | None = Field(None, alias="starsOrder")
    high_light: bool | None = Field(None, alias="highLight")
    note: str | None = None
    summary: str | None = None

    # Group property
    group_property: list | None = Field(None, alias="groupProperty")
    group_property_with_link: list | None = Field(None, alias="groupPropertyWithLink")

    # Packages (renovate)
    price_package_1: float | None = Field(None, alias="pricePackage1")
    attchment_package_1: list | None = Field(None, alias="attchmentPackage1")
    detail_package_1: str | None = Field(None, alias="detailPackage1")
    renovate_price_package_1: float | None = Field(None, alias="renovatePricePackage1")
    album_package_1: list | None = Field(None, alias="albumPackage1")
    detail_package_2: str | None = Field(None, alias="detailPackage2")
    attchment_package_2: list | None = Field(None, alias="attchmentPackage2")
    price_package_2: float | None = Field(None, alias="pricePackage2")
    renovate_price_package_2: float | None = Field(None, alias="renovatePricePackage_2")
    album_package_2: list | None = Field(None, alias="albumPackage2")
    detail_package_3: str | None = Field(None, alias="detailPackage3")
    attchment_package_3: list | None = Field(None, alias="attchmentPackage3")
    price_package_3: float | None = Field(None, alias="pricePackage3")
    renovate_price_package_3: float | None = Field(None, alias="renovatePricePackage_3")
    album_package_3: list | None = Field(None, alias="albumPackage3")
    title_renovate: str | None = Field(None, alias="titleRenovate")
    sub_title_renovate: str | None = Field(None, alias="subTitleRenovate")

    # Contact
    work_phone_nxt: str | None = Field(None, alias="workPhoneNxt")
    ref_debt: str | None = Field(None, alias="refDebt")
    telephone: str | None = None
    work_phone: str | None = Field(None, alias="workPhone")

    # Campaign (API returns inconsistent types: int/str/None, list/str/None)
    is_campaign: str | int | None = Field(None, alias="isCampaign")
    campaign_name: str | list | None = Field(None, alias="campaignName")
    campaign_name_th: list | None = Field(None, alias="campaignNameTh")
    campaign_condition: list | None = Field(None, alias="campaignCondition")
    condition: str | None = None

    # Deals / Tags (API returns [] or dict or None)
    hot_deals: dict | list | None = Field(None, alias="hot_deals")
    highlights: dict | list | None = None
    tags: list | None = None
    icons: list | None = None
    is_hot_deal: bool | None = Field(None, alias="isHotDeal")
    subscription_channel: str | None = Field(None, alias="subscriptionChannel")

    # Raw JSON for future-proofing
    raw_json: dict[str, Any] = Field(default_factory=dict)

    model_config = {"populate_by_name": True}

    @field_validator(
        "sell_price", "discount_price", "shock_price",
        "price_package_1", "price_package_2", "price_package_3",
        "renovate_price_package_1", "renovate_price_package_2", "renovate_price_package_3",
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
        if self.geo_map and "lat" in self.geo_map:
            return float(self.geo_map["lat"])
        if self.map_data and "langtitude" in self.map_data:
            return float(self.map_data["langtitude"])
        return None

    def get_lon(self) -> float | None:
        if self.geo_map and "lon" in self.geo_map:
            return float(self.geo_map["lon"])
        if self.map_data and "longtitude" in self.map_data:
            return float(self.map_data["longtitude"])
        return None


class BamAssetDetail(BaseModel):
    """Parsed property from BAM detail endpoint (extra fields not in search)."""

    id: int
    market_code: str | None = None
    asset_state_code: str | None = None
    asset_state: str | None = None

    # Admin
    ao_id: str | None = None
    ao_name: str | None = None
    dept_code: str | None = None
    dept_name: str | None = None
    mom_name: str | None = None
    v_id: str | None = None
    v_name: str | None = None
    m_id: str | None = None
    m_name: str | None = None

    # Classification
    npa_type: str | None = None
    mk_code1: str | None = None
    mk_code2: str | None = None
    mk_code3: str | None = None
    mk_code4: str | None = None
    mk_code5: str | None = None
    col_no: str | None = None
    col_type: str | None = None
    col_typedesc: str | None = None
    col_sub_type: str | None = None
    col_sub_typedesc: str | None = None

    # Location
    add_district: str | None = None
    city_name: str | None = None
    city_expand: str | None = None
    province_name: str | None = None
    physical_zone: str | None = None
    property_location: str | None = None
    location: str | None = None

    # Size
    rai: str | None = None
    ngan: str | None = None
    wa: str | None = None
    area_meter: str | None = None
    usabled_area: str | None = None
    size_build: str | None = None
    bedroom: int | None = None
    bathroom: int | None = None
    studio: int | None = None
    livingroom: int | None = None
    kitchen: int | None = None
    parking: int | None = None

    # Pricing (whole baht, stored as strings in API)
    evaluate_amt: str | None = None
    evaluate_date: str | None = None
    cost_asset_amt: str | None = None
    center_price: str | None = None
    grade: str | None = None
    sale_price_spc_amt: str | None = None
    sale_price_spc_from_date: str | None = None
    sale_price_spc_to_date: str | None = None
    shock_price: float | None = None
    is_shock_price: bool | None = None
    shock_price_condition: str | None = None
    shock_price_from_date: str | None = None
    shock_price_to_date: str | None = None
    maintenance_price: float | None = None

    # Dates
    start_date: str | None = None
    end_date: str | None = None
    sale_date: str | None = None
    key_date: str | None = None
    update_date: str | None = None
    create_date: str | None = None
    modify_date: str | None = None

    # GPS
    gps_lat1: str | None = None
    gps_long1: str | None = None

    # Text
    project_th: str | None = None
    project_en: str | None = None
    invitation_th: str | None = None
    property_detail: str | None = None
    note: str | None = None

    # Images
    album_property: list[dict] | None = None
    image_map: list[dict] | None = None
    image_360: list[dict] | None = None

    # Media
    display_youtube: bool | None = None
    link_youtube: str | None = None
    display_sketchup: bool | None = None
    ember_code_th: str | None = None
    ember_code_en: str | None = None

    # Contact
    telephone: str | None = None
    work_phone: str | None = None
    work_phone_nxt: str | None = None
    ref_debt: str | None = None

    # Nearby
    nearby: list[dict] | None = None

    # Status
    asset_state_pending: str | None = None
    display_price: bool | None = None
    display_special_price: bool | None = None
    display_property: bool | None = None
    status_approve: str | None = None
    status_hidden_property: str | None = None
    is_active: bool | None = Field(None, alias="isActive")
    property_star: str | None = None

    # Group property
    group_property: list | None = None

    # Campaign (API returns inconsistent types)
    is_campaign: str | int | None = None
    campaign_name: str | list | None = None
    is_hot_deal: bool | None = None
    hot_deals: dict | list | None = None
    highlights: dict | list | None = None
    tags: list | None = None
    tag_name: str | None = None
    icons: list | None = None

    # Packages
    title_renovate: str | None = None
    sub_title_renovate: str | None = None
    detail_package_1: str | None = None
    attchment_package_1: list | None = None
    price_package_1: float | None = None
    renovate_price_package_1: float | None = None
    album_package_1: list | None = None
    detail_package_2: str | None = None
    attchment_package_2: list | None = None
    price_package_2: float | None = None
    renovate_price_package_2: float | None = None
    album_package_2: list | None = None
    detail_package_3: str | None = None
    attchment_package_3: list | None = None
    price_package_3: float | None = None
    renovate_price_package_3: float | None = None
    album_package_3: list | None = None

    # Display/misc
    display_property_desc: str | None = None
    display_center_price_startdate: str | None = None
    display_center_price_enddate: str | None = None
    display_center_price_desc: str | None = None
    tmp_display_price: str | None = None
    display_home_condo: str | bool | None = None
    reason_head_sales: str | None = None
    reason_office_market: str | None = None
    reason_head_market: str | None = None

    # Subscription
    expired_subscription_datetime: str | None = None
    last_subscription_user_id: str | None = None
    subscription_channel: str | None = None
    fourth_price_buy_to_date: str | None = None

    # Internal
    internal_record: str | None = None
    response_segment: str | None = None
    property_source: str | None = None
    property_special: str | None = None
    property_highlight: str | bool | None = None
    tracking_log_detail: str | None = None
    reserve_start_date: str | None = None
    reserve_end_date: str | None = None
    date_auction: str | None = None
    document_auction: str | None = None
    license: str | None = None
    asset_code: str | None = None

    # Engagement
    view_count: int | None = None
    datetime_now: int | None = Field(None, alias="datetimeNow")

    model_config = {"populate_by_name": True}


class BamSearchResponse(BaseModel):
    """Top-level search API response."""

    data: list[dict[str, Any]] = Field(default_factory=list)
    total_data: int = Field(0, alias="totalData")

    model_config = {"populate_by_name": True}


# ---------------------------------------------------------------------------
# SQLAlchemy models (database layer)
# ---------------------------------------------------------------------------


class Base(DeclarativeBase):
    pass


class BamProperty(Base):
    """Merged search + detail data for a BAM NPA property."""

    __tablename__ = "bam_properties"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)  # BAM asset ID
    asset_no: Mapped[str | None] = mapped_column(Text)  # market_code
    asset_state: Mapped[str | None] = mapped_column(Text)
    asset_state_code: Mapped[str | None] = mapped_column(Text)

    # Location
    province: Mapped[str | None] = mapped_column(Text, index=True)
    district: Mapped[str | None] = mapped_column(Text)
    sub_district: Mapped[str | None] = mapped_column(Text)
    physical_zone: Mapped[str | None] = mapped_column(Text)
    property_location: Mapped[str | None] = mapped_column(Text)
    lat: Mapped[float | None] = mapped_column(Float)
    lon: Mapped[float | None] = mapped_column(Float)

    # Project
    project_th: Mapped[str | None] = mapped_column(Text)
    project_en: Mapped[str | None] = mapped_column(Text)

    # Classification
    asset_type: Mapped[str | None] = mapped_column(Text)
    asset_group: Mapped[str | None] = mapped_column(Text)
    asset_code: Mapped[str | None] = mapped_column(Text)
    col_type: Mapped[str | None] = mapped_column(Text)
    col_typedesc: Mapped[str | None] = mapped_column(Text)
    col_sub_type: Mapped[str | None] = mapped_column(Text)
    col_sub_typedesc: Mapped[str | None] = mapped_column(Text)
    license_number: Mapped[str | None] = mapped_column(Text)
    grade: Mapped[str | None] = mapped_column(Text)

    # Size
    rai: Mapped[float | None] = mapped_column(Numeric(10, 2))
    ngan: Mapped[float | None] = mapped_column(Numeric(10, 2))
    wa: Mapped[float | None] = mapped_column(Numeric(10, 2))
    area_meter: Mapped[float | None] = mapped_column(Numeric(12, 2))
    usable_area: Mapped[float | None] = mapped_column(Numeric(12, 2))
    size_build: Mapped[str | None] = mapped_column(Text)
    bedroom: Mapped[int | None] = mapped_column(Integer)
    bathroom: Mapped[int | None] = mapped_column(Integer)
    studio: Mapped[int | None] = mapped_column(Integer)
    livingroom: Mapped[int | None] = mapped_column(Integer)
    kitchen: Mapped[int | None] = mapped_column(Integer)
    parking: Mapped[int | None] = mapped_column(Integer)

    # Pricing (whole baht)
    sell_price: Mapped[float | None] = mapped_column(Numeric(14, 2))  # center_price
    discount_price: Mapped[float | None] = mapped_column(Numeric(14, 2))
    shock_price: Mapped[float | None] = mapped_column(Numeric(14, 2))
    evaluate_amt: Mapped[float | None] = mapped_column(Numeric(14, 2))  # appraised
    cost_asset_amt: Mapped[float | None] = mapped_column(Numeric(14, 2))  # BAM's cost
    sale_price_spc: Mapped[float | None] = mapped_column(Numeric(14, 2))  # special price
    sale_price_spc_from: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    sale_price_spc_to: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    evaluate_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    price_flag: Mapped[int | None] = mapped_column(Integer)

    # Package prices
    price_package_1: Mapped[float | None] = mapped_column(Numeric(14, 2))
    renovate_price_package_1: Mapped[float | None] = mapped_column(Numeric(14, 2))
    price_package_2: Mapped[float | None] = mapped_column(Numeric(14, 2))
    renovate_price_package_2: Mapped[float | None] = mapped_column(Numeric(14, 2))
    price_package_3: Mapped[float | None] = mapped_column(Numeric(14, 2))
    renovate_price_package_3: Mapped[float | None] = mapped_column(Numeric(14, 2))

    # Status flags
    is_hot_deal: Mapped[bool | None] = mapped_column(Boolean)
    is_shock_price: Mapped[bool | None] = mapped_column(Boolean)
    is_campaign: Mapped[str | None] = mapped_column(Text)
    campaign_name: Mapped[str | None] = mapped_column(Text)
    stars: Mapped[str | None] = mapped_column(Text)
    high_light: Mapped[bool | None] = mapped_column(Boolean)
    display_price: Mapped[bool | None] = mapped_column(Boolean)
    display_property: Mapped[bool | None] = mapped_column(Boolean)

    # Text descriptions
    property_detail: Mapped[str | None] = mapped_column(Text)
    invitation_th: Mapped[str | None] = mapped_column(Text)
    note: Mapped[str | None] = mapped_column(Text)
    summary: Mapped[str | None] = mapped_column(Text)

    # Department / Admin
    department_code: Mapped[str | None] = mapped_column(Text)
    department_name: Mapped[str | None] = mapped_column(Text)
    group_of_department: Mapped[str | None] = mapped_column(Text)
    admin_id: Mapped[str | None] = mapped_column(Text)
    admin_name: Mapped[str | None] = mapped_column(Text)

    # Contact
    work_phone: Mapped[str | None] = mapped_column(Text)
    work_phone_nxt: Mapped[str | None] = mapped_column(Text)
    telephone: Mapped[str | None] = mapped_column(Text)

    # Nearby (list of strings or dicts)
    nearby: Mapped[dict | None] = mapped_column(JSONB)

    # Images
    album_property: Mapped[dict | None] = mapped_column(JSONB)
    map_images: Mapped[dict | None] = mapped_column(JSONB)

    # Dates
    start_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    end_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    sale_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    key_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    bam_update_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    bam_create_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    bam_modify_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # Engagement
    view_count: Mapped[int | None] = mapped_column(Integer)

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
        Index("ix_bam_province", "province"),
        Index("ix_bam_asset_type", "asset_type"),
        Index("ix_bam_grade", "grade"),
        Index("ix_bam_sell_price", "sell_price"),
        Index("ix_bam_location", "province", "district"),
        Index("ix_bam_asset_no", "asset_no"),
        Index("ix_bam_evaluate", "evaluate_amt"),
    )


class BamPriceHistory(Base):
    __tablename__ = "bam_price_history"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    asset_id: Mapped[int] = mapped_column(Integer, index=True)

    sell_price: Mapped[float | None] = mapped_column(Numeric(14, 2))
    discount_price: Mapped[float | None] = mapped_column(Numeric(14, 2))
    shock_price: Mapped[float | None] = mapped_column(Numeric(14, 2))
    evaluate_amt: Mapped[float | None] = mapped_column(Numeric(14, 2))
    sale_price_spc: Mapped[float | None] = mapped_column(Numeric(14, 2))

    # new, price_change, state_change
    change_type: Mapped[str] = mapped_column(String(20))

    scraped_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (
        Index("ix_bam_ph_asset_date", "asset_id", "scraped_at"),
    )


class BamScrapeLog(Base):
    __tablename__ = "bam_scrape_logs"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    total_api: Mapped[int | None] = mapped_column(Integer)
    total_detail: Mapped[int | None] = mapped_column(Integer)
    new_count: Mapped[int | None] = mapped_column(Integer)
    updated_count: Mapped[int | None] = mapped_column(Integer)
    price_changed_count: Mapped[int | None] = mapped_column(Integer)
    state_changed_count: Mapped[int | None] = mapped_column(Integer)
    failed_pages: Mapped[int | None] = mapped_column(Integer)
    failed_details: Mapped[int | None] = mapped_column(Integer)
    error: Mapped[str | None] = mapped_column(Text)
    provinces_scraped: Mapped[str | None] = mapped_column(Text)

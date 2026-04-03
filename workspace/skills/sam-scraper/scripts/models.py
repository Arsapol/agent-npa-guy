"""
SAM (บสส. — Thai Asset Management Corporation) NPA Scraper Models
Pydantic v2 models + SQLAlchemy ORM for PostgreSQL storage.

Source: https://sam.or.th/site/npa/
"""

from __future__ import annotations

import re
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator, model_validator
from sqlalchemy import (
    ARRAY,
    BigInteger,
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import DeclarativeBase, relationship


# ============================================================================
# ENUMS
# ============================================================================


class SAMStatus(str, Enum):
    AUCTION = "ประมูล"
    DIRECT_SALE = "ซื้อตรง"
    PENDING_PRICE = "รอประกาศราคา"


class SAMPropertyType(str, Enum):
    LAND = "ที่ดินเปล่า"
    CONDO = "ห้องชุดพักอาศัย"
    HOUSE = "บ้านเดี่ยว"
    TOWNHOUSE = "ทาวน์เฮ้าส์"
    COMMERCIAL = "อาคารพาณิชย์"
    FACTORY = "โรงงาน/โกดัง"
    OTHER = "อสังหาริมทรัพย์อื่นๆ"
    SHOWROOM = "โชว์รูม"
    HOME_OFFICE = "โฮมออฟฟิศ"
    HOTEL = "โรงแรม/รีสอร์ท"
    OFFICE_CONDO = "ห้องชุดสำนักงาน"
    CONDO_BUILDING = "อาคารชุดพักอาศัย"
    OFFICE_BUILDING = "อาคารสำนักงาน"
    GAS_STATION = "ปั๊มน้ำมัน"
    DUPLEX = "บ้านแฝด"
    COMMERCIAL_CONDO = "ห้องชุดพาณิชยกรรม"
    APARTMENT = "อพาร์ทเมนท์"
    LEASE_COMMERCIAL = "สิทธิการเช่า/พื้นที่การพาณิชย์"
    HOSPITAL = "โรงพยาบาล"
    GOLF_MEMBERSHIP = "บัตรสมาชิกสนามกอล์ฟ"
    GOLF_COURSE = "สนามกอล์ฟ"
    DEPARTMENT_STORE = "ห้างสรรพสินค้า"
    HOUSING_PROJECT = "โครงการที่พักอาศัย/พาณิชยกรรม"


# Mapping from SAM dropdown option_id to enum
SAM_PROPERTY_TYPE_MAP: dict[int, SAMPropertyType] = {
    1: SAMPropertyType.LAND,
    8: SAMPropertyType.CONDO,
    9: SAMPropertyType.HOUSE,
    10: SAMPropertyType.TOWNHOUSE,
    11: SAMPropertyType.COMMERCIAL,
    13: SAMPropertyType.FACTORY,
    14: SAMPropertyType.OTHER,
    16: SAMPropertyType.SHOWROOM,
    17: SAMPropertyType.HOME_OFFICE,
    18: SAMPropertyType.HOTEL,
    19: SAMPropertyType.OFFICE_CONDO,
    20: SAMPropertyType.CONDO_BUILDING,
    21: SAMPropertyType.OFFICE_BUILDING,
    23: SAMPropertyType.GAS_STATION,
    24: SAMPropertyType.DUPLEX,
    25: SAMPropertyType.COMMERCIAL_CONDO,
    26: SAMPropertyType.APARTMENT,
    27: SAMPropertyType.LEASE_COMMERCIAL,
    28: SAMPropertyType.HOSPITAL,
    29: SAMPropertyType.GOLF_MEMBERSHIP,
    30: SAMPropertyType.GOLF_COURSE,
    31: SAMPropertyType.DEPARTMENT_STORE,
    32: SAMPropertyType.HOUSING_PROJECT,
}


# ============================================================================
# PYDANTIC v2 MODELS — PARSING LAYER
# ============================================================================


class SAMListProperty(BaseModel):
    """Parsed from list/table page — lightweight summary."""

    sam_id: int = Field(description="SAM internal ID (used in gotoDetail)")
    code: str = Field(description="Property code e.g. '1T2174', 'CL0175'")
    type_name: str = Field(description="Property type Thai name")
    district: str = Field(default="", description="เขต/อำเภอ")
    province: str = Field(default="", description="จังหวัด")
    size_text: str = Field(default="", description="Raw size text e.g. '44.09 ตร.ม.'")
    price_baht: Optional[int] = Field(default=None, description="Announced sale price in baht")
    status: str = Field(default="", description="ประมูล / ซื้อตรง")
    thumbnail_url: str = Field(default="", description="First image URL from listing")
    floor: Optional[int] = Field(default=None, description="Floor number (condos only)")

    @field_validator("price_baht", mode="before")
    @classmethod
    def parse_price(cls, v: str | int | None) -> int | None:
        if v is None or v == 0:
            return None
        if isinstance(v, int):
            return v
        cleaned = str(v).replace(",", "").strip()
        return int(cleaned) if cleaned else None


class SAMImageInfo(BaseModel):
    """A single gallery image with type classification."""

    url: str
    image_type: str = Field(default="photo", description="'photo', 'certificate', 'map'")


class SAMPropertyDetail(BaseModel):
    """Parsed from detail page — full property information."""

    sam_id: int = Field(description="SAM internal ID")
    code: str = Field(description="Property code e.g. '1T2174'")

    # Type
    type_name: str = Field(description="ประเภททรัพย์สิน")

    # Title deed
    title_deed_type: Optional[str] = Field(
        default=None, description="โฉนดที่ดิน / หนังสือกรรมสิทธิ์ห้องชุด etc."
    )
    title_deed_numbers: Optional[str] = Field(
        default=None, description="Deed numbers e.g. '16734, 16735, 40072'"
    )
    deed_count: Optional[int] = Field(default=None, description="จำนวนเอกสารสิทธิ์")

    # Size
    size_text: Optional[str] = Field(default=None, description="Raw size text")
    size_sqm: Optional[float] = Field(default=None, description="Normalized to sq.m.")
    size_rai: Optional[float] = Field(default=None, description="Rai (land)")
    size_ngan: Optional[float] = Field(default=None, description="Ngan (land)")
    size_wa: Optional[float] = Field(default=None, description="Sq.wah (land)")

    # Address components
    address_full: Optional[str] = Field(default=None, description="Full address text")
    house_number: Optional[str] = Field(default=None, description="เลขที่")
    project_name: Optional[str] = Field(default=None, description="โครงการ/Village name")
    road: Optional[str] = Field(default=None)
    subdistrict: Optional[str] = Field(default=None, description="แขวง/ตำบล")
    district: Optional[str] = Field(default=None, description="เขต/อำเภอ")
    province: Optional[str] = Field(default=None, description="จังหวัด")
    zone_color: Optional[str] = Field(default=None, description="เขตพื้นที่ (สี)")

    # Floor (condo only)
    floor: Optional[int] = Field(default=None, description="ชั้นที่")

    # Pricing
    price_baht: Optional[int] = Field(default=None, description="ราคาประกาศขาย")
    price_per_unit: Optional[float] = Field(
        default=None, description="Price per sq.wa or sq.m"
    )
    price_unit: Optional[str] = Field(
        default=None, description="'ตร.ว.' or 'ตร.ม.'"
    )

    # Status & auction
    status: str = Field(description="สถานะประกาศขาย")
    announcement_start_date: Optional[str] = Field(default=None, description="วันที่เริ่มประกาศขาย")
    registration_end_date: Optional[str] = Field(default=None, description="วันที่สิ้นสุดการลงทะเบียน")
    submission_date: Optional[str] = Field(default=None, description="วันที่ยื่นซอง")
    auction_method_text: Optional[str] = Field(default=None, description="สถานที่ประมูล raw text")

    # Coordinates
    lat: Optional[float] = Field(default=None)
    lng: Optional[float] = Field(default=None)

    # Images
    images: list[SAMImageInfo] = Field(default_factory=list, description="Gallery images")
    map_image_url: Optional[str] = Field(default=None, description="Location map image")

    # Detail tabs
    description: Optional[str] = Field(default=None, description="#tab03 content")
    remarks: Optional[str] = Field(default=None, description="หมายเหตุ")
    access_directions: Optional[str] = Field(default=None, description="#tab02 content")

    # Related
    promotion_links: list[str] = Field(default_factory=list)
    related_properties: list[str] = Field(
        default_factory=list, description="Same-project property codes"
    )

    @field_validator("price_baht", mode="before")
    @classmethod
    def parse_price(cls, v: str | int | None) -> int | None:
        if v is None or v == 0:
            return None
        if isinstance(v, int):
            return v
        cleaned = str(v).replace(",", "").strip()
        return int(cleaned) if cleaned else None

    @model_validator(mode="after")
    def compute_sqm(self) -> "SAMPropertyDetail":
        """Normalize land sizes to sqm if not already set."""
        if self.size_sqm is not None:
            return self
        if self.size_rai is not None or self.size_ngan is not None or self.size_wa is not None:
            r = self.size_rai or 0
            n = self.size_ngan or 0
            w = self.size_wa or 0
            self.size_sqm = (r * 1600) + (n * 400) + (w * 4)
        return self


class SAMDropdownOption(BaseModel):
    """A single dropdown option from the SAM search form."""

    option_type: str = Field(description="'product_type', 'province', 'district', 'status'")
    option_id: int
    option_name: str
    parent_id: Optional[int] = Field(default=None, description="For district → province_id")
    updated_at: datetime = Field(default_factory=datetime.now)


class SAMScrapeResult(BaseModel):
    """Summary of a scrape run."""

    source: str = Field(default="SAM")
    scrape_type: str = Field(description="'options', 'list', 'detail'")
    started_at: datetime
    finished_at: Optional[datetime] = None
    pages_scraped: int = 0
    items_parsed: int = 0
    items_new: int = 0
    items_updated: int = 0
    errors: list[str] = Field(default_factory=list)


# ============================================================================
# HELPERS — SIZE PARSING
# ============================================================================

# Match: "17 ไร่ 2 งาน 53.0 ตร.ว."
_LAND_SIZE_RE = re.compile(
    r"(?:(\d+(?:\.\d+)?)\s*ไร่)?" r"\s*" r"(?:(\d+(?:\.\d+)?)\s*งาน)?" r"\s*" r"(?:(\d+(?:\.\d+)?)\s*ตร\.ว\.)?"
)
# Match: "44.09 ตร.ม."
_SQM_SIZE_RE = re.compile(r"(\d+(?:\.\d+)?)\s*ตร\.ม\.")


def parse_land_size(text: str) -> Optional[tuple[float, float, float]]:
    """Parse '17 ไร่ 2 งาน 53.0 ตร.ว.' → (17.0, 2.0, 53.0) or None."""
    m = _LAND_SIZE_RE.search(text)
    if not m:
        return None
    rai = float(m.group(1)) if m.group(1) else 0.0
    ngan = float(m.group(2)) if m.group(2) else 0.0
    wa = float(m.group(3)) if m.group(3) else 0.0
    if rai == 0 and ngan == 0 and wa == 0:
        return None
    return (rai, ngan, wa)


def parse_sqm_size(text: str) -> Optional[float]:
    """Parse '44.09 ตร.ม.' → 44.09 or None."""
    m = _SQM_SIZE_RE.search(text)
    if m:
        return float(m.group(1))
    return None


def parse_price_per_unit(text: str) -> Optional[tuple[float, str]]:
    """Parse '9,418 บาทต่อตารางวา' → (9418.0, 'ตร.ว.')
    or '106,555 บาทต่อตารางเมตร' → (106555.0, 'ตร.ม.')
    """
    m = re.search(r"([\d,]+(?:\.\d+)?)\s*บาทต่อตาราง(วา|เมตร)", text)
    if not m:
        return None
    price = float(m.group(1).replace(",", ""))
    unit = "ตร.ว." if m.group(2) == "วา" else "ตร.ม."
    return (price, unit)


# ============================================================================
# ADDRESS PARSER
# ============================================================================

# Match: "หมู่บ้าน/โครงการ XXX ถนน YYY แขวง ZZZ เขต WWW จังหวัด QQQ"
# or:    "เลขที่ XXX ถนน YYY แขวง ZZZ เขต WWW จังหวัด QQQ"
_ADDRESS_RE = re.compile(
    r"(?:หมู่บ้าน/โครงการ\s+(?P<project>.+?))?\s*"
    r"(?:เลขที่\s+(?P<number>.+?))?\s*"
    r"(?:ถนน\s+(?P<road>.+?))?\s*"
    r"แขวง\s+(?P<subdistrict>.+?)\s+"
    r"เขต\s+(?P<district>.+?)\s+"
    r"จังหวัด\s+(?P<province>.+?)$"
)


def parse_address(text: str) -> dict:
    """Parse SAM address string into components."""
    text = text.strip()
    m = _ADDRESS_RE.match(text)
    if m:
        return {
            "project_name": m.group("project") or None,
            "house_number": m.group("number") or None,
            "road": m.group("road") or None,
            "subdistrict": m.group("subdistrict").strip(),
            "district": m.group("district").strip(),
            "province": m.group("province").strip(),
        }
    # Fallback: try to extract just district and province
    result: dict = {}
    dist_m = re.search(r"เขต\s+(.+?)\s+จังหวัด", text)
    prov_m = re.search(r"จังหวัด\s+(.+?)$", text)
    if dist_m:
        result["district"] = dist_m.group(1).strip()
    if prov_m:
        result["province"] = prov_m.group(1).strip()
    return result


# ============================================================================
# SQLALCHEMY ORM — STORAGE LAYER
# ============================================================================


class Base(DeclarativeBase):
    pass


class SamProperty(Base):
    """SAM NPA property — full detail stored here."""

    __tablename__ = "sam_properties"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sam_id = Column(Integer, unique=True, nullable=False, index=True)
    code = Column(String(50), nullable=False, index=True)

    # Type
    type_name = Column(String(255), nullable=False)

    # Title deed
    title_deed_type = Column(String(500))
    title_deed_numbers = Column(Text)
    deed_count = Column(Integer)

    # Size — Numeric for precision
    size_text = Column(String(255))
    size_sqm = Column(Numeric(12, 2))
    size_rai = Column(Numeric(8, 2))
    size_ngan = Column(Numeric(8, 2))
    size_wa = Column(Numeric(8, 2))

    # Address
    address_full = Column(Text)
    house_number = Column(String(100))
    project_name = Column(String(500))
    road = Column(String(500))
    subdistrict = Column(String(255))
    district = Column(String(255), index=True)
    province = Column(String(255), index=True)
    zone_color = Column(String(100))

    # Floor
    floor = Column(Integer)

    # Pricing — nullable Numeric
    price_baht = Column(Numeric(15, 0))
    price_per_unit = Column(Numeric(12, 2))
    price_unit = Column(String(20))  # "ตร.ว." or "ตร.ม."

    # Status & auction — structured fields
    status = Column(String(100), index=True)
    announcement_start_date = Column(String(10))   # often "-"
    registration_end_date = Column(String(10))
    submission_date = Column(String(10))
    auction_method_text = Column(Text)  # สถานที่ประมูล raw text

    # Coordinates — Numeric for precision
    lat = Column(Numeric(10, 6))
    lng = Column(Numeric(10, 6))

    # Media
    thumbnail_url = Column(Text)
    map_image_url = Column(Text)

    # Detail content
    description = Column(Text)
    remarks = Column(Text)
    access_directions = Column(Text)

    # Related — PostgreSQL ARRAY
    related_property_codes = Column(ARRAY(String))
    promotion_links = Column(ARRAY(Text))

    # Metadata
    source_url = Column(Text)
    first_seen_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    detail_fetched_at = Column(DateTime)
    is_active = Column(Boolean, default=True, index=True)

    # Relationships
    images = relationship(
        "SamPropertyImage", back_populates="property", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_sam_location", "province", "district"),
        Index("idx_sam_price", "price_baht"),
        Index("idx_sam_type", "type_name"),
        Index("idx_sam_status_active", "is_active", "status"),
    )

    def to_dict(self):
        return {
            "sam_id": self.sam_id,
            "code": self.code,
            "type_name": self.type_name,
            "district": self.district,
            "province": self.province,
            "size_sqm": self.size_sqm,
            "price_baht": self.price_baht,
            "status": self.status,
            "lat": self.lat,
            "lng": self.lng,
        }


class SamPropertyImage(Base):
    """SAM property images."""

    __tablename__ = "sam_property_images"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sam_id = Column(
        Integer,
        ForeignKey("sam_properties.sam_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    image_type = Column(String(20), nullable=False)  # "photo", "map", "certificate"
    image_url = Column(Text, nullable=False)
    image_order = Column(Integer, default=0)
    is_primary = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())

    property = relationship("SamProperty", back_populates="images")

    __table_args__ = (
        Index("idx_sam_images_sam_id", "sam_id", "image_order"),
    )


class SamDropdownCache(Base):
    """Cached dropdown options from SAM search form."""

    __tablename__ = "sam_dropdown_cache"

    id = Column(Integer, primary_key=True, autoincrement=True)
    option_type = Column(String(50), nullable=False, index=True)
    option_id = Column(Integer, nullable=False)
    option_name = Column(String(500), nullable=False)
    parent_id = Column(Integer)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint("option_type", "option_id", name="unique_sam_option"),
    )


class SamScrapeLog(Base):
    """Log of scrape runs for monitoring."""

    __tablename__ = "sam_scrape_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    scrape_type = Column(String(50), nullable=False)  # "options", "list", "detail"
    started_at = Column(DateTime, nullable=False)
    finished_at = Column(DateTime)
    pages_scraped = Column(Integer, default=0)
    items_parsed = Column(Integer, default=0)
    items_new = Column(Integer, default=0)
    items_updated = Column(Integer, default=0)
    error_message = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

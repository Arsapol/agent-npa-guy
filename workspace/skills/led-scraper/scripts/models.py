"""
SQLAlchemy Models for Multi-Source NPA Property Tracking
Database: PostgreSQL (local)
"""

from typing import Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


# ============================================================================
# CORE PROPERTIES TABLE
# ============================================================================


class Property(Base):
    __tablename__ = "properties"

    id = Column(Integer, primary_key=True, autoincrement=True)
    asset_id = Column(String(255), unique=True, nullable=False, index=True)

    # Source identification
    asset_type = Column(String(20), nullable=False, default="LED")
    source_name = Column(String(500), nullable=False)  # 'LED_Songkhla', 'KBank', etc.
    source_id = Column(String(500))

    # Property details
    property_type = Column(String(500), nullable=False)
    address = Column(Text)
    province = Column(String(500), nullable=False)
    ampur = Column(String(500), nullable=False)
    tumbol = Column(String(500), nullable=False)
    province_id = Column(String(10))

    # Size
    size_rai = Column(Float, default=0)
    size_ngan = Column(Float, default=0)
    size_wa = Column(Float, default=0)

    # Owner
    property_owner = Column(Text)

    # Unified pricing (satang - store as INTEGER for precision)
    primary_price_satang = Column(BigInteger, nullable=False)
    appraisal_price_satang = Column(BigInteger)

    # Sale info
    sale_status = Column(String(255), nullable=False)
    sale_type = Column(String(500))

    # Denormalized auction data (for performance)
    next_auction_date = Column(String(10))  # ISO8601: YYYY-MM-DD
    next_auction_status = Column(String(255))
    last_auction_date = Column(String(10))
    last_auction_status = Column(String(255))
    total_auction_count = Column(Integer, default=0)

    # Metadata
    extraction_timestamp = Column(String(255))
    source_url = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    led_property = relationship(
        "LedProperty",
        back_populates="property",
        uselist=False,
        cascade="all, delete-orphan",
    )
    bank_npa_property = relationship(
        "BankNpaProperty",
        back_populates="property",
        uselist=False,
        cascade="all, delete-orphan",
    )
    images = relationship(
        "PropertyImage", back_populates="property", cascade="all, delete-orphan"
    )
    auctions = relationship(
        "AuctionHistory", back_populates="property", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index("idx_properties_location", "province", "ampur", "tumbol"),
        Index("idx_properties_price", "primary_price_satang"),
        Index("idx_properties_source", "source_name", "asset_type"),
        Index("idx_properties_status", "sale_status"),
        CheckConstraint(
            "asset_type IN ('LED', 'BANK_NPA', 'COURT_AUCTION', 'PRIVATE_SALE')",
            name="check_asset_type",
        ),
    )

    @property
    def size_sqm(self) -> float:
        """Calculate total size in square meters"""
        return (self.size_rai * 1600) + (self.size_ngan * 400) + (self.size_wa * 4)

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "asset_id": self.asset_id,
            "asset_type": self.asset_type,
            "source_name": self.source_name,
            "property_type": self.property_type,
            "province": self.province,
            "ampur": self.ampur,
            "tumbol": self.tumbol,
            "size_sqm": self.size_sqm,
            "primary_price_satang": self.primary_price_satang,
            "sale_status": self.sale_status,
            "next_auction_date": self.next_auction_date,
        }


# ============================================================================
# LED-SPECIFIC PROPERTIES
# ============================================================================


class LedProperty(Base):
    __tablename__ = "led_properties"

    id = Column(Integer, primary_key=True, autoincrement=True)
    asset_id = Column(
        String(255),
        ForeignKey("properties.asset_id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    # LED identification
    case_number = Column(String(500), nullable=False, index=True)
    lot_number = Column(String(255))

    # LED legal info
    court = Column(String(500), nullable=False, index=True)
    plaintiff = Column(Text, index=True)
    defendant = Column(Text)
    owner_suit_name = Column(Text)
    issue_date = Column(String(10))  # ISO8601: YYYY-MM-DD

    # Deed
    deed_type = Column(String(255))
    deed_number = Column(String(255))

    # LED pricing (satang)
    enforcement_officer_price_satang = Column(BigInteger)
    department_appraisal_price_satang = Column(BigInteger)
    committee_determined_price_satang = Column(BigInteger)
    deposit_amount_satang = Column(BigInteger)
    reserve_fund_special_satang = Column(BigInteger)

    # LED sale info
    sale_location = Column(Text)
    sale_time = Column(String(20))
    contact_office = Column(String(500))
    contact_phone = Column(String(500))

    # LED flags
    is_extra_pledge = Column(Boolean, default=False)
    occupant = Column(String(500))

    # Additional
    remark = Column(Text)
    law_court_id = Column(String(10))

    # Relationship
    property = relationship("Property", back_populates="led_property")

    def to_dict(self):
        """Convert to dictionary"""
        return {
            "asset_id": self.asset_id,
            "case_number": self.case_number,
            "court": self.court,
            "plaintiff": self.plaintiff,
            "enforcement_officer_price_satang": self.enforcement_officer_price_satang,
            "committee_determined_price_satang": self.committee_determined_price_satang,
        }


# ============================================================================
# BANK NPA PROPERTIES
# ============================================================================


class BankNpaProperty(Base):
    __tablename__ = "bank_npa_properties"

    id = Column(Integer, primary_key=True, autoincrement=True)
    asset_id = Column(
        String(255),
        ForeignKey("properties.asset_id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    # Bank identification
    bank_name = Column(String(255), nullable=False, index=True)
    bank_branch = Column(String(500))
    bank_code = Column(String(20))

    # Account info
    account_number = Column(String(500), nullable=False, index=True)
    loan_account_number = Column(String(500))
    loan_type = Column(String(500))

    # Borrower info
    borrower_name = Column(Text, nullable=False, index=True)
    guarantor_name = Column(Text)
    co_borrower_name = Column(Text)

    # Bank pricing (satang)
    outstanding_debt_satang = Column(BigInteger, nullable=False)
    bank_appraisal_price_satang = Column(BigInteger)
    starting_bid_satang = Column(BigInteger)
    reserve_price_satang = Column(BigInteger)
    minimum_bid_satang = Column(BigInteger)

    # Dates
    loan_origination_date = Column(String(10))
    default_date = Column(String(10))
    foreclosure_date = Column(String(10), index=True)
    possession_date = Column(String(10))
    listing_date = Column(String(10))

    # Bank contacts
    asset_manager = Column(String(500))
    asset_manager_phone = Column(String(255))
    asset_manager_email = Column(String(500))

    # Property condition
    asset_condition = Column(String(500))
    occupancy_status = Column(String(255))
    collateral_type = Column(String(500))

    # Additional
    legal_case_number = Column(String(500))
    auction_terms = Column(Text)
    special_conditions = Column(Text)
    viewing_schedule = Column(Text)

    # Relationship
    property = relationship("Property", back_populates="bank_npa_property")

    __table_args__ = (
        CheckConstraint(
            "bank_name IN ('KBank', 'KTB', 'SCB', 'BBL', 'TMB', 'CIMB', 'Other')",
            name="check_bank_name",
        ),
    )


# ============================================================================
# PROPERTY IMAGES
# ============================================================================


class PropertyImage(Base):
    __tablename__ = "property_images"

    id = Column(Integer, primary_key=True, autoincrement=True)
    asset_id = Column(
        String(255),
        ForeignKey("properties.asset_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    image_type = Column(String(20), nullable=False)
    image_url = Column(Text, nullable=False)
    image_order = Column(Integer, default=0)
    caption = Column(Text)
    is_primary = Column(Boolean, default=False)
    width = Column(Integer)
    height = Column(Integer)
    file_size = Column(Integer)
    created_at = Column(DateTime, server_default=func.now())

    # Relationship
    property = relationship("Property", back_populates="images")

    __table_args__ = (
        Index("idx_property_images_asset", "asset_id", "image_order"),
        Index("idx_property_images_type", "asset_id", "image_type"),
        CheckConstraint(
            "image_type IN ('land', 'map', 'interior', 'exterior', 'document', 'other')",
            name="check_image_type",
        ),
    )


# ============================================================================
# AUCTION HISTORY
# ============================================================================


class AuctionHistory(Base):
    __tablename__ = "auction_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    asset_id = Column(
        String(255),
        ForeignKey("properties.asset_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    auction_number = Column(Integer, nullable=False)

    # Dates
    date_be = Column(String(20))  # Buddhist Era: DD/MM/YYYY
    date_ce = Column(String(10))  # Common Era ISO8601: YYYY-MM-DD

    # Status
    status = Column(String(255), nullable=False, index=True)
    status_code = Column(String(10))

    # Auction details
    auction_type = Column(String(255))  # 'government', 'bank', 'online'
    starting_price_satang = Column(BigInteger)
    winning_bid_satang = Column(BigInteger)
    winner_name = Column(Text)

    # Stats
    participant_count = Column(Integer)
    bid_count = Column(Integer)
    notes = Column(Text)

    # Metadata
    raw_date = Column(String(20))
    created_at = Column(DateTime, server_default=func.now())

    # Relationship
    property = relationship("Property", back_populates="auctions")

    __table_args__ = (
        Index("idx_auction_asset_date", "asset_id", "date_ce"),
        Index("idx_auction_upcoming", "date_ce", "status"),
        UniqueConstraint("asset_id", "auction_number", name="unique_auction"),
    )


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def baht_to_satang(baht: Optional[float]) -> Optional[int]:
    """Convert baht to satang (1 baht = 100 satang)"""
    if baht is None:
        return None
    return int(baht * 100)


def satang_to_baht(satang: Optional[int]) -> Optional[float]:
    """Convert satang to baht"""
    if satang is None:
        return None
    return satang / 100


def convert_image_path(path: Optional[str]) -> str:
    """Convert Z:\\ paths to web URLs"""
    if not path:
        return ""

    return path.replace("Z:\\", "https://asset.led.go.th/PPKPicture/").replace(
        "\\", "/"
    )


def convert_be_to_iso(be_date: str) -> Optional[str]:
    """
    Convert Buddhist Era date to ISO8601
    Input: DD/MM/YYYY (BE)
    Output: YYYY-MM-DD (CE)
    """
    if not be_date or "/" not in be_date:
        return None

    try:
        day, month, be_year = be_date.split("/")
        ce_year = int(be_year) - 543
        return f"{ce_year}-{month.zfill(2)}-{day.zfill(2)}"
    except (ValueError, IndexError):
        return None

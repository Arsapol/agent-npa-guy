"""Unified NPA property model — normalizes all providers into one shape."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, computed_field


class Source(str, Enum):
    LED = "LED"
    SAM = "SAM"
    BAM = "BAM"
    JAM = "JAM"
    KTB = "KTB"
    KBANK = "KBANK"
    SCB = "SCB"
    GSB = "GSB"
    TTB = "TTB"
    BAY = "BAY"
    LH = "LH"
    GHB = "GHB"


class NpaProperty(BaseModel):
    """Normalized NPA property across all providers.

    All prices in BAHT. All sizes in Thai standard units.
    """

    model_config = {"frozen": True}

    source: Source
    source_id: str  # unique ID within the source table
    property_type: str
    province: str
    district: str
    subdistrict: str

    # Price — always in BAHT
    price_baht: float | None = None
    appraisal_baht: float | None = None
    discount_pct: float | None = None  # computed: (1 - price/appraisal) * 100

    # Size — Thai land units
    size_rai: float | None = None
    size_ngan: float | None = None
    size_wa: float | None = None  # ตร.วา for land
    size_sqm: float | None = None  # ตร.ม. for condos/buildings

    # Rooms
    bedroom: int | None = None
    bathroom: int | None = None

    # GPS
    lat: float | None = None
    lon: float | None = None

    # Status
    status: str = ""
    is_sold: bool = False

    # Auction (LED-specific but useful cross-provider)
    next_auction_date: str | None = None
    total_auction_count: int = 0

    # Project / address
    project_name: str | None = None
    address: str | None = None

    # Links
    source_url: str | None = None
    thumbnail_url: str | None = None

    # Provider-specific extras (not normalized)
    extra: dict[str, Any] = Field(default_factory=dict)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def price_display(self) -> str:
        if self.price_baht is None:
            return "N/A"
        if self.price_baht >= 1_000_000:
            return f"{self.price_baht / 1_000_000:.2f}M"
        if self.price_baht >= 1_000:
            return f"{self.price_baht / 1_000:.1f}K"
        return f"{self.price_baht:.0f}"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def size_display(self) -> str:
        parts: list[str] = []
        if self.size_rai:
            parts.append(f"{self.size_rai:.0f}rai")
        if self.size_ngan:
            parts.append(f"{self.size_ngan:.0f}ngan")
        if self.size_wa:
            parts.append(f"{self.size_wa:.1f}wa")
        if self.size_sqm:
            parts.append(f"{self.size_sqm:.1f}sqm")
        return " ".join(parts) or "N/A"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def location_display(self) -> str:
        parts = [p for p in [self.province, self.district, self.subdistrict] if p]
        return " > ".join(parts)


class SearchFilters(BaseModel):
    """Unified search filters across all providers."""

    model_config = {"frozen": True}

    province: str | None = None
    district: str | None = None
    subdistrict: str | None = None
    min_price: float | None = None
    max_price: float | None = None
    property_type: str | None = None
    keyword: str | None = None
    sources: list[Source] | None = None  # None = all sources
    limit: int = 20
    offset: int = 0
    sort_by: str = "price"  # price, province, newest
    sort_desc: bool = False


class ProviderStats(BaseModel):
    """Per-provider summary."""

    model_config = {"frozen": True}

    source: Source
    total: int
    min_price: float | None = None
    max_price: float | None = None
    avg_price: float | None = None
    provinces: list[dict[str, Any]] = Field(default_factory=list)
    property_types: list[dict[str, Any]] = Field(default_factory=list)

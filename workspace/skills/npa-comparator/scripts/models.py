"""Comparison models for NPA cross-provider and market analysis."""

from __future__ import annotations

import os
import sys
from typing import Literal

from pydantic import BaseModel, Field

import importlib.util as _ilu

_ADAPTER_MODELS_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "npa-adapter", "scripts", "models.py")
)
_spec = _ilu.spec_from_file_location("npa_adapter_models", _ADAPTER_MODELS_PATH)
_adapter_models = _ilu.module_from_spec(_spec)  # type: ignore[arg-type]
_spec.loader.exec_module(_adapter_models)  # type: ignore[union-attr]

NpaProperty = _adapter_models.NpaProperty
PropertyCategory = _adapter_models.PropertyCategory
Source = _adapter_models.Source


# ---------------------------------------------------------------------------
# Strategy mapping
# ---------------------------------------------------------------------------

STRATEGY_MAP: dict[PropertyCategory, list[str]] = {
    PropertyCategory.CONDO: ["rent", "flip", "expat_rental"],
    PropertyCategory.LAND: ["land_bank", "develop", "subdivide"],
    PropertyCategory.HOUSE: ["rent", "flip", "renovate_and_rent"],
    PropertyCategory.TOWNHOUSE: ["rent", "flip", "renovate_and_rent"],
    PropertyCategory.COMMERCIAL: ["lease", "owner_occupy", "redevelop"],
    PropertyCategory.FACTORY: ["lease", "owner_occupy"],
    PropertyCategory.OTHER: ["hold"],
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def rai_ngan_wa_to_total_wa(rai: float | None, ngan: float | None, wa: float | None) -> float:
    """Convert Thai land units to total square wa. 1 rai = 400 wa, 1 ngan = 100 wa."""
    return (rai or 0) * 400 + (ngan or 0) * 100 + (wa or 0)


# ---------------------------------------------------------------------------
# Core models
# ---------------------------------------------------------------------------


class RangeEstimate(BaseModel, frozen=True):
    """Low / mid / high estimate for a numeric value."""

    low: float
    mid: float
    high: float


class AreaBenchmark(BaseModel, frozen=True):
    """Aggregated market/NPA benchmark for a geographic area."""

    median: float | None = None
    p25: float | None = None
    p75: float | None = None
    count: int = 0
    unit: str = ""  # e.g. "baht_per_wa", "baht_per_sqm", "baht_per_unit"
    source_breakdown: dict[str, int] = Field(default_factory=dict)
    data_quality: str = "LOW"  # HIGH (≥10), MEDIUM (≥5), LOW (<5)


class BaseComparison(BaseModel, frozen=True):
    """Shared fields for every comparison type."""

    npa_source: Source
    npa_source_id: str
    npa_category: PropertyCategory
    comparison_type: str  # literal discriminator in subclasses
    comparison_basis: str  # "cross_npa" or "market_verified"
    comparable_count: int = 0
    comparable_sources: list[Source] = Field(default_factory=list)
    area_benchmark: AreaBenchmark | None = None
    npa_concentration: float = 0.0  # % of comparables from same provider
    price_position: str = "BELOW_MEDIAN"  # BELOW_P25 / BELOW_MEDIAN / ABOVE_MEDIAN / ABOVE_P75
    supported_strategies: list[str] = Field(default_factory=list)
    data_quality: str = "LOW"  # HIGH / MEDIUM / LOW
    comparables: list[dict] = Field(default_factory=list)  # capped at 20


# ---------------------------------------------------------------------------
# Type-specific comparison models
# ---------------------------------------------------------------------------


class CondoComparison(BaseComparison, frozen=True):
    """Comparison result for condo properties."""

    comparison_type: Literal["condo"] = "condo"
    price_per_sqm: float | None = None
    median_market_sqm: float | None = None
    discount_vs_market_pct: float | None = None
    discount_vs_npa_median_pct: float | None = None
    bts_proximity_tier: str | None = None  # A / B / C


class LandComparison(BaseComparison, frozen=True):
    """Comparison result for land properties."""

    comparison_type: Literal["land"] = "land"
    price_per_wa: float | None = None
    total_area_wa: float | None = None
    median_area_price_per_wa: float | None = None
    discount_vs_npa_median_pct: float | None = None
    zoning_info: dict | None = None
    development_potential: str | None = None


class HouseComparison(BaseComparison, frozen=True):
    """Comparison result for house / townhouse properties.

    Primary metric is price_per_wa_land (from title deed).
    usable_area_sqm is unreliable across projects — use only for context.
    """

    comparison_type: Literal["house"] = "house"

    # PRIMARY metric — standardized, reliable
    price_per_wa_land: float | None = None
    total_land_wa: float | None = None
    median_area_price_per_wa_land: float | None = None

    # Unit-level price (useful when land area is unavailable)
    price_per_unit: float | None = None
    median_area_price_per_unit: float | None = None

    discount_vs_npa_median_pct: float | None = None

    # Floor area — unreliable across projects, included with caveat
    usable_area_sqm: float | None = None
    price_per_sqm_usable: float | None = None
    usable_area_caveat: str = "Usable area varies by project. Use price_per_wa_land for comparison."

    # Building age — sourced from KBank / GSB / TTB only
    building_age_years: int | None = None
    building_age_source: str | None = None
    renovation_estimate: RangeEstimate | None = None
    renovation_data_caveat: str = "Building age from KBank/GSB/TTB only. Others return None."

    bedrooms: int | None = None
    neighborhood_npa_density: float | None = None


class CommercialComparison(BaseComparison, frozen=True):
    """Comparison result for commercial properties."""

    comparison_type: Literal["commercial"] = "commercial"
    price_per_sqm: float | None = None
    median_area_price_per_sqm: float | None = None
    discount_vs_npa_median_pct: float | None = None
    commercial_density: float | None = None
    property_subtype: str | None = None

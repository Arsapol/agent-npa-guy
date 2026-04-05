"""
Shared Pydantic models for Multi-Strategy NPA Screener v2.

All model definitions from shared-contracts.md.
"""

from enum import Enum
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict

from constants import MORTGAGE_RATE_FIXED


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class PropertyType(str, Enum):
    CONDO = "condo"
    HOUSE = "house"
    TOWNHOUSE = "townhouse"
    LAND = "land"
    HOUSE_AND_LAND = "house_and_land"
    COMMERCIAL = "commercial"


class Strategy(str, Enum):
    RENT = "rent"
    FLIP = "flip"
    LAND_BANK = "land_bank"
    HOSPITALITY = "hospitality"


# ---------------------------------------------------------------------------
# Investor Profile
# ---------------------------------------------------------------------------


class InvestorProfile(BaseModel):
    model_config = ConfigDict(frozen=True)

    purchase_mode: Literal["cash", "mortgage"] = "cash"
    ltv_pct: float = 0.0  # 0.0 for cash, 0.7-1.0 for mortgage
    mortgage_rate: float = MORTGAGE_RATE_FIXED
    hold_horizon_years: int = 5
    entity_type: Literal["personal", "company"] = "personal"
    tabien_baan: bool = False
    renovation_budget_pct: float = 0.0  # % of purchase price (0.10 = 10%)
    strategies: list[str] = ["all"]
    risk_tolerance: Literal["conservative", "moderate", "aggressive"] = "moderate"


# ---------------------------------------------------------------------------
# NPA Candidate (extended from v1)
# ---------------------------------------------------------------------------


class NpaCandidate(BaseModel):
    model_config = ConfigDict(frozen=True)

    # Identity
    source: str  # LED, SAM, BAM, JAM, KTB, KBANK
    source_id: str
    property_type: PropertyType = PropertyType.CONDO
    project_name: str = ""

    # Location
    province: str = ""
    district: str = ""
    subdistrict: str = ""
    lat: Optional[float] = None
    lon: Optional[float] = None

    # Price & size
    price_baht: float
    size_sqm: Optional[float] = None
    price_sqm: Optional[float] = None

    # Building info
    bedroom: Optional[int] = None
    bathroom: Optional[int] = None
    floor: Optional[str] = None
    building_age: Optional[int] = None

    # NPA-specific
    npa_vintage_months: Optional[int] = None
    auction_round: Optional[int] = None

    # Market enrichment
    market_price_sqm: Optional[int] = None
    market_confidence: str = "none"
    market_year_built: Optional[int] = None
    market_total_units: Optional[int] = None
    market_developer: Optional[str] = None
    market_rent_median: Optional[int] = None
    market_units_for_sale: Optional[int] = None
    market_units_for_rent: Optional[int] = None
    market_project_name: Optional[str] = None
    supply_pressure_pct: Optional[float] = None

    # Proximity
    nearest_anchor_name: Optional[str] = None
    nearest_anchor_type: Optional[str] = None
    nearest_anchor_dist_m: Optional[float] = None
    nearest_anchor_enrollment: Optional[int] = None
    nearest_bts_name: Optional[str] = None
    nearest_bts_dist_m: Optional[float] = None
    bts_tier: str = ""

    # Computed
    real_discount_pct: Optional[float] = None
    verified_price_sqm: Optional[float] = None


# ---------------------------------------------------------------------------
# Strategy Score
# ---------------------------------------------------------------------------


class StrategyScore(BaseModel):
    model_config = ConfigDict(frozen=True)

    strategy: Strategy
    sub_strategy: str = ""
    score: float  # 0-100
    verdict: Literal["STRONG_BUY", "BUY", "WATCH", "AVOID"]
    key_metrics: dict[str, Optional[float]] = {}
    flags: list[str] = []
    reject_reasons: list[str] = []
    pass_gates: bool = True


# ---------------------------------------------------------------------------
# Financial Metrics
# ---------------------------------------------------------------------------


class FinancialMetrics(BaseModel):
    model_config = ConfigDict(frozen=True)

    irr_pct: Optional[float] = None
    irr_vs_benchmark: str = ""
    cocr_pct: Optional[float] = None
    dscr: Optional[float] = None
    break_even_occupancy_pct: Optional[float] = None
    hold_cost_monthly: Optional[float] = None
    total_acquisition_cost: Optional[float] = None
    exit_tax_pct: Optional[float] = None
    tax_recommendation: str = ""
    opportunity_cost_comparison: dict[str, float] = {}


# ---------------------------------------------------------------------------
# Pre-Filter Result
# ---------------------------------------------------------------------------


class PreFilterResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    pass_all: bool
    gates: dict[str, bool] = {}
    flags: list[str] = []
    reject_reasons: list[str] = []


# ---------------------------------------------------------------------------
# Property Result (top-level output per property)
# ---------------------------------------------------------------------------


class PropertyResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    candidate: NpaCandidate
    prefilter: PreFilterResult
    strategy_scores: dict[str, StrategyScore] = {}  # Strategy.value -> StrategyScore
    best_strategy: Optional[str] = None
    best_score: float = 0.0
    financial: Optional[FinancialMetrics] = None
    is_dual_strategy: bool = False
    dual_strategies: list[str] = []
    cascade_path: list[str] = []

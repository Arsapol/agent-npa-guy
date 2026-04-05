"""
Hospitality / renovation strategy scorer for Multi-Strategy NPA Screener v2.

Sub-strategies:
  - serviced_apt  : 30+ day furnished rentals (condos and houses)
  - str           : short-term rental / Airbnb-style (houses/villas only)
  - co_living     : digital nomad / shared living (houses, large condos)
  - mini_resort   : villa / landed resort-style (houses/villas only)

Hard reject: condo + STR intent → Hotel Act B.E. 2547 violation.
Research source: workspace/research/strategies/renovation-hospitality-strategy.md
"""

from typing import Optional

from constants import (
    OPERATING_COST_HOSPITALITY,
    RENO_COST_HOSPITALITY_MAX,
    RENO_COST_HOSPITALITY_MIN,
    RENO_MAX_PCT,
    VERIFIED_RENT_FURNISHED,
)
from models_v2 import InvestorProfile, NpaCandidate, PropertyType, Strategy, StrategyScore

# --- Legal compliance base scores by property type ---
# condo=3 (serviced apt only), house=7, villa/house_and_land=8
_LEGAL_SCORE_BY_TYPE: dict[PropertyType, int] = {
    PropertyType.CONDO: 3,
    PropertyType.HOUSE: 7,
    PropertyType.TOWNHOUSE: 6,
    PropertyType.HOUSE_AND_LAND: 8,
    PropertyType.LAND: 0,       # No habitable structure
    PropertyType.COMMERCIAL: 5,
}

# Legal minimum to proceed
_LEGAL_MIN = 3

# Sub-strategy selection thresholds
_LEGAL_THRESHOLD_FULL = 6       # Needed for STR / mini resort
_LEGAL_THRESHOLD_COLIVING = 5   # Co-living requires slightly less

# Renovation cost rate (midpoint of hospitality range per sqm)
_RENO_COST_PER_SQM = (RENO_COST_HOSPITALITY_MIN + RENO_COST_HOSPITALITY_MAX) / 2  # 21_500

# Furnished premium multiplier for serviced apt revenue
_FURNISHED_PREMIUM = 1.3  # 30% over market_rent_median

# Minimum renovation ROI to pass gate
_MIN_RENO_ROI = 0.20

# Bangkok median OCC proxy (no live data; use research benchmark)
_DEFAULT_OCC = 0.66  # 66% Bangkok median (AirBtics 2025)

# Area saturation scores by district keyword (competition proxy)
# Lower = less competition = better score
_SATURATED_DISTRICTS = {"sukhumvit", "silom", "sathorn", "nana", "asok"}
_LOW_COMP_DISTRICTS = {"riverside", "on nut", "phra khanong", "ladprao", "lat phrao"}


def _legal_compliance_score(candidate: NpaCandidate) -> int:
    """
    Compute legal compliance score (0-10) based on property type.

    condo=3 (serviced apt only path), house=7, house_and_land=8.
    Deducts points for known STR-hostile condos (not detectable without DB — skipped).
    """
    return _LEGAL_SCORE_BY_TYPE.get(candidate.property_type, 3)


def _select_sub_strategy(
    candidate: NpaCandidate, legal_score: int
) -> str:
    """Select the best sub-strategy based on property type and legal score."""
    ptype = candidate.property_type
    size = candidate.size_sqm or 0.0

    if ptype in (PropertyType.HOUSE_AND_LAND, PropertyType.HOUSE) and legal_score >= _LEGAL_THRESHOLD_FULL:
        return "mini_resort"
    if size >= 60 and legal_score >= _LEGAL_THRESHOLD_COLIVING:
        return "co_living"
    if legal_score >= _LEGAL_THRESHOLD_FULL:
        return "str"
    return "serviced_apt"


def _estimate_renovation_cost(candidate: NpaCandidate) -> Optional[float]:
    """Estimate hospitality renovation cost (THB). None if size unknown."""
    if candidate.size_sqm is None:
        return None
    return candidate.size_sqm * _RENO_COST_PER_SQM


def _cap_reno_cost(reno_cost: float, price: float) -> float:
    """Cap renovation at RENO_MAX_PCT of purchase price."""
    max_reno = price * RENO_MAX_PCT
    return min(reno_cost, max_reno)


def _annual_gross_revenue(candidate: NpaCandidate, sub_strategy: str) -> Optional[float]:
    """
    Estimate annual gross revenue.

    Serviced apt: market_rent_median * furnished_premium * 12
    STR / mini_resort / co_living: market_rent_median * furnished_premium * 12 * 1.2
    Returns None if no rent data.
    """
    if candidate.market_rent_median is None:
        return None
    monthly_base = candidate.market_rent_median * VERIFIED_RENT_FURNISHED * _FURNISHED_PREMIUM
    if sub_strategy in ("str", "mini_resort"):
        # Use occupancy-adjusted STR gross (monthly equiv × 12)
        monthly_str = monthly_base * (_DEFAULT_OCC * 1.15)  # slight STR uplift
        return monthly_str * 12
    if sub_strategy == "co_living":
        return monthly_base * 1.1 * 12  # slight density uplift
    return monthly_base * 12  # serviced_apt: full month, no OCC haircut


def _renovation_roi(
    reno_cost: float,
    annual_gross_post: float,
    market_rent_median: int,
) -> float:
    """
    Renovation ROI = (post_reno_annual_income - pre_reno_income) / reno_cost.

    Pre-reno: market_rent_median * 12 (bare, no furnishing premium).
    """
    pre_reno_annual = market_rent_median * 12
    post_reno_net_annual = annual_gross_post * (1 - OPERATING_COST_HOSPITALITY)
    incremental = post_reno_net_annual - pre_reno_annual
    if reno_cost <= 0:
        return 0.0
    return incremental / reno_cost


def _competition_score(candidate: NpaCandidate) -> float:
    """
    Return competition score (0.0–1.0). Higher = less competition = better.
    Uses district name as a proxy for saturation benchmarks.
    """
    district = (candidate.district or "").lower()
    for d in _SATURATED_DISTRICTS:
        if d in district:
            return 0.2
    for d in _LOW_COMP_DISTRICTS:
        if d in district:
            return 0.8
    return 0.5  # Moderate / unknown


def _location_score(candidate: NpaCandidate) -> float:
    """
    Location score (0.0–1.0) based on BTS proximity.

    BTS tier A → 1.0, B → 0.65, C → 0.35, no data → 0.3.
    """
    tier = (candidate.bts_tier or "").upper()
    if tier == "A":
        return 1.0
    if tier == "B":
        return 0.65
    if tier == "C":
        return 0.35
    dist = candidate.nearest_bts_dist_m
    if dist is None:
        return 0.3
    if dist <= 300:
        return 1.0
    if dist <= 800:
        return 0.75
    if dist <= 1500:
        return 0.5
    return 0.25


def score_hospitality(
    candidate: NpaCandidate, profile: InvestorProfile
) -> StrategyScore:
    """
    Score a candidate for hospitality/renovation strategy.

    HARD REJECT: condo + STR hint (legal_score < 3).
    Condo properties route to serviced_apt only (30+ day minimum).
    Houses/villas eligible for all sub-strategies.
    """
    reject_reasons: list[str] = []
    flags: list[str] = []

    # --- Hard reject: LAND has no habitable structure ---
    if candidate.property_type == PropertyType.LAND:
        return StrategyScore(
            strategy=Strategy.HOSPITALITY,
            sub_strategy="",
            score=0.0,
            verdict="AVOID",
            key_metrics={},
            flags=[],
            reject_reasons=["property_type=land has no habitable structure for hospitality"],
            pass_gates=False,
        )

    # --- Legal compliance gate ---
    legal_score = _legal_compliance_score(candidate)

    if legal_score < _LEGAL_MIN:
        return StrategyScore(
            strategy=Strategy.HOSPITALITY,
            sub_strategy="",
            score=0.0,
            verdict="AVOID",
            key_metrics={"legal_compliance_score": float(legal_score)},
            flags=[],
            reject_reasons=[
                f"legal_compliance_score={legal_score} < {_LEGAL_MIN} minimum; "
                "Hotel Act B.E. 2547 risk too high"
            ],
            pass_gates=False,
        )

    # Condo hard reject for STR
    if candidate.property_type == PropertyType.CONDO:
        flags.append(
            "CONDO: routed to serviced_apt only (30+ day minimum); "
            "STR rejected per Hotel Act B.E. 2547"
        )

    # --- Sub-strategy selection ---
    sub_strategy = _select_sub_strategy(candidate, legal_score)

    # Force condo to serviced_apt regardless of other conditions
    if candidate.property_type == PropertyType.CONDO:
        sub_strategy = "serviced_apt"

    # --- Renovation cost ---
    reno_cost_raw = _estimate_renovation_cost(candidate)
    if reno_cost_raw is None:
        flags.append("no size_sqm; renovation cost estimated at 0")
        reno_cost_raw = 0.0

    reno_cost = _cap_reno_cost(reno_cost_raw, candidate.price_baht)
    reno_capped = reno_cost < reno_cost_raw
    if reno_capped:
        flags.append(
            f"reno_cost capped at {RENO_MAX_PCT:.0%} of purchase price "
            f"({reno_cost:,.0f} THB)"
        )

    # Reno cost ratio gate: reject if > 80% of purchase price
    rcr = reno_cost / candidate.price_baht if candidate.price_baht > 0 else 0.0
    if rcr > 0.80:
        reject_reasons.append(
            f"renovation_cost_ratio={rcr:.1%} > 80%; not viable"
        )

    # --- Revenue estimation ---
    annual_gross = _annual_gross_revenue(candidate, sub_strategy)
    if annual_gross is None:
        flags.append("no market_rent_median; revenue potential cannot be estimated")
        annual_gross = 0.0

    # --- Renovation ROI ---
    rroi = 0.0
    if candidate.market_rent_median and reno_cost > 0 and annual_gross > 0:
        rroi = _renovation_roi(reno_cost, annual_gross, candidate.market_rent_median)
    elif reno_cost == 0 and annual_gross > 0:
        rroi = 1.0  # No reno cost = infinite ROI; cap at 1.0 for scoring
        flags.append("reno_cost=0 (no size data); RROI set to 1.0")

    if rroi < _MIN_RENO_ROI and reno_cost > 0:
        reject_reasons.append(
            f"renovation_roi={rroi:.1%} < {_MIN_RENO_ROI:.0%} minimum"
        )

    if reject_reasons:
        return StrategyScore(
            strategy=Strategy.HOSPITALITY,
            sub_strategy=sub_strategy,
            score=0.0,
            verdict="AVOID",
            key_metrics={
                "legal_compliance_score": float(legal_score),
                "renovation_cost_ratio": round(rcr, 3),
                "renovation_roi": round(rroi, 3),
            },
            flags=flags,
            reject_reasons=reject_reasons,
            pass_gates=False,
        )

    # --- Score components ---

    # Revenue potential (30%): normalize net annual yield vs purchase price
    net_annual = annual_gross * (1 - OPERATING_COST_HOSPITALITY)
    net_yield = net_annual / candidate.price_baht if candidate.price_baht > 0 else 0.0
    # Target yield range: 5% (min) → 12% (max for mini_resort)
    revenue_component = max(0.0, min(1.0, (net_yield - 0.05) / 0.07))

    # Renovation ROI (25%): 0% → 40% range
    reno_component = max(0.0, min(1.0, (rroi - _MIN_RENO_ROI) / 0.20))

    # Location (20%)
    location_component = _location_score(candidate)

    # Legal compliance (15%): normalize 3 → 10
    legal_component = max(0.0, min(1.0, (legal_score - _LEGAL_MIN) / (10 - _LEGAL_MIN)))

    # Competition (10%)
    competition_component = _competition_score(candidate)

    # --- Composite ---
    raw_score = (
        revenue_component * 0.30
        + reno_component * 0.25
        + location_component * 0.20
        + legal_component * 0.15
        + competition_component * 0.10
    )
    score = raw_score * 100.0

    # --- Verdict ---
    if score >= 70.0:
        verdict = "STRONG_BUY"
    elif score >= 55.0:
        verdict = "BUY"
    elif score >= 40.0:
        verdict = "WATCH"
    else:
        verdict = "AVOID"

    return StrategyScore(
        strategy=Strategy.HOSPITALITY,
        sub_strategy=sub_strategy,
        score=score,
        verdict=verdict,
        key_metrics={
            "legal_compliance_score": float(legal_score),
            "sub_strategy": None,  # stored in sub_strategy field
            "net_annual_income": round(net_annual, 0),
            "net_yield_pct": round(net_yield, 4),
            "renovation_cost": round(reno_cost, 0),
            "renovation_cost_ratio": round(rcr, 3),
            "renovation_roi": round(rroi, 3),
            "location_score": round(location_component, 3),
            "competition_score": round(competition_component, 3),
        },
        flags=flags,
        reject_reasons=[],
        pass_gates=True,
    )

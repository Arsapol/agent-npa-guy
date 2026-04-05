"""
Rental Strategy Scorer for Multi-Strategy NPA Screener v2.

Implements scoring for buy-and-rent strategy based on:
- Gross Rental Yield (GRY) with seasonal adjustments
- Net Rental Yield (NRY) with full holding cost model
- Cash-on-Cash Return (CoCR) parallel gate for leveraged purchases
- Demand Anchor Score (DAS) combining transit + education + hospital proximity
- Supply pressure penalty
- Comparable rental listings (liquidity check)

Research source: workspace/research/strategies/rental-strategy.md (2026-04-05)
"""

from datetime import datetime
from typing import Optional

from constants import (
    CAM_DEFAULT_SQM,
    COCR_MIN,
    DISCOUNT_TIER_A,
    DISCOUNT_TIER_B,
    DISCOUNT_TIER_C,
    DSCR_MIN,
    MORTGAGE_RATE_FIXED,
    SEASONAL_ADJUSTMENT_Q2,
    SUMMER_VACANCY_FACTOR,
    SUPPLY_PRESSURE_SEVERE,
    VERIFIED_RENT_BARE,
    VERIFIED_RENT_FURNISHED,
    YIELD_TIER_A,
    YIELD_TIER_B,
    YIELD_TIER_C,
)
from models_v2 import InvestorProfile, NpaCandidate, Strategy, StrategyScore
from screener import (
    EDUCATION_ANCHORS,
    TIER1_DEVELOPERS,
    TIER2_DEVELOPERS,
    TRANSIT_STATIONS,
    haversine_m,
)

# ---------------------------------------------------------------------------
# GRY thresholds by anchor type and BTS tier
# ---------------------------------------------------------------------------

# (reject_below, minimum, good_min, best_min)
GRY_THRESHOLDS: dict[str, tuple[float, float, float, float]] = {
    "university_tier_c": (0.09, 0.09, 0.10, 0.11),
    "university_tier_b": (0.08, 0.08, 0.09, 0.10),
    "university_tier_a": (0.07, 0.07, 0.08, 0.09),
    "thai_school": (0.065, 0.065, 0.075, 0.085),
    "intl_school": (0.06, 0.06, 0.07, 0.08),
    "hospital": (0.07, 0.07, 0.08, 0.09),
    "default": (0.07, 0.07, 0.08, 0.09),
}

# CoCR minimums by BTS tier (leveraged purchase override)
COCR_TIER: dict[str, float] = {
    "A": 0.05,
    "B": 0.07,
    "C": 0.09,
}

# Vacancy months by tier and anchor type
VACANCY_MONTHS_TIER_A_B = 1.0
VACANCY_MONTHS_TIER_C_STUDENT = 2.0
VACANCY_MONTHS_DEFAULT = 1.0

# Holding cost rates
PROPERTY_TAX_RATE = 0.0002  # 0.02% of assessed value
ASSESSED_VALUE_FACTOR = 0.90  # assessed value ≈ purchase price × 0.90
INSURANCE_RATE = 0.0015  # 0.15% of purchase price
AGENT_FEE_RATE = 0.08  # 8% of annual rent
MAINTENANCE_RATE = 0.005  # 0.5% of purchase price
INCOME_TAX_ON_RENT_RATE = 0.10  # 10% of gross as conservative estimate

# NRY hard thresholds
NRY_HARD_REJECT = 0.015  # 1.5% absolute floor
NRY_CASH_MIN = 0.03  # 3.0% for cash purchase
PRM_REJECT = 20.0  # Price-to-rent multiple reject threshold
PRM_BEST = 14.0  # Price-to-rent multiple best threshold

# DAS thresholds
DAS_HARD_REJECT = 25
DAS_GATE_MIN = 40

# Comparable rental listings thresholds
CRLC_REJECT = 3
CRLC_THIN = 5


# ---------------------------------------------------------------------------
# Demand Anchor Score (DAS)
# ---------------------------------------------------------------------------


def _primary_anchor_score(
    anchor_type: Optional[str],
    anchor_dist_m: Optional[float],
    enrollment: Optional[int],
) -> tuple[int, str]:
    """Compute primary anchor contribution (0–50 pts) and sub-type label."""
    if anchor_type is None or anchor_dist_m is None:
        return 0, "none"

    d = anchor_dist_m

    if anchor_type == "university":
        enroll = enrollment or 0
        if enroll >= 30000:
            pts = 50 if d <= 400 else 40 if d <= 800 else 0
        elif enroll >= 15000:
            pts = 35 if d <= 400 else 25 if d <= 800 else 0
        else:
            pts = 20 if d <= 400 else 10 if d <= 800 else 0
        return pts, "university"

    if anchor_type == "intl_school":
        if enrollment and enrollment > 500:
            pts = 40 if d <= 800 else 28 if d <= 2000 else 0
        else:
            pts = 25 if d <= 800 else 15 if d <= 2000 else 0
        return pts, "intl_school"

    if anchor_type == "thai_school":
        enroll = enrollment or 0
        if enroll >= 3000:
            pts = 30 if d <= 400 else 20 if d <= 800 else 0
        else:
            pts = 15 if d <= 400 else 8 if d <= 800 else 0
        return pts, "thai_school"

    if anchor_type in ("hospital", "hospital_large"):
        pts = 35 if d <= 500 else 25 if d <= 1500 else 0
        return pts, "hospital"

    if anchor_type == "industrial":
        pts = 20 if d <= 2000 else 0
        return pts, "industrial"

    if anchor_type == "cbd":
        pts = 30 if d <= 1000 else 0
        return pts, "cbd"

    return 0, "none"


def _secondary_anchor_score(bts_dist_m: Optional[float]) -> int:
    """Compute secondary (BTS/MRT) contribution (0–20 pts)."""
    if bts_dist_m is None:
        return 0
    if bts_dist_m < 400:
        return 20
    if bts_dist_m < 800:
        return 15
    if bts_dist_m < 1500:
        return 8
    return 0


def _compute_das(candidate: NpaCandidate) -> tuple[int, str]:
    """Compute Demand Anchor Score (0–70) and primary anchor sub-type."""
    primary_pts, sub_type = _primary_anchor_score(
        candidate.nearest_anchor_type,
        candidate.nearest_anchor_dist_m,
        candidate.nearest_anchor_enrollment,
    )
    secondary_pts = _secondary_anchor_score(candidate.nearest_bts_dist_m)
    return primary_pts + secondary_pts, sub_type


# ---------------------------------------------------------------------------
# GRY threshold lookup
# ---------------------------------------------------------------------------


def _gry_threshold_key(anchor_sub_type: str, bts_tier: str) -> str:
    """Map anchor sub-type + BTS tier to a GRY threshold key."""
    if anchor_sub_type == "university":
        tier = bts_tier.upper() if bts_tier else "C"
        return f"university_tier_{tier.lower()}"
    if anchor_sub_type == "intl_school":
        return "intl_school"
    if anchor_sub_type == "thai_school":
        return "thai_school"
    if anchor_sub_type == "hospital":
        return "hospital"
    return "default"


# ---------------------------------------------------------------------------
# Adjusted annual rent
# ---------------------------------------------------------------------------


def _adjusted_annual_rent(
    candidate: NpaCandidate,
    profile: InvestorProfile,
    anchor_sub_type: str,
    apply_seasonal: bool,
) -> Optional[float]:
    """Compute adjusted annual rent using market rent median with haircut.

    Returns None if no rent data available.
    """
    if not candidate.market_rent_median:
        return None

    listed_monthly = float(candidate.market_rent_median)

    # Apply furnished/bare haircut
    haircut = VERIFIED_RENT_FURNISHED if profile.renovation_budget_pct > 0 else VERIFIED_RENT_BARE

    # Seasonal adjustment: if current month is April–June AND anchor is university
    if apply_seasonal and anchor_sub_type == "university":
        haircut = haircut * SEASONAL_ADJUSTMENT_Q2

    return listed_monthly * haircut * 12


# ---------------------------------------------------------------------------
# Holding costs (annual)
# ---------------------------------------------------------------------------


def _annual_holding_costs(
    price_baht: float,
    size_sqm: Optional[float],
    annual_rent: float,
    bts_tier: str,
    anchor_sub_type: str,
) -> float:
    """Compute total annual holding costs for NRY calculation."""
    sqm = size_sqm or 30.0  # fallback to 30 sqm if unknown

    cam_annual = CAM_DEFAULT_SQM * sqm * 12
    tax_annual = price_baht * ASSESSED_VALUE_FACTOR * PROPERTY_TAX_RATE
    insurance_annual = price_baht * INSURANCE_RATE
    agent_annual = annual_rent * AGENT_FEE_RATE
    maintenance_annual = price_baht * MAINTENANCE_RATE
    income_tax_annual = annual_rent * INCOME_TAX_ON_RENT_RATE

    # Vacancy reserve: Tier C + student = 2 months, otherwise 1 month
    tier = bts_tier.upper() if bts_tier else "C"
    is_student_tier_c = (anchor_sub_type == "university") and (tier == "C")
    vacancy_months = VACANCY_MONTHS_TIER_C_STUDENT if is_student_tier_c else VACANCY_MONTHS_TIER_A_B
    vacancy_reserve = (annual_rent / 12) * vacancy_months

    return (
        cam_annual
        + tax_annual
        + insurance_annual
        + agent_annual
        + maintenance_annual
        + income_tax_annual
        + vacancy_reserve
    )


# ---------------------------------------------------------------------------
# CoCR gate (leveraged purchase)
# ---------------------------------------------------------------------------


def _compute_cocr(
    price_baht: float,
    net_annual_income: float,
    ltv_pct: float,
    mortgage_rate: float,
    reno_pct: float,
) -> tuple[float, float]:
    """Return (cocr, dscr) for leveraged purchase scenario."""
    loan = price_baht * ltv_pct
    equity = price_baht * (1 - ltv_pct)
    closing_costs = price_baht * 0.02  # transfer fee approximation
    reno_cost = price_baht * reno_pct
    total_equity_invested = equity + closing_costs + reno_cost

    # Annual debt service (simple interest, full amortisation ignored for screening)
    annual_debt_service = loan * mortgage_rate

    cash_flow = net_annual_income - annual_debt_service
    cocr = cash_flow / total_equity_invested if total_equity_invested > 0 else 0.0
    dscr = net_annual_income / annual_debt_service if annual_debt_service > 0 else 999.0

    return cocr, dscr


# ---------------------------------------------------------------------------
# Summer vacancy effective yield
# ---------------------------------------------------------------------------


def _apply_summer_vacancy(gry: float, bts_tier: str, anchor_sub_type: str) -> float:
    """Apply summer vacancy factor for Tier C + university properties."""
    tier = bts_tier.upper() if bts_tier else "C"
    if anchor_sub_type == "university" and tier == "C":
        return gry * SUMMER_VACANCY_FACTOR
    return gry


# ---------------------------------------------------------------------------
# Scoring sub-components
# ---------------------------------------------------------------------------


def _score_gry(gry: float, gry_min: float, gry_good: float, gry_best: float) -> float:
    """Score GRY component 0–100."""
    if gry >= gry_best:
        return 100.0
    if gry >= gry_good:
        return 70.0 + 30.0 * (gry - gry_good) / (gry_best - gry_good)
    if gry >= gry_min:
        return 40.0 + 30.0 * (gry - gry_min) / (gry_good - gry_min)
    return 0.0


def _score_nry(nry: float) -> float:
    """Score NRY component 0–100."""
    if nry >= 0.07:
        return 100.0
    if nry >= 0.05:
        return 70.0 + 30.0 * (nry - 0.05) / 0.02
    if nry >= 0.03:
        return 40.0 + 30.0 * (nry - 0.03) / 0.02
    return 10.0


def _score_das(das: int) -> float:
    """Score DAS component 0–100."""
    if das >= 60:
        return 100.0
    if das >= 40:
        return 60.0 + 40.0 * (das - 40) / 20.0
    if das >= 25:
        return 20.0 + 40.0 * (das - 25) / 15.0
    return 0.0


def _score_supply_pressure(supply_pct: Optional[float]) -> float:
    """Score supply pressure component 0–100 (higher = less supply = better)."""
    if supply_pct is None:
        return 50.0  # neutral when unknown
    if supply_pct >= SUPPLY_PRESSURE_SEVERE:
        return 0.0
    if supply_pct >= 15.0:
        return 20.0
    if supply_pct >= 10.0:
        return 50.0
    if supply_pct >= 5.0:
        return 75.0
    return 100.0


def _score_building_quality(candidate: NpaCandidate) -> float:
    """Score building quality (developer tier, building age) 0–100."""
    score = 50.0  # base
    dev = (candidate.market_developer or "").lower()

    if any(d in dev for d in TIER1_DEVELOPERS):
        score += 30.0
    elif any(d in dev for d in TIER2_DEVELOPERS):
        score += 15.0

    age = candidate.building_age
    if age is not None:
        if 8 <= age <= 18:  # sweet spot
            score += 20.0
        elif age < 8:
            score += 10.0
        elif age > 20:
            score -= 20.0

    return max(0.0, min(100.0, score))


def _score_liquidity(units_for_rent: Optional[int]) -> float:
    """Score rental liquidity based on active rental listing count 0–100."""
    if units_for_rent is None:
        return 30.0  # penalise unknown
    if units_for_rent >= 10:
        return 100.0
    if units_for_rent >= 5:
        return 70.0
    if units_for_rent >= 3:
        return 40.0
    return 0.0


# ---------------------------------------------------------------------------
# Main scoring function
# ---------------------------------------------------------------------------


def score_rental(candidate: NpaCandidate, profile: InvestorProfile) -> StrategyScore:
    """Score a candidate NPA property for the buy-and-rent strategy.

    Returns a StrategyScore with verdict STRONG_BUY / BUY / WATCH / AVOID.
    """
    flags: list[str] = []
    reject_reasons: list[str] = []
    key_metrics: dict[str, Optional[float]] = {}

    # ------------------------------------------------------------------
    # Step 1: Demand Anchor Score (DAS)
    # ------------------------------------------------------------------
    das, anchor_sub_type = _compute_das(candidate)
    key_metrics["das"] = float(das)

    if das < DAS_HARD_REJECT:
        reject_reasons.append(f"DAS {das} < 25: no structural tenant demand")

    if das < DAS_GATE_MIN:
        flags.append(f"DAS {das} below gate minimum 40 — penalty applied")

    # ------------------------------------------------------------------
    # Step 2: Seasonal check
    # ------------------------------------------------------------------
    current_month = datetime.now().month
    is_q2 = 4 <= current_month <= 6
    apply_seasonal = is_q2

    # ------------------------------------------------------------------
    # Step 3: Adjusted annual rent & GRY
    # ------------------------------------------------------------------
    annual_rent = _adjusted_annual_rent(candidate, profile, anchor_sub_type, apply_seasonal)
    key_metrics["annual_rent_adj"] = annual_rent

    if annual_rent is None:
        reject_reasons.append("No rent data available (market_rent_median missing)")
        return StrategyScore(
            strategy=Strategy.RENT,
            sub_strategy=anchor_sub_type,
            score=0.0,
            verdict="AVOID",
            key_metrics=key_metrics,
            flags=flags,
            reject_reasons=reject_reasons,
            pass_gates=False,
        )

    gry = annual_rent / candidate.price_baht
    key_metrics["gry"] = round(gry, 4)

    # Apply summer vacancy to effective yield for Tier C university
    effective_gry = _apply_summer_vacancy(gry, candidate.bts_tier, anchor_sub_type)
    key_metrics["effective_gry"] = round(effective_gry, 4)
    if effective_gry < gry:
        flags.append(
            f"Summer vacancy applied (Tier C + university): effective GRY {effective_gry:.1%} vs gross {gry:.1%}"
        )

    # GRY threshold lookup
    threshold_key = _gry_threshold_key(anchor_sub_type, candidate.bts_tier)
    gry_reject, gry_min, gry_good, gry_best = GRY_THRESHOLDS.get(
        threshold_key, GRY_THRESHOLDS["default"]
    )
    key_metrics["gry_min_threshold"] = gry_min

    if effective_gry < gry_reject:
        reject_reasons.append(
            f"GRY {effective_gry:.1%} < reject threshold {gry_reject:.1%} for {threshold_key}"
        )

    # ------------------------------------------------------------------
    # Step 4: NRY (Net Rental Yield)
    # ------------------------------------------------------------------
    annual_costs = _annual_holding_costs(
        candidate.price_baht,
        candidate.size_sqm,
        annual_rent,
        candidate.bts_tier,
        anchor_sub_type,
    )
    net_annual_income = annual_rent - annual_costs
    nry = net_annual_income / candidate.price_baht
    key_metrics["nry"] = round(nry, 4)
    key_metrics["annual_holding_costs"] = round(annual_costs, 0)

    gnhc = 1.0 - (nry / gry) if gry > 0 else 1.0
    key_metrics["gnhc"] = round(gnhc, 4)
    if gnhc > 0.50:
        flags.append(f"GNHC {gnhc:.1%} > 50%: cost structure is borderline — consider price negotiation")

    # NRY hard reject: no leverage rescue possible
    if nry < NRY_HARD_REJECT:
        reject_reasons.append(
            f"NRY {nry:.1%} < 1.5% hard floor — negative carry even with leverage"
        )

    # ------------------------------------------------------------------
    # Step 5: CoCR parallel gate (leveraged purchase)
    # ------------------------------------------------------------------
    cocr: Optional[float] = None
    dscr: Optional[float] = None
    leveraged_ok = False
    tier_key = (candidate.bts_tier or "C").upper()
    cocr_tier_min = COCR_TIER.get(tier_key, COCR_MIN)

    if profile.purchase_mode == "mortgage" and profile.ltv_pct > 0:
        cocr, dscr = _compute_cocr(
            candidate.price_baht,
            net_annual_income,
            profile.ltv_pct,
            profile.mortgage_rate,
            profile.renovation_budget_pct,
        )
        key_metrics["cocr"] = round(cocr, 4)
        key_metrics["dscr"] = round(dscr, 4)

        if cocr >= cocr_tier_min and dscr >= DSCR_MIN:
            leveraged_ok = True
            flags.append(
                f"CoCR {cocr:.1%} >= {cocr_tier_min:.1%} gate with DSCR {dscr:.2f}: leveraged purchase viable"
            )
        else:
            flags.append(
                f"CoCR {cocr:.1%} < {cocr_tier_min:.1%} or DSCR {dscr:.2f} < {DSCR_MIN}: leverage does not rescue"
            )

    # NRY gate: reject only if leverage also fails
    if NRY_HARD_REJECT <= nry < NRY_CASH_MIN and not leveraged_ok:
        reject_reasons.append(
            f"NRY {nry:.1%} < 3% and CoCR/DSCR gate not met — reject for cash and leveraged"
        )

    # ------------------------------------------------------------------
    # Step 6: Comparable rental listings (liquidity gate)
    # ------------------------------------------------------------------
    units_for_rent = candidate.market_units_for_rent
    key_metrics["units_for_rent"] = float(units_for_rent) if units_for_rent else None

    if units_for_rent is not None and units_for_rent < CRLC_REJECT:
        reject_reasons.append(
            f"CRLC {units_for_rent} < 3: no verifiable rental market"
        )
    elif units_for_rent is not None and units_for_rent < CRLC_THIN:
        flags.append(f"CRLC {units_for_rent}: thin rental market — verify with local agent")

    # ------------------------------------------------------------------
    # Step 7: Price-to-Rent Multiple (PRM)
    # ------------------------------------------------------------------
    monthly_rent_adj = annual_rent / 12
    prm = candidate.price_baht / (monthly_rent_adj * 12)
    key_metrics["prm"] = round(prm, 2)

    if prm > PRM_REJECT:
        reject_reasons.append(f"PRM {prm:.1f}x > 20x: annual rent < 5% of price")

    # ------------------------------------------------------------------
    # Step 8: Discount check
    # ------------------------------------------------------------------
    discount = candidate.real_discount_pct or 0.0
    key_metrics["real_discount_pct"] = discount

    tier = (candidate.bts_tier or "C").upper()
    min_discount = (
        DISCOUNT_TIER_A if tier == "A"
        else DISCOUNT_TIER_B if tier == "B"
        else DISCOUNT_TIER_C
    )

    # ------------------------------------------------------------------
    # Step 9: Compute composite score
    # ------------------------------------------------------------------
    # Weights: Yield 30%, DAS 25%, Supply 20%, Building 15%, Liquidity 10%
    # Yield = average of GRY component (15%) and NRY component (15%, or CoCR if leveraged)

    gry_component = _score_gry(effective_gry, gry_min, gry_good, gry_best)

    if leveraged_ok and cocr is not None:
        # Score NRY component via CoCR when leveraged
        nry_component = min(100.0, (cocr / cocr_tier_min) * 60.0)
    else:
        nry_component = _score_nry(nry)

    yield_score = (gry_component * 0.50 + nry_component * 0.50)  # equal split within yield bucket

    das_score = _score_das(das)
    supply_score = _score_supply_pressure(candidate.supply_pressure_pct)
    building_score = _score_building_quality(candidate)
    liquidity_score = _score_liquidity(units_for_rent)

    composite = (
        yield_score * 0.30
        + das_score * 0.25
        + supply_score * 0.20
        + building_score * 0.15
        + liquidity_score * 0.10
    )

    key_metrics["score_yield"] = round(yield_score, 1)
    key_metrics["score_das"] = round(das_score, 1)
    key_metrics["score_supply"] = round(supply_score, 1)
    key_metrics["score_building"] = round(building_score, 1)
    key_metrics["score_liquidity"] = round(liquidity_score, 1)

    # ------------------------------------------------------------------
    # Step 10: Verdict
    # ------------------------------------------------------------------
    pass_gates = len(reject_reasons) == 0

    gry_passes = effective_gry >= gry_min
    nry_passes = nry >= NRY_CASH_MIN or leveraged_ok

    if not pass_gates:
        verdict = "AVOID"
    elif composite >= 80 and discount >= 0.30 and gry_passes and nry_passes:
        verdict = "STRONG_BUY"
    elif composite >= 60 and discount >= min_discount and gry_passes:
        verdict = "BUY"
    elif composite >= 40:
        verdict = "WATCH"
    else:
        verdict = "AVOID"

    return StrategyScore(
        strategy=Strategy.RENT,
        sub_strategy=anchor_sub_type,
        score=round(composite, 1),
        verdict=verdict,
        key_metrics=key_metrics,
        flags=flags,
        reject_reasons=reject_reasons,
        pass_gates=pass_gates,
    )

"""
Flip Strategy Scorer for Multi-Strategy NPA Screener v2.

Evaluates three sub-strategies (Quick Flip, Medium Hold, Renovation Flip)
and returns the best viable one.
"""

from typing import Optional

from constants import (
    CAM_DEFAULT_SQM,
    FLIP_MAX_ABSORPTION_MONTHS,
    FLIP_MEDIUM_MIN_DISCOUNT,
    FLIP_MIN_ANNUALIZED_RETURN,
    FLIP_MIN_NET_MARGIN,
    FLIP_QUICK_MIN_DISCOUNT,
    RENO_MAX_PCT,
    SBT_RATE,
    STAMP_DUTY_RATE,
    SUPPLY_PRESSURE_SEVERE,
    TRANSFER_FEE_RATE,
    VERIFIED_SALE_MULTIPLIER,
    WHT_RATE,
)
from models_v2 import NpaCandidate, InvestorProfile, Strategy, StrategyScore

# ---------------------------------------------------------------------------
# Internal constants (flip-specific, not in constants.py)
# ---------------------------------------------------------------------------

# Entry discount thresholds (vs verified market price = listed × 0.92)
_QUICK_MIN_DISCOUNT = 0.35       # 35% vs verified (≈40% vs listed)
_MEDIUM_MIN_DISCOUNT = 0.25      # from FLIP_MEDIUM_MIN_DISCOUNT
_RENO_MIN_DISCOUNT = 0.30        # 30% vs verified pre-reno

# Absorption thresholds (months of supply, using supply_pressure_pct as proxy)
_ABSORPTION_GREEN = 30.0         # ≤30 months → all sub-strategies viable
_ABSORPTION_YELLOW = 45.0        # 31–45 → medium hold + reno only
_ABSORPTION_ORANGE = 60.0        # 46–60 → reno only (if discount ≥40%)

# Net margin / annualized return minimums
_QUICK_MIN_NET_MARGIN = 0.20     # 20% net margin (updated per M8 in research)
_QUICK_MIN_IRR = 0.20            # 20% p.a.
_MEDIUM_ANNUALIZED_MIN = 0.15    # 15% p.a.
_RENO_MIN_NET_MARGIN = 0.22      # 22% post-reno net margin
_RENO_MIN_ROI = 2.0              # Renovation ROI > 2x (200%)
_ABSOLUTE_MIN_NET_MARGIN = 0.10  # Universal floor — reject if below this

# Exit price floor for quick flip (mortgage-eligible buyer pool)
_QUICK_EXIT_FLOOR_THB = 3_500_000

# Acquisition cost as fraction of purchase price
_ACQUISITION_COST_PCT = 0.025    # midpoint of 2–3%

# Quick flip hold months (midpoint)
_QUICK_HOLD_MONTHS = 9
_MEDIUM_HOLD_MONTHS = 24         # 2-year midpoint for medium hold
_RENO_HOLD_MONTHS = 12           # 6–18 month midpoint

# WHT effective rate (corrected per fineng-researcher)
_WHT_EFFECTIVE_RATE = 0.03

# Scoring weights (must sum to 1.0)
_W_DISCOUNT = 0.35
_W_NET_MARGIN = 0.20
_W_ABSORPTION = 0.20
_W_LIQUIDITY = 0.15
_W_RENO_UPSIDE = 0.10


# ---------------------------------------------------------------------------
# Helper: compute verified market price per sqm
# ---------------------------------------------------------------------------

def _verified_market_price_sqm(candidate: NpaCandidate) -> Optional[float]:
    """Returns verified (transaction) market price per sqm, or None if unavailable."""
    if candidate.market_price_sqm is None:
        return None
    return candidate.market_price_sqm * VERIFIED_SALE_MULTIPLIER


def _npa_price_sqm(candidate: NpaCandidate) -> Optional[float]:
    """Returns NPA price per sqm, using pre-computed field or deriving it."""
    if candidate.price_sqm is not None:
        return float(candidate.price_sqm)
    if candidate.size_sqm and candidate.size_sqm > 0:
        return candidate.price_baht / candidate.size_sqm
    return None


def _entry_discount(candidate: NpaCandidate) -> Optional[float]:
    """
    Returns entry discount as a fraction (0.0–1.0) vs verified market price.
    Uses pre-computed real_discount_pct if available (already vs verified market).
    """
    if candidate.real_discount_pct is not None:
        return candidate.real_discount_pct / 100.0

    verified = _verified_market_price_sqm(candidate)
    npa_psm = _npa_price_sqm(candidate)
    if verified is None or npa_psm is None or verified <= 0:
        return None
    return (verified - npa_psm) / verified


# ---------------------------------------------------------------------------
# Helper: absorption proxy from supply_pressure_pct
# ---------------------------------------------------------------------------

def _absorption_months_proxy(candidate: NpaCandidate) -> Optional[float]:
    """
    Maps supply_pressure_pct to an approximate absorption months value.
    supply_pressure_pct = units_for_sale / total_units * 100.
    Higher supply pressure → higher absorption months.
    Calibrated to Bangkok market (Tier A ≈ 30mo at ~8% supply pressure).
    Returns None if data unavailable.
    """
    spp = candidate.supply_pressure_pct
    if spp is None:
        return None
    # Linear interpolation: 0% → 10mo, 10% → 30mo, 25% → 60mo, 40%+ → 90mo
    if spp <= 0:
        return 10.0
    if spp <= 10.0:
        return 10.0 + (spp / 10.0) * 20.0      # 10–30 months
    if spp <= 25.0:
        return 30.0 + ((spp - 10.0) / 15.0) * 30.0   # 30–60 months
    return 60.0 + ((spp - 25.0) / 15.0) * 30.0        # 60–90+ months


# ---------------------------------------------------------------------------
# Helper: liquidity score from market_confidence + bts_tier
# ---------------------------------------------------------------------------

def _liquidity_score(candidate: NpaCandidate) -> float:
    """
    Returns a 0.0–1.0 liquidity score based on market_confidence and BTS tier.
    """
    conf_score = {
        "high": 1.0,
        "medium": 0.65,
        "low": 0.35,
        "none": 0.15,
    }.get(candidate.market_confidence, 0.15)

    tier_score = {
        "A": 1.0,
        "B": 0.65,
        "C": 0.30,
        "": 0.20,
    }.get(candidate.bts_tier, 0.20)

    return conf_score * 0.6 + tier_score * 0.4


# ---------------------------------------------------------------------------
# Helper: exit cost fraction for a given hold in months
# ---------------------------------------------------------------------------

def _exit_cost_fraction(hold_months: int, tabien_baan: bool) -> float:
    """
    Returns total exit cost as a fraction of exit price.
    Includes SBT (or stamp duty), WHT, transfer fee.
    tabien_baan: if True and hold < 60mo, SBT is exempt.
    """
    if hold_months >= 60:
        sbt_or_stamp = STAMP_DUTY_RATE
    elif tabien_baan:
        sbt_or_stamp = 0.0   # registered in unit → SBT exempt
    else:
        sbt_or_stamp = SBT_RATE

    return sbt_or_stamp + _WHT_EFFECTIVE_RATE + TRANSFER_FEE_RATE


# ---------------------------------------------------------------------------
# Helper: compute net margin for a flip
# ---------------------------------------------------------------------------

def _compute_net_margin(
    entry_discount: float,
    hold_months: int,
    size_sqm: Optional[float],
    tabien_baan: bool,
    reno_cost_fraction: float = 0.0,
    npa_price_per_sqm: Optional[float] = None,
) -> float:
    """
    Returns net profit margin as a fraction of purchase price.

    All values normalised: purchase = 1.0.
    exit_price = 1.0 / (1 - entry_discount)  [at verified market price]
    Costs: acquisition + CAM holding + exit taxes + reno.

    CAM holding cost: expressed as a fraction of purchase price.
    Requires npa_price_per_sqm to convert absolute CAM (THB/sqm/mo) to fraction.
    Falls back to a 0.25%/month estimate if unavailable.
    """
    purchase = 1.0
    exit_price = purchase / (1.0 - entry_discount) if entry_discount < 1.0 else purchase

    acquisition = purchase * _ACQUISITION_COST_PCT

    # CAM holding cost as fraction of purchase price
    if size_sqm and size_sqm > 0 and npa_price_per_sqm and npa_price_per_sqm > 0:
        # purchase_price_total = npa_price_per_sqm * size_sqm
        # cam_total_thb = CAM_DEFAULT_SQM * size_sqm * hold_months
        # holding_cost_fraction = cam_total_thb / purchase_price_total
        #                       = CAM_DEFAULT_SQM * hold_months / npa_price_per_sqm
        holding_cost = CAM_DEFAULT_SQM * hold_months / npa_price_per_sqm
    else:
        holding_cost = 0.0025 * hold_months  # ~0.25%/month fallback

    exit_fraction = _exit_cost_fraction(hold_months, tabien_baan)
    exit_cost = exit_price * exit_fraction

    reno_cost = purchase * reno_cost_fraction

    gross_profit = exit_price - purchase
    net_profit = gross_profit - acquisition - holding_cost - exit_cost - reno_cost
    return net_profit / purchase


# ---------------------------------------------------------------------------
# Helper: annualized return from net margin
# ---------------------------------------------------------------------------

def _annualized_return(net_margin: float, hold_months: int) -> float:
    """Converts net margin to annualized return."""
    if hold_months <= 0:
        return 0.0
    base = 1.0 + net_margin
    if base <= 0:
        return -1.0  # total loss floor
    return base ** (12.0 / hold_months) - 1.0


# ---------------------------------------------------------------------------
# Helper: score a single metric 0.0–1.0 with linear scaling
# ---------------------------------------------------------------------------

def _score_between(value: float, floor: float, target: float) -> float:
    """
    Scales value linearly: 0.0 at floor, 1.0 at target (or above).
    Returns 0.0 if value < floor.
    """
    if value < floor:
        return 0.0
    if value >= target:
        return 1.0
    return (value - floor) / (target - floor)


# ---------------------------------------------------------------------------
# Sub-strategy scorers
# ---------------------------------------------------------------------------

def _score_quick_flip(
    candidate: NpaCandidate,
    profile: InvestorProfile,
    discount: float,
    absorption_months: Optional[float],
    liquidity: float,
) -> tuple[float, list[str], list[str], dict]:
    """
    Returns (score 0–100, flags, reject_reasons, key_metrics).
    score=0 with non-empty reject_reasons means hard reject.
    """
    flags: list[str] = []
    rejects: list[str] = []
    metrics: dict = {}

    # Hard gate: LED/SAM can't meet transfer deadline
    if candidate.source.upper() in ("LED", "SAM"):
        rejects.append("QUICK_FLIP_INELIGIBLE: LED/SAM auction cannot meet transfer deadline")
        return 0.0, flags, rejects, metrics

    # Hard gate: force cash for <24mo holds
    if profile.purchase_mode == "mortgage":
        flags.append("CASH_ONLY: quick flip requires cash purchase (hold < 24mo)")

    # Hard gate: exit price floor
    if candidate.price_baht > 0:
        # Estimated exit price at verified market
        exit_price = candidate.price_baht / (1.0 - discount) if discount < 1.0 else candidate.price_baht
        metrics["estimated_exit_price"] = round(exit_price)
        if exit_price < _QUICK_EXIT_FLOOR_THB:
            rejects.append(f"EXIT_BELOW_FLOOR: estimated exit {exit_price:,.0f} < 3.5M THB minimum")
            return 0.0, flags, rejects, metrics

    # Hard gate: absorption
    if absorption_months is not None and absorption_months > _ABSORPTION_GREEN:
        rejects.append(f"SLOW_ABSORPTION: {absorption_months:.0f}mo supply > 30mo max for quick flip")
        return 0.0, flags, rejects, metrics

    # Net margin
    net_margin = _compute_net_margin(
        discount,
        _QUICK_HOLD_MONTHS,
        candidate.size_sqm,
        profile.tabien_baan,
        npa_price_per_sqm=_npa_price_sqm(candidate),
    )
    ann_return = _annualized_return(net_margin, _QUICK_HOLD_MONTHS)
    metrics["net_margin_pct"] = round(net_margin * 100, 1)
    metrics["annualized_return_pct"] = round(ann_return * 100, 1)
    metrics["entry_discount_pct"] = round(discount * 100, 1)

    if net_margin < _ABSOLUTE_MIN_NET_MARGIN:
        rejects.append(f"NET_MARGIN_INSUFFICIENT: {net_margin*100:.1f}% < 10% absolute floor")
        return 0.0, flags, rejects, metrics

    if ann_return < _QUICK_MIN_IRR:
        flags.append(f"BELOW_OPPORTUNITY_COST: {ann_return*100:.1f}% p.a. < 20% quick flip hurdle")

    # Score components
    s_discount = _score_between(discount, _QUICK_MIN_DISCOUNT, 0.50)
    s_margin = _score_between(net_margin, _ABSOLUTE_MIN_NET_MARGIN, _QUICK_MIN_NET_MARGIN)
    s_absorption = _score_between(
        _ABSORPTION_GREEN - (absorption_months or _ABSORPTION_GREEN),
        0, _ABSORPTION_GREEN
    ) if absorption_months is not None else 0.5
    s_liquidity = liquidity

    score_raw = (
        s_discount * _W_DISCOUNT
        + s_margin * _W_NET_MARGIN
        + s_absorption * _W_ABSORPTION
        + s_liquidity * _W_LIQUIDITY
    )
    # Reno upside weight redistributed to liquidity for non-reno sub-strategies
    score_raw = score_raw / (1.0 - _W_RENO_UPSIDE)
    score = min(round(score_raw * 100, 1), 100.0)

    metrics["liquidity_score"] = round(liquidity, 2)
    return score, flags, rejects, metrics


def _score_medium_hold(
    candidate: NpaCandidate,
    profile: InvestorProfile,
    discount: float,
    absorption_months: Optional[float],
    liquidity: float,
) -> tuple[float, list[str], list[str], dict]:
    flags: list[str] = []
    rejects: list[str] = []
    metrics: dict = {}

    # Hard gate: absorption
    if absorption_months is not None and absorption_months > _ABSORPTION_YELLOW:
        rejects.append(f"SLOW_ABSORPTION: {absorption_months:.0f}mo supply > 45mo for medium hold")
        return 0.0, flags, rejects, metrics

    # Leverage allowed for 1–3yr hold
    if profile.purchase_mode == "mortgage" and profile.hold_horizon_years < 2:
        flags.append("CASH_ONLY: mortgage inadvisable for <24mo hold")

    # Net margin at profile horizon (capped at 36mo)
    hold_months = min(profile.hold_horizon_years * 12, _MEDIUM_HOLD_MONTHS)
    npa_psm = _npa_price_sqm(candidate)
    net_margin = _compute_net_margin(
        discount,
        hold_months,
        candidate.size_sqm,
        profile.tabien_baan,
        npa_price_per_sqm=npa_psm,
    )
    ann_return = _annualized_return(net_margin, hold_months)
    metrics["net_margin_pct"] = round(net_margin * 100, 1)
    metrics["annualized_return_pct"] = round(ann_return * 100, 1)
    metrics["entry_discount_pct"] = round(discount * 100, 1)
    metrics["hold_months"] = hold_months

    if net_margin < _ABSOLUTE_MIN_NET_MARGIN:
        rejects.append(f"NET_MARGIN_INSUFFICIENT: {net_margin*100:.1f}% < 10% absolute floor")
        return 0.0, flags, rejects, metrics

    if ann_return < _MEDIUM_ANNUALIZED_MIN:
        flags.append(f"BELOW_OPPORTUNITY_COST: {ann_return*100:.1f}% p.a. < 15% hurdle")

    # Timeline sensitivity: check delayed exit (2× hold)
    delayed_margin = _compute_net_margin(
        discount, hold_months * 2, candidate.size_sqm, profile.tabien_baan,
        npa_price_per_sqm=npa_psm,
    )
    delayed_irr = _annualized_return(delayed_margin, hold_months * 2)
    if delayed_irr < 0.16:
        flags.append(f"TIMELINE_SENSITIVE: delayed IRR {delayed_irr*100:.1f}% < 16% benchmark")
    metrics["delayed_irr_pct"] = round(delayed_irr * 100, 1)

    # Score components
    s_discount = _score_between(discount, _MEDIUM_MIN_DISCOUNT, 0.45)
    s_margin = _score_between(ann_return, _ABSOLUTE_MIN_NET_MARGIN, _MEDIUM_ANNUALIZED_MIN)
    s_absorption = _score_between(
        _ABSORPTION_YELLOW - (absorption_months or _ABSORPTION_YELLOW),
        0, _ABSORPTION_YELLOW
    ) if absorption_months is not None else 0.5
    s_liquidity = liquidity

    score_raw = (
        s_discount * _W_DISCOUNT
        + s_margin * _W_NET_MARGIN
        + s_absorption * _W_ABSORPTION
        + s_liquidity * _W_LIQUIDITY
    )
    score_raw = score_raw / (1.0 - _W_RENO_UPSIDE)
    score = min(round(score_raw * 100, 1), 100.0)

    metrics["liquidity_score"] = round(liquidity, 2)
    return score, flags, rejects, metrics


def _score_renovation_flip(
    candidate: NpaCandidate,
    profile: InvestorProfile,
    discount: float,
    absorption_months: Optional[float],
    liquidity: float,
) -> tuple[float, list[str], list[str], dict]:
    flags: list[str] = []
    rejects: list[str] = []
    metrics: dict = {}

    # Hard gate: absorption
    if absorption_months is not None and absorption_months > _ABSORPTION_ORANGE:
        rejects.append(f"SLOW_ABSORPTION: {absorption_months:.0f}mo supply > 60mo for reno flip")
        return 0.0, flags, rejects, metrics

    # Renovation budget
    reno_pct = profile.renovation_budget_pct if profile.renovation_budget_pct > 0 else 0.10
    if reno_pct > RENO_MAX_PCT:
        flags.append(f"RENO_COST_HIGH: {reno_pct*100:.0f}% > 20% max of purchase price")

    # Net margin including reno cost
    net_margin = _compute_net_margin(
        discount,
        _RENO_HOLD_MONTHS,
        candidate.size_sqm,
        profile.tabien_baan,
        reno_cost_fraction=reno_pct,
        npa_price_per_sqm=_npa_price_sqm(candidate),
    )
    ann_return = _annualized_return(net_margin, _RENO_HOLD_MONTHS)
    metrics["net_margin_pct"] = round(net_margin * 100, 1)
    metrics["annualized_return_pct"] = round(ann_return * 100, 1)
    metrics["entry_discount_pct"] = round(discount * 100, 1)
    metrics["reno_cost_pct"] = round(reno_pct * 100, 1)

    if net_margin < _ABSOLUTE_MIN_NET_MARGIN:
        rejects.append(f"NET_MARGIN_INSUFFICIENT: {net_margin*100:.1f}% < 10% absolute floor")
        return 0.0, flags, rejects, metrics

    # Renovation ROI: value uplift / reno cost
    # Uplift = entry_discount × purchase price (the "gap" reno bridges to market)
    # Reno cost = reno_pct × purchase price
    if reno_pct > 0:
        reno_roi = discount / reno_pct  # simplified: discount gap / reno fraction
        metrics["reno_roi_ratio"] = round(reno_roi, 2)
        if reno_roi < 1.0:
            rejects.append(f"RENO_ROI_NEGATIVE: reno ROI {reno_roi:.2f}x < 1x")
            return 0.0, flags, rejects, metrics
        if reno_roi < _RENO_MIN_ROI:
            flags.append(f"RENO_ROI_LOW: {reno_roi:.2f}x < 2x target")
        s_reno = _score_between(reno_roi, 1.0, _RENO_MIN_ROI)
    else:
        s_reno = 0.5  # no reno budget provided, neutral

    # Score components (reno upside replaces w=0.10)
    s_discount = _score_between(discount, _RENO_MIN_DISCOUNT, 0.45)
    s_margin = _score_between(net_margin, _ABSOLUTE_MIN_NET_MARGIN, _RENO_MIN_NET_MARGIN)
    s_absorption = _score_between(
        _ABSORPTION_ORANGE - (absorption_months or _ABSORPTION_ORANGE),
        0, _ABSORPTION_ORANGE
    ) if absorption_months is not None else 0.5
    s_liquidity = liquidity

    score_raw = (
        s_discount * _W_DISCOUNT
        + s_margin * _W_NET_MARGIN
        + s_absorption * _W_ABSORPTION
        + s_liquidity * _W_LIQUIDITY
        + s_reno * _W_RENO_UPSIDE
    )
    score = min(round(score_raw * 100, 1), 100.0)

    metrics["liquidity_score"] = round(liquidity, 2)
    return score, flags, rejects, metrics


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def score_flip(candidate: NpaCandidate, profile: InvestorProfile) -> StrategyScore:
    """
    Score a candidate NPA property for flip viability.

    Evaluates three sub-strategies (quick_flip, medium_hold, renovation_flip)
    and returns the StrategyScore for the best viable one.

    Auto-rejects if:
    - entry discount is negative (NPA at or above market)
    - supply pressure exceeds SUPPLY_PRESSURE_SEVERE
    - no market price data is available
    """
    all_flags: list[str] = []
    all_rejects: list[str] = []

    # --- Pre-compute shared inputs ---
    discount = _entry_discount(candidate)

    if discount is None:
        return StrategyScore(
            strategy=Strategy.FLIP,
            sub_strategy="",
            score=0.0,
            verdict="AVOID",
            key_metrics={},
            flags=[],
            reject_reasons=["NO_MARKET_DATA: cannot compute entry discount without market_price_sqm"],
            pass_gates=False,
        )

    if discount <= 0:
        return StrategyScore(
            strategy=Strategy.FLIP,
            sub_strategy="",
            score=0.0,
            verdict="AVOID",
            key_metrics={"entry_discount_pct": round(discount * 100, 1)},
            flags=[],
            reject_reasons=["NEGATIVE_DISCOUNT: NPA price at or above verified market"],
            pass_gates=False,
        )

    # Universal supply pressure gate
    if candidate.supply_pressure_pct is not None and candidate.supply_pressure_pct >= SUPPLY_PRESSURE_SEVERE:
        return StrategyScore(
            strategy=Strategy.FLIP,
            sub_strategy="",
            score=0.0,
            verdict="AVOID",
            key_metrics={"supply_pressure_pct": candidate.supply_pressure_pct},
            flags=[],
            reject_reasons=[f"SEVERE_SUPPLY_PRESSURE: {candidate.supply_pressure_pct:.1f}% >= {SUPPLY_PRESSURE_SEVERE}% threshold"],
            pass_gates=False,
        )

    absorption_months = _absorption_months_proxy(candidate)
    liquidity = _liquidity_score(candidate)

    # --- Score each sub-strategy ---
    quick_score, quick_flags, quick_rejects, quick_metrics = _score_quick_flip(
        candidate, profile, discount, absorption_months, liquidity
    )
    medium_score, medium_flags, medium_rejects, medium_metrics = _score_medium_hold(
        candidate, profile, discount, absorption_months, liquidity
    )
    reno_score, reno_flags, reno_rejects, reno_metrics = _score_renovation_flip(
        candidate, profile, discount, absorption_months, liquidity
    )

    # Collect all rejects for context
    all_rejects = list({*quick_rejects, *medium_rejects, *reno_rejects})
    all_flags = list({*quick_flags, *medium_flags, *reno_flags})

    # --- Pick the best viable sub-strategy ---
    candidates: list[tuple[float, str, dict, list[str], list[str]]] = []
    if not quick_rejects:
        candidates.append((quick_score, "quick_flip", quick_metrics, quick_flags, quick_rejects))
    if not medium_rejects:
        candidates.append((medium_score, "medium_hold", medium_metrics, medium_flags, medium_rejects))
    if not reno_rejects:
        candidates.append((reno_score, "renovation_flip", reno_metrics, reno_flags, reno_rejects))

    if not candidates:
        return StrategyScore(
            strategy=Strategy.FLIP,
            sub_strategy="",
            score=0.0,
            verdict="AVOID",
            key_metrics={"entry_discount_pct": round(discount * 100, 1)},
            flags=all_flags,
            reject_reasons=all_rejects,
            pass_gates=False,
        )

    best_score, best_sub, best_metrics, best_flags, _ = max(candidates, key=lambda x: x[0])

    # --- Map score to verdict ---
    if best_score >= 75:
        verdict = "STRONG_BUY"
    elif best_score >= 55:
        verdict = "BUY"
    elif best_score >= 40:
        verdict = "WATCH"
    else:
        verdict = "AVOID"

    # Add absorption months to metrics if available
    if absorption_months is not None:
        best_metrics = {**best_metrics, "absorption_months_proxy": round(absorption_months, 1)}

    return StrategyScore(
        strategy=Strategy.FLIP,
        sub_strategy=best_sub,
        score=best_score,
        verdict=verdict,
        key_metrics=best_metrics,
        flags=best_flags,
        reject_reasons=[],  # viable — no hard rejects on the winning sub-strategy
        pass_gates=True,
    )

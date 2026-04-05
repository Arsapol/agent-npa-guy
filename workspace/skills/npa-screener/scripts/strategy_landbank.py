"""
Land banking strategy scorer for Multi-Strategy NPA Screener v2.

Only scores LAND and HOUSE_AND_LAND property types.
Research source: workspace/research/strategies/land-banking-strategy.md
"""

from typing import Optional

from constants import EQUITY_COST
from models_v2 import InvestorProfile, NpaCandidate, PropertyType, Strategy, StrategyScore

# --- Land tax rates (Land and Building Tax Act B.E. 2562) ---
# Vacant land escalates every 3 years, capped at 3.0%
_LAND_TAX_VACANT = {
    (0, 3): 0.003,   # Years 1-3
    (3, 6): 0.006,   # Years 4-6
    (6, 9): 0.009,   # Years 7-9
}
_LAND_TAX_DEFAULT = 0.009  # Beyond year 9
_LAND_TAX_AGRICULTURAL = 0.0015  # If registered for agricultural use
_MAINTENANCE_RATE = 0.001  # ~0.1% of purchase price annually

# --- Infrastructure status weight multipliers ---
_INFRA_STATUS_MULTIPLIERS = {
    "confirmed": 1.0,
    "approved": 0.7,
    "planned": 0.3,
    "rumored": 0.0,
}

# --- BTS distance decay (used as transit proximity proxy) ---
# Mirrors TPS distance decay in research doc
_BTS_DISTANCE_DECAY = [
    (500, 1.0),
    (1000, 0.75),
    (1500, 0.50),
    (2500, 0.20),
]

# --- Normalization bounds (research doc: Score Normalization table) ---
_NORM = {
    "lpmi": (0.05, 0.50),    # 5% → 50% YoY
    "zus": (1.0, 4.0),        # ZUS ratio 1.0 → 4.0
    "cltd": (0.15, 0.50),     # 15% → 50% discount
    "hcb": (0.035, 0.010),    # Inverted: 3.5% (bad) → 1.0% (good) annual
}

# Minimum discount for land banking (hard reject below this)
_MIN_DISCOUNT = 0.15
# Hard reject: no BTS within this distance
_MAX_BTS_DIST_M = 3000.0


def _normalize(value: float, low: float, high: float) -> float:
    """Clamp and normalize value to [0, 1]. Handles inverted ranges."""
    if high > low:
        return max(0.0, min(1.0, (value - low) / (high - low)))
    # Inverted: lower value is better (e.g. HCB)
    return max(0.0, min(1.0, (low - value) / (low - high)))


def _transit_proximity_score(nearest_bts_dist_m: Optional[float]) -> float:
    """
    Compute transit proximity score (0.0–1.0) from BTS distance.

    Uses distance decay from research doc as proxy for TPS.
    Returns 0.0 if no BTS within 3km.
    """
    if nearest_bts_dist_m is None or nearest_bts_dist_m > _MAX_BTS_DIST_M:
        return 0.0
    for threshold, score in _BTS_DISTANCE_DECAY:
        if nearest_bts_dist_m <= threshold:
            return score
    return 0.0


def _annual_holding_cost_rate(hold_horizon_years: int) -> float:
    """
    Compute blended annual holding cost rate for a given horizon.

    Returns the rate as a fraction of purchase price (e.g. 0.013 = 1.3%).
    Uses equity cost (7%) instead of BoT rate per task spec.
    """
    total_land_tax_rate = 0.0
    for year in range(1, hold_horizon_years + 1):
        for (lo, hi), rate in _LAND_TAX_VACANT.items():
            if lo < year <= hi:
                total_land_tax_rate += rate
                break
        else:
            total_land_tax_rate += _LAND_TAX_DEFAULT
    avg_land_tax_rate = total_land_tax_rate / hold_horizon_years
    return EQUITY_COST + avg_land_tax_rate + _MAINTENANCE_RATE


def _holding_cost_score(hcb_annual_rate: float) -> float:
    """Normalize HCB (inverted: lower cost = higher score)."""
    low, high = _NORM["hcb"]  # (0.035, 0.010) — inverted
    return _normalize(hcb_annual_rate, low, high)


def score_landbank(
    candidate: NpaCandidate, profile: InvestorProfile
) -> StrategyScore:
    """
    Score a candidate for land banking strategy.

    Returns AVOID for non-land property types.
    Uses BTS proximity as a proxy for transit access since we lack an
    infrastructure_projects DB. Infrastructure status assumed "confirmed"
    for operational BTS/MRT lines.
    """
    reject_reasons: list[str] = []
    flags: list[str] = []

    # --- Hard reject: wrong property type ---
    if candidate.property_type not in (PropertyType.LAND, PropertyType.HOUSE_AND_LAND):
        return StrategyScore(
            strategy=Strategy.LAND_BANK,
            sub_strategy="",
            score=0.0,
            verdict="AVOID",
            key_metrics={},
            flags=[],
            reject_reasons=[f"property_type={candidate.property_type.value} not eligible for land banking"],
            pass_gates=False,
        )

    # --- Hard reject: discount below minimum ---
    discount = candidate.real_discount_pct or 0.0
    if discount < _MIN_DISCOUNT:
        reject_reasons.append(f"real_discount_pct={discount:.1%} < 15% minimum for land banking")

    # --- Hard reject: no BTS within 3km ---
    tps_raw = _transit_proximity_score(candidate.nearest_bts_dist_m)
    if tps_raw == 0.0:
        reject_reasons.append(
            "no BTS/MRT within 3km — transit premium cannot be modelled"
        )

    if reject_reasons:
        return StrategyScore(
            strategy=Strategy.LAND_BANK,
            sub_strategy="land_banking",
            score=0.0,
            verdict="AVOID",
            key_metrics={
                "transit_proximity_score": tps_raw,
                "real_discount_pct": discount,
            },
            flags=flags,
            reject_reasons=reject_reasons,
            pass_gates=False,
        )

    # --- Component: Transit proximity (25%) ---
    # Operational BTS = confirmed → multiplier 1.0 (baked into distance decay)
    transit_component = tps_raw  # already 0.0–1.0

    # --- Component: Price momentum (20%) ---
    # We lack a live LPMI table; use real_discount_pct as a proxy signal.
    # A deep discount in a specific area can indicate motivated sellers (momentum proxy).
    # Without district_land_price_index, score at midpoint (0.5) to avoid penalising
    # properties we simply lack data for.
    lpmi_score = 0.5
    flags.append("LPMI_proxy: no district_land_price_index table; using neutral 0.5")

    # --- Component: Zoning potential (20%) ---
    # Without a live ZUS query, use BTS tier as a coarse zoning proxy.
    # BTS tier A (both <800m) → orange/high-density zone likely → ZUS ~3.0
    # BTS tier B → yellow zone likely → ZUS ~2.0
    # BTS tier C / no label → green zone likely → ZUS ~1.5
    bts_tier = (candidate.bts_tier or "").upper()
    if bts_tier == "A":
        zus_proxy = 3.0
    elif bts_tier == "B":
        zus_proxy = 2.0
    else:
        zus_proxy = 1.5
        flags.append("ZUS_proxy: tier C/unknown BTS tier; using conservative ZUS=1.5")
    zoning_component = _normalize(zus_proxy, *_NORM["zus"])

    # --- Component: Discount vs market (15%) ---
    discount_component = _normalize(discount, *_NORM["cltd"])

    # --- Component: Holding cost (15%) ---
    hcb_rate = _annual_holding_cost_rate(profile.hold_horizon_years)
    hcb_component = _holding_cost_score(hcb_rate)

    # --- Component: Development density (5%) ---
    # Use size_sqm as a development potential proxy (larger plot = higher DDP).
    # Normalize: 100 sqw (~400 sqm) min → 1000 sqm max. Score 0 if no size data.
    size = candidate.size_sqm or 0.0
    density_component = _normalize(size, 400.0, 1000.0) if size > 0 else 0.0
    if size == 0.0:
        flags.append("DDP_proxy: no size_sqm data; density component scored 0")

    # --- Composite score (weights from task spec) ---
    raw_score = (
        transit_component * 0.25
        + lpmi_score * 0.20
        + zoning_component * 0.20
        + discount_component * 0.15
        + hcb_component * 0.15
        + density_component * 0.05
        # IPC (non-transit infra, 15% in research → reduced to ~remaining weight)
        # No IPC data available without infrastructure_projects table; omit.
    )
    # Rescale to 0-100
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
        strategy=Strategy.LAND_BANK,
        sub_strategy="land_banking",
        score=score,
        verdict=verdict,
        key_metrics={
            "transit_proximity_score": round(tps_raw, 3),
            "zus_proxy": zus_proxy,
            "real_discount_pct": round(discount, 3),
            "hcb_annual_rate": round(hcb_rate, 4),
            "lpmi_score_proxy": lpmi_score,
            "density_component": round(density_component, 3),
            "composite_raw": round(raw_score, 4),
        },
        flags=flags,
        reject_reasons=[],
        pass_gates=True,
    )

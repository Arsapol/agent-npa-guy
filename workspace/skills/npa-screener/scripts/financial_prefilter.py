"""
Financial pre-filter for Multi-Strategy NPA Screener v2.

Applies 5 financial gates to quickly reject or flag candidates before
running full strategy scoring.
"""

from typing import Optional

from constants import (
    COCR_MIN,
    DSCR_MIN,
    DSCR_STRESS_BPS,
    IRR_BENCHMARK,
    MORTGAGE_RATE_FIXED,
    SBT_RATE,
    TRANSFER_FEE_RATE,
    VERIFIED_RENT_BARE,
    WHT_RATE,
)
from models_v2 import InvestorProfile, NpaCandidate, PreFilterResult

# Exit costs = SBT + transfer fee + WHT
EXIT_COST_RATE = SBT_RATE + TRANSFER_FEE_RATE + WHT_RATE  # 0.083
MINIMUM_DISCOUNT = EXIT_COST_RATE + 0.10  # 0.183

# Net income after operating expenses (35% opex)
NET_INCOME_FACTOR = 0.65

# Annual appreciation assumption for IRR approximation
ANNUAL_APPRECIATION_PCT = 0.03


def _annual_net_income(candidate: NpaCandidate) -> Optional[float]:
    """Return estimated annual net income, or None if no rent data."""
    if candidate.market_rent_median is None:
        return None
    annual_gross = candidate.market_rent_median * 12 * VERIFIED_RENT_BARE
    return annual_gross * NET_INCOME_FACTOR


def _annual_debt_service(price: float, ltv: float, rate: float) -> float:
    """Annual interest-only debt service (conservative, interest-only approximation)."""
    loan = price * ltv
    return loan * rate


def financial_prefilter(
    candidate: NpaCandidate, profile: InvestorProfile
) -> PreFilterResult:
    """
    Apply 5 financial gates to a candidate.

    Gates 1 is always applied.
    Gates 2-3 are skipped for cash investors (no debt service).
    Gate 4 is a FLAG (not reject) — stress test at mortgage_rate + 200bps.
    Gate 5 is a FLAG (not reject) — IRR approximation.
    Income-dependent gates (2-5) are skipped if no rent data.
    """
    gates: dict[str, bool] = {}
    flags: list[str] = []
    reject_reasons: list[str] = []

    price = candidate.price_baht
    discount = candidate.real_discount_pct  # e.g. 0.25 means 25% below market

    # ------------------------------------------------------------------
    # Gate 1: Entry discount < exit costs + 10%
    # ------------------------------------------------------------------
    if discount is None:
        # Cannot evaluate — treat as failing (no market data)
        gates["gate1_entry_discount"] = False
        reject_reasons.append(
            "Gate 1 FAIL: no real_discount_pct — cannot verify entry discount"
        )
    elif discount < MINIMUM_DISCOUNT:
        gates["gate1_entry_discount"] = False
        reject_reasons.append(
            f"Gate 1 FAIL: discount {discount:.1%} < required {MINIMUM_DISCOUNT:.1%} "
            f"(exit costs {EXIT_COST_RATE:.1%} + 10%)"
        )
    else:
        gates["gate1_entry_discount"] = True

    # ------------------------------------------------------------------
    # Income-dependent gates
    # ------------------------------------------------------------------
    net_income = _annual_net_income(candidate)
    is_mortgage = profile.purchase_mode == "mortgage"

    # Gate 2: CoCR < 5% on leveraged deal (mortgage only)
    if not is_mortgage:
        gates["gate2_cocr"] = True  # cash investor — skip
    elif net_income is None:
        gates["gate2_cocr"] = True  # no rent data — skip (not penalised)
    else:
        equity = price * (1.0 - profile.ltv_pct)
        cocr = net_income / equity if equity > 0 else 0.0
        if cocr < COCR_MIN:
            gates["gate2_cocr"] = False
            reject_reasons.append(
                f"Gate 2 FAIL: CoCR {cocr:.1%} < {COCR_MIN:.0%} minimum"
            )
        else:
            gates["gate2_cocr"] = True

    # Gate 3: DSCR < 1.25 for income strategies (mortgage only)
    # Applies to rent and hospitality strategies
    income_strategies = {"rent", "hospitality"}
    active_strategies = set(profile.strategies)
    is_income_strategy = bool(active_strategies & income_strategies) or "all" in active_strategies

    if not is_mortgage or not is_income_strategy:
        gates["gate3_dscr"] = True  # cash or non-income strategy — skip
    elif net_income is None:
        gates["gate3_dscr"] = True  # no rent data — skip
    else:
        debt_service = _annual_debt_service(price, profile.ltv_pct, profile.mortgage_rate)
        dscr = net_income / debt_service if debt_service > 0 else float("inf")
        if dscr < DSCR_MIN:
            gates["gate3_dscr"] = False
            reject_reasons.append(
                f"Gate 3 FAIL: DSCR {dscr:.2f} < {DSCR_MIN} minimum"
            )
        else:
            gates["gate3_dscr"] = True

    # Gate 4: DSCR < 1.0 at +200bps stress (FLAG, not reject)
    if is_mortgage and is_income_strategy and net_income is not None:
        stress_rate = profile.mortgage_rate + DSCR_STRESS_BPS / 10000
        stressed_debt_service = _annual_debt_service(price, profile.ltv_pct, stress_rate)
        stressed_dscr = (
            net_income / stressed_debt_service if stressed_debt_service > 0 else float("inf")
        )
        gates["gate4_dscr_stress"] = True  # never rejects
        if stressed_dscr < 1.0:
            flags.append(
                f"Gate 4 FLAG: stressed DSCR {stressed_dscr:.2f} < 1.0 "
                f"at +{DSCR_STRESS_BPS}bps ({stress_rate:.2%} rate)"
            )
    else:
        gates["gate4_dscr_stress"] = True  # not applicable

    # Gate 5: IRR < 16% (FLAG, not reject)
    # IRR ≈ (annual_income + annual_appreciation) / total_investment
    total_investment = price * (1.0 - profile.ltv_pct) if is_mortgage else price
    if net_income is not None and total_investment > 0:
        annual_appreciation = price * ANNUAL_APPRECIATION_PCT
        irr_approx = (net_income + annual_appreciation) / total_investment
        gates["gate5_irr"] = True  # never rejects
        if irr_approx < IRR_BENCHMARK:
            flags.append(
                f"Gate 5 FLAG: estimated IRR {irr_approx:.1%} < {IRR_BENCHMARK:.0%} benchmark"
            )
    else:
        gates["gate5_irr"] = True  # not applicable

    hard_gates = ["gate1_entry_discount", "gate2_cocr", "gate3_dscr"]
    pass_all = all(gates.get(g, True) for g in hard_gates)

    return PreFilterResult(
        pass_all=pass_all,
        gates=gates,
        flags=flags,
        reject_reasons=reject_reasons,
    )

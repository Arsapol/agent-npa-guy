"""
Strategy router for Multi-Strategy NPA Screener v2.

Routes a candidate through eligible strategies based on property type and
investor profile, applies cascade rules, and returns a consolidated result.
"""

from models_v2 import (
    InvestorProfile,
    NpaCandidate,
    PreFilterResult,
    PropertyResult,
    PropertyType,
    Strategy,
    StrategyScore,
)
from financial_prefilter import financial_prefilter
from strategy_rent import score_rental
from strategy_flip import score_flip
from strategy_landbank import score_landbank
from strategy_hospitality import score_hospitality


# ---------------------------------------------------------------------------
# Strategy eligibility by property type
# ---------------------------------------------------------------------------

_ELIGIBLE_STRATEGIES: dict[PropertyType, list[Strategy]] = {
    PropertyType.CONDO: [Strategy.RENT, Strategy.FLIP, Strategy.HOSPITALITY],
    PropertyType.HOUSE: [Strategy.RENT, Strategy.FLIP, Strategy.HOSPITALITY],
    PropertyType.TOWNHOUSE: [Strategy.RENT, Strategy.FLIP, Strategy.HOSPITALITY],
    PropertyType.LAND: [Strategy.LAND_BANK],
    PropertyType.HOUSE_AND_LAND: [Strategy.FLIP, Strategy.LAND_BANK, Strategy.HOSPITALITY],
    PropertyType.COMMERCIAL: [],
}


def _resolve_strategies(
    candidate: NpaCandidate, profile: InvestorProfile
) -> list[Strategy]:
    """
    Return the list of strategies to score, filtered by property type and
    investor profile.strategies.
    """
    type_eligible = _ELIGIBLE_STRATEGIES.get(candidate.property_type, [])
    if "all" in profile.strategies:
        return list(type_eligible)
    requested = {s.lower() for s in profile.strategies}
    return [s for s in type_eligible if s.value in requested]


def _avoid_score(strategy: Strategy, reason: str) -> StrategyScore:
    """Build a minimal AVOID StrategyScore."""
    return StrategyScore(
        strategy=strategy,
        sub_strategy="",
        score=0.0,
        verdict="AVOID",
        key_metrics={},
        flags=[],
        reject_reasons=[reason],
        pass_gates=False,
    )


def _score_strategy(
    strategy: Strategy,
    candidate: NpaCandidate,
    profile: InvestorProfile,
    furnished: bool = False,
) -> StrategyScore:
    """Dispatch to the appropriate scorer."""
    if strategy == Strategy.RENT:
        if furnished:
            # Re-score with a profile that has renovation_budget_pct > 0 to trigger furnished path
            furnished_profile = InvestorProfile(
                **{
                    **profile.model_dump(),
                    "renovation_budget_pct": profile.renovation_budget_pct
                    if profile.renovation_budget_pct > 0
                    else 0.10,
                }
            )
            return score_rental(candidate, furnished_profile)
        return score_rental(candidate, profile)
    if strategy == Strategy.FLIP:
        return score_flip(candidate, profile)
    if strategy == Strategy.LAND_BANK:
        return score_landbank(candidate, profile)
    if strategy == Strategy.HOSPITALITY:
        return score_hospitality(candidate, profile)
    return _avoid_score(strategy, f"unknown strategy: {strategy.value}")


def _hospitality_is_eligible_for_condo(score: StrategyScore) -> bool:
    """
    Condo + hospitality is only valid when sub_strategy is serviced_apt.
    The scorer already enforces this, but we gate out non-serviced_apt results.
    """
    return score.sub_strategy in ("serviced_apt", "")


def route_and_score(
    candidate: NpaCandidate, profile: InvestorProfile
) -> PropertyResult:
    """
    Route a candidate through eligible strategies and return a consolidated result.

    Steps:
    1. Determine eligible strategies from property type + investor profile.
    2. Run financial_prefilter — if pass_all is False, return all strategies as AVOID.
    3. Score each eligible strategy.
    4. Apply cascade rules:
       a. flip < 55 + rent eligible → also score rent (adds "failed_flip_to_rent").
       b. rent bare score < 55 + renovation_budget_pct > 0 → re-score furnished
          (adds "bare_to_furnished").
       c. Condo + hospitality → force serviced_apt; reject STR results.
    5. Set dual strategy flag when both rent >= 55 and flip >= 55.
    6. Pick best_strategy as highest-scoring non-AVOID strategy.
    """
    prefilter: PreFilterResult = financial_prefilter(candidate, profile)
    cascade_path: list[str] = []

    if not prefilter.pass_all:
        all_avoid: dict[str, StrategyScore] = {
            s.value: _avoid_score(s, "financial_prefilter_failed")
            for s in _resolve_strategies(candidate, profile)
        }
        return PropertyResult(
            candidate=candidate,
            prefilter=prefilter,
            strategy_scores=all_avoid,
            best_strategy=None,
            best_score=0.0,
            is_dual_strategy=False,
            dual_strategies=[],
            cascade_path=[],
        )

    eligible = _resolve_strategies(candidate, profile)
    strategy_scores: dict[str, StrategyScore] = {}

    # Score all eligible strategies
    for strat in eligible:
        raw_score = _score_strategy(strat, candidate, profile)

        # Rule c: condo + hospitality → only serviced_apt is allowed
        if strat == Strategy.HOSPITALITY and candidate.property_type == PropertyType.CONDO:
            if not _hospitality_is_eligible_for_condo(raw_score):
                raw_score = _avoid_score(
                    Strategy.HOSPITALITY,
                    "condo_hospitality: only serviced_apt (30+ day) allowed for condo",
                )

        strategy_scores[strat.value] = raw_score

    # Rule a: cascade from flip to rent
    flip_score_obj = strategy_scores.get(Strategy.FLIP.value)
    rent_eligible = Strategy.RENT in eligible
    if (
        flip_score_obj is not None
        and flip_score_obj.score < 55
        and not rent_eligible
        and Strategy.RENT in _ELIGIBLE_STRATEGIES.get(candidate.property_type, [])
    ):
        cascade_path.append("failed_flip_to_rent")
        rent_cascade = _score_strategy(Strategy.RENT, candidate, profile)
        strategy_scores[Strategy.RENT.value] = rent_cascade

    # Rule b: re-score rent furnished when bare score < 55 and reno budget present
    rent_score_obj = strategy_scores.get(Strategy.RENT.value)
    if (
        rent_score_obj is not None
        and rent_score_obj.score < 55
        and profile.renovation_budget_pct > 0
    ):
        cascade_path.append("bare_to_furnished")
        furnished_score = _score_strategy(Strategy.RENT, candidate, profile, furnished=True)
        # Only replace if the furnished score is better
        if furnished_score.score > rent_score_obj.score:
            strategy_scores[Strategy.RENT.value] = furnished_score

    # Determine dual strategy
    final_rent = strategy_scores.get(Strategy.RENT.value)
    final_flip = strategy_scores.get(Strategy.FLIP.value)
    is_dual = (
        final_rent is not None
        and final_flip is not None
        and final_rent.score >= 55
        and final_flip.score >= 55
    )
    dual_strategies = [Strategy.RENT.value, Strategy.FLIP.value] if is_dual else []

    # Pick best non-AVOID strategy
    best_strategy: str | None = None
    best_score: float = 0.0
    for key, ss in strategy_scores.items():
        if ss.verdict != "AVOID" and ss.score > best_score:
            best_score = ss.score
            best_strategy = key

    return PropertyResult(
        candidate=candidate,
        prefilter=prefilter,
        strategy_scores=strategy_scores,
        best_strategy=best_strategy,
        best_score=best_score,
        is_dual_strategy=is_dual,
        dual_strategies=dual_strategies,
        cascade_path=cascade_path,
    )

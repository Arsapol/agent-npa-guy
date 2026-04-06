"""
Multi-strategy report output for NPA Screener v2.

Provides format_report_v2 (markdown string) and export_json_v2 (JSON file).
"""

import json
from typing import Optional

from constants import (
    IRR_BENCHMARK,
    SUPPLY_PRESSURE_HIGH,
    SUPPLY_PRESSURE_MODERATE,
    SUPPLY_PRESSURE_SEVERE,
)
from models_v2 import InvestorProfile, PropertyResult, Strategy


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _fmt_baht(value: Optional[float]) -> str:
    if value is None:
        return "—"
    if value >= 1_000_000:
        return f"{value / 1_000_000:.2f}M"
    if value >= 1_000:
        return f"{value / 1_000:.0f}K"
    return f"{value:.0f}"


def _fmt_pct(value: Optional[float], decimals: int = 1) -> str:
    if value is None:
        return "—"
    return f"{value:.{decimals}f}%"


def _supply_level(pct: Optional[float]) -> str:
    if pct is None:
        return "—"
    if pct >= SUPPLY_PRESSURE_SEVERE:
        return f"SEVERE ({pct:.1f}%)"
    if pct >= SUPPLY_PRESSURE_HIGH:
        return f"HIGH ({pct:.1f}%)"
    if pct >= SUPPLY_PRESSURE_MODERATE:
        return f"MODERATE ({pct:.1f}%)"
    return f"LOW ({pct:.1f}%)"


def _irr_vs_benchmark(irr: Optional[float]) -> str:
    benchmark = IRR_BENCHMARK * 100  # 16.0
    if irr is None:
        return "—"
    diff = irr - benchmark
    sign = "+" if diff >= 0 else ""
    return f"{sign}{diff:.1f}pp vs {benchmark:.0f}%"


def _verdict_emoji(verdict: str) -> str:
    return {
        "STRONG_BUY": "**STRONG_BUY**",
        "BUY": "**BUY**",
        "WATCH": "WATCH",
        "AVOID": "~~AVOID~~",
    }.get(verdict, verdict)


def _non_avoid_results(results: list[PropertyResult]) -> list[PropertyResult]:
    return [
        r
        for r in results
        if r.best_strategy is not None
        and r.strategy_scores.get(r.best_strategy) is not None
        and r.strategy_scores[r.best_strategy].verdict != "AVOID"
    ]


def _sort_key(r: PropertyResult) -> float:
    return r.best_score


# ---------------------------------------------------------------------------
# format_report_v2
# ---------------------------------------------------------------------------


def format_report_v2(
    results: list[PropertyResult],
    profile: InvestorProfile,
    top_n: int = 50,
) -> str:
    lines: list[str] = []

    # -----------------------------------------------------------------------
    # Summary section
    # -----------------------------------------------------------------------
    total = len(results)
    prefilter_pass = sum(1 for r in results if r.prefilter.pass_all)
    prefilter_fail = total - prefilter_pass

    lines.append("# NPA Screener v2 — Multi-Strategy Report")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Properties screened:** {total}")
    lines.append(
        f"- **Pre-filter:** {prefilter_pass} passed / {prefilter_fail} failed"
    )
    lines.append("")

    # Verdict distribution by strategy
    strategy_verdicts: dict[str, dict[str, int]] = {}
    for r in results:
        for strat, ss in r.strategy_scores.items():
            if strat not in strategy_verdicts:
                strategy_verdicts[strat] = {
                    "STRONG_BUY": 0,
                    "BUY": 0,
                    "WATCH": 0,
                    "AVOID": 0,
                }
            strategy_verdicts[strat][ss.verdict] += 1

    if strategy_verdicts:
        lines.append("### Verdict Distribution by Strategy")
        lines.append("")
        lines.append(
            "| Strategy | STRONG_BUY | BUY | WATCH | AVOID |"
        )
        lines.append("|----------|-----------|-----|-------|-------|")
        for strat, counts in sorted(strategy_verdicts.items()):
            lines.append(
                f"| {strat} "
                f"| {counts['STRONG_BUY']} "
                f"| {counts['BUY']} "
                f"| {counts['WATCH']} "
                f"| {counts['AVOID']} |"
            )
        lines.append("")

    # By-provider count
    provider_counts: dict[str, int] = {}
    for r in results:
        src = r.candidate.source
        provider_counts[src] = provider_counts.get(src, 0) + 1

    lines.append("### Properties by Provider")
    lines.append("")
    for src, cnt in sorted(provider_counts.items()):
        lines.append(f"- **{src}**: {cnt}")
    lines.append("")

    # Investor profile
    lines.append("### Investor Profile")
    lines.append("")
    lines.append(f"- Mode: {profile.purchase_mode.upper()}")
    if profile.purchase_mode == "mortgage":
        lines.append(f"- LTV: {profile.ltv_pct * 100:.0f}%")
        lines.append(f"- Mortgage rate: {profile.mortgage_rate * 100:.1f}%")
    lines.append(f"- Hold horizon: {profile.hold_horizon_years} years")
    lines.append(f"- Entity: {profile.entity_type}")
    lines.append(f"- Tabien baan: {'Yes' if profile.tabien_baan else 'No'}")
    lines.append(f"- Reno budget: {profile.renovation_budget_pct * 100:.0f}%")
    lines.append(f"- Strategies: {', '.join(profile.strategies)}")
    lines.append(f"- Risk tolerance: {profile.risk_tolerance}")
    lines.append("")

    # -----------------------------------------------------------------------
    # Top N table
    # -----------------------------------------------------------------------
    scored = sorted(results, key=_sort_key, reverse=True)
    top = scored[:top_n]

    lines.append(f"## Top {min(top_n, len(top))} Properties")
    lines.append("")
    lines.append(
        "| # | Best Strategy | Score | Source | Project | Location "
        "| Price | Discount | Yield | BTS Tier | Dual? | IRR vs 16% |"
    )
    lines.append(
        "|---|--------------|-------|--------|---------|----------"
        "|-------|----------|-------|----------|-------|------------|"
    )

    for i, r in enumerate(top, 1):
        c = r.candidate
        best = r.best_strategy or "—"
        score = f"{r.best_score:.1f}"
        project = (c.project_name or c.market_project_name or "—")[:30]
        location = f"{c.district}, {c.province}" if c.district else c.province or "—"
        price = _fmt_baht(c.price_baht)
        discount = _fmt_pct(c.real_discount_pct)
        fin = r.financial
        irr_raw = fin.irr_pct if fin else None
        # Yield: look in best strategy key_metrics first
        yield_val: Optional[float] = None
        if r.best_strategy and r.best_strategy in r.strategy_scores:
            yield_val = r.strategy_scores[r.best_strategy].key_metrics.get(
                "gross_yield_pct"
            )
        yield_str = _fmt_pct(yield_val)
        bts = c.bts_tier or "—"
        dual = "Yes" if r.is_dual_strategy else "No"
        irr_str = _irr_vs_benchmark(irr_raw)

        lines.append(
            f"| {i} | {best} | {score} | {c.source} | {project} "
            f"| {location} | {price} | {discount} | {yield_str} "
            f"| {bts} | {dual} | {irr_str} |"
        )

    lines.append("")

    # -----------------------------------------------------------------------
    # Detailed cards for top 20
    # -----------------------------------------------------------------------
    lines.append("## Detailed Cards — Top 20")
    lines.append("")

    for i, r in enumerate(top[:20], 1):
        c = r.candidate
        project = c.project_name or c.market_project_name or "Unknown"
        location = (
            f"{c.subdistrict}, {c.district}, {c.province}"
            if c.subdistrict
            else (f"{c.district}, {c.province}" if c.district else c.province or "—")
        )

        lines.append(f"### #{i} — {project}")
        lines.append(f"**{c.source}** `{c.source_id}` | {location}")
        lines.append(
            f"Price: {_fmt_baht(c.price_baht)} "
            f"({_fmt_baht(c.price_sqm or c.verified_price_sqm)}/sqm, "
            f"{c.size_sqm or '—'} sqm) | "
            f"Discount: {_fmt_pct(c.real_discount_pct)} | "
            f"BTS Tier: {c.bts_tier or '—'}"
        )
        if c.nearest_bts_name:
            lines.append(
                f"Nearest BTS/MRT: {c.nearest_bts_name} "
                f"({c.nearest_bts_dist_m:.0f}m)"
                if c.nearest_bts_dist_m is not None
                else f"Nearest BTS/MRT: {c.nearest_bts_name}"
            )
        if c.nearest_anchor_name:
            dist_str = (
                f" ({c.nearest_anchor_dist_m:.0f}m)"
                if c.nearest_anchor_dist_m is not None
                else ""
            )
            lines.append(
                f"Anchor: {c.nearest_anchor_name} "
                f"({c.nearest_anchor_type}){dist_str}"
            )
        lines.append("")

        # Dual-strategy badge
        if r.is_dual_strategy:
            strats = " + ".join(r.dual_strategies)
            lines.append(f"> **DUAL STRATEGY**: {strats}")
            lines.append("")

        # Cascade path
        if r.cascade_path:
            cascade_str = " → ".join(r.cascade_path)
            lines.append(f"> Cascade: {cascade_str}")
            lines.append("")

        # Per-strategy scores
        lines.append("#### Strategy Scores")
        lines.append("")
        for strat_key, ss in r.strategy_scores.items():
            verdict_str = _verdict_emoji(ss.verdict)
            sub = f" ({ss.sub_strategy})" if ss.sub_strategy else ""
            lines.append(
                f"- **{strat_key.upper()}{sub}**: "
                f"{verdict_str} — {ss.score:.1f}/100"
            )
            if ss.key_metrics:
                metrics_parts = []
                for k, v in ss.key_metrics.items():
                    if v is not None:
                        metrics_parts.append(f"{k}={v:.2f}")
                if metrics_parts:
                    lines.append(f"  - Metrics: {', '.join(metrics_parts)}")
            if ss.flags:
                lines.append(f"  - Flags: {', '.join(ss.flags)}")
            if ss.reject_reasons:
                lines.append(f"  - Rejected: {', '.join(ss.reject_reasons)}")
        lines.append("")

        # Financial overlay
        fin = r.financial
        if fin:
            lines.append("#### Financial Overlay")
            lines.append("")
            lines.append(
                f"- IRR: {_fmt_pct(fin.irr_pct)} ({fin.irr_vs_benchmark or _irr_vs_benchmark(fin.irr_pct)})"
            )
            lines.append(f"- CoCR: {_fmt_pct(fin.cocr_pct)}")
            lines.append(
                f"- DSCR: {fin.dscr:.2f}" if fin.dscr is not None else "- DSCR: —"
            )
            lines.append(
                f"- Break-even occupancy: {_fmt_pct(fin.break_even_occupancy_pct)}"
            )
            lines.append(
                f"- Hold cost (monthly): {_fmt_baht(fin.hold_cost_monthly)}"
            )
            lines.append(
                f"- Total acquisition cost: {_fmt_baht(fin.total_acquisition_cost)}"
            )
            if fin.tax_recommendation:
                lines.append(f"- Tax recommendation: {fin.tax_recommendation}")
            lines.append("")

        # Supply pressure
        supply_str = _supply_level(c.supply_pressure_pct)
        lines.append(f"**Supply pressure:** {supply_str}")
        lines.append("")

        # All flags from all strategies
        all_flags: list[str] = []
        all_rejects: list[str] = []
        for ss in r.strategy_scores.values():
            all_flags.extend(ss.flags)
            all_rejects.extend(ss.reject_reasons)
        # Also prefilter
        all_flags.extend(r.prefilter.flags)
        all_rejects.extend(r.prefilter.reject_reasons)

        if all_flags:
            unique_flags = list(dict.fromkeys(all_flags))
            lines.append(f"**Flags:** {', '.join(unique_flags)}")
        if all_rejects:
            unique_rejects = list(dict.fromkeys(all_rejects))
            lines.append(f"**Reject reasons:** {', '.join(unique_rejects)}")

        lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# export_json_v2
# ---------------------------------------------------------------------------


def export_json_v2(results: list[PropertyResult], path: str) -> None:
    non_avoid = [
        r
        for r in results
        if not (
            r.best_strategy
            and r.strategy_scores.get(r.best_strategy, None) is not None
            and r.strategy_scores[r.best_strategy].verdict == "AVOID"
        )
        and r.prefilter.pass_all
    ]

    entries = []
    for r in non_avoid:
        base = r.candidate.model_dump()

        strategy_scores_out: dict[str, dict] = {}
        for strat_key, ss in r.strategy_scores.items():
            strategy_scores_out[strat_key] = {
                "score": ss.score,
                "verdict": ss.verdict,
                "sub_strategy": ss.sub_strategy,
                "key_metrics": ss.key_metrics,
                "flags": ss.flags,
                "reject_reasons": ss.reject_reasons,
                "pass_gates": ss.pass_gates,
            }

        financial_out = r.financial.model_dump() if r.financial else None

        entry = {
            **base,
            "strategy_scores": strategy_scores_out,
            "financial": financial_out,
            "best_strategy": r.best_strategy,
            "best_score": r.best_score,
            "is_dual_strategy": r.is_dual_strategy,
            "dual_strategies": r.dual_strategies,
            "cascade_path": r.cascade_path,
        }
        entries.append(entry)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2, default=str)

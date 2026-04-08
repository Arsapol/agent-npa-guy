"""Main comparison dispatcher for NPA properties.

Single entry point: ``compare_npa(npa)`` dispatches to the appropriate
type-specific builder based on ``npa.category`` and returns a typed
comparison result (CondoComparison, LandComparison, HouseComparison,
CommercialComparison, or BaseComparison).

Cross-NPA comparison is the primary signal for all non-condo types.
Condos additionally attempt external market data via market_adapter.
"""

from __future__ import annotations

import os
import sys
from typing import Any

# ---------------------------------------------------------------------------
# Path setup — adapter must be first so its own 'from models import ...' works
# ---------------------------------------------------------------------------

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_ADAPTER_DIR = os.path.abspath(os.path.join(_SCRIPT_DIR, "..", "..", "npa-adapter", "scripts"))

sys.path.insert(0, _ADAPTER_DIR)

import models as _adapter_models  # noqa: E402 — adapter's models.py
# Sibling scripts (proximity, benchmarks) need _SCRIPT_DIR in path.
# Insert AFTER adapter models import so 'models' cache already points to adapter's copy.
sys.path.insert(0, _SCRIPT_DIR)

NpaProperty = _adapter_models.NpaProperty
SearchFilters = _adapter_models.SearchFilters
Source = _adapter_models.Source
PropertyCategory = _adapter_models.PropertyCategory

# ---------------------------------------------------------------------------
# Import sibling modules BEFORE loading local models.
# benchmarks.py always (re)registers "_npa_comparator_models" in sys.modules,
# so we must import it first — then read local models from the registered copy.
# If we load local models before benchmarks, the class identities diverge and
# Pydantic v2 validation rejects AreaBenchmark instances from benchmarks.
# ---------------------------------------------------------------------------

from proximity import find_comparables  # noqa: E402
from benchmarks import compute_benchmark  # noqa: E402

# market_adapter for condo path
from market_adapter import compare_npa_to_market  # noqa: E402

# Now get local models — benchmarks has registered the authoritative copy.
_lm = sys.modules["_npa_comparator_models"]

BaseComparison = _lm.BaseComparison
CondoComparison = _lm.CondoComparison
LandComparison = _lm.LandComparison
HouseComparison = _lm.HouseComparison
CommercialComparison = _lm.CommercialComparison
AreaBenchmark = _lm.AreaBenchmark
RangeEstimate = _lm.RangeEstimate
STRATEGY_MAP = _lm.STRATEGY_MAP
rai_ngan_wa_to_total_wa = _lm.rai_ngan_wa_to_total_wa


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _subject_metric(npa: NpaProperty) -> float | None:
    """Normalized price metric for the subject property (matches benchmark unit)."""
    price = npa.best_price_baht
    if not price or price <= 0:
        return None

    cat = npa.category

    if cat == PropertyCategory.CONDO:
        if not npa.size_sqm or npa.size_sqm <= 0:
            return None
        return price / npa.size_sqm

    if cat == PropertyCategory.LAND:
        total_wa = rai_ngan_wa_to_total_wa(npa.size_rai, npa.size_ngan, npa.size_wa)
        if total_wa <= 0:
            return None
        return price / total_wa

    if cat in (PropertyCategory.HOUSE, PropertyCategory.TOWNHOUSE):
        total_wa = rai_ngan_wa_to_total_wa(npa.size_rai, npa.size_ngan, npa.size_wa)
        if total_wa > 0:
            return price / total_wa
        return price

    if cat in (PropertyCategory.COMMERCIAL, PropertyCategory.FACTORY):
        if not npa.size_sqm or npa.size_sqm <= 0:
            return None
        return price / npa.size_sqm

    return price


def _price_position(metric: float | None, benchmark: AreaBenchmark | None) -> str:
    """Classify subject price vs benchmark percentiles."""
    if metric is None or benchmark is None or benchmark.median is None:
        return "UNKNOWN"
    if benchmark.p25 is not None and metric < benchmark.p25:
        return "BELOW_P25"
    if metric < benchmark.median:
        return "BELOW_MEDIAN"
    if benchmark.p75 is not None and metric > benchmark.p75:
        return "ABOVE_P75"
    return "ABOVE_MEDIAN"


def _discount_vs_median(metric: float | None, benchmark: AreaBenchmark | None) -> float | None:
    """(1 - metric/median) * 100. Positive = cheaper than median."""
    if metric is None or benchmark is None or not benchmark.median or benchmark.median <= 0:
        return None
    return round((1 - metric / benchmark.median) * 100, 1)


def _data_quality(comp_count: int, has_gps: bool) -> str:
    if comp_count > 20:
        return "HIGH"
    if comp_count >= 5 and has_gps:
        return "HIGH"
    if comp_count >= 5:
        return "MEDIUM"
    if comp_count >= 3:
        return "MEDIUM"
    return "LOW"


def _npa_concentration(npa: NpaProperty, comps: list[dict[str, Any]]) -> float:
    if not comps:
        return 0.0
    same = sum(1 for c in comps if c.get("source") == npa.source.value)
    return round(same / len(comps), 3)


def _comp_sources(comps: list[dict[str, Any]]) -> list[Source]:
    seen: set[str] = set()
    result: list[Source] = []
    for c in comps:
        src = c.get("source")
        if src and src not in seen:
            seen.add(src)
            try:
                result.append(Source(src))
            except ValueError:
                pass
    return result


def _density_within_1km(npa: NpaProperty, comps: list[dict[str, Any]]) -> float:
    """Count of comparables within 1 km (GPS-aware density signal)."""
    if npa.lat is None or npa.lon is None:
        return float(len(comps))  # no GPS — use total as proxy
    count = 0
    for c in comps:
        dist = c.get("distance_km")
        if dist is not None and dist <= 1.0:
            count += 1
    return float(count)


def _extract_building_age(npa: NpaProperty) -> tuple[int | None, str | None]:
    """Return (age_years, source_label) from provider-specific extra fields."""
    extra = npa.extra or {}
    import datetime

    current_year = datetime.datetime.now().year

    # KBank: building_age is an integer (years)
    if npa.source == Source.KBANK:
        age = extra.get("building_age")
        if age is not None:
            try:
                return int(age), "kbank_building_age"
            except (TypeError, ValueError):
                pass

    # GSB: builded_year is a text year (Buddhist or CE)
    if npa.source == Source.GSB:
        yr_text = extra.get("builded_year")
        if yr_text:
            try:
                yr = int(str(yr_text).strip())
                # Buddhist era years are ~543 greater than CE
                if yr > 2500:
                    yr -= 543
                if 1900 < yr <= current_year:
                    return current_year - yr, "gsb_builded_year"
            except (TypeError, ValueError):
                pass

    # TTB: building_info or year_built in extra
    if npa.source == Source.TTB:
        for key in ("year_built", "building_year", "build_year"):
            yr_text = extra.get(key)
            if yr_text:
                try:
                    yr = int(str(yr_text).strip())
                    if yr > 2500:
                        yr -= 543
                    if 1900 < yr <= current_year:
                        return current_year - yr, f"ttb_{key}"
                except (TypeError, ValueError):
                    pass

    return None, None


def _renovation_estimate(age_years: int | None, sqm: float | None) -> RangeEstimate | None:
    """Rough renovation cost: age_years * sqm * rate_per_sqm_per_year."""
    if age_years is None or sqm is None or sqm <= 0:
        return None
    # Heuristic: older buildings cost more per sqm to renovate
    low = age_years * sqm * 300
    mid = age_years * sqm * 500
    high = age_years * sqm * 800
    return RangeEstimate(low=round(low, 0), mid=round(mid, 0), high=round(high, 0))


# ---------------------------------------------------------------------------
# Type-specific builders
# ---------------------------------------------------------------------------


def _build_condo(
    npa: NpaProperty,
    comps: list[dict[str, Any]],
    benchmark: AreaBenchmark,
    concentration: float,
    pos: str,
    quality: str,
    sources: list[Source],
) -> CondoComparison:
    price_per_sqm = None
    if npa.best_price_baht and npa.size_sqm and npa.size_sqm > 0:
        price_per_sqm = round(npa.best_price_baht / npa.size_sqm, 0)

    metric = _subject_metric(npa)
    discount_npa = _discount_vs_median(metric, benchmark)

    # External market data attempt
    median_market_sqm: float | None = None
    discount_market: float | None = None
    basis = "cross_npa"
    try:
        market_match = compare_npa_to_market(npa)
        if market_match.median_price_sqm and market_match.median_price_sqm > 0:
            median_market_sqm = market_match.median_price_sqm
            discount_market = market_match.discount_vs_market_pct
            basis = "market_verified"
    except Exception:
        pass

    return CondoComparison(
        npa_source=npa.source,
        npa_source_id=npa.source_id,
        npa_category=npa.category,
        comparison_basis=basis,
        comparable_count=len(comps),
        comparable_sources=sources,
        area_benchmark=benchmark,
        npa_concentration=concentration,
        price_position=pos,
        supported_strategies=STRATEGY_MAP.get(PropertyCategory.CONDO, []),
        data_quality=quality,
        comparables=comps,
        price_per_sqm=price_per_sqm,
        median_market_sqm=median_market_sqm,
        discount_vs_market_pct=discount_market,
        discount_vs_npa_median_pct=discount_npa,
    )


def _build_land(
    npa: NpaProperty,
    comps: list[dict[str, Any]],
    benchmark: AreaBenchmark,
    concentration: float,
    pos: str,
    quality: str,
    sources: list[Source],
) -> LandComparison:
    total_wa = rai_ngan_wa_to_total_wa(npa.size_rai, npa.size_ngan, npa.size_wa)
    total_wa = total_wa if total_wa > 0 else None

    price_per_wa = None
    if npa.best_price_baht and total_wa and total_wa > 0:
        price_per_wa = round(npa.best_price_baht / total_wa, 2)

    metric = _subject_metric(npa)
    discount_npa = _discount_vs_median(metric, benchmark)

    return LandComparison(
        npa_source=npa.source,
        npa_source_id=npa.source_id,
        npa_category=npa.category,
        comparison_basis="cross_npa",
        comparable_count=len(comps),
        comparable_sources=sources,
        area_benchmark=benchmark,
        npa_concentration=concentration,
        price_position=pos,
        supported_strategies=STRATEGY_MAP.get(PropertyCategory.LAND, []),
        data_quality=quality,
        comparables=comps,
        price_per_wa=price_per_wa,
        total_area_wa=total_wa,
        median_area_price_per_wa=benchmark.median,
        discount_vs_npa_median_pct=discount_npa,
    )


def _build_house(
    npa: NpaProperty,
    comps: list[dict[str, Any]],
    benchmark: AreaBenchmark,
    concentration: float,
    pos: str,
    quality: str,
    sources: list[Source],
) -> HouseComparison:
    total_wa = rai_ngan_wa_to_total_wa(npa.size_rai, npa.size_ngan, npa.size_wa)
    total_wa_val = total_wa if total_wa > 0 else None

    price_per_wa_land = None
    if npa.best_price_baht and total_wa_val and total_wa_val > 0:
        price_per_wa_land = round(npa.best_price_baht / total_wa_val, 2)

    price_per_sqm_usable = None
    if npa.best_price_baht and npa.size_sqm and npa.size_sqm > 0:
        price_per_sqm_usable = round(npa.best_price_baht / npa.size_sqm, 0)

    metric = _subject_metric(npa)
    discount_npa = _discount_vs_median(metric, benchmark)
    density = _density_within_1km(npa, comps)

    age_years, age_source = _extract_building_age(npa)
    reno = _renovation_estimate(age_years, npa.size_sqm)

    return HouseComparison(
        npa_source=npa.source,
        npa_source_id=npa.source_id,
        npa_category=npa.category,
        comparison_basis="cross_npa",
        comparable_count=len(comps),
        comparable_sources=sources,
        area_benchmark=benchmark,
        npa_concentration=concentration,
        price_position=pos,
        supported_strategies=STRATEGY_MAP.get(npa.category, []),
        data_quality=quality,
        comparables=comps,
        price_per_wa_land=price_per_wa_land,
        total_land_wa=total_wa_val,
        median_area_price_per_wa_land=benchmark.median,
        price_per_unit=npa.best_price_baht,
        median_area_price_per_unit=None,  # not computed separately from benchmark
        discount_vs_npa_median_pct=discount_npa,
        usable_area_sqm=npa.size_sqm,
        price_per_sqm_usable=price_per_sqm_usable,
        building_age_years=age_years,
        building_age_source=age_source,
        renovation_estimate=reno,
        bedrooms=npa.bedroom,
        neighborhood_npa_density=density,
    )


def _build_commercial(
    npa: NpaProperty,
    comps: list[dict[str, Any]],
    benchmark: AreaBenchmark,
    concentration: float,
    pos: str,
    quality: str,
    sources: list[Source],
) -> CommercialComparison:
    price_per_sqm = None
    if npa.best_price_baht and npa.size_sqm and npa.size_sqm > 0:
        price_per_sqm = round(npa.best_price_baht / npa.size_sqm, 0)

    metric = _subject_metric(npa)
    discount_npa = _discount_vs_median(metric, benchmark)
    density = _density_within_1km(npa, comps)

    # Infer subtype from raw property_type string
    pt = (npa.property_type or "").lower()
    if "โรงงาน" in pt or "factory" in pt:
        subtype = "factory"
    elif "โกดัง" in pt or "warehouse" in pt:
        subtype = "warehouse"
    elif "office" in pt or "สำนักงาน" in pt:
        subtype = "office"
    else:
        subtype = "shophouse"

    return CommercialComparison(
        npa_source=npa.source,
        npa_source_id=npa.source_id,
        npa_category=npa.category,
        comparison_basis="cross_npa",
        comparable_count=len(comps),
        comparable_sources=sources,
        area_benchmark=benchmark,
        npa_concentration=concentration,
        price_position=pos,
        supported_strategies=STRATEGY_MAP.get(npa.category, []),
        data_quality=quality,
        comparables=comps,
        price_per_sqm=price_per_sqm,
        median_area_price_per_sqm=benchmark.median,
        discount_vs_npa_median_pct=discount_npa,
        commercial_density=density,
        property_subtype=subtype,
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def compare_npa(npa: NpaProperty) -> BaseComparison:
    """Compare an NPA property against comparable NPA properties in the same area.

    Dispatches to a type-specific builder based on ``npa.category``:
    - CONDO        → CondoComparison (tries external market data first)
    - LAND         → LandComparison (cross-NPA, price per wa)
    - HOUSE/TOWNHOUSE → HouseComparison (cross-NPA, price per wa land)
    - COMMERCIAL/FACTORY → CommercialComparison (cross-NPA, price per sqm)
    - OTHER        → BaseComparison (proximity + benchmark only)

    Returns the appropriate subclass with all populated fields.
    """
    cat = npa.category

    comps = find_comparables(npa)
    benchmark = compute_benchmark(cat, npa.province, npa.district)

    concentration = _npa_concentration(npa, comps)
    sources = _comp_sources(comps)
    metric = _subject_metric(npa)
    pos = _price_position(metric, benchmark)
    quality = _data_quality(len(comps), npa.lat is not None)

    common = dict(
        comps=comps,
        benchmark=benchmark,
        concentration=concentration,
        pos=pos,
        quality=quality,
        sources=sources,
    )

    if cat == PropertyCategory.CONDO:
        return _build_condo(npa, **common)
    if cat == PropertyCategory.LAND:
        return _build_land(npa, **common)
    if cat in (PropertyCategory.HOUSE, PropertyCategory.TOWNHOUSE):
        return _build_house(npa, **common)
    if cat in (PropertyCategory.COMMERCIAL, PropertyCategory.FACTORY):
        return _build_commercial(npa, **common)

    # OTHER — BaseComparison
    return BaseComparison(
        npa_source=npa.source,
        npa_source_id=npa.source_id,
        npa_category=cat,
        comparison_type="other",
        comparison_basis="cross_npa",
        comparable_count=len(comps),
        comparable_sources=sources,
        area_benchmark=benchmark,
        npa_concentration=concentration,
        price_position=pos,
        supported_strategies=STRATEGY_MAP.get(cat, []),
        data_quality=quality,
        comparables=comps,
    )

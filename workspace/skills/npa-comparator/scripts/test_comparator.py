"""Integration tests for npa-comparator.

Run with:
    cd /Users/arsapolm/.nanobot-npa-guy/workspace/skills/npa-comparator/scripts
    uv run python3 -m pytest test_comparator.py -v

All tests require a live connection to npa_kb PostgreSQL.
Tests are resilient to sparse data — they verify structure and reasonable ranges,
not exact counts (inventory changes over time).
"""

from __future__ import annotations

import sys
import os

import pytest

# ---------------------------------------------------------------------------
# Path setup — import comparator first so it registers _npa_comparator_models
# ---------------------------------------------------------------------------

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_ADAPTER_DIR = os.path.abspath(os.path.join(_SCRIPT_DIR, "..", "..", "npa-adapter", "scripts"))

sys.path.insert(0, _SCRIPT_DIR)
# comparator.py inserts adapter dir at import time
import comparator  # noqa: E402

from comparator import compare_npa  # noqa: E402
from proximity import find_comparables, ProximityConfig  # noqa: E402
from benchmarks import compute_benchmark  # noqa: E402

# Adapter models (adapter dir already in sys.path after comparator import)
from adapter import search  # noqa: E402
from models import SearchFilters, Source, PropertyCategory  # noqa: E402

# Local comparator models (registered by comparator import)
_lm = sys.modules["_npa_comparator_models"]
CondoComparison = _lm.CondoComparison
LandComparison = _lm.LandComparison
HouseComparison = _lm.HouseComparison
CommercialComparison = _lm.CommercialComparison
BaseComparison = _lm.BaseComparison
AreaBenchmark = _lm.AreaBenchmark


# ---------------------------------------------------------------------------
# Fixtures — fetch real properties from the DB
# ---------------------------------------------------------------------------


def _first_match(category: PropertyCategory, sources=None, require_gps: bool = False):
    """Fetch the first available property matching category + optional GPS."""
    s_list = sources or list(Source)
    filters = SearchFilters(
        province="กรุงเทพ",
        sources=s_list,
        limit=50,
        sort_by="price",
    )
    props = search(filters)
    for p in props:
        if p.category != category:
            continue
        if require_gps and (p.lat is None or p.lon is None):
            continue
        if p.is_sold:
            continue
        return p
    return None


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.integration
def test_compare_condo():
    """BAM condo in Bangkok returns CondoComparison with expected fields."""
    npa = _first_match(PropertyCategory.CONDO, sources=[Source.BAM], require_gps=True)
    if npa is None:
        pytest.skip("No BAM condo with GPS found in Bangkok")

    result = compare_npa(npa)

    assert isinstance(result, CondoComparison)
    assert result.comparison_type == "condo"
    assert result.npa_source == Source.BAM
    assert result.npa_category == PropertyCategory.CONDO
    assert result.supported_strategies == ["rent", "flip", "expat_rental"]
    assert result.data_quality in ("HIGH", "MEDIUM", "LOW")
    assert result.price_position in ("BELOW_P25", "BELOW_MEDIAN", "ABOVE_MEDIAN", "ABOVE_P75", "UNKNOWN")
    assert result.comparable_count >= 0
    assert result.comparables == result.comparables[:20]  # capped at 20


@pytest.mark.integration
def test_compare_land():
    """Land property with GPS returns LandComparison with price_per_wa."""
    npa = _first_match(PropertyCategory.LAND, require_gps=True)
    if npa is None:
        pytest.skip("No land property with GPS found in Bangkok")

    result = compare_npa(npa)

    assert isinstance(result, LandComparison)
    assert result.comparison_type == "land"
    assert result.comparison_basis == "cross_npa"
    assert result.supported_strategies == ["land_bank", "develop", "subdivide"]

    if result.total_area_wa is not None:
        assert result.total_area_wa >= 0
    if result.price_per_wa is not None and result.total_area_wa:
        assert result.price_per_wa > 0


@pytest.mark.integration
def test_compare_house():
    """House property returns HouseComparison with price_per_wa_land as primary."""
    npa = _first_match(PropertyCategory.HOUSE)
    if npa is None:
        pytest.skip("No house property found in Bangkok")

    result = compare_npa(npa)

    assert isinstance(result, HouseComparison)
    assert result.comparison_type == "house"
    assert result.comparison_basis == "cross_npa"
    assert "rent" in result.supported_strategies or "flip" in result.supported_strategies

    # Caveat strings must be set
    assert "price_per_wa_land" in result.usable_area_caveat
    assert "KBank" in result.renovation_data_caveat

    # price_per_unit is the subject price
    if npa.best_price_baht:
        assert result.price_per_unit == npa.best_price_baht


@pytest.mark.integration
def test_compare_commercial():
    """Commercial property returns CommercialComparison with price_per_sqm."""
    npa = _first_match(PropertyCategory.COMMERCIAL)
    if npa is None:
        pytest.skip("No commercial property found in Bangkok")

    result = compare_npa(npa)

    assert isinstance(result, CommercialComparison)
    assert result.comparison_type == "commercial"
    assert result.comparison_basis == "cross_npa"
    assert result.property_subtype in ("shophouse", "office", "warehouse", "factory")


@pytest.mark.integration
def test_compare_no_gps():
    """LED property (no GPS) falls back to district matching and still returns a result."""
    filters = SearchFilters(province="กรุงเทพ", sources=[Source.LED], limit=20)
    props = search(filters)
    led_props = [p for p in props if p.lat is None and not p.is_sold]

    if not led_props:
        pytest.skip("No LED properties without GPS found in Bangkok")

    npa = led_props[0]
    result = compare_npa(npa)

    # Should not crash; may have 0 comps if district is sparse
    assert isinstance(result, BaseComparison)
    assert result.comparable_count >= 0
    # All comps from district fallback have no distance_km
    for c in result.comparables:
        assert "distance_km" in c


@pytest.mark.integration
def test_benchmark_condo_bangkok():
    """Bangkok condo benchmark returns realistic price_per_sqm values."""
    bench = compute_benchmark(PropertyCategory.CONDO, "กรุงเทพ", "")

    assert isinstance(bench, AreaBenchmark)
    assert bench.count > 0, "Expected at least some Bangkok condos in DB"
    assert bench.median is not None
    # Bangkok condo NPA prices: roughly 20,000–150,000 ฿/sqm
    assert 5_000 < bench.median < 500_000, f"Median {bench.median} outside plausible range"
    assert bench.p25 is not None and bench.p25 <= bench.median
    assert bench.p75 is not None and bench.p75 >= bench.median
    assert bench.data_quality in ("HIGH", "MEDIUM", "LOW")


@pytest.mark.integration
def test_proximity_returns_nearby():
    """Comparables found via GPS bbox are within configured radius."""
    npa = _first_match(PropertyCategory.CONDO, sources=[Source.BAM], require_gps=True)
    if npa is None:
        pytest.skip("No BAM condo with GPS found")

    cfg = ProximityConfig(radius_km=2.0, max_results=20)
    comps = find_comparables(npa, config=cfg)

    # All comps with distance_km should be within radius (small tolerance for bbox edge)
    for c in comps:
        dist = c.get("distance_km")
        if dist is not None:
            assert dist <= 2.5, f"Comp at {dist}km exceeds 2km radius (tolerance 0.5km)"


@pytest.mark.integration
def test_strategy_mapping():
    """Each category returns the correct supported_strategies."""
    expected = {
        PropertyCategory.CONDO: ["rent", "flip", "expat_rental"],
        PropertyCategory.LAND: ["land_bank", "develop", "subdivide"],
        PropertyCategory.HOUSE: ["rent", "flip", "renovate_and_rent"],
        PropertyCategory.TOWNHOUSE: ["rent", "flip", "renovate_and_rent"],
        PropertyCategory.COMMERCIAL: ["lease", "owner_occupy", "redevelop"],
        PropertyCategory.FACTORY: ["lease", "owner_occupy"],
    }
    for cat, strategies in expected.items():
        npa = _first_match(cat)
        if npa is None:
            continue  # skip if no data for this type in Bangkok
        result = compare_npa(npa)
        assert result.supported_strategies == strategies, (
            f"{cat.value}: got {result.supported_strategies}, expected {strategies}"
        )


@pytest.mark.integration
def test_subject_excluded_from_comps():
    """Subject property must not appear in its own comparables list."""
    npa = _first_match(PropertyCategory.CONDO, sources=[Source.BAM], require_gps=True)
    if npa is None:
        pytest.skip("No BAM condo with GPS found")

    comps = find_comparables(npa)
    for c in comps:
        assert not (
            c.get("source") == npa.source.value and c.get("source_id") == npa.source_id
        ), "Subject property appeared in its own comparables"

"""Area benchmark calculator for NPA cross-provider price statistics.

Computes median / p25 / p75 price benchmarks for a given property category
and geographic area by querying all NPA providers via the npa-adapter.

Cross-NPA only — no external market data for non-condo types.
"""

from __future__ import annotations

import importlib.util
import os
import sys
import time
from statistics import median

# ---------------------------------------------------------------------------
# Path setup — adapter first (so adapter.py's own 'from models import ...' works)
# ---------------------------------------------------------------------------

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_ADAPTER_DIR = os.path.abspath(os.path.join(_SCRIPT_DIR, "..", "..", "npa-adapter", "scripts"))

sys.path.insert(0, _ADAPTER_DIR)

# Adapter's models.py cached under the name 'models' in sys.modules so that
# adapter.py can import it via its own 'from models import ...' at load time.
import models as _adapter_models  # noqa: E402
from adapter import search  # noqa: E402

SearchFilters = _adapter_models.SearchFilters
_AdapterNpaProperty = _adapter_models.NpaProperty

# ---------------------------------------------------------------------------
# Load local models.py under a unique name (avoids 'models' cache conflict)
# ---------------------------------------------------------------------------

_LOCAL_MODELS_PATH = os.path.join(_SCRIPT_DIR, "models.py")
_spec = importlib.util.spec_from_file_location("_npa_comparator_models", _LOCAL_MODELS_PATH)
_local_models = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
sys.modules["_npa_comparator_models"] = _local_models
_spec.loader.exec_module(_local_models)  # type: ignore[union-attr]

AreaBenchmark = _local_models.AreaBenchmark
PropertyCategory = _local_models.PropertyCategory
Source = _local_models.Source
rai_ngan_wa_to_total_wa = _local_models.rai_ngan_wa_to_total_wa

# ---------------------------------------------------------------------------
# Cache
# ---------------------------------------------------------------------------

_cache: dict[str, tuple[float, AreaBenchmark]] = {}
CACHE_TTL: float = 86400.0  # 24 hours


def _cache_key(category: PropertyCategory, province: str, district: str) -> str:  # type: ignore[valid-type]
    return f"{category.value}:{province}:{district}"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

# Keywords used to pre-filter the adapter search by raw Thai property_type string.
# The adapter applies ILIKE '%keyword%' on the raw type column.
_CATEGORY_KEYWORDS: dict[PropertyCategory, str | None] = {  # type: ignore[valid-type]
    PropertyCategory.CONDO: "ห้องชุด",
    PropertyCategory.LAND: "ที่ดิน",
    PropertyCategory.HOUSE: "บ้านเดี่ยว",
    PropertyCategory.TOWNHOUSE: "ทาวน์",
    PropertyCategory.COMMERCIAL: "อาคารพาณิชย์",
    PropertyCategory.FACTORY: "โรงงาน",
    PropertyCategory.OTHER: None,
}


def _unit_label(category: PropertyCategory) -> str:  # type: ignore[valid-type]
    if category == PropertyCategory.CONDO:
        return "baht_per_sqm"
    if category == PropertyCategory.LAND:
        return "baht_per_wa"
    if category in (PropertyCategory.HOUSE, PropertyCategory.TOWNHOUSE):
        return "baht_per_wa"  # primary: land area from title deed
    if category in (PropertyCategory.COMMERCIAL, PropertyCategory.FACTORY):
        return "baht_per_sqm"
    return "baht_per_unit"


def _extract_metric(prop: _AdapterNpaProperty, category: PropertyCategory) -> float | None:  # type: ignore[valid-type]
    """Extract the normalised price metric for a property given its category.

    Returns None when the required size field is missing or zero.
    """
    price = prop.best_price_baht
    if not price or price <= 0:
        return None

    if category == PropertyCategory.CONDO:
        if not prop.size_sqm or prop.size_sqm <= 0:
            return None
        return price / prop.size_sqm

    if category == PropertyCategory.LAND:
        total_wa = rai_ngan_wa_to_total_wa(prop.size_rai, prop.size_ngan, prop.size_wa)
        if total_wa <= 0:
            return None
        return price / total_wa

    if category in (PropertyCategory.HOUSE, PropertyCategory.TOWNHOUSE):
        # Primary metric: price per wa of land (standardised from title deed)
        total_wa = rai_ngan_wa_to_total_wa(prop.size_rai, prop.size_ngan, prop.size_wa)
        if total_wa > 0:
            return price / total_wa
        # Fallback: total unit price when no land area is recorded
        return price

    if category in (PropertyCategory.COMMERCIAL, PropertyCategory.FACTORY):
        if not prop.size_sqm or prop.size_sqm <= 0:
            return None
        return price / prop.size_sqm

    # OTHER
    return price


def _percentile(sorted_values: list[float], pct: float) -> float:
    """Interpolated percentile from a sorted list (pct in [0, 1])."""
    n = len(sorted_values)
    if n == 0:
        return 0.0
    idx = pct * (n - 1)
    lo = int(idx)
    hi = lo + 1
    if hi >= n:
        return sorted_values[-1]
    return sorted_values[lo] + (idx - lo) * (sorted_values[hi] - sorted_values[lo])


# ---------------------------------------------------------------------------
# Main function
# ---------------------------------------------------------------------------


def compute_benchmark(
    category: PropertyCategory,  # type: ignore[valid-type]
    province: str,
    district: str = "",
) -> AreaBenchmark:
    """Compute cross-NPA price benchmarks for a property category and location.

    Results are cached in-process for 24 hours. Benchmarks reflect NPA asking
    prices only — not external market data (no house/land market source exists
    in the current DB).

    Args:
        category: PropertyCategory enum value.
        province: Thai province name (e.g. "กรุงเทพมหานคร").
        district: Thai district name. Optional — omit for province-wide benchmark.

    Returns:
        AreaBenchmark with median, p25, p75, count, unit, source_breakdown,
        and data_quality (HIGH >20, MEDIUM 5-20, LOW <5).
    """
    key = _cache_key(category, province, district)
    now = time.time()

    cached = _cache.get(key)
    if cached is not None:
        cached_at, result = cached
        if now - cached_at < CACHE_TTL:
            return result

    filters = SearchFilters(
        province=province,
        district=district if district else None,
        property_type=_CATEGORY_KEYWORDS.get(category),
        limit=500,
        offset=0,
        sort_by="price",
    )

    try:
        properties = search(filters)
    except Exception as exc:
        print(f"[benchmarks] search failed: {exc}", file=sys.stderr)
        properties = []

    values: list[float] = []
    source_counts: dict[str, int] = {}

    for prop in properties:
        # Strict category filter — adapter keyword pre-filter may include near-matches
        if prop.category != category:
            continue
        metric = _extract_metric(prop, category)
        if metric is None or metric <= 0:
            continue
        values.append(metric)
        src = prop.source.value
        source_counts[src] = source_counts.get(src, 0) + 1

    count = len(values)
    unit = _unit_label(category)

    if count == 0:
        result = AreaBenchmark(
            median=None,
            p25=None,
            p75=None,
            count=0,
            unit=unit,
            source_breakdown=source_counts,
            data_quality="LOW",
        )
        _cache[key] = (now, result)
        return result

    values.sort()
    med = float(median(values))
    p25 = _percentile(values, 0.25)
    p75 = _percentile(values, 0.75)

    if count > 20:
        quality = "HIGH"
    elif count >= 5:
        quality = "MEDIUM"
    else:
        quality = "LOW"

    result = AreaBenchmark(
        median=med,
        p25=p25,
        p75=p75,
        count=count,
        unit=unit,
        source_breakdown=source_counts,
        data_quality=quality,
    )
    _cache[key] = (now, result)
    return result

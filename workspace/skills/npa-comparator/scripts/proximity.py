"""GPS proximity matcher — finds comparable NPA properties by location, type, and size."""

from __future__ import annotations

import os
import sys
from math import atan2, cos, radians, sin, sqrt
from typing import Any

from pydantic import BaseModel

# ---------------------------------------------------------------------------
# Path setup — import from npa-adapter
# ---------------------------------------------------------------------------

_ADAPTER_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "npa-adapter", "scripts")
)
sys.path.insert(0, _ADAPTER_DIR)

from adapter import search  # noqa: E402
from models import NpaProperty, PropertyCategory, SearchFilters  # noqa: E402


# ---------------------------------------------------------------------------
# Haversine distance
# ---------------------------------------------------------------------------


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance between two GPS points in kilometers."""
    R = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))


# ---------------------------------------------------------------------------
# Defaults by category
# ---------------------------------------------------------------------------

_DEFAULT_RADIUS_KM: dict[PropertyCategory, float] = {
    PropertyCategory.CONDO: 2.0,
    PropertyCategory.HOUSE: 3.0,
    PropertyCategory.TOWNHOUSE: 3.0,
    PropertyCategory.LAND: 5.0,
    PropertyCategory.COMMERCIAL: 3.0,
    PropertyCategory.FACTORY: 10.0,
    PropertyCategory.OTHER: 5.0,
}

_DEFAULT_SIZE_TOLERANCE: dict[PropertyCategory, float] = {
    PropertyCategory.CONDO: 0.30,
    PropertyCategory.HOUSE: 0.40,
    PropertyCategory.TOWNHOUSE: 0.40,
    PropertyCategory.LAND: 0.50,
    PropertyCategory.COMMERCIAL: 0.50,
    PropertyCategory.FACTORY: 0.50,
    PropertyCategory.OTHER: 0.50,
}


# ---------------------------------------------------------------------------
# Config model
# ---------------------------------------------------------------------------


class ProximityConfig(BaseModel, frozen=True):
    """Configuration for proximity search.

    None values fall back to per-category defaults.
    """

    radius_km: float | None = None
    size_tolerance_pct: float | None = None
    max_results: int = 20


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _total_wa(npa: NpaProperty) -> float | None:
    """Total land area in square wa (1 rai = 400 wa, 1 ngan = 100 wa)."""
    if npa.size_rai is None and npa.size_ngan is None and npa.size_wa is None:
        return None
    return (npa.size_rai or 0) * 400 + (npa.size_ngan or 0) * 100 + (npa.size_wa or 0)


def _within_size_tolerance(
    subject: NpaProperty,
    candidate: NpaProperty,
    category: PropertyCategory,
    tolerance_pct: float,
) -> bool:
    """True if candidate size is within ±tolerance_pct of subject size."""
    if category in (PropertyCategory.CONDO, PropertyCategory.COMMERCIAL, PropertyCategory.FACTORY):
        subj = subject.size_sqm
        cand = candidate.size_sqm
    else:
        subj = _total_wa(subject)
        cand = _total_wa(candidate)

    if subj is None or cand is None or subj == 0:
        return True  # not enough data to filter — keep candidate
    return abs(cand - subj) / subj <= tolerance_pct


def _bbox(
    lat: float, lon: float, radius_km: float
) -> tuple[float, float, float, float]:
    """Return (lat_min, lat_max, lon_min, lon_max) bounding box."""
    dlat = radius_km / 111.32
    dlon = radius_km / (111.32 * cos(radians(lat)))
    return lat - dlat, lat + dlat, lon - dlon, lon + dlon


def _apply_filters(
    subject: NpaProperty,
    candidates: list[NpaProperty],
    size_tol: float,
    max_results: int,
    *,
    use_distance: bool,
) -> list[dict[str, Any]]:
    """Filter candidates by category + size, exclude subject, add distance_km, sort."""
    ranked: list[tuple[float, dict[str, Any]]] = []

    for cand in candidates:
        # Exclude the subject property itself
        if cand.source == subject.source and cand.source_id == subject.source_id:
            continue
        # Same property category only
        if cand.category != subject.category:
            continue
        # Skip sold properties
        if cand.is_sold:
            continue
        # Size similarity
        if not _within_size_tolerance(subject, cand, subject.category, size_tol):
            continue

        # Compute distance
        if (
            use_distance
            and subject.lat is not None
            and subject.lon is not None
            and cand.lat is not None
            and cand.lon is not None
        ):
            dist = haversine_km(subject.lat, subject.lon, cand.lat, cand.lon)
        else:
            dist = float("inf")

        row = cand.model_dump()
        row["distance_km"] = round(dist, 3) if dist != float("inf") else None
        ranked.append((dist, row))

    ranked.sort(key=lambda x: x[0])
    return [r for _, r in ranked[:max_results]]


# ---------------------------------------------------------------------------
# Search strategies
# ---------------------------------------------------------------------------


def _search_gps(
    npa: NpaProperty,
    radius_km: float,
    size_tol: float,
    max_results: int,
) -> list[dict[str, Any]]:
    """GPS bbox search — returns empty list when subject has no coordinates."""
    if npa.lat is None or npa.lon is None:
        return []

    lat_min, lat_max, lon_min, lon_max = _bbox(npa.lat, npa.lon, radius_km)
    filters = SearchFilters(
        province=npa.province or None,
        lat_min=lat_min,
        lat_max=lat_max,
        lon_min=lon_min,
        lon_max=lon_max,
        limit=200,
        sort_by="price",
    )
    candidates = search(filters)
    return _apply_filters(npa, candidates, size_tol, max_results, use_distance=True)


def _search_district(
    npa: NpaProperty,
    size_tol: float,
    max_results: int,
) -> list[dict[str, Any]]:
    """District-wide fallback — no GPS filter."""
    filters = SearchFilters(
        province=npa.province or None,
        district=npa.district or None,
        limit=200,
        sort_by="price",
    )
    candidates = search(filters)
    return _apply_filters(npa, candidates, size_tol, max_results, use_distance=False)


def _search_province(
    npa: NpaProperty,
    size_tol: float,
    max_results: int,
) -> list[dict[str, Any]]:
    """Province-wide last resort."""
    filters = SearchFilters(
        province=npa.province or None,
        limit=200,
        sort_by="price",
    )
    candidates = search(filters)
    return _apply_filters(npa, candidates, size_tol, max_results, use_distance=False)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def find_comparables(
    npa: NpaProperty,
    config: ProximityConfig | None = None,
) -> list[dict[str, Any]]:
    """Find comparable NPA properties by GPS proximity, category, and size.

    Each result is a dict of all NpaProperty fields plus ``distance_km``
    (float km when GPS available, None otherwise).  Results are sorted by
    distance ascending and capped at ``config.max_results`` (default 20).

    Fallback strategy:
    1. GPS bbox at configured radius (skipped when subject has no GPS).
    2. District-wide search (no GPS filter) when fewer than 3 GPS comps found.
    3. Province-wide search when still fewer than 3 comps.
    """
    if config is None:
        config = ProximityConfig()

    cat = npa.category
    radius_km = config.radius_km if config.radius_km is not None else _DEFAULT_RADIUS_KM.get(cat, 5.0)
    size_tol = (
        config.size_tolerance_pct
        if config.size_tolerance_pct is not None
        else _DEFAULT_SIZE_TOLERANCE.get(cat, 0.50)
    )
    max_r = config.max_results

    # 1. GPS search
    results = _search_gps(npa, radius_km, size_tol, max_r)

    # 2. District fallback
    if len(results) < 3:
        results = _search_district(npa, size_tol, max_r)

    # 3. Province fallback
    if len(results) < 3:
        results = _search_province(npa, size_tol, max_r)

    return results

"""Bridge between npa-adapter (NpaProperty) and npa-screener (NpaCandidate).

Converts adapter output to screener input without coupling the adapter
to screener-specific models.  Lives in the screener repo.

Usage (v2 pipeline — extract_v2, screener_v2):
    from adapter_bridge import extract_candidates
    candidates = extract_candidates(["กรุงเทพมหานคร"], max_price=5_000_000)

Usage (demand scripts — raw NpaProperty):
    from adapter_bridge import search_bbox, search_district
    nearby = search_bbox(13.76, 100.57, radius_m=1000)
"""

from __future__ import annotations

import importlib.util
import math
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Dynamic import of adapter modules (symlinked from Collector)
# ---------------------------------------------------------------------------

_SCRIPT_DIR = Path(__file__).resolve().parent
_ADAPTER_DIR = _SCRIPT_DIR.parent.parent / "npa-adapter" / "scripts"


def _load_module(name: str, filename: str):
    """Load a module from the adapter directory via importlib."""
    path = _ADAPTER_DIR / filename
    if not path.exists():
        raise ImportError(f"Adapter module not found: {path}")
    spec = importlib.util.spec_from_file_location(name, str(path))
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


# Ensure adapter directory is on sys.path so adapter.py can `from models import ...`
_adapter_str = str(_ADAPTER_DIR)
if _adapter_str not in sys.path:
    sys.path.insert(0, _adapter_str)

# Load adapter models first (adapter.py depends on `from models import ...`)
_adapter_models = _load_module("_adapter_models", "models.py")
# Also register as "models" so adapter.py's `from models import ...` resolves
sys.modules["models"] = _adapter_models
_adapter = _load_module("_npa_adapter", "adapter.py")
_market_adapter = _load_module("_market_adapter", "market_adapter.py")

# Re-export market adapter function for screener use
batch_match_market = _market_adapter.batch_match_market

# Type aliases for readability
NpaProperty = _adapter_models.NpaProperty
SearchFilters = _adapter_models.SearchFilters
Source = _adapter_models.Source
PropertyCategory = _adapter_models.PropertyCategory

# Import screener v2 model
from models_v2 import NpaCandidate, PropertyType


# ---------------------------------------------------------------------------
# PropertyCategory → PropertyType mapping
# ---------------------------------------------------------------------------

_CATEGORY_TO_TYPE: dict[PropertyCategory, PropertyType] = {
    PropertyCategory.CONDO: PropertyType.CONDO,
    PropertyCategory.HOUSE: PropertyType.HOUSE,
    PropertyCategory.TOWNHOUSE: PropertyType.TOWNHOUSE,
    PropertyCategory.LAND: PropertyType.LAND,
    PropertyCategory.COMMERCIAL: PropertyType.COMMERCIAL,
    PropertyCategory.FACTORY: PropertyType.COMMERCIAL,
    PropertyCategory.OTHER: PropertyType.CONDO,  # matches extract_v2 fallback
}


# ---------------------------------------------------------------------------
# Vintage computation
# ---------------------------------------------------------------------------

_DT_FMTS = ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d")


def _compute_vintage_months(first_seen_at: str | None) -> int | None:
    """Months on market from first_seen_at, matching extract_v2's SQL logic."""
    if not first_seen_at:
        return None
    raw = str(first_seen_at)[:26]
    for fmt in _DT_FMTS:
        try:
            dt = datetime.strptime(raw, fmt)
            delta_s = (datetime.now() - dt).total_seconds()
            return int(round(delta_s / 86400.0 / 30.0))
        except ValueError:
            continue
    return None


# ---------------------------------------------------------------------------
# Core bridge: NpaProperty → models_v2.NpaCandidate
# ---------------------------------------------------------------------------


def to_candidate(npa: NpaProperty) -> NpaCandidate:
    """Convert an adapter NpaProperty to a screener v2 NpaCandidate."""
    price = npa.best_price_baht or npa.price_baht or 0.0
    sqm = npa.size_sqm
    price_sqm = price / sqm if (sqm and sqm > 0 and price > 0) else None

    ptype = _CATEGORY_TO_TYPE.get(npa.category, PropertyType.CONDO)

    floor_val = npa.extra.get("floor")
    building_age_val = npa.extra.get("building_age")

    return NpaCandidate(
        source=npa.source.value,
        source_id=str(npa.source_id),
        property_type=ptype,
        project_name=npa.project_name or "",
        province=npa.province or "",
        district=npa.district or "",
        subdistrict=npa.subdistrict or "",
        lat=npa.lat,
        lon=npa.lon,
        price_baht=price,
        size_sqm=sqm,
        price_sqm=price_sqm,
        bedroom=npa.bedroom,
        bathroom=npa.bathroom,
        floor=str(floor_val) if floor_val else None,
        building_age=int(building_age_val) if building_age_val else None,
        npa_vintage_months=_compute_vintage_months(npa.first_seen_at),
        auction_round=npa.total_auction_count if npa.total_auction_count > 0 else None,
    )


# ---------------------------------------------------------------------------
# High-level extraction (replaces extract_v2.extract_all_properties)
# ---------------------------------------------------------------------------

LEGACY_SOURCES = [Source.LED, Source.SAM, Source.BAM, Source.JAM, Source.KTB, Source.KBANK]
ALL_SOURCES = list(Source)

# Providers with GPS columns (LED has no lat/lon — excluded from bbox searches)
GPS_SOURCES = [s for s in Source if s != Source.LED]


def extract_candidates(
    provinces: list[str],
    max_price: float | None = None,
    property_types: list[str] | None = None,
    sources: list[Source] | None = None,
) -> list[NpaCandidate]:
    """Extract NPA candidates bridged to screener v2 format.

    Args:
        provinces: Thai province names (partial match via ILIKE)
        max_price: Upper price bound in baht
        property_types: PropertyType values e.g. ["condo", "house"]. None = all.
        sources: Provider list. None = all 12 providers.

    Returns:
        List of NpaCandidate ready for screener pipeline.
    """
    if sources is None:
        sources = ALL_SOURCES

    allowed: set[PropertyType] | None = None
    if property_types:
        allowed = {PropertyType(pt) for pt in property_types}

    all_candidates: list[NpaCandidate] = []

    for province in provinces:
        filters = SearchFilters(
            province=province,
            max_price=max_price,
            sources=sources,
            limit=10_000,
            sort_by="price",
        )
        results = _adapter.search(filters)

        for npa in results:
            candidate = to_candidate(npa)
            if allowed and candidate.property_type not in allowed:
                continue
            if candidate.price_baht <= 0:
                continue
            all_candidates.append(candidate)

    return all_candidates


# ---------------------------------------------------------------------------
# Convenience: bbox search for demand scripts (returns raw NpaProperty)
# ---------------------------------------------------------------------------


def search_bbox(
    lat: float,
    lon: float,
    radius_m: float = 1000,
    sources: list[Source] | None = None,
    property_type: str | None = None,
    max_price: float | None = None,
) -> list[NpaProperty]:
    """Search NPA properties within a GPS bounding box.

    Returns raw NpaProperty (not NpaCandidate) — demand scripts do
    their own aggregation and don't need the full candidate model.
    """
    dlat = radius_m / 111_320
    dlon = radius_m / (111_320 * math.cos(math.radians(lat)))

    filters = SearchFilters(
        lat_min=lat - dlat,
        lat_max=lat + dlat,
        lon_min=lon - dlon,
        lon_max=lon + dlon,
        property_type=property_type,
        max_price=max_price,
        sources=sources or GPS_SOURCES,
        limit=10_000,
    )
    return _adapter.search(filters)


def search_district(
    district: str,
    sources: list[Source] | None = None,
    max_price: float | None = None,
) -> list[NpaProperty]:
    """Search NPA properties by district name (ILIKE partial match)."""
    filters = SearchFilters(
        district=district,
        max_price=max_price,
        sources=sources or ALL_SOURCES,
        limit=10_000,
    )
    return _adapter.search(filters)

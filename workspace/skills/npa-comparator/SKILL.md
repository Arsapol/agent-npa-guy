---
name: npa-comparator
description: Cross-NPA comparison engine for Thai distressed properties. Finds comparable NPA properties by GPS proximity, computes area benchmarks (median/p25/p75), and returns type-specific comparison results (condo, land, house, commercial). Condos additionally use external market data from market_adapter when available. Non-condo is cross-NPA only — no external market data exists yet.
---

# NPA Comparator

Finds comparable NPA properties and benchmarks pricing for any property type.

## What It Does

Given an `NpaProperty`, returns a typed comparison showing:
- How its price ranks vs comparable NPAs in the same area
- Area benchmark (median / p25 / p75) for that property type + district
- Which investment strategies make sense for this type
- Honest `data_quality` signal (HIGH / MEDIUM / LOW)

## ⚠️ Honest Limitations

**Non-condo types (land, house, townhouse, commercial, factory) are cross-NPA comparison only.**

There is no external market data for these types in the current DB. The comparison signal answers: *"Is this NPA cheap relative to other NPAs of the same type in the same area?"* — not *"Is this NPA cheap relative to market asking prices?"*

Condo is the only type with true market comparison (via DDProperty, Hipflat, PropertyHub, ZMyHome).

**True market comparison for non-condo requires Phase 2 data sources:**
- DDProperty house/land listings (scraper currently indexes condos only)
- Treasury Department land appraisal API (ราคาประเมินที่ดิน)
- Baania.com house/land listings

## Usage

```python
import sys, os
sys.path.insert(0, '/path/to/npa-comparator/scripts')
from comparator import compare_npa

# Load any NpaProperty from npa-adapter
from adapter import search
from models import SearchFilters, Source

results = search(SearchFilters(province='กรุงเทพ', sources=[Source.BAM], limit=5))
npa = results[0]

result = compare_npa(npa)
print(result.comparison_type)       # "condo" / "land" / "house" / "commercial" / "other"
print(result.price_position)        # BELOW_P25 / BELOW_MEDIAN / ABOVE_MEDIAN / ABOVE_P75
print(result.data_quality)          # HIGH / MEDIUM / LOW
print(result.comparable_count)      # how many comps found
print(result.area_benchmark.median) # median price/unit for this area+type
```

## Per-Type Examples

### Condo

```python
from comparator import compare_npa
result = compare_npa(condo_npa)  # → CondoComparison

result.price_per_sqm          # subject price per sqm
result.median_market_sqm      # external market median (None if no project match)
result.discount_vs_market_pct # vs DDProperty/Hipflat (None if no market data)
result.discount_vs_npa_median_pct  # vs NPA median in same district
result.comparison_basis       # "market_verified" or "cross_npa"
```

### Land

```python
result = compare_npa(land_npa)  # → LandComparison

result.price_per_wa           # subject price per ตร.วา
result.total_area_wa          # total area (rai*400 + ngan*100 + wa)
result.median_area_price_per_wa  # benchmark median
result.discount_vs_npa_median_pct
```

### House / Townhouse

```python
result = compare_npa(house_npa)  # → HouseComparison

# PRIMARY metric — land area from title deed (reliable, standardized)
result.price_per_wa_land      # ฿/ตร.วา of land
result.total_land_wa
result.median_area_price_per_wa_land

# Unit price
result.price_per_unit

# Renovation (KBank/GSB/TTB only — None from other providers)
result.building_age_years     # None for most providers
result.renovation_estimate    # RangeEstimate(low, mid, high) or None
result.renovation_data_caveat # explains data limitation

# Usable area — informational only, NOT for comparison
result.usable_area_sqm        # raw from provider
result.price_per_sqm_usable   # UNRELIABLE — definition varies by project
result.usable_area_caveat     # "Use price_per_wa_land for comparison."
```

### Commercial / Factory

```python
result = compare_npa(commercial_npa)  # → CommercialComparison

result.price_per_sqm
result.median_area_price_per_sqm
result.property_subtype       # "shophouse" / "office" / "warehouse" / "factory"
result.commercial_density     # nearby commercial NPAs within 1km
```

## Strategy Mapping

| Type | Strategies |
|------|-----------|
| CONDO | rent, flip, expat_rental |
| LAND | land_bank, develop, subdivide |
| HOUSE | rent, flip, renovate_and_rent |
| TOWNHOUSE | rent, flip, renovate_and_rent |
| COMMERCIAL | lease, owner_occupy, redevelop |
| FACTORY | lease, owner_occupy |

## comparison_basis Field

| Value | Meaning |
|-------|---------|
| `"market_verified"` | Compared against DDProperty/Hipflat/PropertyHub/ZMyHome market data (condos with project name match only) |
| `"cross_npa"` | Compared against other NPA properties of same type in same area. **Not** a market price comparison. |

## data_quality Field

| Value | Threshold |
|-------|-----------|
| `"HIGH"` | >20 comps, or ≥5 comps with GPS |
| `"MEDIUM"` | 3–20 comps |
| `"LOW"` | <3 comps or no GPS |

## Proximity Search Config

Override defaults per call:

```python
from proximity import ProximityConfig, find_comparables

cfg = ProximityConfig(radius_km=1.0, size_tolerance_pct=0.20, max_results=10)
comps = find_comparables(npa, config=cfg)
```

Default radii: CONDO 2km, HOUSE/TOWNHOUSE/COMMERCIAL 3km, LAND 5km, FACTORY 10km.
Fallback: district-wide → province-wide when <3 GPS comps found.

## Architecture

```
npa-comparator/
  scripts/
    models.py      — Pydantic v2 comparison models (BaseComparison + type-specific)
    proximity.py   — GPS bbox → haversine filter → district/province fallback
    benchmarks.py  — cross-NPA median/p25/p75 per category+district (24h cache)
    comparator.py  — dispatcher: compare_npa() → typed result
```

All scripts import from `npa-adapter` (symlinked from Collector) via `sys.path`. No raw SQL — uses `adapter.search()` exclusively.

## Phase 2 Roadmap

To enable true market comparison for non-condo:

1. **DDProperty houses/land** — Modify Collector's ddproperty scraper to capture non-condo listings with `property_type` field.
2. **Treasury land appraisal API** — Government ราคาประเมินที่ดิน by deed number. Strongest signal for land.
3. **Baania/Thinkofliving** — House project market prices.

Once available, `comparator.py` condo path pattern can be replicated for each type.

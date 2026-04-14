# Market Comparator Skill

Compare NPA auction prices against market listings (DDProperty, PropertyHub, Hipflat) for the same area. Apple-to-apple comparison with discount scoring.

## Usage

### CLI

```bash
# By coordinate
python scripts/compare.py --lat 7.06 --lon 100.52 --radius 2000

# By asset ID (auto-resolves GPS from DB)
python scripts/compare.py --asset-id 1869319 --source LED

# By road name (finds NPA properties near a named road)
python scripts/compare.py --road "กาญจนวณิชย์" --radius 500

# JSON output (for agent consumption)
python scripts/compare.py --road "กาญจนวณิชย์" --format json
```

### Python API

```python
from scripts.compare import run_comparison, find_npa_near_road, find_market_comps, compare_npa_vs_market

# Quick comparison (returns formatted string)
output = run_comparison(road="กาญจนวณิชย์", radius_m=500, fmt="table")

# Granular control
npa_list = find_npa_near_road("กาญจนวณิชย์", radius_m=500)
market_list = find_market_comps(lat=7.06, lon=100.52, radius_m=2000)
results = compare_npa_vs_market(npa_list, market_list)
```

## Output Columns

| Column | Description |
|--------|-------------|
| source | NPA provider (LED, BAM, KBank, etc.) |
| asset_id | Provider's unique identifier |
| type | condo / land_building / land |
| price | NPA auction/selling price (฿) |
| area | Land area in sqw or sqm |
| ฿/unit | Price per sqw (land) or sqm (condo) |
| dist_m | Distance from search point/road |
| market_med | Median market price for same property type |
| market_range | Min-max market price range |
| discount% | (market_median - npa) / market_median |
| rating | DEEP_DISCOUNT / GOOD_DEAL / FAIR / OVERPRICED / NO_COMP |

## Rating Scale

| Rating | Discount % | Signal |
|--------|-----------|--------|
| DEEP_DISCOUNT | ≥ 40% | Strong buy signal |
| GOOD_DEAL | 20-40% | Worth investigating |
| FAIR | 0-20% | At or near market |
| OVERPRICED | < 0% | Above market — avoid |
| NO_COMP | — | No market data for comparison |

## Property Type Matching

Apple-to-apple comparison:
- **condo** (ห้องชุด/คอนโด) → compared with condo listings → ฿/sqm
- **land_building** (ที่ดินพร้อมสิ่งปลูกสร้าง) → compared with house listings → ฿/sqw
- **land** (ที่ดินเปล่า) → compared with land listings → ฿/sqw

## Data Sources

| Source | GPS | Text fallback | Coverage |
|--------|-----|---------------|----------|
| DDProperty | Partial | full_address ILIKE | Best for BKK, partial provinces |
| PropertyHub | Project-level | — | Good provincial coverage |
| Hipflat | Project-level | — | Project-level stats only |

## Dependencies

- PostGIS (`osm_roads` table from road-proximity skill)
- NPA database tables (all 12 providers)
- Market listing tables (DDProperty, PropertyHub, Hipflat)

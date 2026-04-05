# NPA Screener Skill

Screen NPA condo properties against the verified investment criteria framework.
Takes raw NPA property data and outputs a scored, filtered shortlist.

## When to Use
- After scraping new NPA data from any provider
- When user asks to evaluate a specific NPA property
- When running periodic screening of all providers
- Before recommending any NPA property for purchase

## Screening Pipeline

### Step 1: Gate Check (auto-reject)
```
REJECT if ANY:
  - leasehold AND remaining_years < 30
  - year_built < 2006
  - npa_price_per_sqm >= market_price_per_sqm (DDProperty/Hipflat)
  - title_type IN ('นส.3', 'นส.3ก')
  - npa_concentration_in_building > 8%
  - structural_notice = true
```

### Step 2: Threshold Check (must pass ALL)
```
PASS if ALL:
  - real_discount >= 20%  (vs DDProperty/Hipflat, NOT provider appraisal)
  - year_built BETWEEN 2008 AND current_year
  - distance_to_education_anchor <= 800m
  - gross_yield >= tier_minimum  (Tier A: 6%, B: 7%, C: 8%)
  - active_resale_listings >= 3
  - freehold = true
```

### Step 3: BTS/MRT Tier Assignment
```
IF distance_to_bts <= 800m AND distance_to_anchor <= 800m:
  tier = 'A', min_yield = 6%, min_discount = 15%
ELIF distance_to_bts <= 1500m AND distance_to_anchor <= 800m:
  tier = 'B', min_yield = 7%, min_discount = 20%
ELSE:
  tier = 'C', min_yield = 8%, min_discount = 25%
  REQUIRE verified_rental_demand = true
  REQUIRE anchor_enrollment >= 15000
```

### Step 4: Score (0-100)
```python
score = (
    discount_score * 0.25 +      # >=35%: 100, 20-35%: 60, <20%: 0
    age_score * 0.15 +            # 2015-2018: 100, 2008-2014: 70, 2006-2008: 40
    bts_score * 0.15 +            # <400m: 100, 400-600m: 70, 600-800m: 40
    anchor_score * 0.10 +         # <400m: 100, 400-600m: 70, 600-800m: 40
    yield_score * 0.10 +          # >=9%: 100, 7-9%: 70, 6-7%: 40
    developer_score * 0.10 +      # known: 100, mid: 60, unknown: 20
    building_size_score * 0.05 +  # 200+: 100, 50-200: 60, 30-50: 30
    anchor_type_score * 0.05 +    # tier1 intl/top5 uni: 100, top20: 70, other: 40
    listing_score * 0.05          # 50+: 100, 10-50: 60, 3-10: 30
)
```

### Step 5: Summer Vacancy Adjustment
```
IF tier == 'C' AND anchor_type == 'university':
  effective_yield = gross_yield * 0.75  # 3 months vacancy
  IF effective_yield < min_yield:
    verdict = 'AVOID'
```

### Step 6: Output
```
STRONG BUY: score >= 80 AND discount >= 30% AND yield >= 7%
BUY:        score >= 60 AND discount >= 20% AND yield >= tier_minimum
WATCH:      score >= 40 OR one threshold borderline
AVOID:      score < 40 OR any gate failed
```

## Education Anchor Profiles

| Type | Unit Size | Rent Range | Tenant | Vacancy Risk |
|---|---|---|---|---|
| University | 22-35 sqm (studio), 35-50 sqm (1BR) | 5,500-9,000 THB/mo | Students, young pros | HIGH (summer) |
| Intl School | 50-120 sqm (2-3BR) | 30,000-100,000+ THB/mo | Expat families | LOW (year-round) |
| Thai School | 35-80 sqm (1-2BR) | 12,000-40,000 THB/mo | Provincial families | LOW-MED |

## Market Verification Protocol

NEVER skip this step. For every candidate:

1. Search DDProperty: `"{project name}" site:ddproperty.com`
2. Search Hipflat: `"{project name}" site:hipflat.co.th`
3. Record: lowest asking price/sqm, median asking price/sqm, number of listings
4. Search rental: `"{project name} ให้เช่า"`
5. Record: rental range, number of rental listings
6. Calculate: real_discount = (market_median - npa_price) / market_median
7. Calculate: gross_yield = (annual_rent / npa_price)

If zero listings found on both DDProperty and Hipflat → liquidity = ZERO → AVOID.

## Known Traps Database (update as discovered)

| Trap Pattern | Examples | Detection |
|---|---|---|
| Provider appraisal inflation | BAM "35% below appraisal" = 0% below market | Always verify on DDProperty |
| NPA above market | Park 24, Lumpini 24, Clover ลาดพร้าว 83 | Compare to listings |
| Leasehold disguised | Triple Y สามย่าน, CU land properties | Check underlying land title |
| Old building yield trap | Monterey Place 1994, รื่นรมย์ 1997 | Year built check |
| Micro-project illiquidity | 5-unit buildings near ม.รังสิต | Building size check |
| NPA concentration | Multiple providers selling same building | Cross-query all 6 providers |
| Discount > 55% | Usually hidden defects or juristic debt | Extra due diligence required |

## Data Source Caveats

| Provider | GPS Quality | Price Unit | Notes |
|---|---|---|---|
| LED | None (no lat/lon) | Satang (÷100) | Keyword match only, distances unverified |
| SAM | Property-level | Baht | Good quality |
| BAM | Property-level (100%) | Baht | Best coordinate coverage |
| JAM | Subdistrict centroids | Baht | ~75% share coordinates. Distances approximate. |
| KTB | Property-level (95%) | Baht | Small inventory |
| KBank | Property-level (100%) | Baht | Good quality |

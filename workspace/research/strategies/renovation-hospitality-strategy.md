# Renovation / Hospitality Strategy — Metrics Research
**Date:** 2026-04-05  
**Researcher:** Renovation & Hospitality Strategy Agent  
**For:** Multi-Strategy NPA Screener

---

## Executive Summary

The renovation/hospitality play in Thailand is **high-upside but legally hazardous**. Short-term Airbnb-style rentals (<30 days) are technically illegal under the Hotel Act 2547. Enforcement intensified in 2025 with coordinated crackdowns. The viable path is either: (a) **30-day minimum stays** (legal, lower rates, steady demand from expats/nomads), or (b) **serviced apartment** positioning with professional management to blur the line. Pure Airbnb-flip in condos should be scored as a high-risk sub-strategy.

**Viable sub-strategies ranked by legal risk:**

| Sub-strategy | Legal risk | Yield potential |
|---|---|---|
| Serviced apartment (30+ day min) | LOW | 5-8% gross |
| Co-living / digital nomad house | LOW-MEDIUM | 6-10% gross |
| Mini resort / villa (landed) | MEDIUM | 8-15% gross |
| Airbnb-style STR (<30 days, condo) | HIGH | 12-20% gross (if operating) |

---

## Legal Risk Framework (Critical — Read First)

### The Law

**Hotel Act B.E. 2547 (2004), Section 15 + 59:**
- Any rental < 30 consecutive days = hotel business requiring license
- Penalty: up to 1 year imprisonment + fine up to ฿20,000 + ฿10,000/day continuing
- Recent 2025 court cases: fines exceeding ฿100,000

**Condominium Act B.E. 2522, Section 17/1:**
- Juristic person (condo committee) can ban commercial activity in units
- Violation fine: up to ฿50,000 + ฿5,000/day

**Hotel licensing for condos:**
- Properties with > 4 rooms / > 20 guests: full hotel license required
- Non-hotel license (< 4 rooms): available to Thai nationals only
- In practice: 0% of Bangkok's 16,806 Airbnb listings hold valid STR licenses

### 2025 Enforcement Reality

- March 2025: Interior Ministry directed DOPA to intensify crackdowns
- High-profile crackdown in Pattaya targeting foreign investors with multiple condo units
- Authorities actively monitor Airbnb listings and send undercover inspectors
- Intensified enforcement in tourist-heavy districts of Bangkok

### Legal Compliance Scorecard (automatable)

| Factor | Score | Rule |
|---|---|---|
| Minimum stay ≥ 30 days | +2 | Legal safe harbor |
| Building juristic allows commercial use | +2 | Check condo rules |
| Property type = villa/house (not condo) | +2 | Easier to license |
| Area = Phuket/Koh Samui (light enforcement) | +1 | Geography matters |
| Foreign owner + condo + <30 days | -3 | Maximum risk |

**Legal risk score: ≥ 3 = proceed, < 1 = reject for STR strategy**

---

## Metric Definitions

### 1. Daily Rate Potential (DRP)

**Formula:**
```
DRP = Area_ADR × Size_multiplier × Condition_multiplier

Size multipliers: Studio (<35 sqm) = 0.85, 1BR (35-60 sqm) = 1.0, 2BR (60-90 sqm) = 1.4
Condition multiplier: unrenovated = 0.6, cosmetic reno = 0.85, full reno = 1.0, premium = 1.2
```

**Area ADR benchmarks (2025 data, THB/night):**
| Area | Low season ADR | High season ADR | Annual median ADR |
|---|---|---|---|
| Bangkok (all) | ฿1,200 | ฿2,800 | ฿1,815 |
| Sukhumvit / Silom | ฿1,500 | ฿3,500 | ฿2,200 |
| Bangkok Riverside | ฿1,800 | ฿4,000 | ฿2,600 |
| Phuket | ฿2,200 | ฿5,500 | ฿3,038 |
| Chiang Mai | ฿900 | ฿2,400 | ฿1,556 |
| Pattaya | ฿1,100 | ฿3,200 | ฿1,900 |

**Data source:** AirBtics / AirROI STR analytics (no DB table; requires external API or manual update quarterly)  
**Threshold:** DRP > ฿1,500/night = viable STR, < ฿800/night = reject

---

### 2. Occupancy Rate by Area (OCC)

**Formula:**
```
OCC = Annual_booked_nights / 365
Annualized gross = DRP × OCC × 365
```

**Benchmark data (2025 actual):**
| Market | Median OCC | Top-10% OCC | Low-25% OCC |
|---|---|---|---|
| Bangkok | 66% (241 nights) | 89%+ | 20% |
| Phuket | 65% (237 nights) | 85%+ | 22% |
| Chiang Mai | 65% (237 nights) | 84%+ | 18% |

**Seasonality:**
- Peak: January, February, December (NOV-FEB = high season, AUG/SEP lowest)
- High season premium: ~40-55% above low season rates
- Low season OCC can drop to 30-40% for average properties

**Data source:** No DB column; derive from `location_intel` area data + proximity to tourist nodes  
**Proxy metric (automatable):** Tourism_proximity_score (distance to attractions/hotels hub) as OCC proxy  
**Threshold:** Expected OCC > 55% = viable, < 40% = reject  
**Weight:** 15% of sub-strategy score

---

### 3. Renovation Cost Ratio (RCR)

**Formula:**
```
RCR = Reno_cost / Purchase_price
Reno_cost = sqm × cost_per_sqm_tier

Cost tiers (2025 Bangkok actuals):
- Cosmetic (paint, fixtures, furniture): 3,000-5,000 THB/sqm
- Standard full fit-out: 15,000-20,000 THB/sqm
- Premium fit-out: 25,000-30,000 THB/sqm
- Luxury fit-out: 35,000-45,000 THB/sqm
```

**For hospitality/STR renovation, recommended tier:**
- Airbnb optimized (durable finishes, photogenic design, smart home): 18,000-25,000 THB/sqm
- Co-living conversion (shared spaces, individual rooms): 12,000-18,000 THB/sqm
- Serviced apartment (professional, functional): 15,000-22,000 THB/sqm

**Example: 30 sqm studio at ฿800,000 purchase price:**
```
Reno cost (standard): 30 × 18,000 = ฿540,000
RCR = 540,000 / 800,000 = 0.675
Total acquisition = ฿1,340,000
```

**Data source:** Calculated from `sqm` column in NPA tables + property type  
**Threshold:** RCR < 0.40 = efficient, 0.40-0.70 = acceptable, > 0.70 = marginal, > 1.0 = reject  
**Weight:** 10% of sub-strategy score

---

### 4. Renovation ROI (RROI)

**Formula:**
```
Monthly gross (STR) = DRP × OCC × 30
Monthly gross (long-term pre-reno) = Market_long_term_rent × 0.7  (NPA typical vacancy discount)

Rent premium = Monthly_gross_STR - Monthly_gross_LT
Payback months = Reno_cost / Rent_premium
RROI (annual) = (Rent_premium × 12) / Reno_cost
```

**Benchmarks:**
- STR gross monthly (Bangkok median 30 sqm): ฿1,815 × 66% × 30 = ~฿35,900
- Long-term rent (Bangkok 30 sqm): ฿12,000-18,000/month
- Rent premium from STR: ~฿18,000-23,000/month
- Reno cost (30 sqm at ฿18,000/sqm): ฿540,000
- Payback: 540,000 / 20,000 = 27 months
- RROI = 240,000 / 540,000 = 44% (before operating costs)

**Operating cost deductions (STR-specific):**
- Platform fee (Airbnb): 3% host fee
- Management fee (if outsourced): 15-25% of revenue
- Cleaning: ฿500-1,000/turnover
- Utilities: ฿2,000-4,000/month
- Net deduction: ~35-40% of gross

**Net RROI formula:**
```
Net_RROI = RROI × (1 - 0.375)  (approximate net factor)
```

**Data source:** Calculated; inputs from `sqm`, `asking_price`, area ADR benchmarks  
**Threshold:** Net RROI > 20% = strong, 10-20% = acceptable, < 10% = weak  
**Weight:** 20% of sub-strategy score

---

### 5. Legal Compliance Score (LCS)

**Formula (0-10 scale):**
```
LCS = 0
+ 3 if min_stay_capability ≥ 30 days (building allows, or villa/house property type)
+ 2 if building_type != "condominium" (house, shophouse, villa)
+ 2 if juristic_allows_commercial (from condo rules research)
+ 2 if area == tourist destination with light enforcement (Phuket, Koh Samui)
+ 1 if owner = Thai national (can apply non-hotel license)
- 3 if condo + foreign owner + STR intent
- 2 if building has active short-term rental bans documented
```

**Data source:**
- `property_type` column in NPA tables
- Building juristic status: requires manual research per building
- Approximate automatable: property_type + geography + building age

**Threshold:** LCS ≥ 6 = proceed, 3-5 = flag for manual review, < 3 = reject for STR  
**Weight:** 25% of sub-strategy score (heaviest — legal risk is a blocker)

---

### 6. Competition Density (CD)

**Formula:**
```
CD = active_STR_listings_within_1km / total_residential_units_within_1km

Saturation proxy (automatable with GPS):
- Count DDProperty/Hipflat listings in same district
- Cross-reference with tourism demand proxy
```

**Area saturation benchmarks (2025):**
| Area | Status | Active listings |
|---|---|---|
| Lower Sukhumvit (Nana-Asok) | Oversaturated | Very high |
| Silom / Sathorn | Oversaturated | High |
| Ari / Ladprao | Moderate | Medium |
| Riverside (outside hotel cluster) | Under-served | Low-medium |
| Ratchada / Huay Kwang | Moderate | Medium |
| On Nut / Phra Khanong | Low | Growing |

**Data source:** No direct DB column; proxy using `district` from NPA tables against area saturation lookup table  
**Threshold:** CD < 0.05 = low competition (good), 0.05-0.15 = moderate, > 0.15 = saturated  
**Weight:** 10% of sub-strategy score

---

### 7. Tourism Demand Proximity (TDP)

**Formula:**
```
TDP_score = weighted sum of:
- Distance to nearest BTS/MRT (meters): weight 30%
- Distance to major tourist attraction/mall (meters): weight 25%
- Distance to international hospital (meters): weight 15%
- Distance to nightlife/entertainment district (meters): weight 20%
- Distance to international airport (km): weight 10%
```

**Score mapping:**
```
BTS/MRT < 300m = 10pts; 300-800m = 7pts; 800-1500m = 4pts; > 1500m = 1pt
Tourist attraction < 500m = 10pts; 500-1500m = 7pts; 1500-3000m = 4pts; > 3km = 0pt
```

**High-demand tourist zones (Bangkok):**
- Siam/Asok/Nana/Ekkamai corridor
- Silom/Sathorn financial + tourist zone
- Riverside (Saphan Taksin area)
- Chatuchak weekend market area

**Data source:** GPS from NPA tables + `location_intel` skill (BTS/MRT proximity already computed)  
**Threshold:** TDP_score > 60 = high demand, 40-60 = moderate, < 40 = low  
**Weight:** 20% of sub-strategy score

---

### 8. Foreigner Rental Premium (FRP)

**Note:** No publicly available dataset precisely quantifies the premium. Based on market observation:

**Empirical estimates:**
- Short-term foreigners (Airbnb tourists): pay 40-80% more than Thai long-term tenants for same unit
- Expat long-term (1-year lease): 15-30% premium over Thai tenant rates
- Serviced apartment (furnished, bills included): 30-50% premium vs unfurnished
- Co-living (all-inclusive): priced as THB-denominated but targets foreigners at ฿8,000-15,000/room/month

**Operationalization:**
```
FRP_multiplier:
- Unit in tourist/expat zone + furnished + internet: 1.3
- Same unit unfurnished in residential zone: 1.0
- Premium international design + bilingual listing: 1.15 additional
```

**Data source:** Qualitative; encode as binary flag: `foreigner_demand_area` (Sukhumvit, Silom, Riverside, Near international school/hospital = true)  
**Weight:** Not standalone — baked into DRP area multipliers above

---

## Sub-Strategy Scoring Models

### A. Short-Term Rental (Airbnb-style)

**Scoring weights:**
| Metric | Weight | Score range |
|---|---|---|
| Legal Compliance Score | 30% | 0-10 |
| Daily Rate Potential | 20% | 0-10 |
| Occupancy (area proxy) | 15% | 0-10 |
| Renovation ROI | 20% | 0-10 |
| Competition Density | 15% | 0-10 (inverted) |

**Minimum threshold to qualify:** LCS ≥ 6 AND TDP_score ≥ 50 AND RCR < 0.70  
**Auto-reject triggers:** Condo + foreign owner intent + no 30-day capability = reject

---

### B. Serviced Apartment (30+ day furnished)

**Scoring weights:**
| Metric | Weight | Score range |
|---|---|---|
| Legal Compliance Score | 15% | 0-10 (lower weight — legal) |
| Monthly yield vs market | 30% | 0-10 |
| Renovation ROI | 20% | 0-10 |
| Expat demand proximity | 20% | 0-10 |
| Building quality / age | 15% | 0-10 |

**Benchmark:** Serviced apartment gross yield 5-8%; target ≥ 6.5% net after costs  
**Sweet spot:** 1BR, 35-55 sqm, Sukhumvit/Silom, year 2008-2018, renovated to ฿20,000/sqm

---

### C. Co-living / Digital Nomad

**Scoring weights:**
| Metric | Weight | Score range |
|---|---|---|
| Room density potential | 25% | 0-10 |
| Coworking proximity | 20% | 0-10 |
| Internet infrastructure (fiber) | 15% | 0-10 |
| Monthly per-room rate | 25% | 0-10 |
| Building rules compliance | 15% | 0-10 |

**Revenue model:**
```
Gross = num_rooms × monthly_room_rate
- Studio converted to 2 rooms: 2 × ฿8,000 = ฿16,000 vs ฿14,000 undivided (14% lift)
- 2BR converted to 4 rooms: 4 × ฿7,500 = ฿30,000 vs ฿20,000 (50% lift)
```

**Target:** Areas near WeWork/coworking (Asok, Ari, Chiang Mai Nimman, Phuket Chalong)  
**Legal status:** 30+ day stays → legal; Airbnb-style turnover → Hotel Act applies

---

### D. Mini Vacation / Resort-style (Villa/Landed)

**Only viable for:** Houses, villas, landed property — not condos  
**Legal path:** Private home rental with proper licensing; villas can apply for small hotel license  

**Key metrics:**
- Renovation cost to resort standard: ฿25,000-45,000/sqm
- Target ADR: ฿3,000-8,000/night (Bangkok villa) to ฿5,000-15,000/night (Phuket pool villa)
- Occupancy target: 55-65%
- Gross yield: 8-15% (higher due to premium pricing)

**Auto-filter:** `property_type` must be house/villa; GPS must show low density residential or tourist area

---

## Composite Renovation/Hospitality Score

**For screener implementation:**

```python
def renovation_hospitality_score(property):
    # Step 1: Legal compliance — hard filter
    lcs = compute_legal_compliance_score(property)
    if lcs < 3:
        return {"score": 0, "reject_reason": "legal_risk_too_high"}
    
    # Step 2: Sub-strategy selection
    if property.type in ["house", "villa"] and lcs >= 6:
        sub_strategy = "mini_resort"
        max_yield = 0.12
    elif property.sqm >= 60 and lcs >= 5:
        sub_strategy = "co_living"
        max_yield = 0.09
    elif lcs >= 6 and tdp_score >= 50:
        sub_strategy = "short_term_rental"
        max_yield = 0.14
    else:
        sub_strategy = "serviced_apartment"
        max_yield = 0.07
    
    # Step 3: Financial viability
    rcr = renovation_cost_ratio(property)
    rroi = renovation_roi(property, sub_strategy)
    
    # Step 4: Composite score (0-100)
    score = (
        lcs * 0.25 * 10 +          # 25% legal
        tdp_score * 0.20 +          # 20% tourism demand
        rroi_score * 0.20 +         # 20% renovation ROI
        drp_score * 0.20 +          # 20% rate potential
        competition_score * 0.15    # 15% competition
    )
    
    return {"score": score, "sub_strategy": sub_strategy, "max_yield": max_yield}
```

---

## Key Thresholds Summary Table

| Metric | Reject | Flag | Proceed |
|---|---|---|---|
| Legal Compliance Score | < 3 | 3-5 | ≥ 6 |
| Renovation Cost Ratio | > 0.80 | 0.50-0.80 | < 0.50 |
| Net Renovation ROI | < 10% | 10-20% | > 20% |
| Occupancy proxy (area) | < 40% | 40-55% | > 55% |
| Daily Rate Potential | < ฿800 | ฿800-1,500 | > ฿1,500 |
| Tourism Demand Proximity | < 40 | 40-60 | > 60 |
| Competition Density | > 0.20 | 0.10-0.20 | < 0.10 |

---

## DB Columns Needed (Implementation Notes)

| Metric | Source | DB / Computed |
|---|---|---|
| `property_type` | All NPA tables | Existing column |
| `sqm` / `usable_area` | All NPA tables | Existing column |
| `asking_price` | All NPA tables | Existing column |
| `lat`, `lon` | All NPA tables | Existing — use for TDP |
| `district` / `province` | All NPA tables | Existing — map to area ADR |
| `building_year` | BAM/JAM/KTB/KBank | Existing where scraped |
| `legal_compliance_score` | Computed | New computed column |
| `area_adr_benchmark` | External lookup | New lookup table by district |
| `area_occ_benchmark` | External lookup | New lookup table by district |
| `reno_cost_estimate` | Computed | = sqm × tier_rate |
| `renovation_roi` | Computed | Formula above |
| `tourism_demand_score` | Computed | From location_intel skill |

---

## Data Sources

- AirBtics Bangkok 2025: ADR ฿1,815, OCC 66%, annual revenue ฿414K
- AirROI Bangkok 2025: Median OCC 66%, top-10% OCC 89%+
- Phuket STR: ADR ฿3,038, OCC 65%, 11,809 active listings
- Chiang Mai STR: ADR ฿1,556, OCC 65%, 6,919 active listings
- Global Property Guide Q3 2025: Bangkok average gross yield 6.05%
- Condodee renovation guide 2025: Standard fit-out ฿15,000-20,000/sqm; luxury ฿35,000-45,000/sqm
- Rumavi / Thai Thailand Advisor 2026: Hotel Act penalties, enforcement timeline
- bangkokresidential.com 2025: Serviced apartment yields 5-6%, avg ฿82,800/month
- AirBnb Bangkok legal: 0% of 16,806 listings hold valid STR license

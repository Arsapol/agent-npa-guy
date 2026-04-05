# Land Banking Strategy — Measurable & Automatable Metrics
**Research Date:** 2026-04-05
**Analyst:** Land Banking Strategy Researcher (Team: strategy-research, Task #3)

---

## Executive Summary

Land banking in Thai NPA context means acquiring distressed land/property at below-market prices in corridors where confirmed infrastructure or zoning changes will drive appreciation. The holding period is typically 3–8 years. Cheap holding cost (BoT rate at 1.00%) and aggressive Bangkok expansion make this viable — but only where infrastructure is CONFIRMED, not planned or rumored.

Key insight from research: **Transit proximity premium is measurable and quantifiable.** Areas along the Pink Line rose 20.7% YoY; Samut Prakan (new city plan August 2025) rose 44% YoY. EEC Bang Lamung rose 126.5% YoY. These are the benchmarks for target corridor selection.

---

## Infrastructure Status Classification (MANDATORY Pre-Filter)

Before scoring any metric, classify infrastructure status. This classification governs weight multipliers throughout.

| Status | Definition | Weight Multiplier |
|--------|-----------|-------------------|
| **CONFIRMED** | Under construction + EIA approved + funding secured | 1.0× |
| **APPROVED** | BOC/Cabinet approval + EIA filed, not yet started | 0.7× |
| **PLANNED** | Government announcement, no EIA, no funding | 0.3× |
| **RUMORED** | Developer marketing, no government announcement | 0.0× (auto-reject) |

**Data source:** MRTA/EXAT/DOH official project pages, BOC announcements, NESDC EEC portal.
**How to automate:** Scrape MRTA project pages quarterly; maintain a `infrastructure_projects` table with `status`, `confirmed_date`, `expected_completion`.

---

## Metric 1: Transit Proximity Score (TPS)

**Category:** Transit-Oriented

### Formula
```
TPS = Σ (Station_Weight_i × Distance_Decay_i × Status_Multiplier_i)

Where:
  Station_Weight = 1.0 (BTS/MRT operational)
                 = 0.85 (under construction, opening ≤2 yrs)
                 = 0.60 (under construction, opening 2-5 yrs)
                 = 0.00 (planned only — no weight)

  Distance_Decay = 1.0 (0–500m)
                 = 0.75 (500–1000m)
                 = 0.50 (1000–1500m)
                 = 0.20 (1500–2500m)
                 = 0.00 (>2500m)

  Status_Multiplier = from Infrastructure Status Classification above
```

### Current Bangkok Lines (as of April 2026)
| Line | Status | Key Corridor |
|------|--------|-------------|
| BTS Sukhumvit/Silom | OPERATIONAL | Core Bangkok |
| MRT Blue/Purple | OPERATIONAL | Hua Lamphong → Tao Poon |
| Yellow Line | OPERATIONAL (2023) | Lat Phrao → Samrong |
| Pink Line | OPERATIONAL (June 2025) | Khae Rai → Min Buri |
| Orange Line East | CONFIRMED, opening ~2027 | Thailand Cultural Ctr → Min Buri |
| Orange Line West | CONFIRMED, opening ~2030 | Thailand Cultural Ctr → Bang Khun Non |
| Green Line Extensions | OPERATIONAL | Samut Prakan/Bang Pu |

### Thresholds
| TPS | Rating | Action |
|-----|--------|--------|
| ≥ 0.70 | Tier A | Strong buy zone |
| 0.40–0.69 | Tier B | Viable with price discipline |
| 0.20–0.39 | Tier C | Only if deep discount (>35%) |
| < 0.20 | Reject | Transit premium cannot be modelled |

### Weight in Land Banking Score
**25%**

### DB Implementation
```sql
-- Existing: ktb_properties, kbank_properties etc have lat/lng
-- New table needed:
CREATE TABLE infrastructure_projects (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL,  -- 'BTS','MRT','Expressway','Industrial','EEC'
    status TEXT NOT NULL,  -- 'operational','confirmed','approved','planned','rumored'
    expected_completion DATE,
    confirmed_date DATE,
    geom GEOMETRY(LINESTRING/POINT, 4326),  -- PostGIS
    source_url TEXT,
    last_verified DATE
);
```

---

## Metric 2: Land Price Momentum Index (LPMI)

**Category:** Price Trend Analysis

### Formula
```
LPMI = (Current_District_Index / Index_4Q_Ago) - 1

Expressed as YoY % change in district land price index.
Source: REIC (Real Estate Information Center) quarterly land price indices.
```

### Benchmark Data (Q3 2025, REIC)
| Area | YoY LPMI | Driver |
|------|----------|--------|
| Bang Phli–Bang Bo (Samut Prakan) | +44.0% | Industrial/logistics expansion |
| Bang Lamung, Chonburi (EEC) | +126.5% | Foreign manufacturing relocation |
| Si Racha, Chonburi (EEC) | +88.6% | Port + industrial proximity |
| Pink Line corridor (Nonthaburi) | +20.7% | Transit opening June 2025 |
| Samut Prakan–Phra Pradaeng | +26.1% | New city plan Aug 2025 |
| Greater Bangkok average | +14.3% | General expansion |
| Rayong (EEC) | +43.5% | Production base relocations |

### Thresholds
| LPMI | Rating |
|------|--------|
| > +25% YoY | Strong momentum |
| +10% to +25% | Positive trend |
| +5% to +10% | Weak / watch |
| < +5% or negative | No land banking play here |

### Weight in Land Banking Score
**20%**

### Data Source & Automation
- **Primary:** REIC quarterly land price index reports (reic.or.th) — scrape quarterly
- **Proxy (automatable now):** Cross-reference `bam_properties`, `jam_properties`, `sam_properties` price history by `province`/`district` — compute median price per sqm trend over rolling 12 months from existing DB
- **SQL proxy:**
```sql
SELECT
    province,
    district,
    AVG(price_baht / area_sqm) AS price_per_sqm,
    date_trunc('quarter', scraped_at) AS quarter
FROM bam_properties
WHERE area_sqm > 0
GROUP BY province, district, quarter
ORDER BY province, district, quarter;
```

---

## Metric 3: Holding Cost Burden (HCB)

**Category:** Financial Viability

### Formula
```
Annual_HCB = Land_Tax + Opportunity_Cost + Maintenance

Land_Tax:
  Year 1–3 (vacant): 0.30% × Appraised_Value
  Year 4–6 (vacant): 0.60% × Appraised_Value  [+0.30% every 3 yrs]
  Year 7–9 (vacant): 0.90% × Appraised_Value
  Year 10+ (vacant): up to 3.0% × Appraised_Value (cap)

  Note: Agricultural use registered = 0.15% (much lower — can register as orchard)

Opportunity_Cost = Purchase_Price × BoT_Policy_Rate (currently 1.00%)

Maintenance = ~0.1% of purchase price annually (fencing, clearing)

Total_HCB_% = (Annual_HCB / Purchase_Price) × 100
```

### Holding Cost Examples (per ฿1M purchase price)
| Year | Tax (vacant) | Opp. Cost (1%) | Maintenance | Annual Total |
|------|-------------|----------------|-------------|--------------|
| 1 | ฿3,000 | ฿10,000 | ฿1,000 | ฿14,000 (1.4%) |
| 3 | ฿3,000 | ฿10,000 | ฿1,000 | ฿14,000 (1.4%) |
| 4 | ฿6,000 | ฿10,000 | ฿1,000 | ฿17,000 (1.7%) |
| 7 | ฿9,000 | ฿10,000 | ฿1,000 | ฿20,000 (2.0%) |

**Agricultural registration trick:** If land can be registered for agricultural use (orchard, rice field), tax drops to 0.15% of appraised value. This is legal if land actually has crops. Reduces holding cost significantly.

### Thresholds
| HCB (annual) | Rating |
|-------------|--------|
| < 2.0% purchase price | Acceptable (land banking viable) |
| 2.0–3.5% | Marginal (needs faster appreciation) |
| > 3.5% | High burden (only justifiable if LPMI > 30%) |

### Weight in Land Banking Score
**15%**

---

## Metric 4: Zoning Upside Score (ZUS)

**Category:** Regulatory / Development Potential

### Formula
```
ZUS = (Target_FAR / Current_FAR) × Zoning_Change_Probability × Status_Multiplier

Zoning_Change_Probability:
  New city plan enacted (law in force)              = 1.0
  Draft revision published (BMA/Provincial hearing) = 0.6
  BMA/Cabinet commitment announced                  = 0.4
  Historical precedent only                         = 0.2
```

### Bangkok Color Zone Reference (City Plan 2556 + 4th Revision)
| Zone Color | Use | Max FAR |
|-----------|-----|---------|
| Red (พ.1–พ.5) | Commercial/mixed | 7.0–10.0 |
| Orange (ย.7–ย.10) | High-density residential | 5.0–7.0 |
| Yellow (ย.3–ย.6) | Medium-density residential | 2.5–4.0 |
| Green (ก.) | Low-density residential | 0.5–1.0 |
| Light green | Agricultural/conservation | 0.1 |
| Purple | Industrial | Varies |

**4th Revision impact (BMA, expected enforcement ~2025):**
- Green zones near transit corridors → reclassified to yellow/orange
- Medium-density zones near BTS stations → upgraded to high-density (+FAR 20%)
- Samut Prakan new plan (August 2025): green/low-density → medium/high near transit

### Thresholds
| ZUS | Rating |
|-----|--------|
| ≥ 3.0 | Exceptional upside (FAR tripling) |
| 2.0–2.9 | Strong upside |
| 1.5–1.9 | Moderate upside |
| 1.0–1.4 | Minimal upside (already zoned well) |
| < 1.0 | Downzoning risk — reject |

### Weight in Land Banking Score
**20%**

### Data Source
- BMA City Planning Dept: bangkokplanning.go.th
- Samut Prakan, Nonthaburi, Pathum Thani provincial planning offices
- EEC zoning portal: eec.or.th
- Our `zoning-check` skill already covers Bangkok 2556 — needs extension for 4th revision + provincial plans

---

## Metric 5: Development Density Potential (DDP)

**Category:** Build-Out Value

### Formula
```
DDP = (Max_FAR × Land_Area_sqm × Buildable_GFA) / Purchase_Price

Buildable_GFA = Max_FAR × Land_Area (adjusted for OSR setbacks)
OSR (Open Space Ratio): typically 30–40% of plot for medium/high density

Effective_GFA = Max_FAR × Land_Area × (1 - OSR_fraction)

DDP_ratio = Effective_GFA / Purchase_Price_per_sqm
  (how many buildable sqm of GFA per baht spent)
```

### Thresholds
| DDP Ratio | Meaning |
|-----------|---------|
| > 5.0 sqm GFA per ฿1,000 spent | Very high development potential |
| 3.0–5.0 | Good |
| 1.5–3.0 | Moderate |
| < 1.5 | Low — likely already priced in |

### Weight in Land Banking Score
**10%**

---

## Metric 6: Infrastructure Proximity Composite (IPC)

**Category:** Infrastructure-Driven (non-transit)

### Formula
```
IPC = MAX(
    Expressway_Score,
    Industrial_Estate_Score,
    EEC_Zone_Score,
    Airport_Score
)

Expressway_Score:
  < 2km from confirmed new interchange     = 1.0
  2–5km from confirmed interchange         = 0.7
  < 2km from existing interchange          = 0.5
  5–10km                                   = 0.2

Industrial_Estate_Score:
  Within 5km of major estate (Amata/WHA/Rojana) = 1.0
  5–15km                                         = 0.6
  15–30km                                        = 0.3

EEC_Zone_Score:
  Within designated EEC S-curve zone     = 1.0
  EEC province (Chonburi/Rayong/Chachoengsao) = 0.6
  Adjacent province                      = 0.2

Airport_Score:
  < 10km from BKK/Suvarnabhumi           = 0.8
  < 15km from DMK (Don Mueang)           = 0.6
  < 15km from U-Tapao (EEC cargo hub)    = 0.7
```

### Key Infrastructure Projects 2025–2030 (CONFIRMED/APPROVED)
| Project | Status | Corridor Impact |
|---------|--------|----------------|
| Orange Line East | CONFIRMED (~2027) | Min Buri, Lat Krabang, Ramkhamhaeng |
| Orange Line West | CONFIRMED (~2030) | Taling Chan, Bang Khun Non |
| M82 Motorway (Bang Khun Thian–Ban Phaeo) | CONFIRMED | Samut Sakhon corridor |
| Rama III–Dao Khanong Expressway (18.7km) | CONFIRMED (open ~2025) | South BKK |
| US$3.2B new expressway (Samut Sakhon–Bang Phli) | APPROVED | SW + SE BKK link |
| U-Tapao Airport expansion (EEC) | CONFIRMED | Rayong, Bang Lamung |
| Pink Line Muang Thong spur | CONFIRMED (open June 2025) | Impact/Muang Thong |

### Weight in Land Banking Score
**10%** (overlaps with TPS for transit; this covers non-transit infra)

---

## Metric 7: Comparable Land Transaction Discount (CLTD)

**Category:** Pricing Discipline

### Formula
```
CLTD = (Comparable_Market_Price - NPA_Asking_Price) / Comparable_Market_Price × 100%

Comparable_Market_Price = Median of:
  - REIC district land price index (converted to ฿/sqm/rai)
  - Recent LED auction results (same tambon, same zone color)
  - BAM/JAM/SAM listed prices for similar land plots nearby
  - Treasury appraised value (กรมธนารักษ์) if available
```

### Thresholds
| CLTD | Rating |
|------|--------|
| ≥ 35% below comparable | Strong buy — NPA discount working |
| 25–34% below | Acceptable |
| 15–24% below | Marginal — price risk |
| < 15% below | Reject — NPA premium not justified |
| At or above market | Hard reject |

**Critical note:** Provider appraisals (SAM, BAM internal) are NOT comparables — always use REIC or actual transaction data.

### Weight in Land Banking Score
**15%** (price discipline is non-negotiable gate)

**Hard reject rule:** If CLTD < 15%, score the property 0 regardless of other metrics.

---

## Composite Land Banking Score (LBS)

### Formula
```
LBS = (TPS × 0.25) + (LPMI_normalized × 0.20) + (ZUS_normalized × 0.20)
    + (CLTD_normalized × 0.15) + (HCB_inverse × 0.15)
    + (IPC × 0.05) + (DDP_normalized × 0.05)

All components normalized to 0.0–1.0 before weighting.
```

### Score Normalization
| Metric | Min (0.0) | Max (1.0) |
|--------|-----------|-----------|
| TPS | 0.0 | 0.7+ |
| LPMI | 5% YoY | 50% YoY |
| ZUS | 1.0 | 4.0+ |
| CLTD | 15% | 50%+ |
| HCB (inverted) | 3.5% annual | 1.0% annual |
| IPC | 0.0 | 1.0 |
| DDP | 1.5 | 5.0+ |

### Decision Thresholds
| LBS | Decision |
|-----|---------|
| ≥ 0.70 | Buy — strong land banking candidate |
| 0.55–0.69 | Conditional buy — validate ZUS or LPMI first |
| 0.40–0.54 | Hold/watch — revisit in 6 months |
| < 0.40 | Pass |

---

## Hard Reject Filters (Any One = Immediate Reject)

1. **Infrastructure status = RUMORED** — no weight, no scoring
2. **CLTD < 15%** — not buying at a meaningful discount
3. **Title deed = นส.3 or สค.1** — no chanote, no land banking
4. **Leasehold** — can't appreciate capital value for the holder
5. **HCB > 5% annual** — holding cost destroys IRR
6. **Flood zone HIGH** — land banking in flood-prone areas needs 40%+ discount; if CLTD < 40%, reject
7. **EEC zone but not S-curve industry target** — speculative without demand anchor
8. **Land area < 100 sqw** — too small for land banking play (minimum viable plot)

---

## Exit Strategy Framework

Land banking only makes sense with a defined exit. Auto-score should flag viable exits.

| Exit Type | Trigger Condition | Target IRR |
|-----------|------------------|-----------|
| Transit opening premium | Station opens within 1km, price +20–40% | 15–25% IRR |
| Zoning upgrade flip | City plan enacted, FAR doubled | 20–35% IRR |
| Developer sale | Branded developer acquires neighboring plots | 25–40% IRR |
| Industrial land flip | Industrial estate announces expansion | 20–30% IRR |
| EEC enterprise zone | S-curve zone designation confirmed | 20–45% IRR |

**Holding period assumption:** 3–7 years. At 1.4% annual holding cost, break-even appreciation needed = ~10% total (3yr hold) to ~12% (7yr hold) before any profit. Target minimum appreciation: 35% over hold period.

---

## DB Schema Requirements

### New Tables Needed
```sql
-- Infrastructure projects (transit + roads + industrial)
CREATE TABLE infrastructure_projects (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('BTS','MRT','Expressway','Motorway','Industrial','Airport','EEC','Other')),
    status TEXT NOT NULL CHECK (status IN ('operational','confirmed','approved','planned','rumored')),
    confirmed_date DATE,
    expected_completion DATE,
    last_verified DATE NOT NULL DEFAULT CURRENT_DATE,
    source_url TEXT,
    geom GEOMETRY(GEOMETRY, 4326),  -- PostGIS — line or point
    notes TEXT
);

-- District land price index (from REIC or computed from NPA DB)
CREATE TABLE district_land_price_index (
    id SERIAL PRIMARY KEY,
    province TEXT NOT NULL,
    district TEXT NOT NULL,
    period DATE NOT NULL,  -- first day of quarter
    price_index NUMERIC,  -- REIC index points
    median_price_per_sqm NUMERIC,  -- derived from NPA DB if REIC unavailable
    yoy_change_pct NUMERIC,
    source TEXT NOT NULL,  -- 'REIC' or 'NPA_DB_derived'
    UNIQUE (province, district, period, source)
);
```

### Existing Tables That Feed Land Banking Score
| DB Table | Fields Used | Metric |
|----------|------------|--------|
| `bam_properties`, `jam_properties`, `ktb_properties`, `kbank_properties`, `sam_properties` | `lat`, `lng`, `price_baht`, `area_sqm`, `asset_type` | CLTD, DDP |
| `bam_price_history`, `jam_price_history` etc. | `price_baht`, `recorded_at` | LPMI proxy |
| `flood_risk` (if exists) | `risk_level` | Hard reject filter |
| Future `infrastructure_projects` | `geom`, `status` | TPS, IPC |

---

## Data Collection Gaps & Next Steps

| Gap | Priority | Action |
|-----|----------|--------|
| REIC district land price index | HIGH | Scrape reic.or.th quarterly PDFs → parse to `district_land_price_index` |
| MRTA/EXAT project geometries | HIGH | Download KML/GeoJSON from official portals → `infrastructure_projects` |
| Bangkok 4th revision zoning map | HIGH | Scrape BMA city planning dept PDFs → extend `zoning-check` skill |
| EEC zone boundaries (GeoJSON) | MEDIUM | Download from eec.or.th → spatial query layer |
| Samut Prakan new city plan (Aug 2025) | MEDIUM | Provincial planning office — document only |
| Treasury appraisal (กรมธนารักษ์) per rai by area | MEDIUM | treasurydept.go.th — reference for CLTD baseline |
| Industrial estate boundary polygons | LOW | IEAT portal or Thai-Koujyo.com |
| Population growth by amphoe (district) | LOW | DOPA annual registration data |

---

## Key Risks for Land Banking in Thai NPA Context

1. **Infrastructure delays are common** — Orange Line East civil works done since 2023 but still not open as of April 2026. Price premium may partially correct before opening.
2. **Speculation already priced in** — EEC Bang Lamung +126.5% YoY means the easy money is gone; need to find second-wave beneficiaries.
3. **Foreign ownership restriction** — Thai land cannot be owned by foreigners directly. Land banking is structurally Thai-only or requires complex (risky) structures.
4. **LBT escalation** — Vacant land tax escalates every 3 years. A 7-year hold on expensive land crosses two escalation thresholds.
5. **Liquidity** — Land (especially outer Bangkok/EEC) has thin buyer pools. Exit may take 12–24 months.
6. **Zoning delay risk** — Bangkok 4th city plan revision has been delayed multiple times (already extended 6 months as of 2024). "Expected 2025" is not confirmed.
7. **Rumored vs confirmed** — Developer marketing routinely labels PLANNED infrastructure as CONFIRMED. Always verify against MRTA/EXAT/DOH primary sources.

---

## Sources

- Bangkok Post: Orange Line full open 2030
- Khaosod English: Orange Line 28 stations
- Wikipedia: Pink Line Bangkok, Mass Rapid Transit Master Plan
- Nation Thailand: EEC land prices Q1 2025 (47B baht, +31% YoY)
- Bangkok Post: EEC land prices surge Q1 2025
- Thailand-Property.com: Bang Lamung +126.5%
- Bangkok Post: Bangkok land prices Q3 2025 (+14.3% YoY, Bang Phli +44%)
- Nation Thailand: Bangkok zoning deliberation extended
- The Legal Co.: Bangkok 4th revision city plan implications
- Conrad Properties / LexBangkok: Land & Building Tax 2026 guide
- Cushman & Wakefield: Thailand Industrial MarketBeat Q2 2025
- Nation Thailand: EXAT 11 expressway projects 10-year plan
- DOH: M82 Bang Khun Thian–Ban Phaeo motorway
- Worldometer/MacroTrends: Bangkok metro population 11.4M (2025)
- REIC (via Bangkok Post): District land price indices Q3 2025

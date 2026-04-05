# BUY-AND-RENT Strategy: Measurable Metrics for NPA Screener

**Author:** Rental Strategy Researcher
**Date:** 2026-04-05
**Status:** Draft — pending cross-debate

---

## 1. Strategy Overview

Buy a distressed NPA condo at ≥20% market discount. Hold and rent to a target tenant type identified by nearby demand anchors. Exit via resale in year 3–7 when cycle recovers (bottom estimated 2027-2028).

**Market context headwinds (2026):**
- 24.8% Bangkok metro condo vacancy (macro)
- 60-month sell-out period for new stock
- Listed rents 10–15% above transaction rents (use 85% haircut on listed rents)
- CBD Sukhumvit/Sathorn vacancy 18–22% despite prime branding
- Prime transit-connected units: 5–8% vacancy (structural demand floor)
- Mortgage rejection 40–70% — most landlords/sellers are cash-constrained

**Market context tailwinds (2026):**
- DTV (Destination Thailand Visa) driving digital nomad inflow
- Bangkok prime apartment rents +8.4% YoY late 2025
- Downtown apartment occupancy 94.4% Q2 2025 for professionally managed stock
- Thai apartment market ~745K units, 90% occupancy for sub-10K/mo segment

---

## 2. Tenant Sub-Types & Demand Anchors

| Sub-type | Primary anchor | Secondary anchor | Target unit | Typical rent/mo |
|---|---|---|---|---|
| Student | University ≤ 800m | BTS/MRT access | 22–35 sqm studio | 5,500–9,000 THB |
| Thai family | Thai school ≤ 800m | Expressway ≤ 1km | 35–80 sqm 1–2BR | 12,000–40,000 THB |
| Expat/Foreigner | Intl school ≤ 2km | BTS < 600m | 50–120 sqm 2–3BR | 30,000–100,000+ THB |
| Worker | Hospital/industrial zone ≤ 1.5km | MRT/BTS ≤ 1.5km | 22–45 sqm studio/1BR | 6,000–15,000 THB |

---

## 3. Metric Definitions

### 3.1 Core Yield Metrics

#### M1 — Gross Rental Yield (GRY)
```
GRY = (Estimated Annual Rent / Purchase Price) × 100
```
- **Estimated Annual Rent** = Market listed rent × 0.85 (transaction discount) × 12
  - The 0.85 factor already embeds negotiation friction and ~1 month effective vacancy.
  - Do NOT additionally multiply by 11 months — that double-counts the discount.
  - Vacancy is modeled separately in M2 (NRY) as a holding cost, not here.
  - **Seasonal query adjustment:** If listing data is queried in April–June (Q2 trough), apply:
    `adjusted_rent = listed_rent × 0.85 × 1.12` to correct for seasonal depression (~12% below annual median).
    For queries in other months: no adjustment.
- **Data source:** `hipflat_projects.avg_rent_sqm` or `zmyhome_listings.price` (rent column) filtered by project/area; fallback `ddproperty_listings` rent ads
- **Threshold:** Floors are set so that GRY minimum implies NRY ≥ 3% after typical holding costs (GNHC ≤ 50%). At GNHC = 50%, GRY must be ≥ 6% to produce NRY ≥ 3%.

| Anchor type | Reject | Minimum | Good | Best |
|---|---|---|---|---|
| University (Tier C, no BTS) | < 9% | 9% | 10–11% | ≥ 11% |
| University (Tier B, BTS 800–1500m) | < 8% | 8% | 9–10% | ≥ 10% |
| University (Tier A, BTS < 800m) | < 7% | 7% | 8–9% | ≥ 9% |
| Thai school | < 6.5% | 6.5% | 7.5–8.5% | ≥ 8.5% |
| Intl school | < 6% | 6% | 7–8% | ≥ 8% |
| Hospital/worker | < 7% | 7% | 8–9% | ≥ 9% |

**Why floors increased vs. prior version:** At GNHC 50–65% (observed in worked examples), the old 7% GRY floor produced NRY 2.45–2.72% — below the M2 reject threshold of 3%. Thresholds are now set so GRY minimum × (1 − 0.50) ≥ 3% at minimum, with a buffer for higher GNHC scenarios.

- **Weight in scoring:** 15%

---

#### M2 — Net Rental Yield (NRY)
```
NRY = ((Annual Rent - Holding Costs) / Purchase Price) × 100
```

**Holding Costs (annual, modeled by unit size):**

| Cost item | Rate | Notes |
|---|---|---|
| CAM fee | 40–80 THB/sqm/month | Use 60 THB/sqm as default; query juristic fee from `npa_properties.cam_fee` if available |
| Property tax (Land & Building) | 0.02% of assessed value (residential/rental) | Assessed value ≈ purchase price × 0.9 |
| Building insurance (unit) | 0.15% of purchase price per year | ~4,000–12,000 THB/yr typical |
| Vacancy reserve | GRY × 8.3% (= 1 month) for Tier A/B; × 16.7% (= 2 months) for Tier C student | Structural, not operational |
| Rental agent/management fee | 8% of annual rent (standard Bangkok agent) | If self-managed: 0%, but model 5% for pipeline conservatism |
| Maintenance reserve | 0.5% of purchase price per year | Cosmetic repairs, appliance replacement |
| Income tax on rental | 30% flat deduction allowed; effective tax ~5–15% of net after deduction | Use 10% of gross as conservative estimate |

**Default NRY model for 30 sqm unit at 1.5M THB purchase:**
- CAM: 60 × 30 × 12 = 21,600 THB
- Tax: 1,350,000 × 0.02% = 270 THB (minimal at this price)
- Insurance: 1,500,000 × 0.15% = 2,250 THB
- Vacancy reserve: 1 month (Tier A/B) or 2 months (Tier C student) of adjusted annual rent (from M1)
- Agent: 8% of adjusted annual rent
- Maintenance reserve: 7,500 THB
- Tax: ~10% of adjusted annual rent

**Note:** Adjusted annual rent here = listed × 0.85 × 12 (from M1). Vacancy is a separate line item in M2, not embedded in M1. No double-count.

**Threshold:**
- Primary: NRY ≥ 3% (cash purchase). If NRY < 3%, reject for cash purchase.
- Leverage override: If NRY < 3% but CoCR ≥ tier minimum (Tier A: 5%, Tier B: 7%, Tier C: 9%) with DSCR > 1.25 at 70% LTV, property passes for leveraged rental. Do NOT reject solely on NRY when leverage is available.
- Hard reject: NRY < 1.5% regardless of leverage (negative carry even with mortgage service).

- **Data source:** Derived from M1 + holding cost model
- **Weight in scoring:** 20%

---

#### M3 — Rent-to-Market Discount Gap (RMDG)
```
RMDG = ((Market Comparable Rent - NPA Listed Rent Estimate) / Market Comparable Rent) × 100
```
Purpose: Catches cases where market rent is already too low to justify NPA purchase price.

- **Data source:** `hipflat_price_history`, `zmyhome_listings`, `ddproperty_listings` — median rent in same subdistrict, same sqm band (±20%)
- **Threshold:** NPA unit must not require rent BELOW market to achieve occupancy. If comparable rent data shows < 5,500 THB/mo for studios in area, the product-market fit is broken.
- **Weight in scoring:** 5% (flag only — does not score positively, just avoids a trap)

---

#### M4 — Price-to-Rent Multiple (PRM)
```
PRM = Purchase Price / (Monthly Rent × 12)
```
Lower = faster payback.

- **Threshold:** Reject if PRM > 20x (annual rent < 5% of price). Best is PRM ≤ 14x (≥ 7.1% gross).
- **Data source:** Derived
- **Weight in scoring:** 5% (redundant with GRY but validates rent data from two angles)

---

### 3.2 Demand Quality Metrics

#### M5 — Demand Anchor Score (DAS)
```
DAS = primary_anchor_score + secondary_anchor_score
```

**Primary anchor scoring (0–50 pts):**

| Condition | Points |
|---|---|
| University > 30K enrollment ≤ 400m | 50 |
| University > 30K enrollment 400–800m | 40 |
| University 15K–30K enrollment ≤ 400m | 35 |
| University 15K–30K enrollment 400–800m | 25 |
| Intl school (>500 students) ≤ 800m | 40 |
| Intl school (>500 students) 800m–2km | 28 |
| Thai school (>3K students) ≤ 400m | 30 |
| Thai school (>3K students) 400–800m | 20 |
| Hospital (≥ 300 beds) ≤ 500m | 35 |
| Hospital (≥ 300 beds) 500m–1.5km | 25 |
| Industrial zone ≤ 2km | 20 |
| CBD office cluster ≤ 1km | 30 |

**Secondary anchor scoring (0–20 pts):**
- BTS/MRT < 400m: +20
- BTS/MRT 400–800m: +15
- BTS/MRT 800–1500m: +8
- Expressway ramp < 1km: +5
- Mall/market < 500m: +5

**Threshold:** DAS ≥ 40 to pass Gate 2. DAS < 25 = auto-reject (no structural tenant demand).

- **Data source:** `location_intel` skill output — `bts_stations`, `mrt_stations`, `schools`, `hospitals` tables (or GPS haversine against known anchor coordinates)
- **Weight in scoring:** 20%

---

#### M6 — Comparable Rental Listings Count (CRLC)
```
CRLC = count of active rental listings in same building or within 200m, same sqm band (±30%)
```
Purpose: Measures market liquidity for rentals (not just resale).

- **Data source:** `ddproperty_listings` WHERE listing_type = 'rent' AND project_match; `zmyhome_listings` WHERE type = 'rent'
- **Threshold:**

| Count | Interpretation | Action |
|---|---|---|
| ≥ 10 active rent listings | Strong rental market | Proceed |
| 5–9 listings | Moderate — verify with DAS | Proceed with caution |
| 3–4 listings | Thin market — higher vacancy risk | Require ≥ 1% GRY premium |
| < 3 listings | No verifiable rental market | Reject or require manual field check |

- **Weight in scoring:** 10%

---

#### M7 — Days-on-Market Proxy (DOMP)
```
DOMP = median days a rental listing stays active in same area/project
```
A low DOMP indicates fast absorption (structural demand). A high DOMP = oversupply or wrong price point.

- **Benchmark (2026):**
  - Prime transit area (Asoke-Phrom Phong, Rama 9): 10–25 days
  - Well-located outer area: 25–40 days
  - Remote or oversupplied: 45–70 days
- **Threshold:** DOMP > 60 days = demand signal failure. Require extra 1% yield premium.
- **Data source:** Not available in current DB directly. Proxy: compare listing `created_at` vs `updated_at` in `ddproperty_listings` or `zmyhome_listings`. If many listings stay > 60 days, flag it.
- **Weight in scoring:** 5% (proxy quality is low — flag only)

---

### 3.3 Supply Risk Metrics

#### M8 — NPA Concentration in Building (NCB)
```
NCB = (NPA units in same building across all 6 providers / total units in building) × 100
```
Already in existing framework as auto-reject > 8%. Included here for completeness.

- **Data source:** `npa-adapter` cross-query by project name + province
- **Threshold:** > 8% = auto-reject (juristic collapse risk)
- **Weight in scoring:** Hard gate, not weighted

---

#### M9 — Rental Supply Pipeline (RSP)
```
RSP = count of new condo projects within 1km, EIA approved or under construction, total units ≥ 200, expected completion within 24 months
```
New supply compresses rents and increases vacancy.

- **Data source:** Not in current DB. Sourced from: DDProperty project listings (filter "new project" + "under construction"), PropertyHub `propertyhub_projects.status` field
- **Threshold:**
  - 0 new projects: no penalty
  - 1–2 projects (< 1,000 total new units): flag, yield must absorb 1–2% compression
  - 3+ projects or > 1,000 units: yield floor +2%, consider rejecting Tier C
- **Weight in scoring:** 5% (penalty only)

---

### 3.4 Holding Cost & Tax Metrics

#### M10 — Gross-to-Net Yield Haircut (GNHC)
```
GNHC = 1 - (NRY / GRY)
```
Measures how much yield is consumed by friction costs.

- **Expected range:** 25–40% haircut is normal in Bangkok (gross 7% → net 4.2–5.25%)
- **Threshold:** If GNHC > 50%, the cost structure is destroying the investment case. Walk away or renegotiate price.
- **Data source:** Derived from M1 and M2
- **Weight in scoring:** Informational only — inputs already in M2

---

#### M11 — Break-Even Holding Period (BEHP)
```
BEHP (years) = (Acquisition costs + Renovation) / (Annual Net Rent - Annual Holding Costs)
```
Where acquisition costs = transfer fee (2% of assessed value) + specific business tax (3.3% if held < 5 years) + stamp duty (0.5%) + agent fee (3%)

- **Benchmark:** BEHP ≤ 3 years for university/worker; ≤ 4 years for intl school (higher rent, higher price)
- **Threshold:** BEHP > 5 years = reject (ties capital through the expected cycle bottom)
- **Data source:** Derived — uses `property-calc` skill formulas
- **Weight in scoring:** 5%

---

## 4. Seasonality Adjustments by Tenant Type

| Tenant type | Peak months (raise rent 5–10%) | Off-peak (budget vacancy) | Annual vacancy budget |
|---|---|---|---|
| Student (university) | Aug–Oct (semester start), Jan (2nd sem) | Apr–Jun (end of year, graduation) | 2–3 months for Tier C |
| Thai family | Jan–Mar (new school year search), Jul | Dec (holiday freeze) | 1 month |
| Expat/Foreigner | Sep–Nov (corporate relocation), Jan | Apr–Jun (Songkran disruption), Aug | 1–1.5 months |
| Worker (hospital/industrial) | Year-round (low seasonality) | None significant | 0.5–1 month |

**Critical note:** Listed rents in Apr–Jun (Thai summer / post-Songkran) are 10–15% below Nov–Feb peak. Do NOT anchor rent estimates to Apr–Jun listings. Use median of 12-month range or ask agent for "normal month" figures.

---

## 5. Real Rental Demand Verification (Anti-Gaming Protocol)

Listed rents overstate achievable rents by 10–15%. Use these 3 signals, require ≥ 2 to confirm demand:

**Signal 1 — Listing volume + recency**
Query `zmyhome_listings` + `ddproperty_listings` for ≥ 3 active rental ads in same project/200m radius. If listings older than 90 days, they're likely overpriced and stuck — discount them.

**Signal 2 — Comparable recent transactions (rent)**
Check `hipflat_price_history` for rent PSM trends. If avg PSM rent is falling YoY, apply extra vacancy buffer.

**Signal 3 — Building occupancy proxy**
NPA concentration < 3% in building = likely high owner-occupancy = low distress = building in demand. NPA concentration 3–8% = mixed signal.

**Bonus signal (manual, not automatable):** Line up 3 rental agents in area (Dot Property, RentHub, DDProperty agents) and ask for actual recent lease prices. Adjust model rent downward to agent consensus.

---

## 6. Net Yield Model: Full Example

Formula convention used throughout:
- Adjusted annual rent = listed_rent × 0.85 × 12 (NO additional monthly multiplier)
- Vacancy reserve = separate line in M2 holding costs (1 month for Tier A/B, 2 months for Tier C)
- GRY = adjusted_annual_rent / purchase_price × 100

---

**Example A — Reject (at-market price):**
28 sqm studio, university Tier B (BTS 1km, uni 500m)
Purchase price: 1,200,000 THB | Listed rent: 7,500 THB/mo
Adjusted annual rent: 7,500 × 0.85 × 12 = 76,500 THB
**GRY:** 76,500 / 1,200,000 = 6.38% — FAILS minimum 8% for Tier B. **Reject.**

---

**Example B — Pass GRY, marginal NRY (NPA discount):**
Same property, NPA price: 740,000 THB (38% discount from 1,200,000)
**GRY:** 76,500 / 740,000 = 10.34% ✓ passes Tier B minimum (8%)

Annual holding costs (M2):
- CAM: 60 × 28 × 12 = 20,160
- Insurance: 740,000 × 0.15% = 1,110
- Property tax: 666,000 × 0.02% = 133
- Agent fee: 76,500 × 8% = 6,120
- Maintenance: 740,000 × 0.5% = 3,700
- Income tax (10% of gross): 76,500 × 10% = 7,650
- Vacancy reserve (1 month, Tier B): 6,375

**Total costs:** 45,248 THB/yr
**Net annual income:** 76,500 - 45,248 = 31,252 THB
**NRY:** 31,252 / 740,000 = 4.22% ✓ passes 3% threshold
**GNHC:** 1 - (4.22/10.34) = 59.2% — above 50%, borderline. Flag for leverage check.

Leverage check (70% LTV at 3%):
- Loan: 740,000 × 0.70 = 518,000 THB | Annual debt service: ~29,100 THB
- Cash invested: 222,000 + 14,800 closing = 236,800 THB
- Cash flow after debt: 31,252 - 29,100 = 2,152 THB/yr
- **CoCR: 2,152 / 236,800 = 0.9%** — DSCR = 31,252 / 29,100 = 1.07 < 1.25. Leverage does NOT rescue this property at current rent level.
- **Conclusion: Cash-only, NRY 4.22% is acceptable but thin. Flag as marginal.**

---

**Example C — Strong pass (Tier A, higher rent):**
28 sqm studio, Tier A (BTS 300m, uni 400m)
NPA price: 740,000 THB | Listed rent: 9,500 THB/mo (Tier A premium)
Adjusted annual rent: 9,500 × 0.85 × 12 = 96,900 THB
**GRY:** 96,900 / 740,000 = 13.1% ✓ strong

Holding costs: same CAM + insurance + tax; agent fee 96,900 × 8% = 7,752; vacancy 0.5 month = 3,979; tax 9,690; maintenance 3,700
**Total costs:** 46,524 THB
**NRY:** (96,900 - 46,524) / 740,000 = 50,376 / 740,000 = 6.81% ✓ strong
**GNHC:** 48.1% ✓ under 50%

**Conclusion from examples:** The NPA discount is the critical lever. At 38% discount + Tier A rent premium, NRY reaches 6.8% with GNHC < 50%. At market price with Tier B rent, GRY itself fails the new floor. Unit size, rent tier, and NPA discount interact — the screener must evaluate all three simultaneously.

---

## 7. Scoring Scorecard

| Metric | Weight | Formula | Reject Threshold |
|---|---|---|---|
| M1 Gross Rental Yield | 15% | per anchor type table above | < minimum for tier |
| M2 Net Rental Yield | 20% | < 3% = reject | < 3% |
| M5 Demand Anchor Score | 20% | 0–70 pts scale | < 40 pts |
| M6 Comparable Rental Listings | 10% | count active rent ads | < 3 |
| M1 × Price Discount (yield × discount) | 10% | GRY × (discount%) | < 7% × 20% = 1.4 |
| M9 Supply Pipeline Penalty | 5% | count new projects | penalty applied |
| M7 Days-on-Market Proxy | 5% | days listed | > 60d = penalty |
| M4 Price-to-Rent Multiple | 5% | < 20x | > 20x |
| M11 Break-Even Holding Period | 5% | years | > 5 years |
| M3 Rent-to-Market Gap | 5% | flag only | below local floor |
| **Total** | **100%** | | |

**Score interpretation:**
- ≥ 75: Strong rental candidate
- 55–74: Acceptable — proceed with manual demand verification
- 40–54: Marginal — requires local agent confirmation + price negotiation
- < 40: Reject

---

## 8. Assumptions & Defensibility Notes

**Why 85% haircut on listed rents?**
Listed rents on DDProperty/ZMyHome/Hipflat are asking prices. Bangkok Residential (2025) and multiple agent surveys confirm transaction rents run 10–15% below listed. This is not optional. Using listed rents directly inflates GRY by 1–2 percentage points and creates false positives.

**Why 10–15% tax estimate vs 30% standard deduction?**
The 30% standard deduction applies to gross income (not assessable income). After the 30% deduction, rental income is taxed at progressive rates. For a Thai resident with 72K THB/month total income (rental + salary), effective marginal rate on the rental portion is ~15–20%. The 10% of gross estimate is a reasonable simplification for pipeline screening — does not replace actual tax planning.

**Why separate student vacancy from other types?**
Student leases are shorter (1 academic year) and have concentrated move-in/move-out at semester boundaries. Buildings that are ONLY near universities with NO BTS have structural 3-month summer vacancy (April–June). This is not resolvable through pricing — it's a product-market fit issue. Buildings with both university AND BTS attract workers/expats who fill summer gaps.

**Why DAS ≥ 40 threshold?**
A score of 40 requires at minimum a hospital ≥ 300 beds within 1.5km + BTS within 800m. This represents the minimum structural demand needed to sustain 90%+ occupancy in a market with 24.8% macro vacancy. Below this, the property is competing on price alone — which is not a defensible position for a 3–7 year hold.

---

## 9. Data Gaps & Limitations

| Gap | Impact | Workaround |
|---|---|---|
| No rental transaction data (only listed prices) | GRY overstated if not discounted | Apply 85% haircut; verify with agent |
| No building-level occupancy data in DB | Cannot compute actual vacancy for specific building | Use NPA concentration + listing age as proxy |
| DOMP not stored in DB | Can't reliably compute days-on-market | Use listing_updated vs listing_created delta |
| No enrollment data in DB | DAS school scoring requires manual lookup | Store in KB after each analysis |
| Supply pipeline not scraped | RSP metric is manual | Manual check on DDProperty new projects |

---

*Sources: GlobalPropertyGuide Q3 2025, BambooRoutes 2026, BangkokResidential 2025, CondoDee 2025, Asia Lifestyle Magazine 2025, Agent-Condo 2025, Cushman & Wakefield Thailand MarketBeat, ForbesAndPartners 2025 rental tax guide, CondoDee CAM fees guide 2025*

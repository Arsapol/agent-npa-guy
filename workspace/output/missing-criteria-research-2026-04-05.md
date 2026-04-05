# Missing Criteria Research — Synthesis Report

**Date:** 2026-04-05 | **Sources:** 4 parallel research agents

## Executive Summary

Our current NPA screening framework has **significant blind spots** that explain why all 5 BUY candidates showed WEAK/DEAD demand signals. The core issue: **we screen properties but not the market environment.** In the current mid-fall cycle, even "good" NPA properties carry structural risks that our framework doesn't capture.

---

## TIER 1: Critical Missing Criteria (Must Add)

### 1. Market Cycle Adjustment — Raise All Discount Thresholds +5%

- **Current:** Tier A: 15%, Tier B: 20%, Tier C: 25%
- **Proposed:** Tier A: 20%, Tier B: 25%, Tier C: 30%
- **Why:** BKK is mid-fall (not bottom). 60-month sell-out period. -3% to -5% YoY declines. 40-70% mortgage rejection. 220,000 unsold units. No bottom signals have triggered.
- **Source:** Market cycle researcher, institutional frameworks researcher (independently confirmed)

### 2. Rent Haircut — Apply 10-15% to Listed Rents Before Yield Calc

- **Current:** Use Hipflat/PropertyHub median rent directly
- **Proposed:** Apply 10% haircut (conservative) or 15% (student areas in off-season)
- **Why:** 24.8% Bangkok condo vacancy. Listed rents are ASKING prices, not transaction rents. Landlords negotiate 10-15% below headline after concessions (free months, furniture).
- **Impact on our candidates:**
  - ไรส์ พระราม 9: yield drops from 7.1% to ~6.0% (fails university 7% threshold)
  - เวลาดี: yield drops from 6.6% to ~5.6%
  - เดอะไลน์: yield drops from 4.6% to ~3.9% (already failing)

### 3. Months of Supply Gate (Absorption Rate)

- **Current:** Not measured
- **Proposed:** If area sell-out period > 36 months, require 35%+ discount. If > 60 months, AVOID.
- **Why:** Bangkok average is 57-60 months. 12 zones need 5+ years to clear. This is the single best predictor of exit difficulty.
- **Data source:** Can compute from Hipflat/PropertyHub listings vs. transaction data

### 4. Bank Financing Availability on Building

- **Current:** Not checked
- **Proposed:** Gate check — if Thai banks won't lend on this building, auto-reject
- **Why:** 40-70% mortgage rejection rate. Banks have informal blacklists of high-NPA-concentration buildings. Cash-only buyer pool is tiny. A building where banks refuse to lend is effectively illiquid regardless of discount.
- **How to check:** Call 2-3 banks with building name + unit size before bidding

### 5. NPA Vintage (Time in NPA Status)

- **Current:** Not tracked
- **Proposed:** 
  - 0-12 months: Bank not motivated yet, may pull from market
  - 12-36 months: Sweet spot — motivated seller, legal clarity
  - 36+ months: Require 40%+ discount + full legal audit (stale = hidden problems)
- **Data source:** `first_seen_at` in our scraper tables

---

## TIER 2: Important Missing Criteria (Should Add)

### 6. LED Auction Round Number as Distress Signal

- **Current:** Tracked in DB but not used in scoring
- **Proposed:** Round 4-5 = yellow flag (manual review). Round 6+ at 70% floor = auto-reject unless independent valuation confirms
- **Why:** Multiple failed rounds = structural problem (occupant, legal dispute, building defect), not just pricing

### 7. Sinking Fund Depletion Risk

- **Current:** Check juristic fund ≥ 70% collection rate
- **Proposed:** Also check absolute sinking fund balance vs. building age. Buildings 2008-2015 may have depleted sinking funds needing 15-50K/unit special assessments.
- **Why:** Direct yield impact. In high-NPA buildings, non-defaulting owners bear larger share.

### 8. Occupancy Risk by NPA Source

- **Current:** Treat all NPA sources equally
- **Proposed:** LED court auctions = HIGH occupancy risk (cannot inspect, previous owner may still be inside). Bank NPA (BAM/SAM/JAM) = LOWER risk (typically vacant before listing). Add source-specific risk multiplier.
- **Why:** Eviction takes 3-18 months + 200K THB legal. During this time: zero rent, ongoing CAM fees.

### 9. Inner vs. Outer Corridor Quality

- **Current:** BTS tier uses distance only (800m/1500m)
- **Proposed:** Add corridor quality sub-score. Inner Sukhumvit (Nana-Phrom Phong) ≠ Outer Sukhumvit (Udom Suk-Kheha) despite same BTS distance. Downtown absorption 93% vs outer ring struggling.
- **Why:** 86% of new supply is suburban. Outer ring has permanent supply overhang.

### 10. RENT-Only Strategy Gate

- **Current:** Framework is ambiguous (computes yield but doesn't force strategy)
- **Proposed:** In current cycle, ALL NPA purchases must be scored as RENT plays. Flip exit requires 36+ month hold minimum. Add holding period assumption to all-in cost.
- **Why:** 57-month sell-out period. No cap rate compression expected. Returns must be income-driven.

---

## TIER 3: Nice-to-Have Improvements

### 11. Seasonal Demand Gate for Universities

- Block yield calculation for university-anchor properties outside Aug-Oct, or apply 15% seasonal haircut
- Students lease in August-October (73% of annual volume)

### 12. Stale Listing Ratio (Automatable)

- Flag buildings where >40% of DDProperty/Hipflat rental listings are >30 days old
- Indicates weak absorption vs. paper availability

### 13. Renovation as Mandatory Cost (Not Contingency)

- Apply minimum 5% renovation cost to ALL NPA yield calculations
- Section 473 of Thai Civil Code: no defect recourse on NPA purchases

### 14. Exit Cap Rate Stress Test

- Model exit at +150 bps above going-in cap rate
- Must still show positive return on 5-year hold

### 15. Portfolio Concentration Warning

- Flag if buying 2+ NPAs in same building/district/vintage
- Correlated risk: same juristic fund, same buyer pool, same maintenance trajectory

### 16. Add RentHub.in.th to Market-Checker

- Better student rental demand signal than DDProperty for university areas

---

## Impact on Current Candidates

Applying the critical missing criteria to our 5 BUY candidates:


| Property      | Current                 | After Rent Haircut   | After Cycle Adj            | After Absorption     | New Verdict |
| ------------- | ----------------------- | -------------------- | -------------------------- | -------------------- | ----------- |
| ไรส์ พระราม 9 | BUY (7.1%, 28.6% disc)  | 6.0% yield (FAIL 7%) | Need 25% disc (PASS)       | 60mo sell-out (FLAG) | **WATCH**   |
| เวลาดี        | BUY (6.6%, 30.4% disc)  | 5.6% yield (FAIL)    | Need 25% disc (PASS)       | Unknown absorption   | **WATCH**   |
| อีควิน็อคซ์   | BUY (16.4%, 31.5% disc) | Yield suspicious     | NPA hotspot (457)          | —                    | **AVOID**   |
| เดอะไลน์      | BUY (9.3%, 17.9% disc)  | 7.9% yield           | Need 25% disc (FAIL 17.9%) | 60mo sell-out        | **AVOID**   |
| เออร์บานา     | BUY (21.7%, 27.8% disc) | Yield suspicious     | 33% supply pressure        | 20yr building        | **AVOID**   |


**Net effect:** No candidates survive the enhanced framework. This suggests either:

1. The current NPA market genuinely has no good deals (possible — mid-fall cycle)
2. We need to wait for the H2 2026 LTV expiry wave for better pricing
3. We should shift focus to specific micro-markets where Tier A locations show 93% clearance

---

## Bottom Timing Signals — When to Re-Screen


| Signal             | Current            | Trigger for "Buy"                      |
| ------------------ | ------------------ | -------------------------------------- |
| Absorption rate    | 1.6%/mo            | Need 2.5%+ for 3 consecutive quarters  |
| Sell-out period    | 60 months          | Need < 36 months                       |
| Mortgage rejection | 40-70%             | Need sustained < 30%                   |
| Transfer volume    | -13% YoY           | Need 3+ months positive YoY            |
| Household debt/GDP | 86.7%              | Need < 80%                             |
| NPA formation      | Peak passed (2024) | Wait for pipeline to clear (2027-2028) |


**Recommended re-screening window: H2 2026 (after LTV expiry) or Q1 2027.**

---

## Recommended Framework Changes (Priority Order)

1. Apply 10% rent haircut to all yield calculations
2. Raise discount thresholds +5% for current cycle
3. Add bank financing check as hard gate
4. Add NPA vintage scoring (use first_seen_at)
5. Add LED auction round penalty
6. Distinguish inner vs. outer BTS corridors
7. Force RENT-only strategy declaration
8. Add sinking fund adequacy to due diligence
9. Add stale listing ratio check
10. Add seasonal adjustment for university anchors


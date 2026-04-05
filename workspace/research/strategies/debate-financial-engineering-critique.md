# Financial Engineering Critique — Cross-Strategy Debate
**Author:** Financial Engineering Researcher  
**Date:** 2026-04-05  
**Target audience:** All strategy researchers + team lead  
**Purpose:** Reality-check whether the numbers actually work after financing costs and taxes

---

## Framing: Why This Critique Exists

Every strategy report correctly identifies good properties. None of them fully close the loop on post-financing, post-tax returns. The gap between "gross yield" and "what you actually earn on the cash you deployed" can be 2-5x. A 5% gross yield rental with 70% LTV becomes 16.7% CoCR — or it becomes -3% if you miscalculate. This critique forces each strategy to answer the right question: **what does the levered, after-tax IRR look like?**

---

## 1. RENTAL STRATEGY — Where the Math Works and Where It Breaks

### What the researcher got right
- 85% transaction haircut on listed rents is correct and important
- Separate vacancy budgets per tenant type is smart
- GNHC > 50% = reject is a sound rule

### What is missing or wrong

**Problem 1: No CoCR calculation anywhere.**  
The entire report analyzes unlevered returns (NRY). This is incomplete for any investor using a mortgage. The researcher's own Tier B example shows NRY of 2.72–3.08% on cash purchase. But run that through leverage:

```
Purchase: 880,000 THB
LTV 70% → loan: 616,000 THB, down payment: 264,000 THB
Mortgage (3.1% fixed 3yr, 30yr term): ~2,621 THB/mo = 31,452 THB/yr
Net annual income (after operating costs, before debt service): ~23,942 THB
Cash flow after debt service: 23,942 - 31,452 = -7,510 THB (NEGATIVE)

CoCR = -7,510 / (264,000 + 17,600 closing) = -2.7%
```

**The leveraged version of the researcher's own example is a loss-making investment at 880K purchase price.** A rental property that achieves 3% NRY on an unlevered basis cannot be financed — the mortgage payment exceeds income. This is critical: for properties under ~1.5M THB, mortgage financing is mathematically impossible at typical CAM/management cost structures. The screening must reject leveraged rental buys unless NRY > ~5%.

**DSCR rule for rental strategy:** NRY / mortgage_rate must be > 1.25 to absorb debt. At 3.1% mortgage on 70% LTV:
- Required NRY ≥ 3.1% × 0.7 × 1.25 = 2.71% (barely viable, zero margin)
- Practical minimum NRY for leveraged rental: **4.5%** (provides DSCR ~1.5)

**Revised GRY minimums after leverage:**
| Tier | Researcher min GRY | Required GRY for 4.5% NRY | Gap |
|------|--------------------|--------------------------|-----|
| Uni Tier A | 6% | ~8% (assumes 25-30% haircut to net) | +2% |
| Uni Tier B | 7% | ~9% | +2% |
| Thai school | 5.5% | ~7.5% | +2% |

The researcher's thresholds are correct for CASH purchases only. For levered purchases, add 2% to every GRY minimum.

**Problem 2: Income tax on rental income is understated.**  
The report uses 10% of gross as a "conservative estimate." For investors with other income (salary, business), marginal rate on rental income can be 20-25%. The 10% assumption underestimates holding costs by ~5-10% of gross rent for most active investors. Use 15% of gross as the conservative pipeline assumption, not 10%.

**Problem 3: The example never models the exit.**  
The rental strategy targets a 3-7 year hold and exit at "cycle recovery." There is no IRR calculation, no exit tax modeling. A 3-year hold means SBT at 3.3% on exit — this is ~2.8% of sale price extra cost vs. holding 5+ years. For a 5-year hold underwriting, that's the difference between an 8% and 10% IRR.

**Recommendation for rental researcher:** Add CoCR and DSCR as required metrics before NRY. Revise GRY thresholds to have a "leveraged" and "cash" column. Add exit tax sensitivity to scoring.

---

## 2. FLIP STRATEGY — Mostly Sound but One Dangerous Assumption

### What the researcher got right
- SBT 3.3% correctly modeled as a hard cost
- Holding cost calculator is solid
- Quick Flip scenario A (June 2026 deadline) is sharp — good timing insight
- Buyer pool depth analysis with <3M THB mortgage rejection is excellent
- 10% minimum net margin after all costs is conservative and correct

### What is missing or wrong

**Problem 1: The benchmark is wrong.**  
The flip strategy is implicitly benchmarked against "better than cash purchase." It needs to be benchmarked against opportunity cost:

- Thai REITs yield 5-7% with daily liquidity
- SET index: ~10% total return historically
- Thai bonds: 3%

A flip strategy that produces 15% net margin over 12 months = 15% annualized return. That beats all benchmarks. But a flip producing 15% over 24 months = 7.2% annualized — barely above REIT yield, with much more execution risk and zero liquidity. **The researcher's "medium hold flip" minimum of 10% annualized return is too low.** After accounting for illiquidity risk (no exit for 1-3 years), the minimum should be SET index return + 5% = 15% annualized for the illiquidity premium to be justified.

**Revised minimum annualized returns:**
| Sub-strategy | Researcher min | Adjusted minimum | Rationale |
|---|---|---|---|
| Quick Flip (6-12mo) | 18% p.a. | 20% p.a. | Illiquidity + execution risk |
| Medium Hold (1-3yr) | 10% p.a. | 15% p.a. | Must beat SET + illiquidity premium |
| Reno Flip | 12% p.a. | 18% p.a. | Reno risk + illiquidity |

**Problem 2: Renovation flip ignores financing the renovation.**  
A cosmetic renovation of 35 sqm at 8,000 THB/sqm = 280,000 THB. Full standard reno at 20,000 THB/sqm = 700,000 THB. The report assumes this is cash from pocket. But:
- If the investor doesn't have the cash, renovation must wait for home improvement loan approval (1-2 months) or mortgage top-up (requires 12 months of payments)
- Renovation financing at 6-7% adds to effective IRR hurdle
- The financing cost of renovation is not modeled in the Reno ROI formula

**Problem 3: Scenario A (Quick Flip by June 2026) has a timing problem.**  
The researcher correctly identifies the 0.01% transfer fee window expiring June 2026. However:
- LED/SAM/BAM acquisition timeline: 30-90 days from winning bid to title transfer
- If you're reading this in April 2026, you have ≈60 days to complete acquisition AND find a buyer AND complete their transfer
- Practically: quick flip window is **already closed** for LED/SAM properties (auction → transfer → relist → find buyer = 90+ days minimum)
- Only BAM/JAM/KBank direct purchase (no auction delay) can still make the June deadline

Flag this as an execution timing risk in the screener.

**Problem 4: Withholding tax on flip is not fully modeled.**  
The report says "~2% WHT" for quick flip. The actual WHT table is complex — it depends on appraised value, years of ownership, and income bracket. For a 12-month hold on a 3M THB property with high appraised value, WHT can be 3-5% of appraised value, not 2%. Use the formula:
```
WHT_income = appraised_value × years_held_factor - deduction_per_year × years_held
Actual WHT varies from 1% to 8% of appraised value
Budget 3% as conservative pipeline estimate, not 2%
```

---

## 3. LAND BANKING — The Most Financially Disciplined Report, One Blind Spot

### What the researcher got right
- HCB calculation with escalating vacant land tax is accurate and important
- Infrastructure status classification (CONFIRMED vs RUMORED multiplier) is the best methodological contribution across all four reports
- Hard reject for IRR < break-even appreciation is sound
- Agricultural registration tax trick (0.15% vs 0.30%) is a real optimization worth implementing

### What is missing or wrong

**Problem 1: IRR targets are too wide and unanchored to cost of capital.**  
The exit strategy framework lists "15-25% IRR" for transit opening premium, "25-40% IRR" for developer sale. These are target ranges, not minimum thresholds. For a 7-year land banking hold at 1.4% annual HCB, the required total appreciation to cover holding costs is ~10% (1.4% × 7). That's a low hurdle — **it doesn't account for opportunity cost**.

The correct minimum IRR for land banking:
```
Required IRR = (1 + benchmark_return)^hold_years × (1 + HCB/yr)^hold_years - 1
= (1.07)^5 × (1.014)^5 - 1 = 1.403 × 1.072 = 1.504 → 50.4% total, = 8.5% IRR

Minimum land banking IRR = 8.5% for 5yr hold
(assumes 7% SET benchmark + 1.4% HCB cost)
```

A flat land appreciation of 35% over 5 years = 6.2% IRR. **That's below the minimum.** The researcher's "target 35% over hold period" is not enough to beat opportunity cost on a 5-year hold. Require minimum 50% total appreciation (8.5% IRR) over 5 years.

**Problem 2: The HCB model uses 1% opportunity cost (BoT rate) which is too conservative.**  
BoT policy rate is 1.00% — but that's the interbank lending rate, not the opportunity cost of equity capital. Money tied up in land could be in SET index (7-10%) or Thai REITs (6-7%). Using 1% opportunity cost drastically understates the true holding cost.

**Revised HCB with realistic opportunity cost:**
```python
# Researcher's formula:
Annual_HCB_researcher = Land_Tax + (Purchase_Price × 0.01) + Maintenance
# For 1M THB: 3,000 + 10,000 + 1,000 = 14,000 THB/yr = 1.4%

# Corrected formula (equity opportunity cost at 7%):
Annual_HCB_corrected = Land_Tax + (Purchase_Price × 0.07) + Maintenance
# For 1M THB: 3,000 + 70,000 + 1,000 = 74,000 THB/yr = 7.4%
```

The true annual holding cost burden is **7.4%, not 1.4%**. At 7.4% annual cost, a 7-year hold requires 67% total appreciation just to break even. This changes the viability threshold significantly: only EEC-tier appreciation corridors (100%+ YoY) are viable for long holds.

**Recommendation:** The HCB metric should use max(BoT_rate, benchmark_equity_return) as opportunity cost, not BoT rate alone. This makes land banking appear correctly risky relative to alternatives.

**Problem 3: Exit liquidity is mentioned but not scored.**  
Outer Bangkok and EEC land can take 12-24 months to find a buyer. A 7-year hold that requires 18 months to exit is effectively an 8.5-year hold — this meaningfully reduces IRR (a 20% appreciation spread over 8.5 vs 7 years = 2.1% vs 2.7% annualized gain, meaningful difference). Add a liquidity score penalty of -0.5% IRR per expected 6 months of exit time.

---

## 4. RENOVATION/HOSPITALITY — Good Metrics, Financial Model Has Holes

### What the researcher got right
- Legal compliance score as 25-30% of total weight is correct — legal risk is a portfolio killer
- Co-living revenue model (2BR → 4 rooms = 50% lift) is well-structured
- RCR threshold (> 0.70 = marginal, > 1.0 = reject) is the right framework

### What is missing or wrong

**Problem 1: The net RROI formula uses a flat 37.5% deduction that hides the real number.**  
The researcher calculates:
```
Net_RROI = RROI × (1 - 0.375)
```
But the 37.5% operating cost deduction doesn't include:
- Income tax on STR revenue (personal: 15-35% effective, or hotel business license: 20% CIT)
- Property tax at rental rate (0.2% of appraised value for rented residential, not 0.02%)
- SBT on eventual exit (3.3% if < 5 years — and STR operators typically flip or reposition after 2-3 years)
- Interest cost if financed (3.1-6% on the renovation loan)

Full cost stack for STR:
```
Gross STR revenue:           100%
Platform fee (3%):           -3%
Management fee (20%):        -20%
Cleaning/turnover (est 5%):  -5%
Utilities (est 5%):          -5%
Property tax (0.2%):         -variable
Income tax (15% effective):  -15%
NET:                         ~47% of gross
(vs researcher's 62.5%)
```

The researcher's net RROI will be overstated by ~30% relative to reality.

**Recalculated example:**
```
STR gross monthly (30 sqm, Bangkok median): 35,900 THB
Net at 47%: 16,873 THB/mo
LT rent baseline: 14,000 THB/mo
Rent premium: 2,873 THB/mo
Reno cost: 540,000 THB
Payback: 540,000 / 2,873 = 188 months (15.6 years)
Net RROI: 6.4%
```

At 6.4% net RROI, **the standard Bangkok STR renovation does not clear the 10% threshold the researcher set**. The math only works in:
- High-ADR areas (Sukhumvit/Riverside with ≥ ฿2,200/night ADR)
- High-occupancy operations (OCC > 75%, top-quartile operators)
- Lower renovation cost (cosmetic only: ฿3,000-5,000/sqm vs ฿18,000)

**The "median Bangkok STR" case does not produce a viable return after full costs.** Only the top quartile works.

**Problem 2: No CoCR or DSCR model for the financed case.**  
A serviced apartment purchased at 1.5M THB with 70% LTV:
```
Loan: 1,050,000 THB
Monthly mortgage (~3.1%, 30yr): ~4,472 THB/mo
Annual debt service: 53,664 THB
Annual STR net income: 16,873 × 12 = 202,476 THB
Net cash flow: 202,476 - 53,664 = 148,812 THB
CoCR = 148,812 / (450,000 down + 30,000 closing + 540,000 reno) = 14.5%
```

At 1.5M NPA purchase price with full renovation, the serviced apartment actually produces acceptable CoCR (14.5%). But the researcher doesn't show this — they only show unlevered RROI. The financing analysis dramatically changes the picture for higher-priced properties.

**Problem 3: No holding period IRR model.**  
Hospitality is the strategy with the longest capital recovery period (renovation + ramp-up = 6-12 months before stabilized income). Without IRR modeling, you can't compare this against rental strategy or flip strategy. The composite score is internally coherent but not cross-strategy comparable.

---

## 5. THE BENCHMARK PROBLEM — All Four Reports

**This is the most important critique.**

Every strategy researcher implicitly benchmarks against "better than doing nothing" or "better than a bank deposit." None of them explicitly compare to:

| Benchmark | Return | Liquidity |
|-----------|--------|-----------|
| Thai government bond (10yr) | 3.0% | High |
| Thai REITs (avg yield 2025) | 6-7% | Medium-High |
| SET index (total return, historical avg) | 8-10% | High |
| S&P 500 in USD (via TFEX/ETF) | 9-11% | High |

**The correct illiquidity premium for NPA property:**  
NPA real estate is illiquid (6-24 months to exit), requires active management, has legal risks, and has execution risk. The required return premium over liquid alternatives should be:
- vs Thai REITs: minimum +3-5% (they do property for you, professionally)
- vs SET index: minimum +3-5% (for concentrated single-asset risk)

**Implied minimum IRR for any NPA strategy:**  
```
SET return 10% + concentration risk 3% + illiquidity premium 3% = 16% minimum IRR
```

Against this standard:
- Rental (levered, 5yr hold, Tier A): 12-14% IRR — **FAILS**
- Flip (quick, Tier A): 20-30% IRR — **PASSES**
- Flip (medium hold, recovery thesis): 10-15% IRR — **BORDERLINE/FAILS**
- Land banking (EEC corridor): 20-30% IRR — **PASSES (high-quality corridors only)**
- Land banking (transit, standard): 10-12% IRR — **FAILS against benchmark**
- Renovation/hospitality (top quartile): 15-20% IRR — **BORDERLINE**

**Implication:** Rental strategy only beats the benchmark if:
1. NPA entry discount is ≥ 35% (not 20%)
2. BTS Tier A location (for exit premium)
3. LTV kept at ≤ 60% to avoid negative carry risk
4. Hold period ≥ 5 years (to get stamp duty not SBT at exit)
5. Monthly rent ≥ ฿8,500 for 28-35 sqm units (not the 6,375 in the researcher's example)

The screener should display IRR vs. benchmark clearly, not just a property score. A property scoring 75/100 on the rental matrix with a 9% IRR should still be flagged as **"below opportunity cost threshold"**.

---

## 6. SBT Timing: How It Differs Per Strategy

The flip researcher correctly models SBT. The rental researcher mentions it in BEHP but doesn't build it into the yield model. The land banking researcher ignores it (relevant only at exit). The hospitality researcher ignores it. Here is the unified treatment:

| Strategy | Typical hold | SBT applies? | Impact |
|---|---|---|---|
| Quick Flip | 6-12 months | YES — 3.3% | Hard cost, bake into M8 net margin |
| Medium Hold Flip | 1-3 years | YES — 3.3% | Hard cost |
| Rental (target 3-5yr) | 3-5 years | YES — 3.3% | Saveable: target ≥5yr or use tabien baan |
| Rental (5yr+) | 5-7 years | NO — 0.5% | Save 2.8% of sale price |
| Land banking | 5-8 years | NO — 0.5% | Plan for 5yr+ to save 2.8% |
| Reno/hospitality | 2-4 years | YES — 3.3% | Significant — add to cost model |
| Company-held (any) | Any | ALWAYS YES — 3.3% | Personal > company for ≥5yr hold |

**The 5-year tabien baan exemption** (registering your name in the house registration book for ≥1 year) is available only to owner-occupied properties. It applies to the rental strategy only if the investor actually lives there for a year first — valid for primary residence plays but not investment. STR/hospitality strategy cannot use this exemption.

---

## 7. Proposed Unified Financial Scoring Layer

To integrate across all strategies, I propose these 5 metrics become mandatory gates in the screener for every property regardless of strategy:

### Gate 1: Opportunity Cost Check
```python
if irr < 0.16:  # 16% = SET + concentration + illiquidity
    flag = "BELOW_OPPORTUNITY_COST"
    # Still show property, but display red warning
```

### Gate 2: CoCR Viability Check (leveraged deals only)
```python
if ltv > 0 and cocr < 0.05:
    reject_reason = "NEGATIVE_CARRY_RISK"
    # Leveraged purchase generates less income than debt service
```

### Gate 3: Exit Tax Budget
```python
exit_cost = sbt_if_under_5yr + transfer_fee + legal
if npa_discount_pct < exit_cost_pct + 0.10:
    reject_reason = "INSUFFICIENT_DISCOUNT_TO_COVER_EXIT_COSTS"
    # Minimum 10% margin above exit costs in the entry discount
```

### Gate 4: DSCR Floor (rental/hospitality only)
```python
if strategy in ("rental", "hospitality") and dscr < 1.25:
    reject_reason = "DSCR_BELOW_MINIMUM"
```

### Gate 5: Hold Cost Sensitivity to Rate Rise
```python
if sensitivity_at_plus_2pct["dscr"] < 1.0:
    flag = "RATE_RISK: underwater if rates rise 200bps"
```

These 5 gates run on every property before strategy-specific scoring begins. They are the financial engineering layer that sits above the four strategy scorecards.

---

## 8. Summary: Where Each Strategy Needs Work

| Issue | Rental | Flip | Land Bank | Reno/Hosp |
|---|---|---|---|---|
| Add CoCR/DSCR | CRITICAL | Optional (no rental income) | Optional (no income) | CRITICAL |
| Revise yield thresholds for leverage | CRITICAL | N/A | N/A | HIGH |
| Benchmark against SET/REIT | HIGH | HIGH | HIGH | HIGH |
| Full exit tax modeling | HIGH | Done | Medium | HIGH |
| Correct opportunity cost in HCB | N/A | N/A | CRITICAL | N/A |
| Revise net operating model | Medium | Low | Low | CRITICAL |
| Add IRR to composite score | HIGH | Done | Medium | HIGH |

**Bottom line:** The rental and renovation/hospitality strategies need the most revision. The flip strategy is the most financially complete but needs better benchmarking. The land banking strategy is methodologically strong but uses BoT rate as opportunity cost, which makes it look 5x more attractive than it actually is relative to liquid alternatives.

---

*Financial Engineering Researcher — strategy-research team*

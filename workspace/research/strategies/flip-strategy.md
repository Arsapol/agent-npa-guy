# Flip Strategy: Measurable, Automatable Metrics
**Research Date:** 2026-04-05
**Context:** Bangkok NPA market, mid-fall cycle, 60-month avg sell-out, Tier A 93% clearance

---

## Market Reality Check (Before Any Flip Metric)

The Bangkok condo market is in a confirmed declining phase:
- Overall price index -0.2% YoY, -0.5% QoQ as of Q3 2025
- 60-month national sell-out period; 12 zones require 5+ years
- Condo transfers -13.3% volume, -19.3% value YoY (9M 2025)
- Days on market: 180–240 days in 2025 (was 90–120 in 2021)
- Mortgage rejections: 40–70% for properties <3M THB; 80% at peak
- But Tier A (BTS+MRT <800m, downtown completed stock): 93% clearance rate

**Implication:** Flips in a down market require larger entry discounts to absorb: (a) price drift during hold, (b) exit costs, (c) liquidity time risk. The NPA entry discount is the primary buffer. A 30% NPA discount in Tier A is a different risk profile than 30% in Don Mueang.

---

## Sub-Strategy Definitions

| Sub-Strategy | Hold Period | Core Thesis |
|---|---|---|
| Quick Flip | 6–12 months | Deep discount + ready-to-move, cash buyer market, no market appreciation needed |
| Medium Hold Flip | 1–3 years | Ride cycle recovery; LTV expiry June 2026 creates 2nd dip → buy low, exit Q2–Q4 2027 |
| Renovation Flip | 6–18 months | Buy dated/vacant, add value via renovation, exit at market rate of renovated comparable |

---

## Metric 1: Entry Discount vs. Verified Market Price

**Formula:**
```
entry_discount_pct = (verified_market_price_per_sqm - npa_price_per_sqm) / verified_market_price_per_sqm * 100
```
Where `verified_market_price_per_sqm` = median of DDProperty + Hipflat listings for same project OR comparable projects within 500m, same building age ±3 years.

**Data Source:**
- NPA price: `bam_properties.asking_price / area_sqm`, `jam_properties.asking_price / area_sqm`, etc.
- Market price: `ddproperty_listings` + `hipflat_price_history` → median per sqm by project/subdistrict
- Join key: `npa_adapter` normalized view + GPS proximity

**Thresholds:**

| Sub-Strategy | Minimum | Good | Strong |
|---|---|---|---|
| Quick Flip | 35% | 40% | 45%+ |
| Medium Hold Flip | 25% | 30% | 35%+ |
| Renovation Flip | 30% (pre-reno) | 35% | 40%+ |

**Reject if:** NPA price ≥ market price (negative discount). Also reject if "discount" is vs. provider appraised value — always use DDProperty/Hipflat as benchmark.

**Weight:** 25% (highest weight — primary buffer for all flip types)

---

## Metric 2: Absorption Rate (Months of Supply in Micro-Market)

**Formula:**
```
absorption_rate = active_listings_count / (avg_monthly_transactions_last_6mo)
# Result: months of supply
```
Where micro-market = same subdistrict (แขวง) + building type + price band ±20%

**Data Source:**
- Active listings count: `ddproperty_listings WHERE status='active'` + `hipflat_projects` listing count by subdistrict
- Monthly transactions: `ddproperty_listings` date-based proxy (listings removed = assumed sold); or use `zmyhome_listings` sale events
- Fallback: Colliers/CBRE published absorption data by zone (index in KB)

**Market Benchmarks (2025–2026):**
- National average: 60 months of supply
- Tier A (BTS <800m, downtown): 30–34 months (Yannawa-Bang Kho Laem at 30 months = best in class)
- Tier B (BTS 800–1500m, midtown): 45–55 months
- Outer/no-BTS: 60–90+ months

**Thresholds:**

| Absorption (months supply) | Signal | Allowed Sub-Strategies |
|---|---|---|
| ≤ 30 months | Green — liquid zone | All 3 |
| 31–45 months | Yellow — proceed with caution | Medium Hold, Reno only |
| 46–60 months | Orange — slow zone | Reno Flip only if discount ≥40% |
| > 60 months | Red — no flip | REJECT all flip types |

**Weight:** 20%

---

## Metric 3: Price Momentum Score (3M / 6M / 12M)

**Formula:**
```
price_momentum_3m = (avg_price_per_sqm_current_quarter - avg_price_per_sqm_3mo_ago) / avg_price_per_sqm_3mo_ago * 100
price_momentum_12m = same for 12 months
momentum_score = weighted avg: (3m * 0.5) + (6m * 0.3) + (12m * 0.2)
```

**Data Source:**
- `hipflat_price_history` (per sqm, by project or subdistrict) — best time series
- `ddproperty_price_history` for cross-validation
- `zmyhome_price_history` as tertiary
- Aggregate by subdistrict if project-level data sparse (<5 data points)

**Thresholds:**

| Momentum Score | Signal | Notes |
|---|---|---|
| > +2% | Positive momentum | Supports quick flip |
| 0% to +2% | Flat/slightly positive | Medium hold viable |
| -2% to 0% | Mild decline | Renovation flip only (add value to overcome drift) |
| < -2% | Active decline | Requires extra 10% entry discount buffer |

**Special rule for Medium Hold Flip:** Negative momentum NOW is acceptable IF the thesis is cycle recovery by 2027. Log the momentum at acquisition and re-evaluate at 12-month mark.

**Weight:** 15%

---

## Metric 4: Listing Velocity (Days to Close Proxy)

**Formula:**
```
avg_days_on_market = avg(date_relisted_or_removed - date_listed) for comparable sold units
# Proxy if no sold date: use median listing age of SOLD/REMOVED listings in same zone
```

**Data Source:**
- `ddproperty_listings` — track `first_seen_date` vs `last_seen_date`; disappearance = proxy for sale/removal
- `hipflat_projects` price history change events as proxy for transactions
- Fallback: use zone-level estimates (Tier A: 60–90 days; Tier B: 120–180 days; Outer: 180–240+ days)

**Thresholds:**

| Avg Days on Market | Velocity | Impact on Strategy |
|---|---|---|
| < 90 days | Fast | Quick Flip viable |
| 90–150 days | Moderate | All strategies viable, budget extended holding costs |
| 150–210 days | Slow | Add 3-month buffer to holding cost calculation |
| > 210 days | Very slow | Quick Flip REJECT; others need 30%+ entry discount |

**Weight:** 10%

---

## Metric 5: Buyer Pool Depth (Cash vs. Mortgage Exposure)

**Formula:**
```
mortgage_exposure_score = (pct_listings_under_3m_thb) * 0.7 + (pct_listings_3m_to_7m_thb) * 0.4
# Score 0–1; higher = more mortgage-dependent buyer pool = higher exit risk
```

**Data Source:**
- `ddproperty_listings.price` distribution in subdistrict
- `bam_properties.asking_price` / `jam_properties.asking_price` for comparable NPA price range
- Market data: mortgage rejection rate 70% for <3M THB; 40–45% for 3–7M THB; lower above 7M

**Thresholds & Buyer Pool Segments:**

| Price Range | Mortgage Rejection | Buyer Profile | Flip Viability |
|---|---|---|---|
| < 3M THB | 70–80% | Mostly cash; limited buyer pool | Risky — small pool of cash buyers |
| 3–7M THB | 40–45% | Mixed; Thai nationals get 0.01% transfer fee | Moderate — fee incentive helps |
| > 7M THB | ~20–25% | Cash-heavy investors; foreign buyer pool | Better exit liquidity |

**Note:** Thai government fee reduction (0.01% transfer + mortgage) applies to Thai nationals, properties ≤7M THB, until June 2026. Properties in this range have a structural demand incentive through Q2 2026. Factor this into quick flip timing.

**Weight:** 10%

---

## Metric 6: Holding Cost Calculator

**Formula:**
```
monthly_holding_cost = (mortgage_payment_if_financed) + CAM_fee + annual_property_tax/12 + vacancy_opportunity_cost
total_holding_cost = monthly_holding_cost * hold_months + acquisition_costs
```

**Component Benchmarks (2025):**

| Cost Item | Rate | Notes |
|---|---|---|
| CAM fee | 35–80 THB/sqm/month | Varies by project; median ~50 THB/sqm/month |
| Annual property tax | 0.02%–0.1% of appraised value | Investor (non-owner-occupied) rate; 0.02% up to 50M appraised |
| Mortgage (if financed) | ~3.5–4.5% p.a. | Krungsri/KBank NPA loan programs; 70% LTV typical |
| Acquisition cost (buy side) | ~2–3% | Transfer fee (now 0.01% if eligible) + legal + due diligence |
| Exit cost (sell side) | SBT 3.3% (<5yr) or Stamp Duty 0.5% (≥5yr) + withholding tax | See Exit Tax Metric below |

**Example: 35 sqm condo, 2M THB NPA purchase, 6-month hold:**
```
CAM: 50 THB/sqm × 35sqm × 6mo = 10,500 THB
Property tax: 0.02% × 2M = 400 THB/yr → 200 THB for 6mo
Total holding: ~10,700 THB (~0.5% of purchase price)
Exit SBT: 3.3% × 2.5M sale price = 82,500 THB
Acquisition: ~2% × 2M = 40,000 THB
Total costs excl. mortgage: ~133,200 THB
Required appreciation to break even: ~133,200 / 2M = 6.7%
```

**Data Source:**
- `zmyhome_projects.cam_fee` (if scraped)
- `ddproperty_listings` — extract CAM from listing descriptions via regex
- Property tax: calculated from `kbank_properties.appraised_value` or SAM appraisal
- SBT: applied at sale

**Weight:** Informational input to net profit calculation — not a standalone score. Used in Metric 8.

---

## Metric 7: Exit Tax Optimization

**Formula:**
```
exit_tax_rate = IF hold < 5 years → SBT 3.3% of higher(sale price, cadastral value)
                ELSE → Stamp Duty 0.5%

withholding_tax = progressive rate on deemed income (year of sale)
# For individual sellers: assessed on cadastral value, minus deductions, divided by years held
# 5-year hold divides income over 5 years → lower bracket
```

**Key Thresholds:**

| Hold Period | Tax Regime | Effective Tax on Sale |
|---|---|---|
| < 1 year | SBT 3.3% + WHT (high bracket) | ~5–8% total |
| 1–2 years | SBT 3.3% + WHT (moderate) | ~4–6% total |
| 2–5 years | SBT 3.3% + WHT (lower with divisor) | ~4–5% total |
| 5+ years | Stamp Duty 0.5% + WHT (low) | ~1–3% total |

**Optimization Rules:**
1. **Quick Flip (6–12 mo):** Budget 3.3% SBT + ~2% WHT = 5.3% exit overhead. Need this in discount buffer.
2. **Medium Hold (1–3 yr):** Same SBT but WHT divisor lowers income tax. ~4.5–5% total.
3. **Renovation Flip crossing 5yr:** If renovation + stabilization pushes past 5 years, drop to 0.5% stamp duty. Worth planning if marginal.
4. **Inheritance exemption:** If seller inherited the NPA property (rare but possible in estate auctions), SBT may be exempt regardless of hold period.
5. **House registration book (Tabien Baan) exemption:** If you register in the unit for 1+ year, SBT exempt even if <5yr hold. Practical for small investors with 1 property.

**Data Source:** Static rules — no DB table. Encode as configuration in property-calc skill.

**Weight:** Informational — adjust net profit calculation.

---

## Metric 8: Net Flip Profit Score (Composite)

**Formula:**
```
gross_profit = exit_price - entry_price
net_profit = gross_profit - total_holding_cost - exit_taxes - acquisition_costs - renovation_costs

net_profit_margin = net_profit / entry_price * 100
annualized_return = (1 + net_profit_margin/100)^(12/hold_months) - 1
```

**Minimum Thresholds:**

| Sub-Strategy | Min Net Margin | Min Annualized Return |
|---|---|---|
| Quick Flip (6–12mo) | 15% | 18% p.a. |
| Medium Hold Flip (1–3yr) | 20% | 10% p.a. |
| Renovation Flip | 18% post-reno | 12% p.a. |

**Reject if:** Net margin < 10% after all costs — insufficient buffer for market drift and execution risk.

**Data Source:** All upstream metrics combined. Property-calc skill outputs this.

**Weight:** 20% (primary go/no-go gate)

---

## Metric 9: Renovation ROI (Renovation Flip Only)

**Formula:**
```
reno_cost = cost_per_sqm * unit_sqm  # see benchmarks below
post_reno_value = comparable_renovated_unit_price_per_sqm * unit_sqm
reno_value_uplift = post_reno_value - pre_reno_npa_price
reno_roi = (reno_value_uplift - reno_cost) / reno_cost * 100
```

**Renovation Cost Benchmarks (Bangkok 2025):**

| Scope | Cost/sqm | Notes |
|---|---|---|
| Cosmetic (paint, fixtures, flooring) | 5,000–8,000 THB/sqm | Best ROI; suitable for 2006–2015 era units |
| Standard renovation (kitchen, bathroom, full fit-out) | 15,000–20,000 THB/sqm | Typical NPA refresh |
| Premium fit-out | 25,000–35,000 THB/sqm | Only justified for >150,000 THB/sqm exit price |
| Full gut renovation | 35,000–45,000 THB/sqm | Rarely justified for flip; more suitable for rental conversion |

**Value Uplift Evidence:**
- Renovated units vs. unrenovated in same building: 10–20% premium (Condodee 2025)
- BTR (Buy to Renovate) strategy: entry at 75,000 THB/sqm + 15,000 reno = 90,000 effective cost; comparable RMI at 170,000 THB/sqm — 47% discount
- Kitchen + bathroom upgrades drive best resale premium per baht spent

**Thresholds:**

| Reno ROI | Signal |
|---|---|
| > 200% | Excellent (renovation adds 2x its cost in value) |
| 100–200% | Good |
| 50–100% | Marginal — reconsider scope |
| < 50% | Renovation not justified for flip strategy |

**Reject if:** `reno_cost > 15% of entry_price` AND `reno_roi < 100%` — renovation is destroying value, not adding it.

**Data Source:**
- Pre-reno comparable: `ddproperty_listings` with filter `renovation_status=original` (infer from listing description)
- Post-reno comparable: listings with keywords "renovated", "fully furnished", "new fit-out"
- Reno cost: use benchmarks above; validate with local contractor quotes if >2M THB renovation budget

**Weight:** 15% (Renovation Flip only; replace Metric 5 weight for this sub-strategy)

---

## Metric 10: Comparable Transaction Evidence (Deal Confidence Score)

**Formula:**
```
# Count of verifiable sold/transferred comparables in same subdistrict, last 6 months
# Comparable = same building type, size ±20%, price ±30%, <500m radius
comparable_count = COUNT(transactions where criteria met)
deal_confidence = LOG10(max(comparable_count, 1)) * 10  # scale 0–20+
```

**Data Source:**
- `ddproperty_listings` disappearance events (proxy for sales)
- `zmyhome_appraisals` (if appraisal data available — implies recent transaction)
- `hipflat_price_history` — price changes on sold units
- LED/SAM auction results — actual hammer prices (most reliable transaction data we have)
- KB: ingested REIC/Land Department reports on actual transfer volumes

**Thresholds:**

| Comparable Count (6mo) | Confidence | Notes |
|---|---|---|
| ≥ 10 | High — market is liquid | Reliable exit price estimate |
| 5–9 | Moderate | Widen price estimate range ±10% |
| 2–4 | Low — thin market | Quick flip not recommended; medium hold only |
| 0–1 | Very thin | REJECT all flip types — no exit evidence |

**Weight:** informational gate — required minimum of 2 comparables before any flip recommendation proceeds.

---

## Summary Scoring Matrix

| Metric | Weight | Quick Flip | Medium Hold | Reno Flip |
|---|---|---|---|---|
| M1: Entry Discount | 25% | ≥35% | ≥25% | ≥30% |
| M2: Absorption Rate | 20% | ≤30mo | ≤45mo | ≤60mo |
| M3: Price Momentum | 15% | ≥0% | ≥-2% | ≥-2% |
| M4: Listing Velocity | 10% | <90d | <180d | <210d |
| M5: Buyer Pool | 10% | >3M THB | any | any |
| M8: Net Profit Score | 20% | ≥15% margin | ≥20% margin | ≥18% margin |

**Gate checks (must pass before scoring):**
- Comparable count ≥ 2 (M10)
- Entry discount > 0% (M1) — NPA at or above market = auto-reject
- Absorption rate < 60 months for any flip (M2)
- Net profit margin ≥ 10% minimum after all costs (M8)

**Composite Score Calculation:**
```
flip_score = sum(metric_score * weight for each metric)
# Each metric_score: 0 = reject threshold, 0.5 = minimum pass, 1.0 = strong
```

| Composite Score | Recommendation |
|---|---|
| ≥ 0.75 | Strong Flip — proceed |
| 0.55–0.74 | Conditional Flip — proceed with noted risks |
| 0.40–0.54 | Marginal — model sensitivity, likely better as rental |
| < 0.40 | Do not flip |

---

## Viable Flip Scenarios in Current BKK Market (April 2026)

### Scenario A: Quick Flip — Tier A Condo, 3–7M THB
**Profile:** BAM/JAM/KBank unit on BTS line, 30–50 sqm, priced 90,000–130,000 THB/sqm NPA vs 150,000–180,000 market. 40%+ discount. Ready-to-move-in. Thai buyer eligible for 0.01% transfer fee through June 2026.
**Why it works:** Fee incentive creates a demand window until June 2026. 93% clearance in this segment. Cash buyer pool viable at 3–7M price point.
**Exit risk:** LTV relaxation expiry June 2026 may soften demand H2 2026.
**Target:** Buy by April 2026, exit before June 2026 fee expiry.

### Scenario B: Medium Hold Flip — BTS B-Tier, 2027 Recovery
**Profile:** NPA unit 800–1500m from BTS, 25–35% discount, current market -3% to -5% YoY. Buy at cycle bottom Q2 2026 (post-LTV expiry second dip), exit Q2–Q4 2027 as supply exhaustion in this tier drives price stabilization.
**Why it works:** Supply pause (new launches -54.5% YoY Q4 2025) means inventory absorption by 2027 in well-connected zones. 2–3 year hold crosses the supply/demand inflection.
**Risk:** Absorption slower than expected; holding costs and SBT still apply at 3yr.

### Scenario C: Renovation Flip — 2008–2015 Era Unit, 35–50 sqm
**Profile:** Dated but structurally sound condo, 2008–2015 build (sweet spot per screening framework), cosmetic renovation only (5,000–8,000 THB/sqm), in Onnut/Ekkamai/Ekkamai corridor. Buy at 30%+ discount, renovate to modern standard, exit at renovated-unit comparable price.
**Why it works:** Renovated vs. unrenovated premium 10–20%; cosmetic reno cost ~200,000 THB on 35 sqm; premium uplift ~500,000–800,000 THB.
**Risk:** Renovation cost overrun; need contractor access post-NPA acquisition (may face occupied unit issues).

---

## Implementation: DB Queries for Automation

### Absorption Rate (per subdistrict)
```sql
-- Proxy using listing age distribution in DDProperty
SELECT
  subdistrict,
  COUNT(*) FILTER (WHERE status = 'active') as active_listings,
  COUNT(*) FILTER (WHERE last_seen < NOW() - INTERVAL '30 days' AND first_seen < last_seen - INTERVAL '7 days') / 6.0 as est_monthly_sales,
  COUNT(*) FILTER (WHERE status = 'active') /
    NULLIF(COUNT(*) FILTER (WHERE last_seen < NOW() - INTERVAL '30 days' AND first_seen < last_seen - INTERVAL '7 days') / 6.0, 0) as months_supply
FROM ddproperty_listings
WHERE property_type = 'condo' AND province = 'กรุงเทพมหานคร'
GROUP BY subdistrict
HAVING COUNT(*) > 10
ORDER BY months_supply ASC;
```

### Price Momentum (per subdistrict, 3M vs 12M)
```sql
WITH recent AS (
  SELECT project_id, AVG(price_per_sqm) as avg_price_recent
  FROM hipflat_price_history
  WHERE recorded_at > NOW() - INTERVAL '90 days'
  GROUP BY project_id
),
older AS (
  SELECT project_id, AVG(price_per_sqm) as avg_price_older
  FROM hipflat_price_history
  WHERE recorded_at BETWEEN NOW() - INTERVAL '455 days' AND NOW() - INTERVAL '365 days'
  GROUP BY project_id
)
SELECT
  p.subdistrict,
  AVG((r.avg_price_recent - o.avg_price_older) / o.avg_price_older * 100) as momentum_12m_pct
FROM recent r
JOIN older o ON r.project_id = o.project_id
JOIN hipflat_projects p ON r.project_id = p.uuid
GROUP BY p.subdistrict
ORDER BY momentum_12m_pct DESC;
```

### NPA Entry Discount Calculator
```sql
-- For a given NPA property, find market comparables
WITH npa AS (
  SELECT asset_no, asking_price, area_sqm,
         asking_price / NULLIF(area_sqm, 0) as npa_price_per_sqm,
         lat, lon
  FROM bam_properties
  WHERE asset_no = :asset_no
),
market_comps AS (
  SELECT
    d.id, d.price_per_sqm,
    ST_Distance(ST_Point(d.lon, d.lat), ST_Point(n.lon, n.lat)) as dist_m
  FROM ddproperty_listings d, npa n
  WHERE ST_DWithin(ST_Point(d.lon, d.lat)::geography, ST_Point(n.lon, n.lat)::geography, 500)
    AND d.property_type = 'condo'
    AND d.status = 'active'
)
SELECT
  n.asset_no,
  n.npa_price_per_sqm,
  PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY m.price_per_sqm) as market_median_per_sqm,
  (1 - n.npa_price_per_sqm / PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY m.price_per_sqm)) * 100 as entry_discount_pct,
  COUNT(m.id) as comparable_count
FROM npa n, market_comps m
GROUP BY n.asset_no, n.npa_price_per_sqm;
```

---

## Data Gaps & Limitations

1. **No actual sold prices in DB** — DDProperty/Hipflat show asking prices only. Listing disappearance is a proxy, not confirmation of sale. Real Land Department transfer data (REIC) is not scraped. Impact: exit price estimates have ±10–15% uncertainty. Mitigation: use 10th percentile of listings as conservative exit price.

2. **Renovation status not tagged** — DDProperty descriptions mention "renovated" but not structured. Needs NLP extraction or manual tagging. Impact: pre/post-reno price premium hard to isolate from noise.

3. **Mortgage rejection by unit size** — Rejection rate data is at property value level, not unit-level detail. 70% applies to <3M THB but we don't have per-subdistrict breakdowns. Impact: buyer pool depth is an approximation.

4. **CAM fee** — Only ZMyHome sometimes publishes CAM fees. Most DB records lack this field. Impact: holding cost calculations use benchmark estimates (50 THB/sqm/month) rather than actual project fees.

5. **Occupied NPA units** — Renovation Flip assumes vacant. If unit is occupied post-auction, renovation timeline extends by 6–18 months (eviction process). Not tracked in DB. Mitigation: cross-reference SAM/BAM "occupancy status" fields where available.

---

## Sources

- [Colliers Bangkok Condominium Market Q3 2025](https://www.colliers.com/en-th/research/bangkok-condominium-market-q3)
- [Colliers Bangkok Condominium Market Q4 2025](https://www.colliers.com/en-th/research/q4-condominium-report-2025)
- [Bangkok Condo Oversupply: Insights for Investors 2025 — Asia Lifestyle Magazine](https://www.asialifestylemagazine.com/bangkok-condo-oversupply-market-2025/)
- [Thailand Residential Property Market Analysis 2026 — Global Property Guide](https://www.globalpropertyguide.com/asia/thailand/price-history)
- [Bangkok Condo Renovation Guide 2025 — CondoDee](https://condodee.com/bangkok-condo-renovation-guide-2025/)
- [Thailand Property Transfer Fees & Tax Guide 2025/2026 — Forbes & Partners](https://www.forbesandpartners.com/thailand-property-transfer-cost-tax-breakdown/)
- [Thailand Condominium Tax Guide 2025 — Frank Legal & Tax](https://franklegaltax.com/thailand-condominium-tax-guide-2025/)
- [Mortgage Rejection Rates Expected to Remain High — Bangkok Post](https://property.bangkokpost.com/financing-and-advice/2999699/mortgage-rejection-rates-expected-to-remain-high)
- [Homes Under 3M Baht Slump as Banks Reject 40% of Loans — Nation Thailand](https://www.nationthailand.com/blogs/business/property/40060924)
- [2025 Reduced Transfer and Mortgage Fees — Nishimura & Asahi](https://www.nishimura.com/en/knowledge/publications/20250421-112251)
- [Bangkok Condo Bargains: Top Districts for 2025 Resale Value — Agent Condo](https://www.agent-condo.com/news/bangkok-condo-resale-value)
- [Bangkok Condo Market: What 2025 Data Reveals — Agent Condo](https://agent-condo.com/news/bangkok-condo-market-2025-price-trends)
- [Buy to Renovate vs Ready to Move In — CondoDee](https://condodee.com/buy-renovate-vs-ready-move-in-bangkok/)
- [Thailand Property Market Faces Mortgage Rejection Crisis — Nation Thailand](https://www.nationthailand.com/business/property/40059623)
- [CBRE Bangkok Overall Figures Q3 2025](https://www.cbre.co.th/insights/figures/bangkok-overall-figures-q3-2025)

# NPA Screener v2 — Multi-Strategy Report

## Summary

- **Properties screened:** 32140
- **Pre-filter:** 1389 passed / 30751 failed

### Verdict Distribution by Strategy


| Strategy | STRONG_BUY | BUY | WATCH | AVOID |
| -------- | ---------- | --- | ----- | ----- |
| flip     | 68         | 80  | 65    | 26781 |
| rent     | 25         | 69  | 15    | 26885 |


### Properties by Provider

- **BAM**: 6695
- **JAM**: 17356
- **KBANK**: 3131
- **KTB**: 434
- **LED**: 2684
- **SAM**: 1840

### Investor Profile

- Mode: MORTGAGE
- LTV: 70%
- Mortgage rate: 3.0%
- Hold horizon: 5 years
- Entity: personal
- Tabien baan: No
- Reno budget: 0%
- Strategies: rent, flip
- Risk tolerance: moderate

## Top 10 Properties


| #   | Best Strategy | Score | Source | Project                        | Location                   | Price | Discount | Yield | BTS Tier | Dual? | IRR vs 16%     |
| --- | ------------- | ----- | ------ | ------------------------------ | -------------------------- | ----- | -------- | ----- | -------- | ----- | -------------- |
| 1   | rent          | 93.0  | KBANK  | แอท ซิตี้ สุขุมวิท             | เขตพระโขนง, กรุงเทพมหานคร  | 1.50M | 18.5%    | —     | A        | No    | -15.9pp vs 16% |
| 2   | rent          | 91.5  | KBANK  | ไรส์ พระราม 9                  | เขตห้วยขวาง, กรุงเทพมหานคร | 2.02M | 23.2%    | —     | A        | No    | -14.6pp vs 16% |
| 3   | flip          | 90.9  | JAM    | เดอะวอเตอร์ฟอร์ด รอยัลสูท      | เขตจตุจักร, กรุงเทพมหานคร  | 1.70M | 46.5%    | —     | C        | No    | -15.9pp vs 16% |
| 4   | flip          | 90.9  | KBANK  | เดอะวอเตอร์ฟอร์ด รอยัลสูท      | เขตจตุจักร, กรุงเทพมหานคร  | 1.70M | 46.5%    | —     | C        | No    | -15.9pp vs 16% |
| 5   | flip          | 90.2  | BAM    | ห้องชุดพักอาศัย โครงการโชคชัยป | ลาดพร้าว, กรุงเทพมหานคร    | 431K  | 80.5%    | —     | C        | Yes   | -15.4pp vs 16% |
| 6   | flip          | 89.5  | KBANK  | เดอะ สกาย สุขุมวิท             | เขตบางนา, กรุงเทพมหานคร    | 2.19M | 46.1%    | —     | C        | Yes   | -15.9pp vs 16% |
| 7   | flip          | 89.5  | KBANK  | เดอะ สกาย สุขุมวิท             | เขตบางนา, กรุงเทพมหานคร    | 2.24M | 45.3%    | —     | C        | Yes   | -15.9pp vs 16% |
| 8   | flip          | 89.5  | KBANK  | เดอะ สกาย สุขุมวิท             | เขตบางนา, กรุงเทพมหานคร    | 1.80M | 50.1%    | —     | C        | Yes   | -15.8pp vs 16% |
| 9   | flip          | 89.3  | BAM    | คอนโดมิเนียม โครงการราณีคอนโดท | บางกะปิ, กรุงเทพมหานคร     | 271K  | 69.8%    | —     | C        | No    | —              |
| 10  | flip          | 89.3  | BAM    | คอนโดมิเนียม โครงการราณีคอนโดท | บางกะปิ, กรุงเทพมหานคร     | 258K  | 71.3%    | —     | C        | No    | —              |


## Detailed Cards — Top 20

### #1 — แอท ซิตี้ สุขุมวิท

**KBANK** `058803180` | บางจาก, เขตพระโขนง, กรุงเทพมหานคร
Price: 1.50M (43K/sqm, 35.19 sqm) | Discount: 18.5% | BTS Tier: A
Nearest BTS/MRT: ปุณณวิถี (634m)
Anchor: Bangkok Patana สุขุมวิท 105 (intl_school) (254m)

#### Strategy Scores

- **RENT (intl_school)**: **STRONG_BUY** — 93.0/100
  - Metrics: das=55.00, annual_rent_adj=160650.00, gry=0.11, effective_gry=0.11, gry_min_threshold=0.06, nry=0.06, annual_holding_costs=75530.00, gnhc=0.47, cocr=0.11, dscr=2.71, units_for_rent=10.00, prm=9.32, real_discount_pct=18.50, score_yield=100.00, score_das=90.00, score_supply=100.00, score_building=70.00, score_liquidity=100.00
  - Flags: CoCR 11.2% >= 5.0% gate with DSCR 2.71: leveraged purchase viable
- **FLIP**: ~~AVOID~~ — 0.0/100
  - Metrics: entry_discount_pct=18.50
  - Flags: CASH_ONLY: quick flip requires cash purchase (hold < 24mo)
  - Rejected: EXIT_BELOW_FLOOR: estimated exit 1,836,918 < 3.5M THB minimum, NET_MARGIN_INSUFFICIENT: 6.9% < 10% absolute floor, NET_MARGIN_INSUFFICIENT: -1.5% < 10% absolute floor

#### Financial Overlay

- IRR: 0.1% (below_benchmark)
- CoCR: 0.1%
- DSCR: 2.74
- Break-even occupancy: 0.4%
- Hold cost (monthly): 7K
- Total acquisition cost: 1.54M
- Tax recommendation: personal_5yr_plus

**Supply pressure:** LOW (1.1%)

**Flags:** CoCR 11.2% >= 5.0% gate with DSCR 2.71: leveraged purchase viable, CASH_ONLY: quick flip requires cash purchase (hold < 24mo)
**Reject reasons:** EXIT_BELOW_FLOOR: estimated exit 1,836,918 < 3.5M THB minimum, NET_MARGIN_INSUFFICIENT: 6.9% < 10% absolute floor, NET_MARGIN_INSUFFICIENT: -1.5% < 10% absolute floor

---

### #2 — ไรส์ พระราม 9

**KBANK** `058802856` | บางกะปิ, เขตห้วยขวาง, กรุงเทพมหานคร
Price: 2.02M (60K/sqm, 33.66 sqm) | Discount: 23.2% | BTS Tier: A
Nearest BTS/MRT: รามคำแหง ARL (733m)
Anchor: มหาวิทยาลัยรามคำแหง (university) (733m)

#### Strategy Scores

- **RENT (university)**: **STRONG_BUY** — 91.5/100
  - Metrics: das=55.00, annual_rent_adj=1570800.00, gry=0.78, effective_gry=0.78, gry_min_threshold=0.07, nry=0.56, annual_holding_costs=449353.00, gnhc=0.29, cocr=1.67, dscr=26.44, units_for_rent=13.00, prm=1.29, real_discount_pct=23.20, score_yield=100.00, score_das=90.00, score_supply=100.00, score_building=60.00, score_liquidity=100.00
  - Flags: CoCR 166.9% >= 5.0% gate with DSCR 26.44: leveraged purchase viable
- **FLIP (medium_hold)**: ~~AVOID~~ — 27.6/100
  - Metrics: net_margin_pct=14.70, annualized_return_pct=7.10, entry_discount_pct=23.20, hold_months=24.00, delayed_irr_pct=3.00, liquidity_score=0.79, absorption_months_proxy=15.80
  - Flags: BELOW_OPPORTUNITY_COST: 7.1% p.a. < 15% hurdle, TIMELINE_SENSITIVE: delayed IRR 3.0% < 16% benchmark

#### Financial Overlay

- IRR: 1.4% (above_benchmark)
- CoCR: 1.4%
- DSCR: 20.81
- Break-even occupancy: 0.1%
- Hold cost (monthly): 8K
- Total acquisition cost: 2.08M
- Tax recommendation: personal_5yr_plus

**Supply pressure:** LOW (2.9%)

**Flags:** CoCR 166.9% >= 5.0% gate with DSCR 26.44: leveraged purchase viable, BELOW_OPPORTUNITY_COST: 7.1% p.a. < 15% hurdle, TIMELINE_SENSITIVE: delayed IRR 3.0% < 16% benchmark

---

### #3 — เดอะวอเตอร์ฟอร์ด รอยัลสูท

**JAM** `52` | จันทรเกษม, เขตจตุจักร, กรุงเทพมหานคร
Price: 1.70M (33K/sqm, 51.23 sqm) | Discount: 46.5% | BTS Tier: C
Nearest BTS/MRT: พหลโยธิน (2851m)
Anchor: มหาวิทยาลัยเกษตรศาสตร์ (university) (1689m)

#### Strategy Scores

- **RENT (university)**: ~~AVOID~~ — 52.5/100
  - Metrics: das=0.00, annual_rent_adj=211332.58, gry=0.12, effective_gry=0.09, gry_min_threshold=0.09, nry=0.05, annual_holding_costs=118430.00, gnhc=0.56, cocr=0.11, dscr=2.60, units_for_rent=8.00, prm=8.04, real_discount_pct=46.48, score_yield=59.90, score_das=0.00, score_supply=100.00, score_building=50.00, score_liquidity=70.00
  - Flags: DAS 0 below gate minimum 40 — penalty applied, Summer vacancy applied (Tier C + university): effective GRY 9.3% vs gross 12.4%, GNHC 56.0% > 50%: cost structure is borderline — consider price negotiation, CoCR 10.5% >= 9.0% gate with DSCR 2.60: leveraged purchase viable
  - Rejected: DAS 0 < 25: no structural tenant demand
- **FLIP (renovation_flip)**: **STRONG_BUY** — 90.9/100
  - Metrics: net_margin_pct=56.80, annualized_return_pct=56.80, entry_discount_pct=46.50, reno_cost_pct=10.00, reno_roi_ratio=4.65, liquidity_score=0.72, absorption_months_proxy=14.80

#### Financial Overlay

- IRR: 0.1% (below_benchmark)
- CoCR: 0.1%
- DSCR: 2.73
- Break-even occupancy: 0.5%
- Hold cost (monthly): 8K
- Total acquisition cost: 1.75M
- Tax recommendation: personal_5yr_plus

**Supply pressure:** LOW (2.4%)

**Flags:** DAS 0 below gate minimum 40 — penalty applied, Summer vacancy applied (Tier C + university): effective GRY 9.3% vs gross 12.4%, GNHC 56.0% > 50%: cost structure is borderline — consider price negotiation, CoCR 10.5% >= 9.0% gate with DSCR 2.60: leveraged purchase viable
**Reject reasons:** DAS 0 < 25: no structural tenant demand

---

### #4 — เดอะวอเตอร์ฟอร์ด รอยัลสูท

**KBANK** `051000705` | จันทรเกษม, เขตจตุจักร, กรุงเทพมหานคร
Price: 1.70M (33K/sqm, 51.23 sqm) | Discount: 46.5% | BTS Tier: C
Nearest BTS/MRT: พหลโยธิน (2851m)
Anchor: มหาวิทยาลัยเกษตรศาสตร์ (university) (1689m)

#### Strategy Scores

- **RENT (university)**: ~~AVOID~~ — 52.5/100
  - Metrics: das=0.00, annual_rent_adj=211332.58, gry=0.12, effective_gry=0.09, gry_min_threshold=0.09, nry=0.05, annual_holding_costs=118430.00, gnhc=0.56, cocr=0.11, dscr=2.60, units_for_rent=8.00, prm=8.04, real_discount_pct=46.48, score_yield=59.90, score_das=0.00, score_supply=100.00, score_building=50.00, score_liquidity=70.00
  - Flags: DAS 0 below gate minimum 40 — penalty applied, Summer vacancy applied (Tier C + university): effective GRY 9.3% vs gross 12.4%, GNHC 56.0% > 50%: cost structure is borderline — consider price negotiation, CoCR 10.5% >= 9.0% gate with DSCR 2.60: leveraged purchase viable
  - Rejected: DAS 0 < 25: no structural tenant demand
- **FLIP (renovation_flip)**: **STRONG_BUY** — 90.9/100
  - Metrics: net_margin_pct=56.80, annualized_return_pct=56.80, entry_discount_pct=46.50, reno_cost_pct=10.00, reno_roi_ratio=4.65, liquidity_score=0.72, absorption_months_proxy=14.80

#### Financial Overlay

- IRR: 0.1% (below_benchmark)
- CoCR: 0.1%
- DSCR: 2.73
- Break-even occupancy: 0.5%
- Hold cost (monthly): 8K
- Total acquisition cost: 1.75M
- Tax recommendation: personal_5yr_plus

**Supply pressure:** LOW (2.4%)

**Flags:** DAS 0 below gate minimum 40 — penalty applied, Summer vacancy applied (Tier C + university): effective GRY 9.3% vs gross 12.4%, GNHC 56.0% > 50%: cost structure is borderline — consider price negotiation, CoCR 10.5% >= 9.0% gate with DSCR 2.60: leveraged purchase viable
**Reject reasons:** DAS 0 < 25: no structural tenant demand

---

### #5 — ห้องชุดพักอาศัย โครงการโชคชัยปัญจทรัพย์ คอนโด ลาดพร้าว

**BAM** `DEBKKCU0269001` | ลาดพร้าว, ลาดพร้าว, กรุงเทพมหานคร
Price: 431K (15K/sqm, 29.3 sqm) | Discount: 80.5% | BTS Tier: C
Nearest BTS/MRT: รัชดาภิเษก (2233m)
Anchor: หอวัง จตุจักร (thai_school) (3756m)

> **DUAL STRATEGY**: rent + flip

#### Strategy Scores

- **RENT (thai_school)**: ~~AVOID~~ — 64.5/100
  - Metrics: das=0.00, annual_rent_adj=137689.80, gry=0.32, effective_gry=0.32, gry_min_threshold=0.07, nry=0.18, annual_holding_costs=58475.00, gnhc=0.42, cocr=0.51, dscr=8.75, units_for_rent=5.00, prm=3.13, real_discount_pct=80.54, score_yield=100.00, score_das=0.00, score_supply=100.00, score_building=50.00, score_liquidity=70.00
  - Flags: DAS 0 below gate minimum 40 — penalty applied, CoCR 50.9% >= 9.0% gate with DSCR 8.75: leveraged purchase viable
  - Rejected: DAS 0 < 25: no structural tenant demand
- **FLIP (renovation_flip)**: **STRONG_BUY** — 90.2/100
  - Metrics: net_margin_pct=354.30, annualized_return_pct=354.30, entry_discount_pct=80.50, reno_cost_pct=10.00, reno_roi_ratio=8.05, liquidity_score=0.72, absorption_months_proxy=16.80

#### Financial Overlay

- IRR: 0.6% (above_benchmark)
- CoCR: 0.6%
- DSCR: 8.40
- Break-even occupancy: 0.2%
- Hold cost (monthly): 3K
- Total acquisition cost: 444K
- Tax recommendation: personal_5yr_plus

**Supply pressure:** LOW (3.4%)

**Flags:** DAS 0 below gate minimum 40 — penalty applied, CoCR 50.9% >= 9.0% gate with DSCR 8.75: leveraged purchase viable
**Reject reasons:** DAS 0 < 25: no structural tenant demand

---

### #6 — เดอะ สกาย สุขุมวิท

**KBANK** `058802713` | บางนา, เขตบางนา, กรุงเทพมหานคร
Price: 2.19M (64K/sqm, 34.51 sqm) | Discount: 46.1% | BTS Tier: C
Nearest BTS/MRT: อุดมสุข (600m)
Anchor: St.Andrews สุขุมวิท 107 (intl_school) (1206m)

> **DUAL STRATEGY**: rent + flip

#### Strategy Scores

- **RENT (intl_school)**: **STRONG_BUY** — 88.6/100
  - Metrics: das=43.00, annual_rent_adj=249889.80, gry=0.11, effective_gry=0.11, gry_min_threshold=0.06, nry=0.07, annual_holding_costs=103230.00, gnhc=0.41, cocr=0.14, dscr=3.18, units_for_rent=149.00, prm=8.78, real_discount_pct=46.15, score_yield=97.80, score_das=66.00, score_supply=100.00, score_building=85.00, score_liquidity=100.00
  - Flags: CoCR 14.3% >= 9.0% gate with DSCR 3.18: leveraged purchase viable
- **FLIP (renovation_flip)**: **STRONG_BUY** — 89.5/100
  - Metrics: net_margin_pct=56.70, annualized_return_pct=56.70, entry_discount_pct=46.10, reno_cost_pct=10.00, reno_roi_ratio=4.61, liquidity_score=0.72, absorption_months_proxy=18.90

#### Financial Overlay

- IRR: 0.1% (below_benchmark)
- CoCR: 0.1%
- DSCR: 3.09
- Break-even occupancy: 0.4%
- Hold cost (monthly): 9K
- Total acquisition cost: 2.26M
- Tax recommendation: personal_5yr_plus

**Supply pressure:** LOW (4.5%)

**Flags:** CoCR 14.3% >= 9.0% gate with DSCR 3.18: leveraged purchase viable

---

### #7 — เดอะ สกาย สุขุมวิท

**KBANK** `058802333` | บางนา, เขตบางนา, กรุงเทพมหานคร
Price: 2.24M (65K/sqm, 34.68 sqm) | Discount: 45.3% | BTS Tier: C
Nearest BTS/MRT: อุดมสุข (609m)
Anchor: St.Andrews สุขุมวิท 107 (intl_school) (1212m)

> **DUAL STRATEGY**: rent + flip

#### Strategy Scores

- **RENT (intl_school)**: **STRONG_BUY** — 88.1/100
  - Metrics: das=43.00, annual_rent_adj=249889.80, gry=0.11, effective_gry=0.11, gry_min_threshold=0.06, nry=0.07, annual_holding_costs=103656.00, gnhc=0.41, cocr=0.14, dscr=3.11, units_for_rent=149.00, prm=8.96, real_discount_pct=45.26, score_yield=96.10, score_das=66.00, score_supply=100.00, score_building=85.00, score_liquidity=100.00
  - Flags: CoCR 13.8% >= 9.0% gate with DSCR 3.11: leveraged purchase viable
- **FLIP (renovation_flip)**: **STRONG_BUY** — 89.5/100
  - Metrics: net_margin_pct=54.00, annualized_return_pct=54.00, entry_discount_pct=45.30, reno_cost_pct=10.00, reno_roi_ratio=4.53, liquidity_score=0.72, absorption_months_proxy=18.90

#### Financial Overlay

- IRR: 0.1% (below_benchmark)
- CoCR: 0.1%
- DSCR: 3.02
- Break-even occupancy: 0.4%
- Hold cost (monthly): 9K
- Total acquisition cost: 2.31M
- Tax recommendation: personal_5yr_plus

**Supply pressure:** LOW (4.5%)

**Flags:** CoCR 13.8% >= 9.0% gate with DSCR 3.11: leveraged purchase viable

---

### #8 — เดอะ สกาย สุขุมวิท

**KBANK** `058802353` | บางนา, เขตบางนา, กรุงเทพมหานคร
Price: 1.80M (59K/sqm, 30.56 sqm) | Discount: 50.1% | BTS Tier: C
Nearest BTS/MRT: อุดมสุข (604m)
Anchor: St.Andrews สุขุมวิท 107 (intl_school) (1207m)

> **DUAL STRATEGY**: rent + flip

#### Strategy Scores

- **RENT (intl_school)**: **STRONG_BUY** — 89.2/100
  - Metrics: das=43.00, annual_rent_adj=249889.80, gry=0.14, effective_gry=0.14, gry_min_threshold=0.06, nry=0.08, annual_holding_costs=97991.00, gnhc=0.39, cocr=0.20, dscr=4.02, units_for_rent=149.00, prm=7.20, real_discount_pct=50.11, score_yield=100.00, score_das=66.00, score_supply=100.00, score_building=85.00, score_liquidity=100.00
  - Flags: CoCR 19.8% >= 9.0% gate with DSCR 4.02: leveraged purchase viable
- **FLIP (renovation_flip)**: **STRONG_BUY** — 89.5/100
  - Metrics: net_margin_pct=70.20, annualized_return_pct=70.20, entry_discount_pct=50.10, reno_cost_pct=10.00, reno_roi_ratio=5.01, liquidity_score=0.72, absorption_months_proxy=18.90

#### Financial Overlay

- IRR: 0.2% (above_benchmark)
- CoCR: 0.2%
- DSCR: 3.83
- Break-even occupancy: 0.3%
- Hold cost (monthly): 8K
- Total acquisition cost: 1.85M
- Tax recommendation: personal_5yr_plus

**Supply pressure:** LOW (4.5%)

**Flags:** CoCR 19.8% >= 9.0% gate with DSCR 4.02: leveraged purchase viable

---

### #9 — คอนโดมิเนียม โครงการราณีคอนโดทาวน์ บางกะปิ

**BAM** `HBKKCU1572001` | คลองกุ่ม, บางกะปิ, กรุงเทพมหานคร
Price: 271K (11K/sqm, 24.5 sqm) | Discount: 69.8% | BTS Tier: C
Nearest BTS/MRT: สะพานใหม่ (7768m)
Anchor: มหาวิทยาลัยศรีปทุม (university) (8433m)

#### Strategy Scores

- **RENT (university)**: ~~AVOID~~ — 0.0/100
  - Metrics: das=0.00
  - Flags: DAS 0 below gate minimum 40 — penalty applied
  - Rejected: DAS 0 < 25: no structural tenant demand, No rent data available (market_rent_median missing)
- **FLIP (renovation_flip)**: **STRONG_BUY** — 89.3/100
  - Metrics: net_margin_pct=185.50, annualized_return_pct=185.50, entry_discount_pct=69.80, reno_cost_pct=10.00, reno_roi_ratio=6.98, liquidity_score=0.51, absorption_months_proxy=10.10

#### Financial Overlay

- IRR: — (—)
- CoCR: —
- DSCR: —
- Break-even occupancy: —
- Hold cost (monthly): 2K
- Total acquisition cost: 279K
- Tax recommendation: personal_5yr_plus

**Supply pressure:** LOW (0.1%)

**Flags:** DAS 0 below gate minimum 40 — penalty applied
**Reject reasons:** DAS 0 < 25: no structural tenant demand, No rent data available (market_rent_median missing)

---

### #10 — คอนโดมิเนียม โครงการราณีคอนโดทาวน์ บางกะปิ

**BAM** `HBKKCU1100001` | คลองกุ่ม, บางกะปิ, กรุงเทพมหานคร
Price: 258K (11K/sqm, 24.5 sqm) | Discount: 71.3% | BTS Tier: C
Nearest BTS/MRT: สะพานใหม่ (7768m)
Anchor: มหาวิทยาลัยศรีปทุม (university) (8433m)

#### Strategy Scores

- **RENT (university)**: ~~AVOID~~ — 0.0/100
  - Metrics: das=0.00
  - Flags: DAS 0 below gate minimum 40 — penalty applied
  - Rejected: DAS 0 < 25: no structural tenant demand, No rent data available (market_rent_median missing)
- **FLIP (renovation_flip)**: **STRONG_BUY** — 89.3/100
  - Metrics: net_margin_pct=200.50, annualized_return_pct=200.50, entry_discount_pct=71.30, reno_cost_pct=10.00, reno_roi_ratio=7.13, liquidity_score=0.51, absorption_months_proxy=10.10

#### Financial Overlay

- IRR: — (—)
- CoCR: —
- DSCR: —
- Break-even occupancy: —
- Hold cost (monthly): 2K
- Total acquisition cost: 266K
- Tax recommendation: personal_5yr_plus

**Supply pressure:** LOW (0.1%)

**Flags:** DAS 0 below gate minimum 40 — penalty applied
**Reject reasons:** DAS 0 < 25: no structural tenant demand, No rent data available (market_rent_median missing)

---


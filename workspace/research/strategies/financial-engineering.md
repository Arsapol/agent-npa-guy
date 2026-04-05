# Financial Engineering Layer — Thai NPA Investment
**Date:** 2026-04-05  
**Purpose:** Cross-cutting financial metrics that amplify returns across ALL NPA strategies  
**Applies to:** Rental, Flip, Land Bank, Renovation/Hospitality

---

## 1. Leverage & Financing Metrics

### 1.1 Cash-on-Cash Return (CoCR)

**Formula:**
```
CoCR = Annual Pre-Tax Cash Flow / Total Cash Invested

Annual Pre-Tax Cash Flow = Gross Rent × 12 - Operating Expenses - Annual Debt Service
Total Cash Invested = Down Payment + Closing Costs + Renovation (cash portion)
```

**Python:**
```python
def cash_on_cash_return(
    monthly_rent: float,
    vacancy_rate: float,        # 0.08 = 8%
    operating_expenses: float,  # annual: CAM + insurance + property_tax + mgmt_fee
    annual_debt_service: float, # principal + interest per year
    down_payment: float,
    closing_costs: float,
    renovation_cash: float,
) -> float:
    effective_gross_income = monthly_rent * 12 * (1 - vacancy_rate)
    net_operating_income = effective_gross_income - operating_expenses
    annual_cash_flow = net_operating_income - annual_debt_service
    total_cash_invested = down_payment + closing_costs + renovation_cash
    return annual_cash_flow / total_cash_invested
```

**Data sources:** Actual rent (DDProperty/Hipflat comps), bank mortgage schedule, juristic office CAM fee, land department appraisal for property tax.

**Thresholds by strategy:**
| Strategy | Min CoCR | Target CoCR |
|----------|----------|-------------|
| Rental (BTS tier A) | 5% | 8% |
| Rental (BTS tier B) | 7% | 10% |
| Rental (BTS tier C) | 9% | 12% |
| Flip (leveraged) | N/A (no income) | — |
| Land Bank | N/A (no income) | — |

**Scoring impact:** CoCR below min threshold → REJECT for rental strategy. For flip, use IRR instead.

---

### 1.2 LTV Optimization Decision

**When to maximize leverage (100% LTV, BoT relaxation to June 2026):**
- CoCR with leverage > CoCR without leverage (positive leverage)
- DSCR > 1.25 (comfortable coverage)
- Exit horizon > 3 years (amortization works in your favour)
- Property qualifies: first home > 10M THB, or second home < 10M THB

**When to go cash:**
- Flip horizon < 24 months (mortgage setup cost 1-2% kills IRR)
- NPA discount > 40% (redeployment speed > leverage benefit)
- Property price < 3M THB (mortgage rejection rate 40-70% for this band)
- Renovation > 30% of purchase price (bank won't lend on distressed condition)

**Python decision function:**
```python
def leverage_decision(
    property_price: float,
    monthly_rent: float,
    vacancy_rate: float,
    opex_annual: float,
    mortgage_rate: float,   # e.g. 0.03 for 3% fixed
    ltv: float,             # e.g. 0.90
    loan_term_years: int,   # e.g. 30
    flip_horizon_months: int | None,  # None if rental
) -> dict:
    loan_amount = property_price * ltv
    monthly_rate = mortgage_rate / 12
    n = loan_term_years * 12
    monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate)**n) / ((1 + monthly_rate)**n - 1)
    annual_debt_service = monthly_payment * 12

    noi = monthly_rent * 12 * (1 - vacancy_rate) - opex_annual
    dscr = noi / annual_debt_service if annual_debt_service > 0 else float('inf')

    down_payment = property_price * (1 - ltv)
    cocr_leveraged = (noi - annual_debt_service) / (down_payment + property_price * 0.02)  # +2% closing
    cocr_cash = noi / property_price

    use_leverage = (
        dscr >= 1.25
        and cocr_leveraged > cocr_cash
        and property_price >= 3_000_000
        and (flip_horizon_months is None or flip_horizon_months > 24)
    )

    return {
        "use_leverage": use_leverage,
        "dscr": round(dscr, 2),
        "cocr_leveraged": round(cocr_leveraged, 4),
        "cocr_cash": round(cocr_cash, 4),
        "monthly_payment_thb": round(monthly_payment, 0),
        "loan_amount_thb": round(loan_amount, 0),
    }
```

**Data sources:** Bangkok Bank / KBank mortgage rate sheet (2.9-3.3% fixed first 3 years, 5-7% floating thereafter), BoT LTV circular.

---

### 1.3 Debt Service Coverage Ratio (DSCR)

**Formula:**
```
DSCR = Net Operating Income / Annual Debt Service
NOI = Effective Gross Income - Operating Expenses
Effective Gross Income = Gross Rent × 12 × (1 - vacancy_rate)
```

**Python:**
```python
def dscr(
    monthly_rent: float,
    vacancy_rate: float,
    opex_annual: float,
    annual_debt_service: float,
) -> float:
    egi = monthly_rent * 12 * (1 - vacancy_rate)
    noi = egi - opex_annual
    return noi / annual_debt_service
```

**Thresholds:**
- DSCR < 1.0 → negative cash flow, REJECT if leveraged
- DSCR 1.0-1.25 → marginal, only accept if strong appreciation play
- DSCR 1.25-1.5 → acceptable
- DSCR > 1.5 → strong

**Scoring impact:** DSCR < 1.0 forces either cash purchase or reject for rental strategy.

---

### 1.4 Break-Even Occupancy

**Formula:**
```
Break-Even Occupancy = Fixed Annual Costs / Potential Gross Rent (100% occupancy)
Fixed Annual Costs = Annual Debt Service + Operating Expenses
```

**Python:**
```python
def break_even_occupancy(
    monthly_rent: float,
    opex_annual: float,
    annual_debt_service: float,
) -> float:
    potential_gross = monthly_rent * 12
    fixed_costs = opex_annual + annual_debt_service
    return fixed_costs / potential_gross  # e.g. 0.65 = 65% occupancy needed
```

**Thresholds:**
- BEO < 50% → very safe, absorbs high vacancy
- BEO 50-70% → acceptable
- BEO > 80% → fragile, reject unless premium location

**Data sources:** Juristic office CAM statement, land department appraised value for property tax.

---

### 1.5 Interest Rate Sensitivity

**Context:** Thai mortgages: 2.9-3.3% fixed first 3 years, then 5-7% floating. BoT policy rate 1.00% (historically low, risk is UP).

**Formula — impact of rate increase on cash flow:**
```
ΔCash Flow = -Loan Amount × Δrate / 12 × 12
            = -Loan Amount × Δrate
```

**Python:**
```python
def rate_sensitivity_analysis(
    loan_amount: float,
    base_rate: float,
    scenarios: list[float],  # e.g. [0.005, 0.01, 0.02] = +0.5%, +1%, +2%
    monthly_rent: float,
    vacancy_rate: float,
    opex_annual: float,
) -> list[dict]:
    results = []
    for delta in scenarios:
        new_rate = base_rate + delta
        monthly_rate = new_rate / 12
        # Approximate: recalculate monthly payment at new rate, 27 remaining years (after 3yr fixed)
        n = 27 * 12
        monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate)**n) / ((1 + monthly_rate)**n - 1)
        annual_debt_service = monthly_payment * 12
        egi = monthly_rent * 12 * (1 - vacancy_rate)
        noi = egi - opex_annual
        annual_cash_flow = noi - annual_debt_service
        results.append({
            "rate": round(new_rate * 100, 2),
            "annual_cash_flow": round(annual_cash_flow, 0),
            "dscr": round(noi / annual_debt_service, 2),
        })
    return results
```

**Rule:** If DSCR < 1.0 at base_rate + 2%, flag as RATE RISK and require 15% larger down payment buffer.

---

## 2. Tax Optimization Metrics

### 2.1 SBT vs. Income Tax Optimization

**Regime rules (current law, 2026):**
- Hold < 5 years → Specific Business Tax (SBT) = 3.3% of transaction value (3% SBT + 10% municipal surcharge)
- Hold ≥ 5 years → Stamp Duty = 0.5% of transaction value
- SBT exemption: seller registered in property's house registration book (tabien baan) ≥ 1 year

**Income tax on sale (personal):**
- No separate capital gains tax for Thai individuals
- Gain treated as assessable income, but withholding tax on sale applies per Revenue Dept table (varies with years of ownership and appraised value)

**Python — tax comparison on exit:**
```python
def exit_tax_comparison(
    sale_price: float,
    appraisal_value: float,
    hold_years: float,
    in_tabien_baan: bool = False,
) -> dict:
    """
    Returns estimated exit taxes for NPA sale.
    sale_price and appraisal_value in THB.
    Tax base = higher of sale_price or appraisal_value.
    """
    tax_base = max(sale_price, appraisal_value)

    # SBT regime
    if hold_years < 5 and not in_tabien_baan:
        sbt = tax_base * 0.033  # 3% + 10% municipal
        stamp_duty = 0.0
        regime = "SBT"
    else:
        sbt = 0.0
        stamp_duty = tax_base * 0.005
        regime = "Stamp Duty"

    # Transfer fee (2%, typically split — NPA sellers often absorb)
    transfer_fee = tax_base * 0.02

    return {
        "regime": regime,
        "sbt_thb": round(sbt, 0),
        "stamp_duty_thb": round(stamp_duty, 0),
        "transfer_fee_thb": round(transfer_fee, 0),
        "total_exit_tax_thb": round(sbt + stamp_duty + transfer_fee, 0),
        "exit_tax_pct_of_sale": round((sbt + stamp_duty + transfer_fee) / sale_price * 100, 2),
    }
```

**Scoring impact:**
- Flip strategy: if exit < 5 years, add 3.3% to acquisition hurdle rate
- Long-hold rental: hold ≥ 5 years saves ~2.8% of sale value vs. early exit

**NPA-specific:** LED/SAM/BAM sellers (banks/government) often absorb full 2% transfer fee in down market. Model as 0% to buyer; add 2% back as upside scenario.

---

### 2.2 Transfer Fee Negotiation Value

**Formula — value of full transfer fee absorption by seller:**
```
Transfer Fee Saving = Appraisal Value × 0.01  (buyer's share = 1% of 2% total)
NPA scenario: seller absorbs full 2% → Saving = Appraisal Value × 0.02
```

**Python:**
```python
def transfer_fee_saving(
    appraisal_value: float,
    buyer_absorbs_pct: float = 0.5,  # 0.5 = split, 0.0 = seller pays all
) -> float:
    total_fee = appraisal_value * 0.02
    buyer_cost = total_fee * buyer_absorbs_pct
    max_saving = total_fee  # if seller pays all
    actual_saving = max_saving - buyer_cost
    return round(actual_saving, 0)
```

**Data sources:** Sale and Purchase Agreement; NPA seller motivation inferred from SAM/BAM/LED days-on-market (>180 days = seller likely to absorb fees).

---

### 2.3 Depreciation Benefit (Corporate Holder)

**Thai corporate depreciation rules (Revenue Department):**
- Buildings: max 5% per year straight-line (20-year life)
- Furniture/fixtures: max 20% per year
- Equipment: max 20% per year

**Formula:**
```
Annual Depreciation Deduction = Building Value × Depreciation Rate
Tax Saving = Annual Depreciation Deduction × Corporate Tax Rate (20%)
NPV of Depreciation Shield = Σ (Tax Saving_t / (1+r)^t) for t=1 to N
```

**Python:**
```python
import numpy as np

def depreciation_npv_shield(
    building_value: float,
    depreciation_rate: float = 0.05,  # 5% for buildings
    corporate_tax_rate: float = 0.20,
    discount_rate: float = 0.08,
    hold_years: int = 10,
) -> dict:
    annual_deduction = building_value * depreciation_rate
    annual_tax_saving = annual_deduction * corporate_tax_rate
    cash_flows = [annual_tax_saving] * hold_years
    npv = sum(cf / (1 + discount_rate)**t for t, cf in enumerate(cash_flows, 1))
    return {
        "annual_deduction_thb": round(annual_deduction, 0),
        "annual_tax_saving_thb": round(annual_tax_saving, 0),
        "npv_depreciation_shield_thb": round(npv, 0),
    }
```

**Note:** Land cannot be depreciated — only building value. Split purchase price: typically 20-40% land, 60-80% building for Bangkok condos.

---

### 2.4 Entity Structuring Decision

**Personal vs. Thai Company:**

| Dimension | Personal | Thai Company |
|-----------|----------|--------------|
| Rental income tax | Progressive 5-35% (effective ~5-15% with deductions) | 20% flat on net profit |
| SBT on exit < 5yr | 3.3% | 3.3% (companies always pay SBT regardless of hold) |
| Depreciation | Not available | Yes, 5%/yr building |
| Transfer fee | 2% (negotiable) | 2% (negotiable) |
| Setup cost | 0 | ~50,000-100,000 THB |
| Annual accounting | ~20,000 THB | ~60,000-120,000 THB |
| Scale threshold | 1-2 units | 3+ units |
| Dividend extraction | N/A | 10% withholding tax on dividends |

**CRITICAL:** Thai companies ALWAYS pay SBT (3.3%) on property sale regardless of hold period. Personal holds ≥ 5 years pay only 0.5% stamp duty. For long-hold rental, personal ownership is usually superior.

**Python decision:**
```python
def entity_structure_recommendation(
    num_properties: int,
    avg_annual_rental_income: float,
    hold_years: float,
    investor_other_income: float,  # personal income from other sources
) -> dict:
    # Effective personal tax rate on rental income
    total_personal_income = investor_other_income + avg_annual_rental_income
    # Simplified Thai PIT brackets 2026
    def personal_tax(income):
        brackets = [(150_000, 0), (300_000, 0.05), (500_000, 0.10),
                    (750_000, 0.15), (1_000_000, 0.20), (2_000_000, 0.25),
                    (5_000_000, 0.30), (float('inf'), 0.35)]
        tax = 0
        prev = 0
        for limit, rate in brackets:
            if income <= prev:
                break
            taxable = min(income, limit) - prev
            tax += taxable * rate
            prev = limit
        return tax

    personal_tax_on_rental = personal_tax(total_personal_income) - personal_tax(investor_other_income)
    personal_effective_rate = personal_tax_on_rental / avg_annual_rental_income

    company_tax_on_rental = avg_annual_rental_income * 0.20
    company_effective_rate = 0.20

    # Exit tax difference
    exit_advantage_personal = (0.033 - 0.005) if hold_years >= 5 else 0  # personal saves 2.8% on exit

    recommend_company = (
        num_properties >= 3
        and personal_effective_rate > 0.20
        and hold_years < 5  # company loses exit tax advantage at < 5yr anyway
    )

    return {
        "recommended_structure": "company" if recommend_company else "personal",
        "personal_effective_tax_rate": round(personal_effective_rate * 100, 1),
        "company_effective_tax_rate": 20.0,
        "exit_tax_saving_personal_pct": round(exit_advantage_personal * 100, 1),
        "annual_admin_cost_company_thb": 90_000,  # midpoint estimate
    }
```

---

### 2.5 Foreign Quota Premium/Constraint Analysis

**49% rule:** Foreigners can own up to 49% of total usable floor area per building.

**Impact on NPA screening:**
- Foreign quota FULL → foreign buyer cannot purchase in that building (HARD BLOCK for foreign buyers)
- Foreign quota available → unit trades at slight premium vs. Thai quota in some buildings
- NPA units are typically Thai quota (original owner defaulted = Thai national) → no premium for foreign buyer

**Python:**
```python
def foreign_quota_check(
    building_foreign_quota_used_pct: float,  # e.g. 0.42 = 42% used of 49%
    unit_is_foreign_quota: bool,
    buyer_is_foreign: bool,
) -> dict:
    quota_remaining = max(0, 0.49 - building_foreign_quota_used_pct)
    can_buy_as_foreigner = (
        unit_is_foreign_quota and buyer_is_foreign and quota_remaining > 0
    ) or not buyer_is_foreign

    # NPA units are usually Thai quota
    npa_premium_adjustment = 0.0  # no premium for Thai quota NPA unit
    if unit_is_foreign_quota and quota_remaining < 0.05:
        npa_premium_adjustment = 0.03  # 3% premium if foreign quota is scarce

    return {
        "can_buy": can_buy_as_foreigner,
        "quota_remaining_pct": round(quota_remaining * 100, 1),
        "premium_adjustment": npa_premium_adjustment,
    }
```

---

## 3. Total Return Modeling

### 3.1 IRR Calculation

**Full cash flow model over hold period:**

```python
import numpy as np
from scipy.optimize import brentq

def calculate_irr(cash_flows: list[float]) -> float:
    """
    cash_flows[0] = initial investment as negative number
    cash_flows[1..N] = annual net cash flows
    cash_flows[-1] should include terminal sale proceeds
    """
    def npv(rate, flows):
        return sum(cf / (1 + rate)**t for t, cf in enumerate(flows))

    try:
        irr = brentq(lambda r: npv(r, cash_flows), -0.5, 10.0)
        return round(irr, 4)
    except ValueError:
        return None


def build_npa_cash_flows(
    purchase_price: float,
    closing_costs: float,          # transfer fee + legal + misc
    renovation_cost: float,
    down_payment_pct: float,       # 0.10 = 10% down
    mortgage_rate: float,
    loan_term_years: int,
    monthly_rent: float,
    vacancy_rate: float,
    opex_annual: float,            # CAM + insurance + property_tax + mgmt
    rent_growth_rate: float,       # annual, e.g. 0.02
    hold_years: int,
    exit_price_multiple: float,    # e.g. 1.20 = 20% appreciation
    exit_tax_rate: float,          # from exit_tax_comparison()
) -> list[float]:
    loan = purchase_price * (1 - down_payment_pct)
    down = purchase_price * down_payment_pct
    initial_outflow = -(down + closing_costs + renovation_cost)

    monthly_rate = mortgage_rate / 12
    n = loan_term_years * 12
    monthly_payment = loan * (monthly_rate * (1 + monthly_rate)**n) / ((1 + monthly_rate)**n - 1)
    annual_debt_service = monthly_payment * 12

    flows = [initial_outflow]
    for year in range(1, hold_years + 1):
        rent = monthly_rent * (1 + rent_growth_rate)**(year - 1)
        egi = rent * 12 * (1 - vacancy_rate)
        noi = egi - opex_annual
        cash_flow = noi - annual_debt_service

        if year == hold_years:
            exit_price = purchase_price * exit_price_multiple
            # Remaining loan balance
            payments_made = hold_years * 12
            remaining_balance = loan * (1 + monthly_rate)**payments_made - \
                monthly_payment * ((1 + monthly_rate)**payments_made - 1) / monthly_rate
            net_sale = exit_price * (1 - exit_tax_rate) - remaining_balance
            cash_flow += net_sale

        flows.append(cash_flow)

    return flows
```

**IRR thresholds by strategy:**
| Strategy | Min IRR | Target IRR |
|----------|---------|------------|
| Rental hold 5yr | 10% | 15% |
| Rental hold 10yr | 8% | 12% |
| Flip (12-24 mo) | 20% | 30% |
| Land bank | 12% | 18% |
| Reno/Hospitality | 15% | 25% |

---

### 3.2 Hold Cost Per Month

**Formula:**
```
Hold Cost/Month = (Mortgage Payment + CAM + Insurance + Vacancy Reserve + Property Tax/12)
During renovation period: no rental income, hold cost = pure cash burn
```

**Python:**
```python
def monthly_hold_cost(
    monthly_mortgage: float,
    cam_monthly: float,           # common area maintenance (juristic)
    insurance_annual: float,
    vacancy_reserve_pct: float,   # % of monthly rent set aside, e.g. 0.08
    monthly_rent: float,
    appraisal_value: float,
    property_tax_rate: float = 0.002,  # 0.2% for residential
    is_renovation_period: bool = False,
) -> dict:
    property_tax_monthly = appraisal_value * property_tax_rate / 12
    insurance_monthly = insurance_annual / 12
    vacancy_reserve = monthly_rent * vacancy_reserve_pct
    
    total = monthly_mortgage + cam_monthly + insurance_monthly + property_tax_monthly
    if not is_renovation_period:
        total += vacancy_reserve

    return {
        "total_monthly_hold_cost_thb": round(total, 0),
        "breakeven_rent_thb": round(total, 0),
        "renovation_period_burn_monthly_thb": round(
            monthly_mortgage + cam_monthly + insurance_monthly + property_tax_monthly, 0
        ),
    }
```

**Typical Bangkok condo (2026 benchmarks):**
- CAM: 40-80 THB/sqm/month (e.g., 35sqm unit = 1,400-2,800 THB/mo)
- Insurance: ~3,000-8,000 THB/year for standard condo
- Property tax: 0.02-0.3% appraised value; residential non-rented = 0.02%, rented = 0.2%

---

### 3.3 Renovation Financing (Can It Be Rolled into Mortgage?)

**Thai bank practice:**
- Standard mortgage: covers purchase price only, not renovation
- "Home improvement loan" (สินเชื่อปรับปรุงบ้าน): separate product, 5-7% rate, up to 1M THB
- Some banks (Krungthai, SCB) allow top-up after 1-year payment history
- NPA condition discount should cover renovation: if NPA price < market - renovation - 20% margin, renovation stays cash

**Python:**
```python
def renovation_financing_check(
    npa_price: float,
    market_price: float,
    renovation_estimate: float,
    min_equity_margin: float = 0.20,
) -> dict:
    implied_discount = (market_price - npa_price) / market_price
    renovation_pct_of_price = renovation_estimate / npa_price
    net_margin = implied_discount - renovation_pct_of_price - min_equity_margin

    can_absorb_reno_in_discount = net_margin >= 0

    return {
        "implied_discount_pct": round(implied_discount * 100, 1),
        "renovation_pct_of_price": round(renovation_pct_of_price * 100, 1),
        "net_margin_after_reno": round(net_margin * 100, 1),
        "renovation_covered_by_discount": can_absorb_reno_in_discount,
        "recommendation": (
            "Renovation cost absorbed by NPA discount — no separate financing needed"
            if can_absorb_reno_in_discount
            else f"Gap {-net_margin*100:.1f}% — consider home improvement loan or renegotiate price"
        ),
    }
```

---

### 3.4 Opportunity Cost Benchmark

**2026 benchmarks (Thailand):**
| Asset | Expected Return | Liquidity |
|-------|----------------|-----------|
| Thai 10yr gov bond | 2.8-3.2% | High |
| SET index (Thai equities) | 6-8% historical avg | High |
| S&P 500 ETF (USD-denominated) | 8-10% historical avg | High |
| Thai REITs (REIT avg yield) | 5-7% | Medium |
| Bangkok condo (rental only, no leverage) | 4-6% | Low |
| NPA condo (leveraged, BTS tier A) | 10-18% IRR | Very Low |

**Python:**
```python
BENCHMARKS = {
    "thai_gov_bond_10yr": 0.030,
    "thai_set_index": 0.070,
    "sp500_usd": 0.090,
    "thai_reits": 0.060,
}

def opportunity_cost_analysis(
    npa_irr: float,
    hold_years: int,
    cash_invested: float,
) -> dict:
    results = {}
    for name, annual_return in BENCHMARKS.items():
        future_value = cash_invested * (1 + annual_return)**hold_years
        results[name] = {
            "annual_return_pct": round(annual_return * 100, 1),
            "future_value_thb": round(future_value, 0),
        }
    npa_future_value = cash_invested * (1 + npa_irr)**hold_years
    outperformance_vs_bond = npa_irr - BENCHMARKS["thai_gov_bond_10yr"]
    outperformance_vs_reit = npa_irr - BENCHMARKS["thai_reits"]

    return {
        "npa_irr": round(npa_irr * 100, 1),
        "npa_future_value_thb": round(npa_future_value, 0),
        "benchmarks": results,
        "outperformance_vs_bond_pct": round(outperformance_vs_bond * 100, 1),
        "outperformance_vs_reit_pct": round(outperformance_vs_reit * 100, 1),
        "illiquidity_premium_justified": npa_irr > BENCHMARKS["thai_reits"] + 0.03,
    }
```

**Rule:** If NPA IRR < Thai REIT yield + 3% illiquidity premium, the deal does not compensate for illiquidity risk.

---

## 4. Risk Metrics

### 4.1 Maximum Drawdown (Underwater Risk)

**Definition:** How much property value can fall before equity is wiped out.

**Formula:**
```
Equity Cushion = Property Value - Outstanding Loan Balance
Maximum Tolerable Drop = Equity Cushion / Property Value
```

**Python:**
```python
def underwater_risk(
    current_value: float,
    original_purchase_price: float,
    down_payment_pct: float,
    years_held: float,
    mortgage_rate: float,
    loan_term_years: int,
) -> dict:
    loan = original_purchase_price * (1 - down_payment_pct)
    monthly_rate = mortgage_rate / 12
    n = loan_term_years * 12
    monthly_payment = loan * (monthly_rate * (1 + monthly_rate)**n) / ((1 + monthly_rate)**n - 1)
    payments_made = years_held * 12
    remaining_balance = loan * (1 + monthly_rate)**payments_made - \
        monthly_payment * ((1 + monthly_rate)**payments_made - 1) / monthly_rate

    equity = current_value - remaining_balance
    equity_pct = equity / current_value
    max_drop_pct = equity / current_value  # = equity_pct

    return {
        "current_equity_thb": round(equity, 0),
        "equity_pct": round(equity_pct * 100, 1),
        "max_value_drop_before_underwater_pct": round(max_drop_pct * 100, 1),
        "underwater_threshold_thb": round(remaining_balance, 0),
        "risk_level": (
            "HIGH" if equity_pct < 0.15
            else "MEDIUM" if equity_pct < 0.30
            else "LOW"
        ),
    }
```

**NPA context:** LED auction floor is 70% of appraised value. If you buy at 70%, remaining 30% is equity buffer before underwater. With 90% LTV on a 70%-of-appraisal purchase, equity = (appraisal × 0.70 × 0.10) / (appraisal × 0.70) = 10% — very thin.

---

### 4.2 Liquidity Score

**Formula (composite score 0-100):**

```python
def liquidity_score(
    days_on_market_avg_area: int,        # from DDProperty/Hipflat data
    active_listings_in_building: int,    # supply overhang
    npa_concentration_pct: float,        # % NPA units in building
    building_age_years: int,
    distance_bts_m: int,
) -> dict:
    score = 100

    # Penalize slow-moving areas
    if days_on_market_avg_area > 180:
        score -= 30
    elif days_on_market_avg_area > 90:
        score -= 15

    # Supply overhang in building
    if active_listings_in_building > 10:
        score -= 20
    elif active_listings_in_building > 5:
        score -= 10

    # NPA concentration (>8% = stigma)
    if npa_concentration_pct > 0.08:
        score -= 25
    elif npa_concentration_pct > 0.04:
        score -= 10

    # Age (older = harder to finance for next buyer)
    if building_age_years > 20:
        score -= 15
    elif building_age_years > 15:
        score -= 5

    # BTS proximity
    if distance_bts_m > 1500:
        score -= 20
    elif distance_bts_m > 800:
        score -= 10

    return {
        "liquidity_score": max(0, score),
        "liquidity_tier": (
            "HIGH" if score >= 70
            else "MEDIUM" if score >= 40
            else "LOW"
        ),
        "estimated_months_to_sell": (
            3 if score >= 70 else 9 if score >= 40 else 18
        ),
    }
```

**Scoring impact:** Liquidity score LOW → apply 5% exit price haircut in IRR model.

---

### 4.3 Concentration Risk (Portfolio Level)

**Formula:**
```
Single-Asset Concentration = Asset Value / Total Portfolio Value
Geographic Concentration = Σ(Assets in same sub-district) / Total Portfolio Value
```

**Python:**
```python
def concentration_risk(
    portfolio: list[dict],  # [{value, subdistrict, strategy}]
) -> dict:
    total_value = sum(p["value"] for p in portfolio)
    
    # Geographic HHI
    from collections import defaultdict
    by_subdistrict = defaultdict(float)
    for p in portfolio:
        by_subdistrict[p["subdistrict"]] += p["value"]
    
    hhi_geo = sum((v / total_value)**2 for v in by_subdistrict.values())
    
    # Strategy HHI
    by_strategy = defaultdict(float)
    for p in portfolio:
        by_strategy[p["strategy"]] += p["value"]
    hhi_strategy = sum((v / total_value)**2 for v in by_strategy.values())

    return {
        "total_portfolio_value_thb": round(total_value, 0),
        "geographic_hhi": round(hhi_geo, 3),     # 1.0 = fully concentrated
        "strategy_hhi": round(hhi_strategy, 3),
        "concentration_risk": (
            "HIGH" if hhi_geo > 0.5
            else "MEDIUM" if hhi_geo > 0.25
            else "LOW"
        ),
        "recommendation": (
            "Diversify across 3+ subdistricts"
            if hhi_geo > 0.5
            else "Acceptable concentration"
        ),
    }
```

---

## 5. Composite Financial Engineering Score

**Weights for integration into NPA screener:**

```python
def financial_engineering_score(
    cocr: float,           # 0.0-0.20+
    dscr: float,           # 0.0-3.0+
    irr: float,            # 0.0-0.50+
    break_even_occ: float, # 0.0-1.0
    liquidity_score: int,  # 0-100
    exit_tax_pct: float,   # 0.0-0.05
    equity_pct: float,     # 0.0-1.0
) -> dict:
    # Normalize each metric to 0-1
    score_cocr = min(1.0, max(0, (cocr - 0.03) / (0.15 - 0.03)))      # 3% = 0, 15% = 1
    score_dscr = min(1.0, max(0, (dscr - 0.8) / (2.0 - 0.8)))         # 0.8 = 0, 2.0 = 1
    score_irr = min(1.0, max(0, (irr - 0.05) / (0.30 - 0.05)))        # 5% = 0, 30% = 1
    score_beo = min(1.0, max(0, (0.85 - break_even_occ) / (0.85 - 0.30)))  # 85% = 0, 30% = 1
    score_liq = liquidity_score / 100
    score_exit_tax = min(1.0, max(0, (0.05 - exit_tax_pct) / 0.05))   # 5% = 0, 0% = 1
    score_equity = min(1.0, max(0, (equity_pct - 0.05) / (0.40 - 0.05))) # 5% = 0, 40% = 1

    # Weighted composite (weights sum to 1.0)
    weights = {
        "irr": 0.30,
        "cocr": 0.20,
        "dscr": 0.15,
        "beo": 0.10,
        "liquidity": 0.10,
        "exit_tax": 0.10,
        "equity": 0.05,
    }
    composite = (
        weights["irr"] * score_irr +
        weights["cocr"] * score_cocr +
        weights["dscr"] * score_dscr +
        weights["beo"] * score_beo +
        weights["liquidity"] * score_liq +
        weights["exit_tax"] * score_exit_tax +
        weights["equity"] * score_equity
    )

    return {
        "financial_engineering_score": round(composite * 100, 1),
        "grade": (
            "A" if composite >= 0.75
            else "B" if composite >= 0.60
            else "C" if composite >= 0.45
            else "D"
        ),
        "component_scores": {
            "irr": round(score_irr * 100, 1),
            "cocr": round(score_cocr * 100, 1),
            "dscr": round(score_dscr * 100, 1),
            "break_even_occ": round(score_beo * 100, 1),
            "liquidity": round(score_liq * 100, 1),
            "exit_tax": round(score_exit_tax * 100, 1),
            "equity_cushion": round(score_equity * 100, 1),
        },
    }
```

---

## 6. Strategy-Specific Application Summary

### How financial engineering score changes per strategy:

| Metric | Rental | Flip | Land Bank | Reno/Hospitality |
|--------|--------|------|-----------|-----------------|
| CoCR | Primary | N/A | N/A | Secondary |
| DSCR | Required | N/A | N/A | Required |
| IRR | Secondary | Primary | Primary | Primary |
| BEO | Required | N/A | N/A | Required |
| SBT optimization | Hold ≥5yr | Critical (adds 3.3% cost) | Hold ≥5yr | Depends on exit plan |
| Entity structure | Personal preferred | Personal preferred (1-2 units) | Company if 3+ plots | Depends on scale |
| LTV strategy | Maximize if DSCR OK | Avoid (speed > leverage) | Cash preferred | 60-70% LTV |
| Liquidity score | Min 40 | Min 60 | Min 20 (OK illiquid) | Min 50 |

---

## 7. Key Thai Market Constants (2026)

```python
THAI_CONSTANTS = {
    "bot_policy_rate": 0.0100,           # 1.00% (April 2026)
    "mortgage_fixed_3yr": 0.031,         # 3.1% avg first 3yr fixed
    "mortgage_floating": 0.060,          # 6.0% avg after fixed period
    "corporate_income_tax": 0.20,
    "sbt_rate": 0.033,                   # 3% + 10% municipal surcharge
    "stamp_duty_rate": 0.005,            # 0.5% if hold ≥ 5yr
    "transfer_fee_rate": 0.02,           # 2% of appraisal
    "property_tax_residential_rented": 0.002,   # 0.2%
    "property_tax_residential_vacant": 0.0002,  # 0.02%
    "building_depreciation_max": 0.05,   # 5%/yr straight line
    "foreign_quota_max": 0.49,           # 49% of usable floor area
    "led_auction_floor": 0.70,           # 70% of appraised value
    "ltv_relaxation_deadline": "2026-06-30",  # BoT LTV relaxation expiry
    "mortgage_rejection_rate_under_3m": 0.55, # ~55% rejection for <3M THB
}
```

---

*Sources: BoT policy rate announcement Dec 2025; PropertyScout LTV guide 2025-2026; Bangkok Post LTV relaxation article; FRANK Legal Thai Condo Tax Guide 2025; Forbes & Partners Thailand transfer cost breakdown; PwC Thailand Corporate Deductions; Revenue Department CIT tables.*

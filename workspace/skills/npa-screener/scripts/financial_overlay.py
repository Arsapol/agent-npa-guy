"""
Financial engineering overlay for Multi-Strategy NPA Screener v2.

Computes IRR approximation, cash-on-cash return, DSCR, break-even occupancy,
hold costs, acquisition costs, exit tax, and opportunity cost comparison.
"""

from typing import Optional

from constants import (
    CAM_DEFAULT_SQM,
    IRR_BENCHMARK,
    MORTGAGE_RATE_FIXED,
    SBT_RATE,
    STAMP_DUTY_RATE,
    TRANSFER_FEE_RATE,
)
from models_v2 import FinancialMetrics, InvestorProfile, PropertyResult

# Opportunity cost benchmarks (annualised returns)
OPPORTUNITY_COST_BENCHMARKS: dict[str, float] = {
    "SET": 0.10,
    "thai_bonds": 0.03,
    "REITs": 0.07,
}

# Bangkok cycle: current YoY appreciation assumption
BKK_ANNUAL_APPRECIATION = -0.03  # -3%

# Operating expense ratio applied to gross rent
OPERATING_EXPENSE_RATIO = 0.35  # 65% passes through as net income

# Default vacancy rate
DEFAULT_VACANCY_RATE = 0.08  # 8%

# Insurance estimate as % of price per year
INSURANCE_RATE_ANNUAL = 0.001  # 0.1% of purchase price

# Property tax estimate as % of appraised value per year
PROPERTY_TAX_RATE_ANNUAL = 0.02 * 0.125  # 2% appraised × 12.5% land-and-building rate → 0.25%


def _monthly_mortgage_payment(principal: float, annual_rate: float, term_years: int = 30) -> float:
    """Standard amortising mortgage monthly payment."""
    monthly_rate = annual_rate / 12
    n = term_years * 12
    if monthly_rate == 0:
        return principal / n
    return principal * (monthly_rate * (1 + monthly_rate) ** n) / ((1 + monthly_rate) ** n - 1)


def _estimate_annual_opex(price: float, size_sqm: Optional[float]) -> float:
    """Estimate annual operating expenses: CAM + insurance + property tax."""
    cam_sqm = size_sqm if size_sqm else 35.0  # default studio size
    cam_annual = cam_sqm * CAM_DEFAULT_SQM * 12
    insurance_annual = price * INSURANCE_RATE_ANNUAL
    property_tax_annual = price * PROPERTY_TAX_RATE_ANNUAL
    return cam_annual + insurance_annual + property_tax_annual


def _exit_tax_pct(profile: InvestorProfile) -> float:
    """Return the effective exit tax rate given investor profile."""
    if profile.entity_type == "company":
        return SBT_RATE
    if profile.hold_horizon_years < 5:
        if profile.tabien_baan:
            return 0.0  # SBT exemption
        return SBT_RATE
    return STAMP_DUTY_RATE


def _tax_recommendation(profile: InvestorProfile) -> str:
    if profile.entity_type == "company":
        return "corporate_always_sbt"
    if profile.hold_horizon_years >= 5:
        return "personal_5yr_plus"
    if profile.tabien_baan:
        return "personal_tabien_baan"
    return "personal_short_hold_sbt"


def compute_financial_overlay(
    result: PropertyResult,
    profile: InvestorProfile,
) -> FinancialMetrics:
    """
    Compute financial engineering metrics for a screened NPA property.

    Returns FinancialMetrics. Income-dependent fields are None when
    market_rent_median is unavailable on the candidate.
    """
    candidate = result.candidate
    price = candidate.price_baht
    size_sqm = candidate.size_sqm
    monthly_rent: Optional[float] = (
        float(candidate.market_rent_median) if candidate.market_rent_median else None
    )

    # --- Derived inputs ---
    renovation_cost = price * profile.renovation_budget_pct
    acquisition_costs = price * (TRANSFER_FEE_RATE + 0.01)  # transfer fee + legal
    total_acquisition_cost = price + renovation_cost + acquisition_costs

    exit_tax_rate = _exit_tax_pct(profile)
    exit_costs = price * (exit_tax_rate + TRANSFER_FEE_RATE)

    # --- Mortgage ---
    loan_amount = price * profile.ltv_pct
    equity = price * (1.0 - profile.ltv_pct) + acquisition_costs + renovation_cost
    monthly_payment: Optional[float] = None
    annual_debt_service: float = 0.0
    if profile.purchase_mode == "mortgage" and loan_amount > 0:
        monthly_payment = _monthly_mortgage_payment(
            loan_amount, profile.mortgage_rate
        )
        annual_debt_service = monthly_payment * 12

    # --- Operating expenses ---
    opex_annual = _estimate_annual_opex(price, size_sqm)

    # --- Hold cost monthly ---
    hold_cost_monthly: Optional[float] = (
        (monthly_payment or 0.0)
        + (opex_annual / 12)
    )

    # --- Income-dependent metrics ---
    irr_pct: Optional[float] = None
    irr_vs_benchmark: str = ""
    cocr_pct: Optional[float] = None
    dscr: Optional[float] = None
    break_even_occupancy_pct: Optional[float] = None

    if monthly_rent is not None:
        gross_rent_annual = monthly_rent * 12 * (1.0 - DEFAULT_VACANCY_RATE)
        net_income_annual = gross_rent_annual * (1.0 - OPERATING_EXPENSE_RATIO)

        # IRR approximation (simplified single-period)
        annual_appreciation_gain = BKK_ANNUAL_APPRECIATION * price
        annualised_exit_cost = exit_costs / max(profile.hold_horizon_years, 1)
        annualised_acquisition_cost = acquisition_costs / max(profile.hold_horizon_years, 1)
        irr_numerator = (
            net_income_annual
            + annual_appreciation_gain
            - annualised_exit_cost
            - annualised_acquisition_cost
        )
        irr_pct = irr_numerator / equity if equity > 0 else None

        if irr_pct is not None:
            irr_vs_benchmark = (
                "above_benchmark" if irr_pct >= IRR_BENCHMARK else "below_benchmark"
            )

        # Cash-on-cash return
        if profile.purchase_mode == "mortgage" and annual_debt_service > 0:
            cocr_pct = (net_income_annual - annual_debt_service) / equity if equity > 0 else None
        else:
            # Cash buyer: CoCR = NOI / total equity deployed
            cocr_pct = net_income_annual / equity if equity > 0 else None

        # DSCR (skip for cash buyers)
        if profile.purchase_mode == "mortgage" and annual_debt_service > 0:
            noi = gross_rent_annual - opex_annual
            dscr = noi / annual_debt_service

        # Break-even occupancy
        potential_gross = monthly_rent * 12
        fixed_costs = opex_annual + annual_debt_service
        break_even_occupancy_pct = fixed_costs / potential_gross if potential_gross > 0 else None

    # --- Opportunity cost comparison ---
    opportunity_cost_comparison = dict(OPPORTUNITY_COST_BENCHMARKS)

    return FinancialMetrics(
        irr_pct=round(irr_pct, 4) if irr_pct is not None else None,
        irr_vs_benchmark=irr_vs_benchmark,
        cocr_pct=round(cocr_pct, 4) if cocr_pct is not None else None,
        dscr=round(dscr, 4) if dscr is not None else None,
        break_even_occupancy_pct=(
            round(break_even_occupancy_pct, 4) if break_even_occupancy_pct is not None else None
        ),
        hold_cost_monthly=round(hold_cost_monthly, 2) if hold_cost_monthly is not None else None,
        total_acquisition_cost=round(total_acquisition_cost, 2),
        exit_tax_pct=round(exit_tax_rate, 4),
        tax_recommendation=_tax_recommendation(profile),
        opportunity_cost_comparison=opportunity_cost_comparison,
    )

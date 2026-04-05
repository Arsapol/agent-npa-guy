"""
Shared constants for Multi-Strategy NPA Screener v2.

All values validated through 5-agent research + cross-debate (2026-04-05).
See shared-contracts.md for sources and rationale.
"""

# --- Verified Market Price Adjustments ---
VERIFIED_SALE_MULTIPLIER = 0.92  # Listed sale median → transaction price
VERIFIED_RENT_BARE = 0.85  # Listed rent → bare unit transaction rent
VERIFIED_RENT_FURNISHED = 1.0  # Listed rent → furnished unit (no haircut)

# --- Default Building Costs ---
CAM_DEFAULT_SQM = 55  # THB/sqm/month (median of rental 60 + flip 50)

# --- Financial Benchmarks ---
EQUITY_COST = 0.07  # Opportunity cost: SET 10% risk-adjusted
IRR_BENCHMARK = 0.16  # SET 10% + concentration 3% + illiquidity 3%

# --- Thai Tax Rates ---
SBT_RATE = 0.033  # Specific Business Tax (sell within 5 years)
STAMP_DUTY_RATE = 0.005  # Stamp duty (sell after 5 years, personal only)
TRANSFER_FEE_RATE = 0.02  # Transfer fee (2% of appraised or sale, whichever higher)
WHT_RATE = 0.03  # Withholding tax

# --- Mortgage Parameters ---
MORTGAGE_RATE_FIXED = 0.03  # Years 1-3 typical Thai bank rate
MORTGAGE_RATE_FLOAT = 0.06  # Years 4+ floating rate

# --- Financial Pre-Filter Thresholds ---
COCR_MIN = 0.05  # Minimum cash-on-cash return (leveraged)
DSCR_MIN = 1.25  # Minimum debt service coverage ratio
DSCR_STRESS_BPS = 200  # Rate stress test: +200bps above current

# --- Rental Adjustments ---
SEASONAL_ADJUSTMENT_Q2 = 1.12  # April-June rent uplift for university areas
SUMMER_VACANCY_FACTOR = 0.75  # Tier C university 3-month vacancy

# --- Hospitality ---
OPERATING_COST_HOSPITALITY = 0.53  # FinEng-corrected operating cost ratio

# --- Renovation Cost Benchmarks (THB/sqm) ---
RENO_COST_COSMETIC_MIN = 5000
RENO_COST_COSMETIC_MAX = 8000
RENO_COST_HOSPITALITY_MIN = 18000
RENO_COST_HOSPITALITY_MAX = 25000
RENO_MAX_PCT = 0.20  # Max renovation as % of purchase price

# --- Strategy Thresholds (cycle-adjusted: mid-fall +5%) ---
DISCOUNT_TIER_A = 0.20  # Was 0.15, raised for mid-fall cycle
DISCOUNT_TIER_B = 0.25  # Was 0.20
DISCOUNT_TIER_C = 0.30  # Was 0.25

YIELD_TIER_A = 0.06
YIELD_TIER_B = 0.07
YIELD_TIER_C = 0.08

# --- NPA Vintage (months) ---
NPA_VINTAGE_SWEET_SPOT = (12, 36)  # Motivated seller, legal clarity
NPA_VINTAGE_STALE = 36  # Require 40%+ discount + legal audit

# --- Flip Thresholds ---
FLIP_QUICK_MIN_DISCOUNT = 0.35
FLIP_MEDIUM_MIN_DISCOUNT = 0.25
FLIP_MIN_NET_MARGIN = 0.15
FLIP_MIN_ANNUALIZED_RETURN = 0.15  # Above SET + illiquidity
FLIP_MAX_ABSORPTION_MONTHS = 36  # Quick flip reject above this

# --- Supply Pressure ---
SUPPLY_PRESSURE_SEVERE = 25.0  # % of units for sale → auto-reject
SUPPLY_PRESSURE_HIGH = 15.0
SUPPLY_PRESSURE_MODERATE = 10.0

# --- NPA Concentration (calibrated to BKK avg ~214 per 1km circle) ---
NPA_CONCENTRATION_VERY_HIGH = 400
NPA_CONCENTRATION_HIGH = 250
NPA_CONCENTRATION_NORMAL = 100

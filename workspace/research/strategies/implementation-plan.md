# Multi-Strategy NPA Screener v2 — Implementation Plan

**Date:** 2026-04-05 | **Status:** AWAITING USER APPROVAL

## Architecture

```
Property → Financial Pre-Filter (5 gates) → Strategy Router → Per-Strategy Scoring → Cascade → Ranked Output
```

## Layer 1: Financial Pre-Filter (ALL properties)

| Gate | Formula | Action |
|------|---------|--------|
| Entry discount < exit costs + 10% | `discount_pct < (SBT + transfer + WHT) + 10` | REJECT |
| CoCR < 5% (leveraged) | `net_income / cash_invested < 0.05` | REJECT |
| DSCR < 1.25 (income strategies) | `net_income / debt_service < 1.25` | REJECT |
| DSCR < 1.0 at +200bps | stress test at current_rate + 2% | FLAG |
| IRR < 16% (benchmark) | full cashflow model vs SET+illiquidity premium | FLAG (user decides) |

## Layer 2: Strategy Router

Each property scored against ALL viable strategies based on property type:

| Strategy | Property Types | Key Metrics |
|----------|---------------|-------------|
| **RENT** | Condo | NRY >= 3.5% (cash) or CoCR >= tier min (leveraged), rent haircut 85% (bare) / 100% (furnished), DAS >= 40, seasonal adjustment |
| **FLIP** | Condo, House | Absorption < 36mo, discount >= 35% (quick) / 25% (medium), net margin >= 15%, 2 sold comparables required |
| **LAND BANK** | Land, House+Land | Confirmed infrastructure within 3yr, LPMI direction, HCB with 7% equity cost, discount >= 15% vs REIC |
| **RENO/HOSPITALITY** | Condo (30+ day only), House/Villa (STR OK) | Legal Compliance Score >= 3, RROI >= 20% (after 53% cost stack), renovation <= 20% of purchase |

## Layer 3: Cascade Logic

```
Score property against all viable strategies
If FLIP fails → try RENT (failed flip = long-hold rental candidate)
If RENT fails bare → try RENT furnished (renovation premium)
If condo STR → HARD REJECT (Hotel Act B.E. 2547)
If house/villa STR → score RENO/HOSPITALITY
Flag "DUAL-STRATEGY" if both RENT >= 55 AND FLIP >= 55
```

## Layer 4: Financial Engineering Overlay

- Cash vs Leveraged scoring (parallel tracks)
- Tax optimization recommendations (personal vs corporate, tabien baan flag)
- Hold period optimization (SBT crossover at 5yr)
- IRR vs 16% benchmark display
- Opportunity cost comparison (vs SET index, Thai bonds, REITs)

## Shared Constants (from debate consensus)

| Constant | Value | Source |
|----------|-------|--------|
| Verified sale price | Listed median x 0.92 | Debate: rental + flip agreed |
| Verified rent (bare) | Listed median x 0.85 | Debate: rental researcher |
| Verified rent (furnished) | Listed median x 1.00-1.15 | Debate: reno researcher |
| CAM fee default | 55 THB/sqm/month | Median of rental (60) + flip (50) |
| Equity opportunity cost | 7% | FinEng: SET + illiquidity premium basis |
| Minimum IRR benchmark | 16% | FinEng: SET 10% + concentration 3% + illiquidity 3% |
| SBT crossover | 5 years | Personal: SBT 3.3% (<5yr) vs stamp duty 0.5% (>=5yr) |
| Renovation cost (cosmetic) | 5,000-8,000 THB/sqm | Flip researcher |
| Renovation cost (hospitality) | 18,000-25,000 THB/sqm | Reno researcher |
| Operating cost stack (hospitality) | 53% of gross | FinEng: corrected from reno's 37.5% |
| Mortgage rate assumption | 3% fixed (yr 1-3), 6% floating (yr 4+) | FinEng |

## Key Design Decisions (from debate)

| Issue | Resolution |
|-------|-----------|
| NRY vs CoCR conflict | Parallel gates: pass EITHER NRY >= 3.5% (cash) OR CoCR >= tier min (leveraged with DSCR > 1.25) |
| Rent haircut bare vs furnished | Two tracks: 85% (bare NPA unit), 100-115% (post-renovation furnished) |
| Land banking opportunity cost | Use 7% equity cost, not 1% BoT rate |
| Quick flip timeline | LED/SAM cannot make June 2026 transfer deadline — BAM/JAM/KBank only |
| STR on condos | HARD REJECT. Hotel Act B.E. 2547. Houses/villas OK with license |
| Renovation flip vs hospitality | Score renovation flip FIRST, cascade to hospitality if flip absorption > 45mo |
| GRY-pass/NRY-fail contradiction | Raised GRY floors: Tier B uni 7->8%. NRY is primary gate, GRY secondary |
| Double-counting rent haircut | Fixed: listed x 0.85 x 12 months. Vacancy is separate line item |
| Seasonal rent adjustment | x1.12 if queried April-June (off-season for university areas) |
| Tabien baan | Global investor profile input, not per-strategy |
| Provider appraisal vs govt appraisal | Land Dept (กรมธนารักษ์) valid for tax calc. Provider appraisals never trusted for pricing. |

## Data Gaps to Fill

| Gap | Source | Priority |
|-----|--------|----------|
| Actual sold transaction prices | REIC quarterly, Land Dept | HIGH |
| Building-level occupancy | Juristic office queries, lights-on survey | HIGH (manual) |
| Renovation cost by building | KB ingestion from contractor quotes | MEDIUM |
| Airbnb ADR/occupancy by district | AirDNA or scrape Airbnb | MEDIUM |
| Infrastructure project geometries | MRTA, DOH websites | MEDIUM |
| School enrollment numbers | MOE data | LOW |
| RentHub.in.th listings | New scraper needed | LOW |

## Investor Profile Input (new)

The screener needs an investor profile input to customize scoring:

```python
@dataclass
class InvestorProfile:
    purchase_mode: str  # "cash" | "mortgage"
    ltv_pct: float  # 0.0 for cash, 0.7-1.0 for mortgage
    mortgage_rate: float  # e.g. 0.03
    hold_horizon_years: int  # 1-10
    entity_type: str  # "personal" | "company"
    tabien_baan: bool  # will register residence in unit?
    renovation_budget: float  # 0 = no reno, or THB amount
    strategies: list[str]  # ["rent", "flip", "land_bank", "hospitality"] or ["all"]
    risk_tolerance: str  # "conservative" | "moderate" | "aggressive"
```

## Build Phases

| Phase | What | Effort |
|-------|------|--------|
| **Phase 1** | Financial pre-filter (5 gates) + rent haircut fix + leverage CoCR parallel track + InvestorProfile input | 1 day |
| **Phase 2** | Strategy router: RENT + FLIP scoring with cascade logic | 1-2 days |
| **Phase 3** | LAND BANK + RENO/HOSPITALITY scoring | 1 day |
| **Phase 4** | Financial engineering overlay (IRR, tax optimizer, hold period) | 1 day |
| **Phase 5** | Output: multi-strategy ranked report with per-property strategy recommendations | 0.5 day |

## Research Artifacts

All reports and debate critiques saved at:
- `workspace/research/strategies/rental-strategy.md`
- `workspace/research/strategies/flip-strategy.md`
- `workspace/research/strategies/land-banking-strategy.md`
- `workspace/research/strategies/renovation-hospitality-strategy.md`
- `workspace/research/strategies/financial-engineering.md`
- `workspace/research/strategies/debate-financial-engineering-critique.md`
- `workspace/research/strategies/reno-debate-critique.md`

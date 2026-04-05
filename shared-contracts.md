# Shared Contracts — Multi-Strategy NPA Screener v2

> **RULE: ONLY this file defines shared identifiers. No agent may invent new ones.**

## File Paths

| File | Purpose | Used by |
|------|---------|---------|
| `workspace/skills/npa-screener/scripts/models_v2.py` | All shared Pydantic models | ALL stories |
| `workspace/skills/npa-screener/scripts/constants.py` | All shared constants | ALL stories |
| `workspace/skills/npa-screener/scripts/financial_prefilter.py` | 5 financial gates | story-002, story-007 |
| `workspace/skills/npa-screener/scripts/strategy_rent.py` | Rental strategy scorer | story-003, story-007 |
| `workspace/skills/npa-screener/scripts/strategy_flip.py` | Flip strategy scorer | story-004, story-007 |
| `workspace/skills/npa-screener/scripts/strategy_landbank.py` | Land banking scorer | story-005, story-007 |
| `workspace/skills/npa-screener/scripts/strategy_hospitality.py` | Reno/hospitality scorer | story-006, story-007 |
| `workspace/skills/npa-screener/scripts/strategy_router.py` | Strategy router + cascade | story-007, story-011 |
| `workspace/skills/npa-screener/scripts/financial_overlay.py` | Financial engineering layer | story-008, story-011 |
| `workspace/skills/npa-screener/scripts/report_v2.py` | Output formatter | story-010, story-011 |
| `workspace/skills/npa-screener/scripts/screener_v2.py` | Main CLI entry point | story-011 |
| `workspace/skills/npa-screener/scripts/screener.py` | EXISTING v1 screener (READ ONLY — reuse functions, do not modify) | story-009, story-011 |

## Shared Constants (constants.py)

| Name | Value | Source | Used by |
|------|-------|--------|---------|
| `VERIFIED_SALE_MULTIPLIER` | `0.92` | Debate: rental + flip agreed | strategy_rent, strategy_flip |
| `VERIFIED_RENT_BARE` | `0.85` | Debate: rental researcher | strategy_rent, strategy_hospitality |
| `VERIFIED_RENT_FURNISHED` | `1.0` | Debate: reno researcher | strategy_rent, strategy_hospitality |
| `CAM_DEFAULT_SQM` | `55` | Median of rental (60) + flip (50) | ALL strategy scorers |
| `EQUITY_COST` | `0.07` | FinEng: SET + illiquidity premium | strategy_landbank, financial_overlay |
| `IRR_BENCHMARK` | `0.16` | FinEng: SET 10% + concentration 3% + illiquidity 3% | financial_prefilter, financial_overlay |
| `SBT_RATE` | `0.033` | Thai Specific Business Tax | financial_prefilter, financial_overlay |
| `STAMP_DUTY_RATE` | `0.005` | Thai stamp duty (hold >= 5yr) | financial_overlay |
| `TRANSFER_FEE_RATE` | `0.02` | Thai transfer fee | financial_prefilter, financial_overlay |
| `WHT_RATE` | `0.03` | Withholding tax | financial_prefilter, financial_overlay |
| `MORTGAGE_RATE_FIXED` | `0.03` | Years 1-3 typical | financial_prefilter, financial_overlay |
| `MORTGAGE_RATE_FLOAT` | `0.06` | Years 4+ typical | financial_overlay |
| `COCR_MIN` | `0.05` | Minimum cash-on-cash return | financial_prefilter |
| `DSCR_MIN` | `1.25` | Minimum debt service coverage | financial_prefilter |
| `DSCR_STRESS_BPS` | `200` | Rate stress test (bps above current) | financial_prefilter |
| `SEASONAL_ADJUSTMENT_Q2` | `1.12` | April-June university rent uplift | strategy_rent |
| `SUMMER_VACANCY_FACTOR` | `0.75` | Tier C university effective yield | strategy_rent |
| `OPERATING_COST_HOSPITALITY` | `0.53` | FinEng-corrected (was 0.375) | strategy_hospitality |
| `RENO_COST_COSMETIC_MIN` | `5000` | THB/sqm | strategy_flip, strategy_hospitality |
| `RENO_COST_COSMETIC_MAX` | `8000` | THB/sqm | strategy_flip |
| `RENO_COST_HOSPITALITY_MIN` | `18000` | THB/sqm | strategy_hospitality |
| `RENO_COST_HOSPITALITY_MAX` | `25000` | THB/sqm | strategy_hospitality |
| `RENO_MAX_PCT` | `0.20` | Max renovation as % of purchase | ALL strategy scorers |

## Shared Models (models_v2.py)

### InvestorProfile

```python
class InvestorProfile(BaseModel):
    model_config = ConfigDict(frozen=True)
    
    purchase_mode: Literal["cash", "mortgage"]  # "cash" | "mortgage"
    ltv_pct: float = 0.0  # 0.0 for cash, 0.7-1.0 for mortgage
    mortgage_rate: float = MORTGAGE_RATE_FIXED
    hold_horizon_years: int = 5  # 1-10
    entity_type: Literal["personal", "company"] = "personal"
    tabien_baan: bool = False  # will register residence in unit?
    renovation_budget_pct: float = 0.0  # 0 = no reno, or % of purchase price (e.g. 0.10 = 10%)
    strategies: list[str] = ["all"]  # ["rent", "flip", "land_bank", "hospitality"] or ["all"]
    risk_tolerance: Literal["conservative", "moderate", "aggressive"] = "moderate"
```

### PropertyType (Enum)

```python
class PropertyType(str, Enum):
    CONDO = "condo"
    HOUSE = "house"
    TOWNHOUSE = "townhouse"
    LAND = "land"
    HOUSE_AND_LAND = "house_and_land"
    COMMERCIAL = "commercial"
```

### Strategy (Enum)

```python
class Strategy(str, Enum):
    RENT = "rent"
    FLIP = "flip"
    LAND_BANK = "land_bank"
    HOSPITALITY = "hospitality"
```

### NpaCandidate (extended from v1)

```python
class NpaCandidate(BaseModel):
    """Extended from v1 screener dataclass — now includes property type, NPA vintage, auction rounds."""
    model_config = ConfigDict(frozen=True)
    
    # Identity
    source: str  # LED, SAM, BAM, JAM, KTB, KBANK
    source_id: str
    property_type: PropertyType
    project_name: str = ""
    
    # Location
    province: str = ""
    district: str = ""
    subdistrict: str = ""
    lat: float | None = None
    lon: float | None = None
    
    # Price & size
    price_baht: float
    size_sqm: float | None = None
    price_sqm: float | None = None
    
    # Building info
    bedroom: int | None = None
    bathroom: int | None = None
    floor: str | None = None
    building_age: int | None = None  # KBank only
    
    # NPA-specific
    npa_vintage_months: int | None = None  # months since first_seen_at
    auction_round: int | None = None  # LED only
    
    # Market enrichment (filled by enrich step)
    market_price_sqm: int | None = None
    market_confidence: str = "none"
    market_year_built: int | None = None
    market_total_units: int | None = None
    market_developer: str | None = None
    market_rent_median: int | None = None
    market_units_for_sale: int | None = None
    market_units_for_rent: int | None = None
    market_project_name: str | None = None
    supply_pressure_pct: float | None = None
    
    # Proximity (filled by proximity step)
    nearest_anchor_name: str | None = None
    nearest_anchor_type: str | None = None
    nearest_anchor_dist_m: float | None = None
    nearest_anchor_enrollment: int | None = None
    nearest_bts_name: str | None = None
    nearest_bts_dist_m: float | None = None
    bts_tier: str = ""
    
    # Computed
    real_discount_pct: float | None = None
    verified_price_sqm: float | None = None  # market_price_sqm * VERIFIED_SALE_MULTIPLIER
```

### StrategyScore

```python
class StrategyScore(BaseModel):
    model_config = ConfigDict(frozen=True)
    
    strategy: Strategy
    sub_strategy: str = ""  # e.g. "quick_flip", "medium_hold", "serviced_apt"
    score: float  # 0-100
    verdict: Literal["STRONG_BUY", "BUY", "WATCH", "AVOID"]
    key_metrics: dict[str, float | None]  # strategy-specific metric values
    flags: list[str] = []
    reject_reasons: list[str] = []
    pass_gates: bool = True
```

### FinancialMetrics

```python
class FinancialMetrics(BaseModel):
    model_config = ConfigDict(frozen=True)
    
    irr_pct: float | None = None
    irr_vs_benchmark: str = ""  # "ABOVE" | "BELOW" | "N/A"
    cocr_pct: float | None = None
    dscr: float | None = None
    break_even_occupancy_pct: float | None = None
    hold_cost_monthly: float | None = None
    total_acquisition_cost: float | None = None  # price + reno + transfer + arrears
    exit_tax_pct: float | None = None  # SBT or stamp duty depending on hold
    tax_recommendation: str = ""  # "personal_5yr+" | "personal_tabien_baan" | "corporate"
    opportunity_cost_comparison: dict[str, float] = {}  # {"SET": 0.10, "bonds": 0.03, "REITs": 0.07}
```

### PreFilterResult

```python
class PreFilterResult(BaseModel):
    model_config = ConfigDict(frozen=True)
    
    pass_all: bool
    gates: dict[str, bool]  # gate_name -> pass/fail
    flags: list[str] = []
    reject_reasons: list[str] = []
```

### PropertyResult

```python
class PropertyResult(BaseModel):
    model_config = ConfigDict(frozen=True)
    
    candidate: NpaCandidate
    prefilter: PreFilterResult
    strategy_scores: dict[Strategy, StrategyScore]
    best_strategy: Strategy | None = None
    best_score: float = 0.0
    financial: FinancialMetrics | None = None
    is_dual_strategy: bool = False
    dual_strategies: list[Strategy] = []
    cascade_path: list[str] = []  # e.g. ["flip_failed", "rent_bare_failed", "rent_furnished_pass"]
```

## Strategy-Eligible Property Types

| Strategy | CONDO | HOUSE | TOWNHOUSE | LAND | HOUSE_AND_LAND | COMMERCIAL |
|----------|-------|-------|-----------|------|----------------|------------|
| RENT | Yes | Yes | Yes | No | No | No |
| FLIP | Yes | Yes | Yes | No | Yes | No |
| LAND_BANK | No | No | No | Yes | Yes | No |
| HOSPITALITY (30+ day) | Yes | Yes | Yes | No | Yes | No |
| HOSPITALITY (STR <30d) | **NO (Hotel Act)** | Yes | Yes | No | Yes | No |

## Function Signatures

| Function | File | Signature | Returns |
|----------|------|-----------|---------|
| `financial_prefilter` | `financial_prefilter.py` | `(candidate: NpaCandidate, profile: InvestorProfile) -> PreFilterResult` | PreFilterResult |
| `score_rental` | `strategy_rent.py` | `(candidate: NpaCandidate, profile: InvestorProfile) -> StrategyScore` | StrategyScore |
| `score_flip` | `strategy_flip.py` | `(candidate: NpaCandidate, profile: InvestorProfile) -> StrategyScore` | StrategyScore |
| `score_landbank` | `strategy_landbank.py` | `(candidate: NpaCandidate, profile: InvestorProfile) -> StrategyScore` | StrategyScore |
| `score_hospitality` | `strategy_hospitality.py` | `(candidate: NpaCandidate, profile: InvestorProfile) -> StrategyScore` | StrategyScore |
| `route_and_score` | `strategy_router.py` | `(candidate: NpaCandidate, profile: InvestorProfile) -> PropertyResult` | PropertyResult |
| `compute_financial_overlay` | `financial_overlay.py` | `(result: PropertyResult, profile: InvestorProfile) -> FinancialMetrics` | FinancialMetrics |
| `extract_all_properties` | `screener_v2.py` | `(conn, provinces: list[str], max_price: float | None, property_types: list[PropertyType] | None) -> list[NpaCandidate]` | list[NpaCandidate] |
| `format_report_v2` | `report_v2.py` | `(results: list[PropertyResult], profile: InvestorProfile, top_n: int) -> str` | markdown string |
| `export_json_v2` | `report_v2.py` | `(results: list[PropertyResult], path: str) -> None` | None |

## Cascade Logic (strategy_router.py)

```
1. Determine eligible strategies from PropertyType × InvestorProfile.strategies
2. Run financial_prefilter → if REJECT, return early with AVOID
3. For each eligible strategy, compute score
4. CASCADE RULES:
   a. If FLIP score < 55 AND RENT eligible → score RENT (note: "failed_flip_to_rent")
   b. If RENT bare score < 55 AND renovation_budget > 0 → re-score RENT furnished (note: "bare_to_furnished")
   c. If CONDO + hospitality requested → only score 30+ day (serviced apt), NEVER STR
   d. If HOUSE/VILLA + hospitality → score all sub-types including STR
5. DUAL flag: if rent_score >= 55 AND flip_score >= 55 → is_dual_strategy = True
6. best_strategy = strategy with highest score among those with verdict != AVOID
```

## Existing Code to Reuse (from screener.py v1)

| Function | What it does | Reuse in |
|----------|-------------|----------|
| `enrich_with_market_data()` | Batch trigram match to Hipflat/PropertyHub/ZMyHome | story-011 (call directly) |
| `compute_proximity()` | Haversine to education anchors + BTS/MRT | story-011 (call directly) |
| `EDUCATION_ANCHORS` | Lat/lon list of universities + schools | story-003 (import) |
| `TRANSIT_STATIONS` | Lat/lon list of BTS/MRT/ARL | story-003, story-004 |
| `TIER1_DEVELOPERS`, `TIER2_DEVELOPERS` | Developer name sets | story-003, story-004 |
| `haversine_m()` | Distance calculation | ALL (import from screener.py) |

## Database Tables Referenced

| Table | Used for | Stories |
|-------|----------|---------|
| `sam_properties` | NPA extraction | story-009 |
| `bam_properties` | NPA extraction | story-009 |
| `jam_properties` | NPA extraction | story-009 |
| `ktb_properties` | NPA extraction | story-009 |
| `kbank_properties` | NPA extraction (has building_age) | story-009 |
| `properties` + `led_properties` | LED NPA extraction (has auction_round) | story-009 |
| `hipflat_projects` | Market enrichment, YoY trend | story-011 (via enrich) |
| `propertyhub_projects` + `propertyhub_listings` | Market enrichment | story-011 (via enrich) |
| `zmyhome_projects` + `zmyhome_listings` | Market enrichment | story-011 (via enrich) |

## Research Reports (reference for metric implementations)

| Report | Strategy |
|--------|----------|
| `workspace/research/strategies/rental-strategy.md` | RENT metrics M1-M11 |
| `workspace/research/strategies/flip-strategy.md` | FLIP metrics + 3 scenarios |
| `workspace/research/strategies/land-banking-strategy.md` | LAND_BANK 7 metrics |
| `workspace/research/strategies/renovation-hospitality-strategy.md` | HOSPITALITY metrics + legal gates |
| `workspace/research/strategies/financial-engineering.md` | IRR, CoCR, DSCR, tax formulas |
| `workspace/research/strategies/debate-financial-engineering-critique.md` | Corrections to all strategies |

## Contract Rules

1. **ONLY this file defines shared identifiers.** No agent may invent new model names, function signatures, or file paths.
2. **All strategy scorers return `StrategyScore`.** No custom return types.
3. **All constants come from `constants.py`.** No hardcoded magic numbers in strategy files.
4. **Import shared functions from `screener.py`** (haversine_m, EDUCATION_ANCHORS, etc.) — do NOT duplicate.
5. **Provider appraisals are NEVER trusted for pricing.** Only `market_price_sqm * VERIFIED_SALE_MULTIPLIER` is used.
6. **Land Dept appraisal (กรมธนารักษ์) IS valid** for tax calculation only.
7. **Condo + STR = HARD REJECT.** No exceptions. Hotel Act B.E. 2547.

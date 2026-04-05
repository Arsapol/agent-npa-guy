---
name: analyze
description: Run structured analysis (financial, property, data) using the hybrid ralph pattern. Decomposes research questions into parallel investigation tracks with verification.
---

# Analysis Orchestrator

Run structured, multi-angle analysis using Agent Teams for hypothesis generation and Ralph loops for data crunching.

## Process

### Phase 1: Define the Analysis Brief

Interview the user about:
- **What** they want to analyze (specific stock, portfolio, property, dataset)
- **Why** — what decision does this inform? (buy/sell, invest, allocate, compare)
- **Data sources** — what data is available? (APIs, CSVs, databases, web)
- **Output format** — report, spreadsheet, dashboard, or just a summary?
- **Time constraints** — historical period, deadline for the analysis

### Phase 2: Generate analysis.json

Decompose the analysis into tasks, just like prd.json but for research:

```json
{
  "analysis": "Portfolio Risk Assessment Q1 2026",
  "branchName": "analysis/portfolio-risk-q1",
  "description": "Comprehensive risk analysis of current portfolio positions",
  "objective": "Determine if portfolio is overexposed to any single sector or risk factor",
  "tasks": [
    {
      "id": "task-001",
      "title": "Gather position data",
      "description": "Pull current holdings, cost basis, and market values",
      "priority": 1,
      "passes": false,
      "acceptance_criteria": [
        "All positions exported to data/positions.csv",
        "Data includes: ticker, shares, cost_basis, current_price, sector",
        "Totals reconcile with known portfolio value within 1%"
      ],
      "track": "mechanical",
      "dependencies": []
    },
    {
      "id": "task-002",
      "title": "Calculate sector concentration",
      "description": "Compute allocation percentages by sector and identify overweight positions",
      "priority": 2,
      "passes": false,
      "acceptance_criteria": [
        "Sector allocations sum to 100%",
        "Any sector > 30% flagged as overweight",
        "Results saved to output/sector-analysis.md"
      ],
      "track": "mechanical",
      "dependencies": ["task-001"]
    },
    {
      "id": "task-003",
      "title": "Interpret results and form recommendations",
      "description": "Analyze the findings, compare to benchmarks, and draft actionable recommendations",
      "priority": 3,
      "passes": false,
      "acceptance_criteria": [
        "Recommendations are specific and actionable",
        "Each recommendation cites supporting data",
        "Risk/reward tradeoffs discussed"
      ],
      "track": "creative",
      "dependencies": ["task-002"]
    }
  ]
}
```

### Phase 3: Track Assignment for Analysis

**Mechanical tasks** (Ralph loop):
- Data gathering and cleaning
- Calculations (ratios, returns, correlations, projections)
- Backtesting with defined parameters
- Generating charts and tables
- Validation (numbers reconcile, formulas correct)

**Creative tasks** (Agent Teams):
- Interpreting results — what do the numbers mean?
- Forming hypotheses — why did X happen?
- Comparing scenarios — which approach is better and why?
- Writing narrative analysis — executive summary, recommendations
- Challenging assumptions — devil's advocate on the findings

### Phase 4: Execution

For **mechanical tasks**, modify ralph.sh to use analysis.json instead of prd.json:
```bash
PRD_FILE="analysis.json" ./scripts/ralph.sh 10
```

For **creative tasks**, spawn an Agent Team:
```
Create an agent team for analysis interpretation:
- Analyst: Interprets data, identifies trends, forms hypotheses
- Skeptic: Challenges assumptions, finds flaws in reasoning, checks for biases
- Strategist: Translates findings into actionable recommendations

All agents must cite specific data points from the mechanical track outputs.
```

### Phase 5: Compile Report

After both tracks complete, compile findings into a final report:
- Executive summary (2-3 paragraphs)
- Key findings with supporting data
- Visualizations (charts, tables)
- Recommendations with confidence levels
- Methodology and data sources
- Caveats and limitations

Save as `output/analysis-report.md` or use the `/docx` skill for a formatted Word document.

## Analysis Templates

### Stock Analysis
```
/analyze AAPL

Tasks generated:
1. [mechanical] Pull 12-month price history and compute returns
2. [mechanical] Calculate key ratios (P/E, P/B, EV/EBITDA, FCF yield)
3. [mechanical] Compute technical indicators (RSI, MACD, moving averages)
4. [mechanical] Pull and parse latest earnings transcript
5. [creative] Compare valuation vs sector peers — is it cheap or expensive?
6. [creative] Assess competitive moat and growth catalysts
7. [creative] Bull/bear case with price targets
8. [creative] Final recommendation with confidence level
```

### Property Investment Analysis
```
/analyze "Condo at 123 Main St, $500K asking"

Tasks generated:
1. [mechanical] Calculate rental yield (gross and net)
2. [mechanical] Compute cash-on-cash return with financing scenarios
3. [mechanical] Model 5/10/15 year appreciation scenarios (conservative, base, bull)
4. [mechanical] Calculate break-even occupancy rate
5. [mechanical] Pull comparable sales and rental comps from area
6. [creative] Assess location quality (transit, amenities, growth trajectory)
7. [creative] Identify risks (vacancy, maintenance, market downturn, regulation)
8. [creative] Compare vs alternative investments (index funds, REITs, other properties)
9. [creative] Final recommendation: buy / negotiate / pass
```

### Portfolio Review
```
/analyze portfolio

Tasks generated:
1. [mechanical] Export all positions with cost basis
2. [mechanical] Calculate P&L (realized + unrealized) by position
3. [mechanical] Compute risk metrics (Sharpe, max drawdown, beta, correlation matrix)
4. [mechanical] Analyze sector/geography concentration
5. [creative] Identify portfolio weaknesses and blind spots
6. [creative] Suggest rebalancing actions with rationale
7. [creative] Stress test: what happens in recession / rate hike / sector crash?
```

## Important Rules

1. **Numbers must be verifiable.** Every calculation must have a test or cross-check.
2. **Cite sources.** Every data point must reference where it came from.
3. **Separate fact from opinion.** Mechanical track = facts. Creative track = interpretation.
4. **Disclose limitations.** If data is incomplete or assumptions are made, say so explicitly.
5. **No financial advice framing.** Output analysis and data, not "you should buy X." Frame as "the data suggests..." not "I recommend..."

## Environment Variable Override

To use analysis.json instead of prd.json with ralph.sh:
```bash
PRD_FILE=analysis.json ./scripts/ralph.sh 10
```

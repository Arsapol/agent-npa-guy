---
name: property-calc
description: Thai NPA property financial calculator. Computes acquisition costs (transfer fee, SBT, WHT, stamp duty), rental yield, price per sqm/wah/rai, and break-even timeline. Use when evaluating any property's financials.
---

# Property Financial Calculator

## Overview

Calculates all financial metrics for Thai NPA property evaluation. Handles Thai-specific transfer taxes, size unit conversions (rai/ngan/wah/sqm), and rental yield analysis.

## Usage

### Full Analysis with Rent Range (recommended)
```bash
# Always use LOW/MID/HIGH rent scenarios instead of single rent estimate
python scripts/calc.py --price 1800000 --appraised 2500000 --sqm 35 \
  --rent-low 9000 --rent-mid 10000 --rent-high 12000 \
  --market-price 62800 --renovation 100000
```

### Full Analysis (single rent)
```bash
python scripts/calc.py --price 2500000 --appraised 3500000 --rent 15000 --sqm 35
python scripts/calc.py --price 5000000 --appraised 8000000 --rai 0 --ngan 1 --wah 50 --rent 25000 --renovation 500000
```

### Condo Example
```bash
python scripts/calc.py --price 1800000 --appraised 2500000 --sqm 28 --rent 12000 --common-fee 2000
```

### Land Example
```bash
python scripts/calc.py --price 10000000 --appraised 15000000 --rai 2 --ngan 1 --wah 0
```

### JSON output (for programmatic use)
```bash
python scripts/calc.py --price 2500000 --sqm 35 --rent 15000 --json
```

### LED Auction Round Analysis
```bash
# Show price reduction schedule for round 6
python scripts/calc.py --led-round 6 --led-appraised 2600000

# LED analysis + full financial analysis combined
python scripts/calc.py --price 1820000 --appraised 2600000 --led-round 6 --sqm 143.5 --rent 15000

# JSON output of LED analysis
python scripts/calc.py --led-round 3 --led-appraised 5000000 --json
```

## LED Auction Price Reduction Rules (กรมบังคับคดี)

| นัด (Round) | Starting Price | Notes |
|---|---|---|
| **1st** | 100% of appraised value | Full price |
| **2nd** | 90% | -10% if unsold |
| **3rd** | 80% | -20% if unsold |
| **4th+** | **70%** (floor) | Won't go lower |

**Key points:**
- Floor is 70% — price never drops below this regardless of how many rounds fail
- All 6th-round Bangkok NPA condos are already at the floor
- If a property is at floor and still unsold after 6 rounds, the issue is the property itself, not the price

## Parameters

| Param | Description |
|-------|-------------|
| `--price` | Purchase/auction price in baht (required) |
| `--appraised` | Appraised value in baht (defaults to purchase price) |
| `--rent` | Expected monthly rent in baht |
| `--sqm` | Size in square meters (for condos) |
| `--rai` | Size in rai |
| `--ngan` | Size in ngan |
| `--wah` | Size in square wah |
| `--renovation` | Estimated renovation cost in baht |
| `--vacancy` | Vacancy rate (default: 0.10 = 10%) |
| `--common-fee` | Monthly common area fee in baht |
| `--held-over-5y` | Flag if held >5 years (0.5% stamp duty instead of 3.3% SBT) |
| `--led-round` | LED auction round number (shows price reduction analysis) |
| `--led-appraised` | Appraised price for LED analysis (defaults to --appraised) |
| `--rent-low` | Low rent estimate (baht/month) — use with --rent-mid and --rent-high |
| `--rent-mid` | Mid rent estimate (baht/month) |
| `--rent-high` | High rent estimate (baht/month) |
| `--market-price` | Market price per sqm or wah (for discount sanity check) |
| `--market-unit` | Unit for --market-price: "sqm" (default) or "wah" |

## Thai Transfer Tax Rates

| Tax | Rate | When |
|-----|------|------|
| Transfer Fee | 2% | Always (on appraised value) |
| Specific Business Tax (SBT) | 3.3% | Property held < 5 years |
| Stamp Duty | 0.5% | Property held >= 5 years (replaces SBT) |
| Withholding Tax (WHT) | 1% | Always |

**NPA auction note:** Buyer typically pays transfer fee (2%). SBT/WHT is usually seller's responsibility but varies by auction terms.

## Size Conversions

| Unit | Square Meters |
|------|--------------|
| 1 rai | 1,600 sqm |
| 1 ngan | 400 sqm |
| 1 square wah | 4 sqm |

---
name: npa-adapter
description: Unified query layer across all NPA providers (LED, SAM, BAM, JAM, KTB, KBank). Search, filter, and compare properties from any source through one interface. Each provider keeps its own table — this adapter reads from all of them and normalizes into a common shape.
---

# NPA Adapter — Unified Property Query

## Overview

Query layer that sits on top of all provider tables without changing them. Normalizes field names, price units (LED satang → baht), location columns, and GPS availability into a single `NpaProperty` shape.

## Providers

| Source | Table | Price Unit | GPS | Notes |
|--------|-------|-----------|-----|-------|
| LED | `properties` + `led_properties` | satang (÷100) | No | Court auctions, case/deed info |
| SAM | `sam_properties` | baht | Yes | Government NPA, auction/direct sale |
| BAM | `bam_properties` | baht | Yes | Bank NPA, grade/shock prices |
| JAM | `jam_properties` | baht | Yes | Housing finance, rental data |
| KTB | `ktb_properties` | baht | Yes | Krung Thai Bank NPA |
| KBANK | `kbank_properties` | baht | Yes | KBank NPA, promotion prices |

## Commands

### Search across providers
```bash
# All providers, Bangkok condos under 3M
python scripts/query.py search --province กรุงเทพ --type คอนโด --max-price 3000000

# Only LED + SAM
python scripts/query.py search --province นนทบุรี --sources LED,SAM

# Keyword search, sorted by price desc
python scripts/query.py search --keyword สุขุมวิท --sort price --desc

# JSON output for piping
python scripts/query.py search --province ชลบุรี --max-price 5000000 --json
```

### Per-provider stats
```bash
python scripts/query.py stats
python scripts/query.py stats --json
```

### Cross-provider summary
```bash
python scripts/query.py summary
python scripts/query.py summary --json
```

## Python API

```python
from adapter import search, stats, summary
from models import SearchFilters, Source

# Search BAM + JAM for Bangkok condos
results = search(SearchFilters(
    province="กรุงเทพ",
    property_type="คอนโด",
    max_price=3_000_000,
    sources=[Source.BAM, Source.JAM],
))

for p in results:
    print(f"[{p.source.value}] {p.price_display} | {p.location_display}")
```

## Normalized fields

All `NpaProperty` instances have:
- `price_baht` — always in baht (LED auto-converted from satang)
- `discount_pct` — computed where appraisal is available
- `size_wa` / `size_sqm` — separated correctly (LED condo ตร.ม. fix applied)
- `lat` / `lon` — where available (LED has no GPS)
- `extra` dict — provider-specific fields (grade, case_number, deed_type, etc.)

## Search parameters

| Param | Description |
|-------|-------------|
| `--province` | Province name (partial, case-insensitive) |
| `--district` | District (partial) |
| `--subdistrict` | Sub-district (partial) |
| `--min-price` | Min price in baht |
| `--max-price` | Max price in baht |
| `--type` | Property type (partial, e.g. คอนโด, ที่ดิน, บ้าน) |
| `--keyword` | Free-text search across address/remarks/project |
| `--sources` | Comma-separated provider list (default: all) |
| `--sort` | price, province, newest |
| `--desc` | Sort descending |
| `--limit` | Max results per provider (default: 20) |
| `--json` | JSON output |

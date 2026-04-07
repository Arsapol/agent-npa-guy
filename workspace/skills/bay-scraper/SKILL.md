# BAY/Krungsri NPA Scraper

Scrapes Non-Performing Asset properties from Bank of Ayudhya (BAY/Krungsri) at krungsriproperty.com.

## Overview

- **Provider**: Bank of Ayudhya (BAY) / Krungsri
- **Website**: https://www.krungsriproperty.com
- **Total properties**: ~1,690 declared (~1,268 unique codes extractable)
- **Condos**: ~359 (Z-suffix codes, isCondo=true)
- **Prices**: Stored in whole baht (Numeric)
- **PK**: `code` (property code, e.g. AX1185, ABZ0550)

## Architecture

Two-step scraping:
1. **Discover**: GET `/search-result?keyWord=` extracts ALL property codes via regex from a single HTML page
2. **Fetch**: GET `/Helpers/GetProperties?listCodes=...&pageSize=100` returns JSON (74 fields) in batches of 50

No rate limiting observed. Full scrape = ~26 requests.

## Property Code Format

- Pattern: `{prefix}{X|Y|Z}{digits}`
- X-suffix (770): houses, townhouses, shophouses
- Z-suffix (359): condos (isCondo=true)
- Y-suffix (139): land, special properties
- Compound: `AKX0192_AKY0077` (multiple assets)

## Database Tables

| Table | Purpose |
|-------|---------|
| `bay_properties` | Main property data (PK: code) |
| `bay_price_history` | Price change tracking (1-hour dedup) |
| `bay_scrape_logs` | Scrape run metadata |

## Usage

```bash
# Create tables
python scraper.py --create-tables

# Full scrape
python scraper.py

# Condos only
python scraper.py --category C

# Test with limit
python scraper.py --limit 5

# Query
python query.py search --province กรุงเทพมหานคร
python query.py search --condo --sort discount
python query.py stats
python query.py detail AX1185

# Dedup
python dedup.py            # dry run
python dedup.py --apply    # execute

# Daily cron
./run_scraper.sh
```

## Category Codes

| Code | Thai | English |
|------|------|---------|
| A | บ้านเดี่ยว | Single House |
| B | ทาวน์เฮาส์ | Townhouse |
| C | คอนโดมิเนียม | Condominium |
| D | อาคารพาณิชย์ | Shophouse |
| E | ที่ดินเปล่า | Vacant Land |
| F | อื่น ๆ | Other |

## Limitations

1. Gallery images not in API (listGallerryImage always empty)
2. No building year/age available
3. No floor number for condos
4. ~422 properties not extractable via regex (possibly delisted)

# LH Bank NPA Scraper

## Overview

Scrapes NPA (Non-Performing Asset) properties from LH Bank (ธนาคารแลนด์ แอนด์ เฮ้าส์).
Website: https://www.lhbank.co.th/th/property-for-sale/asset-for-sale/

- ~33 total properties (smallest bank scraper)
- Single listing page, no pagination needed
- 100% GPS availability from hidden form fields
- Kentico CMS, server-rendered HTML, no JSON API

## Database

Tables: `lh_properties`, `lh_price_history`, `lh_scrape_logs`
Prices: whole baht (Numeric)
Primary key: `property_id` (AssetCode, e.g. "LH031A")

## Usage

```bash
cd workspace/skills/lh-scraper/scripts

# Create tables
python scraper.py --create-tables

# Full scrape (all ~33 properties)
python scraper.py

# Limited scrape
python scraper.py --limit 5

# Listing only (no detail pages)
python scraper.py --list-only

# Query
python query.py stats
python query.py search --asset-type "คอนโด"
python query.py search --price-max 3000000
python query.py detail LH031A

# Dedup
python dedup.py            # dry run
python dedup.py --apply    # execute

# Cron
./run_scraper.sh
```

## Architecture

1. Single GET to listing page fetches all ~33 property cards
2. Concurrent detail page fetches (Semaphore=5) for GPS, images, descriptions
3. Upsert by `property_id` (AssetCode)
4. Price history with 1-hour dedup window

## Fields Parsed

| Source | Fields |
|--------|--------|
| Listing card | asset_code, asset_type, area_text, price, address, thumbnail |
| Detail page | sale_price, case_info, description, address, area, GPS, images, PDF, post_date |

## Fields NOT Available

- Appraisal value (ราคาประเมิน)
- Title deed type (โฉนด/นส.3)
- Building year/age
- Project name (sometimes in free-text description)
- Bedrooms/bathrooms (sometimes in free-text description)

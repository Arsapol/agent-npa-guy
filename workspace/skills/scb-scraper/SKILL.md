# SCB NPA Scraper

Scrapes Non-Performing Asset properties from SCB (Siam Commercial Bank) via asset.home.scb.

## Data Source

- **Website**: https://asset.home.scb/
- **Total properties**: ~3,883 (as of 2026-04-07)
- **Architecture**: JSON search API + server-rendered HTML detail pages
- **Auth**: None required
- **Rate limiting**: None observed

## Database

Tables: `scb_properties`, `scb_price_history`, `scb_scrape_logs`

- Prices stored in **whole baht** (Numeric)
- Primary key: `project_id` (SCB's internal integer ID)
- Additional identifier: `project_id_gen` (SCB asset code, e.g. `41002S20G2B01909`)

## Usage

```bash
cd workspace/skills/scb-scraper/scripts

# Create tables
python scraper.py --create-tables

# Full scrape (all asset types)
python scraper.py

# Single asset type
python scraper.py --type condominiums

# Test with limit
python scraper.py --limit 50

# Search only (skip HTML detail pages)
python scraper.py --skip-detail

# Query local database
python query.py stats
python query.py search --province-id 1 --type condominiums
python query.py search --keyword "สุขุมวิท" --max-price 5000000
python query.py history 12345

# Dedup (dry run)
python dedup.py
python dedup.py --apply

# Daily cron
./run_scraper.sh
```

## Asset Types

| Code | Thai Name | Count |
|------|-----------|-------|
| `condominiums` | ห้องชุด/คอนโดมิเนียม | 1,240 |
| `townhouses` | ทาวน์เฮ้าส์ | 878 |
| `single_houses` | บ้านเดี่ยว | 840 |
| `duplex_homes` | บ้านแฝด | 174 |
| `vacant_land` | ที่ดินว่างเปล่า | 103 |
| `warehouses` | โกดัง | 64 |
| `office_buildings` | อาคารสำนักงาน | 30 |
| `factories` | โรงงาน | 22 |
| `building` | อาคาร | 21 |

## Fields

### From Search API (JSON)
project_id, project_type, project_title, price, price_discount, GPS,
province_id, district_id, area_use, land_area, slug, images, promotion info

### From Detail Page (HTML parse)
title_deed, bedrooms, bathrooms, parking, description, full-res images

## Price Notes

- `price`: String with commas in API (e.g. `"4,620,000"`), stored as Numeric in DB
- `price_discount`: `"0"` when no discount
- Province IDs are SCB-custom (NOT standard Thai codes). Bangkok = 1.

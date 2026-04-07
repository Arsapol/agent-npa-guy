# GHB Scraper

Scrapes NPA properties from GHB HomCenter (ธนาคารอาคารสงเคราะห์ / Government Housing Bank).

**Site**: https://www.ghbhomecenter.com/
**Inventory**: ~26,648 properties (largest NPA provider)
**Prices**: Stored in whole baht (integer)
**Upsert key**: `property_no` (public property code, e.g., `1301201301`)

## Architecture

Two-phase HTML scraper:
1. **Listing crawl**: Paginate `/property-foryou-for-sale?pg=N&pt[]=T` to discover property IDs (10 items/page)
2. **Detail crawl**: Fetch `/property-{id}` for each property, parse HTML for GPS, images, deed info, description

Anonymous JWT embedded in page JS (~7d TTL) — used for API calls if needed, refreshed automatically.

## Database Tables

| Table | Purpose |
|-------|---------|
| `ghb_properties` | Main property table, PK = `property_id`, UNIQUE on `property_no` |
| `ghb_price_history` | Price change tracking, 1-hour dedup window |
| `ghb_scrape_logs` | Scrape run metadata |

## Usage

```bash
# Create tables
python scraper.py --create-tables

# Full scrape (all types, all provinces)
python scraper.py

# Condos only
python scraper.py --type 3

# Bangkok only
python scraper.py --province 3001

# Test with limit
python scraper.py --limit 5

# Listing only (skip detail pages)
python scraper.py --skip-detail

# Daily cron
./run_scraper.sh
```

## Query

```bash
python query.py search --province กรุงเทพมหานคร
python query.py search --type-id 3 --price-max 3000000
python query.py stats
python query.py detail 987980
```

## Dedup

```bash
python dedup.py            # dry run
python dedup.py --apply    # execute
```

## Property Type IDs

| ID | Thai | English |
|----|------|---------|
| 1 | บ้านเดี่ยว | Detached house |
| 2 | บ้านแฝด | Semi-detached house |
| 3 | คอนโด | Condominium |
| 4 | ทาวน์เฮ้าส์ | Townhouse |
| 5 | อาคารพาณิชย์ | Commercial building |
| 6 | ที่ดิน | Land |
| 7 | แฟลต | Flat |
| 8 | อื่นๆ | Other |

## Province IDs (common)

| ID | Province |
|----|----------|
| 3001 | กรุงเทพมหานคร |
| 3043 | นนทบุรี |
| 3042 | ปทุมธานี |
| 3019 | ชลบุรี |
| 3024 | เชียงใหม่ |
| 3061 | ภูเก็ต |
| 3073 | สงขลา |

## Rate Limits

- Listing pages: ~2 req/sec (500ms delay)
- Detail pages: 5 concurrent, 500ms delay each
- No observed server-side rate limiting, but conservative defaults to be safe

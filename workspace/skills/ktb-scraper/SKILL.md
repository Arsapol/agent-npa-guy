# KTB NPA Scraper

Scrapes Krungthai Bank (KTB) NPA properties from npa.krungthai.com. Upserts to PostgreSQL with price history tracking.

## Quick Start

```bash
cd workspace/skills/ktb-scraper/scripts

# Create tables only
python scraper.py --create-tables

# Test with 5 properties
python scraper.py --limit 5

# Full scrape (2,673 properties)
python scraper.py

# Search-only (skip detail fetch)
python scraper.py --skip-detail

# Filter by province
python scraper.py --province กรุงเทพมหานคร
```

## Query

```bash
python query.py stats
python query.py search --province กรุงเทพ --type คอนโด --max-price 2000000
python query.py history 230741
```

## Database

Tables: `ktb_properties`, `ktb_price_history`, `ktb_scrape_logs`

Prices in **whole baht** (Numeric). Primary key: `coll_grp_id`.

## Architecture

2-phase sequential (same-origin rate limit):
1. Paginate searchAll (50/page, ~54 pages)
2. Fetch detail per item (bounded concurrency=5)
3. Merge + upsert with price/category change tracking

Rate limit: 25 req/60s sliding window.

## API Reference

See [API_NOTES.md](API_NOTES.md) for endpoint details, field maps, and gotchas.

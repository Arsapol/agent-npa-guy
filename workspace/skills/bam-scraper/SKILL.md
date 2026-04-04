# BAM Scraper

Scrapes NPA properties from BAM (Bangkok Commercial Asset Management) via their public API at bam.co.th.

## What It Does

- Fetches all ~15,900 NPA properties from BAM's search + detail APIs
- Upserts into `bam_properties` PostgreSQL table
- Tracks price changes in `bam_price_history`
- Logs each scrape run in `bam_scrape_logs`

## API Endpoints

| Endpoint | Purpose |
|----------|---------|
| `POST /master/province/filter` | List all 78 provinces |
| `POST /master/District/Dropdown/find` | Districts for a province |
| `POST /api/asset-detail/search` | Paginated property search |
| `GET /property-detail/getExpiredSubscriptionDateTimeByAssetId/{id}` | Full property detail (appraised value, grade, descriptions) |
| `GET /cmk-v2/getCampaignCondition/{id}` | Campaign conditions (seasonal) |

## Database

Tables in `postgresql://arsapolm@localhost:5432/npa_kb`:

- `bam_properties` — merged search + detail data, keyed by BAM asset ID
- `bam_price_history` — price change log (new, price_change, state_change)
- `bam_scrape_logs` — scrape run metadata

Prices stored in **whole baht** (Numeric).

## Usage

```bash
cd workspace/skills/bam-scraper/scripts

# Full scrape (all provinces, ~15,900 assets)
python scraper.py

# Single province
python scraper.py --province กรุงเทพมหานคร

# Test run (first 100 assets)
python scraper.py --limit 100

# Fast mode: search only, no detail fetch
python scraper.py --skip-detail

# Create DB tables only
python scraper.py --create-tables

# Query properties
python query.py search --province กรุงเทพมหานคร
python query.py search --grade A --price-max 5000000
python query.py detail 154304
python query.py stats
```

## Key Fields

| Field | Source | Description |
|-------|--------|-------------|
| `sell_price` | search | BAM asking price (center_price) |
| `evaluate_amt` | detail | Appraised value |
| `cost_asset_amt` | detail | BAM's acquisition cost |
| `grade` | detail | A/B/C grading |
| `sale_price_spc` | detail | Special/discount price with date range |
| `asset_type` | search | Property type (ห้องชุดพักอาศัย, ทาวน์เฮ้าส์, etc.) |
| `col_sub_typedesc` | detail | Collateral sub-type description |

## Architecture

- `models.py` — Pydantic v2 (BamAssetSearch, BamAssetDetail) + SQLAlchemy 2.0 (BamProperty, BamPriceHistory, BamScrapeLog)
- `database.py` — Engine, create_tables, upsert with price/state tracking
- `scraper.py` — Async httpx, Semaphore(10) search / Semaphore(15) detail
- `query.py` — CLI for searching local DB

# GSB (ออมสิน) NPA Scraper

Scrapes Non-Performing Asset properties from Government Savings Bank (ธนาคารออมสิน).

**Site**: https://npa-assets.gsb.or.th/
**Total assets**: ~4,492 NPA properties (as of 2026-04-07)
**Auth**: None — all endpoints are public GET

## Database

Tables in `postgresql://arsapolm@localhost:5432/npa_kb`:

| Table | Description |
|-------|-------------|
| `gsb_properties` | Main property table, PK = `npa_id` (asset_group_id_npa) |
| `gsb_price_history` | Price change tracking with 1-hour dedup window |
| `gsb_scrape_logs` | Scrape run metadata |

Prices stored in **whole baht** (integer).
Building year (`builded_year`) in **Buddhist era** — store as-is, convert in query layer.

## Usage

```bash
cd workspace/skills/gsb-scraper/scripts

# Create tables
python scraper.py --create-tables

# Full scrape (all 3 types: land, land+building, condo)
python scraper.py

# Test with limit
python scraper.py --limit 5

# Condos only
python scraper.py --type 343

# Skip detail fetching (search data only)
python scraper.py --skip-detail

# Query database
python query.py stats
python query.py search --province "กรุงเทพ" --type 343
python query.py search --name "ฮอไรซอน" --max-price 2000000
python query.py history BKK620093

# Dedup (dry run / apply)
python dedup.py
python dedup.py --apply

# Cron wrapper
./run_scraper.sh
```

## Architecture

1. **3 list API calls** — one per asset_type_id (341=land, 342=land+building, 343=condo)
   - API returns ALL items in a single response (no pagination needed)
2. **Detail via HTML parsing** — fetch `/asset/npa?id={npa_id}` and parse `__NEXT_DATA__`
   - NOT via `/_next/data/` routes (buildId is unstable across partial deploys)
   - Bounded concurrency: `asyncio.Semaphore(10)`
3. **Upsert** keyed by `npa_id` (asset_group_id_npa)
4. **Price history** with 1-hour dedup window

## Asset Types

| ID | Description | Count |
|----|-------------|-------|
| 341 | ที่ดิน (Land) | ~107 |
| 342 | ที่ดินพร้อมสิ่งปลูกสร้าง (Land + Building) | ~3,749 |
| 343 | คอนโด/อาคารชุด/ห้องชุด (Condo) | ~636 |

## Pricing Fields

| Field | Description |
|-------|-------------|
| `current_offer_price` | Active selling price |
| `xprice_normal` | Normal selling price |
| `xprice` | Promotional/special price |
| `xtype` | `"promotion"` if promo active, else `"normal"` |
| `group_sell_price` | Group selling price |
| `group_special_price` | Group special price |

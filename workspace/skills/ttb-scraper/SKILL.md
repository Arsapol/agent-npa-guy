# TTB/PAMCO NPA Scraper

Scrapes NPA properties from TTB (TMBThanachart Bank) and PAMCO (บริษัท บริหารสินทรัพย์ พีเอเอ็มซี จำกัด).

## Source

- Site: https://property.pamco.co.th/
- API: https://property-api-prod.automer.io/
- Two sources: PAMCO (type=3) and TTB (type=4)

## Architecture

List-only — the `/property-new/display` endpoint returns ALL fields including GPS, nearby, images, pricing, and special offers. No detail endpoint needed.

## Database

Tables: `ttb_properties`, `ttb_price_history`, `ttb_scrape_logs`

Prices stored in **whole baht** (Numeric). Upsert keyed by `id_property` (integer PK).

Business ID: `id_market` (string, e.g. "B13477", "P00831") with UNIQUE constraint.

## Usage

```bash
# Create tables
python scripts/scraper.py --create-tables

# Full scrape (~1,356 properties)
python scripts/scraper.py

# Filter by province (10=Bangkok)
python scripts/scraper.py --province 10

# Filter by category (4=condo)
python scripts/scraper.py --category 4

# Test with limit
python scripts/scraper.py --limit 5

# Daily cron
bash scripts/run_scraper.sh

# Query
python scripts/query.py search --province "กรุงเทพ"
python scripts/query.py search --source pamco --category 4
python scripts/query.py stats
python scripts/query.py get B13477

# Dedup
python scripts/dedup.py          # dry-run
python scripts/dedup.py --apply  # execute
```

## API Details

- List: `GET /property-new/display?page={n}&limit=200`
- Returns: `{"total": int, "list": [...]}`
- Headers: just User-Agent (no auth)
- Categories: 1=บ้านเดี่ยว, 2=ทาวน์เฮ้าส์, 3=อาคารพาณิชย์, 4=คอนโด, 5=ที่ดิน, 6=โรงงาน, 7=สำนักงาน
- Prices: `lowprice[0].lowprice` as string (whole baht)
- Special prices: `idEvent[0].priceSp1` with date range

## Property Categories (idCategory)

| idCategory | idDetail | Name |
|------------|----------|------|
| 1 | 1 | บ้านเดี่ยว |
| 1 | 2 | ทาวน์เฮ้าส์/ทาวน์โฮม |
| 2 | 4 | คอนโด |
| 3 | 3 | อาคารพาณิชย์ |
| 3 | 7 | สำนักงาน |
| 4 | 5 | ที่ดินเปล่า |
| 5 | 6 | โรงงาน/โกดัง |

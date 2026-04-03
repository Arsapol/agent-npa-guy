---
name: sam-scraper
description: Scrapes and queries Thai NPA (non-performing asset) property listings from SAM (บสส.) at sam.or.th. Use when the user asks about SAM properties, NPA auctions, Thai government asset sales, or needs to refresh property data from sam.or.th. Provides 4,700+ properties with pricing, coordinates, images, deed info, and auction schedules stored in PostgreSQL.
---

# SAM NPA Scraper

Scrapes NPA property listings from SAM (บสส. — Thai Asset Management Corporation) and stores structured data in PostgreSQL for querying.

## When to Use

Activate this skill when the user:
- Asks to scrape, refresh, or update SAM/NPA property data
- Wants to find properties by location, type, price, or auction status
- Needs Thai NPA market data, pricing analysis, or property details
- Asks about upcoming auctions or direct-sale properties from SAM
- Wants to compare properties within a project or area

## Pipeline

Run from `scripts/` directory. Database: `postgresql://arsapolm@localhost:5432/npa_kb`

### Full scrape
```bash
./run_scraper.sh
```

### Refresh listings only (prices, statuses, new properties)
```bash
python3 scrape_list.py --max-pages 0 --delay 2
```

### Fetch missing details
```bash
python3 scrape_detail.py --only-missing --delay 3
```

### Fetch specific properties
```bash
python3 scrape_detail.py --sam-ids 6414,23153 --delay 1
```

### Filter by sale type
```bash
# Auction only
python3 scrape_list.py --filter-status 2
# Direct sale only
python3 scrape_list.py --filter-status 1
```

## Querying Data

After scraping, query `sam_properties` in `npa_kb` database.

### Key fields
| Field | Type | Description |
|-------|------|-------------|
| `sam_id` | int | SAM internal ID (unique) |
| `code` | str | Property code e.g. `1T2174`, `CL0175` |
| `type_name` | str | Thai property type (36 types) |
| `price_baht` | numeric | Announced price (nullable) |
| `price_per_unit` | numeric | Price per sqm or sq.wah |
| `size_sqm` | numeric | Total area in sq.m. |
| `size_rai` / `size_ngan` / `size_wa` | numeric | Thai land units |
| `province` / `district` / `subdistrict` | str | Location hierarchy |
| `lat` / `lng` | numeric(10,6) | GPS coordinates |
| `status` | str | ประมูล / ซื้อตรง / รอประกาศราคา |
| `floor` | int | Floor number (condos only) |
| `related_property_codes` | text[] | Other codes in same project |
| `detail_fetched_at` | datetime | NULL = detail not yet scraped |

### Common queries

**Properties by location and type:**
```sql
SELECT code, type_name, price_baht, size_sqm, district
FROM sam_properties
WHERE province = 'กรุงเทพมหานคร'
  AND type_name = 'ห้องชุดพักอาศัย'
ORDER BY price_baht;
```

**Land in a price range:**
```sql
SELECT code, size_rai, price_baht, district, province
FROM sam_properties
WHERE type_name = 'ที่ดินเปล่า'
  AND price_baht BETWEEN 1000000 AND 10000000
ORDER BY price_baht;
```

**Properties with GPS for mapping:**
```sql
SELECT code, type_name, lat, lng, price_baht
FROM sam_properties
WHERE lat IS NOT NULL AND province = 'ภูเก็ต';
```

**Properties needing detail scrape:**
```sql
SELECT count(*) FROM sam_properties WHERE detail_fetched_at IS NULL;
```

## Database Tables

| Table | Purpose |
|-------|---------|
| `sam_properties` | All property data (list + detail merged) |
| `sam_property_images` | Gallery images with type (photo/certificate) |
| `sam_dropdown_cache` | Province, district, type, status lookup values |
| `sam_scrape_logs` | Scrape run history |

## Technical Details

- **Async httpx** with `asyncio.Semaphore(10)` — 10 max concurrent requests
- **selectolax** (lexbor) for HTML parsing
- **Pydantic v2** models for parse validation
- **200 items/page** for list scraping, **100-item chunks** for detail scraping
- Fan-out HTTP fetches → fan-in sequential DB writes

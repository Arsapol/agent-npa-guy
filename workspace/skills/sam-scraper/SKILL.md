# SAM NPA Scraper

Scrapes NPA property listings from SAM (บสส. — Thai Asset Management Corporation) at [sam.or.th/site/npa/](https://sam.or.th/site/npa/). Extracts property details, coordinates, images, pricing, and auction status.

## Scripts

| Script | Purpose |
|--------|---------|
| `run_scraper.sh` | Full pipeline runner |
| `update_options.py` | Fetch & cache dropdown options (provinces, districts, types, statuses) |
| `scrape_list.py` | Scrape listing pages → `sam_properties` table (200 items/page) |
| `scrape_detail.py` | Scrape detail pages → fill in all fields (chunked, 100/batch) |
| `migrate_schema.py` | One-time DB migration (Float→Numeric, add new columns, etc.) |

## Quick Start

```bash
# Full pipeline (options + list + detail)
./run_scraper.sh

# List only
./run_scraper.sh --list-only

# Detail only (for previously listed properties missing details)
./run_scraper.sh --detail-only --detail-limit=100
```

## Architecture

- **Async httpx** with `asyncio.Semaphore(10)` — max 10 concurrent requests
- **selectolax** (lexbor backend) — 10-30x faster HTML parsing than bs4
- **Pydantic v2** models (`SAMListProperty`, `SAMPropertyDetail`) as parsing/validation layer
- **SQLAlchemy ORM** for PostgreSQL storage with `Numeric` types for precision
- Fan-out fetch → fan-in save pattern (DB writes stay sequential)

## Database Tables

All stored in PostgreSQL `npa_kb` database:

| Table | Purpose |
|-------|---------|
| `sam_properties` | Full property data (list + detail merged) |
| `sam_property_images` | Gallery images (P=photo, C=certificate, M=map) |
| `sam_dropdown_cache` | Cached search form dropdowns |
| `sam_scrape_logs` | Run history for monitoring |

## Data Model

**SAMProperty fields:**
- `sam_id` (unique) — SAM internal ID
- `code` — Property code (e.g. `1T2174`, `CL0175`)
- `type_name` — ประเภททรัพย์สิน (36 types)
- `title_deed_type` / `title_deed_numbers` — Deed info
- `size_sqm` / `size_rai` / `size_ngan` / `size_wa` — Normalized sizes (Numeric)
- `price_baht` (nullable Numeric) / `price_per_unit` / `price_unit` — Pricing
- `lat` / `lng` — Coordinates (Numeric(10,6))
- `status` — ประมูล / ซื้อตรง
- `announcement_start_date` / `registration_end_date` / `submission_date` — Auction dates
- `auction_method_text` — Submission method details
- `thumbnail_url` / `map_image_url` — Media URLs
- `related_property_codes` — PostgreSQL ARRAY(String)
- `promotion_links` — PostgreSQL ARRAY(Text)
- `house_number` / `project_name` / `road` / `subdistrict` / `district` / `province` — Address
- `description` / `remarks` / `access_directions` — Detail text

## Environment

```bash
POSTGRES_URI=postgresql://user@localhost:5432/npa_kb  # default
SAM_DELAY=3  # seconds between requests (default: 3)
```

## Dependencies

```
httpx
selectolax
pydantic>=2.0
sqlalchemy
psycopg2-binary
```

## Notes

- All scripts are fully async with `asyncio.run(main())`.
- 4,707+ properties as of April 2026 across 77 provinces.
- List scraper fetches 200 items/page (24 pages total vs 235 at 20/page).
- Detail scraper processes in chunks of 100 with 10 concurrent fetches.
- Images are hosted at `https://npa.sam.or.th/site/images/npa/{id}/...`

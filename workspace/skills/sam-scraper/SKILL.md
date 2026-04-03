# SAM NPA Scraper

Scrapes NPA property listings from SAM (บสส. — Thai Asset Management Corporation) at [sam.or.th/site/npa/](https://sam.or.th/site/npa/). Extracts property details, coordinates, images, pricing, and auction status.

## Scripts

| Script | Purpose |
|--------|---------|
| `run_scraper.sh` | Full pipeline runner |
| `update_options.py` | Fetch & cache dropdown options (provinces, districts, types, statuses) |
| `scrape_list.py` | Scrape listing pages → `sam_properties` table |
| `scrape_detail.py` | Scrape detail pages → fill in all fields |

## Quick Start

```bash
# Full pipeline (options + list + detail)
./run_scraper.sh

# List only (fast, ~3hrs for all 4700+ properties at 3s delay)
./run_scraper.sh --list-only

# Detail only (for previously listed properties missing details)
./run_scraper.sh --detail-only --detail-limit=100

# First 10 pages only
./run_scraper.sh --list-only --max-pages 10
```

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
- `size_sqm` / `size_rai` / `size_ngan` / `size_wa` — Normalized sizes
- `price_baht` / `price_per_unit` / `price_unit` — Pricing
- `lat` / `lng` — Coordinates
- `status` — ประมูล / ซื้อตรง
- `description` / `remarks` / `access_directions` — Detail text

## Environment

```bash
POSTGRES_URI=postgresql://user@localhost:5432/npa_kb  # default
SAM_DELAY=3  # seconds between requests (default: 3)
```

## Dependencies

```
requests
beautifulsoup4
pydantic>=2.0
sqlalchemy
psycopg2-binary
```

## Notes

- SAM site drops connections after ~5 consecutive requests. Built-in retry with reconnection.
- 4,707+ properties as of April 2026 across 77 provinces.
- Detail scraping is rate-sensitive: use `--delay 5` for reliability.
- Images are hosted at `https://npa.sam.or.th/site/images/npa/{id}/...`

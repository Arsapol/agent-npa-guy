---
name: led-scraper
description: Scrapes NPA property listings from LED (Legal Execution Department / กรมบังคับคดี) website. Extracts property details, auction history, sale status, and pricing from court-ordered property auctions. Runs on schedule via launchd or manually via CLI.
---

# LED Property Scraper

## Overview

Scrapes property auction listings from Thailand's Legal Execution Department (LED / กรมบังคับคดี). Extracts structured data including lot numbers, case info, addresses, pricing, auction history, and sale status.

## How to Run

### Manual (single agency)
```bash
cd /Users/arsapolm/.nanobot-npa-guy/workspace/skills/led-scraper/scripts
python main.py --agency "แพ่งกรุงเทพมหานคร 1" --save-to json --max-pages 100
```

### Manual (all configured agencies)
```bash
python main.py --save-to json --max-pages 500 --parallel-batch-size 3
```

### Manual (save to Turso DB)
```bash
python main.py --save-to both --max-pages 500
```

### Scheduled (launchd)
See `com.npa-guy.led-scraper.plist` in ~/Library/LaunchAgents/

## CLI Arguments

| Arg | Default | Description |
|-----|---------|-------------|
| `--agency` | config.py list | Single agency name |
| `--agencies` | - | Comma-separated agency list |
| `--agencies-file` | - | File with one agency per line |
| `--max-pages` | 500 | Max pages per agency |
| `--concurrent` | 10 | Concurrent page fetches |
| `--parallel-batch-size` | 3 | Agencies processed in parallel |
| `--max-duration` | 840 | Max execution seconds |
| `--save-to` | both | json / db / both |
| `--source-prefix` | LED | Source label prefix |
| `--batch-size` | 50 | DB insert batch size |

## Configured Agencies (config.py)

Currently configured for Bangkok courts:
- กรุงเทพ กองล้มละลาย 1-6 (Bangkok Bankruptcy Division)
- กรุงเทพ สำนักฟื้นฟูกิจการของลูกหนี้ (Rehabilitation)
- แพ่งกรุงเทพมหานคร 1-7 (Bangkok Civil Court)

Edit `config.py` to add/remove agencies.

## Output

- **JSON files**: `led_properties_{agency}_{timestamp}.json` in scripts/ directory
- **Turso DB**: Requires TURSO_DATABASE_URL and TURSO_AUTH_TOKEN in .env

## Dependencies

```
curl-cffi>=0.6.0
selectolax>=0.3.0
sqlalchemy>=2.0.0
sqlalchemy-libsql>=0.1.0
libsql>=0.1.11
python-dotenv>=1.0.0
nest-asyncio>=1.5.0
```

## Environment Variables

Copy `.env.example` to `.env` and fill in:
- `TURSO_DATABASE_URL` — Turso/LibSQL database URL
- `TURSO_AUTH_TOKEN` — Turso auth token

## Data Structure

Each scraped property includes:
- **Identifiers**: lot_number, asset_id, case_number
- **Location**: province, district, sub_district, address
- **Property**: type, land_area (rai/ngan/wah), building details
- **Pricing**: appraisal_price, starting_bid, deposit_required
- **Auction**: up to 8 auction rounds with dates and sale status
- **Status**: sold, not sold, withdrawn, cancelled, etc.

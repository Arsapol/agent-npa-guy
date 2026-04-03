---
name: led-query
description: Query LED NPA properties from local PostgreSQL database. Search by location, price range, property type, upcoming auctions. Get price statistics and database summaries. Use when analyzing properties from the scraped LED data.
---

# LED Property Query

## Overview

SQL interface to the scraped LED (กรมบังคับคดี) property data stored in local PostgreSQL (`npa_kb` database). Provides search, filtering, price statistics, and upcoming auction listings.

## Commands

### Search Properties
```bash
python scripts/query.py search --province "กรุงเทพ" --max-price 3000000 --type "คอนโด"
python scripts/query.py search --district "บางนา" --min-price 1000000 --max-price 5000000
python scripts/query.py search --keyword "สุขุมวิท" --sort price --limit 10
python scripts/query.py search --status "ยังไม่ขาย" --province "นนทบุรี" -v
```

### Upcoming Auctions
```bash
python scripts/query.py upcoming --days 14 --province "กรุงเทพ"
python scripts/query.py upcoming --days 30 --limit 50
```

### Price Statistics
```bash
python scripts/query.py stats --province "กรุงเทพ"
python scripts/query.py stats --district "จตุจักร" --type "คอนโด"
python scripts/query.py stats --province "เชียงใหม่"
```

### Database Summary
```bash
python scripts/query.py summary
```

## Search Parameters

| Param | Description |
|-------|-------------|
| `--province` | Province name (partial, case-insensitive) |
| `--district` | District/Ampur (partial) |
| `--sub-district` | Sub-district/Tumbol (partial) |
| `--min-price` | Minimum price in baht |
| `--max-price` | Maximum price in baht |
| `--type` | Property type (partial, e.g. "คอนโด", "บ้าน", "ที่ดิน") |
| `--status` | Sale status (e.g. "ยังไม่ขาย", "ขายแล้ว") |
| `--keyword` | Search in address and remarks |
| `--sort` | Sort by: price, province, auction_date, created |
| `--desc` | Sort descending |
| `--limit` | Max results (default: 20) |
| `--json` | Output as JSON |
| `-v` | Verbose (show case number, court, contact) |

## Output

Returns property listings with: asset_id, type, address, province/district, size (rai/ngan/wah), price, sale status, auction dates, deed type, case info.

Price statistics show: count, min, median, average, max per area/type group.

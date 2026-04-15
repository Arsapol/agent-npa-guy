# NPA-guy Memory

## User Profile
- Name: Arsapol
- Telegram ID: 1372818654
- Projects: LED scraper (live), NPA multi-provider pipeline

## Cron Jobs
- Morning NPA daily: 08:00
- NPA Price Watch: 09:00
- Dream consolidation: every 2h

## Analysis Preferences
- **All providers must be checked comprehensively** — no selective/sampled approach
- **Pandas-based team analysis** — use DataFrames for data work across providers

## Daily Scan Workflow
1. Write `daily_scan.md` FIRST before any agent-comm calls
2. **Alert triggers (notify Ada via agent-comm):**
   - ANY deal scores 70+ via `best_strategy` → send one-line summary to Ada
   - Auction within 7 days on tracked property → send URGENT alert
   - No deals score 70+ → skip agent-comm entirely (Ada reads daily_scan.md on own schedule)

### daily_scan.md Required Format
- Main table: Property | Source | Score | Price | Yield | Auction Date | Notes
- Price Drops section
- Summary line: total scanned, 70+ count, auctions within 7d

## Ada (Agent)
- Receives notifications via agent-comm
- Workspace: `~/.nanobot-stocks/workspace`
- Config: `~/.nanobot-stocks/config.json`

## Key Watchlist Properties
- SAM 8Z5956 — ฿776K, BTS สะพานควาย 112m, ฿24,250/sqm
- BAM HBKKCU2835001 & HBKKCU2870001 — ฿160K, BTS เพชรเกล้า 115m

## Known Data Issues
- ศรีราชา/ชลบุรี deals: persistent stale appraisals; discount capping at -95% working as intended
- KBANK property images use internal/private URLs blocked by safety guard — must use ZMyHome/condonayoo project images instead

## Tooling & Technical Notes
- **location-intel script**: `skills/location-intel/scripts/location.py` (NOT `location_check.py`)
- **NPA adapter**: Python import fails (`ModuleNotFoundError: No module named 'skills.npa_adapter'`) — use CLI `python scripts/query.py search` instead
- **market-checker skill**: does not exist — fallback stack for investment analysis: web-search + location-intel + kb + npa-comparator
- **KB CLI ingest**: `python skills/kb/scripts/cli_ingest.py --text "..." --category <cat> --area "<area>" --source "<src>"`
- **Overpass API**: queries time out frequently (504) at Kasetsart-area coordinates
- **location-intel bug**: hardcoded BTS stations skip ม.เกษตร/N13 (jumps สะพานใหม่ → หมอชิต)

## Project Reference Data
### Premio Vetro (พรีมิโอ เวโทร)
- 16 floors, 289 units, 1 building, completed 2015, developer บริษัท พรีเมี่ยม เพลสกรุ๊ป จำกัด
- ~720m to BTS ม.เกษตร
- Resale ~฿92,857–107,692/sqm; rentals ฿13,000–16,000/mo (1BR)
- Hipflat trend: downtrend; gov appraisal (2024) ฿81,500–87,800/sqm

### 624 Condolette Ratchada 36 (KBANK 051002243)
- ฿1.25M, 23.74sqm BR1, จันทรเกษม จตุจักร
- ~109m to MRT ลาดพร้าว — location-intel returned wrong coords, manually verified
- Pruksa developer, 8 floors/3 bldgs/486 units, completed 2555/2556
- Gov appraisal ฿48,700–51,900/sqm
- ZMyHome: 12 for sale (฿1.3M–2.9M), 7 for rent (฿6,500–12,000)

### Kensington Disambiguation (near Kasetsart U)
- **Kensington Phahol-Kaset** (เคนซิงตัน พหลโยธิน-เกษตร): พหลโยธิน 42, 2017, 229 units, 8 floors
- **Kensington Phaholyothin 63** (เคนซิงตัน พหลโยธิน 63): พหลโยธิน 63, 2020, 231 units, 8 floors
- 636m apart — often confused; verify which before analysis

## Outstanding Deliverables
- **Kensington Kaset Campus** full analysis — requested 2026-04-09, undelivered as of 2026-04-10

## DB Schema Quirks
- LED: uses `internal` not `property_id`
- `properties.next_auction_date`: varchar, not date type
- SAM `sam_id`: integer type — string IDs like "4T0183" cause query errors
- BAM: uses `asset_type` not `property_type_name`
- KBANK: no `project_name` column (in `asset_info_th` or requires detail scrape)

## Python Adapter Notes
- `search()` function does NOT accept `limit` kwarg despite docs suggesting it should

## Bangkok NPA Shortlist — Best Candidates (2026-04-04 Research)
### Criteria: Near int'l school / university / top hospital / CBD + great price + yield

| # | Code | Project | District | Price | sqm | ฿/sqm | Transit | Key Nearby | Market ฿/sqm | Discount | Notes |
|---|------|---------|----------|-------|-----|-------|---------|------------|-------------|----------|-------|
| 1 | 3A2101 | UD Delight @ Jatujak Station | บางเขน | ฿3.12M | 40.3 | 77K | MRT จตุจักร 494m
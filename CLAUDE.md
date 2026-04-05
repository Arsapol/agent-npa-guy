# NPA-guy — Thai NPA Property Investment Agent

## What This Project Is

A specialized AI agent that analyzes Thai Non-Performing Asset (NPA) properties from government auctions (LED, SAM) and banks. Evaluates whether distressed properties are worth buying based on location, pricing, legal risks, and market comparables.

**Not** a generic real estate assistant — only analyzes distressed/foreclosed assets.

## Project Layout

```
workspace/
├── SOUL.md          # Agent identity & personality
├── AGENTS.md        # Operational rules & analysis template
├── USER.md          # User profile (Arsapol, expert, Bangkok TZ)
├── TOOLS.md         # Tool constraints
├── .env             # DB creds + API keys
├── memory/MEMORY.md # Live state & active properties
├── sessions/        # Telegram + CLI conversation history
├── output/          # Analysis reports & cached HTML
├── data/            # LightRAG cache + scraper logs
├── cron/            # Scheduled jobs
└── skills/          # 12 modular skills (see below)
```

## Database

PostgreSQL: `postgresql://arsapolm@localhost:5432/npa_kb`

| Table Group | Tables |
|-------------|--------|
| LED scraper | `properties`, `led_properties`, `bank_npa_properties`, `property_images`, `auction_history` |
| SAM scraper | `sam_properties`, `sam_property_images`, `sam_dropdown_cache`, `sam_scrape_logs` |
| BAM scraper | `bam_properties`, `bam_price_history`, `bam_scrape_logs` |
| JAM scraper | `jam_properties`, `jam_price_history`, `jam_scrape_logs` |
| KTB scraper | `ktb_properties`, `ktb_price_history`, `ktb_scrape_logs` |
| KBank scraper | `kbank_properties`, `kbank_price_history`, `kbank_scrape_logs` |
| Knowledge base | LightRAG vector/graph tables + `kb_metadata` |

- LED prices stored in **satang** (integer)
- SAM prices stored in **whole baht** (numeric)
- BAM prices stored in **whole baht** (numeric)
- JAM prices stored in **whole baht** (numeric)
- KTB prices stored in **whole baht** (numeric)
- KBank prices stored in **whole baht** (numeric)
- **Use `npa-adapter` for cross-provider queries** — normalizes all prices to baht

## Skills

| Skill | Purpose | How to Run |
|-------|---------|------------|
| `led-scraper` | Scrape court auction properties from LED.go.th | `python main.py --agency "..." --max-pages 500` |
| `sam-scraper` | Scrape SAM NPA properties (4,700+) | `./run_scraper.sh` or individual scripts |
| `bam-scraper` | Scrape BAM NPA properties (15,900+) | `python scraper.py` or `--province กรุงเทพมหานคร` |
| `jam-scraper` | Scrape JAM NPA properties | `python scraper.py` or `--limit 100` |
| `npa-adapter` | Unified query across all providers (LED/SAM/BAM/JAM/KTB/KBank) | `python query.py search --province "กรุงเทพ" --sources LED,BAM` |
| `led-query` | Query LED properties by location/price/date | `python query.py search --province "กรุงเทพ"` |
| `kb` | Temporal knowledge base (LightRAG + PostgreSQL) | `insert_document(content, desc, category, area, source)` |
| `flood-check` | Flood risk assessment (HIGH/MEDIUM/LOW) | `python flood_check.py --lat 13.95 --lon 100.62` |
| `location-intel` | BTS/MRT proximity, nearby amenities | `python location.py --lat 13.73 --lon 100.56` |
| `property-calc` | Acquisition cost, rental yield, break-even | `python calc.py --price 1.8M --sqm 35 ...` |
| `zoning-check` | Bangkok zoning rules (ผังเมือง พ.ศ. 2556) | `python zoning.py --lat 13.73 --lon 100.56` |
| `market-checker` | Verify NPA prices against DDProperty/Hipflat/ZMyHome | `python market_checker.py "project name" --no-ddproperty` |
| `npa-screener` | Screen NPA condos against investment criteria framework | See `SKILL.md` for scoring pipeline |
| `web-search` | Market research query patterns | Templates only, no scripts |
| `npa-journal` | Daily analysis journal & reflections | Write to `thoughts/YYYY-MM-DD.md` |
| `agent-comm` | Message other agents (Ada, Sentinel, Reviewer) | `bash ask_agent.sh "<msg>" "<workspace>"` |

## Scheduled Jobs (launchd)

| Job | Schedule | Script |
|-----|----------|--------|
| LED scraper | Daily 06:00 | `com.npa-guy.led-scraper` |
| SAM scraper | Daily 07:40 | `com.npa-guy.sam-scraper` |

## Core Rules

1. **Location first** — cheap property in bad location = not a deal
2. **Always both sides** — present BUY reasons AND AVOID reasons
3. **Specific numbers** — price/sqm, distance to BTS in meters, yield %
4. **Market comparison mandatory** — compare NPA price vs DDProperty/Hipflat
5. **Legal due diligence** — title deed, encumbrances, zoning, eviction risk
6. **Always ingest to KB** — every analysis ends with KB ingestion (non-negotiable)
7. **Planned infrastructure = zero value** — only OPERATIONAL or UNDER-CONSTRUCTION counts
8. **LED auction floor is 70%** — prices never drop below 70% of appraised value
9. **Flood risk is a filter** — HIGH risk needs 30%+ discount
10. **Rental yield: ranges not single estimates** — always LOW/MID/HIGH scenarios

## KB Ingestion Pattern

```python
insert_document(
    content="...",
    description="[area] [metric] [date]",
    category="pricing|rental|flood|legal|area|project|infrastructure",
    area="Thai area name",
    source="DDProperty|Hipflat|LED|SAM|web_search"
)
```

Categories expire: pricing/rental 90d, flood/infrastructure/project 365d, legal/area 180d.

**Do NOT store in KB**: zoning rules, tax rates, BTS coords, flood zones — these live in dedicated skills.

## Investment Screening Quick-Reference

### Auto-Reject (any one = stop)
- Leasehold < 30 years | Building > 20 years (pre-2006) | NPA ≥ market price
- Invalid title (นส.3 land) | Structural notice | NPA concentration > 8% in building

### Minimum Thresholds
- Real discount ≥ 20% vs DDProperty/Hipflat (NEVER trust provider appraisals)
- Building year 2008-2018 sweet spot
- Education anchor ≤ 800m | Market liquidity ≥ 3 resale listings
- Yield: ≥ 7% (university), ≥ 5.5% (school) — verified rental rates only

### BTS/MRT Tiers
- **A** (both < 800m): min 6% yield, 15% discount
- **B** (BTS 800-1500m): min 7% yield, 20% discount
- **C** (no BTS): min 8% yield, 25% discount + verified rental demand

### Education Anchor Unit Sizes
- University: 22-35 sqm studio, rent 5,500-9,000 THB/mo
- Intl School: 50-120 sqm 2-3BR, rent 30,000-100,000+ THB/mo
- Thai School: 35-80 sqm 1-2BR, rent 12,000-40,000 THB/mo

### Known Traps (April 2026)
- CU land properties = leasehold (Triple Y, IDEO Q จุฬา-สามย่าน)
- KBank premium projects at/above market (Park 24, Lumpini 24, Clover ลาดพร้าว 83)
- Provider "discount" is marketing — always verify on DDProperty/Hipflat

### Pre-Purchase Due Diligence
Juristic fund ≥ 70% | Arrears ≤ 24 months | GPS verified | Renovation ≤ 12% | Enrollment stable

**Full framework:** `workspace/AGENTS.md` → Investment Screening Framework section

## Inter-Agent Communication

| Agent | Workspace | Purpose |
|-------|-----------|---------|
| Ada | `~/.nanobot-stocks/` | Financial analysis, macro context |
| Sentinel | `~/.nanobot-sentinel/` | News monitoring, KB curation |
| Reviewer | `~/.nanobot-reviewer/` | Critical review of investment theses |

## Scraper Data Integrity

### Provider unique identifiers
| Scraper | Business ID | PK type | Notes |
|---------|------------|---------|-------|
| BAM | `asset_no` | `UNIQUE` constraint (PK is internal `id`) | Upsert keyed by `asset_no` |
| JAM | `asset_id` | Integer PK | Is the stable provider ID |
| KTB | `coll_grp_id` | Integer PK | Is the stable provider ID |
| KBank | `property_id` | String PK | Already stable string ID |
| SAM | `sam_id` | `UNIQUE` constraint (PK is autoincrement `id`) | |

### Price history duplicate guard
All price history tables (BAM/JAM/KTB/KBank) have:
- "new" entry only inserted if no prior history exists for that asset
- Change events (price/state) skipped if a record already exists within the last 1 hour

### Dedup scripts
Run after any bulk import or table restore:
```bash
python workspace/skills/bam-scraper/scripts/dedup.py [--apply]
python workspace/skills/jam-scraper/scripts/dedup.py [--apply]
python workspace/skills/kbank-scraper/scripts/dedup.py [--apply]
python workspace/skills/ktb-scraper/scripts/dedup.py [--apply]
```
Default is dry-run; pass `--apply` to execute.

## Development Notes

- Python scripts use **async httpx**, **selectolax**, **Pydantic v2**, **SQLAlchemy**
- Scrapers run with `asyncio.Semaphore(10)` for bounded concurrency
- Use `bun` instead of `npm`, `bunx` instead of `npx`
- `datetime.now()` used throughout (no timezone — machine runs local Bangkok time)
- User is expert-level, expects direct technical communication
- Thai location names used throughout (not transliterated)

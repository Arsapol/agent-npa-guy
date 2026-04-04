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
| Knowledge base | LightRAG vector/graph tables + `kb_metadata` |

- LED prices stored in **satang** (integer)
- SAM prices stored in **whole baht** (numeric)

## Skills

| Skill | Purpose | How to Run |
|-------|---------|------------|
| `led-scraper` | Scrape court auction properties from LED.go.th | `python main.py --agency "..." --max-pages 500` |
| `sam-scraper` | Scrape SAM NPA properties (4,700+) | `./run_scraper.sh` or individual scripts |
| `led-query` | Query LED properties by location/price/date | `python query.py search --province "กรุงเทพ"` |
| `kb` | Temporal knowledge base (LightRAG + PostgreSQL) | `insert_document(content, desc, category, area, source)` |
| `flood-check` | Flood risk assessment (HIGH/MEDIUM/LOW) | `python flood_check.py --lat 13.95 --lon 100.62` |
| `location-intel` | BTS/MRT proximity, nearby amenities | `python location.py --lat 13.73 --lon 100.56` |
| `property-calc` | Acquisition cost, rental yield, break-even | `python calc.py --price 1.8M --sqm 35 ...` |
| `zoning-check` | Bangkok zoning rules (ผังเมือง พ.ศ. 2556) | `python zoning.py --lat 13.73 --lon 100.56` |
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

## Inter-Agent Communication

| Agent | Workspace | Purpose |
|-------|-----------|---------|
| Ada | `~/.nanobot-stocks/` | Financial analysis, macro context |
| Sentinel | `~/.nanobot-sentinel/` | News monitoring, KB curation |
| Reviewer | `~/.nanobot-reviewer/` | Critical review of investment theses |

## Development Notes

- Python scripts use **async httpx**, **selectolax**, **Pydantic v2**, **SQLAlchemy**
- Scrapers run with `asyncio.Semaphore(10)` for bounded concurrency
- Use `bun` instead of `npm`, `bunx` instead of `npx`
- User is expert-level, expects direct technical communication
- Thai location names used throughout (not transliterated)

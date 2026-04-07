# Plan: Add 6 New Bank NPA Scrapers

**Date:** 2026-04-07
**Status:** COMPLETE
**Scope:** Add SCB, GSB, TTB, BAY, LH, GHB scrapers following existing patterns

---

## Requirements Summary

Add scraping support for 6 Thai bank NPA property websites:

| # | Bank | URL | Codename |
|---|------|-----|----------|
| 1 | SCB (ไทยพาณิชย์) | `asset.home.scb/project` | `scb-scraper` |
| 2 | GSB (ออมสิน) | `npa-assets.gsb.or.th` | `gsb-scraper` |
| 3 | TTB/PAMCO | `property.pamco.co.th` | `ttb-scraper` |
| 4 | BAY (กรุงศรี) | `krungsriproperty.com` | `bay-scraper` |
| 5 | LH Bank (แลนด์ แอนด์ เฮ้าส์) | `lhbank.co.th/.../asset-for-sale` | `lh-scraper` |
| 6 | GHB (ธอส.) | `ghbhomecenter.com` | `ghb-scraper` |

Each scraper must follow the **established pattern** from existing scrapers (BAM/KTB/KBank/JAM):

```
workspace/skills/{bank}-scraper/
├── SKILL.md
├── API_NOTES.md
├── recon/            # API exploration scripts + sample JSON
│   ├── test_api.py
│   └── *.json        # sample responses
├── scripts/
│   ├── scraper.py    # async httpx scraper
│   ├── models.py     # Pydantic v2 + SQLAlchemy 2.0
│   ├── database.py   # upsert + price history
│   ├── query.py      # CLI query tool
│   ├── dedup.py      # duplicate cleanup
│   └── run_scraper.sh
└── logs/
```

---

## Acceptance Criteria

- [ ] Each scraper can do a full scrape of all properties from its provider
- [ ] **Detail fetch for every property** — scraper fetches both list AND detail endpoints (or HTML detail page)
- [ ] DB tables: `{bank}_properties`, `{bank}_price_history`, `{bank}_scrape_logs`
- [ ] Prices stored in **whole baht** (Numeric), consistent with BAM/KTB/KBank/JAM
- [ ] Price history with 1-hour dedup window (no duplicate snapshots within same hour)
- [ ] Upsert keyed by provider's stable business ID (UNIQUE constraint)
- [ ] **Critical detail fields captured** (where provided by bank):
  - [ ] GPS coordinates (`lat`, `lon`)
  - [ ] Appraisal/assessed value (`appraised_value`)
  - [ ] Land area (`rai`, `ngan`, `wah` or `land_area_sqw`)
  - [ ] Usable area (`usable_area_sqm`)
  - [ ] Building details (`bedrooms`, `bathrooms`, `floors`, `building_year`)
  - [ ] Title deed type (`title_deed_type` — นส.4, นส.3 ก., etc.)
  - [ ] Project/village name (`project_name`)
  - [ ] Images (`image_urls` or stored in `raw_detail_json`)
  - [ ] Contact info (`contact_name`, `contact_tel`)
  - [ ] Sale conditions (`sale_type` — ขายขาด/เช่า, special discounts)
- [ ] `raw_search_json` + `raw_detail_json` JSONB columns for future-proofing
- [ ] `run_scraper.sh` wrapper with priority provinces (กรุงเทพ, ชลบุรี, นนทบุรี, ปทุมธานี, etc.)
- [ ] `dedup.py` with dry-run default + `--apply` flag
- [ ] `query.py` with search/detail/stats subcommands
- [ ] `SKILL.md` and `API_NOTES.md` documenting endpoints, fields, and field mapping (list vs detail)
- [ ] CLAUDE.md updated with new tables, provider IDs, and price units
- [ ] npa-adapter updated to include new providers in unified queries

---

## Skills to Invoke

Each agent **MUST** load these project skills before starting work:

1. **`/api-reverse-engineering`** — Recon methodology: JS bundle capture, crypto extraction, parameter discovery, auth patterns, Akamai bypass with Camoufox
2. **`/api-scraper-pattern`** — Build patterns: interleaved pipeline, sliding-window rate limiter, pagination cap workarounds, resilient Pydantic types, Text columns, price tracking upsert, recon-first workflow

Both skills live at `.claude/skills/` and are loaded per-session.

---

## Implementation Strategy

### Phase 0: Parallel API Reconnaissance (ALL 6 banks)

**Goal:** Discover each site's hidden API endpoints, authentication requirements, and anti-bot measures.

**Method per site** (following `/api-reverse-engineering` phases 1-5):
1. Load site with Camoufox/Playwright, intercept all JS + XHR responses
2. Search JS bundles for API endpoints, crypto patterns, and parameter construction
3. Replay API calls with plain httpx to confirm headless access works
4. Save raw responses to `recon/*.json`, document in `API_NOTES.md`
5. Write `recon/test_api.py` with endpoint verification
6. **Verify filters actually filter** (compare count with/without param — same count = wrong param)
7. **MANDATORY: Capture property detail page/API** — click through to at least 3 individual property pages and record ALL fields returned (see Detail Page Audit below)

### Detail Page Audit (MANDATORY for each bank)

The list/search API often returns only summary fields (name, price, location, type). The **detail page** typically has critical fields for investment analysis:

| Field Category | Examples | Why It Matters |
|---------------|----------|----------------|
| **Exact address** | ซอย, ถนน, หมู่, เลขที่ | GPS verification, deed lookup |
| **GPS coordinates** | lat/lon | Flood check, location-intel, zoning |
| **Appraisal value** | ราคาประเมิน | Real discount calculation (NPA price vs appraisal) |
| **Land area** | ไร่/งาน/ตร.ว. | Price-per-wah calculation |
| **Usable area** | ตร.ม. | Price-per-sqm, rental yield calc |
| **Building details** | ชั้น, ห้องนอน, ห้องน้ำ, ปีที่สร้าง, สภาพ | Age filter, renovation cost |
| **Title deed info** | เลขโฉนด, ประเภทเอกสารสิทธิ์ (นส.4, นส.3 ก.) | Legal risk (นส.3 = auto-reject) |
| **Sale conditions** | ขายขาด/เช่า, เงื่อนไขพิเศษ, ส่วนลด | Leasehold filter |
| **Images** | รูปทรัพย์ทั้งหมด | Visual condition check |
| **Contact** | ชื่อ, เบอร์, สาขา | For inquiry |
| **Project name** | ชื่อโครงการ/หมู่บ้าน | Market comparison matching |
| **Encumbrances** | ภาระผูกพัน, ผู้เช่า, สิทธิอาศัย | Legal due diligence |

**Recon deliverable per bank:** A field mapping table in `API_NOTES.md`:
```
## Field Mapping: List vs Detail

| Field | In List API? | In Detail API? | API Key | Notes |
|-------|-------------|----------------|---------|-------|
| Price | ✅ | ✅ | sell_price | |
| Appraisal | ❌ | ✅ | appraised_value | Only in detail |
| GPS | ❌ | ✅ | latitude, longitude | |
| Title type | ❌ | ❌ | N/A | Not provided by this bank |
...
```

**Decision rule update:** Even if the list API has >80% of fields, **always build the detail fetcher** if the detail page adds any of: GPS, appraisal value, building year, title deed type, or land/usable area. These are critical for the screening framework.

**Difficulty Assessment (from website analysis):**

| Bank | Frontend | API Likelihood | Anti-Bot Risk | Estimated Difficulty |
|------|----------|---------------|---------------|---------------------|
| **SCB** | SPA (React/Vue) | HIGH — SPA = JSON API behind search | LOW — bank sites rarely use Cloudflare | EASY |
| **GSB** | Next.js SSR | HIGH — Next.js data routes or API | LOW | EASY |
| **TTB** | Unknown (HTTP 500 on static fetch) | MEDIUM — may be SPA that needs JS | MEDIUM — 500 suggests SSR-only or WAF | MEDIUM |
| **BAY** | CMS-like (Kentico?) | HIGH — structured property codes visible (BX1538) | LOW | EASY |
| **LH** | Traditional HTML | MEDIUM — might be server-rendered with no API | LOW | MEDIUM (may need HTML parsing) |
| **GHB** | SPA + `/v3/property/api/` visible | VERY HIGH — API URL pattern already visible | LOW | EASY |

**Parallel execution:** All 6 recon tasks are independent → run as 6 parallel agents.

### Phase 1: Build Scrapers (3 waves)

Based on difficulty assessment, build in order of easiest first:

**Wave 1 (EASY — likely clean JSON APIs):**
- GHB (API pattern `/v3/property/api/` already visible)
- SCB (SPA → guaranteed JSON API)
- BAY (structured property codes → likely REST)

**Wave 2 (MEDIUM — may need HTML parsing or browser):**
- GSB (Next.js → might have `__NEXT_DATA__` or API routes)
- LH (traditional HTML → likely needs selectolax parsing)

**Wave 3 (HARD — needs investigation):**
- TTB/PAMCO (HTTP 500 on fetch → may need Camoufox/Playwright)

Each wave: 2-3 scrapers built in parallel by separate agents.

### Phase 2: Integration

1. Update `npa-adapter` to register all 6 new providers
2. Update `CLAUDE.md` with new table documentation
3. Add `run_scraper.sh` for each with priority provinces
4. Add launchd plist for daily cron (optional, can be done later)

---

## Detailed Steps

### Step 0.1 — Recon: GHB (ghbhomecenter.com)
- **Clue:** `/v3/property/api/Media/{id}` pattern visible in homepage
- **Action:** Try `GET /v3/property/api/Property/Search?...` and similar paths
- **Detail page:** Click a property → capture detail API call → map ALL returned fields
- **Files:** `workspace/skills/ghb-scraper/recon/test_api.py`, `API_NOTES.md`
- **Deliverable:** Field mapping table (list vs detail) + sample `search_response.json` + `detail_response.json`

### Step 0.2 — Recon: SCB (asset.home.scb)
- **Clue:** SPA with search form (property type, location, price range)
- **Action:** Intercept XHR during search to find API base URL
- **Detail page:** Navigate to a property detail → capture all XHR → identify detail endpoint
- **Files:** `workspace/skills/scb-scraper/recon/test_api.py`, `API_NOTES.md`
- **Deliverable:** Field mapping table + sample JSONs

### Step 0.3 — Recon: BAY (krungsriproperty.com)
- **Clue:** Property codes like BX1538, image URLs at `/images/{uuid}/00/01`
- **Action:** Find search/list and detail API endpoints
- **Detail page:** Open property BX1538 → capture detail response → check for appraisal, GPS, deed info
- **Files:** `workspace/skills/bay-scraper/recon/test_api.py`, `API_NOTES.md`
- **Deliverable:** Field mapping table + sample JSONs

### Step 0.4 — Recon: GSB (npa-assets.gsb.or.th)
- **Clue:** Next.js app with `/asset/npa/all` route
- **Action:** Check `/_next/data/` routes or API endpoints in JS bundle
- **Detail page:** Click a property → capture data route → map all fields returned
- **Files:** `workspace/skills/gsb-scraper/recon/test_api.py`, `API_NOTES.md`
- **Deliverable:** Field mapping table + sample JSONs

### Step 0.5 — Recon: LH (lhbank.co.th)
- **Clue:** Traditional HTML with filter dropdowns (province, property type)
- **Action:** Check if search form submits to an API or returns HTML
- **Detail page:** Click a property → check if detail is HTML (selectolax) or JSON API
- **Files:** `workspace/skills/lh-scraper/recon/test_api.py`, `API_NOTES.md`
- **Deliverable:** Field mapping table + sample HTML/JSON

### Step 0.6 — Recon: TTB/PAMCO (property.pamco.co.th)
- **Clue:** HTTP 500 on static fetch — likely requires browser rendering
- **Action:** Use Camoufox/Playwright to load page, intercept API calls
- **Detail page:** Navigate to a property → capture all network requests → map detail fields
- **Files:** `workspace/skills/ttb-scraper/recon/test_api.py`, `API_NOTES.md`
- **Deliverable:** Field mapping table + sample JSONs + notes on anti-bot measures

### Step 1.x — Build each scraper
For each bank (after successful recon):
1. Create `models.py` — Pydantic v2 parse models for **both search AND detail** responses + SQLAlchemy ORM with ALL detail fields
2. Create `database.py` — engine, create_tables, upsert_properties with price history (merge search + detail data into single `{bank}_properties` row)
3. Create `scraper.py` — async httpx with rate limiting + semaphore concurrency; **MUST fetch detail for every property** (interleaved or 2-phase depending on origin)
4. Create `query.py` — search/detail/stats CLI
5. Create `dedup.py` — duplicate cleanup
6. Create `run_scraper.sh` — cron wrapper
7. Create `SKILL.md` — documentation including field mapping table
8. Test with `--limit 10` then full scrape; **verify detail fields populated** (GPS, appraisal, area not null)

### Step 2.1 — Update CLAUDE.md
Add to database table group, unique identifiers table, and development notes.

### Step 2.2 — Update npa-adapter
Register SCB, GSB, TTB, BAY, LH, GHB as new providers with normalized field mapping.

---

## Team Assignment

### Recon Team (Phase 0) — 6 parallel agents (worktree isolation)
Each agent **invokes `/api-reverse-engineering`** then follows its 8 phases:
1. Capture JS bundles (Camoufox `headless=True` for blocked sites, Playwright for others)
2. Grep for crypto patterns (AES, CryptoJS, decrypt, importKey)
3. Find correct API parameter names from JS source (NOT guessing)
4. Handle auth (cookie acquisition if needed)
5. Test with httpx — save responses to `recon/*.json`
6. Document in `API_NOTES.md`

**Agent type:** `general-purpose` (needs browser + HTTP tools)
**Isolation:** Each in its own worktree to avoid conflicts
**Output:** `API_NOTES.md` + `recon/test_api.py` + sample JSONs per bank

### Build Team (Phase 1) — 2-3 parallel agents per wave
Each agent **invokes `/api-scraper-pattern`** then follows its patterns:
1. Decide architecture: interleaved pipeline (separate subdomains) vs 2-phase sequential (same origin) [Pattern 13]
2. Create `models.py` — union types for inconsistent fields [Pattern 4], Text columns [Pattern 5]
3. Create `database.py` — upsert + price history with 1-hour dedup [Pattern 6]
4. Create `scraper.py` — sliding-window rate limiter [Pattern 1], retry 500s [Pattern 2]
5. Create `run_scraper.sh` with `python -u` [Pattern 14]
6. Test incrementally: `--limit 10` → single province → full scrape [Pattern 11]

**Agent type:** `oh-my-claudecode:executor` (model=sonnet)
**Key decision rules from skill:**
- List API has >80% fields needed → skip detail, use list-only architecture [Pattern 17]
- Akamai/WAF on detail pages → separate `detail.py` with Camoufox [Pattern 16]
- Same origin for search+detail → 2-phase sequential, NOT interleaved [Pattern 13]
- Dropdown filters → resolve codes, not display names [Pattern 12]

### Integration (Phase 2) — 1 agent
Update CLAUDE.md, npa-adapter, verify all scrapers run end-to-end.

---

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| TTB/PAMCO returns 500 — may be completely down or geo-blocked | Can't scrape TTB | Check if site works in browser first; defer to last; may need VPN or PAMCO mobile app API instead |
| Some banks use Akamai/Cloudflare WAF | Blocked after N requests | Use Camoufox (already used for KBank); add to recon checklist |
| Encrypted API responses (like JAM) | Need to reverse-engineer JS | Apply JAM crypto.py pattern — extract key from JS bundle |
| Rate limiting / IP bans | Scraper gets blocked mid-run | Use existing sliding-window rate limiter pattern; add backoff |
| Server-rendered HTML (no JSON API) | More fragile scraper | Use selectolax (project standard) for HTML parsing; document CSS selectors |
| Different property ID schemes per bank | Hard to track unique assets | Each scraper defines its own stable business ID; document in CLAUDE.md |

---

## Verification Steps

1. Each scraper: `python scraper.py --create-tables` succeeds
2. Each scraper: `python scraper.py --limit 10` returns properties with detail data populated
3. **Detail coverage check per scraper:**
   ```sql
   -- Must return >0 for all fields the bank provides
   SELECT
     COUNT(*) as total,
     COUNT(lat) as has_gps,
     COUNT(appraised_value) as has_appraisal,
     COUNT(usable_area_sqm) as has_area,
     COUNT(project_name) as has_project,
     COUNT(raw_detail_json) as has_detail_json
   FROM {bank}_properties
   WHERE last_scraped_at > NOW() - INTERVAL '1 hour';
   ```
   - `has_detail_json` must equal `total` (every row fetched detail)
   - Other fields: >0 where the bank provides them (documented in API_NOTES.md)
4. Each scraper: `python query.py stats` shows expected counts
5. Price history: Run scraper twice → verify no duplicate snapshots within 1 hour
6. Dedup: `python dedup.py` (dry-run) reports 0 duplicates after clean scrape
7. npa-adapter: `python query.py search --province กรุงเทพ --sources SCB,GSB,TTB,BAY,LH,GHB` returns results
8. **Field mapping verification:** Compare `API_NOTES.md` field mapping table against actual DB columns — no unmapped fields that the bank provides

---

## Execution Recommendation

**Recommended approach:** Start with Phase 0 (recon) for all 6 banks in parallel. This is the highest-uncertainty phase — we need to discover each site's API before we can build anything. Once recon is done, Wave 1-3 builds can proceed rapidly since the code pattern is well-established.

**Estimated scope per scraper:**
- Recon: ~30 min per site (variable — TTB could be longer)
- Build: ~20 min per site (templated from BAM/KTB)
- Integration: ~10 min total

**Total: ~6 scrapers x ~50 min = ~5 hours of agent time, parallelizable to ~2 hours wall clock.**

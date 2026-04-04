---
name: api-scraper-pattern
description: Proven patterns for building async Python scrapers against Thai government and bank NPA APIs (LED, SAM, BAM, JAM). Covers interleaved pipeline architecture, rate limiting, pagination caps, resilient type handling, and PostgreSQL upsert with price tracking. Triggers when building a new NPA property scraper, adding a new auction source, or reverse-engineering a Thai financial API.
---

# NPA API Scraper Pattern

Battle-tested architecture for scraping Thai NPA (Non-Performing Asset) property APIs. Extracted from 4 production scrapers: BAM, JAM, SAM, LED.

## When to use

- Building a new scraper for a Thai gov/bank NPA source
- Refactoring an existing scraper for performance
- Debugging rate limit or pagination issues on Thai APIs

## Architecture: Interleaved Pipeline

Search and detail endpoints typically live on **different subdomains** with **independent rate limits**. Run them concurrently:

```
asyncio.Queue (maxsize=200)
     ↑                    ↓
Search Producer      Detail Consumer Pool
(sequential,         (20 concurrent workers,
 rate-limited)        separate httpx client)
     ↓                    ↓
         Merge → Upsert to PostgreSQL
```

**Why interleaved?** BAM search takes ~15 min alone; details take ~10 min. Running both concurrently: ~3.7 min total.

Reference implementation: `workspace/skills/bam-scraper/scripts/scraper.py`

## File structure for new scrapers

```
workspace/skills/{source}-scraper/
├── SKILL.md              # Agent-oriented docs
├── API_NOTES.md          # Rate limits, gotchas, field maps
├── scripts/
│   ├── models.py         # Pydantic v2 (parsing) + SQLAlchemy 2.0 (DB)
│   ├── database.py       # Engine, create_tables, upsert + price tracking
│   ├── scraper.py        # Async httpx scraper with pipeline
│   └── query.py          # CLI for searching local DB
└── recon/                # Test API responses saved as JSON
    ├── test_api.py       # Initial endpoint testing
    └── verify_fields.py  # Field coverage verification
```

## Pattern 1: Sliding window rate limiter

Thai gov APIs rate-limit at ~30 req/60s but return **500 (not 429)**. Use a sliding window:

```python
class SlidingWindowLimiter:
    def __init__(self, max_requests: int, window_seconds: float):
        self._max = max_requests
        self._window = window_seconds
        self._timestamps: list[float] = []

    async def acquire(self) -> None:
        now = time.monotonic()
        cutoff = now - self._window
        self._timestamps = [t for t in self._timestamps if t > cutoff]
        if len(self._timestamps) >= self._max:
            wait = self._timestamps[0] - cutoff
            if wait > 0:
                await asyncio.sleep(wait)
        self._timestamps.append(time.monotonic())
```

**Defaults:** Start with `max_requests=28, window_seconds=60`. Adjust based on observed 500 threshold.

## Pattern 2: Retry strategy for 500-as-rate-limit

```python
async def fetch_with_retry(client, method, url, json_body=None, max_retries=2, base_delay=10.0):
```

- **max_retries=2** — fast-fail. Retrying the SAME request during a rate limit window always fails.
- **base_delay=10s** — exponential: 10s, 20s. Don't waste minutes on doomed retries.
- After failure, **move on** — the next different request after cooldown will succeed.

## Pattern 3: Pagination cap workaround (district drilling)

Some APIs report `totalData: 3276` but silently return empty arrays after page ~32 (~1600 results).

```python
MAX_SEARCH_RESULTS = 1600

if total > MAX_SEARCH_RESULTS:
    districts = await fetch_districts(client, province)
    for dist in districts:
        items = await scrape_partition(client, province, district=dist, seen_ids=seen_ids)
```

**Key:** Use `seen_ids: set[int]` to deduplicate across partitions.

## Pattern 4: Resilient Pydantic types

Thai bank APIs return **wildly inconsistent types** for the same field across assets:

```python
# WRONG — will crash on real data
is_campaign: str | None = None
campaign_name: str | None = None

# CORRECT — handle all observed variants
is_campaign: str | int | None = None          # API returns 0, 1, "true", null
campaign_name: str | list | None = None       # API returns "name", ["name"], null
hot_deals: dict | list | None = None          # API returns {}, [], null
property_highlight: str | bool | None = None  # API returns "text", False, null
```

## Pattern 5: Always use Text columns

**Never use `varchar(N)` for external API data.** A field that looks like `"1"` can suddenly be `"โปรดเลือก"` (9 Thai chars).

```python
# WRONG
stars: Mapped[str | None] = mapped_column(String(5))

# CORRECT
stars: Mapped[str | None] = mapped_column(Text)
```

Use `Text` for ALL string columns from external APIs. Only use `String(N)` for columns YOU control (like `change_type`).

## Pattern 6: Price tracking with upsert

Three tables per scraper:

| Table | Purpose |
|-------|---------|
| `{source}_properties` | Current state, upserted each run |
| `{source}_price_history` | Append-only log of changes |
| `{source}_scrape_logs` | Run metadata |

Change types to track: `new`, `price_change`, `state_change`

```python
def upsert_properties(session, properties):
    # Bulk-load existing by ID
    existing_map = {row.id: row for row in session.execute(select(Model).where(...))}

    for item in properties:
        if item.id not in existing_map:
            # INSERT + price_history(change_type="new")
        else:
            old = existing_map[item.id]
            if price_changed(old, item):
                # UPDATE + price_history(change_type="price_change")
            if state_changed(old, item):
                # UPDATE + price_history(change_type="state_change")
```

## Pattern 7: Fresh client per partition

```python
for province in provinces:
    async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
        items = await scrape_province(client, province)
    # Client closes, connections released
```

Prevents connection pool exhaustion on long-running scrapes across 78 provinces.

## Pattern 8: Recon-first development

Before writing the scraper:

1. **Test endpoints** — Save raw responses as JSON in `recon/`
2. **Check field types** — Print every field's type and sample value
3. **Verify field coverage** — Script that checks model fields vs API keys (0 missing = done)
4. **Test with small limit** — `--limit 5` before full scrape

```python
# recon/verify_fields.py
model_fields = {name for name, _ in Model.model_fields.items()}
api_keys = set(response.keys())
missing = api_keys - model_fields
assert len(missing) == 0, f"Missing: {missing}"
```

## Existing scrapers for reference

| Source | Dir | API Style | Rate Limit | Notes |
|--------|-----|-----------|-----------|-------|
| BAM | `bam-scraper/` | REST JSON, search+detail | ~30/60s on search | District drilling for BKK, interleaved pipeline |
| JAM | `jam-scraper/` | REST JSON, AES-GCM encrypted | ~30/60s | Needs `crypto.py` for decryption |
| SAM | `sam-scraper/` | HTML scraping + AJAX | Moderate | Dropdown cache, separate list/detail scripts |
| LED | `led-scraper/` | REST JSON (court auctions) | Low | Prices in satang (not baht) |

## Degrees of freedom

**Claude MUST follow:**
- Text columns for all external string data
- Union types for inconsistent API fields
- Recon-first workflow (test → verify → scrape)
- Price history tracking pattern
- `raw_json` / `raw_detail_json` JSONB columns for future-proofing

**Claude decides:**
- Rate limiter parameters (based on observed 500 threshold)
- Detail concurrency level (based on endpoint behavior)
- Whether to use interleaved pipeline (only if separate search+detail endpoints)
- Partition strategy for pagination caps (district, asset type, price range, etc.)

## Pattern 9: Concurrency — parallel partitions, sequential pages

APIs that 502 on concurrent deep pagination still handle concurrent *different* queries fine.

```python
# WRONG: 5 concurrent pages to the same query → 502
sem = asyncio.Semaphore(5)
tasks = [fetch_page(client, page=p, province=1) for p in range(1, 20)]

# RIGHT: 8 different amphurs in parallel, each paginating sequentially inside
AMPHUR_CONCURRENCY = 8
sem = asyncio.Semaphore(AMPHUR_CONCURRENCY)

async def scrape_amphur(amp):
    async with sem:
        for page in range(1, total_pages + 1):  # sequential within
            await fetch_page(client, page=page, province=prov, district=amp)

await asyncio.gather(*[scrape_amphur(a) for a in amphurs])  # parallel across
```

**Also test larger page sizes** — `limit=200` vs `limit=50` = 4x fewer requests with no penalty.

## Pattern 10: Debug logging from day one

Every scraper call must log immediately. Never batch logs or log only at milestones.

```python
# WRONG: only logs every 50 pages — looks stuck between logs
if p % 50 == 0:
    print(f"Page {p}/{total}")

# RIGHT: every partition logs on entry and completion with timing
t0 = time.time()
result = await fetch_page(...)
print(f"[{prov}/{amp}] {total} items, {pages}p ({time.time()-t0:.1f}s)")
# ... paginate ...
print(f"[{prov}/{amp}] done: {len(props)} scraped, {fails} fails ({time.time()-t0:.1f}s)")
```

## Pattern 11: Test with timeouts, not open-ended runs

```bash
# Quick validation (60s) before full run
perl -e 'alarm 60; exec @ARGV' python -u scraper.py --limit 200

# Only after this passes cleanly:
python -u scraper.py  # full run
```

Never `sleep 120 && tail` to check background progress. Use hard timeouts for fast feedback.

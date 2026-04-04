---
name: api-reverse-engineering
description: Reverse-engineers protected web APIs by analyzing frontend JS bundles to extract encryption keys, correct parameter names, and authentication patterns. Triggers when the user needs to scrape a site with encrypted API responses, client-side rendering, or undocumented API parameters.
---

# API Reverse Engineering

Methodology for building scrapers against protected/encrypted web APIs by analyzing the frontend JavaScript source code.

## When to use

- Site uses CSR (client-side rendering) and fetches data via API
- API responses are encrypted or obfuscated
- API parameters are undocumented and guessing returns wrong results
- Site requires specific cookies/session tokens for API access

## Phase 1: Reconnaissance — capture JS bundles

Use Playwright or Camoufox to load the site and capture all JS files.

**IMPORTANT:** `playwright_stealth` API changed. The old `stealth_async(page)` import no longer exists. Use:

```python
# OLD (broken) — ImportError
from playwright_stealth import stealth_async
await stealth_async(page)

# NEW (correct)
from playwright_stealth import Stealth
stealth = Stealth()
await stealth.apply_stealth_async(context)  # pass context, not page
page = await context.new_page()
```

**If Akamai blocks Playwright entirely**, use Camoufox instead (see Phase 7).

```python
from camoufox.async_api import AsyncCamoufox

async with AsyncCamoufox(headless=True, humanize=True) as browser:
    page = await browser.new_page()

    # Intercept all JS responses
    js_sources = {}
    page.on("response", lambda resp: capture_js(resp, js_sources))

    await page.goto(url, wait_until="networkidle")
```

Save all JS bundles locally for grep analysis. Do NOT try to read minified JS in context — save to files and search with regex.

## Phase 2: Find encryption logic

Search downloaded JS files for crypto patterns:

```python
patterns = {
    "CryptoJS": r"CryptoJS",
    "_encrypted": r"_encrypted",
    "decrypt": r"\.decrypt\(",
    "split_colon": r'split\(["\']:["\']',
    "AES": r"\bAES\b",
    "importKey": r"importKey",
    "secret": r"secretKey|secret_key|encryptKey",
}
```

When found, extract surrounding context (~300 chars) to understand:
1. The algorithm (AES-GCM, AES-CBC, etc.)
2. The key (often hardcoded as a string constant near the decrypt function)
3. The format (how iv, tag, ciphertext are packed — usually colon-separated hex)

## Phase 3: Find correct API parameters

**This is where most mistakes happen.** The frontend JS is the ONLY source of truth for parameter names and values.

Search for the API endpoint call (e.g., `/v1/assets`) and read how parameters are built:

```javascript
// Example from real site — note the naming:
d.get("/v1/assets", {params: {
    Province: r.value.province,      // PROVINCE_ID, not PROVINCE_CODE!
    District: r.value.amphur,        // AMPHUR_ID, not AMPHUR_CODE!
    SubDistrict: r.value.district,   // DISTRICT_ID
    "typeSaleIn[]": n.value,         // array param
}})
```

**Common traps:**
- Dropdown values have multiple ID fields (`CODE` vs `ID`) — the API uses one, not the other
- Parameter names may be case-sensitive (`Province` works, `province` doesn't)
- Array params need `[]` suffix (`typeSaleIn[]`, not `typeSaleIn`)
- Some params are silently ignored if wrong — no error, just unfiltered results

**Verification method:** Make one request with the filter, check if `count` actually changes vs unfiltered. If count stays the same, the parameter is being ignored.

## Phase 4: Handle authentication

Check if the API requires session cookies:

1. Make an API call without cookies → note the response (500? empty? redirect?)
2. Visit the homepage first to get `Set-Cookie` headers
3. Use an HTTP client that persists cookies across requests (`httpx.Client`)
4. Re-init the session periodically (cookies expire)

```python
async with httpx.AsyncClient(timeout=120.0, follow_redirects=True) as client:
    # Acquire cookie
    await client.get("https://example.com/")
    # Now API calls work
    resp = await client.get("https://example.com/api/data", params={...})
```

## Phase 5: Handle slow/unreliable backends

When deep pagination causes 502/timeout errors, the backend DB is the bottleneck.

**Solution: partition queries to keep result sets small.**

```
Instead of: /assets?page=1..798 (39K results)
Do:         /assets?Province=1&page=1..3  (120 results)
            /assets?Province=2&page=1..5  (250 results)
            ...one province at a time
```

**Rules:**
- Sequential pagination within a partition (concurrent causes 502)
- Can run different partitions concurrently if the API handles it
- Refresh cookies every N partitions
- Log EVERY request immediately (timing + status) — never batch logs
- Test with short timeouts (`timeout 60 python scraper.py`) for fast feedback

## Phase 6: Production scraper pattern

```
scripts/
├── crypto.py      # Decrypt/encrypt utility
├── models.py      # Pydantic v2 (parsing) + SQLAlchemy (storage)
├── database.py    # Upsert with change detection
├── scraper.py     # Main async scraper
└── run_scraper.sh # Shell wrapper
```

Key design decisions:
- Store `raw_json` JSONB column — future-proof against schema changes
- Track price changes in a separate history table (only insert on actual change)
- Detect status transitions (sold/unsold) by comparing with previous scrape
- Use `Text` columns for any user-generated string fields (names overflow `VARCHAR(255)`)

## Development workflow — test incrementally

**Never stack multiple fixes before testing.** One change → short timeout test → confirm → next change.

```bash
# WRONG: edit 3 things, run full scrape, wait 20 min, discover it's broken
# RIGHT: edit 1 thing, test with timeout
perl -e 'alarm 60; exec @ARGV' python -u scraper.py --limit 100
```

**Unbuffered output is mandatory** during development: `python -u` ensures logs appear immediately. Without it, the process appears stuck when it's actually working.

**Verify filters actually filter.** A silently-ignored parameter returns the same `count` as unfiltered. Always compare:
```python
# If count_with_filter == count_without_filter, the param is being ignored
```

## Phase 7: Akamai Bot Manager bypass

Akamai runs **sensor.js** (~50KB fingerprinting engine) that checks CDP `Runtime.Enable` leak, WebGL renderer, canvas hash, TLS fingerprint, and behavioral signals. Most automation tools fail.

**What doesn't work:**
- `httpx` / `requests` → 403
- `curl_cffi` (TLS impersonation only) → Gets PoW challenge, can't execute JS
- `curl_cffi` + manual PoW solver → Solves PoW (200 from `/_sec/verify`), but retry still 403 due to fingerprint validation
- Playwright headless + stealth → 403
- nodriver headless → 403
- nodriver headed → Works but shows browser window

**What works:**
- **Camoufox `headless=True`** — patches Firefox at C++ level, all fingerprints spoofed before JS executes

```python
from camoufox.async_api import AsyncCamoufox

async with AsyncCamoufox(headless=True, humanize=True) as browser:
    page = await browser.new_page()
    await page.goto(url, wait_until="networkidle")
    html = await page.content()
```

**Install:** `pip install 'camoufox[geoip]' && python -m camoufox fetch`

**Platform notes:**
- `headless=True` works on macOS and Linux
- `headless="virtual"` (Xvfb) only works on Linux
- Slow (~8s/page) — only for detail enrichment, not bulk scraping

**Architecture:** If only detail pages are Akamai-protected (list API works with httpx), build two separate scripts: `scraper.py` (httpx, bulk) + `detail.py` (Camoufox, on-demand).

## Phase 8: ASP.NET double JSON parse

Some sites (KBank) use ASP.NET WebMethods that wrap JSON in `{"d": "<json-string>"}`. The `d` value is a **string**, not an object:

```python
# Response: {"d": "{\"Success\":true,\"Data\":{...}}"}
raw = response.json()         # {"d": "<string>"}
inner = json.loads(raw["d"])  # {"Success": true, "Data": {...}}
```

**How to detect:** If `response.json()["d"]` returns a string starting with `{`, it needs double-parsing.

## Debugging checklist

When the scraper fails silently or returns wrong data:

1. **Wrong results but no error?** → Check parameter names/values against JS source
2. **500 or timeout?** → Check if cookie is set, try visiting homepage first
3. **502 on deep pages?** → Partition the query, reduce result set size
4. **Stuck with no output?** → Add per-request logging with timing
5. **Encryption changed?** → Re-run Playwright recon, check for new JS bundle hashes
6. **Filter param ignored?** → Compare count with and without the param — same count means wrong param name/value
7. **Dropdown IDs don't match API filter?** → Read the JS that builds the request — it maps dropdown fields to param values (e.g., `AMPHUR_ID` not `AMPHUR_CODE`)

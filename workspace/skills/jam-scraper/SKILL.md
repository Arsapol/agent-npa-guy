# JAM Scraper (JMT Network Services — BaanBaan Property)

## Site

- URL: `https://www.jjpropertythai.com`
- Nuxt 3 CSR app, API at `/api/proxy/v1/`
- Backend: `https://api.jjpropertythai.com/baanbaan/` (403 direct, must go through proxy)
- ~39,871 properties as of 2026-04-04

## API Encryption

All API responses are **AES-256-GCM** encrypted.

- Key: `QWT9g38M6fwBzJcbCjRjIBqn97UBm1Cf` (32 bytes, hardcoded in `_nuxt/tVx1KLp4.js`)
- Response format: `iv_hex:tag_hex:ciphertext_hex`
- Decrypt: `AESGCM(key).decrypt(iv, ciphertext + tag, None)`
- Implementation: `scripts/crypto.py`

## API Authentication

**Cookie required.** The API returns 500/timeout without a valid `cookiesession1` cookie.

1. Visit `https://www.jjpropertythai.com/` — server sets `cookiesession1` via `Set-Cookie`
2. Use that cookie for all subsequent API calls
3. Cookie may expire after ~100 requests — refresh by revisiting homepage

## API Endpoints

| Endpoint | Purpose |
|----------|---------|
| `GET /api/proxy/v1/assets` | List properties (paginated, filtered) |
| `GET /api/proxy/v1/asset/{id}` | Single property detail (singular!) |
| `GET /api/proxy/v1/dropdown/province` | Province list |
| `GET /api/proxy/v1/dropdown/amphur` | All amphurs (no param needed) |
| `GET /api/proxy/v1/dropdown/district` | All subdistricts/tambons |
| `GET /api/proxy/v1/dropdown/typeAsset` | Property type list |
| `GET /api/proxy/v1/dropdown/typeSell` | Sale type list |
| `GET /api/proxy/v1/dropdown/company` | Company list |

## Filter Parameters (for `/assets`)

**CRITICAL:** Parameter names and values come from JS source `B5or3bo8.js`. Using wrong IDs returns wrong results silently (no error, just unfiltered data).

| Param | Value | Source |
|-------|-------|--------|
| `Province` | `PROVINCE_ID` (1-77) | dropdown/province → `PROVINCE_ID` |
| `District` | `AMPHUR_ID` (1-998) | dropdown/amphur → `AMPHUR_ID` |
| `SubDistrict` | `DISTRICT_ID` (1-8887) | dropdown/district → `DISTRICT_ID` |
| `typeSaleIn[]` | Sale type code | dropdown/typeSell → `Type_Sale_Code` |
| `typeAssets[]` | Asset type code | dropdown/typeAsset → `Type_Asset_Code` |
| `companyCodeIn[]` | Company code | dropdown/company → `Company_Code` |
| `freeText` | Search text | |
| `page` | Page number (1-based) | |
| `limit` | Items per page (default 12, max 50) | |
| `SellingStart` / `SellingEnd` | Price range (baht) | |
| `user_code` | Always `"521789"` | Hardcoded in frontend |

**Common mistakes:**
- `PROVINCE_CODE` (10, 11, ...) ≠ `PROVINCE_ID` (1, 2, ...) — API uses `PROVINCE_ID`
- `AMPHUR_CODE` (1001, 1002, ...) ≠ `AMPHUR_ID` (1, 2, ...) — API uses `AMPHUR_ID`
- `provinceIn[]` does NOT work — must use `Province` (capital P, no array)
- Unfiltered queries (no Province param) return all 39K+ results and cause backend 502 on deep pages

## Scraping Strategy

The backend database is slow. Deep pagination (page 100+) causes 502 timeouts.

**Solution: partition by Province → Amphur → SubDistrict**

```
For each province:
  For each amphur in province:
    Fetch page 1 → get count
    If count > 50 pages:
      Drill into subdistricts
    Else:
      Paginate sequentially (one page at a time)
```

**Performance characteristics:**
- Page 1 of any query: 2-30s (cold start)
- Subsequent pages: 2-15s each
- Concurrent requests to SAME partition → 502 errors
- Concurrent requests to DIFFERENT partitions → OK but risky
- Sequential within partition is safest
- Bangkok (province_id=1) has ~18,600 properties across 51 amphurs — takes longest

## Sold-Out Detection

| Field | Value when sold |
|-------|----------------|
| `Status_Soldout` | `True` |
| `Image_Sold_Out` | URL to soldout overlay image |
| `Images_Main_Web` | Swapped to soldout image |
| `Soldout_date` | Often `null` (unreliable) |

## Database

PostgreSQL: `postgresql://arsapolm@localhost:5432/npa_kb`

| Table | Purpose |
|-------|---------|
| `jam_properties` | All properties with 102 API fields + `raw_json` JSONB |
| `jam_price_history` | Price changes tracked per scrape (new/price_change/sold/unsold) |
| `jam_scrape_logs` | Scrape run metadata |

Prices stored in **whole baht** (Numeric), not satang.

## Usage

```bash
cd scripts/

# Create tables
python scraper.py --create-tables

# Test scrape (first 200 properties)
python scraper.py --limit 200

# Full scrape (~30-60 min)
python scraper.py

# Shell wrapper
./run_scraper.sh
```

## File Layout

```
jam-scraper/
├── SKILL.md                          # This file
├── scripts/
│   ├── crypto.py                     # AES-GCM decrypt
│   ├── models.py                     # Pydantic v2 + SQLAlchemy models
│   ├── database.py                   # Upsert + price history tracking
│   ├── scraper.py                    # Main scraper (async httpx)
│   └── run_scraper.sh                # Shell wrapper
└── recon/
    ├── crack_encryption.py           # JS analysis → found AES key
    ├── diagnose_api.py               # API timeout/error diagnostics
    ├── test_decrypt.py               # Decryption proof-of-concept
    ├── browse_and_capture.py         # Playwright browser capture
    ├── intercept_and_decrypt.py      # Playwright data interception
    ├── scrape_all.py                 # Early recon scraper (superseded)
    ├── js_sources/                   # Downloaded Nuxt JS bundles
    │   └── tVx1KLp4.js              # Contains AES key + decrypt logic
    │   └── B5or3bo8.js              # Contains search API param building
    └── data/                         # Recon output (dropdowns, samples)
```

## Known Issues

1. API is slow (2-30s per request) — their backend DB is the bottleneck
2. Deep pagination (>100 pages unfiltered) causes 502 — solved by province/amphur partitioning
3. Cookie expires periodically — scraper refreshes every 20 provinces
4. `Soldout_date` is often null even for sold properties — use `Update_date` as proxy
5. Encryption key is hardcoded in JS — may change on site redeploy (check `tVx1KLp4.js`)

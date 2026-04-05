# DDProperty.com API Recon Report

**Date:** 2026-04-04  
**Investigator:** Camoufox + httpx recon  
**Status:** WORKING — prototype validated on 3 projects

---

## TL;DR

DDProperty uses Cloudflare Bot Management (not Akamai). The key strategy:
1. Use **Camoufox** once to acquire `cf_clearance` + `__cf_bm` cookies (~8s)
2. Use **httpx** with those cookies for all subsequent API calls (fast, lightweight)
3. Primary data path: `/_next/data/{BUILD_ID}/en/condo-for-sale.json?freetext=...`
4. Project metadata path: `/api/consumer/project?name=...`

---

## Anti-Bot Measures

| Method | Result |
|--------|--------|
| Plain `httpx` / `requests` | **403 Cloudflare** — blocked immediately |
| `curl` | **403 Cloudflare** |
| Playwright headless | **Not tested** (Camoufox used directly) |
| **Camoufox `headless=True`** | **WORKS** — gets past CF, acquires cookies |
| httpx + CF cookies from Camoufox | **WORKS** — all subsequent API calls pass |

### Cloudflare Cookie Flow

```
1. Camoufox loads https://www.ddproperty.com/en
2. CF Bot Management runs sensor.js → evaluates fingerprint
3. Camoufox passes → CF sets cookies:
     - cf_clearance     (the session token)
     - __cf_bm          (bot management token)
     - _cfuvid          (CF unique visitor ID)
     - pgutid           (PropertyGuru user tracking)
     - sixpack_client_id (A/B testing)
     - _dd_s            (Datadog session)
4. Use these cookies in all httpx calls → 200 OK
```

**Cookie TTL:** `cf_clearance` appears valid for ~30 minutes in testing.  
**Re-acquisition:** Re-run Camoufox session when cookies expire (status 403 on httpx).

---

## API Endpoints Discovered

### 1. Primary Search API — Next.js Data Endpoint

```
GET /_next/data/{BUILD_ID}/en/condo-for-sale.json
GET /_next/data/{BUILD_ID}/en/condo-for-rent.json
```

**Parameters (query string):**

| Param | Type | Example | Notes |
|-------|------|---------|-------|
| `freetext` | string | `triple y residence samyan` | Project name or area |
| `listingType` | string | `sale` \| `rent` | Match the URL slug |
| `page` | int | `1`, `2`, ... | Pagination |
| `propertyTypeCode` | string | `CONDO` | Filter by type |
| `propertyTypeGroup` | string | `N` | N=non-landed, B=bungalow |
| `region_code` | string | `TH10` | Bangkok = TH10 |
| `bedrooms` | int | `1`, `2` | Bedroom count |
| `minPrice` | int | `1000000` | Min price (THB) |
| `maxPrice` | int | `10000000` | Max price (THB) |
| `minSize` | float | `30` | Min sqm |
| `maxSize` | float | `100` | Max sqm |

**Response structure:**
```json
{
  "pageProps": {
    "pageData": {
      "resultCount": 19,
      "searchParams": { "freetext": "...", "listingType": "sale", "page": 1 },
      "data": {
        "listingsData": [ ...listing objects... ],
        "paginationData": { "totalPages": 1 }
      }
    }
  }
}
```

**Listing object key fields:**
```json
{
  "listingData": {
    "id": 500034318,
    "statusCode": "ACT",
    "typeCode": "SALE",
    "price": { "value": 5600000, "currency": "THB" },
    "floorArea": 33.45,
    "bedrooms": 1,
    "bathrooms": 1,
    "psfText": "฿167,414 / sqm",
    "pricePerArea": { "localeStringValue": "฿167,414 / sqm" },
    "url": "https://www.ddproperty.com/en/property/...-500034318",
    "property": { "id": 7006 },
    "fullAddress": "Rama 4 Road, Wang Mai, Pathum Wan, Bangkok",
    "listingFeatures": [
      { "text": "33 sqm" },
      { "text": "Built: 2019" },
      { "text": "Leasehold" }
    ]
  }
}
```

**Build ID:** `eSYGxg6TJlYl4EPdcSFiR`  
Changes when DDProperty deploys a new frontend. Fetch dynamically from homepage:
```python
import re, httpx
resp = httpx.get("https://www.ddproperty.com/en", cookies=cf_cookies)
build_id = re.search(r'"buildId"\s*:\s*"([^"]+)"', resp.text).group(1)
```

---

### 2. Project Lookup API

```
GET /api/consumer/project
```

**Parameters:**

| Param | Required | Example |
|-------|----------|---------|
| `name` | Yes | `triple y residence samyan` |
| `locale` | Yes | `en` |
| `region` | Yes | `th` |
| `size` | No | `5` (default 20) |
| `page` | No | `1` |

**Response:**
```json
{
  "total": 2,
  "size": 2,
  "data": [
    {
      "id": 34797,
      "property_id": 7006,       ← use this in SRP freetext filter
      "name": "Triple Y Residence Samyan",
      "completion_year": 2019,
      "total_units": 516,
      "starting_price": { "value": 4490000, "unit": "THB" },
      "max_price": { "value": null, "unit": "THB" },
      "developer_name": "Golden Land Property Development",
      "property_type_code": "CONDO",
      "postcode": "10330",
      "adm_level1": "TH10",      ← Bangkok
      "adm_level2": "TH1007",    ← Pathum Wan district
      "tenure_code": "L"         ← L=Leasehold, F=Freehold
    }
  ]
}
```

**Notes:**
- `property_id` is the numeric ID used in URL slugs (`/en/project/7006-triple-y-residence-samyan`)
- `id` is the internal developer listing ID — use `property_id` for project page URLs
- Returns fuzzy matches — always check `name` field matches the target project
- Searching "triple y residence" returns both "Triple Y Residence Samyan" AND unrelated "Dusit Central Park" — verify the match

**Authentication:** CF cookies required (403 without them)

---

### 3. MRT Stations List (no auth required)

```
GET /api/consumer/search-with-filter/mrt-items?region=th&locale=en
```

Returns all BTS/MRT/ARL stations with coordinates. Works **without CF cookies**.

---

### 4. Other Confirmed API Endpoints (require CF cookies)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/consumer/search-with-filter/location-items` | GET | Location dropdown items |
| `/api/consumer/location/mrt-distances` | GET | Distance to MRT stations |
| `/api/consumer/location/nearby-pois` | GET | Nearby amenities |
| `/api/consumer/location/places-autocomplete` | GET | Address autocomplete |
| `/api/consumer/listings/other` | GET | Other listings by same agent |
| `/api/consumer/project-price-insights` | GET | Price insights (requires more params) |
| `/api/consumer/property-transactions/transactions` | GET | Registered transactions (complex params) |
| `/api/consumer/autocomplete` | POST | Search autocomplete (**broken server-side**) |
| `/api/consumer/condo-directory/search` | GET | Condo project directory (**500 error**) |
| `/api/consumer/search/generate-url` | POST | Generate search URL (**broken**) |

---

## Pagination

The `/_next/data` API paginates via `&page=N`.

```
resultCount: 142 listings
totalPages: ceil(142 / 20) = 8
Default page size: 20 listings/page
```

Example: 15 Sukhumvit Residences has 142 sale / 123 rent listings across 8 pages.

**Rate limiting:** Not observed during testing. Use 0.5s delay between pages to be polite.

---

## Project Page Structure

Project pages (`/en/project/{id}-{slug}`) are served by a legacy "guruland-proxy" system:
- Not Next.js SSR — no `__NEXT_DATA__` in the HTML
- Project listings are loaded via AJAX: `/en/sf2-search/ajax/properties/{projectId}/listings/{SALE|RENT}`
- This endpoint returns **HTML** (not JSON), rendered listing cards
- The JSON listing data is embedded as `data-ec-impression` attributes in the HTML

**sf2 endpoint format:**
```
GET /en/sf2-search/ajax/properties/{project_id}/listings/SALE?limit=24
GET /en/sf2-search/ajax/properties/{project_id}/listings/RENT?limit=24
```

This endpoint is **less reliable** — getting 500 errors intermittently. Prefer the `/_next/data` SRP approach.

---

## Authentication Requirements

| Endpoint | Auth |
|----------|------|
| `/_next/data/...` SRP | CF cookies required |
| `/api/consumer/project` | CF cookies required |
| `/api/consumer/search-with-filter/mrt-items` | **None** |
| `/en/sf2-search/ajax/properties/...` | CF cookies required |
| All `/api/consumer/listings/*` | CF cookies required |

No API keys, no OAuth tokens, no `Authorization` header required. Cloudflare cookies are the only auth mechanism.

---

## Recommended Scraping Approach

### Architecture

```
1. Cookie pool (Camoufox, ~8s each)
   └─ Refresh when 403 received

2. httpx client with CF cookies
   ├─ Project lookup: /api/consumer/project?name=...
   └─ Listing fetch: /_next/data/{BUILD_ID}/en/condo-for-{sale|rent}.json
```

### Step-by-Step for NPA Screening

```python
# 1. Get CF cookies (once per session, ~8s)
cookies = await get_cf_cookies()  # via Camoufox

# 2. Look up project ID + metadata
project = await lookup_project("triple y residence samyan", client)
# → id=7006, units=516, built=2019, type=CONDO

# 3. Fetch all sale listings
sale_listings = await fetch_listings(
    freetext="triple y residence samyan",
    listing_type="sale",
    ...
)
# → 19 listings, price/sqm: 137k-179k THB/sqm, median 156k

# 4. Fetch all rent listings
rent_listings = await fetch_listings(
    freetext="triple y residence samyan",
    listing_type="rent",
    ...
)
# → 10 listings, 27k-60k THB/mo
```

### BUILD_ID Refresh

The BUILD_ID is embedded in every Next.js response and changes on frontend deploys.
Refresh strategy: on 404 error from `/_next/data`, re-fetch the homepage to extract new build ID.

---

## Sample Validated Results

All results validated 2026-04-04:

| Project | Sale Listings | Median Price/sqm | Rent Listings | Median Rent |
|---------|--------------|-----------------|--------------|-------------|
| Triple Y Residence Samyan | 19 | ฿156,061/sqm | 10 | ฿30,000/mo |
| The Inspire Place Abac Rama 9 | 8 | ฿41,523/sqm | 3 | ฿13,000/mo |
| 15 Sukhumvit Residences | 142 | ฿128,201/sqm | 123 | ฿65,000/mo |

---

## Working curl Commands

These work **only with valid CF cookies**. Get them from Camoufox first.

```bash
# Project lookup
curl -s "https://www.ddproperty.com/api/consumer/project?name=triple+y+residence&locale=en&region=th&size=3" \
  -H "Cookie: cf_clearance=XXX; __cf_bm=YYY" \
  -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36" \
  | jq '.data[] | {name, property_id, completion_year, total_units}'

# Sale listings
BUILD_ID="eSYGxg6TJlYl4EPdcSFiR"
curl -s "https://www.ddproperty.com/_next/data/${BUILD_ID}/en/condo-for-sale.json?freetext=triple+y+residence+samyan&listingType=sale" \
  -H "Cookie: cf_clearance=XXX; __cf_bm=YYY" \
  -H "User-Agent: Mozilla/5.0 ..." \
  | jq '.pageProps.pageData | {resultCount, listings: [.data.listingsData[].listingData | {id, price: .price.value, sqm: .floorArea, psm: .psfText}]}'

# MRT stations (no auth needed)
curl -s "https://www.ddproperty.com/api/consumer/search-with-filter/mrt-items?region=th&locale=en" \
  | jq '[.[] | {line: .name, stations: [.stations[] | {name, lat: .location.latitude, lng: .location.longitude}]}]'
```

---

## Endpoints That Don't Work (as of 2026-04-04)

| Endpoint | Error | Notes |
|----------|-------|-------|
| `POST /api/consumer/autocomplete` | 500 "Cannot destructure property 'region'" | Server bug — body parser broken |
| `GET /api/consumer/condo-directory/search` | 500 "There was a problem fetching projects" | Backend error |
| `POST /api/consumer/search/generate-url` | 500 "Cannot read properties of undefined (reading 'forEach')" | Server bug |
| `GET /api/consumer/property-transactions/transactions` | 400 "required params not provided" | Needs: transactionType, propertyTypeGroup, bedrooms, postcode |
| `GET /api/consumer/project-price-insights` | 400 | Missing required params |

---

## Files

| File | Content |
|------|---------|
| `recon/network_capture.json` | First network capture pass |
| `recon/srp_next_data.json` | Full `__NEXT_DATA__` from SRP page |
| `recon/project_lookup_sample.json` | Full project object from `/api/consumer/project` |
| `recon/listings_html.html` | Raw HTML from sf2 listings endpoint |
| `recon/js_sources/` | 96 JS bundles (all API endpoint strings extracted) |
| `scripts/ddproperty_checker.py` | **Working prototype scraper** |

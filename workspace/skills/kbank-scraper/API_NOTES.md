# KBank NPA Scraper — API & Architecture Notes

## Inventory

- **13,361** total properties (as of 2026-04-04)
- **6,314** with active promotions (PromotionProperties)

## Two-Phase Data Pipeline

### Phase 1: List API (httpx — no browser needed)

**Endpoint**: `POST /Custom/KWEB2020/NPA2023Backend13.aspx/GetProperties`

```json
{
  "filter": {
    "CurrentPageIndex": 1,
    "PageSize": 50,
    "SearchPurposes": ["AllProperties"],
    "Provinces": [10],
    "PropertyTypes": ["05"],
    "MinPrice": 1000000,
    "MaxPrice": 5000000
  }
}
```

**Key findings from reverse-engineering:**
- Pagination param is `CurrentPageIndex` (1-based) — discovered by analyzing `search-npa-script.js` via Playwright interception
- `PageSize` caps at 50 → 268 pages for full scrape
- Response is ASP.NET wrapped: `{"d": "<json-string>"}` — needs double JSON parse
- No Akamai protection on this endpoint — plain httpx works
- Filters (`Provinces`, `PropertyTypes`, `MinPrice`/`MaxPrice`) all verified working

**Fields available (40 keys per item):**

| Category | Fields |
|----------|--------|
| Identity | `PropertyID`, `PropertyIDFormat`, `SourceCode`, `SourceSaleType` |
| Price | `SellPrice` (baht), `PromotionPrice`, `AdjustPrice`, `PromotionName` |
| Location | `ProvinceName`, `AmphurName`, `TambonName`, `VillageTH`, `Latitude`, `Longtitude` |
| Property | `PropertyTypeName`, `Bedroom`, `Bathroom`, `BuildingAge`, `UseableArea` |
| Land | `Rai`, `Ngan`, `SquareArea`, `AreaValue` |
| Status | `IsNew`, `IsHot`, `IsReserve`, `IsSoldOut`, `PMMaintenanceStatus` |
| Media | `PropertyMediaes[]` (thumbnail, mobile, PC, map) |

### Phase 2: Detail Enrichment (Camoufox — headless browser)

**URL pattern**: `GET /th/propertyforsale/detail/{PropertyID}.html`

**Why Camoufox?** KBank uses Akamai Bot Manager on detail pages. We tested every alternative:

| Approach | Result |
|----------|--------|
| httpx (plain) | 403 — Akamai blocks |
| curl_cffi (TLS impersonation) | Got PoW challenge page, can't execute JS |
| curl_cffi + PoW solver | PoW solved (200), but retry still 403 — fingerprint check fails |
| Playwright headless | 403 |
| Playwright headed + stealth | PASS — but heavy (150MB Chromium download) |
| nodriver headless | 403 |
| nodriver headed | PASS — but must show window |
| **Camoufox headless=True** | **PASS — no window, bypasses Akamai** |
| Camoufox headed | PASS |

**Why Camoufox works headless:** It patches Firefox at the C++ level — WebGL, AudioContext, canvas, screen geometry are all spoofed before Akamai's sensor.js executes. Other tools only patch at the JS level, which Akamai detects.

**Extra fields from detail page:**
- Title deed number (โฉนดเลขที่) → `.property-info .property-row .property-td`
- Full address → `.location-container p`
- Nearby places with distances → `.place-nearby table tr`
- JSON-LD structured data (Product + Accommodation schema)

## Rate Limiting

- **List API**: No observed rate limit. Start conservative at 20 req/60s.
- **Detail pages**: Unknown. Camoufox is slow (~8s/page), so natural rate limiting.

## Headers Required

### List API
```
Content-Type: application/json
X-Requested-With: XMLHttpRequest
Referer: https://www.kasikornbank.com/th/propertyforsale/search/pages/index.aspx
Origin: https://www.kasikornbank.com
User-Agent: Mozilla/5.0 ...
```

### Detail Page (Camoufox handles automatically)
No manual headers needed — Camoufox manages browser fingerprint.

## Other Endpoints (from JS source)

| Endpoint | Purpose |
|----------|---------|
| `NPA2023Backend13.aspx/GetProperties` | Property search (primary) |
| `NPA2023Backend13.aspx/RequestStations` | BTS/MRT station list |
| `GarageBackendNPA108.aspx/*` | Alternative backend (403 without session) |
| `GarageBackendHL28.aspx/*` | Home loan backend |
| `pfsapp.kasikornbank.com/pfs-frontend-api/property-images/` | Image CDN only |

## Recon Files

| File | Purpose |
|------|---------|
| `recon/test_e2e.py` | End-to-end validation (list + detail) |
| `recon/test_nodriver.py` | nodriver headed test (works) |
| `recon/test_camoufox.py` | Camoufox headless test (works) |
| `recon/test_akamai_bypass.py` | PoW solver attempt (fails at fingerprint) |
| `recon/find_params.py` | JS reverse-engineering for filter params |
| `recon/js_sources/search-npa-script.js` | Main frontend JS with filter construction |

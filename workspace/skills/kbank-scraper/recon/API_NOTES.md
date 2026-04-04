# KBank NPA API — Reverse-Engineered Parameters

## Endpoint
```
POST https://www.kasikornbank.com/Custom/KWEB2020/NPA2023Backend13.aspx/GetProperties
Content-Type: application/json
```

## Request Body Structure
```json
{
  "filter": {
    "CurrentPageIndex": 1,
    "AllCurrentPageIndex": 1,
    "PageSize": 20,
    "SearchPurposes": ["AllProperties"],
    "Search": "keyword text",
    "Provinces": [10],
    "Amphurs": [1001],
    "PropertyTypes": ["01"],
    "MinPrice": 0,
    "MaxPrice": 5000000,
    "MinArea": 0,
    "MaxArea": 100,
    "Bedroom": 2,
    "Bathroom": 1,
    "Nearby": "สถานีรถไฟฟ้า...",
    "NearbyMeters": 1000,
    "SourceSaletypes": ["..."],
    "PropertyIds": ["id1", "id2"]
  }
}
```

## Parameter Details

### Pagination
| Parameter | Type | Notes |
|-----------|------|-------|
| `CurrentPageIndex` | int | **THIS IS THE PAGINATION PARAM** — starts at 1 |
| `AllCurrentPageIndex` | int | Used in default payload, always 1 |
| `PageSize` | int | Items per page, default 20, max 50 |

### Filters
| Parameter | Type | Example | Notes |
|-----------|------|---------|-------|
| `SearchPurposes` | string[] | `["AllProperties"]` | Tab selector. Values: `AllProperties`, `PromotionProperties`, `HaveAi` |
| `Search` | string | `"บางนา"` | Free-text keyword search |
| `Provinces` | int[] | `[10]` | Province IDs (integer, from dropdown) |
| `Amphurs` | int[] | `[1001]` | District/Amphur IDs (integer, child of province) |
| `PropertyTypes` | string[] | `["01"]` | Property type codes (string, from dropdown) |
| `MinPrice` | int | `0` | Min price in baht |
| `MaxPrice` | int | `5000000` | Max price in baht (empty string = no max) |
| `MinArea` | int | `0` | Min area |
| `MaxArea` | int | `100` | Max area |
| `Bedroom` | int | `2` | Number of bedrooms |
| `Bathroom` | int | `1` | Number of bathrooms |
| `Nearby` | string | station location | BTS/MRT station location string |
| `NearbyMeters` | int | `1000` | Radius in meters from station |
| `SourceSaletypes` | string[] | | Source/sale type filter |
| `PropertyIds` | string[] | | Fetch specific properties by ID |

### Sort / Ordering
- `Ordering` parameter exists but is **commented out** in current code
- Known values: `"Hot"`, `"New"`
- May still work if sent

## Response Structure
```json
{
  "d": "{\"Success\": true, \"Data\": {\"TotalRows\": 13361, \"Items\": [...]}}"
}
```
- Response `d` is a **JSON string** that needs double-parsing
- `Data.TotalRows` = total matching properties
- `Data.Items` = array of property objects

## Other Endpoints
| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/GetProperties` | POST | Main property search |
| `/RequestStations` | GET | BTS/MRT station list |

## Base URLs
```
backendPFSURL: /Custom/KWEB2020/NPA2023Backend13.aspx
backendNPAURL: /Custom/KWEB2020/GarageBackendNPA108.aspx
backendHLURL:  /Custom/KWEB2020/GarageBackendHL28.aspx
```

## Source Files
- `search-npa-script.js` (152KB) — Main search page logic, filter construction
- `HomeHeader.bundle.js` — Shared API wrapper function `D()`
- `constants.js` — Backend URL configs
- `property-noti.js` — Property notification/alert subscriptions

## Key Insight
The reason `PageNo`, `PageIndex`, `PageNumber` were ignored: the correct parameter is **`CurrentPageIndex`** (PascalCase, inside the `filter` object). The frontend constructs `objPayload.filter.CurrentPageIndex = page` before each API call.

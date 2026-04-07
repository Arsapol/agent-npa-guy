# GHB HomCenter API Recon Notes

**Site**: https://www.ghbhomecenter.com/
**Provider**: ธนาคารอาคารสงเคราะห์ (Government Housing Bank)
**Total properties**: ~26,648 (as of 2026-04-07)
**Architecture**: Server-rendered HTML (Laravel/PHP) + REST API for mobile features

## Scraping Strategy

GHB uses a **hybrid approach**:
1. **Search/listing**: Server-rendered HTML pages (no search API for anonymous users)
2. **Detail**: Server-rendered HTML pages (all fields in HTML + JS variables)
3. **Supporting data**: REST API at `/v3/property/api` (locations, saved properties)

The REST API `/search` endpoint exists but returns `Access Denied` for anonymous JWT tokens.
The recommended approach is **HTML scraping** for search + detail, supplemented by the API for location hierarchies.

## Authentication

Anonymous JWT is embedded in every page's inline JavaScript:
```javascript
var accessToken = "eyJ0eXAiOiJKV1Q...";
```

- Algorithm: RS256
- TTL: ~7 days (field `exp` in JWT payload)
- Scopes: `["read", "write"]`
- Issuer: `https://www.ghbhomecenter.com/npa/`
- Required headers for API calls:
  ```
  Authorization: Bearer {jwt}
  token: {jwt}
  source: mobile
  ```

Token must be refreshed by re-fetching any HTML page when expired.

## Endpoints

### 1. HTML Search (Primary — Server-Rendered)

```
GET /property-foryou-for-sale?{params}
GET /property-for-sale?{params}
```

Returns server-rendered HTML with 10 properties per page.

| Param | Description | Example |
|-------|-------------|---------|
| `p` | Province ID (from location API) | `3001` (Bangkok) |
| `d` | District/Amphur ID | `5033` (คลองเตย) |
| `sd` | Sub-district/Tumbon ID | - |
| `pt[]` | Property type ID (repeatable) | `3` (condo) |
| `kw` | Keyword search | `สุขุมวิท` |
| `minp` | Min price (baht) | `1000000` |
| `maxp` | Max price (baht) | `5000000` |
| `mina` | Min area (sqw/sqm) | `50` |
| `maxa` | Max area (sqw/sqm) | `200` |
| `pId` | Promotion ID | `65` (ทรัพย์ตรงใจ) |
| `st` | Sort order | `PriceAsc`, `PriceDesc`, `AreaAsc`, `AreaDesc` |
| `pg` | Page number (1-based) | `1` |
| `lid` | Location ID (from autocomplete) | - |

**URL variants** (different view types):
- `/property-foryou-for-sale` — "For You" recommendations (default sort)
- `/property-for-sale` — Standard listing
- `/property-foryou-grid-for-sale` — Grid view
- `/property-search-maps` — Map view (empty markers, loads lazily)

**Pagination**: 10 items/page, handled by `pg` param. Total pages = `ceil(total / 10)`.

### 2. HTML Detail Page

```
GET /property-{propertyId}
```

Returns full property detail as server-rendered HTML.

**Alternative URL** (by property number):
```
GET /npa-{propertyNo}
```

### 3. REST API — Location Hierarchy

```
GET /v3/property/api/location/province
GET /v3/property/api/location/amphur/{provinceId}
GET /v3/property/api/location/tumbon/{amphurId}
```

Returns JSON. Requires JWT auth headers.

Response format:
```json
{
  "code": 200,
  "message": "Success",
  "data": [
    {
      "provinceId": 3001,
      "code": "10",
      "nameTh": "กรุงเทพมหานคร",
      "nameEn": "Bangkok",
      "url": "/Bangkok",
      "displayFlag": "Y"
    }
  ]
}
```

### 4. REST API — Keyword Autocomplete

```
GET /ProxyAPI/search/keyword/{query}
```

No auth required. Returns JSON array of location suggestions:
```json
[
  {
    "locationName": "...",
    "locationDisplayName": "...",
    "locationType": 1,
    "locationId": 123
  }
]
```

### 5. REST API — Media (Images)

```
GET /v3/property/api/Media/{mediaId}
GET /v3/property/api/Media/{mediaId}-{width}-{height}
```

No auth required. Returns image binary.
- Full size: no suffix
- Thumbnail: append `-{w}-{h}` (e.g., `-348-257`, `-380-280`, `-280-120`, `-50-50`)

### 6. REST API — Saved Properties (authenticated)

```
GET /v3/property/api/saveproperty?trackingId={trackingId}
```

Returns rich JSON with full property data. Paginated (10/page).
This endpoint works with anonymous JWT but returns data associated with the tracking session.

## Property Type IDs

| ID | Thai Name | English |
|----|-----------|---------|
| 1 | บ้านเดี่ยว | Detached house |
| 2 | บ้านแฝด | Semi-detached house |
| 3 | คอนโด | Condominium |
| 4 | ทาวน์เฮ้าส์ | Townhouse |
| 5 | อาคารพาณิชย์ | Commercial building |
| 6 | ที่ดิน | Land |
| 7 | แฟลต | Flat |
| 8 | อื่นๆ | Other |

## Promotion IDs

| ID | Name |
|----|------|
| 477 | งานประมูลบ้านมือสอง ธอส. ออนไลน์ ครั้งที่ 3 ประจำปี 2569 |
| 65 | โครงการทรัพย์ตรงใจ |
| 259 | Marketplace ตลาดนัดบ้านมือสองออนไลน์ |
| 257 | โครงการทรัพย์ฝากขาย (Virtual NPL Management) |

## Field Mapping Table

### From HTML Search Page (listing card)

| Field | CSS/Regex | Sample Value |
|-------|-----------|--------------|
| Property ID | `a[href*='/property-']` → regex `/property-(\d+)` | `987980` |
| Price | Card text contains `บาท` or `฿` | `68,000 บาท` |
| Title | Card text, first line | `ขายคอนโด (ปลาทอง94)` |
| Location | Card text, second line | `บางพูน, เมืองปทุมธานี, ปทุมธานี` |
| Area | Card text with `ตร.ม.` or `ตร.ว.` | `26.25 ตร.ม.` |
| Property code | `รหัสทรัพย์:` text | `1301201301` |
| Order number | `ลำดับทรัพย์ที่:` text | `510` |
| Image | `img[src*='/v3/property/api/Media/']` | URL with size suffix |
| Promotion label | Card overlay text | `ทรัพย์โปรโมชั่นราคาพิเศษ` |

### From HTML Detail Page

| Field | Source | Sample Value |
|-------|--------|--------------|
| Title | `h1` text | `ขายคอนโด (ปลาทอง94)` |
| Price | `h3.text-price` text | `฿ 68,000` |
| Property code | `.row` label `รหัสทรัพย์` | `1301201301` |
| Property type | `.row` label `ประเภททรัพย์` | `คอนโด` |
| Project/village | `.row` label `โครงการ` | `ปลาทอง94` |
| Area (sqm/sqw) | `.row` first col with `ตร.ม.` or `ตร.ว.` | `26.25 ตร.ม.` |
| Floor info | `.row` adjacent to area | `ชั้นที่ 4 จาก 4 ชั้น` |
| Title deed no. | `.row` label `เลขที่โฉนด/นส 3ก.` | `28146` |
| House number | `.row` label `เลขที่` | `322/50` |
| Soi | `.row` label `ซอย` | `รังสิตซิตี้` |
| Road | `.row` label `ถนน` | `รังสิต-ปทุมธานี` |
| Sub-district | `.row` label `แขวง/ตำบล` | `บางพูน` |
| District | `.row` label `เขต/อำเภอ` | `เมืองปทุมธานี` |
| Province | `.row` label `จังหวัด` | `ปทุมธานี` |
| GPS lat | JS `var geoLat = {value}` or `daddr={lat},{lon}` | `13.9886` |
| GPS lon | JS `var geoLong = {value}` or `daddr={lat},{lon}` | `100.578` |
| Images | regex `/v3/property/api/Media/(\d+)(?!-)` | Array of media IDs |
| Map image | `img[title*='แผนที่']` src | Media URL |
| Description | `meta[name='description']` content | Full text description |

### From REST API — saveproperty (richest JSON source)

| API Field | Type | Sample | Notes |
|-----------|------|--------|-------|
| `propertyId` | int | `1178283` | Internal DB ID |
| `propertyNo` | str | `3401103791` | Public property code |
| `propertyType` | str | `บ้านเดี่ยว` | Thai name |
| `typeId` | int | `1` | Property type ID |
| `propertyName` | str | `บ้านเดี่ยว null` | May contain "null" string |
| `villageName` | str | `null` | Project/village name (may be null string) |
| `priceAmt` | int | `525000` | Sale price in baht |
| `promotionPriceAmt` | int | `525000` | Promotion price in baht |
| `beginAuctionPrice` | int | `525000` | Starting auction price |
| `salePrice` | int | `0` | 0 if not separately set |
| `area` | str | `27.4` | Area (sqw for houses, sqm for condos) |
| `areaTxt` | str | `27.4 ตร.ว.` | Formatted area with unit |
| `usageArea` | str | `0` | Usable area (sqm) |
| `usageAreaTxt` | str | `-` | Formatted usable area |
| `rai` | str | `0` | Land area: rai |
| `ngan` | str | `0` | Land area: ngan |
| `wa` | str | `0` | Land area: wah |
| `floors` | int | `1` | Number of floors |
| `floor` | int | `0` | Floor number (for condos) |
| `bedrooms` | int | `0` | Number of bedrooms |
| `bathrooms` | int | `0` | Number of bathrooms |
| `parkingLot` | int | `0` | Parking spaces |
| `geoLat` | float | `15.2625` | GPS latitude |
| `geoLong` | float | `104.848` | GPS longitude |
| `deedNo` | str | `24106` | Title deed number |
| `houseNo` | str | `19` | House/unit number |
| `moo` | null/str | `null` | Moo (village group) |
| `soi` | str | `สุขาสงเคราะห์ 1` | Soi name |
| `road` | str | `สุขาสงเคราะห์` | Road name |
| `tumbon` | str | `ในเมือง` | Sub-district name |
| `tumbonId` | int | `0` | Sub-district ID |
| `amphur` | str | `เมืองอุบลราชธานี` | District name |
| `amphurId` | int | `5295` | District ID |
| `province` | str | `อุบลราชธานี` | Province name |
| `provinceId` | int | `3023` | Province ID |
| `imageUrl` | str | `https://...Media/{id}` | Primary image URL |
| `contactPerson` | str | `ฝ่ายบริหารหนี้...` | Contact person/dept |
| `contactTelNo` | str | `0-2645-9000 : ...` | Contact phone |
| `callTelno` | str | `026459000` | Call center number |
| `branchCode` | str | `081` | Branch code |
| `branchId` | int | `125` | Branch ID |
| `promotionFlag` | int | `1` | Has promotion |
| `promotionId` | int | `65` | Promotion ID |
| `promotionName` | str | `โครงการทรัพย์ตรงใจ` | Promotion name |
| `eventType` | str | `99` | Event type code |
| `bidOnlineFlag` | str | `N` | Online auction flag |
| `bidDate` | str | `` | Auction date |
| `bookingFlag` | str | `N` | Can book online |
| `bookingUrl` | str | `https://...booking/{id}` | Booking URL |
| `contactUrl` | str | `https://...contact/{id}` | Contact URL |
| `shareUrl` | str | `https://...npa-{no}` | Share URL |
| `propertyActiveFlag` | int | `1` | Active listing |
| `propertyStatus` | str | `03` | Status code |
| `status` | int | `1` | General status |
| `createdDate` | str | `2021-11-10 14:38:12` | Created timestamp |
| `modifiedDate` | str | `2026-03-23 09:35:03` | Modified timestamp |
| `viewCount` | int | `0` | View count |
| `orderNo` | int | `0` | Display order |

## Rate Limits

- No observed rate limiting during testing
- Recommended: 1-2 req/sec for HTML pages, 5 req/sec for API
- Use `asyncio.Semaphore(10)` for bounded concurrency (project standard)

## Scraper Design Recommendations

1. **Listing crawl**: Iterate `/property-foryou-for-sale?pg=1..N` with filters per province
   - 10 items per page, ~2,665 pages for all 26,648 properties
   - Extract property IDs from card links
2. **Detail crawl**: Fetch `/property-{id}` for each property ID
   - Parse HTML for all fields (key-value pairs, GPS, images, meta)
3. **JWT refresh**: Re-extract token from any HTML page before it expires (~7 days)
4. **Location data**: Pre-fetch all provinces, districts, sub-districts from API
5. **Price**: Stored in **whole baht** (integer)
6. **Dedup key**: `propertyNo` (public property code, e.g., `1301201301`)
7. **Change detection**: Track `modifiedDate` from saveproperty API or re-scrape periodically

## Files in This Recon

| File | Description |
|------|-------------|
| `test_api.py` | Working test script demonstrating all endpoints |
| `API_NOTES.md` | This document |
| `provinces.json` | All 77 Thai provinces with IDs |
| `amphurs_bangkok.json` | All 50 Bangkok districts |
| `sample_saveproperty.json` | Sample saveproperty response (10 items, rich JSON) |
| `sample_search_cards.json` | Parsed search listing cards |
| `sample_detail.json` | Parsed detail page data |

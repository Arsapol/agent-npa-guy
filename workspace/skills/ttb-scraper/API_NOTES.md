# TTB/PAMCO NPA Property API — Recon Notes

**Site**: https://property.pamco.co.th/
**API Base**: `https://property-api-prod.automer.io/`
**Media CDN**: `https://media.pamco.co.th/`
**S3 Bucket**: `npa-property-bucket.s3.ap-southeast-1.amazonaws.com`
**Date**: 2026-04-07

## Architecture

- **Frontend**: Next.js SSR app (buildId changes on deploy)
- **Backend**: REST API at `property-api-prod.automer.io` (nginx/1.21.6)
- **CDN**: CloudFront (BKK50-P3 POP)
- **Images**: S3 with pre-signed URLs + media.pamco.co.th CDN

## Anti-Bot Measures

**Minimal.** No WAF, no Akamai, no CryptoJS encryption.

- CloudFront returns HTTP 500 if `User-Agent` header is missing/empty
- With any browser-like `User-Agent`, returns 200
- No rate limiting observed during testing
- No cookies/tokens required
- API is fully open (CORS allows `property.pamco.co.th` origin)
- **Camoufox NOT needed** — plain httpx works perfectly

Required headers:
```
User-Agent: Mozilla/5.0 (Macintosh; ...) Chrome/131.0.0.0 Safari/537.36
Accept: application/json, text/plain, */*
Origin: https://property.pamco.co.th
Referer: https://property.pamco.co.th/
```

## Endpoints

### 1. Property Listing (primary scraper endpoint)

```
GET {API}/property-new/display?page={n}&limit={n}[&province={id}][&district={id}][&subdistrict={id}][&type={cat}]
```

| Param | Type | Description |
|-------|------|-------------|
| `page` | int | Page number (1-indexed) |
| `limit` | int | Items per page (tested up to 200) |
| `province` | int | Province code (e.g. 10 = Bangkok) |
| `district` | string | District code (e.g. "1001") |
| `subdistrict` | string | Sub-district code (e.g. "100101") |
| `type` | int | Property category (see table below) |

**Response**: `{"total": 1356, "list": [...]}`

**Pagination**: `ceil(total / limit)` pages. Page beyond last returns `{"total": N, "list": []}`.

### 2. Property Detail (via Next.js SSR)

```
GET {SITE}/_next/data/{buildId}/assets/{route}/{slug}.json
```

| Route | Condition |
|-------|-----------|
| `pamco` | property.type == 3 |
| `ttb` | property.type == 4 |
| `auctions` | auction properties |
| `consignments` | consignment properties |

**Note**: `buildId` changes on every deployment. Extract from homepage `__NEXT_DATA__`.

**Response**: `{"pageProps": {"propertys": {...}, "nearbyAsset": [...], ...}}`

Detail has 5 extra fields vs listing: `TeamAo`, `province`, `district`, `subDistrict`, `pathQRcode`.
Listing has 5 fields not in detail: `Region`, `provinceNameTh`, `districtNameTh`, `subDistrictNameTh`, `detail`.

### 3. Province Dropdown

```
POST {API}/dropdown/province
Content-Type: application/json

{"province": 10, "district": null}
```

Returns districts for a province. With `district` set, returns sub-districts.

### 4. Province List (from homepage SSR)

Available in `__NEXT_DATA__.props.pageProps.drop` — 77 provinces with region mapping.

### 5. Property Type Dropdown (from homepage SSR)

Available in `__NEXT_DATA__.props.pageProps.dropdownDetail` — 27 property sub-types.

## Property Categories (`type` query parameter)

| type | Thai | English | Count (2026-04-07) |
|------|------|---------|----|
| 1 | บ้านเดี่ยว | Detached House | 319 |
| 2 | ทาวน์เฮ้าส์ | Townhouse | 362 |
| 3 | อาคารพาณิชย์ | Commercial Building | 166 |
| 4 | คอนโด | Condo | 225 |
| 5 | ที่ดินเปล่า | Vacant Land | 38 |
| 6 | โรงงาน | Factory/Industrial | 19 |
| 7 | สำนักงาน | Office | 122 |
| **Total** | | | **1,356** |

Note: `type` in query = category filter. The property object's `.type` field = source (3=PAMCO, 4=TTB).

## Property Source Types (`.type` field in property object)

| .type | Source | Slug Prefix | Detail Route | Count |
|-------|--------|-------------|-------------|-------|
| 3 | PAMCO | `p0xxxx` | `/assets/pamco/{slug}` | ~500 |
| 4 | TTB Bank | `b1xxxx` | `/assets/ttb/{slug}` | ~856 |

## Field Mapping

### Core Fields (from listing endpoint — no detail call needed)

| API Field | Description | Example |
|-----------|-------------|---------|
| `idProperty` | Internal PK | 3439 |
| `slug` | URL slug / unique ID | "p00979" |
| `idMarket` | Marketing ID | "P00979" |
| `type` | Source: 3=PAMCO, 4=TTB | 3 |
| `npaProductTitle` | Property title | "ทาวน์เฮ้าส์ ว.แลนด์เฮ้าส์..." |
| `npaProductLatitude` | GPS latitude (string) | "7.102857" |
| `npaProductLongitude` | GPS longitude (string) | "100.554044" |
| `npaProductArea` | Land area in sq.wah (string) | "30.20" |
| `area` | Land area rai-ngan-wah format | "0000-0-30.2" |
| `useableArea` | Usable area in sqm (string) | "100.50" |
| `searchArea` | Searchable area (same as npaProductArea) | "30.20" |
| `landid` | Title deed number(s) | "ฉ.306006" |
| `houseid` | House number | "132/57" |
| `hgroup` | Project/village name | "ว.แลนด์เฮ้าส์ พรีโม่ คาซ่า 2" |
| `idDetail` | Property sub-type ID (maps to dropdownDetail) | 2 |
| `npaProductProvinceId` | Province code | 90 |
| `npaProductAmphurId` | District code (string) | "9011" |
| `npaProductDistrictId` | Sub-district code (string) | "901114" |
| `street` | Street name | "บ้านควนหิน-บ่อโพธิ์" |
| `soi` | Soi (lane) | "เพชรจันทร์" |
| `moo` | Moo (village number) | "" |
| `floor` | Number of floors | "1" |
| `bedRoom` | Bedrooms | "" |
| `bathRoom` | Bathrooms | "" |
| `livingRoom` | Living rooms | "" |
| `kitchen` | Kitchens | "" |
| `parking` | Parking spaces | "" |
| `telAO` | Account officer phone | "08 0042 5143" |
| `isApprove` | Published flag | true |
| `startDate` | Listing start | "2024-10-30" |
| `endDate` | Listing end | "2044-12-31" |
| `created_datetime` | Created | "2025-11-10T07:00:00+07:00" |
| `updated_datetime` | Updated | "2026-04-04T04:00:02+07:00" |
| `tag` | Special tag (null or "recommend") | null |
| `NpaApprisal` | Appraisal data (usually null) | null |
| `NpaConProp` | Consignment/condition data (usually null) | null |
| `investment` | Investment note | "" |
| `noteAsset` | Asset note | null |
| `comment` | Comment | null |
| `redCase` | Red case number | null |
| `payDown` | Down payment info | null |
| `video` | Video URL | "" |

### Price Fields

| Field | Description | Example |
|-------|-------------|---------|
| `lowprice[0].lowprice` | Asking price in **whole baht** (string) | "2400000" |
| `lowprice[0].active` | Price is active | true |
| `lowprice[0].noPrice` | Price hidden (contact for price) | false |
| `lowprice[0].noPriceNote` | Hidden price note | "ลดราคาพิเศษ สนใจติดต่อ..." |
| `idEvent[0].priceSp1` | Promotional price in **whole baht** (string) | "2023000" |
| `idEvent[0].startDate` | Promotion start | "2026-03-02" |
| `idEvent[0].endDate` | Promotion end | "2026-05-31" |
| `idEvent[0].noteSale` | Promotion note | null |

### Image Fields

| Field | Description | URL Pattern |
|-------|-------------|-------------|
| `thumbnail[]` | Thumbnail images | `{S3PATH}{path}` |
| `illustration[]` | Detail photos | `{S3PATH}{path}` |
| `map[]` | Location map images | `{S3PATH}{path}` |
| `titleThumbnail[]` | Original thumbnail filenames | "B13553.jpg" |
| `titleIllustration[]` | Original illustration filenames | "B13553-01.jpg" |
| `posterVideo` | Video poster | "" |
| `fileMap` | Pre-signed S3 URL for map | Full S3 URL with signature |

Image URL construction: `https://media.pamco.co.th/{thumbnail[0]}`

### Location Fields

| Field | Description | Example |
|-------|-------------|---------|
| `nearBy[]` | Nearby landmarks | `[{"nearby": "แม็คโคร สงขลา", "distance": "6.60"}]` |
| `googleMap` | Embedded Google Maps iframe HTML | `<iframe src="...">` |
| `provinceNameTh` | Province name (listing only) | "สงขลา" |
| `districtNameTh` | District name (listing only) | "หาดใหญ่" |
| `subDistrictNameTh` | Sub-district name (listing only) | "น้ำน้อย" |
| `Region` | Region name (listing only) | "ภาคใต้" |

### Status Fields

| Field | Description | Values |
|-------|-------------|--------|
| `statusDetail[0].noh` | Status code | "00" = available |
| `checker` | Active/valid flag | true |

### Detail-Only Fields (from SSR endpoint)

| Field | Description |
|-------|-------------|
| `TeamAo.name` | Account officer name |
| `province` | Province name (Thai) |
| `district` | District name (Thai) |
| `subDistrict` | Sub-district name (Thai) |
| `pathQRcode` | QR code callback URL |

## GPS Extraction from Google Maps Iframe

When `npaProductLatitude`/`npaProductLongitude` are empty, GPS can be extracted from `googleMap` iframe:

```python
import re

iframe = property["googleMap"]
# Pattern: !3d{lat}!2d{lng} or !3d{lat}...!2d{lng}
m = re.search(r'!3d([\d.]+).*?!2d([\d.]+)', iframe)  # Note: reversed in embed URL
# Actually the URL uses: !2d{lng}!3d{lat} format
m = re.search(r'!2d([\d.]+)[^!]*!3d([\d.]+)', iframe)
if m:
    lng, lat = m.group(1), m.group(2)
```

## Scraper Strategy

1. **Use listing endpoint only** — it returns all fields needed for screening
2. **Paginate with limit=200** — 7 pages to get all 1,356 properties
3. **No detail calls needed** for basic screening (GPS, price, area, location all in listing)
4. **Detail calls** only needed for: `TeamAo` (officer name), `pathQRcode`
5. **Province dropdown** from homepage SSR — cache once
6. **Property type dropdown** from homepage SSR — cache once
7. **Price stored in whole baht** (string) — parse to int
8. **Area in sq.wah** (string) — parse to float
9. **Useable area in sqm** (string) — parse to float
10. **BuildId** must be refreshed when detail calls return 404

## Rate Limiting / Politeness

No rate limiting detected. Recommended:
- 1-2 second delay between pages
- Cache province/dropdown data
- Full scrape takes ~15 seconds (7 pages x 2s delay)

## Promotion Properties

The `/assetpromotion` page shows properties with active `idEvent[]` entries.
These are filtered at the SSR level, not via the API. To find promotions,
check `idEvent` array in listing data — non-empty means promotion active.

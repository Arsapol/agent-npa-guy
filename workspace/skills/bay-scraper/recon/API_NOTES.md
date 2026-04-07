# BAY/Krungsri (krungsriproperty.com) API Recon

## Overview

- **Provider**: Bank of Ayudhya (BAY) / Krungsri
- **Website**: https://www.krungsriproperty.com
- **CMS**: Kentico Xperience (ASP.NET Core)
- **Total properties**: ~1,690 declared (1,268 unique codes extractable via regex)
- **Property types**: Houses, townhouses, condos, land, shophouses, warehouses, hotels, etc.
- **Condos**: YES — 359 Z-suffix codes are condos (isCondo=true, category C)
- **Date checked**: 2026-04-07

## Architecture

The site is **server-side rendered** (Kentico CMS). There is no SPA framework.
Property data is available via a single JSON API endpoint (`/Helpers/GetProperties`).
Search/listing pages are SSR HTML with client-side pagination.

## API Endpoints

### 1. Property Listing (JSON) -- PRIMARY ENDPOINT

```
GET /Helpers/GetProperties?listCodes={codes}&pageNumber=1&pageSize=50&orderBy=
```

- **Method**: GET
- **Auth**: None (public)
- **Rate limit**: None observed
- **Batch size**: Tested up to 50 codes per request (all returned)
- **Response**: JSON array of property objects (74 fields each)
- **Requires**: Property codes (comma-separated)

Example:
```
GET /Helpers/GetProperties?listCodes=AX1185,BX1538&pageNumber=1&pageSize=50&orderBy=
```

### 2. Search / Listing (HTML) -- CODE DISCOVERY

```
GET /search-result?keyWord=&category={cat}&province={province}&district={district}&priceMin={min}&priceMax={max}&landMin={min}&landMax={max}&condoSizeMin={min}&condoSizeMax={max}&sort={sort}&page={page}
```

- **Method**: GET
- **Response**: SSR HTML containing ALL property codes embedded in the page
- **Pagination**: Client-side (all codes in one HTML response, JS does pagination at 10/page)
- **Total count**: Embedded in `_convertDatasource({total})` JS call

**Filter parameters:**
| Parameter | Values | Notes |
|-----------|--------|-------|
| `keyWord` | text | Free-text search |
| `category` | A,B,C,D,E,F | Property category code (comma-separated) |
| `province` | Thai name | URL-encoded Thai province name |
| `district` | Thai name | URL-encoded Thai district name |
| `priceMin` | number | Minimum price in THB |
| `priceMax` | number | Maximum price in THB |
| `landMin` | number | Minimum land size |
| `landMax` | number | Maximum land size |
| `condoSizeMin` | number | Minimum condo size (sqm) |
| `condoSizeMax` | number | Maximum condo size (sqm) |
| `sort` | string | Sort order |
| `page` | number | Page number (client-side only) |

### 3. Property Detail (HTML)

```
GET /detail?code={code}
```

- Server-rendered HTML detail page
- Contains deed info, nearby places, contact info
- No additional JSON API for details (all data available in GetProperties)
- Map is loaded via Google Maps JS (no GPS in HTML; GPS is in API response)

### 4. Images

```
GET /images/{itemGUID_no_dashes}/{category}/{index}
```

- `00/01` = thumbnail (~72KB webp)
- `01/01` = full cover image (~520KB webp)
- `01/02`, `02/01` etc. = additional images (may be 0 bytes if none)
- itemGUID comes from the `itemGUID` field (strip dashes)
- `coverImageUrl` field provides the cover image path directly

## Property Categories

| Code | Thai Name | English Name | Count |
|------|-----------|--------------|-------|
| A | บ้านเดี่ยว | Single House | 341 |
| B | ทาวน์เฮาส์ | Townhouse | 273 |
| C | คอนโดมิเนียม | Condominium | 733 |
| D | อาคารพาณิชย์ | Shophouse | 148 |
| E | ที่ดินเปล่า | Vacant Land | 149 |
| F | อื่น ๆ | Other | 46 |

**Note**: Z-suffix codes (e.g. ABZ0550, AAZ0071) are condos with `isCondo=true`. The prior recon missed these because the regex pattern excluded `Z` codes.

## Property Type Distribution (from 902 fetched)

| Type | Count |
|------|-------|
| บ้านเดี่ยว (Single House) | 292 |
| ทาวน์เฮาส์ (Townhouse) | 262 |
| ที่ดินเปล่า (Vacant Land) | 136 |
| ตึกแถว (Shophouse) | 135 |
| บ้านแฝด (Semi-detached) | 25 |
| อาคารที่พักอาศัย (Residential Building) | 12 |
| โกดัง (Warehouse) | 9 |
| ห้องแถว (Row House) | 6 |
| โรงแรม (Hotel) | 5 |
| อาคารตึก (Building) | 5 |
| อาคารโรงคลุม (Covered Building) | 4 |
| เรือนแถว (Row House) | 2 |
| โฮมออฟฟิศ (Home Office) | 2 |
| อพาร์ทเม้นท์ (Apartment) | 2 |
| อาคารสำนักงาน (Office Building) | 2 |
| บ้านพักตากอากาศ (Resort House) | 1 |
| โชว์รูมรถยนต์ (Car Showroom) | 1 |
| โรงงาน (Factory) | 1 |

## Field Mapping (74 fields from GetProperties)

### Core Identity
| API Field | Description | Example |
|-----------|-------------|---------|
| `code` | Property code (PK) | `AX1185` |
| `itemID` | Internal Kentico ID | `866` |
| `itemGUID` | UUID (used for images) | `a97f6220-9d9f-41c6-9725-143267bfdb30` |
| `ou` | Organization unit | `BAY` |
| `ouName` | Organization name | `ธนาคารกรุงศรีอยุธยา จำกัด (มหาชน)` |

### Property Details
| API Field | Description | Example |
|-----------|-------------|---------|
| `propertyType` | Type code | `2` |
| `propertyTypeName` | Type name (TH) | `บ้านเดี่ยว` |
| `propertyTypeObject` | Full type object with EN name | `{code, name, name_EN, categoryCode}` |
| `propertyCategoryObject` | Category object with icons | `{code, name, name_EN, iconFilter, iconDetail}` |
| `project` | Project/village name (TH) | `บ้านฟ้า กรีนเนอรี่` |
| `project_EN` | Project name (EN) | `Baan Fah Greenery` |
| `detail` | Description (TH) | (free text) |
| `detail_EN` | Description (EN) | `Residential Zone, 4 m.width...` |
| `displayText` | Display name | `บ้านฟ้า กรีนเนอรี่` |
| `isCondo` | Condo flag | `false` (always false currently) |

### Location
| API Field | Description | Example |
|-----------|-------------|---------|
| `lati` | Latitude (string) | `"13.93490616"` |
| `long` | Longitude (string) | `"100.447325"` |
| `subdistrict` | Subdistrict (TH) | `บางพลับ` |
| `subdistrict_EN` | Subdistrict (EN) | `Bang Phlap` |
| `district` | District (TH) | `ปากเกร็ด` |
| `district_EN` | District (EN) | `Pak Kret` |
| `province` | Province (TH) | `นนทบุรี` |
| `province_EN` | Province (EN) | `Nonthaburi` |
| `defaultAddress` | Full address | `null` (not populated in API) |

### Size
| API Field | Description | Example |
|-----------|-------------|---------|
| `landSizeRai` | Land: rai | `0` |
| `landSizeNgan` | Land: ngan | `0` |
| `landSizeSqWa` | Land: sq.wa (fractional) | `73.3` |
| `landSizeTotalSqWa` | Land: total sq.wa | `73.3` |
| `sizeSqMeter` | Condo size (sqm) | `0.0` (non-condo) |
| `roomWidth` | Width (meters) | `15.0` |
| `roomDeepth` | Depth (meters) | `19.5` |
| `sizeText` | Formatted size string | `0 ไร่ 0 งาน 73 ตร.ว.` |

### Pricing (THB)
| API Field | Description | Example |
|-----------|-------------|---------|
| `salePrice` | Appraisal/sale price | `4978000.0` |
| `promoPrice` | Special/promo price | `3500000.0` |
| `discount` | Discount percentage | `29.69` |
| `finalPrice` | Final price | `3500000.0` |

### Title Deed
| API Field | Description | Example |
|-----------|-------------|---------|
| `deedNo` | Deed number (TH) | `โฉนด 18802` |
| `deedNo_EN` | Deed number (EN) | `Title deed no. 18802` |
| `owner` | Owner name (TH) | (usually empty) |
| `owner_EN` | Owner name (EN) | (usually empty) |

### Building Details
| API Field | Description | Example |
|-----------|-------------|---------|
| `bedCount` | Bedrooms | `3` |
| `bathCount` | Bathrooms | `4` |
| `parkCount` | Parking spots | `2` |
| `flagFitness` | Has fitness | `true` |
| `flagSwim` | Has pool | `true` |
| `flagSecurity` | Has security | `true` |
| `flagShop` | Has shops | `false` |
| `flagLift` | Has elevator | `false` |

### Status & Dates
| API Field | Description | Example |
|-----------|-------------|---------|
| `public` | Is published | `true` |
| `saleStatus` | Sale status code | `"1"` |
| `statusRemark` | Status remark | `""` |
| `beginDate` | Listing start | `2021-11-30T00:00:00` |
| `endDate` | Listing end | `0001-01-01T00:00:00` |
| `flagHighlight` | Featured property | `true` |
| `flagPromo` | Has promotion | `false` |

### Contact
| API Field | Description | Example |
|-----------|-------------|---------|
| `saleName` | Contact name (TH) | `คุณหฤทัย` |
| `saleName_EN` | Contact name (EN) | `Khun Haruthaw` |
| `saleContact` | Phone number | `02-296-4028` |

### Images
| API Field | Description | Example |
|-----------|-------------|---------|
| `coverImageUrl` | Cover image path | `/images/{guid}/01/01` |
| `listGallerryImage` | Gallery images | `[]` (always empty in API) |
| `listCoverImages` | Cover images list | `null` |
| `listOtherImages` | Other images list | `null` |
| `listDocumentImage` | Document images | `null` |
| `listMapImage` | Map images | `null` |
| `vdoURL` | Video URL | `""` |

### Metadata
| API Field | Description | Example |
|-----------|-------------|---------|
| `pageView` | View count | `3868` |
| `itemCreatedBy` | Creator ID | `67` |
| `itemCreatedWhen` | Created date | `2024-04-01T09:58:34` |
| `itemModifiedBy` | Modifier ID | `65` |
| `itemModifiedWhen` | Modified date | `2026-04-07T15:48:57` |
| `itemOrder` | Sort order | `0` |

## Scraping Strategy

### Recommended approach (2-step):

1. **Discover codes**: Fetch `/search-result?keyWord=` and extract all property codes using regex `[A-Z]{1,3}[XYZ]\d{3,5}(?:_[A-Z]+\d+)?`
   - All 1,268 codes are embedded in a single HTML page (JS pagination data)
   - Code suffixes: X=770 (houses/land), Z=359 (condos), Y=139 (land/special)
   - No multi-page crawling needed — one request gets all codes

2. **Fetch details**: Call `/Helpers/GetProperties?listCodes={batch}&pageNumber=1&pageSize=100&orderBy=` with batches of 50 codes
   - 1,268 codes / 50 per batch = 26 requests total
   - Returns 74 fields per property including GPS, pricing, deed, contact
   - No rate limiting observed

### Gallery images:
- Cover image: `https://www.krungsriproperty.com{coverImageUrl}`
- Thumbnail: `/images/{guid_no_dashes}/00/01`
- Full: `/images/{guid_no_dashes}/01/01`
- Gallery images are NOT returned by the API (listGallerryImage always empty)
- To get gallery, scrape detail page HTML for image elements

### Code format:
- Pattern: `{prefix}{X|Y|Z}{digits}`
- Prefix: 1-3 uppercase letters (A, AB, AK, etc.)
- X = houses/standard (770), Z = condos (359), Y = land/special (139)
- Compound codes: `AKX0192_AKY0077` (multiple assets)

## Limitations

1. **Gallery empty in API** -- `listGallerryImage` always returns `[]`; must scrape detail page HTML for gallery images
2. **1,268 vs 1,690 discrepancy** -- Site declares 1,690 but only 1,268 unique codes extractable via regex; ~422 may be delisted or use non-standard code formats
3. **No appraisal value separate from sale price** -- `salePrice` appears to be the appraised/asking price, `promoPrice` is the discounted price
4. **No building year/age** -- Not available in API or detail page
5. **No floor number for condos** -- `sizeSqMeter` is available but floor/unit number not exposed

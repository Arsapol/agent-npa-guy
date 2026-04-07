# LH Bank NPA Scraper - Recon Notes

## Overview

- **Provider**: LH Bank (ธนาคารแลนด์ แอนด์ เฮ้าส์)
- **Base URL**: `https://www.lhbank.co.th`
- **CMS**: Kentico (server-rendered HTML, no JSON API)
- **Total properties**: ~33 (as of 2026-04-07)
- **Data access**: Pure HTML scraping with selectolax
- **GPS availability**: 100% (all properties have lat/lng in hidden fields)

## Pages

| Page | URL | Purpose |
|------|-----|---------|
| Main listing | `/th/property-for-sale/asset-for-sale/` | All bank-owned NPA properties |
| Special price | `/th/property-for-sale/special-property` | Discounted properties (currently 0) |
| Online booking | `/th/property-for-sale/subscription-property` | Same 33 properties, booking flow |
| Detail | `/th/property-for-sale/detail/?AssetCode={code}&Asset={type}` | Individual property |

### Asset param values
- `Asset=1` — normal listing view
- `Asset=2` — subscription/booking view (same detail content)

## No Pagination Needed

All 33 properties render on a single page. No AJAX pagination, no "load more" button.
The listing is small enough to scrape in one request.

## No JSON API

The site is built on Kentico CMS with server-rendered HTML. No XHR/fetch API endpoints found.
Filters (province, district, asset type, price range) submit as form POST with ASP.NET ViewState,
but since total count is only 33, scraping the full page directly is simpler.

## Property Type Distribution (2026-04-07)

| Type | Count |
|------|-------|
| บ้านเดี่ยว 2 ชั้น | 10 |
| ทาวน์เฮ้าส์ | 9 |
| คอนโด (ห้องชุด) | 6 |
| ที่ดินเปล่า | 3 |
| มินิแฟคตอรี่ | 1 |
| ที่ดินเปล่า พร้อมสิ่งปลูกสร้าง | 1 |
| อาคารพาณิชย์ | 1 |
| (empty/0) | 2 |

## Listing Page Selectors

### Card container
```
#containerCards .item.asset-for-sale-bank
```

### Card fields

| Field | Selector | Notes |
|-------|----------|-------|
| Detail URL | `.item-detail-asset-for-sale` `onclick` attr | Pattern: `window.location.href='/th/property-for-sale/detail/?AssetCode=LH031A&Asset=1'` |
| Asset code | `.grid-cards-text .row` (1st) `.col` (2nd) | Label: รหัสสินทรัพย์ |
| Asset type | `.grid-cards-text .row` (2nd) `.col` (2nd) | Label: ประเภทสินทรัพย์ |
| Area | `.grid-cards-text .row` (3rd) `.col` (2nd) | Label: เนื้อที่ |
| Price | `[class*=price]` | Raw text, e.g. `3,000,000` |
| Location | Row containing `img[src*='pin-location']` parent text | Full Thai address |
| Thumbnail | `.card-img img` `src` | Relative URL, prepend BASE_URL |

### Parsing approach
Iterate `.grid-cards-text .row` elements, extract label/value pairs from child `div[class*=col]` elements.

## Detail Page Selectors

### Main container
```
.page-detail.assets-for-sale-detail
```

### Labeled fields (`.d-table` pairs)

| span ID | Label (Thai) | Field | Example |
|---------|-------------|-------|---------|
| `lbl_AssetCode` | (in h1) | Asset code | `LH031A` |
| `lbl_SalePrice` | ราคาประกาศขาย | Sale price (baht) | `3,000,000` |
| `lbl_CaseInformation` | ข้อมูลคดี | Case type | `สินทรัพย์ธนาคาร` |
| `lbl_Status` | สถานะ | Description/condition | Free text with bedrooms, floors, nearby transit, usable area |
| `lbl_AssetType` | ประเภทสินทรัพย์ | Property type | `คอนโด (ห้องชุด)` |
| `lbl_Address` | ที่ตั้งสินทรัพย์ | Full address | Thai address with soi, road, district, province |
| `lbl_Arae` | เนื้อที่/พื้นที่ใช้สอย | Area | `0-0-46.50 ตารางเมตร` (note: "Arae" is LH Bank's typo) |
| `lbl_PostDate` | วันที่บันทึก | Record date | `ข้อมูล ณ วันที่ 29/05/2568` |

### Hidden fields (GPS, PDF, map image)

| input ID | Field | Example |
|----------|-------|---------|
| `hdfLatitude` | GPS latitude | `13.787325` |
| `hdfLongitude` | GPS longitude | `100.5711829` |
| `hdfMap` | Map image URL | `/LH/media/Main/PageCover/pic1_29.jpg?ext=.jpg` |
| `hdfPDF` | PDF download URL | `/getattachment/.../property-for-sale-Detail-ดาวน์โหลดเอกสาร` |
| `hdfAssetCode` | Asset code (hidden) | `LH031A` |

### Image gallery
```
.fg-gallery img
```
Returns all property photos. Typical count: 10-18 images per property.
URLs are relative (e.g., `/getmedia/{guid}/{filename}.jpg?width=800&height=600&ext=.jpg`).

### Buttons
| Button | Class/ID | Action |
|--------|----------|--------|
| Google Maps | `button#btnGoogle` | Opens Google Maps with lat/lng from hidden fields |
| Map image | `button.image-maps` | Shows map image from `hdfMap` |
| PDF download | `button#btnPDF` | Downloads PDF from `hdfPDF` |
| Contact | `button.btn-contact` | Opens modal `.modal-contact` |
| Online booking | `button#btnAaccept` | Redirects to booking page |
| Print | `button.btn-print` | `window.print()` |

## Field Mapping Table

| LH Bank Field | DB Column | Source | Notes |
|---|---|---|---|
| AssetCode (URL param + lbl_AssetCode) | `property_id` (PK) | listing + detail | Unique identifier, e.g. `LH031A` |
| lbl_SalePrice | `sale_price` | detail | Integer, whole baht (remove commas) |
| lbl_CaseInformation | `case_info` | detail | Always "สินทรัพย์ธนาคาร" so far |
| lbl_Status | `description` | detail | Free text: condition, bedrooms, nearby, usable area |
| lbl_AssetType | `asset_type` | listing + detail | Enum: บ้านเดี่ยวชั้นเดียว, บ้านเดี่ยว 2 ชั้น, คอนโด, ทาวน์เฮ้าส์, etc. |
| lbl_Address | `address` | detail | Full Thai address |
| lbl_Arae | `area_text` | listing + detail | Raw text like `0-0-46.50 ตารางเมตร` or `0-0-80 ตารางวา` |
| lbl_PostDate | `post_date` | detail | Thai date `ข้อมูล ณ วันที่ DD/MM/BBBB` (Buddhist era) |
| hdfLatitude | `latitude` | detail (hidden) | Decimal degrees |
| hdfLongitude | `longitude` | detail (hidden) | Decimal degrees |
| hdfMap | `map_image_url` | detail (hidden) | Relative URL to map image |
| hdfPDF | `pdf_url` | detail (hidden) | Relative URL to PDF attachment |
| .fg-gallery img src | `images` (JSON array) | detail | Full-size photos, 10-18 per property |
| thumbnail (.card-img img) | `thumbnail_url` | listing | Card thumbnail image |
| location text (pin-location row) | `location_text` | listing | Shorter address from card |
| price text ([class*=price]) | `price_text` | listing | Same as sale_price, from card |

### Fields NOT available from LH Bank
- **Appraisal value** (ราคาประเมิน) — not shown
- **Land area vs usable area** — combined in single `lbl_Arae` field
- **Building year / age** — not shown (sometimes mentioned in `lbl_Status` free text)
- **Title deed type** (โฉนด/นส.3) — not shown
- **Floor/unit number** — sometimes in `lbl_Address` or `lbl_Status`
- **Project name** — sometimes extractable from `lbl_Status` or `lbl_Address`
- **Number of bedrooms/bathrooms** — sometimes in `lbl_Status` free text
- **Contact person** — generic bank hotline only (tel:1327, callcenter@lhbank.co.th)

## Area Format Parsing

The `lbl_Arae` field uses Thai land measurement format:
- `0-0-46.50 ตารางเมตร` → 46.50 sqm (condos)
- `0-0-80 ตารางวา` → 80 sq.wah (land/houses)
- `94-2-60 ไร่` → 94 rai 2 ngan 60 sq.wah (large land)
- Format: `{rai}-{ngan}-{sq.wah} {unit}`

## Scraper Architecture Recommendation

1. **Single request** fetches all ~33 listing cards
2. **Sequential detail requests** for each property (33 requests total)
3. **No rate limiting needed** — tiny dataset, but add 1-2s delay to be polite
4. **Semaphore(5)** for bounded concurrent detail fetches
5. **Price tracking**: Compare `lbl_SalePrice` on each scrape for price history
6. **Dedup**: Upsert by `property_id` (AssetCode)
7. **Parse `lbl_Status`** with regex for bedrooms, bathrooms, usable area, project name

## Contact

- Hotline: 1327
- Email: callcenter@lhbank.co.th

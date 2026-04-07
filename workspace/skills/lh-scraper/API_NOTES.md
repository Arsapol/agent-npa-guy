# LH Bank NPA Property Scraper — API Notes

## Site Overview

| Item | Value |
|------|-------|
| Provider | LH Bank (ธนาคารแลนด์ แอนด์ เฮ้าส์) |
| Base URL | `https://www.lhbank.co.th` |
| Listing URL | `/th/property-for-sale/asset-for-sale/` |
| Detail URL | `/th/property-for-sale/detail/?AssetCode={code}&Asset=1` |
| Platform | ASP.NET WebForms / Kentico CMS |
| Method | **Server-rendered HTML** (no usable JSON API) |
| Total properties | ~33 (as of 2026-04-07) |
| Inventory size | Very small — single page, no server-side pagination |

## How It Works

All properties are **pre-rendered in a single HTML page**. Client-side JavaScript splits them into pages of 9 (`.content[data-id="1"]` through `[data-id="4"]`) and toggles visibility with `onClickPageNumber()`.

There is a JSON API at `/CMSWebParts/Customization/InterestedAssets/API/SearchAssets.aspx/getData` but it returns **401 Unauthorized** without an active ASP.NET session — not usable for scraping. The server-rendered HTML contains all properties, so the API is unnecessary.

### Other Property Sections

| Section | URL | Notes |
|---------|-----|-------|
| ทรัพย์ของธนาคารเสนอขาย (main) | `/th/property-for-sale/asset-for-sale/` | 33 properties |
| ทรัพย์ราคาพิเศษ (special) | `/th/property-for-sale/special-property` | 0 properties (as of 2026-04-07) |
| จองซื้อทรัพย์ออนไลน์ (subscription) | `/th/property-for-sale/subscription-property` | 33 properties (same set, different detail URL param) |

## Search Filters (Client-Side)

The filters control the SearchAssets API call, but since we scrape all pre-rendered HTML, these are only relevant for reference:

| Filter | HTML ID | Values |
|--------|---------|--------|
| ประเภทสินทรัพย์ (type) | `#drpAssetType` | บ้านเดี่ยวชั้นเดียว, บ้านเดี่ยว 2 ชั้น, คอนโด (ห้องชุด), ทาวน์เฮ้าส์, มินิแฟคตอรี่, ที่ดินเปล่า, ที่ดินเปล่า พร้อมสิ่งปลูกสร้าง, อาคารพาณิชย์ |
| จังหวัด (province) | `#drpProvince` | Dynamic (loaded via JS from API) |
| อำเภอ/เขต (district) | `#drpDistrict` | Dynamic (depends on province) |
| ช่วงราคา (price range) | `#drpPrice` | 1=ต่ำกว่า 3M, 2=3M-5M, 3=มากกว่า 5M |

## Listing Page — CSS Selectors

### Property Card Structure

```
.item.asset-for-sale-bank
  .item-detail-asset-for-sale   [onclick="window.location.href='...'"]
    .item-container
      .card-img > img           [src = thumbnail URL]
      .grid-cards-text
        .row                    → label/value pairs (3 rows)
          div.col-auto          → label text
          div.col-7 / .col-6   → value text
        .row                    → address row
          div.col-1 > img.icon-location
          div.col-11.text-address-asset  → address text
        .font-size-price        → price (plain number, no ฿ symbol)
        a.card-more             → detail link (redundant with onclick)
```

### Extracting Fields from Card

| Field | Selector / Method |
|-------|-------------------|
| Asset code | Regex `AssetCode=(\w+)` from `.item-detail-asset-for-sale[onclick]` |
| Asset type | 2nd `.row` → `.col-6` text (label contains "ประเภท") |
| Area | 3rd `.row` → `.col-6` text (label contains "เนื้อที่") |
| Address | `.text-address-asset` text |
| Price | `.font-size-price` text → strip commas, parse int |
| Thumbnail | `.card-img img[src]` |
| Detail URL | Regex from onclick, or `a.card-more[href]` |

### Pagination

Client-side only. All cards pre-rendered in `.content[data-id]` containers:
- `data-id="1"`: cards 1-9
- `data-id="2"`: cards 10-18
- etc.

**No server-side pagination needed** — single GET request returns everything.

## Detail Page — CSS Selectors

### Main Container

```
.page-detail.assets-for-sale-detail
  .row
    .assets-for-sale-gallery    → image gallery
    .assets-for-sale-description → all text fields
```

### Field Extraction

Fields are in `div.d-table` rows within `.assets-for-sale-description`:

```
div.d-table
  div.d-table-cell.label    → field label (e.g. "ราคาประกาศขาย:")
  div.d-table-cell           → field value
```

| Field | Label Text | Example Value |
|-------|-----------|---------------|
| Asset code | H1 text | "รหัสสินทรัพย์:LH031A" |
| Asking price | ราคาประกาศขาย | 3,000,000 |
| Case info | ข้อมูลคดี | สินทรัพย์ธนาคาร |
| Status/description | สถานะ | ห้องชุดเดอะคริส รัชดา สภาพเดิม 1 ห้องนอน 1 ห้องน้ำ ... |
| Asset type | ประเภทสินทรัพย์ | คอนโด (ห้องชุด) |
| Location | ที่ตั้งสินทรัพย์ | ห้องชุดเลขที่ 324/111 ชั้น 8 ... เขตห้วยขวาง กรุงเทพมหานคร 10310 |
| Area | เนื้อที่/พื้นที่ใช้สอย | 0-0-46.50 ตารางเมตร |
| Record date | วันที่บันทึก | ข้อมูล ณ วันที่ 29/05/2568 |

### Hidden Inputs (GPS & Metadata)

Found via `input[type='hidden']` — name ends with the key after last `$`:

| Hidden Input | Key | Example |
|-------------|-----|---------|
| GPS Latitude | `hdfLatitude` | 13.787325 |
| GPS Longitude | `hdfLongitude` | 100.5711829 |
| Asset Code | `hdfAssetCode` | LH031A |
| Map Image | `hdfMap` | /LH/media/Main/PageCover/pic1_29.jpg |
| PDF Attachment | `hdfPDF` | /getattachment/.../ (may be empty) |

### Image Gallery

```
.assets-for-sale-gallery img    → all gallery images
```

Filter for `/getmedia/` in `src` to exclude UI icons. Images use Kentico CMS media URLs:
```
/getmedia/{uuid}/{filename}.jpg?width=800&height=600&ext=.jpg
```

Typical count: 10-15 images per property.

### Related Properties

`.section-relate-other` contains related property cards using the same `.item.asset-for-sale-bank` structure.

## Field Mapping: List vs Detail

| Data Point | List Page | Detail Page |
|-----------|-----------|-------------|
| Asset code | YES | YES |
| Asset type | YES | YES |
| Area text | YES | YES (more detail) |
| Address | YES (truncated) | YES (full) |
| Price | YES | YES |
| Thumbnail | YES (1 image) | YES (10-15 images) |
| Case info | NO | YES |
| Status/description | NO | YES (bedrooms, condition, nearby) |
| Record date | NO | YES |
| **GPS coordinates** | **NO** | **YES** (hidden inputs) |
| Map image | NO | YES |
| PDF document | NO | YES (when available) |

## Special Notes

### GPS Availability
- **10/10 properties checked have GPS** — appears to be mandatory for all listings
- Coordinates stored in hidden inputs `hdfLatitude` / `hdfLongitude`

### Appraisal / Title Deed
- **NO appraisal value provided** — only asking price
- **NO title deed information** (no โฉนด field)
- **NO land title type** (no นส.3, นส.4 distinction)

### Price Format
- Prices are in **whole baht** (integer)
- Displayed with comma separators, no ฿ symbol on cards
- No "ราคาประเมิน" (appraisal) field — only "ราคาประกาศขาย" (asking price)

### Area Format
- Format: `ไร่-งาน-ตารางวา/ตารางเมตร` (e.g. "0-0-46.50 ตารางเมตร")
- Condos use ตารางเมตร (sqm), land/houses use ตารางวา (sq wah)

### Status Field (สถานะ)
- This is a **free-text description**, NOT a status enum
- Contains: property name, condition, bedrooms, bathrooms, nearby transit, usable area
- Useful for extracting structured data with regex

### Scraper Strategy
1. Single GET to listing page → parse all 33 cards
2. For each card, GET detail page → parse fields + GPS + images
3. No authentication needed, no rate limiting observed
4. Total requests: 1 (listing) + N (details) = ~34 requests
5. Consider polite delay of 1-2s between detail requests

### Unique Identifier
- `asset_code` (e.g. "LH031A") — stable, unique per property
- Pattern: `LH` + 3 digits + 1 letter suffix (e.g. LH031A, LH004D, LHFG)

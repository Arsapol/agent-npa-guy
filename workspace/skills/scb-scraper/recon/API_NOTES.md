# SCB NPA API Recon — asset.home.scb

## Overview

- **Base URL**: `https://asset.home.scb/`
- **Total properties**: ~3,883 (as of 2026-04-07)
- **Architecture**: Server-rendered jQuery SPA. List/search via JSON API. Detail data is **server-rendered HTML** (the `get_project_detail` API endpoint is broken/session-locked and always returns the same cached property).
- **Auth**: None required for read operations
- **Rate limiting**: None observed (tested 500-item pages)

## API Endpoints

### 1. Search/List — `GET api/project/cmd`

**Command**: `get_project`

| Parameter | Type | Required | Example | Notes |
|-----------|------|----------|---------|-------|
| `command` | string | yes | `get_project` | Fixed value |
| `type` | string | yes | `project` | Fixed value |
| `page` | int | yes | `1` | 1-indexed |
| `limit` | int | yes | `50` | No hard cap; tested up to 500 |
| `sortBy` | string | no | `all` | `all`, `price_asc`, `price_desc`, `new` |
| `asset-type` | string | no | `condominiums` | See Asset Types below |
| `asset-location` | string | no | `1` or `1-1018` | Province ID, or `{province_id}-{district_id}` |
| `price-min` | int | no | `1000000` | In baht |
| `price-max` | int | no | `5000000` | In baht |
| `use-area-min` | int | no | `20` | Usable area in sqm |
| `use-area-max` | int | no | `40` | Usable area in sqm |
| `area-size-min` | int | no | `200` | Land area in sqw (ตร.ว.) |
| `area-size-max` | int | no | `500` | Land area in sqw |
| `amount-bedroom` | int | no | `1` | Number of bedrooms |
| `amount-bathroom` | int | no | `1` | Number of bathrooms |
| `find-search-text` | string | no | `สุขุมวิท` | Free-text search |
| `ownership` | string | no | `1` | `1` = ขายขาด (freehold). Other values untested. |

**Response**: `{ "s": "y", "m": "", "d": [...], "total": 3883 }`

**List item fields**:
```
project_id, project_type, project_title, price, price_discount,
project_address_detail, image_project, image_project_gen,
project_recommended, project_sold_out, project_booking, project_hide,
project_id_gen, owner_email, slug, promotion_description,
promotion_start_date, promotion_end_date, latitude, longitude,
contact_download_map, contact_download_map_gen,
category_find_home, category_find_loan, category_find_exchange,
create_date, district_id, province_id, area_use, land_area, area_sqm,
image_use, project_type_name, total_favorite, total_booking,
data_location, project_new, project_address, promotion_status
```

**Key field notes**:
- `price`: String with commas, e.g. `"4,620,000"` — in whole baht
- `price_discount`: String `"0"` when no discount
- `latitude`/`longitude`: String with decimals
- `area_use`: String, usable area in sqm
- `land_area`: String, land area in sqw (ตร.ว.)
- `area_sqm`: Float, land area converted to sqm
- `project_id_gen`: SCB internal asset code, e.g. `"41002S20G2B01909"`
- `slug`: Thai URL slug for detail page
- `image_use`: Relative path for thumbnail, prefix with BASE_URL

### 2. Province List — `GET api/project/cmd`

**Command**: `get_province`

**Response**: `{ "s": "y", "d": [{ "province_id": 1, "title": "กรุงเทพมหานคร", "area": "BKK" }, ...] }`

- 77 provinces total
- Province IDs are **custom** (NOT standard Thai codes). Bangkok = 1.
- `area` field: region code (BKK, CEN, EAS, NORE, NOR, SOU, WES)

### 3. District List — `GET api/project/cmd`

**Command**: `get_district`

| Parameter | Type | Required |
|-----------|------|----------|
| `province_id` | string | yes |

**Response**: `{ "s": "y", "d": [{ "district_id": 1018, "title": "คลองสาน" }, ...] }`

Bangkok has 51 districts.

### 4. Autocomplete — `GET api/project/cmd`

**Command**: `get_suggest`

| Parameter | Type | Required |
|-----------|------|----------|
| `k` | string | yes |

**Response**: `{ "s": "y", "d": [{ "id": 123, "name": "..." }, ...] }`

### 5. Map Pin Detail — `GET api/project/cmd`

**Command**: `get_list_detail`

| Parameter | Type | Required |
|-----------|------|----------|
| `project_id` | string | yes |

Returns a subset of fields for map popup display.

### 6. Detail Page — `GET /project/{slug}` (HTML)

**NOT a JSON API** — the detail page is server-rendered HTML. Must be parsed with selectolax.

#### Hidden inputs available:
| Input ID | Maps to |
|----------|---------|
| `pid` | project_id |
| `pjt` | project_type (e.g. `condominiums`) |
| `lat` | latitude |
| `lng` | longitude |
| `txt-project-code` | SCB asset code (e.g. `42002S20G2B01901`) |
| `txt-project-name` | project_title |
| `txt-project-type` | project_type |
| `txt-location` | district, province display text |
| `chk-sold-out` | sold out flag (`F`/`T`) |
| `value-loan-capacity` | price (string with commas) |

#### Parseable from `.project_detailed` div:
| Field | Regex pattern |
|-------|--------------|
| Code | `รหัส:(.+?)ประเภท` |
| Type name | `ประเภท:(.+?)เอกสารสิทธิ์` |
| Title deed | `เอกสารสิทธิ์:(.+?)เนื้อที่` |
| Land area | `เนื้อที่:(.+?)พื้นที่ใช้สอย` |
| Usable area | `พื้นที่ใช้สอย:(.+?)ห้องนอน` |
| Bedrooms | `ห้องนอน:(\d+)` |
| Bathrooms | `ห้องน้ำ:(\d+)` |
| Parking | `ที่จอดรถ:(\d+)` |
| Description | After `รายละเอียดทรัพย์` |

#### Images from HTML:
- `img[src*="stocks/project"]` and `[data-src*="stocks/project"]`
- Full size: URLs containing `o0x0`
- Thumbnails: URLs containing `c300x200` or `d800x600`

### 7. Home/Hot Properties — `GET api/home/cmd`

**Command**: `get_home_project`

| Parameter | Value |
|-----------|-------|
| `type` | `project` |
| `badge` | `hot` or `recommended` |
| `page` | 1 |
| `limit` | 10 |

Returns featured/promoted properties (same field structure as list).

## Asset Types

### Working types (verified with results):
| Code | Thai Name | Count |
|------|-----------|-------|
| `condominiums` | ห้องชุด/คอนโดมิเนียม | 1,240 |
| `townhouses` | ทาวน์เฮ้าส์ | 878 |
| `single_houses` | บ้านเดี่ยว | 840 |
| `duplex_homes` | บ้านแฝด | 174 |
| `vacant_land` | ที่ดินว่างเปล่า | 103 |
| `warehouses` | โกดัง | 64 |
| `office_buildings` | อาคารสำนักงาน | 30 |
| `factories` | โรงงาน | 22 |
| `building` | อาคาร | 21 |
| `semi_concrete_and_wood` | บ้านครึ่งตึกครึ่งไม้ | 14 |
| `apartment_or_dormitories` | อพาร์ทเม้นท์/หอพัก | 4 |
| `hotels` | โรงแรม | 3 |
| `gas_station` | สถานีบริการน้ำมัน | 2 |

### Non-working types (pipe `|` in value breaks filter):
`homes_with_business|home`, `bussiness_premises|home`, `home_office|home`,
`bussiness_premises|business`, `homes_with_business|business`, `home_office|business`

Also zero results: `golf_field`, `school`

## Scraping Strategy

### For the scraper:
1. **List endpoint** provides most fields needed: price, GPS, area, type, images, province/district
2. **Detail page HTML** provides: title deed type, bedrooms, bathrooms, parking, description, contact phone numbers, full-res images
3. **Pagination**: Use `limit=200` per page, iterate until `page * limit >= total`
4. **No detail API**: Must fetch detail page HTML for each property and parse with selectolax

### Image URL patterns:
- Base: `https://asset.home.scb/`
- Thumbnail: `stocks/project/c300x200/{gen_prefix}/{image_file}`
- Medium: `stocks/project/d800x600/{gen_prefix}/{image_file}`
- Full: `stocks/project/o0x0/{gen_prefix}/{image_file}`

### Price notes:
- List API returns price as **string with commas** (e.g. `"4,620,000"`)
- Price is in **whole baht**
- `price_discount` is `"0"` when no discount, otherwise the discounted price string
- `promotion_status`: `"F"` = no promotion, `"T"` = has promotion

## Field Mapping Table

| Field | List API | Detail HTML | Notes |
|-------|----------|-------------|-------|
| GPS lat/lng | `latitude`, `longitude` | `#lat`, `#lng` inputs | String with decimals |
| Price | `price` | `value-loan-capacity` input | String with commas, in baht |
| Discount price | `price_discount` | — | `"0"` if none |
| Land area | `land_area` | Regex from detail text | sqw (ตร.ว.) |
| Usable area | `area_use` | Regex from detail text | sqm (ตร.ม.) |
| Bedrooms | — | Regex `ห้องนอน:(\d+)` | Only in detail page |
| Bathrooms | — | Regex `ห้องน้ำ:(\d+)` | Only in detail page |
| Parking | — | Regex `ที่จอดรถ:(\d+)` | Only in detail page |
| Floors | — | In description text | E.g. "2 ชั้น" |
| Building year | — | NOT available | Not provided by SCB |
| Title deed | — | Regex `เอกสารสิทธิ์:(.+?)` | E.g. "โฉนด 117533", "กรรมสิทธิ์ 741/204" |
| Project name | `project_title` | `#txt-project-name` | Full title |
| Asset code | `project_id_gen` | `#txt-project-code` | SCB internal code |
| Images | `image_use` (thumbnail) | `img[src*="stocks/project"]` | Multiple full-res from detail |
| Contact | — | In description text | Phone numbers in description |
| Sale type | — | `ownership` filter | `1` = ขายขาด |
| Sold out | `project_sold_out` | `#chk-sold-out` | `F`/`T` flag |
| Province | `province_id` | — | Custom ID, not standard Thai |
| District | `district_id` | — | Custom ID |
| Address | `project_address_detail` | `.project-map-address` | Full address string |
| Description | — | After `รายละเอียดทรัพย์` in detail | Free text with contact info |

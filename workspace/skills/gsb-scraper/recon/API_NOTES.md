# GSB (ออมสิน) NPA API — Reverse Engineering Notes

**Site**: https://npa-assets.gsb.or.th/
**Stack**: Next.js (SSR with getServerSideProps)
**Backend base**: `https://npa-assets.gsb.or.th/apipr`
**Total assets**: ~4,492 NPA properties (as of 2026-04-07)
**Auth**: None required — all endpoints are public GET

## API Endpoints

### 1. List/Search Properties
```
GET /apipr/npa/asset
```

**Query params:**

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `asset_type_dev` | string | Yes | Always `"npa"` |
| `asset_type_id` | int | No | Filter by type (341=land, 342=land+building, 343=condo) |
| `province_code` | string | No | 2-digit province code (e.g. "10" = Bangkok) |
| `district_code` | string | No | 2-digit district code |
| `sub_district_code` | string | No | Sub-district code |
| `asset_subtype_id` | int | No | Building subtype (34411=detached house, etc.) |
| `price_range` | int | No | 0=all, 1=<1.5M, 2=1-4M, 3=3.5-7M, 4=6.5-14M, 5=14-25M, 6=all (alias) |
| `asset_name_or_id` | string | No | Search by project name or NPA ID |
| `filter` | string | No | Sort: `"asc"` or `"desc"` (by price) |
| `page` | int | No | Page number (default 1) |
| `page_size` | int | No | Items per page (default 12) |

**IMPORTANT**: `page_size` does NOT limit actual results. The API returns ALL matching items regardless of page_size. The `page` and `page_size` values only affect `total_page` calculation in metadata. Use province/type filters to reduce result sets.

**Response structure:**
```json
{
  "status": 200,
  "message": "สำเร็จ",
  "list_asset_type": [{"name": "...", "id": 343}],
  "asset_count": null,
  "data": [
    {
      "asset_name": "คอนโด/อาคารชุด/ห้องชุด",
      "asset_type_id": 343,
      "page": 1,
      "page_size": 12,
      "total_page": 14,
      "asset_type_count": 636,
      "asset_list": [ ...items... ]
    }
  ]
}
```

**List item fields:**

| Field | Type | Description |
|-------|------|-------------|
| `asset_id` | string | Internal numeric ID |
| `asset_group_id` | string | GSB internal group ID (e.g. "GSBCD202100008") |
| `asset_group_id_npa` | string | Public NPA ID (e.g. "BKK620093") — **primary key** |
| `asset_type_id` | int | 341/342/343/344/345/346/347/348/349 |
| `asset_type_desc` | string | Type name in Thai |
| `asset_subtype_desc` | string | Subtype (บ้านเดี่ยว, ทาวน์เฮ้าส์, etc.) |
| `asset_name` | string/null | Project/condo name |
| `current_offer_price` | int | Current selling price (baht) — may equal xprice_normal |
| `xprice_normal` | int | Normal selling price (baht) |
| `xprice` | int | Promotional/special price (baht) |
| `xtype` | string | `"promotion"` if promo active, else `"normal"` |
| `image_id` | string | Primary image ID |
| `sum_rai` | int/null | Land area: rai |
| `sum_ngan` | int/null | Land area: ngan |
| `sum_square_wa` | int/null | Land area: sq wah |
| `square_meter` | float/null | Usable area (sqm) — mainly for condos |
| `rai_ngan_wa` | string | Formatted land area ("0 ไร่ 1 งาน 0 ตร.ว") |
| `province_name` | string | Province name (Thai) |
| `district_name` | string | District name (Thai) |
| `sub_district_name` | string | Sub-district name (Thai) |
| `village_head` | string | Village/project name |
| `deed_info` | string | Title deed info (e.g. "โฉนดที่ดิน 32880") |
| `ind_flag` | string | "Y"/"N" — industrial flag |
| `is_recommend` | bool | Recommended property |
| `promo_type` | string | Promotion type code |
| `promotion_type` | string | Promotion type |
| `events` | string(JSON) | JSON-encoded array of active promotions/events |
| `group_sell_price` | int | Group selling price |
| `group_special_price` | int/null | Group special price |

### 2. Property Detail (via HTML __NEXT_DATA__ parsing)
```
GET /asset/npa?id={npa_id}&asset_type_id={type_id}&type_id=asset_group_id_npa
```

Parse `<script id="__NEXT_DATA__">` JSON from the HTML response, then read `.props.pageProps.info`.

**Note**: The Next.js data route (`/_next/data/{buildId}/...`) is unreliable because `buildId` can differ between listing and detail pages during partial deploys. Direct HTML parsing is always reliable.

**Response**: `{ "pageProps": { "info": {...}, "list": {...}, ... } }`

**Detail `info` fields (superset of list fields):**

| Field | Type | Description |
|-------|------|-------------|
| `latitude` | string | GPS latitude (e.g. "13.713850") |
| `longitude` | string | GPS longitude (e.g. "100.441218") |
| `building_no` | string | Building number |
| `floor_no` | string | Floor number (condos) |
| `asset_number` | string | Unit/room number (condos, e.g. "471/348") |
| `square_meter` | float | Usable area in sqm |
| `square_wa` | float/null | Area in sq wah |
| `width_meter` | string | Plot width in meters |
| `depth_meter` | string | Plot depth in meters |
| `builded_year` | string/null | Year built (Buddhist era, e.g. "2545") |
| `road` | string | Road name |
| `alley` | string | Alley/soi name |
| `remark` | string/null | Additional notes |
| `is_public` | string | "Y"/"N" |
| `booking_count` | int | Current booking count |
| `count_view` | string | Page view count |
| `asset_pdf` | string/null | PDF document ID |
| `asset_image` | array | `[{"id": "452143"}, ...]` — photo IDs |
| `asset_map` | array | `[{"id": "486315"}, ...]` — map image IDs |
| `panorama_image` | array | Panorama image IDs (usually empty) |
| `buildings` | array | Building details (see below) |
| `events` | array | Active promotions (parsed, not JSON string) |

**Building detail sub-object:**
```json
{
  "building_no": "226",
  "building_code": "30070299765",
  "buildings": "1",
  "moo": "11",
  "asset_subtype_desc": "บ้านเดี่ยว",
  "number_floor": "1",
  "square_meter": 145.5,
  "bedroom_no": 0,
  "bathroom_no": 0,
  "livingroom_no": 0,
  "garage_capacity": 0,
  "image_id": "1259239",
  "deed_info": "โฉนดที่ดิน 32880",
  "asset_detail": "บ้านเดี่ยวตึกชั้นเดียว"
}
```

**Event/promotion sub-object:**
```json
{
  "event_id": 190,
  "group_id": 629,
  "promo_id": 249,
  "id": 121922,
  "event_name": "Big Mega Sale บ้านออมสิน ...",
  "location": "ธนาคารออมสินทุกสาขาทั่วประเทศ",
  "period": "03 เม.ย. 2569 - 30 ธ.ค. 2569",
  "start_date": "2026-04-03T00:00:00Z",
  "starting": true,
  "promotion_name": "งาน Big Mega Sale ...",
  "group_name": "อายุทรัพย์ 6 ปี - ไม่เกิน 9 ปี",
  "promotion_type": "1",
  "booking_price": 20000,
  "special_price": 1575000,
  "sell_price": 2250000,
  "is_special_price2": "N",
  "special_condition_remark": null
}
```

### 3. Lookup Endpoints

```
GET /apipr/npa/asset_type          → 9 asset types
GET /apipr/npa/asset_subtype       → 11 building subtypes
GET /apipr/npa/province            → 77 provinces
GET /apipr/npa/district?province_code=10   → districts for province
GET /apipr/npa/sub_district?province_code=10&district_code=22  → sub-districts
GET /apipr/npa/event               → 2 active events/promotions
```

### 4. Image/Document URLs

```
Image:  GET /apipr/npa/image?id={image_id}&asset_type_id={asset_type_id}
PDF:    GET /apipr/npa/image?id={asset_pdf}&asset_type_id={asset_type_id}
```

All media uses the same `/apipr/npa/image` endpoint. Returns `image/jpeg`.

## Reference Tables

### Asset Types (asset_type_id)
| ID | Short | Description |
|----|-------|-------------|
| 341 | LD | ที่ดิน (Land) |
| 342 | LB | ที่ดินพร้อมสิ่งปลูกสร้าง (Land + Building) |
| 343 | CD | คอนโด/อาคารชุด/ห้องชุด (Condo) |
| 344 | BD | อาคารสิ่งปลูกสร้าง (Building only) |
| 345 | MC | เครื่องจักร (Machinery) |
| 346 | CA | รถยนต์ (Car) |
| 347 | SH | เรือ (Ship) |
| 348 | RP | สิทธิการเช่า (Leasehold) |
| 349 | OT | อื่นๆ (Other) |

### Asset Subtypes (asset_subtype_id) — for type 342/344
| ID | Description |
|----|-------------|
| 34411 | บ้านเดี่ยว (Detached house) |
| 34412 | บ้านแฝด (Semi-detached) |
| 34413 | ทาวน์เฮ้าส์ (Townhouse) |
| 34414 | อาคารพาณิชย์ (Commercial) |
| 34415 | อาคารสำนักงาน (Office) |
| 34416 | โกดัง (Warehouse) |
| 34417 | ห้องแถว (Row house) |
| 34418 | โรงเรียน (School) |
| 34419 | หอพัก (Dormitory) |
| 34420 | โรงแรม (Hotel) |
| 34483 | อื่นๆ (Other) |

### Price Ranges (price_range)
| Value | Range (baht) |
|-------|-------------|
| 0 | All prices |
| 1 | Up to ~1,500,000 |
| 2 | ~1,000,000 - 4,000,000 |
| 3 | ~3,500,000 - 7,000,000 |
| 4 | ~6,500,000 - 14,000,000 |
| 5 | ~14,000,000 - 25,000,000 |
| 6 | All (same as 0) |

### Province Codes (examples)
| Code | Province |
|------|----------|
| 10 | กรุงเทพมหานคร |
| 11 | สมุทรปราการ |
| 12 | นนทบุรี |
| 13 | ปทุมธานี |
| 20 | ชลบุรี |
| 73 | นครปฐม |

## Scraping Strategy

1. **No pagination needed** — `/apipr/npa/asset` returns ALL items when filtered by `asset_type_id`. Use one call per type.
2. **Three relevant types**: 341 (107 land), 342 (3,749 land+building), 343 (636 condos) = ~4,492 total
3. **Detail via HTML parsing** — Fetch `/asset/npa?id={npa_id}&asset_type_id={type_id}&type_id=asset_group_id_npa` and parse `__NEXT_DATA__` from HTML
4. **Do NOT use Next.js data routes** — buildId is unstable across partial deploys
5. **No rate limiting observed** — but use semaphore(10) per project standard
6. **No cookies/auth required**
7. **Prices in whole baht** (integer)

## Key Differences from Other Scrapers
- List endpoint returns ALL items (no real pagination) — simpler than BAM/SAM
- Detail available via Next.js SSR data route (needs buildId)
- GPS coordinates in detail only (not in list)
- Building year in Buddhist era (subtract 543 for CE)
- Events/promotions are embedded (JSON string in list, parsed object in detail)
- `xprice` = promotional price, `xprice_normal` = normal price, `current_offer_price` = active price

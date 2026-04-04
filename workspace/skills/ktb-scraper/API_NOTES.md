# KTB NPA API Notes

## Base URL
`https://npa.krungthai.com/api/v1/`

## Endpoints

| Endpoint | Method | Auth | Purpose |
|----------|--------|------|---------|
| `/product/searchAll` | POST | No | Paginated property listing |
| `/product/searchSaleDetail` | POST | No | Full property detail |
| `/product/promotionSale` | POST | No | Promotion-only listing |
| `/product/flashSale` | POST | No | Flash sale listing |
| `/product/mortgageSale` | POST | No | Mortgage sale listing |
| `/product/ledSale` | POST | No | LED auction listing |
| `/product/homePage` | POST | No | Homepage featured |
| `/product/getContact` | POST | No | Contact info per property |
| `/product/getPromotionDropdown` | GET | No | Active promotions |
| `/system/getCategoryList` | GET | No | 26 property types |
| `/system/DopaProvince/dopaProvinceListNew/detail` | GET | No | 77 provinces + districts |

## Rate Limits
- Same origin for all endpoints — shared rate limit
- Observed threshold: ~30 req/60s (returns 500, not 429)
- Conservative setting: 25 req/60s with sliding window

## Search Body
```json
{
  "shrProvince": "กรุงเทพมหานคร",
  "shrAmphur": "",
  "typeProp": [],
  "priceRangeMin": "",
  "priceRangeMax": "",
  "orderBy": "",
  "search": "",
  "collCode": "",
  "paging": {"totalRows": 0, "rowsPerPage": 50, "currentPage": 1}
}
```

## Detail Body
```json
{"speedDy": 0, "collGrpId": "230741", "cateNo": 3}
```

## Key Fields

| Field | Type | Notes |
|-------|------|-------|
| `collGrpId` | int | Primary key (property group ID) |
| `collCateNo` | int | Property type (maps to getCategoryList) |
| `cateNo` | int | Sale category (1=พร้อมขาย, 3=ราคาพิเศษ, etc.) |
| `priceNumber` | string | Current price in whole baht |
| `nmlPrice` | string | Normal/appraised price (formatted with commas) |
| `shrPriceVos` | array | Year-over-year price history |
| `area` | string | "rai-ngan-wah" format (e.g. "0-0-42.6") |
| `sumAreaNum` | float | Total area in sqm |
| `lat`/`lon` | string | GPS coordinates |

## Date Format Gotcha
- **Search**: `YYYY-MM-DD` (ISO)
- **Detail**: `DD/MM/BBBB` (Buddhist Era, +543 years)

## Detail Adds Over Search
- `collTypeName` — e.g. "ที่ดินพร้อมสิ่งปลูกสร้าง"
- `collDesc` — full description
- `listImg` — array of `{attTypeId, fileName, collId, seqNo}`
- `lodge` — occupancy status
- `shrAddrline1/2` — address lines
- `bedroomNum`, `bathroomNum` — room counts
- `nearHospitalName/Dist`, `nearSchoolName/Dist`, `nearShopName/Dist`
- `shrPriceVos` — 5 years (vs 2-3 in search)

## Total Properties (as of 2026-04-04)
- searchAll: 2,673
- promotionSale: 2,175
- ledSale: 4,612
- flashSale: 76
- mortgageSale: 19

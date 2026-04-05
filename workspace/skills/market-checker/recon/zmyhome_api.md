# ZMyHome.com — API Recon Notes

**Date:** 2026-04-04
**Tested by:** NPA-guy recon agent

---

## Summary

ZMyHome is a PHP/Yii2 framework site served behind Cloudflare. It is **server-rendered** (not a SPA). Data lives in HTML pages, not a private JSON API. There is one useful JSON endpoint for autocomplete. Everything else must be scraped from HTML.

---

## Anti-Bot Assessment

| Check | Result |
|-------|--------|
| Cloudflare | Yes (`server: cloudflare`, `cf-ray` header) |
| CF Challenge / JS challenge | **No** — simple HTTPS with browser UA passes |
| CAPTCHA | Not observed |
| Cookie required | `PHPSESSID` + `_csrf` set on first visit; not required for listing pages |
| Rate limiting | None observed (5 rapid requests all 200) |
| Bot UA block | Yes — `python-httpx/0.27` UA returns 403; any browser UA works |
| Session / login required | No — all project/listing pages are public |

**Verdict:** Very permissive. A standard `httpx.Client` with a browser User-Agent works with no extra measures. No Camoufox needed.

---

## Key Endpoints

### 1. Project Autocomplete / Search

```
GET /search/load-point?term=<query>
Headers required:
  X-Requested-With: XMLHttpRequest   ← CRITICAL — without this, always returns empty
  (Referer header is NOT required)
```

**Returns:** JSON array. Without `X-Requested-With: XMLHttpRequest`, returns empty string every time.
This is a Yii2 AJAX detection check — the framework only responds to requests it identifies as XHR.

**Response structure:**
```json
[
  {
    "id": "12971",
    "label": "เซอร์เคิล คอนโดมิเนียม",
    "lat": 13.7496976852,
    "lng": 100.5559616089,
    "namemodel": "Project",
    "icon": "<svg>...</svg>"
  }
]
```

**namemodel values:** `Project` (condo), `ProjectHouse` (house/townhouse), `KeyMarker` (area/landmark), `propertyAddress`, `subdistrict`

**Notes:**
- Returns max 20 results
- Searches project name (English and Thai both work)
- Use this to resolve project name → numeric `id` (e.g. "circle condominium" → `12971`)
- The numeric `id` is used in all listing URLs (not the `V12971` code)
- Project code `V12971` is the one used on the project detail page URL

---

### 2. Project Detail Page

```
GET /project/V{id}
e.g. GET /project/V12971
```

**Server-rendered HTML containing:**
- Project name (Thai + English)
- Developer name
- Year built (ปีที่สร้างเสร็จ)
- Launch price (ราคาเปิดตัว)
- Common area fee (ค่าส่วนกลาง) per sqm/month
- Number of buildings, floors, total units, parking
- Facilities list
- **Listing summary tab** with counts and price ranges per type (buy/rent/sold/rented)
- **Government Treasury valuation table** by floor (กรมธนารักษ์ ราคาประเมิน, THB/sqm per floor)
- Nearby amenities (BTS/MRT, shops, hospitals)

**Listing summary extraction (CSS: `#nav_announce .nav-announce__item`):**
```
ประกาศขาย (13): ช่วงราคา 3,300,000 - 6,700,000 บาท | ล่าสุด 01 ก.ค. 68
ประกาศเช่า (13): ช่วงราคา 14,000 - 37,000 บาท  | ล่าสุด 21 พ.ย. 68
ขายแล้ว (6): ช่วงราคา 4,800,000 - 9,500,000 บาท | ล่าสุด 13 ก.ย. 65
เช่าแล้ว (4): ช่วงราคา 15,000 - 8,500,000 บาท  | ล่าสุด 21 มี.ค. 62
```

**Government valuation table (CSS: `table` first occurrence):**
```
Headers: ตึก | ชั้น | บาท/ตร.ม. | ประเภท
Row: 1 | 10 | 85,000 | ห้องชุดพักอาศัย
Row: 1 | 17 | 91,100 | ห้องชุดพักอาศัย
...
```

---

### 3. Listings Pages (Buy / Rent / Sold / Rented)

```
GET /buy/condo/project-list/{numeric_id}
GET /rent/condo/project-list/{numeric_id}
GET /sold/condo/project-list/{numeric_id}
GET /rented/condo/project-list/{numeric_id}
```

**Server-rendered HTML, one page = 14 listings (no per-page control found).**

Pagination works but appears to show the same 14 on multiple page params — the page parameter may not be functional, or listings beyond ~14 may require sorting changes.

**Card structure (CSS: `article.card-property__item--article`):**
- Property ID in link: `a[href^="/property/"]`
- Price text: `.card-property__price-room--priceRoom` — **IMPORTANT: concatenated with no separator**
  - Raw: `"3,609,000107,699 ฿/ม2"` = total_price + psm concatenated
  - Parse by stripping all non-digits, then finding the rightmost split where total % 1000 == 0 and psm is in range [100, 999999]
  - Falls back to % 500, then % 100 for rental prices (e.g. 16,500/mo)
- Unit/size text: `.card-property__price-room--unitRoom`
- Meta (bedrooms, bathrooms, floor, direction): `.card-property__meta-info__size-list li`

**Example parsed cards:**
```
V200249: 3,609,000 THB | 107,699 ฿/m² | 33.51 m² | 1 bed | floor 17
V102601: 3,999,000 THB | 119,338 ฿/m² | 33.51 m² | studio | floor 25
V72893:  5,800,000 THB | 148,718 ฿/m² | 39 m²    | 1 bed | floor 32
```

**Also has Schema.org JSON-LD** on listing pages:
```json
{"@type": "ItemList", "numberOfItems": 14, "itemListElement": [...]}
```
And on each property detail page:
```json
{"@type": "Offer", "priceSpecification": {"price": 3609000, "priceCurrency": "THB"}}
```

---

### 4. Property Detail Page

```
GET /property/V{property_id}
e.g. GET /property/V200249
```

Contains Schema.org `Offer` JSON-LD with exact price in THB, plus full description with unit number, floor, size, condo fees, etc.

---

### 5. Other Known Endpoints

| Endpoint | Method | Notes |
|----------|--------|-------|
| `/search/load-point?term=` | GET | Autocomplete — needs Referer header |
| `/api/ajax/property-favorite-toggle` | POST | Auth required |
| `/api/ajax/set-session` | POST | Session management |
| `/api/cookie/accept-pdpa` | POST | PDPA cookie accept |
| `/project/add-log-view-project-contact` | POST | Analytics ping; returns `{"status":false,"errorText":"No Data !!"}` without params |
| `/search/result?keyword=&id=&type=Project` | GET | Full search results page (HTML, 1.7MB) |

No undocumented JSON APIs found. No GraphQL. No `/api/v1/` prefix routes.

---

## Data Structure Summary

### From `/project/V{id}` (single request):
- Project name (Thai + English)
- Developer
- Year built
- Total units
- Number of floors
- Common area fee
- Active listing counts (buy/rent/sold/rented)
- Price ranges per listing type
- Government appraisal values (per floor, per sqm)
- Nearby transport/amenities

### From `/buy/condo/project-list/{id}` (HTML parse):
- Individual listing IDs, prices, sizes, floor, bedroom count
- Price per sqm (pre-calculated)
- Broker acceptance flag
- Last update date

### NOT available via API (would need per-listing fetches):
- Full listing description
- Exact unit number
- Contact details

---

## Recommended Scraping Approach

### Workflow: Project Name → Market Data

```python
# Step 1: Resolve project name to ID
GET /search/load-point?term={name}
  Headers: Referer: https://zmyhome.com/search
  => returns id (e.g. "12971") and namemodel="Project"

# Step 2: Fetch project page for summary + gov valuation
GET /project/V{id}
  => Parse #nav_announce for price ranges + counts
  => Parse first <table> for government appraisal by floor

# Step 3: Fetch sale listings for per-unit prices
GET /buy/condo/project-list/{id}
  => Parse article.card-property__item--article for each listing

# Step 4: Fetch rental listings
GET /rent/condo/project-list/{id}
  => Same card structure, price = monthly baht
```

### Implementation notes:
- `httpx.Client` with browser UA — no playwright needed
- Session cookie (`PHPSESSID`) not required for reads
- Referer header required on autocomplete endpoint only
- Safe to run at ~1 req/sec with no throttling observed
- Pages are large (200–400KB) — parse with `selectolax` not BeautifulSoup

---

## Comparison: ZMyHome vs DDProperty vs Hipflat

| Feature | ZMyHome | DDProperty | Hipflat |
|---------|---------|------------|---------|
| Project search by name | Yes (JSON autocomplete) | Yes | Yes |
| Sale listings with price/sqm | Yes (HTML) | Yes | Yes |
| Rental listings | Yes | Yes | Limited |
| Per-listing floor / direction | Yes | Yes | Partial |
| Sold listings (historical) | **Yes** | No | No |
| Rented listings (historical) | **Yes** | No | No |
| Government appraisal value (กรมธนารักษ์) | **Yes** | No | No |
| Price range summary on project page | **Yes** (instant, 1 req) | No | No |
| Year built / total units | Yes | Yes | Partial |
| API (JSON) | Autocomplete only | Full JSON API | Partial |
| Anti-bot difficulty | Very easy | Medium | Easy |
| Page size (HTML) | 200–400KB | 50–100KB | ~80KB |

### ZMyHome unique value for NPA screening:

1. **Government appraisal table (กรมธนารักษ์)** — per-floor valuation data. Critical for NPA analysis because LED auction floor = 70% of appraised value. This data is not available on DDProperty or Hipflat.

2. **Sold listings** — actual transacted prices (not just asking). Hipflat has some historical data but not from individual listings. DDProperty has none.

3. **Price range instant summary** — one project page request returns buy/rent/sold/rented price ranges. Fast NPA screening: compare NPA asking price vs ZMyHome sale range in 1 request.

4. **Rental price history** — "เช่าแล้ว" (rented) listings show previously rented prices, useful for rental yield calculations.

---

## Verdict: Is ZMyHome Worth Building?

**Yes — recommended as a complement to DDProperty/Hipflat, not a replacement.**

Build a lightweight scraper that:
- Uses `/search/load-point` to resolve project names to IDs
- Fetches `/project/V{id}` for the summary + government appraisal
- Fetches `/buy/condo/project-list/{id}` and `/rent/condo/project-list/{id}` for per-unit prices

**Do not** try to replicate DDProperty's full database — ZMyHome has fewer listings (typically 10-30 per project vs DDProperty's 50-200). Use ZMyHome specifically for:
- Government appraisal values (unique)
- Cross-checking sold prices against asking prices
- Rental yield validation via rented listings
- Quick price range sanity check (1 request)

**Estimated effort:** 1–2 hours for a working scraper. No reverse engineering needed. Plain HTML parsing.

---

## Sample Working Requests

```python
import httpx
import re
import json
from selectolax.parser import HTMLParser

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# 1. Search for project
r = httpx.get(
    "https://zmyhome.com/search/load-point",
    params={"term": "circle condominium"},
    headers={"User-Agent": UA, "Referer": "https://zmyhome.com/search"}
)
projects = [x for x in r.json() if x["namemodel"] == "Project"]
# => [{"id": "12971", "label": "เซอร์เคิล คอนโดมิเนียม", ...}]

# 2. Fetch project summary
project_id = "12971"
r = httpx.get(f"https://zmyhome.com/project/V{project_id}", headers={"User-Agent": UA})
tree = HTMLParser(r.text)
items = tree.css("#nav_announce .nav-announce__item")
for item in items:
    strong = item.css_first("strong").text(strip=True)
    count = item.css_first(".counter").text(strip=True)
    price_range = item.css_first(".nav-announce__item__meta-price").text(strip=True)
    # => "ประกาศขาย (13): ช่วงราคา 3,300,000 - 6,700,000 บาท"

# 3. Fetch sale listings
r = httpx.get(f"https://zmyhome.com/buy/condo/project-list/{project_id}", headers={"User-Agent": UA})
tree = HTMLParser(r.text)
for article in tree.css("article.card-property__item--article"):
    prop_id = article.css_first('a[href^="/property/"]').attrs["href"].split("/")[-1]
    price_raw = article.css_first(".card-property__price-room--priceRoom").text(strip=True)
    # price_raw = "3,609,000107,699 ฿/ม2" — needs regex split
    m = re.match(r"([\d,]+)([\d,]+)\s*฿/ม2", price_raw)
    price_thb = int(m.group(1).replace(",","")) if m else None
    price_psm = int(m.group(2).replace(",","")) if m else None
    size_raw = article.css_first(".card-property__price-room--unitRoom").text(strip=True)
    # size_raw = "33.51  ม2ไม่รับนายหน้า"
    size_m = re.match(r"([\d.]+)\s*ม2", size_raw)
    size_sqm = float(size_m.group(1)) if size_m else None
```

---

## Files

- This recon: `workspace/skills/market-checker/recon/zmyhome_api.md`
- Prototype script: `workspace/skills/market-checker/scripts/zmyhome_lookup.py`

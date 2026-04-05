# Hipflat.co.th API Recon

**Date:** 2026-04-04  
**Status:** Complete — working prototype available

---

## Summary

Hipflat is a **Server-Side Rendered (SSR)** site powered by a Java/Spring backend (no Next.js). All project data is embedded in the HTML response. There is **no public JSON API** for project detail pages — but there IS a working autocomplete/search API and UUID-based page routing that makes automation viable.

---

## API Endpoints Discovered

### 1. Project Search / Autocomplete

```
GET https://www.hipflat.co.th/api/geo?projects=true&q={query}
```

- **Returns:** JSON array of matching projects
- **Authentication:** Browser-style `User-Agent` required (plain Python UA → 403), no cookies needed
- **Rate limit:** Not observed — 5 rapid requests at 0.18s avg with no throttling
- **Response format:**

```json
[
  {
    "id": "f678b91e-5cb7-4eb7-9ba9-5518f8398417",
    "name": "15 สุขุมวิท เรสซิเด็นท์",
    "url_name": "",
    "parent_names": [],
    "depth": 0,
    "geo_level_name": "โครงการ",
    "categoryId": 2,
    "categoryText": "โครงการ"
  }
]
```

- `id` = UUID used for direct page routing
- `categoryId: 2` = projects (vs areas which are `1`)
- Works with English names (hipflat.com) — returns English field values
- Works with Thai names and partial matches
- Minimum query length: 2 characters

### 2. Project Page (UUID redirect)

```
GET https://www.hipflat.co.th/projects/{UUID}
→ 302 redirect to https://www.hipflat.co.th/projects/{slug}
```

- UUID from autocomplete API maps directly to a project page via redirect
- No need to construct the slug manually
- Example: `/projects/f678b91e-5cb7-4eb7-9ba9-5518f8398417` → `/projects/15-sukhumvit-residences-htzxov`

### 3. English Version (hipflat.com)

```
GET https://www.hipflat.com/api/geo?projects=true&q={query}
GET https://www.hipflat.com/projects/{UUID}
```

- Same structure, same UUID namespace
- Returns English field names (`"Project"` not `"โครงการ"`)
- Price shown in **USD** on project pages (not THB)
- Thai version (hipflat.co.th) shows THB — use Thai version for NPA analysis

### 4. Internal APIs (not useful for data extraction)

These are POST endpoints for tracking/lead generation only:
- `POST /adform/api/events/impression`
- `POST /adform/api/events/apply`
- `POST /adform/api/lead-contact`
- `POST /api/v1/projects/apply`
- `POST /api/tracking/track`

---

## Data Available via HTML Extraction

All data is in the HTML source of `/projects/{UUID}`. No JavaScript execution needed.

### From Thai page (hipflat.co.th) — preferred

| Field | Location | Example |
|-------|----------|---------|
| Project name (EN+TH) | `<h1>` tag | `15 Sukhumvit Residences (15 สุขุมวิท เรสซิเด็นท์)` |
| Avg sale price/sqm (project) | Inline text | `ราคาเฉลี่ย ขาย คือ ฿ 125,000 ต่อตารางเมตร` |
| Avg sold price/sqm (historical) | Market insights section | `ราคาเฉลี่ยต่อตารางเมตร: ฿110,000` |
| Price trend | Meta tag / inline | `แนวโน้มขาขึ้น` (uptrend) / `แนวโน้มขาลง` (downtrend) |
| YoY change | Market insights | `-1.3 % วิวัฒนาการเมื่อเทียบกับ มีนาคม 2025` |
| YtD change | Market insights | `+1.8 % ... -0.6 % นับตั้งแต่ต้นปี` |
| Units for sale (active listings) | Text pattern | `74 ยูนิตประกาศขาย` |
| Units for rent (active listings) | Text pattern | `151 ยูนิต` ให้เช่า |
| Sale price range | FAQ JSON-LD | `฿ 3,300,000 จนถึง ฿ 63,125,000` |
| Rent price range | FAQ JSON-LD | `฿ 12,000 / เดือน จนถึง ฿ 214,170 / เดือน` |
| Days on market (avg) | Sold insights | `1253 วันในตลาดก่อนขายได้` |
| Sold below asking (%) | Sold insights | `ต่ำกว่าราคาขายเดิม 14%` |
| District avg sale price/sqm | Market insights | `฿ 157,894/ตรม` (Watthana) |
| District avg rent price/sqm | Market insights | `฿ 650/ตรม` |
| District vs Bangkok premium | Market insights | `12.1 % สูงกว่า กรุงเทพ ค่าเฉลี่ย` |
| Avg rent by bedroom type | Market insights | `สตูดิโอ ฿ 18,000, 1BR ฿ 28,000` |
| Year completed | Header specs | `ม.ค. 2013 สร้างเสร็จแล้ว` |
| Floors | Header specs | `25 ชั้น` |
| Total project units | Description text | `159 ยูนิต` (from description paragraph) |
| Buildings | Header specs | `1 จำนวนอาคาร` |
| Service charge | Project specs | `฿ 40/sqm` |
| Sinking fund | Project specs | `฿ 500/sqm` |
| BTS/MRT distance | FAQ JSON-LD | named stations |
| Recent transactions | Previous sales table | date, price, price/sqm, size, floor |

### Key Regex Patterns (Thai page)

```python
# Avg sale price/sqm for THIS project (current listings)
re.findall(r'ราคาเฉลี่ย ขาย คือ ฿ ([\d,]+)', html)
# → ['125,000']

# Avg sold price/sqm (historical transactions)
re.findall(r'ราคาเฉลี่ยต่อตารางเมตร:?\s*฿?\s*([\d,]+)', html)
# → ['110,000', '157,894', '650']  (project, district sale, district rent)

# Price trend direction
re.findall(r'แนวโน้ม(ขาขึ้น|ขาลง)', html)
# → ['ขาขึ้น'] = uptrend

# YoY change percentage
re.findall(r'([+-]?\d+\.?\d*)\s*%\s*วิวัฒนาการเมื่อเทียบกับ', html)
# → ['-1.3']

# Active sale listings count
re.findall(r'(\d+)\s*ยูนิตประกาศขาย', html)
# → ['74']

# Active rental listings count  
re.findall(r'ให้เช่า\s+(\d+)\s+ยูนิต', html)
# → ['151']

# Sold below asking %
re.findall(r'ต่ำกว่าราคาขายเดิม\s*([\d.]+)%', html)
# → ['14']

# Days on market
re.findall(r'(\d+)\s*วันในตลาดก่อนขายได้', html)
# → ['1253']

# Year completed
re.findall(r'(ม\.ค\.|ก\.พ\.|มี\.ค\.|เม\.ย\.|พ\.ค\.|มิ\.ย\.|ก\.ค\.|ส\.ค\.|ก\.ย\.|ต\.ค\.|พ\.ย\.|ธ\.ค\.)\s*(\d{4})', html)
# → [('ม.ค.', '2013')]

# Sale price range
re.findall(r'ราคาขาย.*?฿\s*([\d,]+).*?฿\s*([\d,]+)', html)
# or from FAQ JSON-LD (more reliable)
```

---

## Authentication & Anti-Bot

### What works

- **Browser User-Agent required**: Any realistic browser UA string works, no cookies needed
- **Plain Python UA (`python-requests/...`) → 403** — blocked by Cloudflare
- **No session cookies needed** for either the autocomplete API or page fetches
- The site does set `_hipFlat_user_id` and `Origin` cookies on homepage visit, but they are NOT required for data access

### Cloudflare presence

- `Server: cloudflare` on all responses
- `CF-RAY` header present
- Lightweight protection only — no JS challenge, no CAPTCHA observed
- `window.__CF$cv$params` in page HTML but no active bot detection triggered

### Required headers (minimal)

```python
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Referer': 'https://www.hipflat.co.th/',
}
```

### Rate limiting

- No observable rate limiting at normal scraping speeds
- 5 rapid sequential requests completed in 0.18s avg each
- Recommend polite delays (1-2s) to avoid triggering future protection

---

## Slug Format

```
{project-name-romanized}-{6-char-id}
Example: 15-sukhumvit-residences-htzxov
```

- The 6-char suffix is NOT derived from the UUID — it's an opaque server-assigned ID
- **Do NOT try to construct slugs** — use UUID routing instead
- UUID comes from `/api/geo?projects=true&q=...` autocomplete

---

## Recommended Automation Approach

### Step 1: Search by project name → UUID
```
GET /api/geo?projects=true&q={project_name}
→ parse id field from first result
```

### Step 2: Fetch project page via UUID
```
GET /projects/{uuid}
→ follows redirect to /projects/{slug}
→ parse HTML for all data fields
```

### Two-request lookup, no cookies, no JS execution needed.

**Estimated time per lookup:** ~0.5-1s total (two HTTP requests)

---

## Data Quality Notes

- **Avg sale price/sqm** shows TWO values: `ราคาเฉลี่ย ขาย คือ ฿ X` = current listing avg; `ราคาเฉลี่ยต่อตารางเมตร: ฿Y` in the "sold properties" section = historical transaction avg
- Use the **historical transaction avg** for NPA valuation (more accurate, reflects actual deals not asking prices)
- **Total project units** is not cleanly tagged — best source is the description paragraph (e.g., "X ยูนิต การเดินทาง...")
- The sold properties section may be absent for newer or thinly-traded projects
- District averages are always present and reliable

---

## Sample Working Request (curl equivalent)

```python
import urllib.request
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Accept': 'application/json',
    'Referer': 'https://www.hipflat.co.th/',
}

# Search
url = "https://www.hipflat.co.th/api/geo?projects=true&q=15+sukhumvit+residences"
req = urllib.request.Request(url, headers=headers)
resp = urllib.request.urlopen(req)
results = json.loads(resp.read())
uuid = results[0]['id']  # "f678b91e-5cb7-4eb7-9ba9-5518f8398417"

# Fetch project page
page_url = f"https://www.hipflat.co.th/projects/{uuid}"
req2 = urllib.request.Request(page_url, headers={**headers, 'Accept': 'text/html'})
resp2 = urllib.request.urlopen(req2)
html = resp2.read().decode('utf-8')
# → parse with regex, see hipflat_checker.py
```

---

## Files

- `recon/hipflat_api.md` — this file
- `scripts/hipflat_checker.py` — working prototype for NPA screening

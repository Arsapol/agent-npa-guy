# BAM API Notes & Scraper Architecture

## API Endpoints

| Endpoint | Method | URL | Purpose |
|----------|--------|-----|---------|
| Provinces | POST | `bam-bo-api-prd.bam.co.th/master/province/filter` | 78 provinces `{value,label}` |
| Districts | POST | `bam-bo-api-prd.bam.co.th/master/District/Dropdown/find` | Districts per province |
| Search | POST | `bam-els-sync-api-prd.bam.co.th/api/asset-detail/search` | Paginated property search (201 on success, NOT 200) |
| Detail | GET | `bam-bo-api-prd.bam.co.th/property-detail/getExpiredSubscriptionDateTimeByAssetId/{id}` | Full detail: appraised value, grade, descriptions |
| Campaign | GET | `bam-bo-api-prd.bam.co.th/cmk-v2/getCampaignCondition/{id}` | Seasonal campaign conditions (often empty) |

## Critical Rate Limit Behavior (Search Endpoint)

- **Limit**: ~30-35 requests per ~60s window on `bam-els-sync-api-prd`
- **Symptom**: HTTP 500 after burst of search requests
- **Recovery**: API recovers after ~60s of no requests
- **Retrying the SAME failed request during the window always fails** — but NEW requests after cooldown succeed
- **Detail endpoint** (`bam-bo-api-prd`) has no observed rate limit — 100+ concurrent requests work fine
- **Solution**: Sequential search with 2.5s delay between requests (24 req/min)

## API Result Cap

- `totalData` field reports true count (e.g., 3276 for Bangkok)
- But the API **silently returns empty `data:[]` after page ~32** (~1600 results max)
- Only Bangkok exceeds 1600 as of 2026-04-04
- **Solution**: Drill down by district for provinces >1600 total

## Type Inconsistencies (Pydantic Gotchas)

BAM API returns wildly inconsistent types for the same field across different assets:

| Field | Expected | Actually returns |
|-------|----------|-----------------|
| `isCampaign` | str | `0`, `1` (int), `null`, `"true"` |
| `campaignName` | str | `["mahachonplus"]` (list), `null` |
| `hot_deals` | dict | `[]` (empty list), `null`, `{...}` |
| `highlights` | dict | `[]` (empty list), `null`, `{...}` |
| `property_highlight` | str | `False` (bool) |
| `display_home_condo` | str | `True`/`False` (bool) |
| `stars` | numeric str | `"โปรดเลือก"` (Thai text, 9 chars!) |

**Fix:** Use union types in Pydantic — `str | int | None`, `str | list | None`, `dict | list | None`, `str | bool | None`.

## Database Column Sizing

**Use `Text` for ALL string columns.** BAM API returns unpredictable string lengths. `varchar(50)` caused crashes on:
- `stars` field ("โปรดเลือก" instead of "1")
- Various other fields with unexpectedly long Thai text

Prices stored in **whole baht** (Numeric), same as JAM/SAM scrapers.

## Scraper Architecture

```
scrape_all()
  └─ for each province (fresh httpx client per province):
       └─ scrape_province()
            ├─ if total > 1600: fetch districts, drill down
            │   └─ _scrape_search_partition(province, district)
            │        └─ sequential search_page() with 2.5s delay
            ├─ else: _scrape_search_partition(province)
            └─ fetch details: semaphore(5), 0.2s per request
```

## DB Tables

- `bam_properties` — merged search + detail data, keyed by BAM asset ID
- `bam_price_history` — price change log (new, price_change, state_change)
- `bam_scrape_logs` — scrape run metadata

## Recon Data

`recon/` directory contains test API responses saved as JSON during initial development:
- `provinces.json`, `districts_bangkok.json`, `search_bangkok.json`
- `detail_responses.json`, `campaign_responses.json`
- `verify_fields.py`, `verify_live.py` — field coverage verification scripts

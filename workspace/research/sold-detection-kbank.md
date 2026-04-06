# KBank NPA — Sold Detection Investigation
Date: 2026-04-05

## DB Schema Findings

- **`is_sold_out`** (boolean): present on `kbank_properties`. KBank API returns this flag directly — when they mark a property as sold out it appears in the list response.
- **`is_reserve`** (boolean): also tracked; similar status flag.
- **`last_scraped_at`**: updated every scrape run via `_apply_item_to_prop`.
- **`first_seen_at`**: set once on insert.
- No `is_active` column. No `removed_at` column. No explicit "disappeared" tracking.

## Data Freshness

- Only **one scrape run** so far: 2026-04-04 (all 13,361 properties share same `last_scraped_at`)
- All `kbank_price_history` entries are `change_type = 'new'` — no price/status changes recorded yet
- 0 properties older than 7 days (all inserted 2026-04-04)

## `is_sold_out` Current State

| `is_sold_out` | Count |
|---|---|
| false | 13,206 |
| true | 155 |

KBank **keeps sold properties in the API response** with `is_sold_out = true` rather than removing them silently. This is different from what was assumed.

## Disappearance Detection — Can We Do It?

**Yes, but only after 2+ scrape runs exist.**

The pattern:
1. Each scrape updates `last_scraped_at` on every property it touches.
2. After a scrape completes, any property whose `last_scraped_at` < scrape start time was NOT returned by the API — it disappeared.
3. "Disappeared" = likely sold (or rarely, delisted for another reason).

Since there's only one scrape run, no disappearances can be detected yet. After the next daily scrape runs, the query below becomes meaningful.

## SQL Query: "Likely Sold / Disappeared"

```sql
-- Properties not seen in the most recent scrape run
-- Replace '2026-04-05 06:00:00+07' with the actual scrape start timestamp
SELECT
    property_id,
    property_type_name,
    province_name,
    amphur_name,
    sell_price,
    first_seen_at,
    last_scraped_at,
    is_sold_out
FROM kbank_properties
WHERE last_scraped_at < '2026-04-05 06:00:00+07'
ORDER BY last_scraped_at DESC;
```

**Dynamic version** (uses max scrape time as latest run marker):
```sql
WITH latest_run AS (
    SELECT max(last_scraped_at) AS run_ts FROM kbank_properties
)
SELECT
    p.property_id,
    p.property_type_name,
    p.province_name,
    p.amphur_name,
    p.sell_price,
    p.first_seen_at,
    p.last_scraped_at,
    p.is_sold_out
FROM kbank_properties p, latest_run
WHERE p.last_scraped_at < latest_run.run_ts - interval '10 minutes'
ORDER BY p.last_scraped_at;
```

The 10-minute buffer accounts for scrape duration across 268 pages.

## Recommended Implementation

To properly track disappearances, the scraper should:
1. After each full scrape completes, mark missing properties as removed:

```sql
-- Run after scraper finishes, passing $1 = scrape start timestamp
UPDATE kbank_properties
SET is_active = false, removed_at = now()
WHERE last_scraped_at < $1
  AND (is_active IS NULL OR is_active = true);
```

This requires adding `is_active` (boolean) and `removed_at` (timestamptz) columns — they don't exist yet.

**Alternatively** (no schema change): use `kbank_scrape_logs` to get `started_at` of the latest run, then query `last_scraped_at < started_at` as the "disappeared" set.

## Current Count of "Disappeared"

- **0** — only one scrape run exists. The query will return results after the next scheduled run (daily at 06:00).
- 155 properties are already marked `is_sold_out = true` by KBank's own API flag.

## Summary

| Question | Answer |
|---|---|
| `is_active` or similar flag? | No — only `is_sold_out` from API. No disappearance tracking. |
| Detect by `last_scraped_at`? | Yes — viable once 2+ runs exist |
| "Likely sold" SQL query? | See dynamic query above (uses max scrape ts as anchor) |
| How many disappeared? | 0 today (first scrape run was 2026-04-04); 155 already `is_sold_out = true` |

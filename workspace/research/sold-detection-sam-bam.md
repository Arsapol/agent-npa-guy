# Sold/Removed Property Detection — SAM, BAM, JAM, KTB

*Investigated: 2026-04-05 (updated with fresh DB queries)*

---

## Summary Table

| Provider | Explicit Sold Field | Disappearance Detection | Est. Sold/Removed |
|----------|--------------------|-----------------------|-------------------|
| SAM      | No (only `is_active`, all=true) | Yes via `is_active` flip or `updated_at` staleness | 0 confirmed; need multi-run history |
| BAM      | No explicit sold flag | Yes via `display_property` flip or `last_scraped_at` staleness | 0 confirmed currently; need multi-run |
| JAM      | YES — `status_soldout` boolean + `soldout_date` | Yes directly | 245 sold, 2,783 null (unknown) |
| KTB      | No explicit sold flag | Yes via `last_scraped_at` staleness or `price_end_dt` past | Stale check not yet possible (1 scrape run) |

---

## SAM

**Schema:** `is_active` (boolean), `status` (varchar), `updated_at`, `first_seen_at`

**Status values:**
- `ซื้อตรง` — Direct sale (4,523)
- `ประมูล` — Auction (150)
- `รอประกาศราคา` — Awaiting price announcement (34)

**Current state:**
- All 4,707 rows have `is_active = true`
- Data is very fresh: first scraped 2026-04-03, last updated 2026-04-04
- `registration_end_date` is null for all rows — not a useful sold signal

**Sold detection approach:**
SAM does not return removed/sold properties via API. When a property sells, it disappears from the search feed. Detection requires comparing consecutive scrape runs:

```sql
-- Properties gone missing (not refreshed in last N days)
SELECT sam_id, code, address_full, status, updated_at
FROM sam_properties
WHERE is_active = true
  AND updated_at < NOW() - INTERVAL '3 days'
ORDER BY updated_at ASC;
```

When a property disappears: run `UPDATE sam_properties SET is_active = false WHERE sam_id = ?` in the scraper's reconciliation step.

**How many appear sold:** 0 confirmed (scraper too new, only 2 days of data).

---

## BAM

**Schema:** `asset_state` / `asset_state_code`, `display_property`, `end_date`, `sale_date`, `last_scraped_at`, `first_seen_at`

**Status values:**
- `ทรัพย์พร้อมขาย` / code `1` — Ready for sale (all 6,798 rows)
- `display_property = true` for all rows

**Key fields:**
- `sale_date`: NULL for all 6,798 rows (would be populated when sold — never observed yet)
- `end_date`: NULL for all 6,798 rows
- `price_flag`: 2 (4,479), 3 (2,288), 1 (31) — meaning unclear, not a sold indicator
- `asset_state_code = 1` = available; other codes likely = sold/withdrawn but not yet observed
- All 6,798 entries are `change_type="new"` in `bam_price_history` (no state changes yet)

**Last scrape distribution:**
- 2026-04-05: 3,469 rows (3 province partitions: ปทุมธานี 1,548; นนทบุรี 1,057; สมุทรปราการ 864)
- 2026-04-04: 3,329 rows (กรุงเทพมหานคร 3,226 + 103 detail-only)
- **WARNING:** Scrapes are province-partitioned — staleness check must account for which provinces were scraped in each run

**Sold detection approach:**
BAM only returns available properties in its search API. Sold items disappear. Detection via staleness:

```sql
-- Properties not seen in latest scrape run (likely sold/withdrawn)
SELECT asset_no, project_th, province, sell_price, last_scraped_at
FROM bam_properties
WHERE last_scraped_at < (
    SELECT MAX(last_scraped_at) - INTERVAL '2 hours'
    FROM bam_properties
)
ORDER BY last_scraped_at ASC;
```

For marking: add `is_active` column or use `asset_state_code != 1` if BAM returns non-1 codes for sold items in future.

**How many appear sold:** 0 confirmed yet. Since scrapes are province-partitioned, staleness detection must compare within same province: a BKK property not seen in the BKK re-scrape = likely sold; but a BKK property not seen in a ปทุมธานี run = irrelevant.

---

## JAM

**Schema:** `status_soldout` (boolean), `soldout_date` (timestamptz), `image_sold_out` (text), `update_date`

**This is the best provider for sold detection — explicit field exists.**

**Current counts:**
- `status_soldout = false`: 35,792 (active)
- `status_soldout = true`: 245 (confirmed sold)
- `status_soldout = null`: 2,783 (unknown — likely legacy rows or fetch errors)

**Notes on soldout_date:**
- Only 57 of 245 sold properties have `soldout_date` populated (189 have `status_soldout=true` but NULL date)
- Dates range from 2024-06 to 2026-02, so JAM keeps historical sold items in its API for years
- `update_date` is the reliable timestamp for when status changed

**`image_sold_out`:** populated for 38,171 rows — this appears to be a URL to a "sold out" overlay image, present on ALL rows as a template (not a sold indicator by itself). Cross-tabulated:
- `status_soldout=false` + has_sold_img: 35,451 (image is just a template)
- `status_soldout=true` + has_sold_img: 238 (actual sold)
- `status_soldout=true` + no_sold_img: 7 (sold but no overlay)

**Scraper already tracks sold transitions:** The JAM scraper writes `change_type="sold"` and `change_type="unsold"` events to `jam_price_history`. Currently 0 transition events recorded (all 38,820 are `change_type="new"` from the first scrape run).

**SQL to identify sold:**

```sql
-- Confirmed sold
SELECT asset_id, type_asset_th, province, district, selling, soldout_date, update_date
FROM jam_properties
WHERE status_soldout = true
ORDER BY update_date DESC;

-- Sold in last 30 days
SELECT asset_id, type_asset_th, province, selling, update_date
FROM jam_properties
WHERE status_soldout = true
  AND update_date > NOW() - INTERVAL '30 days'
ORDER BY update_date DESC;
```

**How many appear sold:** 245 confirmed sold, 2,783 status unknown.

---

## KTB

**Schema:** `price_str_dt` (text), `price_end_dt` (text), `last_scraped_at`, `first_seen_at`, `is_speedy`, `is_new_asset`, `is_promotion`, `is_new_pay`

**No explicit sold/active field.**

**Date range of data:** All 2,671 from single scrape on 2026-04-04. All `change_type="new"` in `ktb_price_history`.

**`price_end_dt`:** All 2,671 rows have this populated. Distribution:
- 1 expired (2026-04-04), 19 expire today (2026-04-05)
- Most expire within 2026-2027 range
- Some far-future dates (2056, 2200, 2201) — likely "no expiry" sentinel values
- This is price validity end date, NOT a sold indicator, but expired + missing from next scrape = strong sold signal

**Flag columns (all boolean, none = sold):**
- `is_speedy=0`: 2,173; `is_speedy=1`: 422 (expedited sale)
- `is_new_asset=1`: 76 (newly listed)
- `is_promotion=1`: 2,173

**Sold detection approach:**
Like BAM, KTB's search API only returns available properties. Detection via staleness:

```sql
-- Properties not refreshed in latest scrape (likely sold)
SELECT coll_grp_id, province, amphur, asset_type, price, last_scraped_at
FROM ktb_properties
WHERE last_scraped_at < (
    SELECT MAX(last_scraped_at) - INTERVAL '2 hours'
    FROM ktb_properties
)
ORDER BY last_scraped_at ASC;

-- Properties with expired price_end_dt (no longer listed at current price)
SELECT coll_grp_id, province, asset_type, price, price_end_dt
FROM ktb_properties
WHERE price_end_dt < '2026-04-05'
ORDER BY price_end_dt DESC;
```

**How many appear sold:** 0 confirmed (only 1 scrape run on 2026-04-04).

---

## Recommendations

### Immediate actions

1. **JAM**: Sold detection is already working. Filter `status_soldout = true` in all investment queries.

2. **SAM scraper**: Add reconciliation step — after each full scrape, set `is_active = false` for any `sam_id` not seen in current run. Track `deactivated_at` timestamp.

3. **BAM scraper**: Same reconciliation pattern — compare `asset_no` set from current scrape vs DB, mark missing as inactive.

4. **KTB scraper**: Same reconciliation pattern — compare `coll_grp_id` set.

### Schema additions needed

```sql
-- SAM (already has is_active, just needs scraper to flip it)
ALTER TABLE sam_properties ADD COLUMN IF NOT EXISTS deactivated_at TIMESTAMPTZ;

-- BAM
ALTER TABLE bam_properties ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true;
ALTER TABLE bam_properties ADD COLUMN IF NOT EXISTS deactivated_at TIMESTAMPTZ;

-- KTB
ALTER TABLE ktb_properties ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true;
ALTER TABLE ktb_properties ADD COLUMN IF NOT EXISTS deactivated_at TIMESTAMPTZ;
```

### Staleness threshold per provider
- **SAM**: Mark inactive if `updated_at < NOW() - 3 days` (scrapes daily at 07:40)
- **BAM**: Mark inactive if `last_scraped_at < latest_run - 2 hours` (full province coverage per run)
- **JAM**: Use `status_soldout = true` directly; no staleness needed
- **KTB**: Mark inactive if `last_scraped_at < latest_run - 2 hours`

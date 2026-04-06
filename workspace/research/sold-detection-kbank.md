# KBank NPA — Sold Detection Investigation

**Date:** 2026-04-05  
**Investigator:** subagent  
**DB:** `npa_kb` / tables: `kbank_properties`, `kbank_price_history`

---

## 1. Does KBank scraper track `is_active` or similar flag?

**No `is_active` flag exists.** Current relevant columns:

| Column | Type | Notes |
|--------|------|-------|
| `is_sold_out` | `boolean` | From KBank API field `IsSoldOut`. **155 rows = true** today. KBank flags this before delisting. |
| `is_reserve` | `boolean` | Reserved/under-offer. **268 rows = true** today. |
| `last_scraped_at` | `timestamptz` | Updated on every upsert in `_apply_item_to_prop()`. Key field for disappearance detection. |
| `first_seen_at` | `timestamptz` | Set once on first insert. |

**No `presumed_sold_at`, no `removed_at`, no `is_active` column.**

Key insight: KBank **keeps sold properties in the API** with `is_sold_out = true` rather than removing them silently. This is better than assumed — they telegraph disposition before delisting.

---

## 2. SQL to identify "likely sold" = in DB but not in latest scrape

**Dynamic version** (no hardcoded dates, uses `kbank_scrape_logs` for run anchor):

```sql
-- Properties not seen in the most recent scrape session
-- Uses kbank_scrape_logs.started_at as the run boundary
WITH latest_run AS (
    SELECT started_at FROM kbank_scrape_logs
    ORDER BY started_at DESC LIMIT 1
)
SELECT
    p.property_id,
    p.property_id_format,
    p.property_type_name,
    p.province_name,
    p.amphur_name,
    p.sell_price,
    p.is_sold_out,
    p.is_reserve,
    p.first_seen_at::date,
    p.last_scraped_at::date AS last_seen
FROM kbank_properties p, latest_run lr
WHERE p.last_scraped_at < lr.started_at
ORDER BY p.last_scraped_at;
```

**Simpler fallback** (no scrape_logs dependency, uses 10-min buffer on max ts):

```sql
WITH latest_run AS (
    SELECT max(last_scraped_at) AS run_ts FROM kbank_properties
)
SELECT
    p.property_id,
    p.property_type_name,
    p.province_name,
    p.sell_price,
    p.is_sold_out,
    p.first_seen_at::date,
    p.last_scraped_at::date AS last_seen
FROM kbank_properties p, latest_run lr
WHERE p.last_scraped_at < lr.run_ts - interval '10 minutes'
ORDER BY p.last_scraped_at;
```

The 10-minute buffer accounts for scrape duration across 268 pages at 20 req/60s.

---

## 3. How many properties appear to have disappeared?

**0 today.** Only one scrape run exists (2026-04-04). All 13,361 rows share the same `last_scraped_at`. The stale-detection query returns 0 because there's no prior baseline.

Current best proxy for "sold":
- **155 properties** with `is_sold_out = true` — KBank API already flags these
  - Top types: บ้านเดี่ยว (61), ทาวน์เฮ้าส์ (39), คอนโด (22), อาคารพาณิชย์ (18)
  - Top provinces: ชลบุรี (28), กรุงเทพ (20), เชียงใหม่ (9), ปทุมธานี (8), นนทบุรี (8)
- **268 properties** with `is_reserve = true` — sales pipeline, may convert to sold

After the next daily scrape (06:00 daily per cron), the disappearance query will yield real results.

---

## 4. Add `presumed_sold_at` column + detection logic

### Schema migration

```sql
ALTER TABLE kbank_properties
    ADD COLUMN IF NOT EXISTS presumed_sold_at timestamptz,
    ADD COLUMN IF NOT EXISTS is_active boolean NOT NULL DEFAULT true;

CREATE INDEX IF NOT EXISTS ix_kbank_active ON kbank_properties(is_active);
CREATE INDEX IF NOT EXISTS ix_kbank_presumed_sold ON kbank_properties(presumed_sold_at)
    WHERE presumed_sold_at IS NOT NULL;
```

### Python implementation (add to `database.py`)

```python
from sqlalchemy import update

def mark_presumed_sold(session: Session, scrape_started_at: datetime) -> int:
    """
    After a full scrape, mark properties not seen in this run as presumed sold.
    Also inserts a price_history record for each newly marked property.
    Returns count of newly marked rows.
    """
    # Find properties that disappeared (not updated in this scrape run)
    gone_stmt = select(KbankProperty).where(
        KbankProperty.last_scraped_at < scrape_started_at,
        KbankProperty.presumed_sold_at.is_(None),
        KbankProperty.is_active == True,
    )
    gone = list(session.execute(gone_stmt).scalars())

    if not gone:
        return 0

    now = datetime.now()
    for prop in gone:
        prop.presumed_sold_at = now
        prop.is_active = False
        session.add(KbankPriceHistory(
            property_id=prop.property_id,
            sell_price=prop.sell_price,
            promotion_price=prop.promotion_price,
            adjust_price=prop.adjust_price,
            change_type="presumed_sold",
            scraped_at=now,
        ))

    session.commit()
    return len(gone)
```

### Wire into `scraper.py` — add after the scrape log is committed

```python
# After logging the scrape run:
with Session(engine) as session:
    sold_count = mark_presumed_sold(session, started_at)
    print(f"[scraper] Marked {sold_count} properties as presumed sold")
```

Note: pass `started_at` (the scrape start time), not `finished_at`, so any property that KBank removed mid-scrape is also caught.

---

## 5. Two-signal detection strategy

`is_sold_out` (KBank API) and disappearance detection are complementary:

| Signal | Meaning | When available |
|--------|---------|----------------|
| `is_sold_out = true` | KBank explicitly flagged it | Immediately — KBank sets before delisting |
| `presumed_sold_at IS NOT NULL` | Not returned by any scrape since that date | After 2nd scrape run |
| `is_reserve = true` | Reserved/pending | Now — may revert |

**Combined "sold or gone" query (once schema change applied):**

```sql
SELECT
    property_id,
    property_id_format,
    province_name,
    amphur_name,
    sell_price,
    is_sold_out,
    is_reserve,
    presumed_sold_at::date,
    first_seen_at::date
FROM kbank_properties
WHERE is_sold_out = true
   OR is_active = false
ORDER BY coalesce(presumed_sold_at, last_scraped_at) DESC;
```

---

## Summary

| Question | Answer |
|----------|--------|
| `is_active` or similar? | No — only `is_sold_out` from API. No disappearance tracking yet. |
| Detect by `last_scraped_at`? | Yes — viable now that structure exists, but needs 2+ scrape runs to yield results |
| "Likely sold" SQL? | See dynamic query above (anchors on `kbank_scrape_logs.started_at`) |
| How many disappeared? | **0** today (first run 2026-04-04); **155** already `is_sold_out = true` |
| Can we add `presumed_sold_at`? | Yes — simple `ALTER TABLE` + `mark_presumed_sold()` function in `database.py`, called at end of each scrape |

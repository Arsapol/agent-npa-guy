---
name: npa-alerts
description: NPA property alert system. Scans ALL provider databases (LED, SAM, BAM, JAM, KTB, KBANK) for newly added properties, price drops, best deals, properties near BTS/MRT, and upcoming auctions. Can generate daily reports and run on schedule.
---

# NPA Alerts

Automated alert system for NPA property opportunities across all 6 providers.

## Commands

All commands run from `scripts/` directory:

### New Properties (last N hours) — ALL 6 PROVIDERS
```bash
python alert.py new --hours 24                           # Last 24h across all providers
python alert.py new --hours 48 --source bam              # BAM only, last 48h
python alert.py new --source jam                         # JAM only
python alert.py new --source ktb                         # KTB only
python alert.py new --source kbank                       # KBANK only
python alert.py new --json                               # JSON output
```
**Sources:** `all` (default), `led`, `sam`, `bam`, `jam`, `ktb`, `kbank`

### Price Drops — ALL 5 PROVIDERS WITH HISTORY
```bash
python alert.py drops --hours 24 --min-drop 5            # ≥5% price drops in last 24h
python alert.py drops --hours 168 --min-drop 10 --limit 20  # ≥10% drops in last 7 days
python alert.py drops --json                             # JSON output
```
**Sources:** SAM (sam_price_history), BAM, JAM, KTB, KBANK (all via price_history tables)

### Price Increases — UNUSUAL, WORTH INVESTIGATING
```bash
python alert.py increases --hours 24 --min-increase 5    # ≥5% price increases in last 24h
python alert.py increases --hours 168 --min-increase 10   # ≥10% increases in last 7 days
python alert.py increases --json                         # JSON output
```
**Why it matters:** NPA prices normally only go DOWN. A price increase signals something changed — re-appraisal, encumbrance removed, market shift, or area gentrification. Worth investigating the reason.

### Best Deals (biggest discount vs enforcement officer appraisal)
```bash
python alert.py deals --min-discount 30 --limit 20   # >30% below appraisal
python alert.py deals --max-price 5000000            # Under ฿5M
```

### Near BTS/MRT — ALL 5 PROVIDERS WITH GPS
```bash
python alert.py bts --meters 500 --limit 20           # Within 500m of any station
python alert.py bts --meters 1000 --max-price 3000000  # Under ฿3M within 1km
python alert.py bts --source bam                       # BAM only near transit
```
**Sources:** `all` (default), `sam`, `bam`, `jam`, `ktb`, `kbank`
(LED has no GPS data)

### Upcoming Auctions (LED)
```bash
python alert.py upcoming --days 14            # Next 2 weeks
python alert.py upcoming --days 30 --province "กรุงเทพ"  # Bangkok only
```

### Full Daily Report
```bash
python alert.py report                        # All sections combined
```

## Alert Sections

| Section | Sources | Description |
|---------|---------|-------------|
| New Properties | LED + SAM + BAM + JAM + KTB + KBANK | Properties added in last 24h (by `first_seen_at` / `created_at`) |
| Price Drops | SAM + BAM + JAM + KTB + KBANK | Price drops ≥5% detected via price_history tables |
| Price Increases | SAM + BAM + JAM + KTB + KBANK | Price increases ≥5% — unusual for NPA, investigate why |
| Best Deals | LED | Properties >30% below enforcement officer appraisal |
| Near BTS/MRT | SAM + BAM + JAM + KTB + KBANK | Properties within 500m of transit (has GPS) |
| Upcoming Auctions | LED | Properties with auction dates in next 30 days |

## Data Sources

| Provider | Count | Price Field | GPS | Price History | Notes |
|----------|-------|-------------|-----|---------------|-------|
| **LED** (กรมบังคับคดี) | 17,705 | satang (÷100) | ❌ | — | Court auctions, `created_at` |
| **SAM** (บสส.) | 4,707 | baht | ✅ | ✅ sam_price_history | Best data quality, `first_seen_at` |
| **BAM** (BAY) | 6,798 | baht (discount_price) | ✅ | ✅ bam_price_history | Grade A/B properties, `first_seen_at` |
| **JAM** (IMC) | 38,820 | baht (discount) | ✅ | ✅ jam_price_history | 2nd largest NPA source, `first_seen_at` |
| **KTB** (Krungthai) | 2,671 | baht (price) | ✅ | ✅ ktb_price_history | Biggest discounts, `first_seen_at` |
| **KBANK** | 13,361 | baht (promotion_price) | ✅ | ✅ kbank_price_history | Thin condo inventory, `first_seen_at` |

## Transit Stations

Hardcoded BTS/MRT stations for distance calculations. Covers:
- BTS Sukhumvit Line (สยาม → สมุทรปราการ)
- BTS Silom Line (สยาม → สำโรง + กรุงธนบุรี extension)
- BTS Northern Extension (หมอชิต → สายหยุด)
- MRT Blue Line (สวนจตุจักร → แบริ่ง + ลุมพินี → สามย่าน)
- MRT Purple Line connection (บางซื่อ)

## Notes

- LED properties don't have GPS coordinates — transit alerts exclude LED
- LED `next_auction_date` is stored as varchar (not date) — queries cast to date
- Enforcement officer price (`enforcement_officer_price_satang`) serves as the appraisal baseline for LED deals
- Very high discounts (>90%) are normal for properties that have gone through many auction rounds
- Price drop detection uses `change_type = 'price_drop'` in price_history tables (recorded by scrapers)

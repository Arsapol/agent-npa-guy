---
name: npa-alerts
description: NPA property alert system. Scans LED + SAM databases for newly added properties, best deals, properties near BTS/MRT, and upcoming auctions. Can generate daily reports and run on schedule.
---

# NPA Alerts

Automated alert system for NPA property opportunities from LED and SAM databases.

## Commands

All commands run from `scripts/` directory:

### New Properties (last N hours)
```bash
python alert.py new --hours 24               # Last 24 hours
python alert.py new --hours 48 --source sam  # SAM only, last 48h
python alert.py new --json                   # JSON output
```

### Best Deals (biggest discount vs enforcement officer appraisal)
```bash
python alert.py deals --min-discount 30 --limit 20   # >30% below appraisal
python alert.py deals --max-price 5000000            # Under ฿5M
```

### Near BTS/MRT (SAM properties with GPS)
```bash
python alert.py bts --meters 500 --limit 20   # Within 500m of any station
python alert.py bts --meters 1000 --max-price 3000000  # Under ฿3M within 1km
```

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

| Section | Source | Description |
|---------|--------|-------------|
| New Properties | LED + SAM | Properties added in last 24h |
| Best Deals | LED | Properties >30% below enforcement officer appraisal |
| Near BTS/MRT | SAM | Properties within 500m of transit (has GPS) |
| Upcoming Auctions | LED | Properties with auction dates in next 30 days |

## Data Sources

- **LED (กรมบังคับคดี)**: Court-ordered property auctions. Price in satang. Uses `enforcement_officer_price_satang` as appraisal reference.
- **SAM (บสส.)**: Government asset management direct sales. Price in baht. Has GPS coordinates for distance-to-transit calculations.

## Transit Stations

Hardcoded BTS/MRT stations for distance calculations. Covers:
- BTS Sukhumvit Line (สยาม → สมุทรปราการ)
- BTS Silom Line (สยาม → สำโรง + กรุงธนบุรี extension)
- BTS Northern Extension (หมอชิต → สายหยุด)
- MRT Blue Line (สวนจตุจักร → แบริ่ง + ลุมพินี → สามย่าน)
- MRT Purple Line connection (บางซื่อ)

## Notes

- LED properties don't have GPS coordinates in current schema — transit alerts only work for SAM
- LED `next_auction_date` is stored as varchar (not date) — queries cast to date
- Enforcement officer price (`enforcement_officer_price_satang`) serves as the appraisal baseline for LED deals
- Very high discounts (>90%) are normal for properties that have gone through many auction rounds

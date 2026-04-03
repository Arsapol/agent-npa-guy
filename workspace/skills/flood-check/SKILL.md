---
name: flood-check
description: Flood risk assessment for Thai NPA properties. Hardcoded Bangkok metro flood zones (based on 2011 data + historical patterns) plus provincial risk data. Returns risk level (HIGH/MEDIUM/LOW) with recommendations. Use before recommending any property.
---

# Flood Risk Check

## Overview

Assesses flood risk using hardcoded zone data for Bangkok metro area and provincial risk levels for other regions. Based on historical flood data (2011 floods, recurring patterns) and geographic factors (elevation, canal proximity, coastal subsidence).

## Usage

### By Coordinates
```bash
python scripts/flood_check.py --lat 13.95 --lon 100.62
python scripts/flood_check.py --lat 13.73 --lon 100.56
```

### With Province Fallback
```bash
python scripts/flood_check.py --lat 7.88 --lon 98.38 --province "ภูเก็ต"
```

### JSON Output
```bash
python scripts/flood_check.py --lat 13.88 --lon 100.42 --json
```

## Risk Levels

| Level | Meaning | NPA Impact |
|-------|---------|------------|
| 🔴 HIGH | Historically flooded, structural risk | Deal-breaker for ground floor. 30%+ discount needed. |
| 🟡 MEDIUM | Localized risk, varies by micro-location | Check specifics. 10-15% ground floor discount. |
| 🟢 LOW | Well-drained, elevated, good infrastructure | Not a major concern. Standard due diligence. |
| ⚪ UNKNOWN | No data for this location | Manual research required. |

## Covered Zones (Bangkok Metro)

HIGH risk: Rangsit, Bang Bua Thong, Nonthaburi West, Lat Krabang-Min Buri, Samut Prakan coast, Don Mueang-Lak Si

MEDIUM risk: Bang Khen, Bang Kapi, Pathum Thani, Bang Phlat-Taling Chan, Samut Prakan North

LOW risk: Sukhumvit-Silom core, Sathorn, Ari-Phahon Yothin, Thong Lo-Ekkamai

## Provinces Covered

ภูเก็ต, เชียงใหม่, กระบี่, สงขลา, สุราษฎร์ธานี, แพร่, ตรัง, พัทลุง, นนทบุรี

## Limitations

- Zone data is approximate (bounding boxes, not precise flood maps)
- Historical data primarily from 2011 floods + recurring patterns
- Micro-location matters: a property 50m from a canal is different from 500m
- For UNKNOWN areas, use web search: "[area] น้ำท่วม ประวัติ"
- Government flood maps: flood.gistda.or.th

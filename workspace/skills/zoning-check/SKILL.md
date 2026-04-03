---
name: zoning-check
description: Thai city planning (ผังเมือง) and building control checker. Looks up zone color codes, FAR/OSR limits, max height/floors, permitted uses, airport restrictions, EIA thresholds, and road-width height rules. Based on Bangkok Plan พ.ศ. 2556 (active as of April 2026). Always verify with official GIS at plludds.dpt.go.th/landuse/.
---

# Zoning & Building Control Check

## Overview

Checks Thai zoning regulations for NPA property assessment. Based on the **Bangkok Comprehensive Plan พ.ศ. 2556** (3rd revision), which remains the legally active plan as of April 2026. The 4th revision draft is blocked by a Consumer Council lawsuit (filed Feb 2026).

**IMPORTANT**: This skill provides approximate zone lookups. Always verify with the official GIS tool:
- **All provinces**: https://plludds.dpt.go.th/landuse/
- **Bangkok**: https://cityplangis.bangkok.go.th
- **Mobile apps**: "Check ผังเมือง กทม" or "DPT Landuse Plan"

## Usage

### By Coordinates
```bash
python scripts/zoning.py --lat 13.7369 --lon 100.5606
python scripts/zoning.py --lat 13.7454 --lon 100.5341 --type "คอนโดสูง"
python scripts/zoning.py --lat 13.7369 --lon 100.5606 --road-width 12
```

### Look Up Zone Code
```bash
python scripts/zoning.py --lat 0 --lon 0 --zone ย.7
python scripts/zoning.py --lat 0 --lon 0 --zone พ.4
```

## Bangkok Zone System (พ.ศ. 2556)

### Residential (ย. = ที่อยู่อาศัย)

| Zone | Color | Density | FAR | OSR | Height |
|------|-------|---------|-----|-----|--------|
| ย.1-ย.2 | Yellow | Very low | 1.5 | 20% | 12m / 3 floors |
| ย.3-ย.4 | Yellow | Low | 2.5 | 12.5% | 23m / 8 floors |
| ย.5 | Orange | Medium-low | 3.5 | 10% | FAR-controlled |
| ย.6 | Orange | Medium | 4.0 | 7.5% | FAR-controlled |
| ย.7-ย.8 | Orange | Medium | 5.0 | 6.0% | FAR-controlled |
| ย.9 | Brown | High | 7.0 | 4.5% | FAR-controlled |
| ย.10 | Brown | High | 8.0 | 4.0% | FAR-controlled |

### Commercial (พ. = พาณิชยกรรม)

| Zone | FAR | OSR | Description |
|------|-----|-----|-------------|
| พ.1-พ.2 | 6.0 | 5.0% | Neighborhood/district commercial |
| พ.3, พ.5 | 7.0 | 4.5% | Major commercial areas |
| พ.4 | 8.0 | 4.0% | CBD (Siam, Silom, Sathorn, Asok) |

### Other

| Zone | FAR | Height | Use |
|------|-----|--------|-----|
| อ.1 | 2.0 | 23m | Light industrial |
| อ.2 | 1.5 | 23m | Heavy industrial (NO residential) |
| ก.1 | 0.5 | 9m / 2F | Agricultural conservation |
| ก.2 | 1.0 | 12m / 3F | Rural/agricultural |

## Building Height Rules (พ.ร.บ. ควบคุมอาคาร)

1. **Road width rule**: Max height = **2x road width** (กฎกระทรวง ฉบับที่ 55)
2. **Road <10m**: Max building height = **23m** regardless
3. **23m threshold**: Buildings >23m = "อาคารสูง" (high-rise) — stricter fire, structural, elevator requirements
4. **Setbacks**: ≤9m height: 2m from boundary | 9-23m: 3m | >23m: 6m all sides

## Airport Height Restrictions

| Airport | Inner (4km) | Mid (8km) | Outer (16km) |
|---------|-------------|-----------|--------------|
| Suvarnabhumi | 45m | 60m | 150m |
| Don Mueang | 45m (4.61km) | 60m | 150m |

Must apply to **CAAT** for construction within safety zones.

## EIA Thresholds

| Type | Trigger |
|------|---------|
| Condo | **≥80 units** OR **≥4,000 sqm** usable area |
| Housing | **≥500 plots** OR **≥100 rai** |

EIA is triggered by **unit count/area, NOT height**. A 10-floor building with 80+ units needs EIA. A 30-floor building with 79 units does not (but needs high-rise permits).

## FAR Bonus (5-20% additional)

Available for: public open space, low-income housing, extra parking near transit, water retention.

## Official Verification Tools

| Tool | URL | Coverage |
|------|-----|----------|
| DPT GIS | plludds.dpt.go.th/landuse/ | All provinces |
| Bangkok GIS | cityplangis.bangkok.go.th | Bangkok only |
| App | "Check ผังเมือง กทม" | Bangkok (iOS/Android) |
| App | "DPT Landuse Plan" | All provinces |
| ASA data | download.asa.or.th/03media/04law/cpa/BMA_LandUse_2556.xls | Bangkok (definitive FAR/OSR) |
| Longdo Map | map.longdo.com (city plan layer) | All provinces |
| LandsMaps | landsmaps.dol.go.th | All provinces |

## Sources

- กฎกระทรวงให้ใช้บังคับผังเมืองรวมกรุงเทพมหานคร พ.ศ. 2556
- พ.ร.บ. ควบคุมอาคาร พ.ศ. 2522 + กฎกระทรวง ฉบับที่ 55 พ.ศ. 2543
- พ.ร.บ. การเดินอากาศ (aviation safety zones)
- ASA (asa.or.th/laws-and-regulations/cpa/)

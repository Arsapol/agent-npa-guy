---
name: location-intel
description: Location intelligence for Thai NPA properties. Finds nearby BTS/MRT stations, schools, hospitals, and shopping malls with distance calculations. Uses hardcoded Bangkok transit data + Overpass API (OpenStreetMap) for amenities. No API key needed.
---

# Location Intelligence

## Overview

Finds nearby amenities and transit for any coordinates in Thailand. BTS/MRT/ARL stations use hardcoded data (more reliable than OSM for Bangkok). Schools, hospitals, and shopping use the free Overpass API (OpenStreetMap).

## Usage

### Full Report
```bash
python scripts/location.py --lat 13.7369 --lon 100.5606
python scripts/location.py --lat 13.8027 --lon 100.5536 --radius 3000
```

### Transit Only (fast, no API call)
```bash
python scripts/location.py --lat 13.7369 --lon 100.5606 --transit-only
```

### JSON Output
```bash
python scripts/location.py --lat 13.7248 --lon 100.5783 --json
```

## Parameters

| Param | Description |
|-------|-------------|
| `--lat` | Latitude (required) |
| `--lon` | Longitude (required) |
| `--radius` | Search radius in meters (default: 2000) |
| `--transit-only` | Only show BTS/MRT/ARL stations (no Overpass API call) |
| `--json` | Output as JSON |

## Transit Rating

| Rating | Distance | Impact |
|--------|----------|--------|
| PREMIUM | ≤500m | 20-30% price premium |
| GOOD | 500m-1km | 10-20% premium |
| MODERATE | 1-2km | Neutral |
| FAR | >2km | Discount factor |

## Data Sources

- **BTS/MRT/ARL**: Hardcoded 65+ stations with coordinates (Sukhumvit, Silom, Blue Line, Airport Rail Link)
- **Schools**: Overpass API — schools, kindergartens, universities
- **Hospitals**: Overpass API — hospitals, clinics
- **Shopping**: Overpass API — malls, supermarkets, department stores

## Getting Coordinates

For a property address, use web search to find coordinates:
- Search: "[address] พิกัด" or "[address] coordinates"
- Or use Google Maps: right-click → "What's here?"

## Limitations

- Transit data covers Bangkok metro area only (BTS, MRT Blue, ARL)
- Provincial transit (tram, local rail) not included
- Overpass API has rate limits — avoid rapid repeated queries
- OSM data quality varies by area (Bangkok is well-covered)

## Infrastructure Skepticism Rule

When mentioning "future upside" from planned transit/infrastructure in property analysis:
1. Check `scripts/infrastructure_status.md` for status (OPERATIONAL / FUNDED / PLANNED)
2. **Only OPERATIONAL and FUNDED+UNDER-CONSTRUCTION** count as upside
3. **PLANNED = zero value** — do NOT use as a value driver (e.g. Chiang Mai Light Rail, Phuket Tram)
4. If you catch yourself saying "planned" or "proposed" in an analysis, remove it or explicitly mark it as speculative with zero current value

# Road Proximity — Setup Guide

Complete setup instructions for a fresh machine.

## Prerequisites

- PostgreSQL (tested with v18)
- Homebrew (macOS)

## Step 1: Install system dependencies

```bash
brew install postgis osrm-backend
```

- `postgis` — spatial extension for PostgreSQL (~86MB)
- `osrm-backend` — routing engine binaries: `osrm-extract`, `osrm-partition`, `osrm-customize`, `osrm-routed`

## Step 2: Enable PostgreSQL extensions

```bash
psql postgresql://arsapolm@localhost:5432/npa_kb -c "CREATE EXTENSION IF NOT EXISTS postgis;"
psql postgresql://arsapolm@localhost:5432/npa_kb -c "CREATE EXTENSION IF NOT EXISTS pg_trgm;"
```

- `postgis` — spatial queries (ST_Distance, ST_DWithin, ST_ClosestPoint)
- `pg_trgm` — trigram indexes for fuzzy road name search

## Step 3: Download OSM data + import roads into PostGIS

```bash
cd workspace/skills/road-proximity
bash scripts/import_roads.sh
```

This does:
1. Downloads `thailand-latest.osm.pbf` from Geofabrik (~300MB) into `data/`
2. Enables PostGIS extension
3. Runs `osm2pgsql` with `scripts/roads.lua` Lua style (filters only roads, skips footways/cycleways)
4. Creates spatial + text indexes
5. Prints road count by type

**Time**: ~2 min download + ~1 min import
**Disk**: ~300MB for .pbf file

## Step 4: Pre-process OSRM routing data

```bash
bash scripts/osrm_setup.sh
```

This does:
1. `osrm-extract` — extracts road network from .pbf using car.lua profile
2. `osrm-partition` — partitions graph for MLD routing algorithm
3. `osrm-customize` — computes edge weights

**Time**: ~3-5 min
**Disk**: ~3.5GB for OSRM processed files in `data/`
**RAM peak**: ~6GB during extract

## Step 5: Start OSRM routing server

```bash
bash scripts/osrm_server.sh start
```

- Runs on port **5001** (5000 is taken by macOS AirPlay)
- Uses ~2GB RAM while running
- Override port: `OSRM_PORT=5002 bash scripts/osrm_server.sh start`

## Verify setup

```bash
# Test PostGIS (straight-line distance)
python scripts/query.py nearest --lat 13.75 --lon 100.50 --main-only

# Test OSRM (driving distance/time)
python scripts/query.py route --lat 13.75 --lon 100.50

# Full summary (both)
python scripts/query.py summary --lat 13.75 --lon 100.50
```

## Data refresh

```bash
# Re-download + re-import roads (if OSM data updated)
bash scripts/import_roads.sh

# Re-process OSRM (only needed after roads re-import)
bash scripts/osrm_server.sh stop
bash scripts/osrm_setup.sh
bash scripts/osrm_server.sh start
```

## Gotchas

| Issue | Solution |
|-------|----------|
| `postgis is not available` | `brew install postgis`, then re-run `CREATE EXTENSION` |
| `osrm-extract: command not found` | `brew install osrm-backend` |
| Port 5000 in use (macOS AirPlay) | Default is already 5001; or set `OSRM_PORT=5002` |
| SRID mismatch errors in PostGIS | Always use `ST_SetSRID(ST_MakePoint(lon, lat), 4326)` — the `way` column is SRID 4326 |
| `car.lua profile not found` | Check `ls /opt/homebrew/share/osrm/profiles/` or `/opt/homebrew/opt/osrm-backend/share/osrm/profiles/` |
| OSRM uses too much RAM | Stop server when not needed: `bash scripts/osrm_server.sh stop` |

## File Structure

```
road-proximity/
├── SKILL.md              # Skill reference (usage, API, schema)
├── SETUP.md              # This file
├── .gitignore            # Excludes data/ and .omc/
├── data/                 # NOT in git (~3.9GB)
│   ├── thailand-latest.osm.pbf       # Geofabrik download
│   ├── thailand-latest.osrm.*        # OSRM processed files (~20 files)
│   └── osrm.pid                      # Server PID file
└── scripts/
    ├── roads.lua          # osm2pgsql Lua style (filters only roads)
    ├── import_roads.sh    # Download + PostGIS import
    ├── osrm_setup.sh      # OSRM pre-processing (extract/partition/customize)
    ├── osrm_server.sh     # OSRM server start/stop/status
    └── query.py           # Python query module + CLI
```

## Python dependencies

All already available in project environment:
- `httpx` — OSRM HTTP API calls
- `pydantic` — result models
- `sqlalchemy` + `psycopg2` — PostGIS queries

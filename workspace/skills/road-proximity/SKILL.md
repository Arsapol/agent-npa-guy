# Road Proximity Skill

Find nearest roads and calculate actual driving distance/time to any GPS coordinate using OpenStreetMap data stored locally in PostGIS + OSRM routing engine.

## Data Source

- **Provider**: OpenStreetMap via [Geofabrik Thailand extract](https://download.geofabrik.de/asia/thailand.html) (~300MB .osm.pbf)
- **Update frequency**: Weekly (roads rarely change)
- **Storage**: PostGIS `osm_roads` table in `npa_kb` (~2.8M road segments)
- **Routing**: OSRM (Open Source Routing Machine) for actual driving distance/time

## Setup from Scratch

### Prerequisites

- PostgreSQL (tested with v18)
- Homebrew (macOS)

### Step 1: Install system dependencies

```bash
brew install postgis osrm-backend
```

- `postgis` — spatial extension for PostgreSQL (~86MB)
- `osrm-backend` — routing engine binaries: `osrm-extract`, `osrm-partition`, `osrm-customize`, `osrm-routed`

### Step 2: Enable PostgreSQL extensions

```bash
psql postgresql://arsapolm@localhost:5432/npa_kb -c "CREATE EXTENSION IF NOT EXISTS postgis;"
psql postgresql://arsapolm@localhost:5432/npa_kb -c "CREATE EXTENSION IF NOT EXISTS pg_trgm;"
```

- `postgis` — spatial queries (ST_Distance, ST_DWithin, ST_ClosestPoint)
- `pg_trgm` — trigram indexes for fuzzy road name search

### Step 3: Download OSM data + import roads into PostGIS

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

### Step 4: Pre-process OSRM routing data

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

### Step 5: Start OSRM routing server

```bash
bash scripts/osrm_server.sh start
```

- Runs on port **5001** (5000 is taken by macOS AirPlay)
- Uses ~2GB RAM while running
- Override port: `OSRM_PORT=5002 bash scripts/osrm_server.sh start`

### Verify setup

```bash
# Test PostGIS (straight-line distance)
python scripts/query.py nearest --lat 13.75 --lon 100.50 --main-only

# Test OSRM (driving distance/time)
python scripts/query.py route --lat 13.75 --lon 100.50

# Full summary (both)
python scripts/query.py summary --lat 13.75 --lon 100.50
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

## Usage

### CLI commands

```bash
# Straight-line proximity (PostGIS only — no OSRM needed)
python scripts/query.py nearest --lat 13.73 --lon 100.56 --radius 2000 --limit 5
python scripts/query.py nearest --lat 13.73 --lon 100.56 --main-only
python scripts/query.py distance --lat 13.73 --lon 100.56 --road-type primary

# Full summary with access rating
python scripts/query.py summary --lat 13.73 --lon 100.56

# Actual driving route (requires OSRM running)
python scripts/query.py route --lat 13.73 --lon 100.56
python scripts/query.py route-between --from-lat 13.84 --from-lon 100.57 --to-lat 13.75 --to-lon 100.50

# OSRM server management
bash scripts/osrm_server.sh start
bash scripts/osrm_server.sh stop
bash scripts/osrm_server.sh status
```

### Python API

```python
from scripts.query import (
    find_nearest_roads,
    find_nearest_main_road,
    road_summary,
    route_to_main_road,
    route_between,
)

# Straight-line
roads = find_nearest_roads(lat=13.73, lon=100.56, radius_m=2000, limit=5)

# Full summary (includes routing if OSRM running)
summary = road_summary(lat=13.73, lon=100.56)
# → access_rating: "GOOD", nearest_main_road: ถนนงามวงศ์วาน (387m straight-line)
# → route_to_main_road: 3.77km, 6.6 min driving

# Driving route
route = route_to_main_road(lat=13.84, lon=100.57)
# → distance_km: 3.77, duration_min: 6.6, road_name: ถนนงามวงศ์วาน
```

### Access rating logic

| Rating | Condition |
|--------|-----------|
| EXCELLENT | Main road within 200m straight-line |
| GOOD | Main road within 800m |
| FAIR | Main road within 2000m, or no main road but any road nearby |
| POOR | Nearest road > 500m, or main road > 2000m |
| NO_ROAD_ACCESS | No road found within radius |

## Data refresh

```bash
# Re-download + re-import roads (if OSM data updated)
bash scripts/import_roads.sh

# Re-process OSRM (only needed after roads re-import)
bash scripts/osrm_server.sh stop
bash scripts/osrm_setup.sh
bash scripts/osrm_server.sh start
```

## Road Types (highway tag)

| Type | Description | Count (~) |
|------|-------------|-----------|
| motorway | ทางด่วน / มอเตอร์เวย์ | 2,600 |
| trunk | ถนนสายหลัก (e.g. พหลโยธิน, สุขุมวิท) | 18,000 |
| primary | ถนนสายรอง | 27,000 |
| secondary | ถนนในเมือง สายสำคัญ | 28,000 |
| tertiary | ถนนในเมือง สายย่อย | 80,000 |
| residential | ถนนในหมู่บ้าน / ซอย | 350,000 |
| service | ทางเข้า / ทางภายใน | 210,000 |
| unclassified | ถนนไม่จัดประเภท | 39,000 |

`main road` = motorway, trunk, primary, secondary

## Schema

```sql
-- Created by osm2pgsql with scripts/roads.lua
CREATE TABLE osm_roads (
    id BIGSERIAL PRIMARY KEY,
    osm_id BIGINT,
    name TEXT,
    name_th TEXT,
    highway TEXT NOT NULL,
    ref TEXT,          -- road number e.g. "302"
    lanes TEXT,
    surface TEXT,
    way GEOMETRY(LineString, 4326)
);

-- Indexes
CREATE INDEX idx_osm_roads_way ON osm_roads USING GIST (way);
CREATE INDEX idx_osm_roads_highway ON osm_roads (highway);
CREATE INDEX idx_osm_roads_name ON osm_roads USING GIN (name gin_trgm_ops);
CREATE INDEX idx_osm_roads_name_th ON osm_roads USING GIN (name_th gin_trgm_ops);
```

## File Structure

```
road-proximity/
├── SKILL.md              # This file
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

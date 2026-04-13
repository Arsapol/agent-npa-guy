# Road Proximity Skill

Find nearest roads and calculate actual driving distance/time to any GPS coordinate using OpenStreetMap data stored locally in PostGIS + OSRM routing engine.

**Setup**: See [SETUP.md](SETUP.md) for fresh machine installation.

## Data Source

- **Provider**: OpenStreetMap via [Geofabrik Thailand extract](https://download.geofabrik.de/asia/thailand.html) (~300MB .osm.pbf)
- **Update frequency**: Weekly (roads rarely change)
- **Storage**: PostGIS `osm_roads` table in `npa_kb` (~2.8M road segments)
- **Routing**: OSRM (Open Source Routing Machine) for actual driving distance/time

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

CREATE INDEX idx_osm_roads_way ON osm_roads USING GIST (way);
CREATE INDEX idx_osm_roads_highway ON osm_roads (highway);
CREATE INDEX idx_osm_roads_name ON osm_roads USING GIN (name gin_trgm_ops);
CREATE INDEX idx_osm_roads_name_th ON osm_roads USING GIN (name_th gin_trgm_ops);
```

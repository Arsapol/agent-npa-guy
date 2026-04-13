# Road Proximity Skill

Find nearest roads to any GPS coordinate using OpenStreetMap data stored locally in PostGIS.

## Data Source

- **Provider**: OpenStreetMap via Geofabrik Thailand extract
- **Update frequency**: Weekly (cron)
- **Storage**: PostGIS `osm_roads` table in `npa_kb`

## Usage

### Query nearest roads
```bash
python scripts/query.py nearest --lat 13.73 --lon 100.56 --radius 2000 --limit 5
```

### Query distance to specific road type
```bash
python scripts/query.py distance --lat 13.73 --lon 100.56 --road-type primary
```

### Refresh data
```bash
bash scripts/import_roads.sh
```

## Road Types (highway tag)

| Type | Description |
|------|-------------|
| motorway | ทางด่วน / มอเตอร์เวย์ |
| trunk | ถนนสายหลัก (e.g. พหลโยธิน, สุขุมวิท) |
| primary | ถนนสายรอง |
| secondary | ถนนในเมือง สายสำคัญ |
| tertiary | ถนนในเมือง สายย่อย |
| residential | ถนนในหมู่บ้าน / ซอย |

## Schema

```sql
CREATE TABLE osm_roads (
    id BIGSERIAL PRIMARY KEY,
    osm_id BIGINT,
    name TEXT,
    name_th TEXT,
    highway TEXT,
    ref TEXT,          -- road number e.g. "3"
    lanes TEXT,
    surface TEXT,
    way GEOMETRY(LineString, 4326)
);
```

-- osm2pgsql Lua style: import only roads into osm_roads table

local roads = osm2pgsql.define_way_table('osm_roads', {
    { column = 'osm_id', type = 'bigint' },
    { column = 'name', type = 'text' },
    { column = 'name_th', type = 'text' },
    { column = 'highway', type = 'text', not_null = true },
    { column = 'ref', type = 'text' },
    { column = 'lanes', type = 'text' },
    { column = 'surface', type = 'text' },
    { column = 'way', type = 'linestring', projection = 4326 },
})

-- Only process ways with a highway tag
function osm2pgsql.process_way(object)
    local highway = object.tags.highway
    if not highway then
        return
    end

    -- Keep only actual roads, skip footways/cycleways/paths
    local dominated = {
        footway = true,
        cycleway = true,
        path = true,
        steps = true,
        pedestrian = true,
        bridleway = true,
        construction = true,
        proposed = true,
        raceway = true,
    }

    if dominated[highway] then
        return
    end

    roads:insert({
        osm_id = object.id,
        name = object.tags.name or object.tags['name:en'],
        name_th = object.tags['name:th'] or object.tags.name,
        highway = highway,
        ref = object.tags.ref,
        lanes = object.tags.lanes,
        surface = object.tags.surface,
        way = object:as_linestring(),
    })
end

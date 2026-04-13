"""Road proximity queries against PostGIS osm_roads table + OSRM routing."""

import argparse
import json
import os
import sys

import httpx
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, text

DB_URL = os.getenv("DATABASE_URL", "postgresql://arsapolm@localhost:5432/npa_kb")
OSRM_URL = os.getenv("OSRM_URL", "http://localhost:5001")

MAIN_ROAD_TYPES = ("motorway", "trunk", "primary", "secondary")
ALL_ROAD_TYPES = ("motorway", "trunk", "primary", "secondary", "tertiary", "residential",
                  "unclassified", "service", "living_street", "motorway_link", "trunk_link",
                  "primary_link", "secondary_link", "tertiary_link")

HIGHWAY_PRIORITY = {t: i for i, t in enumerate(ALL_ROAD_TYPES)}


class NearestRoad(BaseModel):
    """Result of a nearest-road query."""
    osm_id: int
    name: str | None = None
    name_th: str | None = None
    highway: str
    ref: str | None = None
    distance_m: float = Field(description="Straight-line distance in meters")
    lanes: str | None = None
    surface: str | None = None


class RouteResult(BaseModel):
    """Result of an OSRM routing query."""
    from_lat: float
    from_lon: float
    to_lat: float
    to_lon: float
    distance_m: float = Field(description="Actual driving distance in meters")
    duration_s: float = Field(description="Estimated driving time in seconds")
    distance_km: float = Field(description="Driving distance in km")
    duration_min: float = Field(description="Driving time in minutes")
    road_name: str | None = None
    road_type: str | None = None


def _engine():
    return create_engine(DB_URL)


def _osrm_available() -> bool:
    """Check if OSRM server is running."""
    try:
        resp = httpx.get(f"{OSRM_URL}/nearest/v1/driving/100.5,13.7", timeout=2)
        return resp.status_code == 200
    except (httpx.ConnectError, httpx.TimeoutException):
        return False


def _osrm_route(from_lat: float, from_lon: float, to_lat: float, to_lon: float) -> dict | None:
    """Get driving route between two points via OSRM."""
    url = f"{OSRM_URL}/route/v1/driving/{from_lon},{from_lat};{to_lon},{to_lat}"
    try:
        resp = httpx.get(url, params={"overview": "false"}, timeout=10)
        data = resp.json()
        if data.get("code") != "Ok" or not data.get("routes"):
            return None
        return data["routes"][0]
    except (httpx.ConnectError, httpx.TimeoutException):
        return None


def _nearest_point_on_road(lat: float, lon: float, osm_id: int) -> tuple[float, float] | None:
    """Get closest point on a specific road segment to snap routing target."""
    query = text("""
        SELECT
            ST_Y(ST_ClosestPoint(way, ST_SetSRID(ST_MakePoint(:lon, :lat), 4326))) AS snap_lat,
            ST_X(ST_ClosestPoint(way, ST_SetSRID(ST_MakePoint(:lon, :lat), 4326))) AS snap_lon
        FROM osm_roads
        WHERE osm_id = :osm_id
        LIMIT 1
    """)
    with _engine().connect() as conn:
        row = conn.execute(query, {"lat": lat, "lon": lon, "osm_id": osm_id}).mappings().first()
    if not row:
        return None
    return (row["snap_lat"], row["snap_lon"])


def route_to_main_road(lat: float, lon: float) -> RouteResult | None:
    """Get actual driving route from a GPS point to the nearest main road."""
    main_road = find_nearest_main_road(lat, lon)
    if not main_road:
        return None

    snap = _nearest_point_on_road(lat, lon, main_road.osm_id)
    if not snap:
        return None

    route = _osrm_route(lat, lon, snap[0], snap[1])
    if not route:
        return None

    return RouteResult(
        from_lat=lat,
        from_lon=lon,
        to_lat=snap[0],
        to_lon=snap[1],
        distance_m=route["distance"],
        duration_s=route["duration"],
        distance_km=round(route["distance"] / 1000, 2),
        duration_min=round(route["duration"] / 60, 1),
        road_name=main_road.name_th or main_road.name,
        road_type=main_road.highway,
    )


def route_between(from_lat: float, from_lon: float, to_lat: float, to_lon: float) -> RouteResult | None:
    """Get driving route between any two GPS points."""
    route = _osrm_route(from_lat, from_lon, to_lat, to_lon)
    if not route:
        return None

    return RouteResult(
        from_lat=from_lat,
        from_lon=from_lon,
        to_lat=to_lat,
        to_lon=to_lon,
        distance_m=route["distance"],
        duration_s=route["duration"],
        distance_km=round(route["distance"] / 1000, 2),
        duration_min=round(route["duration"] / 60, 1),
    )


def find_nearest_roads(
    lat: float,
    lon: float,
    radius_m: float = 2000,
    limit: int = 5,
    road_types: tuple[str, ...] | None = None,
) -> list[NearestRoad]:
    """Find nearest roads to a GPS point within radius."""
    types = road_types or ALL_ROAD_TYPES

    query = text("""
        SELECT
            osm_id,
            name,
            name_th,
            highway,
            ref,
            lanes,
            surface,
            ST_Distance(way::geography, ST_MakePoint(:lon, :lat)::geography) AS distance_m
        FROM osm_roads
        WHERE highway = ANY(:types)
          AND ST_DWithin(way::geography, ST_MakePoint(:lon, :lat)::geography, :radius)
        ORDER BY distance_m
        LIMIT :limit
    """)

    with _engine().connect() as conn:
        rows = conn.execute(query, {
            "lat": lat, "lon": lon,
            "radius": radius_m, "limit": limit,
            "types": list(types),
        }).mappings().all()

    return [NearestRoad(**dict(r)) for r in rows]


def find_nearest_main_road(lat: float, lon: float, radius_m: float = 5000) -> NearestRoad | None:
    """Find the single nearest main road (motorway/trunk/primary/secondary)."""
    results = find_nearest_roads(lat, lon, radius_m=radius_m, limit=1, road_types=MAIN_ROAD_TYPES)
    return results[0] if results else None


def distance_to_road_type(lat: float, lon: float, road_type: str, radius_m: float = 10000) -> NearestRoad | None:
    """Find nearest road of a specific type."""
    results = find_nearest_roads(lat, lon, radius_m=radius_m, limit=1, road_types=(road_type,))
    return results[0] if results else None


def road_summary(lat: float, lon: float, radius_m: float = 2000) -> dict:
    """Get a summary of road access for a GPS point — useful for NPA analysis."""
    all_nearby = find_nearest_roads(lat, lon, radius_m=radius_m, limit=20)
    main_road = find_nearest_main_road(lat, lon)

    # Deduplicate by name, keep closest per name
    seen: dict[str, NearestRoad] = {}
    for r in all_nearby:
        key = r.name_th or r.name or f"unnamed_{r.osm_id}"
        if key not in seen:
            seen[key] = r

    nearest = all_nearby[0] if all_nearby else None

    result = {
        "nearest_road": nearest.model_dump() if nearest else None,
        "nearest_main_road": main_road.model_dump() if main_road else None,
        "roads_within_radius": len(all_nearby),
        "unique_named_roads": len([r for r in seen.values() if r.name or r.name_th]),
        "access_rating": _rate_access(nearest, main_road),
        "nearby_roads": [r.model_dump() for r in list(seen.values())[:10]],
    }

    # Add routing data if OSRM is available
    if _osrm_available():
        route = route_to_main_road(lat, lon)
        result["route_to_main_road"] = route.model_dump() if route else None
    else:
        result["route_to_main_road"] = None
        result["osrm_note"] = "OSRM not running — start with: bash scripts/osrm_server.sh start"

    return result


def _rate_access(nearest: NearestRoad | None, main_road: NearestRoad | None) -> str:
    """Rate road access quality for NPA property evaluation."""
    if not nearest:
        return "NO_ROAD_ACCESS"
    if nearest.distance_m > 500:
        return "POOR"
    if not main_road:
        return "FAIR"
    if main_road.distance_m <= 200:
        return "EXCELLENT"
    if main_road.distance_m <= 800:
        return "GOOD"
    if main_road.distance_m <= 2000:
        return "FAIR"
    return "POOR"


def main():
    parser = argparse.ArgumentParser(description="Road proximity queries")
    sub = parser.add_subparsers(dest="command", required=True)

    # nearest
    p_near = sub.add_parser("nearest", help="Find nearest roads")
    p_near.add_argument("--lat", type=float, required=True)
    p_near.add_argument("--lon", type=float, required=True)
    p_near.add_argument("--radius", type=float, default=2000)
    p_near.add_argument("--limit", type=int, default=5)
    p_near.add_argument("--main-only", action="store_true", help="Only main roads")

    # distance
    p_dist = sub.add_parser("distance", help="Distance to a road type")
    p_dist.add_argument("--lat", type=float, required=True)
    p_dist.add_argument("--lon", type=float, required=True)
    p_dist.add_argument("--road-type", required=True, choices=ALL_ROAD_TYPES)

    # summary
    p_sum = sub.add_parser("summary", help="Road access summary for NPA analysis")
    p_sum.add_argument("--lat", type=float, required=True)
    p_sum.add_argument("--lon", type=float, required=True)
    p_sum.add_argument("--radius", type=float, default=2000)

    # route — driving route to main road
    p_route = sub.add_parser("route", help="Driving route to nearest main road (requires OSRM)")
    p_route.add_argument("--lat", type=float, required=True)
    p_route.add_argument("--lon", type=float, required=True)

    # route-between — driving route between two points
    p_rb = sub.add_parser("route-between", help="Driving route between two points (requires OSRM)")
    p_rb.add_argument("--from-lat", type=float, required=True)
    p_rb.add_argument("--from-lon", type=float, required=True)
    p_rb.add_argument("--to-lat", type=float, required=True)
    p_rb.add_argument("--to-lon", type=float, required=True)

    args = parser.parse_args()

    if args.command == "nearest":
        types = MAIN_ROAD_TYPES if args.main_only else None
        results = find_nearest_roads(args.lat, args.lon, args.radius, args.limit, types)
        output = [r.model_dump() for r in results]
    elif args.command == "distance":
        result = distance_to_road_type(args.lat, args.lon, args.road_type)
        output = result.model_dump() if result else {"error": "No road found in range"}
    elif args.command == "summary":
        output = road_summary(args.lat, args.lon, args.radius)
    elif args.command == "route":
        if not _osrm_available():
            output = {"error": "OSRM not running. Start with: bash scripts/osrm_server.sh start"}
        else:
            result = route_to_main_road(args.lat, args.lon)
            output = result.model_dump() if result else {"error": "No route found"}
    elif args.command == "route-between":
        if not _osrm_available():
            output = {"error": "OSRM not running. Start with: bash scripts/osrm_server.sh start"}
        else:
            result = route_between(args.from_lat, args.from_lon, args.to_lat, args.to_lon)
            output = result.model_dump() if result else {"error": "No route found"}

    print(json.dumps(output, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()

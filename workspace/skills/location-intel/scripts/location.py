#!/usr/bin/env python3
"""Location intelligence for Thai NPA properties.

Uses Overpass API (OpenStreetMap) to find nearby amenities:
BTS/MRT stations, schools, hospitals, shopping malls.
"""

import argparse
import json
import math
import sys
import urllib.request
import urllib.parse

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# Bangkok BTS/MRT station coordinates (manually curated for accuracy)
# These are more reliable than OSM data for Thai transit
BTS_MRT_STATIONS = [
    # BTS Sukhumvit Line
    {"name": "BTS คูคต (Khu Khot)", "lat": 13.9326, "lon": 100.6469, "line": "BTS Sukhumvit"},
    {"name": "BTS แยก คปอ. (Royal Thai Air Force Museum)", "lat": 13.9175, "lon": 100.6268, "line": "BTS Sukhumvit"},
    {"name": "BTS พหลโยธิน 59 (Phahon Yothin 59)", "lat": 13.8997, "lon": 100.6137, "line": "BTS Sukhumvit"},
    {"name": "BTS สายหยุด (Sai Yud)", "lat": 13.8879, "lon": 100.6098, "line": "BTS Sukhumvit"},
    {"name": "BTS สะพานใหม่ (Saphan Mai)", "lat": 13.8768, "lon": 100.6062, "line": "BTS Sukhumvit"},
    {"name": "BTS หมอชิต (Mo Chit)", "lat": 13.8027, "lon": 100.5536, "line": "BTS Sukhumvit"},
    {"name": "BTS สะพานควาย (Saphan Khwai)", "lat": 13.7939, "lon": 100.5494, "line": "BTS Sukhumvit"},
    {"name": "BTS อารีย์ (Ari)", "lat": 13.7797, "lon": 100.5447, "line": "BTS Sukhumvit"},
    {"name": "BTS สนามเป้า (Sanam Pao)", "lat": 13.7720, "lon": 100.5417, "line": "BTS Sukhumvit"},
    {"name": "BTS อนุสาวรีย์ (Victory Monument)", "lat": 13.7627, "lon": 100.5374, "line": "BTS Sukhumvit"},
    {"name": "BTS พญาไท (Phaya Thai)", "lat": 13.7565, "lon": 100.5347, "line": "BTS Sukhumvit"},
    {"name": "BTS ราชเทวี (Ratchathewi)", "lat": 13.7517, "lon": 100.5318, "line": "BTS Sukhumvit"},
    {"name": "BTS สยาม (Siam)", "lat": 13.7454, "lon": 100.5341, "line": "BTS Sukhumvit"},
    {"name": "BTS ชิดลม (Chit Lom)", "lat": 13.7440, "lon": 100.5430, "line": "BTS Sukhumvit"},
    {"name": "BTS เพลินจิต (Phloen Chit)", "lat": 13.7439, "lon": 100.5480, "line": "BTS Sukhumvit"},
    {"name": "BTS นานา (Nana)", "lat": 13.7404, "lon": 100.5554, "line": "BTS Sukhumvit"},
    {"name": "BTS อโศก (Asok)", "lat": 13.7369, "lon": 100.5606, "line": "BTS Sukhumvit"},
    {"name": "BTS พร้อมพงษ์ (Phrom Phong)", "lat": 13.7303, "lon": 100.5696, "line": "BTS Sukhumvit"},
    {"name": "BTS ทองหล่อ (Thong Lo)", "lat": 13.7248, "lon": 100.5783, "line": "BTS Sukhumvit"},
    {"name": "BTS เอกมัย (Ekkamai)", "lat": 13.7194, "lon": 100.5855, "line": "BTS Sukhumvit"},
    {"name": "BTS พระโขนง (Phra Khanong)", "lat": 13.7152, "lon": 100.5913, "line": "BTS Sukhumvit"},
    {"name": "BTS อ่อนนุช (On Nut)", "lat": 13.7059, "lon": 100.6012, "line": "BTS Sukhumvit"},
    {"name": "BTS บางจาก (Bang Chak)", "lat": 13.6965, "lon": 100.6045, "line": "BTS Sukhumvit"},
    {"name": "BTS ปุณณวิถี (Punnawithi)", "lat": 13.6893, "lon": 100.6102, "line": "BTS Sukhumvit"},
    {"name": "BTS อุดมสุข (Udom Suk)", "lat": 13.6798, "lon": 100.6098, "line": "BTS Sukhumvit"},
    {"name": "BTS บางนา (Bang Na)", "lat": 13.6685, "lon": 100.6048, "line": "BTS Sukhumvit"},
    {"name": "BTS แบริ่ง (Bearing)", "lat": 13.6600, "lon": 100.6011, "line": "BTS Sukhumvit"},
    {"name": "BTS สำโรง (Samrong)", "lat": 13.6458, "lon": 100.5955, "line": "BTS Sukhumvit"},
    {"name": "BTS เคหะฯ (Kheha)", "lat": 13.5932, "lon": 100.6393, "line": "BTS Sukhumvit"},
    # BTS Silom Line
    {"name": "BTS สนามกีฬา (National Stadium)", "lat": 13.7463, "lon": 100.5290, "line": "BTS Silom"},
    {"name": "BTS ราชดำริ (Ratchadamri)", "lat": 13.7405, "lon": 100.5394, "line": "BTS Silom"},
    {"name": "BTS ศาลาแดง (Sala Daeng)", "lat": 13.7284, "lon": 100.5345, "line": "BTS Silom"},
    {"name": "BTS ช่องนนทรี (Chong Nonsi)", "lat": 13.7231, "lon": 100.5290, "line": "BTS Silom"},
    {"name": "BTS สุรศักดิ์ (Surasak)", "lat": 13.7191, "lon": 100.5193, "line": "BTS Silom"},
    {"name": "BTS สะพานตากสิน (Saphan Taksin)", "lat": 13.7186, "lon": 100.5141, "line": "BTS Silom"},
    {"name": "BTS กรุงธนบุรี (Krung Thon Buri)", "lat": 13.7208, "lon": 100.5032, "line": "BTS Silom"},
    {"name": "BTS วงเวียนใหญ่ (Wongwian Yai)", "lat": 13.7213, "lon": 100.4943, "line": "BTS Silom"},
    {"name": "BTS บางหว้า (Bang Wa)", "lat": 13.7207, "lon": 100.4573, "line": "BTS Silom"},
    # MRT Blue Line (key stations)
    {"name": "MRT ท่าพระ (Tha Phra)", "lat": 13.7258, "lon": 100.4665, "line": "MRT Blue"},
    {"name": "MRT หัวลำโพง (Hua Lamphong)", "lat": 13.7375, "lon": 100.5168, "line": "MRT Blue"},
    {"name": "MRT สามย่าน (Sam Yan)", "lat": 13.7325, "lon": 100.5288, "line": "MRT Blue"},
    {"name": "MRT สีลม (Si Lom)", "lat": 13.7291, "lon": 100.5360, "line": "MRT Blue"},
    {"name": "MRT ลุมพินี (Lumphini)", "lat": 13.7256, "lon": 100.5435, "line": "MRT Blue"},
    {"name": "MRT สุขุมวิท (Sukhumvit)", "lat": 13.7372, "lon": 100.5607, "line": "MRT Blue"},
    {"name": "MRT เพชรบุรี (Phetchaburi)", "lat": 13.7482, "lon": 100.5636, "line": "MRT Blue"},
    {"name": "MRT พระราม 9 (Phra Ram 9)", "lat": 13.7578, "lon": 100.5652, "line": "MRT Blue"},
    {"name": "MRT ศูนย์วัฒนธรรม (Thailand Cultural Centre)", "lat": 13.7652, "lon": 100.5701, "line": "MRT Blue"},
    {"name": "MRT ห้วยขวาง (Huai Khwang)", "lat": 13.7783, "lon": 100.5741, "line": "MRT Blue"},
    {"name": "MRT สุทธิสาร (Sutthisan)", "lat": 13.7897, "lon": 100.5741, "line": "MRT Blue"},
    {"name": "MRT รัชดาภิเษก (Ratchadaphisek)", "lat": 13.7977, "lon": 100.5743, "line": "MRT Blue"},
    {"name": "MRT ลาดพร้าว (Lat Phrao)", "lat": 13.8061, "lon": 100.5736, "line": "MRT Blue"},
    {"name": "MRT พหลโยธิน (Phahon Yothin)", "lat": 13.8130, "lon": 100.5620, "line": "MRT Blue"},
    {"name": "MRT จตุจักร (Chatuchak Park)", "lat": 13.8022, "lon": 100.5537, "line": "MRT Blue"},
    {"name": "MRT บางซื่อ (Bang Sue)", "lat": 13.8064, "lon": 100.5377, "line": "MRT Blue"},
    {"name": "MRT ตลาดบางใหญ่ (Talat Bang Yai)", "lat": 13.8646, "lon": 100.4161, "line": "MRT Blue"},
    # Airport Rail Link
    {"name": "ARL พญาไท (Phaya Thai)", "lat": 13.7565, "lon": 100.5347, "line": "Airport Rail Link"},
    {"name": "ARL ราชปรารภ (Ratchaprarop)", "lat": 13.7539, "lon": 100.5401, "line": "Airport Rail Link"},
    {"name": "ARL มักกะสัน (Makkasan)", "lat": 13.7506, "lon": 100.5571, "line": "Airport Rail Link"},
    {"name": "ARL รามคำแหง (Ramkhamhaeng)", "lat": 13.7579, "lon": 100.5967, "line": "Airport Rail Link"},
    {"name": "ARL หัวหมาก (Hua Mak)", "lat": 13.7383, "lon": 100.6357, "line": "Airport Rail Link"},
    {"name": "ARL บ้านทับช้าง (Ban Thap Chang)", "lat": 13.7263, "lon": 100.6636, "line": "Airport Rail Link"},
    {"name": "ARL ลาดกระบัง (Lat Krabang)", "lat": 13.7277, "lon": 100.7236, "line": "Airport Rail Link"},
    {"name": "ARL สุวรรณภูมิ (Suvarnabhumi)", "lat": 13.6928, "lon": 100.7508, "line": "Airport Rail Link"},
]


def haversine(lat1, lon1, lat2, lon2):
    """Calculate distance in meters between two coordinates."""
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def find_nearest_stations(lat, lon, max_distance=2000, limit=5):
    """Find nearest BTS/MRT/ARL stations from hardcoded data."""
    results = []
    for station in BTS_MRT_STATIONS:
        dist = haversine(lat, lon, station["lat"], station["lon"])
        if dist <= max_distance:
            results.append({
                "name": station["name"],
                "line": station["line"],
                "distance_m": round(dist),
                "walk_min": round(dist / 80),  # ~80m/min walking speed
            })
    results.sort(key=lambda x: x["distance_m"])
    return results[:limit]


def overpass_query(lat, lon, radius, category):
    """Query Overpass API for nearby amenities."""
    queries = {
        "school": f"""
            [out:json][timeout:15];
            (
              node["amenity"="school"](around:{radius},{lat},{lon});
              way["amenity"="school"](around:{radius},{lat},{lon});
              node["amenity"="kindergarten"](around:{radius},{lat},{lon});
              node["amenity"="university"](around:{radius},{lat},{lon});
            );
            out center;
        """,
        "hospital": f"""
            [out:json][timeout:15];
            (
              node["amenity"="hospital"](around:{radius},{lat},{lon});
              way["amenity"="hospital"](around:{radius},{lat},{lon});
              node["amenity"="clinic"](around:{radius},{lat},{lon});
            );
            out center;
        """,
        "shopping": f"""
            [out:json][timeout:15];
            (
              node["shop"="mall"](around:{radius},{lat},{lon});
              way["shop"="mall"](around:{radius},{lat},{lon});
              node["shop"="supermarket"](around:{radius},{lat},{lon});
              way["shop"="supermarket"](around:{radius},{lat},{lon});
              node["shop"="department_store"](around:{radius},{lat},{lon});
              way["shop"="department_store"](around:{radius},{lat},{lon});
            );
            out center;
        """,
        "park": f"""
            [out:json][timeout:15];
            (
              node["leisure"="park"](around:{radius},{lat},{lon});
              way["leisure"="park"](around:{radius},{lat},{lon});
            );
            out center;
        """,
    }

    query = queries.get(category)
    if not query:
        return []

    data = urllib.parse.urlencode({"data": query}).encode()
    req = urllib.request.Request(OVERPASS_URL, data=data)
    req.add_header("User-Agent", "NPA-guy-location-intel/1.0")

    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            result = json.loads(resp.read())
    except Exception as e:
        print(f"  ⚠️  Overpass query failed for {category}: {e}", file=sys.stderr)
        return []

    amenities = []
    for el in result.get("elements", []):
        el_lat = el.get("lat") or el.get("center", {}).get("lat")
        el_lon = el.get("lon") or el.get("center", {}).get("lon")
        if not el_lat or not el_lon:
            continue

        name = el.get("tags", {}).get("name:en") or el.get("tags", {}).get("name", "Unknown")
        dist = haversine(lat, lon, el_lat, el_lon)

        amenities.append({
            "name": name,
            "type": el.get("tags", {}).get("amenity") or el.get("tags", {}).get("shop") or el.get("tags", {}).get("leisure", category),
            "distance_m": round(dist),
            "lat": el_lat,
            "lon": el_lon,
        })

    amenities.sort(key=lambda x: x["distance_m"])
    return amenities


def location_report(lat, lon, radius=2000):
    """Generate full location intelligence report."""
    report = {
        "coordinates": {"lat": lat, "lon": lon},
        "radius_m": radius,
    }

    # Transit (from hardcoded data — fast and reliable)
    stations = find_nearest_stations(lat, lon, max_distance=radius)
    report["transit"] = stations

    nearest = stations[0] if stations else None
    if nearest:
        dist = nearest["distance_m"]
        if dist <= 500:
            report["transit_rating"] = "PREMIUM (within 500m)"
        elif dist <= 1000:
            report["transit_rating"] = "GOOD (within 1km)"
        elif dist <= 2000:
            report["transit_rating"] = "MODERATE (within 2km)"
        else:
            report["transit_rating"] = "FAR (>2km)"
    else:
        report["transit_rating"] = "NO STATION NEARBY"

    # Schools, hospitals, shopping from Overpass
    for category in ["school", "hospital", "shopping"]:
        report[category] = overpass_query(lat, lon, radius, category)[:10]

    return report


def print_report(report):
    """Pretty-print location report."""
    lat, lon = report["coordinates"]["lat"], report["coordinates"]["lon"]
    print(f"\n{'='*60}")
    print(f"LOCATION INTELLIGENCE REPORT")
    print(f"Coordinates: {lat}, {lon} | Radius: {report['radius_m']}m")
    print(f"{'='*60}")

    print(f"\n--- Transit: {report.get('transit_rating', 'N/A')} ---")
    for s in report.get("transit", []):
        print(f"  {s['name']} ({s['line']})")
        print(f"    Distance: {s['distance_m']}m | Walk: ~{s['walk_min']} min")

    for category, label in [("school", "Schools"), ("hospital", "Hospitals"), ("shopping", "Shopping")]:
        items = report.get(category, [])
        print(f"\n--- {label} ({len(items)} found) ---")
        for item in items[:5]:
            print(f"  {item['name']} — {item['distance_m']}m")

    print(f"\n{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(description="Location intelligence for Thai NPA properties")
    parser.add_argument("--lat", type=float, required=True, help="Latitude")
    parser.add_argument("--lon", type=float, required=True, help="Longitude")
    parser.add_argument("--radius", type=int, default=2000, help="Search radius in meters (default: 2000)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--transit-only", action="store_true", help="Only show transit stations")

    args = parser.parse_args()

    if args.transit_only:
        stations = find_nearest_stations(args.lat, args.lon, max_distance=args.radius)
        if args.json:
            print(json.dumps(stations, ensure_ascii=False, indent=2))
        else:
            for s in stations:
                print(f"  {s['name']} ({s['line']}) — {s['distance_m']}m (~{s['walk_min']}min walk)")
        return

    report = location_report(args.lat, args.lon, radius=args.radius)

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_report(report)


if __name__ == "__main__":
    main()

"""CLI to get GPS coordinates from Thai deed (parcel) numbers.

Usage:
    # Single lookup
    python main.py --pv 90 --am 01 --parcel 83776 --token <JWT>

    # Lookup with amphur name search
    python main.py --pv 90 --amphur-name "เมืองสงขลา" --parcel 83776 --token <JWT>

    # Simple lat,lon output
    python main.py --pv 90 --am 01 --parcel 83776 --token <JWT> --simple

    # Batch from JSON file
    python main.py --batch deeds.json --token <JWT>

    # Token from env var
    export LANDSMAPS_TOKEN=<JWT>
    python main.py --pv 90 --am 01 --parcel 83776
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys

from client import LandsMapsClient
from models import AmphurRegistry, DeedQuery, ParcelResult


def format_result(query: DeedQuery, result: ParcelResult) -> dict:
    """Format a parcel result as a clean dict for JSON output."""
    return {
        "query": {
            "province_code": query.province_code,
            "amphur_code": query.amphur_code,
            "parcel_no": query.parcel_no,
        },
        "gps": {
            "lat": result.lat,
            "lon": result.lon,
        },
        "location": {
            "province": result.provname,
            "province_en": result.provname_en,
            "amphur": result.amphurname,
            "amphur_en": result.amphurname_en,
            "tumbol": result.tumbolname,
            "tumbol_en": result.tumbolname_en,
        },
        "area": {
            "rai": int(result.rai) if result.rai else 0,
            "ngan": int(result.ngan) if result.ngan else 0,
            "wa": int(result.wa) if result.wa else 0,
            "subwa": int(result.subwa) if result.subwa else 0,
            "sqm": result.area_sqm,
        },
        "land_price_per_rai": result.landprice,
        "parcel_type": result.parcel_type,
        "land_office": result.landoffice,
        "qrcode_link": result.qrcode_link,
    }


def format_simple(result: ParcelResult) -> str:
    """Return just lat,lon."""
    return f"{result.lat},{result.lon}"


async def single_lookup(
    client: LandsMapsClient,
    query: DeedQuery,
    simple: bool,
) -> None:
    result = await client.get_parcel(query)
    if result is None:
        print(f"No result for parcel {query.parcel_no}", file=sys.stderr)
        sys.exit(1)

    if simple:
        print(format_simple(result))
    else:
        print(json.dumps(format_result(query, result), ensure_ascii=False, indent=2))


async def batch_lookup(
    client: LandsMapsClient,
    batch_path: str,
    simple: bool,
) -> None:
    raw = json.loads(open(batch_path, encoding="utf-8").read())
    queries = [DeedQuery.model_validate(item) for item in raw]

    results = await client.get_parcels_batch(queries)

    output = []
    for query, result, error in results:
        if error:
            output.append({"query": query.model_dump(), "error": error})
        elif result:
            if simple:
                print(f"{query.parcel_no}: {format_simple(result)}")
            else:
                output.append(format_result(query, result))

    if not simple:
        print(json.dumps(output, ensure_ascii=False, indent=2))


def resolve_amphur_code(
    registry: AmphurRegistry,
    pvcode: str,
    amphur_name: str,
) -> str:
    """Resolve amphur Thai name to code. Exits if ambiguous or not found."""
    matches = registry.search_by_thai_name(amphur_name, pvcode=pvcode)
    if not matches:
        # Try English
        matches = registry.search_by_eng_name(amphur_name, pvcode=pvcode)

    if not matches:
        print(f"No amphur matching '{amphur_name}' in province {pvcode}", file=sys.stderr)
        available = registry.list_by_province(pvcode)
        if available:
            print("Available amphurs:", file=sys.stderr)
            for a in available:
                print(f"  {a.amcode}: {a.amnamethai} ({a.amnameeng})", file=sys.stderr)
        sys.exit(1)

    if len(matches) > 1:
        print(f"Multiple amphurs match '{amphur_name}':", file=sys.stderr)
        for a in matches:
            print(f"  {a.amcode}: {a.amnamethai} ({a.amnameeng})", file=sys.stderr)
        print("Use --am with the exact code.", file=sys.stderr)
        sys.exit(1)

    return matches[0].amcode


async def async_main() -> None:
    parser = argparse.ArgumentParser(description="Get GPS from Thai deed number")
    parser.add_argument("--token", default=os.environ.get("LANDSMAPS_TOKEN"), help="Bearer JWT token (or set LANDSMAPS_TOKEN env var). Auto-acquired if omitted.")
    parser.add_argument("--simple", action="store_true", help="Output just lat,lon")

    # Single mode
    parser.add_argument("--pv", help="2-digit province code (e.g. 90)")
    parser.add_argument("--am", help="2-digit amphur code (e.g. 01)")
    parser.add_argument("--amphur-name", help="Amphur name (Thai or English) — resolves to code")
    parser.add_argument("--parcel", help="Parcel/deed number")

    # Batch mode
    parser.add_argument("--batch", help="Path to JSON file with list of {province_code, amphur_code, parcel_no}")

    args = parser.parse_args()

    client = await LandsMapsClient.create(args.token)

    if args.batch:
        await batch_lookup(client, args.batch, args.simple)
        return

    if not args.pv or not args.parcel:
        print("Required: --pv <province_code> --parcel <parcel_no>", file=sys.stderr)
        print("Plus either --am <amphur_code> or --amphur-name <name>", file=sys.stderr)
        sys.exit(1)

    am_code = args.am
    if not am_code:
        if not args.amphur_name:
            print("Required: --am <amphur_code> or --amphur-name <name>", file=sys.stderr)
            sys.exit(1)
        registry = AmphurRegistry()
        am_code = resolve_amphur_code(registry, args.pv, args.amphur_name)

    query = DeedQuery(province_code=args.pv, amphur_code=am_code, parcel_no=args.parcel)
    await single_lookup(client, query, args.simple)


if __name__ == "__main__":
    asyncio.run(async_main())

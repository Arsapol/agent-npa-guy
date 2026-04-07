#!/usr/bin/env python3
"""Unified NPA query CLI — search across all 12 providers.

Usage:
    python query.py search --province กรุงเทพ --max-price 3000000
    python query.py search --province นนทบุรี --sources LED,SAM,BAM
    python query.py search --sources SCB,GSB,TTB,BAY,LH,GHB --type คอนโด
    python query.py search --type คอนโด --min-price 500000 --max-price 2000000
    python query.py stats
    python query.py summary
"""

from __future__ import annotations

import argparse
import json
from adapter import search, stats, summary
from models import SearchFilters, Source


def _parse_sources(s: str | None) -> list[Source] | None:
    if not s:
        return None
    return [Source(x.strip().upper()) for x in s.split(",")]


def _format_price(baht: float | None) -> str:
    if baht is None:
        return "N/A"
    if baht >= 1_000_000:
        return f"฿{baht / 1_000_000:.2f}M"
    if baht >= 1_000:
        return f"฿{baht / 1_000:.1f}K"
    return f"฿{baht:.0f}"


def cmd_search(args: argparse.Namespace) -> None:
    filters = SearchFilters(
        province=args.province,
        district=args.district,
        subdistrict=args.subdistrict,
        min_price=args.min_price,
        max_price=args.max_price,
        property_type=args.property_type,
        keyword=args.keyword,
        sources=_parse_sources(args.sources),
        limit=args.limit,
        offset=args.offset,
        sort_by=args.sort,
        sort_desc=args.desc,
    )

    results = search(filters)

    if args.json:
        print(json.dumps(
            [r.model_dump() for r in results],
            ensure_ascii=False, indent=2, default=str,
        ))
        return

    src_label = args.sources or "ALL"
    print(f"[{src_label}] Found {len(results)} properties:\n")

    for p in results:
        discount = f" ({p.discount_pct:+.0f}%)" if p.discount_pct else ""
        print(f"  [{p.source.value}:{p.source_id}] {p.property_type}")
        print(f"    {p.location_display}")
        print(f"    Price: {_format_price(p.price_baht)}{discount} | Size: {p.size_display}")
        if p.project_name:
            print(f"    Project: {p.project_name}")
        if p.address:
            print(f"    Address: {p.address[:80]}")
        if p.lat and p.lon:
            print(f"    GPS: {p.lat:.6f}, {p.lon:.6f}")
        if p.next_auction_date:
            print(f"    Auction: {p.next_auction_date} (#{p.total_auction_count})")
        if p.status:
            print(f"    Status: {p.status}")
        print()


def cmd_stats(args: argparse.Namespace) -> None:
    provider_stats = stats()

    if args.json:
        print(json.dumps(
            [s.model_dump() for s in provider_stats],
            ensure_ascii=False, indent=2, default=str,
        ))
        return

    grand_total = sum(s.total for s in provider_stats)
    print(f"=== NPA Cross-Provider Stats ({grand_total:,} total) ===\n")

    for s in provider_stats:
        print(f"  {s.source.value}: {s.total:,} properties")
        print(f"    Price: {_format_price(s.min_price)} — {_format_price(s.max_price)}")
        print(f"    Avg: {_format_price(s.avg_price)}")
        if s.provinces:
            top3 = ", ".join(f"{p['province']}({p['cnt']})" for p in s.provinces[:3])
            print(f"    Top: {top3}")
        print()


def cmd_summary(args: argparse.Namespace) -> None:
    result = summary()

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
        return

    print(f"=== NPA Summary: {result['grand_total']:,} total properties ===\n")
    for p in result["providers"]:
        avg = _format_price(p["avg_price"])
        print(f"  {p['source']:6s} | {p['total']:>6,} props | avg {avg}")
        if p["top_provinces"]:
            provs = ", ".join(f"{x['province']}" for x in p["top_provinces"][:3])
            print(f"         | top: {provs}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Unified NPA query across LED, SAM, BAM, JAM, KTB, KBank, SCB, GSB, TTB, BAY, LH, GHB",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # search
    sp = sub.add_parser("search", help="Search properties across providers")
    sp.add_argument("--province", type=str, help="Province name (partial)")
    sp.add_argument("--district", type=str, help="District (partial)")
    sp.add_argument("--subdistrict", type=str, help="Sub-district (partial)")
    sp.add_argument("--min-price", type=float, help="Min price in baht")
    sp.add_argument("--max-price", type=float, help="Max price in baht")
    sp.add_argument("--type", dest="property_type", type=str, help="Property type (partial)")
    sp.add_argument("--keyword", type=str, help="Keyword search")
    sp.add_argument("--sources", type=str, help="Comma-separated: LED,SAM,BAM,JAM,KTB,KBANK")
    sp.add_argument("--limit", type=int, default=20)
    sp.add_argument("--offset", type=int, default=0)
    sp.add_argument("--sort", default="price", choices=["price", "province", "newest"])
    sp.add_argument("--desc", action="store_true")
    sp.add_argument("--json", action="store_true")

    # stats
    st = sub.add_parser("stats", help="Per-provider statistics")
    st.add_argument("--json", action="store_true")

    # summary
    sm = sub.add_parser("summary", help="Cross-provider summary")
    sm.add_argument("--json", action="store_true")

    args = parser.parse_args()
    if args.command == "search":
        cmd_search(args)
    elif args.command == "stats":
        cmd_stats(args)
    elif args.command == "summary":
        cmd_summary(args)


if __name__ == "__main__":
    main()

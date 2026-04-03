#!/usr/bin/env python3
"""Check for stale KB entries and optionally mark them.

Usage:
    python check_stale.py                    # Report stale entries
    python check_stale.py --mark             # Mark expired entries as stale
    python check_stale.py --category pricing # Check specific category
    python check_stale.py --summary          # Quick summary only
"""

import argparse
import os
import subprocess
import sys

POSTGRES_URI = os.getenv("POSTGRES_URI", "postgresql://arsapolm@localhost:5432/npa_kb")


def run_sql(sql):
    result = subprocess.run(
        ["psql", POSTGRES_URI, "-t", "-A", "-F", "\t", "-c", sql],
        capture_output=True, text=True, timeout=10,
    )
    if result.returncode != 0:
        print(f"Error: {result.stderr.strip()}", file=sys.stderr)
        return None
    return result.stdout.strip()


def summary():
    output = run_sql("""
        SELECT category,
               COUNT(*) as total,
               COUNT(*) FILTER (WHERE NOT stale AND valid_until > NOW()) as fresh,
               COUNT(*) FILTER (WHERE stale OR valid_until <= NOW()) as expired
        FROM kb_metadata
        GROUP BY category
        ORDER BY category;
    """)
    if not output:
        print("No metadata entries found.")
        return

    print(f"\nKB Freshness Summary ({POSTGRES_URI.split('/')[-1]})")
    print(f"{'Category':<18} {'Total':>6} {'Fresh':>6} {'Stale':>6}")
    print("-" * 40)
    total_all, fresh_all, stale_all = 0, 0, 0
    for line in output.split("\n"):
        parts = line.split("\t")
        if len(parts) >= 4:
            cat, total, fresh, stale = parts
            print(f"{cat:<18} {total:>6} {fresh:>6} {stale:>6}")
            total_all += int(total)
            fresh_all += int(fresh)
            stale_all += int(stale)
    print("-" * 40)
    print(f"{'TOTAL':<18} {total_all:>6} {fresh_all:>6} {stale_all:>6}")

    if stale_all > 0:
        print(f"\n⚠️  {stale_all} stale entries need re-verification")


def list_stale(category=None, limit=30):
    where = "stale = true OR valid_until <= NOW()"
    if category:
        where += f" AND category = '{category}'"

    output = run_sql(f"""
        SELECT id, category, area, source, summary,
               ingested_at::date, valid_until::date,
               EXTRACT(DAY FROM NOW() - valid_until)::int as days_overdue
        FROM kb_metadata
        WHERE {where}
        ORDER BY valid_until ASC
        LIMIT {limit};
    """)

    if not output:
        print("✅ No stale entries!")
        return

    print(f"\nStale KB Entries:\n")
    for line in output.split("\n"):
        parts = line.split("\t")
        if len(parts) >= 8:
            id_, cat, area, src, desc, ingested, valid, overdue = parts
            print(f"  [{id_}] [{cat}] {area or '-'}")
            print(f"      {desc[:80]}")
            print(f"      Source: {src or '-'} | Ingested: {ingested} | Overdue: {overdue}d")
            print()


def mark_expired():
    result = subprocess.run(
        ["psql", POSTGRES_URI, "-c",
         "UPDATE kb_metadata SET stale = true, stale_marked_at = NOW() "
         "WHERE stale = false AND valid_until <= NOW();"],
        capture_output=True, text=True, timeout=10,
    )
    if result.returncode != 0:
        print(f"Error: {result.stderr.strip()}", file=sys.stderr)
        return

    # Parse "UPDATE N"
    output = result.stdout.strip()
    print(f"Marked stale: {output}")


def main():
    parser = argparse.ArgumentParser(description="KB staleness checker")
    parser.add_argument("--summary", action="store_true", help="Quick summary by category")
    parser.add_argument("--mark", action="store_true", help="Mark expired entries as stale")
    parser.add_argument("--category", help="Filter by category")
    parser.add_argument("--limit", type=int, default=30)

    args = parser.parse_args()

    if args.mark:
        mark_expired()

    if args.summary:
        summary()
    else:
        list_stale(category=args.category, limit=args.limit)
        print()
        summary()


if __name__ == "__main__":
    main()

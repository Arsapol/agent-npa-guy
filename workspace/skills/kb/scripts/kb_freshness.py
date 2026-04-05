#!/usr/bin/env python3
"""
KB Freshness Checker for NPA-guy's Knowledge Base.

Scans all docs in kb_metadata, cross-references with LED/SAM property locations,
and reports which are stale, expiring soon, or have zero coverage.

Usage:
    python3 kb_freshness.py              # Full report
    python3 kb_freshness.py --stale      # Only stale docs
    python3 kb_freshness.py --area NAME  # Check specific area
    python3 kb_freshness.py --queue      # Re-research queue (areas/categories to refresh)
"""

import argparse
import os
import subprocess
import sys
from datetime import datetime, timedelta
from collections import defaultdict

# ─── Configuration ───────────────────────────────────────────────────────────

CATEGORY_TTL = {
    "pricing": 90,
    "rental": 90,
    "flood": 365,
    "project": 365,
    "infrastructure": 365,
    "legal": 180,
    "area": 180,
    "other": 90,
}

EXPIRING_SOON_DAYS = 7

PG_URI = os.environ.get("POSTGRES_URI", "postgresql:///npa_kb")

# ─── Helpers ─────────────────────────────────────────────────────────────────


def psql(sql: str, uri: str = PG_URI) -> list[list[str]]:
    """Run a psql query and return rows as list of lists."""
    result = subprocess.run(
        ["psql", uri, "-t", "-A", "-F", "\t", "-c", sql],
        capture_output=True, text=True, timeout=15,
    )
    if result.returncode != 0:
        print(f"⚠️  psql error: {result.stderr.strip()[:200]}", file=sys.stderr)
        return []
    lines = result.stdout.strip()
    if not lines:
        return []
    return [line.split("\t") for line in lines.split("\n")]


def psql_one(sql: str) -> list[str] | None:
    """Run a psql query returning a single row."""
    rows = psql(sql)
    return rows[0] if rows else None


def fmt_date(dt_str: str) -> str:
    """Format a timestamp string to a readable date."""
    if not dt_str:
        return "-"
    try:
        return dt_str[:10]
    except Exception:
        return dt_str


def days_between(dt_str: str, ref: datetime) -> int | None:
    """Days between a timestamp string and a reference datetime. Positive = future."""
    if not dt_str:
        return None
    try:
        dt = datetime.fromisoformat(dt_str)
        return (dt - ref).days
    except Exception:
        return None


# ─── Data Retrieval ──────────────────────────────────────────────────────────


def get_all_metadata(area_filter: str = "") -> list[dict]:
    """Fetch all kb_metadata rows with computed freshness fields."""
    where_parts = []
    if area_filter:
        safe_area = area_filter.replace("'", "''")
        where_parts.append(f"(area ILIKE '%{safe_area}%')")

    where = f"WHERE {' AND '.join(where_parts)}" if where_parts else ""

    sql = f"""
        SELECT
            doc_id,
            category,
            COALESCE(area, '(no area)') as area,
            COALESCE(source, '(no source)') as source,
            summary,
            ingested_at::text,
            valid_until::text,
            stale,
            EXTRACT(DAY FROM valid_until - NOW())::numeric(10,1) as days_remaining,
            CASE
                WHEN stale OR valid_until <= NOW() THEN 'STALE'
                WHEN valid_until <= NOW() + INTERVAL '{EXPIRING_SOON_DAYS} days' THEN 'EXPIRING_SOON'
                ELSE 'FRESH'
            END as status
        FROM kb_metadata
        {where}
        ORDER BY valid_until ASC;
    """
    rows = psql(sql)
    results = []
    for r in rows:
        if len(r) < 10:
            continue
        results.append({
            "doc_id": r[0],
            "category": r[1],
            "area": r[2],
            "source": r[3],
            "summary": r[4],
            "ingested_at": r[5],
            "valid_until": r[6],
            "stale": r[7] == "t",
            "days_remaining": float(r[8]) if r[8] else None,
            "status": r[9],
        })
    return results


def get_property_areas() -> set[str]:
    """Get all distinct areas from LED/SAM properties tables for coverage check."""
    areas = set()

    # From properties table (has province + ampur)
    rows = psql(
        "SELECT DISTINCT COALESCE(ampur, province) FROM properties "
        "WHERE ampur IS NOT NULL AND ampur != '-' AND province IS NOT NULL AND province != '-';"
    )
    for r in rows:
        if r and r[0]:
            areas.add(r[0].strip())

    # Also get provinces
    rows = psql(
        "SELECT DISTINCT province FROM properties "
        "WHERE province IS NOT NULL AND province != '-';"
    )
    for r in rows:
        if r and r[0]:
            areas.add(r[0].strip())

    return areas


def get_kb_areas() -> set[str]:
    """Get all distinct areas from kb_metadata."""
    rows = psql(
        "SELECT DISTINCT area FROM kb_metadata WHERE area IS NOT NULL AND area != '';"
    )
    return {r[0].strip() for r in rows if r and r[0]}


def normalize_area(area: str) -> str:
    """Normalize area name for comparison by removing เขต prefix and stripping."""
    a = area.strip()
    # Remove เขต prefix for comparison
    if a.startswith("เขต"):
        a = a[3:].strip()
    return a


def build_area_mapping(property_areas: set[str], kb_areas: set[str]) -> dict[str, list[str]]:
    """Build a mapping from normalized property area to matching kb areas."""
    mapping = defaultdict(list)
    # Build normalized lookup for kb_areas
    kb_normalized = {}
    for ka in kb_areas:
        kn = normalize_area(ka)
        kb_normalized[kn] = ka
        # Also store as-is
        kb_normalized[ka] = ka

    for pa in property_areas:
        pn = normalize_area(pa)
        if pn in kb_normalized:
            mapping[pa].append(kb_normalized[pn])
        elif pa in kb_normalized:
            mapping[pa].append(kb_normalized[pa])
    return dict(mapping)


# ─── Report Builders ─────────────────────────────────────────────────────────

HEADER = """
╔══════════════════════════════════════════════════════════════════╗
║              📊 NPA KB Freshness Report                         ║
╚══════════════════════════════════════════════════════════════════╝
"""

DIVIDER = "─" * 70


def print_full_report(area_filter: str = ""):
    """Print the complete freshness report."""
    docs = get_all_metadata(area_filter)
    if not docs:
        print("No documents found in kb_metadata.")
        return

    now = datetime.now()

    # ─── Summary ─────────────────────────────────────────────
    total = len(docs)
    fresh = [d for d in docs if d["status"] == "FRESH"]
    stale = [d for d in docs if d["status"] == "STALE"]
    expiring = [d for d in docs if d["status"] == "EXPIRING_SOON"]

    print(HEADER)
    if area_filter:
        print(f"  🔍 Filtered by area: '{area_filter}'\n")
    print(f"  Report generated: {now.strftime('%Y-%m-%d %H:%M')}")
    print(f"  {DIVIDER}")
    print(f"  Total docs:       {total:>5}")
    print(f"  ✅ Fresh:          {len(fresh):>5}  ({100*len(fresh)/total:.0f}%)")
    print(f"  ⚠️  Expiring soon: {len(expiring):>5}  (within {EXPIRING_SOON_DAYS} days)")
    print(f"  ❌ Stale:          {len(stale):>5}  ({100*len(stale)/total:.0f}%)" if stale else
          f"  ❌ Stale:             0")
    print(f"  {DIVIDER}")

    # ─── By Category ─────────────────────────────────────────
    print(f"\n  📁 Freshness by Category:")
    print(f"  {'Category':<18} {'Total':>5} {'Fresh':>6} {'Expiring':>9} {'Stale':>6} {'TTL':>5}")
    print(f"  {'─'*18} {'─'*5} {'─'*6} {'─'*9} {'─'*6} {'─'*5}")

    by_cat = defaultdict(list)
    for d in docs:
        by_cat[d["category"]].append(d)

    for cat in sorted(by_cat.keys()):
        cat_docs = by_cat[cat]
        ct = len(cat_docs)
        cf = len([d for d in cat_docs if d["status"] == "FRESH"])
        ce = len([d for d in cat_docs if d["status"] == "EXPIRING_SOON"])
        cs = len([d for d in cat_docs if d["status"] == "STALE"])
        ttl = CATEGORY_TTL.get(cat, 90)
        ttl_str = f"{ttl}d"
        print(f"  {cat:<18} {ct:>5} {cf:>6} {ce:>9} {cs:>6} {ttl_str:>5}")

    # ─── By Area ─────────────────────────────────────────────
    print(f"\n  📍 Freshness by Area (top 20):")
    print(f"  {'Area':<22} {'Total':>5} {'Fresh':>6} {'Expiring':>9} {'Stale':>6}")
    print(f"  {'─'*22} {'─'*5} {'─'*6} {'─'*9} {'─'*6}")

    by_area = defaultdict(list)
    for d in docs:
        by_area[d["area"]].append(d)

    sorted_areas = sorted(by_area.items(), key=lambda x: len(x[1]), reverse=True)
    for area, area_docs in sorted_areas[:20]:
        at = len(area_docs)
        af = len([d for d in area_docs if d["status"] == "FRESH"])
        ae = len([d for d in area_docs if d["status"] == "EXPIRING_SOON"])
        ast = len([d for d in area_docs if d["status"] == "STALE"])
        display = area[:22] if len(area) <= 22 else area[:19] + "..."
        print(f"  {display:<22} {at:>5} {af:>6} {ae:>9} {ast:>6}")

    # ─── Stale Details ───────────────────────────────────────
    if stale:
        print(f"\n  ❌ Stale Documents ({len(stale)}):")
        print(f"  {DIVIDER}")
        for d in stale[:30]:
            summary_short = (d["summary"][:60] + "...") if len(d.get("summary", "")) > 60 else (d.get("summary", "-"))
            days_over = abs(d["days_remaining"]) if d["days_remaining"] is not None else "?"
            print(f"  [{d['category']:<14}] {d['area']}")
            print(f"    {summary_short}")
            print(f"    Expired: {days_over}d ago | Ingested: {fmt_date(d['ingested_at'])} | Source: {d['source']}")
            print()

    # ─── Expiring Soon Details ───────────────────────────────
    if expiring:
        print(f"\n  ⏰ Expiring Soon ({len(expiring)}):")
        print(f"  {DIVIDER}")
        for d in sorted(expiring, key=lambda x: x["days_remaining"] or 0):
            summary_short = (d["summary"][:60] + "...") if len(d.get("summary", "")) > 60 else (d.get("summary", "-"))
            days_left = d["days_remaining"]
            print(f"  [{d['category']:<14}] {d['area']}")
            print(f"    {summary_short}")
            print(f"    Expires in {days_left:.0f}d | Valid until: {fmt_date(d['valid_until'])} | Source: {d['source']}")
            print()

    # ─── Coverage Gap Analysis ───────────────────────────────
    print(f"\n  🔎 Coverage Gap Analysis:")
    print(f"  {DIVIDER}")

    property_areas = get_property_areas()
    kb_areas = get_kb_areas()

    # Normalize for comparison
    area_map = build_area_mapping(property_areas, kb_areas)
    uncovered = []
    for pa in sorted(property_areas):
        pa_norm = normalize_area(pa)
        # Check if any kb area matches
        matched = False
        for ka in kb_areas:
            ka_norm = normalize_area(ka)
            if pa_norm == ka_norm or pa == ka:
                matched = True
                break
            # Substring match for broader areas
            if pa_norm in ka_norm or ka_norm in pa_norm:
                matched = True
                break
        if not matched:
            uncovered.append(pa)

    if uncovered:
        print(f"  Areas with NPA properties but NO KB coverage ({len(uncovered)}):")
        for u in uncovered[:30]:
            print(f"    • {u}")
        if len(uncovered) > 30:
            print(f"    ... and {len(uncovered) - 30} more")
    else:
        print(f"  ✅ All property areas have KB coverage")

    print()


def print_stale_only(area_filter: str = ""):
    """Print only stale and expiring-soon documents."""
    docs = get_all_metadata(area_filter)
    stale = [d for d in docs if d["status"] == "STALE"]
    expiring = [d for d in docs if d["status"] == "EXPIRING_SOON"]

    if not stale and not expiring:
        print("✅ No stale or expiring-soon documents found!")
        if area_filter:
            print(f"   (filtered by area: '{area_filter}')")
        return

    print(f"\n{'═'*70}")
    print(f"  🗑️  Stale & Expiring Documents")
    print(f"{'═'*70}\n")

    if stale:
        print(f"  ❌ STALE ({len(stale)}):")
        for d in stale:
            summary_short = (d["summary"][:70] + "...") if len(d.get("summary", "")) > 70 else (d.get("summary", "-"))
            days_over = abs(d["days_remaining"]) if d["days_remaining"] is not None else "?"
            print(f"    [{d['category']}] {d['area']}")
            print(f"      {summary_short}")
            print(f"      Expired {days_over}d ago | Source: {d['source']}")
            print()

    if expiring:
        print(f"\n  ⏰ EXPIRING SOON ({len(expiring)}):")
        for d in sorted(expiring, key=lambda x: x["days_remaining"] or 0):
            summary_short = (d["summary"][:70] + "...") if len(d.get("summary", "")) > 70 else (d.get("summary", "-"))
            print(f"    [{d['category']}] {d['area']}")
            print(f"      {summary_short}")
            print(f"      Expires in {d['days_remaining']:.0f}d | Source: {d['source']}")
            print()


def print_area_report(area_name: str):
    """Detailed report for a specific area."""
    docs = get_all_metadata(area_name)
    if not docs:
        print(f"❌ No KB documents found matching area: '{area_name}'")
        return

    print(f"\n{'═'*70}")
    print(f"  📍 Area Report: '{area_name}'")
    print(f"{'═'*70}\n")

    now = datetime.now()
    total = len(docs)
    fresh = [d for d in docs if d["status"] == "FRESH"]
    stale = [d for d in docs if d["status"] == "STALE"]
    expiring = [d for d in docs if d["status"] == "EXPIRING_SOON"]

    print(f"  Total: {total} | Fresh: {len(fresh)} | Expiring: {len(expiring)} | Stale: {len(stale)}")
    print(f"  {DIVIDER}\n")

    # Category breakdown
    by_cat = defaultdict(list)
    for d in docs:
        by_cat[d["category"]].append(d)

    for cat in sorted(by_cat.keys()):
        cat_docs = by_cat[cat]
        cf = len([d for d in cat_docs if d["status"] == "FRESH"])
        ce = len([d for d in cat_docs if d["status"] == "EXPIRING_SOON"])
        cs = len([d for d in cat_docs if d["status"] == "STALE"])
        ttl = CATEGORY_TTL.get(cat, 90)
        status_icon = "✅" if cs == 0 and ce == 0 else ("⏰" if ce > 0 else "❌")
        print(f"  {status_icon} {cat} (TTL: {ttl}d) — {cf} fresh, {ce} expiring, {cs} stale")

        for d in sorted(cat_docs, key=lambda x: x["valid_until"]):
            days = d["days_remaining"]
            if d["status"] == "STALE":
                icon = "  ❌"
            elif d["status"] == "EXPIRING_SOON":
                icon = "  ⏰"
            else:
                icon = "  ✅"
            summary_short = (d["summary"][:55] + "...") if len(d.get("summary", "")) > 55 else (d.get("summary", "-"))
            days_str = f"{days:.0f}d left" if days is not None else "?"
            if d["status"] == "STALE":
                days_str = f"{abs(days):.0f}d ago" if days is not None else "?"
            print(f"  {icon} {summary_short}")
            print(f"       {days_str} | Until: {fmt_date(d['valid_until'])} | Source: {d['source']}")
        print()

    # Recommendations
    missing_cats = set(CATEGORY_TTL.keys()) - set(by_cat.keys())
    if missing_cats:
        print(f"  📋 Missing categories for this area:")
        for mc in sorted(missing_cats):
            print(f"    • {mc} (TTL: {CATEGORY_TTL[mc]}d)")
        print()


def print_research_queue():
    """Output a prioritized re-research queue."""
    docs = get_all_metadata()

    print(f"\n{'═'*70}")
    print(f"  📋 Re-Research Queue")
    print(f"{'═'*70}\n")

    now = datetime.now()

    # Priority 1: Stale items
    stale = [d for d in docs if d["status"] == "STALE"]
    # Priority 2: Expiring soon
    expiring = [d for d in docs if d["status"] == "EXPIRING_SOON"]

    # Build queue by area → categories needing refresh
    queue = defaultdict(lambda: {"stale_cats": set(), "expiring_cats": set(), "stale_items": [], "expiring_items": []})

    for d in stale:
        area = d["area"]
        queue[area]["stale_cats"].add(d["category"])
        queue[area]["stale_items"].append(d)

    for d in expiring:
        area = d["area"]
        queue[area]["expiring_cats"].add(d["category"])
        queue[area]["expiring_items"].append(d)

    # Areas with no coverage at all
    property_areas = get_property_areas()
    kb_areas = get_kb_areas()
    uncovered_areas = []
    for pa in sorted(property_areas):
        pa_norm = normalize_area(pa)
        matched = False
        for ka in kb_areas:
            ka_norm = normalize_area(ka)
            if pa_norm == ka_norm or pa == ka or pa_norm in ka_norm or ka_norm in pa_norm:
                matched = True
                break
        if not matched:
            uncovered_areas.append(pa)

    # Output
    if stale:
        print(f"  🔴 Priority 1 — Stale ({len(stale)} items across {len([a for a,q in queue.items() if q['stale_cats']])} areas):")
        for area in sorted(queue.keys()):
            q = queue[area]
            if not q["stale_cats"]:
                continue
            cats = ", ".join(sorted(q["stale_cats"]))
            print(f"    📍 {area} → {cats}")
            for d in sorted(q["stale_items"], key=lambda x: x["days_remaining"] or 0):
                days_over = abs(d["days_remaining"]) if d["days_remaining"] is not None else "?"
                print(f"       [{d['category']}] {d['summary'][:60]}...")
                print(f"         Expired {days_over}d ago | Source to re-search: {d['source']}")
        print()

    if expiring:
        print(f"  🟡 Priority 2 — Expiring Soon ({len(expiring)} items):")
        for area in sorted(queue.keys()):
            q = queue[area]
            if not q["expiring_cats"]:
                continue
            cats = ", ".join(sorted(q["expiring_cats"]))
            print(f"    📍 {area} → {cats}")
            for d in sorted(q["expiring_items"], key=lambda x: x["days_remaining"] or 0):
                print(f"       [{d['category']}] expires in {d['days_remaining']:.0f}d — {d['summary'][:50]}...")
        print()

    if uncovered_areas:
        print(f"  🔵 Priority 3 — Areas with NPA properties but NO KB coverage ({len(uncovered_areas)}):")
        for u in uncovered_areas[:30]:
            print(f"    📍 {u} → needs: pricing, rental, area, flood")
        if len(uncovered_areas) > 30:
            print(f"    ... and {len(uncovered_areas) - 30} more areas")
        print()

    # Summary actions
    print(f"  {DIVIDER}")
    print(f"  📊 Summary of re-research actions needed:")
    print(f"     Stale items to refresh:    {len(stale)}")
    print(f"     Items expiring soon:        {len(expiring)}")
    print(f"     Areas needing first scan:   {len(uncovered_areas)}")

    # Recommended research commands
    if stale or expiring or uncovered_areas:
        print(f"\n  🛠️  Suggested kb_tools calls to re-research:")
        for area in sorted(queue.keys())[:5]:
            q = queue[area]
            all_cats = q["stale_cats"] | q["expiring_cats"]
            for cat in sorted(all_cats):
                print(f'     insert_document(content="...", category="{cat}", area="{area}", source="web_search")')
        for u in uncovered_areas[:3]:
            print(f'     # Area scan needed: "{u}" — research pricing, rental, area, flood')
        print()


# ─── Main ────────────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        description="NPA KB Freshness Checker — reports stale/expiring docs and coverage gaps"
    )
    parser.add_argument(
        "--stale", action="store_true",
        help="Show only stale and expiring-soon documents"
    )
    parser.add_argument(
        "--area", type=str, default="",
        help="Filter to a specific area (e.g. 'อ่อนนุช', 'บางเขน')"
    )
    parser.add_argument(
        "--queue", action="store_true",
        help="Output a prioritized re-research queue"
    )
    args = parser.parse_args()

    # Quick connectivity check
    test = psql_one("SELECT COUNT(*) FROM kb_metadata;")
    if test is None:
        print("❌ Cannot connect to npa_kb database or kb_metadata table is missing.")
        print("   Check that PostgreSQL is running and the npa_kb database exists.")
        sys.exit(1)

    if args.queue:
        print_research_queue()
    elif args.stale:
        print_stale_only(args.area)
    elif args.area:
        print_area_report(args.area)
    else:
        print_full_report(args.area)


if __name__ == "__main__":
    main()

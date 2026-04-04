"""
KBank NPA Scraper — Detail page enrichment via Camoufox.

Fetches detail pages for selected properties and extracts:
  - Title deed number (โฉนดเลขที่)
  - Full address
  - Nearby places with distances

Uses Camoufox headless=True to bypass Akamai Bot Manager.

Usage:
    python detail.py --ids 028818655,058803725    # specific properties
    python detail.py --enrich-all                  # all un-enriched properties
    python detail.py --enrich-all --limit 50       # first 50 un-enriched
"""

import argparse
import asyncio
import json
import re
from datetime import datetime, timezone

from camoufox.async_api import AsyncCamoufox
from selectolax.parser import HTMLParser
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_engine
from models import KbankProperty

DETAIL_BASE = "https://www.kasikornbank.com/th/propertyforsale/detail"
SEARCH_URL = "https://www.kasikornbank.com/th/propertyforsale/search/pages/index.aspx"
PAGE_DELAY = 3  # seconds between detail page fetches


def parse_detail_html(html: str) -> dict:
    """Extract deed, address, nearby places from detail page HTML."""
    tree = HTMLParser(html)
    result: dict = {}

    # Full address
    addr_node = tree.css_first(".location-container p")
    if addr_node:
        result["full_address"] = addr_node.text(strip=True)

    # Title deed from property-info rows
    for row in tree.css(".property-info .property-row, .property-table .property-row"):
        cells = row.css(".property-td")
        if len(cells) < 2:
            continue
        label = cells[0].text(strip=True)
        value = cells[1].text(strip=True)
        if "ประเภท" in label and "เอกสารสิทธิ์" in label:
            result["deed_type"] = value
        elif "เลขที่" in label and "เอกสารสิทธิ์" in label:
            result["deed_number"] = value

    # Fallback regex for deed number
    if "deed_number" not in result:
        deed_match = re.search(r'โฉนด[เลขที่\s]*?(\d+)', html)
        if deed_match:
            result["deed_number"] = deed_match.group(1)

    # Nearby places
    nearby: list[dict] = []
    for tr in tree.css(".place-nearby table tbody tr, .place-nearby table tr"):
        cells = tr.css("td")
        if len(cells) < 2:
            continue
        name_node = cells[0].css_first("span.list")
        name = name_node.text(strip=True) if name_node else cells[0].text(strip=True)
        distance = cells[1].text(strip=True)
        if name and distance:
            nearby.append({"name": name, "distance": distance})
    if nearby:
        result["nearby_places"] = nearby

    return result


async def enrich_properties(property_ids: list[str]) -> dict[str, dict]:
    """Fetch detail pages for given property IDs and return parsed data."""
    results: dict[str, dict] = {}

    if not property_ids:
        print("[detail] No properties to enrich.")
        return results

    print(f"[detail] Enriching {len(property_ids)} properties via Camoufox...")

    async with AsyncCamoufox(headless=True, humanize=True) as browser:
        page = await browser.new_page()

        # Establish session
        print("[detail] Establishing session...")
        await page.goto(SEARCH_URL, wait_until="domcontentloaded")
        await page.wait_for_timeout(3000)

        for i, prop_id in enumerate(property_ids):
            url = f"{DETAIL_BASE}/{prop_id}.html"
            print(f"  [{i + 1}/{len(property_ids)}] {prop_id}...", end=" ")

            try:
                await page.goto(url, wait_until="networkidle")
                await page.wait_for_timeout(3000)
                html = await page.content()

                if len(html) < 10000:
                    print("BLOCKED (Akamai)")
                    continue

                data = parse_detail_html(html)
                results[prop_id] = data
                print(
                    f"OK — addr={'Y' if 'full_address' in data else 'N'} "
                    f"deed={'Y' if 'deed_number' in data else 'N'} "
                    f"nearby={len(data.get('nearby_places', []))}"
                )
            except Exception as e:
                print(f"ERROR: {e}")

            if i < len(property_ids) - 1:
                await asyncio.sleep(PAGE_DELAY)

    return results


def save_enrichment(engine, results: dict[str, dict]) -> int:
    """Update DB rows with detail page data."""
    updated = 0
    now = datetime.now(timezone.utc)

    with Session(engine) as session:
        for prop_id, data in results.items():
            stmt = select(KbankProperty).where(KbankProperty.property_id == prop_id)
            prop = session.execute(stmt).scalar_one_or_none()
            if not prop:
                continue

            if "full_address" in data:
                prop.full_address = data["full_address"]
            if "deed_type" in data:
                prop.deed_type = data["deed_type"]
            if "deed_number" in data:
                prop.deed_number = data["deed_number"]
            if "nearby_places" in data:
                prop.nearby_places = data["nearby_places"]

            prop.has_detail = True
            prop.detail_scraped_at = now
            updated += 1

        session.commit()

    return updated


def get_unenriched_ids(engine, limit: int | None = None) -> list[str]:
    """Get property IDs that haven't been enriched yet."""
    with Session(engine) as session:
        stmt = (
            select(KbankProperty.property_id)
            .where(KbankProperty.has_detail == False)
            .order_by(KbankProperty.sell_price.desc())
        )
        if limit:
            stmt = stmt.limit(limit)
        return [row[0] for row in session.execute(stmt).all()]


async def run(ids: list[str] | None = None, enrich_all: bool = False, limit: int | None = None):
    engine = get_engine()

    if enrich_all:
        ids = get_unenriched_ids(engine, limit)
        print(f"[detail] Found {len(ids)} un-enriched properties")

    if not ids:
        print("[detail] Nothing to enrich.")
        return

    results = await enrich_properties(ids)

    if results:
        updated = save_enrichment(engine, results)
        print(f"\n[detail] Updated {updated} properties in DB")
    else:
        print("\n[detail] No results to save")


def main():
    parser = argparse.ArgumentParser(description="KBank NPA Detail Enrichment")
    parser.add_argument("--ids", help="Comma-separated property IDs")
    parser.add_argument("--enrich-all", action="store_true", help="Enrich all un-enriched")
    parser.add_argument("--limit", type=int, help="Max properties to enrich")
    args = parser.parse_args()

    ids = args.ids.split(",") if args.ids else None

    asyncio.run(run(ids=ids, enrich_all=args.enrich_all, limit=args.limit))


if __name__ == "__main__":
    main()

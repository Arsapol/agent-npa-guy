"""
KBank NPA Scraper — List API paginator with PostgreSQL upsert.

Scrapes all NPA properties from KBank's GetProperties endpoint,
upserts into PostgreSQL, and tracks price/status changes.

Architecture:
  - Sequential paginator (268 pages × 50 items = 13,361 properties)
  - Sliding window rate limiter (20 req/60s)
  - ASP.NET double JSON parse: {"d": "<json>"} → parse inner string
  - DB upsert in batches of 500

Usage:
    python scraper.py                           # full scrape
    python scraper.py --province 10             # BKK only (province ID)
    python scraper.py --type 05                 # condos only
    python scraper.py --limit 100               # first N items (test)
    python scraper.py --create-tables           # create DB tables only
"""

import argparse
import asyncio
import json
import time
from datetime import datetime, timezone

import httpx
from sqlalchemy.orm import Session

from database import create_tables, get_engine, upsert_properties
from models import KbankListResponse, KbankPropertyItem, KbankScrapeLog

LIST_URL = "https://www.kasikornbank.com/Custom/KWEB2020/NPA2023Backend13.aspx/GetProperties"

HEADERS = {
    "Content-Type": "application/json",
    "Accept": "*/*",
    "X-Requested-With": "XMLHttpRequest",
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/146.0.0.0 Safari/537.36"
    ),
    "Referer": "https://www.kasikornbank.com/th/propertyforsale/search/pages/index.aspx",
    "Origin": "https://www.kasikornbank.com",
}

PAGE_SIZE = 50
BATCH_SIZE = 500

# Rate limiter defaults
RATE_LIMIT_MAX = 20
RATE_LIMIT_WINDOW = 60.0


# ---------------------------------------------------------------------------
# Rate limiter
# ---------------------------------------------------------------------------


class SlidingWindowLimiter:
    """Sliding window rate limiter."""

    def __init__(self, max_requests: int, window_seconds: float):
        self._max = max_requests
        self._window = window_seconds
        self._timestamps: list[float] = []

    async def acquire(self) -> None:
        now = time.monotonic()
        cutoff = now - self._window
        self._timestamps = [t for t in self._timestamps if t > cutoff]
        if len(self._timestamps) >= self._max:
            wait = self._timestamps[0] - cutoff
            if wait > 0:
                await asyncio.sleep(wait)
        self._timestamps.append(time.monotonic())


# ---------------------------------------------------------------------------
# API client
# ---------------------------------------------------------------------------


async def fetch_page(
    client: httpx.AsyncClient,
    limiter: SlidingWindowLimiter,
    page: int,
    filter_extra: dict | None = None,
) -> tuple[list[dict], int]:
    """Fetch a single page from the list API. Returns (items, total_rows)."""
    await limiter.acquire()

    filter_obj: dict = {
        "PageSize": PAGE_SIZE,
        "CurrentPageIndex": page,
        "SearchPurposes": ["AllProperties"],
    }
    if filter_extra:
        filter_obj.update(filter_extra)

    try:
        r = await client.post(LIST_URL, headers=HEADERS, json={"filter": filter_obj})
        r.raise_for_status()
    except httpx.HTTPStatusError as e:
        print(f"  [page {page}] HTTP {e.response.status_code} — retrying in 10s...")
        await asyncio.sleep(10)
        r = await client.post(LIST_URL, headers=HEADERS, json={"filter": filter_obj})
        r.raise_for_status()

    # Double JSON parse (ASP.NET wrapper)
    inner = json.loads(r.text)["d"]
    data = json.loads(inner)

    if not data.get("Success"):
        raise ValueError(f"API returned Success=false: {data.get('ErrorMessage')}")

    items = data["Data"]["Items"]
    total = data["Data"]["TotalRows"]
    return items, total


# ---------------------------------------------------------------------------
# Main scraper
# ---------------------------------------------------------------------------


async def scrape(
    limit: int | None = None,
    filter_extra: dict | None = None,
    filter_label: str = "all",
) -> None:
    """Run the full scrape pipeline."""
    started_at = datetime.now(timezone.utc)
    engine = create_tables()
    limiter = SlidingWindowLimiter(RATE_LIMIT_MAX, RATE_LIMIT_WINDOW)

    all_items: list[dict] = []
    all_parsed: list[KbankPropertyItem] = []
    total_rows = 0
    failed_pages = 0

    async with httpx.AsyncClient(timeout=60.0) as client:
        # First page to get total
        print(f"[scraper] Starting KBank scrape (filter: {filter_label})...")
        items, total_rows = await fetch_page(client, limiter, 1, filter_extra)
        total_pages = (total_rows + PAGE_SIZE - 1) // PAGE_SIZE
        print(f"[scraper] Total: {total_rows} properties, {total_pages} pages")

        # Parse first page
        for raw in items:
            try:
                parsed = KbankPropertyItem.model_validate(raw)
                all_items.append(raw)
                all_parsed.append(parsed)
            except Exception as e:
                print(f"  [parse] Failed: {e}")

        # Remaining pages
        for page in range(2, total_pages + 1):
            if limit and len(all_parsed) >= limit:
                print(f"[scraper] Reached limit ({limit}), stopping.")
                break

            try:
                items, _ = await fetch_page(client, limiter, page, filter_extra)
            except Exception as e:
                print(f"  [page {page}] FAILED: {e}")
                failed_pages += 1
                continue

            for raw in items:
                if limit and len(all_parsed) >= limit:
                    break
                try:
                    parsed = KbankPropertyItem.model_validate(raw)
                    all_items.append(raw)
                    all_parsed.append(parsed)
                except Exception as e:
                    print(f"  [parse] Failed: {e}")

            if page % 10 == 0:
                print(f"  [page {page}/{total_pages}] {len(all_parsed)} items collected")

            # Batch upsert every BATCH_SIZE items
            if len(all_parsed) >= BATCH_SIZE:
                _flush_batch(engine, all_parsed, all_items)
                all_parsed.clear()
                all_items.clear()

    # Final flush
    if all_parsed:
        _flush_batch(engine, all_parsed, all_items)

    # Log scrape run
    finished_at = datetime.now(timezone.utc)
    with Session(engine) as session:
        log = KbankScrapeLog(
            started_at=started_at,
            finished_at=finished_at,
            total_api=total_rows,
            total_pages=total_pages,
            failed_pages=failed_pages,
            filter_used=filter_label,
        )
        session.add(log)
        session.commit()

    elapsed = (finished_at - started_at).total_seconds()
    print(f"\n[scraper] Done in {elapsed:.1f}s")


def _flush_batch(engine, parsed: list[KbankPropertyItem], raw: list[dict]) -> None:
    """Upsert a batch to the database."""
    with Session(engine) as session:
        counts = upsert_properties(session, parsed, raw)
        session.commit()
    print(
        f"  [db] new={counts['new']} updated={counts['updated']} "
        f"price_changed={counts['price_changed']} status_changed={counts['status_changed']}"
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(description="KBank NPA Scraper")
    parser.add_argument("--limit", type=int, help="Max items to scrape (for testing)")
    parser.add_argument("--province", type=int, nargs="+", help="Province ID(s) (e.g. 10 20 50)")
    parser.add_argument("--type", dest="prop_type", help="Property type code (e.g. 05=condo)")
    parser.add_argument("--min-price", type=int, help="Min price filter (baht)")
    parser.add_argument("--max-price", type=int, help="Max price filter (baht)")
    parser.add_argument("--create-tables", action="store_true", help="Create tables only")
    args = parser.parse_args()

    if args.create_tables:
        create_tables()
        return

    filter_extra: dict = {}
    label_parts: list[str] = []

    if args.province:
        filter_extra["Provinces"] = args.province
        label_parts.append(f"provinces={args.province}")
    if args.prop_type:
        filter_extra["PropertyTypes"] = [args.prop_type]
        label_parts.append(f"type={args.prop_type}")
    if args.min_price:
        filter_extra["MinPrice"] = args.min_price
        label_parts.append(f"min={args.min_price}")
    if args.max_price:
        filter_extra["MaxPrice"] = args.max_price
        label_parts.append(f"max={args.max_price}")

    filter_label = ", ".join(label_parts) if label_parts else "all"

    asyncio.run(scrape(
        limit=args.limit,
        filter_extra=filter_extra if filter_extra else None,
        filter_label=filter_label,
    ))


if __name__ == "__main__":
    main()

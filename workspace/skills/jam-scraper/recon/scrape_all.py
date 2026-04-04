"""
JAM Full Scrape — dump all properties to JSON for analysis.

Features:
- Retry with exponential backoff on failures
- Resume from checkpoint (saves progress every batch)
- Gentle pacing to avoid rate limits
- Saves partial results so nothing is lost
"""

import asyncio
import json
import time
from datetime import datetime
from pathlib import Path

import httpx
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

KEY = b"QWT9g38M6fwBzJcbCjRjIBqn97UBm1Cf"
BASE_URL = "https://www.jjpropertythai.com/api/proxy/v1"
OUTPUT_DIR = Path(__file__).parent / "data"

HEADERS = {
    "Accept": "application/json",
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Referer": "https://www.jjpropertythai.com/Search",
}

SALE_TYPES = {"1": "ขายสด", "2": "ผ่อนชำระ", "3": "ประมูล"}

# Checkpoint file for resume
CHECKPOINT_FILE = OUTPUT_DIR / "checkpoint.json"


def decrypt(encrypted_str: str) -> dict:
    parts = encrypted_str.split(":")
    if len(parts) != 3:
        raise ValueError(f"Expected 3 parts, got {len(parts)}")
    iv = bytes.fromhex(parts[0])
    tag = bytes.fromhex(parts[1])
    ciphertext = bytes.fromhex(parts[2])
    return json.loads(AESGCM(KEY).decrypt(iv, ciphertext + tag, None).decode("utf-8"))


def decrypt_response(data: dict) -> dict:
    if "_encrypted" in data:
        return decrypt(data["_encrypted"])
    return data


async def fetch_with_retry(
    client: httpx.AsyncClient,
    url: str,
    params: dict,
    max_retries: int = 3,
    base_delay: float = 2.0,
) -> dict | None:
    """Fetch with exponential backoff retry."""
    for attempt in range(max_retries):
        try:
            resp = await client.get(url, params=params, headers=HEADERS)
            resp.raise_for_status()
            return decrypt_response(resp.json())
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                delay = base_delay * (2 ** attempt) + 1
                print(f"    Rate limited, waiting {delay:.0f}s...")
                await asyncio.sleep(delay)
            elif e.response.status_code >= 500:
                delay = base_delay * (2 ** attempt)
                print(f"    Server error {e.response.status_code}, retry in {delay:.0f}s...")
                await asyncio.sleep(delay)
            else:
                print(f"    HTTP {e.response.status_code} for {url}")
                return None
        except (httpx.ReadTimeout, httpx.ConnectTimeout):
            delay = base_delay * (2 ** attempt)
            print(f"    Timeout, retry in {delay:.0f}s...")
            await asyncio.sleep(delay)
        except Exception as e:
            delay = base_delay * (2 ** attempt)
            print(f"    Error: {e}, retry in {delay:.0f}s...")
            await asyncio.sleep(delay)
    print(f"    FAILED after {max_retries} retries")
    return None


async def init_session(client: httpx.AsyncClient):
    """Visit homepage to acquire cookiesession1 — required for API access."""
    resp = await client.get("https://www.jjpropertythai.com/", headers=HEADERS)
    print(f"  Session cookie: {dict(client.cookies)}")
    return resp.status_code == 200


async def fetch_page(client: httpx.AsyncClient, page: int, limit: int = 50) -> dict | None:
    params = {
        "freeText": "",
        "page": page,
        "user_code": "521789",
        "limit": limit,
        "SellingStart": 0,
        "SellingEnd": 100000000,
        "isNearby": "",
        "lon": "",
        "lat": "",
    }
    return await fetch_with_retry(client, f"{BASE_URL}/assets", params)


async def fetch_dropdowns(client: httpx.AsyncClient) -> dict:
    dropdowns = {}
    for name in ["company", "typeAsset", "typeSell", "province"]:
        result = await fetch_with_retry(client, f"{BASE_URL}/dropdown/{name}", {})
        if result:
            dropdowns[name] = result
            count = len(result) if isinstance(result, list) else "object"
            print(f"  {name}: {count}")
    return dropdowns


def save_checkpoint(properties: list[dict], last_page: int, total_pages: int, failed_pages: list[int]):
    CHECKPOINT_FILE.write_text(json.dumps({
        "last_page": last_page,
        "total_pages": total_pages,
        "total_collected": len(properties),
        "failed_pages": failed_pages,
        "timestamp": datetime.now().isoformat(),
    }, indent=2), encoding="utf-8")

    # Also save partial results
    partial_path = OUTPUT_DIR / "partial_properties.json"
    partial_path.write_text(json.dumps(properties, ensure_ascii=False), encoding="utf-8")


def load_checkpoint() -> tuple[list[dict], int, list[int]] | None:
    if not CHECKPOINT_FILE.exists():
        return None
    partial_path = OUTPUT_DIR / "partial_properties.json"
    if not partial_path.exists():
        return None

    cp = json.loads(CHECKPOINT_FILE.read_text())
    properties = json.loads(partial_path.read_text())
    print(f"  Resuming from page {cp['last_page']}, {len(properties)} properties collected")
    return properties, cp["last_page"], cp.get("failed_pages", [])


async def scrape_all_properties() -> list[dict]:
    all_properties = []
    seen_ids = set()
    failed_pages = []
    start_page = 1
    limit = 50

    # Try to resume from checkpoint
    checkpoint = load_checkpoint()
    if checkpoint:
        all_properties, start_page, failed_pages = checkpoint
        seen_ids = {p["Asset_ID"] for p in all_properties if "Asset_ID" in p}
        start_page += 1
        print(f"  Resumed: {len(all_properties)} properties, continuing from page {start_page}")

    async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
        # Acquire session cookie first
        await init_session(client)

        # Get total count from first page (can be slow ~30s on first hit)
        print("  Fetching page 1 (first request is slow, ~30s)...")
        t0 = time.time()
        result = await fetch_page(client, page=1, limit=limit)
        if not result:
            print("  Failed to fetch first page!")
            return all_properties

        print(f"  Page 1 fetched in {time.time() - t0:.1f}s")
        total = result.get("count", 0)
        total_pages = (total + limit - 1) // limit
        print(f"  Total: {total:,} properties, {total_pages} pages")

        # Process first page (unless resuming past it)
        if start_page <= 1:
            for item in result.get("data", []):
                aid = item.get("Asset_ID")
                if aid and aid not in seen_ids:
                    seen_ids.add(aid)
                    all_properties.append(item)
            start_page = 2

        # Sequential pagination — one page at a time
        for p in range(start_page, total_pages + 1):
            t0 = time.time()
            r = await fetch_page(client, page=p, limit=limit)
            elapsed = time.time() - t0

            if r:
                new = 0
                for item in r.get("data", []):
                    aid = item.get("Asset_ID")
                    if aid and aid not in seen_ids:
                        seen_ids.add(aid)
                        all_properties.append(item)
                        new += 1
                print(f"    Page {p}/{total_pages}: +{new} → {len(all_properties):,} total ({elapsed:.1f}s)")
            else:
                failed_pages.append(p)
                print(f"    Page {p}/{total_pages}: FAILED ({elapsed:.1f}s) [{len(failed_pages)} total fails]")

            if p % 50 == 0:
                save_checkpoint(all_properties, p, total_pages, failed_pages)
                print(f"    --- checkpoint saved ---")

            await asyncio.sleep(0.5)

        # Retry failed pages
        if failed_pages:
            print(f"\n  Retrying {len(failed_pages)} failed pages...")
            still_failed = []
            for p in failed_pages:
                await asyncio.sleep(2.0)
                r = await fetch_page(client, page=p, limit=limit)
                if r:
                    for item in r.get("data", []):
                        aid = item.get("Asset_ID")
                        if aid and aid not in seen_ids:
                            seen_ids.add(aid)
                            all_properties.append(item)
                    print(f"    Page {p}: recovered")
                else:
                    still_failed.append(p)
                    print(f"    Page {p}: still failed")
            failed_pages = still_failed

        if failed_pages:
            print(f"  {len(failed_pages)} pages permanently failed: {failed_pages[:20]}")

    return all_properties


async def fetch_sample_details(properties: list[dict], sample_size: int = 10) -> list[dict]:
    sample_ids = [p["Asset_ID"] for p in properties[:sample_size]]
    details = []

    async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
        await init_session(client)
        for aid in sample_ids:
            result = await fetch_with_retry(
                client,
                f"{BASE_URL}/assets/{aid}",
                {"user_code": "521789"},
            )
            if result:
                details.append(result)
            await asyncio.sleep(1.0)

    return details


def analyze(properties: list[dict]):
    n = len(properties)
    if n == 0:
        print("No properties to analyze")
        return

    print(f"\n{'='*60}")
    print(f"ANALYSIS: {n:,} properties")
    print(f"{'='*60}")

    # All field names
    all_keys = set()
    for p in properties:
        all_keys.update(p.keys())
    print(f"\nTotal fields: {len(all_keys)}")

    # Null rates
    key_fields = [
        "Asset_ID", "Selling", "Discount", "Rental",
        "Lat", "Lon", "Province", "District", "SubDistrict",
        "Wah", "Meter", "Bedroom", "Bathroom",
        "Status_Soldout", "Soldout_date", "Status_Acution",
        "Type_Asset_Code", "Type_Sale_Code", "Company_Code",
        "Save_date", "Update_date", "Images_Main_Web",
    ]
    print(f"\nNull/empty rates:")
    for field in key_fields:
        nulls = sum(1 for p in properties if not p.get(field))
        print(f"  {field:25s}: {nulls:6d}/{n} ({nulls/n*100:5.1f}%)")

    # Sale type distribution
    print("\nSale type (Type_Sale_Code):")
    counts = {}
    for p in properties:
        code = str(p.get("Type_Sale_Code", "?"))
        label = SALE_TYPES.get(code, f"unknown({code})")
        counts[label] = counts.get(label, 0) + 1
    for k, v in sorted(counts.items(), key=lambda x: -x[1]):
        print(f"  {k}: {v:,}")

    # Asset type distribution
    print("\nAsset type (Type_Asset_TH):")
    counts = {}
    for p in properties:
        counts[p.get("Type_Asset_TH", "?")] = counts.get(p.get("Type_Asset_TH", "?"), 0) + 1
    for k, v in sorted(counts.items(), key=lambda x: -x[1]):
        print(f"  {k}: {v:,}")

    # Province top 15
    print("\nTop 15 provinces:")
    counts = {}
    for p in properties:
        counts[p.get("PROVINCE_NAME", "?")] = counts.get(p.get("PROVINCE_NAME", "?"), 0) + 1
    for k, v in sorted(counts.items(), key=lambda x: -x[1])[:15]:
        print(f"  {k}: {v:,}")

    # Soldout
    soldout = [p for p in properties if p.get("Status_Soldout")]
    print(f"\nSold out: {len(soldout):,} / {n:,} ({len(soldout)/n*100:.1f}%)")
    if soldout:
        dates = [p.get("Soldout_date") for p in soldout if p.get("Soldout_date")]
        if dates:
            print(f"  Earliest: {min(dates)}")
            print(f"  Latest:   {max(dates)}")

    # Prices
    selling = [p["Selling"] for p in properties if p.get("Selling") and p["Selling"] > 0]
    if selling:
        selling.sort()
        print(f"\nSelling price ({len(selling):,} with price):")
        print(f"  Min:    {selling[0]:>15,.0f} baht")
        print(f"  Q1:     {selling[len(selling)//4]:>15,.0f} baht")
        print(f"  Median: {selling[len(selling)//2]:>15,.0f} baht")
        print(f"  Q3:     {selling[3*len(selling)//4]:>15,.0f} baht")
        print(f"  Max:    {selling[-1]:>15,.0f} baht")

    discount = [p["Discount"] for p in properties if p.get("Discount") and p["Discount"] > 0]
    if discount:
        discount.sort()
        print(f"\nDiscount price ({len(discount):,} with discount):")
        print(f"  Min:    {discount[0]:>15,.0f} baht")
        print(f"  Median: {discount[len(discount)//2]:>15,.0f} baht")
        print(f"  Max:    {discount[-1]:>15,.0f} baht")

    # Discount % distribution
    both = [(p["Selling"], p["Discount"]) for p in properties
            if p.get("Selling") and p["Selling"] > 0 and p.get("Discount") and p["Discount"] > 0]
    if both:
        discounts_pct = [(1 - d/s) * 100 for s, d in both if s > 0]
        discounts_pct.sort()
        print(f"\nDiscount % (off selling price, {len(discounts_pct):,} properties):")
        print(f"  Min:    {discounts_pct[0]:>6.1f}%")
        print(f"  Median: {discounts_pct[len(discounts_pct)//2]:>6.1f}%")
        print(f"  Max:    {discounts_pct[-1]:>6.1f}%")

    # Company distribution
    print("\nCompanies:")
    counts = {}
    for p in properties:
        counts[p.get("Company_TH", "?")] = counts.get(p.get("Company_TH", "?"), 0) + 1
    for k, v in sorted(counts.items(), key=lambda x: -x[1]):
        print(f"  {k}: {v:,}")


async def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    start = time.time()

    print("=== JAM Full Scrape ===\n")

    # Step 1: Dropdowns
    print("1. Fetching dropdowns...")
    async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
        await init_session(client)
        dropdowns = await fetch_dropdowns(client)
    (OUTPUT_DIR / "dropdowns.json").write_text(
        json.dumps(dropdowns, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    # Step 2: All properties
    print("\n2. Scraping all properties...")
    properties = await scrape_all_properties()
    print(f"\n   Total unique: {len(properties):,}")

    # Save final
    final_path = OUTPUT_DIR / f"all_properties_{timestamp}.json"
    final_path.write_text(json.dumps(properties, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"   Saved to {final_path.name}")

    # Step 3: Sample details
    print("\n3. Fetching 10 sample detail pages...")
    details = await fetch_sample_details(properties, sample_size=10)
    (OUTPUT_DIR / f"sample_details_{timestamp}.json").write_text(
        json.dumps(details, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"   Got {len(details)} details")

    # Step 4: Analysis
    analyze(properties)

    elapsed = time.time() - start
    print(f"\nCompleted in {elapsed:.0f}s ({elapsed/60:.1f}m)")
    print(f"Data in: {OUTPUT_DIR}")

    # Cleanup checkpoint
    if CHECKPOINT_FILE.exists():
        CHECKPOINT_FILE.unlink()
    partial = OUTPUT_DIR / "partial_properties.json"
    if partial.exists():
        partial.unlink()


if __name__ == "__main__":
    asyncio.run(main())

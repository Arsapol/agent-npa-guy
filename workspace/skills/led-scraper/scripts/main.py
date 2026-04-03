#!/usr/bin/env python3
"""
Production HTTP-based LED Property Extraction
Optimized for full-scale extraction with progress tracking and error handling
Integrated with Turso database for direct import
"""

import argparse
import asyncio
import json
import re
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from curl_cffi.requests import AsyncSession
from dotenv import load_dotenv
from selectolax.parser import HTMLParser

from config import AGENCIES as VALID_AGENCIES

# Database integration (optional - will gracefully handle if not available)
try:
    from database import PropertyDatabase

    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False
    print(
        "⚠️  Database module not available. Install requirements: pip install -r requirements.txt"
    )

load_dotenv()


def convert_thai_price_to_number(price_str: str) -> Optional[float]:
    """Convert Thai price string to numeric value"""
    if not price_str or price_str == "ไม่มี":
        return None
    try:
        cleaned_price = price_str.replace(",", "")
        return float(cleaned_price)
    except (ValueError, AttributeError):
        return None


def convert_be_to_ce_date(thai_date_str: str) -> Dict[str, str]:
    """Convert Buddhist Era date to Christian Era"""
    if not thai_date_str or "/" not in thai_date_str:
        return {"be_date": thai_date_str, "ce_date": None, "ce_year": None}
    try:
        day, month, be_year = thai_date_str.split("/")
        ce_year = int(be_year) - 543
        ce_date = f"{day}/{month}/{ce_year}"
        return {"be_date": thai_date_str, "ce_date": ce_date, "ce_year": ce_year}
    except (ValueError, IndexError):
        return {"be_date": thai_date_str, "ce_date": None, "ce_year": None}


def convert_issale_to_status(issale_value: str) -> str:
    """Convert issale value to human-readable status text"""
    if not issale_value or issale_value.strip() == "":
        return "scheduled"

    status_map = {
        "1": "ขายแล้ว",
        "0": "ยังไม่ขาย",
        "3": "งดขายไม่มีผู้สู้ราคา",
        "6": "ถอนการยึด",
        "10": "งดขาย",
    }

    return status_map.get(issale_value, issale_value)


def determine_sale_status(issale_values: List[str]) -> tuple[str, Optional[int]]:
    """Determine overall sale status from issale1-8 values and return (status, latest_auction_number)"""
    # Priority order: sold (1) > withdrawn (6) > not sold yet (0) > cancelled no bidders (3) > cancelled (10)

    # Track found statuses with priority levels
    priority = {
        "1": (1, "ขายแล้ว"),
        "6": (2, "ถอนการยึด"),
        "0": (3, "ยังไม่ขาย"),
        "3": (4, "งดขายไม่มีผู้สู้ราคา"),
        "10": (5, "งดขาย"),
    }

    highest_priority = float("inf")
    status = "unknown"
    latest_auction_number = None
    first_unknown = None
    first_unknown_index = None

    # Single pass through the list with index tracking
    # For same priority, keep the LATEST (highest) auction number
    for index, value in enumerate(issale_values, start=1):
        if value in priority:
            prio, label = priority[value]
            if prio < highest_priority:
                # Found higher priority status
                highest_priority = prio
                status = label
                latest_auction_number = index
            elif prio == highest_priority:
                # Same priority - keep the latest (higher) auction number
                latest_auction_number = index
        elif value and value.strip() and first_unknown is None:
            first_unknown = value
            first_unknown_index = index

    # Return highest priority status found, or first unknown value, or "unknown"
    if highest_priority != float("inf"):
        return status, latest_auction_number
    elif first_unknown:
        return first_unknown, first_unknown_index
    else:
        return "unknown", None


def extract_captcha_code(html_content: str) -> Optional[str]:
    """Extract captcha code from HTML"""
    try:
        # Look for captcha code in blue color font (nested font tags)
        blue_captcha_pattern = r"รหัสยืนยัน[^<]*<font[^>]*><font[^>]*color[^>]*blue[^>]*>(\d{4,6})</font></font>"
        match = re.search(blue_captcha_pattern, html_content, re.IGNORECASE)
        if match:
            return match.group(1)

        # Fallback: Look in lines with รหัสยืนยัน
        lines = html_content.split("\n")
        for line in lines:
            if "รหัสยืนยัน" in line and "color" in line.lower() and "blue" in line.lower():
                numbers = re.findall(r"\b\d{4,6}\b", line)
                for num in numbers:
                    if num != "424242":
                        return num

        return None

    except Exception as e:
        print(f"❌ Error extracting captcha: {e}")
        return None


def extract_hidden_form_data(html_content: str) -> List[Dict[str, Any]]:
    """Extract all hidden form data from search results"""
    tree = HTMLParser(html_content)
    forms = tree.css('form[action*="asset_open"]')

    properties = []

    for form in forms:
        hidden_inputs = form.css('input[type="hidden"]')
        property_data = {}

        for input_field in hidden_inputs:
            name = input_field.attributes.get("name")
            value = input_field.attributes.get("value", "")
            if name:
                property_data[name] = value

        if property_data:
            processed_property = process_hidden_form_data(property_data)
            properties.append(processed_property)

    return properties


def process_hidden_form_data(form_data: Dict[str, str]) -> Dict[str, Any]:
    """Process raw hidden form data into structured property information"""
    property_detail = {
        "extraction_success": True,
        "error": "",
        # Basic identifiers
        "lot_number": form_data.get("str_bid_num", ""),
        "asset_id": form_data.get("auc_asset_gen", ""),
        # Case information
        "case_number": f"{form_data.get('law_suit_no', '')}/{form_data.get('law_suit_year', '')}"
        if form_data.get("law_suit_no")
        else "",
        "court": form_data.get("law_court_name", ""),
        # Parties
        "plaintiff": form_data.get("person1", ""),
        "defendant": form_data.get("person2", ""),
        "property_owner": form_data.get("ownername", ""),
        # Property details
        "property_type": form_data.get("assettypedesc", "").strip(),
        "address": form_data.get("addrno", ""),
        "tumbol": form_data.get("tumbol", "").replace("ตำบล", ""),
        "ampur": form_data.get("ampur", "").replace("อำเภอ", ""),
        "province": form_data.get("city", ""),
        # Land size
        "size_rai": form_data.get("rai", "0"),
        "size_ngan": form_data.get("quaterrai", "0"),
        "size_wa": form_data.get("wa", "0"),
        # Land title
        "deed_number": form_data.get("deedno", ""),
        "land_type": form_data.get("landtype", ""),
        # Price assessments (convert to numeric)
        "expert_appraisal_price": convert_thai_price_to_number(
            form_data.get("assetprice1", "0")
        )
        or None,
        "enforcement_officer_price": convert_thai_price_to_number(
            form_data.get("assetprice3", "0")
        )
        or None,
        "department_appraisal_price": convert_thai_price_to_number(
            form_data.get("assetprice2", "0")
        )
        or None,
        "committee_determined_price": convert_thai_price_to_number(
            form_data.get("assetprice4", "0")
        )
        or None,
        # Deposit and reserve amounts
        "deposit_amount": convert_thai_price_to_number(
            form_data.get("ReserveFund", "0")
        )
        or None,
        "reserve_fund_special": convert_thai_price_to_number(
            form_data.get("ReserveFund1", "0")
        )
        or None,
        # Sale information
        "sale_type": form_data.get("saletypename", ""),
        "sale_location": form_data.get("sale_location1", ""),
        "sale_time": form_data.get("sale_time1", ""),
        # Contact
        "contact_office": form_data.get("province_name", ""),
        "contact_phone": form_data.get("tel", ""),
        # Images and maps
        "land_picture": form_data.get("landpicture", ""),
        "map_picture": form_data.get("mapjot", ""),
        # Auction dates
        "auction_dates": [],
        # Additional fields
        "is_extra_pledge": form_data.get("is_extra_pledgb") == "T",
        "occupant": form_data.get("occupant", ""),
        "owner_suit_name": form_data.get("owner_suit_name", ""),
        "issue_date": form_data.get("ischeck_date", ""),
        "remark": form_data.get("remark", ""),
        "debtname": form_data.get("debtname", ""),
        "debtprice": convert_thai_price_to_number(form_data.get("debtprice", "0"))
        or None,
        "map": form_data.get("map", ""),
        "fbidnum": form_data.get("fbidnum", ""),
        "fbidnuml": form_data.get("fbidnuml", ""),
        "fsubbidnum": form_data.get("fsubbidnum", ""),
        "issale": form_data.get("issale", ""),
        "law_court_id": form_data.get("law_court_id", ""),
        "province_id": form_data.get("province_id", ""),
        "AssetTypeID": form_data.get("AssetTypeID", ""),
        "debtdetail": form_data.get("debtdetail", ""),
        "eauc": form_data.get("eauc", ""),
        "remark1": form_data.get("remark1", ""),
        "assetprice5": convert_thai_price_to_number(form_data.get("assetprice5", "0"))
        or None,
        "assetprice6": convert_thai_price_to_number(form_data.get("assetprice6", "0"))
        or None,
        "assetprice7": convert_thai_price_to_number(form_data.get("assetprice7", "0"))
        or None,
        "assetprice8": convert_thai_price_to_number(form_data.get("assetprice8", "0"))
        or None,
        "assetprice9": convert_thai_price_to_number(form_data.get("assetprice9", "0"))
        or None,
        "deedtumbol": form_data.get("deedtumbol", ""),
        "deedampur": form_data.get("deedampur", ""),
        "deedcity": form_data.get("deedcity", ""),
        "landdesc": form_data.get("landdesc", ""),
        "issale1": form_data.get("issale1", ""),
        "issale2": form_data.get("issale2", ""),
        "issale3": form_data.get("issale3", ""),
        "issale4": form_data.get("issale4", ""),
        "issale5": form_data.get("issale5", ""),
        "issale6": form_data.get("issale6", ""),
        "issale7": form_data.get("issale7", ""),
        "issale8": form_data.get("issale8", ""),
        "sale_location2": form_data.get("sale_location2", ""),
        "sale_time2": form_data.get("sale_time2", ""),
    }

    # Process auction dates
    for i in range(1, 9):
        date_field = f"biddate{i}"
        date_value = form_data.get(date_field, "")
        if date_value and date_value.strip():
            if len(date_value) == 8 and date_value.isdigit():
                formatted_date = (
                    f"{date_value[6:8]}/{date_value[4:6]}/{date_value[0:4]}"
                )
                date_info = convert_be_to_ce_date(formatted_date)
                # Get corresponding issale status
                issale_field = f"issale{i}"
                issale_value = form_data.get(issale_field, "")
                auction_status = convert_issale_to_status(issale_value)

                property_detail["auction_dates"].append(
                    {
                        "auction_number": i,
                        "date_be": date_info["be_date"],
                        "date_ce": date_info["ce_date"],
                        "status": auction_status,
                        "raw_date": date_value,
                        "issale_value": issale_value,
                    }
                )

    # Determine overall sale status and latest auction number
    issale_list = [
        form_data.get("issale1", ""),
        form_data.get("issale2", ""),
        form_data.get("issale3", ""),
        form_data.get("issale4", ""),
        form_data.get("issale5", ""),
        form_data.get("issale6", ""),
        form_data.get("issale7", ""),
        form_data.get("issale8", ""),
    ]

    # Get sale_status (highest priority status across all auctions)
    sale_status, _ = determine_sale_status(issale_list)
    property_detail["sale_status"] = sale_status

    # Get latest_auction_number: Find the next auction after the last non-"0" status
    # First priority statuses (completed auctions): "1", "3", "6", "10"
    # "0" means auction is scheduled but not sold yet (current/upcoming)

    last_completed_auction = 0
    for i in range(7, -1, -1):  # Iterate backwards from issale8 to issale1
        issale_value = issale_list[i]
        # Check if this is a completed auction (not "0" and not empty)
        if issale_value and issale_value.strip() and issale_value != "0":
            last_completed_auction = i + 1  # auction number (1-indexed)
            break

    # The next auction after the last completed one is the latest
    # Look for the next issale value that exists (not empty)
    latest_auction_number = None
    for i in range(last_completed_auction, 8):  # From next auction to issale8
        issale_value = issale_list[i]
        if issale_value and issale_value.strip():  # Has any value (including "0")
            latest_auction_number = i + 1
            break

    # If no next auction found, return None
    property_detail["latest_auction_number"] = latest_auction_number

    return property_detail


async def submit_search_form(
    session: AsyncSession, government_agency: str = "สงขลา"
) -> Optional[str]:
    """Submit search form to default.asp and return HTML response"""
    try:
        # Get initial page and extract captcha
        initial_response = await session.get(
            "https://asset.led.go.th/newbidreg/default.asp"
        )
        if initial_response.status_code != 200:
            return None

        initial_html = initial_response.content.decode("tis-620")
        captcha_code = extract_captcha_code(initial_html)

        if not captcha_code:
            return None

        # Submit search form
        search_data = {
            "region_name": government_agency,
            "province": "",
            "ampur": "",
            "tumbol": "",
            "asset_type": "",
            "person1": "",
            "bid_date": "",
            "price_begin": "",
            "price_end": "",
            "rai_if": "1",
            "rai": "",
            "quaterrai_if": "1",
            "quaterrai": "",
            "wa_if": "1",
            "wa": "",
            "seckey": captcha_code,
            "search": "ok",
        }

        from urllib.parse import urlencode

        encoded_data = urlencode(search_data, encoding="tis-620")

        response = await session.post(
            "https://asset.led.go.th/newbidreg/default.asp",
            data=encoded_data,
            headers={
                "Content-Type": "application/x-www-form-urlencoded; charset=tis-620",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            },
        )
        if response.status_code != 200:
            return None
        return response.content.decode("tis-620")

    except Exception as e:
        print(f"❌ Error in search form submission: {e}")
        return None


async def fetch_single_page(
    session: AsyncSession,
    page_num: int,
    government_agency: str,
) -> tuple[int, Optional[str]]:
    """Fetch a single page and return (page_number, html_content)"""
    try:
        page_data = {
            "page": str(page_num),
            "region_name": government_agency,
            "province": "",
            "ampur": "",
            "tumbol": "",
            "asset_type": "",
            "person1": "",
            "bid_date": "",
            "price_begin": "",
            "price_end": "",
            "rai_if": "1",
            "rai": "",
            "quaterrai_if": "1",
            "quaterrai": "",
            "wa_if": "1",
            "wa": "",
            "search": "ok",
        }

        from urllib.parse import urlencode

        encoded_data = urlencode(page_data, encoding="tis-620")

        response = await session.post(
            "https://asset.led.go.th/newbidreg/default.asp",
            data=encoded_data,
            headers={
                "Content-Type": "application/x-www-form-urlencoded; charset=tis-620",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            },
        )

        if response.status_code != 200:
            print(f"⚠️  Page {page_num}: HTTP {response.status_code}")
            return page_num, None

        return page_num, response.content.decode("tis-620")

    except Exception as e:
        print(f"❌ Error fetching page {page_num}: {e}")
        return page_num, None


async def extract_all_pages_production(
    session: AsyncSession,
    government_agency: str = "สงขลา",
    max_pages: int = 78,
    concurrent_pages: int = 10,
    deadline: Optional[float] = None,
) -> List[Dict[str, Any]]:
    """
    Production-grade multi-page extraction with concurrent batching and progress tracking
    """
    all_properties = []
    start_time = time.time()

    print(f"🚀 Starting production extraction for {government_agency}")
    print(f"📊 Target: Up to {max_pages} pages (batches of {concurrent_pages})")

    # Get first page
    print("🔍 Processing page 1...")
    first_page_html = await submit_search_form(session, government_agency)
    if not first_page_html:
        print("❌ Failed to get first page")
        return []

    # Extract from first page and determine total pages
    page_properties = extract_hidden_form_data(first_page_html)
    all_properties.extend(page_properties)

    tree = HTMLParser(first_page_html)
    page_info = None

    # Find text nodes containing pagination info
    if tree.body:
        for node in tree.body.traverse():
            if hasattr(node, "text"):
                text = node.text()
                if text and "หน้าที่" in text and re.search(r"\d+/\d+", text):
                    page_info = text
                    break

    total_pages = max_pages

    if page_info:
        total_pages_match = re.search(r"หน้าที่ (\d+)/(\d+)", page_info)
        if total_pages_match:
            total_pages = min(int(total_pages_match.group(2)), max_pages)

    print(f"✅ Page 1: {len(page_properties)} properties | Total pages: {total_pages}")

    # Process remaining pages in concurrent batches
    failed_pages = []
    consecutive_empty_batches = 0
    remaining_pages = list(range(2, total_pages + 1))

    # Process in batches
    for batch_start in range(0, len(remaining_pages), concurrent_pages):
        # Check deadline before starting each page batch
        if deadline is not None and time.time() > deadline:
            print(f"\n⏰ {government_agency}: Deadline reached, stopping page extraction early")
            print(f"   Collected {len(all_properties)} properties so far")
            break

        batch_end = min(batch_start + concurrent_pages, len(remaining_pages))
        current_batch = remaining_pages[batch_start:batch_end]

        # Progress tracking
        elapsed = time.time() - start_time
        completed_pages = batch_start + 1  # +1 for first page
        avg_time_per_page = elapsed / completed_pages if completed_pages > 0 else 0
        estimated_remaining = avg_time_per_page * (total_pages - completed_pages)

        print(
            f"\n🔄 Fetching batch: pages {current_batch[0]}-{current_batch[-1]} "
            f"({len(current_batch)} pages) | "
            f"Elapsed: {elapsed:.1f}s | ETA: {estimated_remaining:.1f}s"
        )

        # Fetch batch concurrently
        fetch_tasks = [
            fetch_single_page(session, page_num, government_agency)
            for page_num in current_batch
        ]

        batch_results = await asyncio.gather(*fetch_tasks, return_exceptions=True)

        # Process results
        batch_failed = 0
        batch_empty = 0
        for result in batch_results:
            if isinstance(result, Exception):
                print(f"❌ Batch error: {result}")
                batch_failed += 1
                continue

            page_num, page_html = result

            if page_html is None:
                failed_pages.append(page_num)
                print(f"❌ Page {page_num} failed")
                batch_failed += 1
                continue

            page_properties = extract_hidden_form_data(page_html)
            all_properties.extend(page_properties)

            if len(page_properties) == 0:
                batch_empty += 1

            print(
                f"✅ Page {page_num}: {len(page_properties)} properties | Total: {len(all_properties)}"
            )

        # Early termination: stop if entire batch failed or returned no data
        if batch_failed + batch_empty == len(current_batch):
            consecutive_empty_batches += 1
        else:
            consecutive_empty_batches = 0

        if consecutive_empty_batches >= 2:
            print(f"\n⚠️  {government_agency}: 2 consecutive batches with no data — stopping early")
            print(f"   Likely past actual data or session expired. Collected {len(all_properties)} properties.")
            break

        # Delay between batches (not between individual pages)
        if batch_end < len(remaining_pages):
            await asyncio.sleep(2)

    total_time = time.time() - start_time
    success_rate = ((total_pages - len(failed_pages)) / total_pages) * 100

    print("\n🎯 EXTRACTION SUMMARY:")
    print(f"   📊 Total properties: {len(all_properties)}")
    print(f"   📄 Pages processed: {total_pages - len(failed_pages)}/{total_pages}")
    print(f"   ✅ Success rate: {success_rate:.1f}%")
    print(f"   ⏱️ Total time: {total_time:.1f}s ({total_time / 60:.1f} minutes)")
    print(f"   ⚡ Average: {len(all_properties) / total_time:.1f} properties/second")

    if failed_pages:
        print(f"   ❌ Failed pages: {failed_pages}")

    return all_properties


async def save_to_database(
    properties: List[Dict[str, Any]],
    source_name: str,
    batch_size: int = 50,
    db: Optional["PropertyDatabase"] = None,
) -> tuple[int, int]:
    """
    Save scraped properties directly to Turso database (ASYNC)

    Args:
        properties: List of property dictionaries
        source_name: Source identifier (e.g., 'LED_Songkhla')
        batch_size: Number of properties per batch
        db: Shared PropertyDatabase instance (created if not provided)

    Returns:
        tuple: (successful_count, failed_count)
    """
    if not DATABASE_AVAILABLE:
        print("\n❌ Database module not available. Cannot save to database.")
        print("   Install requirements: pip install -r requirements.txt")
        return 0, len(properties)

    print(f"\n💾 Saving to PostgreSQL database (source: {source_name})...")

    # Add source_name to all properties
    for prop in properties:
        prop["source_name"] = source_name
        prop["extraction_timestamp"] = datetime.now().isoformat()

    try:
        if db is None:
            db = PropertyDatabase()
            db.create_tables()

        # Bulk insert (await the async function)
        successful, failed = await db.bulk_insert_led_properties(
            properties, batch_size=batch_size
        )

        return successful, failed

    except Exception as e:
        print(f"\n❌ Database error: {e}")
        import traceback

        traceback.print_exc()
        return 0, len(properties)


async def process_single_agency(
    session: AsyncSession,
    agency: str,
    max_pages: int,
    concurrent_pages: int,
    save_to: str,
    source_name: Optional[str],
    batch_size: int,
    deadline: Optional[float] = None,
    db: Optional["PropertyDatabase"] = None,
) -> Dict[str, Any]:
    """
    Process a single government agency and return results

    Returns:
        Dict with agency results including success status, counts, and errors
    """
    actual_source_name = source_name or f"LED_{agency}"
    agency_start_time = time.time()

    result = {
        "agency": agency,
        "source_name": actual_source_name,
        "success": False,
        "properties_count": 0,
        "pages_processed": 0,
        "db_saved": 0,
        "db_failed": 0,
        "json_file": None,
        "error": None,
        "duration_seconds": 0,
    }

    try:
        print(f"\n{'=' * 80}")
        print(f"🏛️  Processing Agency: {agency}")
        print(f"🏷️  Source Name: {actual_source_name}")
        print(f"{'=' * 80}")

        # Extract all properties for this agency
        all_properties = await extract_all_pages_production(
            session, agency, max_pages, concurrent_pages, deadline=deadline
        )

        if not all_properties:
            result["error"] = "No properties extracted"
            print(f"❌ {agency}: No properties extracted")
            return result

        result["properties_count"] = len(all_properties)
        result["success"] = True

        # Save to JSON if requested
        if save_to in ["json", "both"]:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"led_properties_{agency}_{timestamp}.json"

            extraction_data = {
                "extraction_info": {
                    "timestamp": datetime.now().isoformat(),
                    "method": "HTTP with hidden form extraction + pagination",
                    "total_properties": len(all_properties),
                    "government_agency": agency,
                    "source_name": actual_source_name,
                    "pages_processed": f"1-{max_pages}",
                    "version": "production-v2.0-multi",
                    "extraction_rate": f"{len(all_properties)} properties extracted",
                },
                "properties": all_properties,
            }

            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(extraction_data, f, ensure_ascii=False, indent=2)

            result["json_file"] = output_file
            print(f"💾 {agency}: JSON saved to {output_file}")

        # Save to database if requested
        if save_to in ["db", "both"]:
            if deadline is not None and time.time() > deadline:
                print(f"⏰ {agency}: Deadline reached, skipping database save")
                result["error"] = "Deadline reached before DB save"
            else:
                db_successful, db_failed = await save_to_database(
                    all_properties, actual_source_name, batch_size, db=db
                )
                result["db_saved"] = db_successful
                result["db_failed"] = db_failed

        result["duration_seconds"] = time.time() - agency_start_time

        print(f"\n✅ {agency}: Completed successfully")
        print(f"   📊 Properties: {result['properties_count']}")
        print(f"   ⏱️  Duration: {result['duration_seconds']:.1f}s")

    except Exception as e:
        result["error"] = str(e)
        result["duration_seconds"] = time.time() - agency_start_time
        print(f"\n❌ {agency}: Failed with error: {e}")
        import traceback

        traceback.print_exc()

    return result


async def process_agencies_in_batches(
    agencies: List[str],
    max_pages: int,
    concurrent_pages: int,
    save_to: str,
    source_prefix: str,
    batch_size: int,
    parallel_batch_size: int,
    max_duration_seconds: int = 840,  # 14 minutes (leave 1 min buffer for Lambda)
) -> List[Dict[str, Any]]:
    """
    Process multiple agencies in parallel batches with Lambda timeout handling

    Args:
        agencies: List of government agency names
        parallel_batch_size: Number of agencies to process concurrently
        max_duration_seconds: Maximum execution time (default: 14 min for Lambda)

    Returns:
        List of results for each agency
    """
    all_results = []
    total_start_time = time.time()

    print(f"\n{'=' * 80}")
    print(f"🚀 MULTI-AGENCY EXTRACTION")
    print(f"{'=' * 80}")
    print(f"   📋 Total agencies: {len(agencies)}")
    print(f"   ⚡ Parallel batch size: {parallel_batch_size}")
    print(f"   ⏱️  Max duration: {max_duration_seconds}s ({max_duration_seconds / 60:.1f} min)")
    print(f"   💾 Save to: {save_to}")
    print(f"   🏷️  Source prefix: {source_prefix}")
    print(f"{'=' * 80}\n")

    # Create shared database instance once (avoids Turso rate limits from parallel connections)
    db = None
    if save_to in ["db", "both"] and DATABASE_AVAILABLE:
        try:
            db = PropertyDatabase()
            db.create_tables()
            count = db.get_property_count()
            if count >= 0:
                print(f"📊 Properties in database: {count}")
        except Exception as e:
            print(f"❌ Database initialization failed: {e}")
            print("   Falling back to JSON only")
            save_to = "json"
            db = None

    # Create a single session for all agencies
    async with AsyncSession(
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        },
        timeout=120,
        verify=False,
    ) as session:
        # Process agencies in batches
        for batch_idx in range(0, len(agencies), parallel_batch_size):
            # Check if we're approaching timeout
            elapsed = time.time() - total_start_time
            if elapsed > max_duration_seconds:
                print(
                    f"\n⚠️  WARNING: Approaching timeout limit ({elapsed:.1f}s / {max_duration_seconds}s)"
                )
                print(f"   Stopping processing. Completed {len(all_results)}/{len(agencies)} agencies")
                remaining = agencies[batch_idx:]
                for agency in remaining:
                    all_results.append(
                        {
                            "agency": agency,
                            "source_name": f"{source_prefix}_{agency}",
                            "success": False,
                            "error": "Timeout - not processed",
                            "properties_count": 0,
                        }
                    )
                break

            batch_end = min(batch_idx + parallel_batch_size, len(agencies))
            current_batch = agencies[batch_idx:batch_end]

            print(f"\n{'─' * 80}")
            print(
                f"📦 Batch {batch_idx // parallel_batch_size + 1}: Processing {len(current_batch)} agencies"
            )
            print(f"   Agencies: {', '.join(current_batch)}")
            print(f"   Elapsed: {elapsed:.1f}s | Remaining: {max_duration_seconds - elapsed:.1f}s")
            print(f"{'─' * 80}")

            # Process current batch in parallel
            agency_deadline = total_start_time + max_duration_seconds
            tasks = [
                process_single_agency(
                    session,
                    agency,
                    max_pages,
                    concurrent_pages,
                    save_to,
                    f"{source_prefix}_{agency}",
                    batch_size,
                    deadline=agency_deadline,
                    db=db,
                )
                for agency in current_batch
            ]

            batch_results = await asyncio.gather(*tasks, return_exceptions=True)

            # Handle results
            for result in batch_results:
                if isinstance(result, Exception):
                    print(f"❌ Batch processing error: {result}")
                    all_results.append(
                        {
                            "agency": "unknown",
                            "success": False,
                            "error": str(result),
                            "properties_count": 0,
                        }
                    )
                else:
                    all_results.append(result)

            # Short delay between batches
            if batch_end < len(agencies):
                await asyncio.sleep(1)

    total_duration = time.time() - total_start_time

    # Print comprehensive summary
    print(f"\n{'=' * 80}")
    print(f"📊 MULTI-AGENCY EXTRACTION SUMMARY")
    print(f"{'=' * 80}")
    print(f"   ⏱️  Total Duration: {total_duration:.1f}s ({total_duration / 60:.1f} min)")
    print(f"   📋 Agencies Processed: {len([r for r in all_results if r.get('success')])}/{len(agencies)}")

    successful = [r for r in all_results if r.get("success")]
    failed = [r for r in all_results if not r.get("success")]

    if successful:
        total_properties = sum(r.get("properties_count", 0) for r in successful)
        total_db_saved = sum(r.get("db_saved", 0) for r in successful)
        print(f"\n   ✅ Successful ({len(successful)}):")
        for r in successful:
            print(f"      • {r['agency']}: {r['properties_count']} properties")
        print(f"\n   📊 Total Properties: {total_properties}")
        if save_to in ["db", "both"]:
            print(f"   💾 Total DB Saved: {total_db_saved}")

    if failed:
        print(f"\n   ❌ Failed ({len(failed)}):")
        for r in failed:
            print(f"      • {r['agency']}: {r.get('error', 'Unknown error')}")

    print(f"{'=' * 80}\n")

    return all_results


async def main():
    """Production main function for full-scale extraction with multi-agency support"""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="LED Property Scraper with Turso Integration - Multi-Agency Support"
    )

    # Agency selection (mutually exclusive group)
    agency_group = parser.add_mutually_exclusive_group(required=False)
    agency_group.add_argument(
        "--agency",
        type=str,
        help="Single government agency to scrape (e.g., สงขลา)",
    )
    agency_group.add_argument(
        "--agencies",
        type=str,
        help="Comma-separated list of agencies (e.g., สงขลา,กรุงเทพ,เชียงใหม่)",
    )
    agency_group.add_argument(
        "--agencies-file",
        type=str,
        help="Path to file containing agency names (one per line)",
    )

    # Scraping parameters
    parser.add_argument(
        "--max-pages",
        type=int,
        default=500,
        help="Maximum pages to scrape per agency (default: 500)",
    )
    parser.add_argument(
        "--concurrent",
        type=int,
        default=10,
        help="Number of concurrent pages per batch (default: 10)",
    )

    # Parallel processing
    parser.add_argument(
        "--parallel-batch-size",
        type=int,
        default=3,
        help="Number of agencies to process concurrently (default: 3)",
    )
    parser.add_argument(
        "--max-duration",
        type=int,
        default=840,
        help="Maximum execution time in seconds (default: 840s / 14 min for Lambda)",
    )

    # Save options
    parser.add_argument(
        "--save-to",
        type=str,
        choices=["json", "db", "both"],
        default="both",
        help="Where to save results: json, db (database), or both (default: both)",
    )
    parser.add_argument(
        "--source-prefix",
        type=str,
        default="LED",
        help="Source name prefix for database (default: LED, becomes LED_{agency})",
    )
    parser.add_argument(
        "--source-name",
        type=str,
        help="Source name for database (only for single agency mode)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=50,
        help="Batch size for database insert (default: 50)",
    )

    args = parser.parse_args()

    # Determine agencies to process
    agencies: List[str] = []

    if args.agencies_file:
        # Read from file
        try:
            with open(args.agencies_file, "r", encoding="utf-8") as f:
                agencies = [
                    line.strip() for line in f if line.strip() and not line.startswith("#")
                ]
            print(f"📋 Loaded {len(agencies)} agencies from {args.agencies_file}")
        except FileNotFoundError:
            print(f"❌ Error: File not found: {args.agencies_file}")
            return
        except Exception as e:
            print(f"❌ Error reading agencies file: {e}")
            return
    elif args.agencies:
        # Parse comma-separated list
        agencies = [a.strip() for a in args.agencies.split(",") if a.strip()]
        print(f"📋 Processing {len(agencies)} agencies from command line")
    elif args.agency:
        # Single agency (backwards compatibility)
        agencies = [args.agency]
    else:
        # Default to สงขลา for backwards compatibility
        agencies = ["สงขลา"]
        print("ℹ️  No agency specified, defaulting to: สงขลา")

    if not agencies:
        print("❌ Error: No agencies specified")
        return

    # Handle "all" keyword
    if len(agencies) == 1 and agencies[0].lower() == "all":
        agencies = list(VALID_AGENCIES)
        print(f"📋 Using all {len(agencies)} agencies from config")

    # Validate agencies against known list
    invalid_agencies = [a for a in agencies if a not in VALID_AGENCIES]
    if invalid_agencies:
        print(f"❌ Error: Invalid agency name(s): {', '.join(invalid_agencies)}")
        print(f"   Use one of the {len(VALID_AGENCIES)} valid agencies from config.py")
        return

    # Extract parameters
    MAX_PAGES = args.max_pages
    CONCURRENT_PAGES = args.concurrent
    SAVE_TO = args.save_to
    BATCH_SIZE = args.batch_size
    PARALLEL_BATCH_SIZE = args.parallel_batch_size
    MAX_DURATION = args.max_duration
    SOURCE_PREFIX = args.source_prefix

    # Check database availability if needed
    if SAVE_TO in ["db", "both"] and not DATABASE_AVAILABLE:
        print("\n⚠️  Warning: Database save requested but database module not available")
        print("   Falling back to JSON only")
        SAVE_TO = "json"

    # Create shared database instance once for single-agency mode too
    db = None
    if SAVE_TO in ["db", "both"] and DATABASE_AVAILABLE:
        try:
            db = PropertyDatabase()
            db.create_tables()
        except Exception as e:
            print(f"❌ Database initialization failed: {e}")
            print("   Falling back to JSON only")
            SAVE_TO = "json"

    # Process agencies
    if len(agencies) == 1:
        # Single agency mode (original behavior)
        GOVERNMENT_AGENCY = agencies[0]
        SOURCE_NAME = args.source_name or f"{SOURCE_PREFIX}_{GOVERNMENT_AGENCY}"

        print("🚀 LED Property Extraction - Single Agency Mode")
        print("=" * 60)
        print(f"   🏛️  Agency: {GOVERNMENT_AGENCY}")
        print(f"   📄 Max pages: {MAX_PAGES}")
        print(f"   ⚡ Concurrent: {CONCURRENT_PAGES}")
        print(f"   💾 Save to: {SAVE_TO}")
        print(f"   🏷️  Source: {SOURCE_NAME}")
        print("=" * 60)

        async with AsyncSession(
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            },
            timeout=120,
            verify=False,
        ) as session:
            result = await process_single_agency(
                session,
                GOVERNMENT_AGENCY,
                MAX_PAGES,
                CONCURRENT_PAGES,
                SAVE_TO,
                SOURCE_NAME,
                BATCH_SIZE,
                db=db,
            )

            if result["success"]:
                print("\n" + "=" * 60)
                print("📋 FINAL SUMMARY:")
                print(f"   🏠 Total properties scraped: {result['properties_count']}")
                print(f"   ⏱️  Duration: {result['duration_seconds']:.1f}s")
                if SAVE_TO in ["db", "both"]:
                    print("\n   💾 Database:")
                    print(f"      ✅ Saved: {result['db_saved']}")
                    print(f"      ❌ Failed: {result['db_failed']}")
                if result.get("json_file"):
                    print(f"\n   📄 JSON: {result['json_file']}")
                print("=" * 60)
            else:
                print(f"\n❌ Extraction failed: {result.get('error')}")

    else:
        # Multi-agency mode
        await process_agencies_in_batches(
            agencies=agencies,
            max_pages=MAX_PAGES,
            concurrent_pages=CONCURRENT_PAGES,
            save_to=SAVE_TO,
            source_prefix=SOURCE_PREFIX,
            batch_size=BATCH_SIZE,
            parallel_batch_size=PARALLEL_BATCH_SIZE,
            max_duration_seconds=MAX_DURATION,
        )


if __name__ == "__main__":
    asyncio.run(main())

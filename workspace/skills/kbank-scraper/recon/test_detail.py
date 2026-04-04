"""
KBank NPA property detail page scraper test.
Uses Playwright to bypass Akamai bot protection, then parses with selectolax.
"""

import json
import re
from pathlib import Path

from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync
from selectolax.parser import HTMLParser


DETAIL_URL = "https://www.kasikornbank.com/th/propertyforsale/detail/028818655.html"
OUTPUT_DIR = Path(__file__).parent
HTML_FILE = OUTPUT_DIR / "detail_sample.html"


def fetch_detail_page() -> str:
    """Fetch the detail page HTML using Playwright + stealth (bypasses Akamai)."""
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
            ],
        )
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/131.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1440, "height": 900},
            locale="th-TH",
        )
        page = context.new_page()
        stealth_sync(page)

        # First visit the search page to establish a session
        print("Visiting search page first to establish session...")
        page.goto(
            "https://www.kasikornbank.com/th/propertyforsale/search/pages/index.aspx",
            wait_until="domcontentloaded",
            timeout=30000,
        )
        page.wait_for_timeout(3000)

        # Now visit the detail page
        print("Navigating to detail page...")
        page.goto(DETAIL_URL, wait_until="networkidle", timeout=30000)
        # Wait for content to fully render
        page.wait_for_timeout(5000)
        html = page.content()
        browser.close()
        return html


def extract_text(node) -> str:
    """Extract cleaned text from a node."""
    if node is None:
        return ""
    return node.text(strip=True)


def extract_meta(tree: HTMLParser) -> dict:
    """Extract Open Graph and meta tags."""
    meta = {}
    for tag in tree.css("meta"):
        prop = tag.attributes.get("property", "") or tag.attributes.get("name", "")
        content = tag.attributes.get("content", "")
        if prop and content:
            meta[prop] = content
    return meta


def extract_images(tree: HTMLParser) -> list[str]:
    """Extract property image URLs."""
    images = []
    for img in tree.css("img"):
        src = img.attributes.get("src", "") or img.attributes.get("data-src", "")
        if src and ("property" in src.lower() or "upload" in src.lower() or "image" in src.lower()):
            if src not in images:
                images.append(src)
    for node in tree.css("[style]"):
        style = node.attributes.get("style") or ""
        urls = re.findall(r'url\(["\']?(.*?)["\']?\)', style)
        for url in urls:
            if url and url not in images:
                images.append(url)
    return images


def extract_coordinates(html: str) -> dict:
    """Extract lat/lng from JavaScript or data attributes."""
    coords = {}
    lat_match = re.search(r'(?:lat(?:itude)?)\s*[=:]\s*["\']?([\d.]+)', html, re.IGNORECASE)
    lng_match = re.search(r'(?:lng|lon(?:gitude)?)\s*[=:]\s*["\']?([\d.]+)', html, re.IGNORECASE)
    if lat_match:
        coords["latitude"] = float(lat_match.group(1))
    if lng_match:
        coords["longitude"] = float(lng_match.group(1))

    gmaps = re.search(r'maps.*?[?&]q=([\d.]+),([\d.]+)', html)
    if gmaps and "latitude" not in coords:
        coords["latitude"] = float(gmaps.group(1))
        coords["longitude"] = float(gmaps.group(2))

    return coords


def extract_json_ld(tree: HTMLParser) -> list[dict]:
    """Extract JSON-LD structured data."""
    results = []
    for script in tree.css('script[type="application/ld+json"]'):
        try:
            data = json.loads(script.text())
            results.append(data)
        except (json.JSONDecodeError, TypeError):
            pass
    return results


def extract_property_fields(tree: HTMLParser, html: str) -> dict:
    """Extract all property data fields from the page."""
    data = {}

    # Title
    title_node = tree.css_first("title")
    data["page_title"] = extract_text(title_node)

    # H1, H2, H3 headings
    for tag in ["h1", "h2", "h3"]:
        nodes = tree.css(tag)
        if nodes:
            data[f"{tag}_headings"] = [extract_text(n) for n in nodes if extract_text(n)]

    # Meta tags
    data["meta"] = extract_meta(tree)

    # JSON-LD
    json_ld = extract_json_ld(tree)
    if json_ld:
        data["json_ld"] = json_ld

    # dt/dd pairs
    for dt in tree.css("dt"):
        dd = dt.next
        while dd and dd.tag != "dd":
            dd = dd.next
        if dd:
            label = extract_text(dt)
            value = extract_text(dd)
            if label and value:
                data[f"dt_dd_{label}"] = value

    # Table rows
    for tr in tree.css("tr"):
        cells = tr.css("td, th")
        if len(cells) == 2:
            label = extract_text(cells[0])
            value = extract_text(cells[1])
            if label and value:
                data[f"table_{label}"] = value

    # Divs with detail/info/spec/property classes
    for container in tree.css("[class*='detail'], [class*='info'], [class*='spec'], [class*='property']"):
        cls = container.attributes.get("class", "")
        text = extract_text(container)
        if text and len(text) < 500:
            key = cls.replace(" ", "_")[:60]
            data[f"div_{key}"] = text

    # Thai label patterns
    thai_labels = [
        "ราคา", "พื้นที่", "ที่ตั้ง", "ประเภท", "จังหวัด", "อำเภอ", "ตำบล",
        "เนื้อที่", "ขนาด", "ห้องนอน", "ห้องน้ำ", "ชั้น", "จำนวน",
        "โฉนด", "เลขที่", "สถานะ", "รหัส", "ไร่", "งาน", "ตร.ว", "ตร.ม",
    ]
    for label in thai_labels:
        pattern = re.compile(
            rf'{label}\s*[:\-]?\s*([\d,.\s]+(?:บาท|ตร\.?ว|ตร\.?ม|ไร่|งาน)?)',
            re.UNICODE,
        )
        matches = pattern.findall(html)
        if matches:
            data[f"thai_{label}"] = [m.strip() for m in matches]

    # Images
    images = extract_images(tree)
    if images:
        data["images"] = images

    # Coordinates
    coords = extract_coordinates(html)
    if coords:
        data["coordinates"] = coords

    # Price patterns
    price_patterns = re.findall(r'([\d,]+(?:\.\d+)?)\s*บาท', html)
    if price_patterns:
        data["prices_baht"] = list(set(price_patterns))

    # Property-related links
    links = []
    for a in tree.css("a[href]"):
        href = a.attributes.get("href", "")
        text = extract_text(a)
        if href and ("property" in href.lower() or "detail" in href.lower()):
            links.append({"href": href, "text": text})
    if links:
        data["property_links"] = links[:20]

    # Script tags with property data
    for script in tree.css("script"):
        text = script.text() or ""
        if any(kw in text.lower() for kw in ["property", "price", "latitude", "longitude", "mapdata"]):
            snippet = text[:500].strip()
            if snippet:
                data.setdefault("script_snippets", []).append(snippet)

    return data


def main():
    print(f"Fetching: {DETAIL_URL}")
    html = fetch_detail_page()
    print(f"Response size: {len(html):,} bytes")

    # Check if we got past the bot protection
    if "bm-verify" in html and len(html) < 5000:
        print("WARNING: Still on Akamai bot challenge page. Content not loaded.")
        HTML_FILE.write_text(html, encoding="utf-8")
        print(f"Saved challenge HTML to: {HTML_FILE}")
        return

    # Save raw HTML
    HTML_FILE.write_text(html, encoding="utf-8")
    print(f"Saved to: {HTML_FILE}")

    # Parse
    tree = HTMLParser(html)
    data = extract_property_fields(tree, html)

    # Print summary
    print("\n" + "=" * 70)
    print("EXTRACTED FIELDS SUMMARY")
    print("=" * 70)

    for key, value in sorted(data.items()):
        if isinstance(value, list):
            print(f"\n{key} ({len(value)} items):")
            for item in value[:10]:
                if isinstance(item, dict):
                    print(f"  - {json.dumps(item, ensure_ascii=False)[:120]}")
                else:
                    print(f"  - {str(item)[:120]}")
            if len(value) > 10:
                print(f"  ... and {len(value) - 10} more")
        elif isinstance(value, dict):
            print(f"\n{key}:")
            for k, v in value.items():
                print(f"  {k}: {str(v)[:120]}")
        else:
            print(f"\n{key}: {str(value)[:200]}")


if __name__ == "__main__":
    main()

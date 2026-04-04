"""
Test: nodriver (undetected-chromedriver v2) for Akamai bypass.
Uses existing Chrome installation via CDP — no browser download needed.
"""

import asyncio
import nodriver as uc
from selectolax.parser import HTMLParser
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent
DETAIL_URL = "https://www.kasikornbank.com/th/propertyforsale/detail/028818655.html"


async def main():
    print("=== nodriver Test ===")
    print(f"Target: {DETAIL_URL}\n")

    # Launch browser — uses existing Chrome, headless by default
    print("[1] Launching browser...")
    browser = await uc.start(
        headless=False,  # headless=True gets 403 from Akamai
        sandbox=False,
    )

    # Navigate to search page first (establish session)
    print("[2] Establishing session via search page...")
    tab = await browser.get(
        "https://www.kasikornbank.com/th/propertyforsale/search/pages/index.aspx"
    )
    await tab.sleep(3)

    # Navigate to detail page
    print("[3] Loading detail page...")
    tab = await browser.get(DETAIL_URL)
    await tab.sleep(5)

    # Get page source
    html = await tab.get_content()
    print(f"  HTML size: {len(html):,} bytes")

    # Check if we got past Akamai
    if "bm-verify" in html and len(html) < 5000:
        print("  FAIL — got Akamai challenge page")
        # Try waiting longer
        print("  Waiting 10s for challenge to auto-resolve...")
        await tab.sleep(10)
        html = await tab.get_content()
        print(f"  HTML size after wait: {len(html):,} bytes")

    if len(html) > 100000:
        print("  SUCCESS — got real page!")

        # Parse with selectolax
        tree = HTMLParser(html)

        # Address
        addr = tree.css_first(".location-container p")
        print(f"\n  Address: {addr.text(strip=True) if addr else 'NOT FOUND'}")

        # Title deed
        for row in tree.css(".property-info .property-row, .property-table .property-row"):
            cells = row.css(".property-td")
            if len(cells) >= 2:
                label = cells[0].text(strip=True)
                value = cells[1].text(strip=True)
                if "โฉนด" in label or "เลขที่" in label:
                    print(f"  {label}: {value}")

        # Nearby places
        nearby = tree.css(".place-nearby table tr")
        print(f"  Nearby places: {len(nearby)}")
        for tr in nearby[:3]:
            cells = tr.css("td")
            if len(cells) >= 2:
                name = cells[0].text(strip=True)
                dist = cells[1].text(strip=True)
                print(f"    - {name}: {dist}")

        # Save
        out = OUTPUT_DIR / "detail_nodriver.html"
        out.write_text(html, encoding="utf-8")
        print(f"\n  Saved to: {out}")
    else:
        print(f"  FAIL — unexpected response ({len(html)} bytes)")
        print(f"  First 500 chars: {html[:500]}")

    # Test fetching a second property to check session reuse
    print("\n[4] Testing session reuse (second property)...")
    tab2 = await browser.get(
        "https://www.kasikornbank.com/th/propertyforsale/detail/058803725.html"
    )
    await tab2.sleep(5)
    html2 = await tab2.get_content()
    print(f"  HTML size: {len(html2):,} bytes")
    if len(html2) > 100000:
        tree2 = HTMLParser(html2)
        addr2 = tree2.css_first(".location-container p")
        print(f"  Address: {addr2.text(strip=True) if addr2 else 'NOT FOUND'}")
        print("  SUCCESS — session reuse works!")
    else:
        print("  Session reuse may need more delay")

    browser.stop()
    print("\n=== Done ===")


if __name__ == "__main__":
    uc.loop().run_until_complete(main())

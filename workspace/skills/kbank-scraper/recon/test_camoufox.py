"""
Test: Camoufox headless="virtual" for Akamai bypass.
Firefox-based, C++ level fingerprint spoofing, built-in Xvfb.
"""

import asyncio
from camoufox.async_api import AsyncCamoufox
from selectolax.parser import HTMLParser

DETAIL_URL = "https://www.kasikornbank.com/th/propertyforsale/detail/028818655.html"
SEARCH_URL = "https://www.kasikornbank.com/th/propertyforsale/search/pages/index.aspx"


async def test_camoufox(headless_mode, label: str) -> bool:
    print(f"\n{'=' * 50}")
    print(f"Test: {label}")
    print(f"{'=' * 50}")

    try:
        async with AsyncCamoufox(headless=headless_mode, humanize=True) as browser:
            page = await browser.new_page()

            # Establish session
            print("[1] Establishing session...")
            await page.goto(SEARCH_URL, wait_until="domcontentloaded")
            await page.wait_for_timeout(3000)

            # Detail page
            print("[2] Loading detail page...")
            await page.goto(DETAIL_URL, wait_until="networkidle")
            await page.wait_for_timeout(5000)
            html = await page.content()

            size = len(html)
            print(f"  HTML size: {size:,} bytes")

            if size > 100000:
                tree = HTMLParser(html)
                addr = tree.css_first(".location-container p")
                print(f"  Address: {addr.text(strip=True) if addr else 'NOT FOUND'}")

                nearby = tree.css(".place-nearby table tr")
                print(f"  Nearby places: {len(nearby)}")

                print(f"  PASS")
                return True
            elif "Access Denied" in html:
                print(f"  FAIL — 403 Access Denied")
                return False
            elif "bm-verify" in html:
                print(f"  FAIL — Akamai challenge not resolved")
                return False
            else:
                print(f"  FAIL — unexpected ({size} bytes)")
                print(f"  {html[:300]}")
                return False
    except Exception as e:
        print(f"  ERROR: {e}")
        return False


async def main():
    results = {}

    # Test: headless=True ONLY — no browser window should appear
    results["headless"] = await test_camoufox(True, "Camoufox headless=True (no window expected)")

    # Summary
    print(f"\n{'=' * 50}")
    print("SUMMARY")
    print(f"{'=' * 50}")
    for name, passed in results.items():
        print(f"  {name}: {'PASS' if passed else 'FAIL'}")


if __name__ == "__main__":
    asyncio.run(main())

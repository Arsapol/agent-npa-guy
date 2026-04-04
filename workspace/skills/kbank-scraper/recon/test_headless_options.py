"""
Test headless alternatives for Akamai bypass.

1. nodriver with --headless=new (Chrome 112+ new headless mode)
2. nodriver headed + Xvfb (virtual display)
"""

import asyncio
import sys
import nodriver as uc
from selectolax.parser import HTMLParser

DETAIL_URL = "https://www.kasikornbank.com/th/propertyforsale/detail/028818655.html"
SEARCH_URL = "https://www.kasikornbank.com/th/propertyforsale/search/pages/index.aspx"


async def test_variant(name: str, **kwargs):
    print(f"\n{'=' * 50}")
    print(f"Test: {name}")
    print(f"{'=' * 50}")

    try:
        browser = await uc.start(sandbox=False, **kwargs)
    except Exception as e:
        print(f"  Launch failed: {e}")
        return False

    try:
        # Establish session
        tab = await browser.get(SEARCH_URL)
        await tab.sleep(3)

        # Detail page
        tab = await browser.get(DETAIL_URL)
        await tab.sleep(5)
        html = await tab.get_content()

        size = len(html)
        print(f"  HTML size: {size:,} bytes")

        if size > 100000:
            tree = HTMLParser(html)
            addr = tree.css_first(".location-container p")
            print(f"  Address: {addr.text(strip=True) if addr else 'NOT FOUND'}")
            print(f"  PASS")
            return True
        elif "Access Denied" in html:
            print(f"  FAIL — 403 Access Denied")
            return False
        elif "bm-verify" in html:
            print(f"  FAIL — Akamai challenge not resolved")
            return False
        else:
            print(f"  FAIL — unexpected response")
            print(f"  First 300 chars: {html[:300]}")
            return False
    finally:
        browser.stop()


async def main():
    results = {}

    # Test 1: headless=new via browser_args
    results["headless=new (arg)"] = await test_variant(
        "headless=new via browser_args",
        headless=False,  # don't use nodriver's built-in headless
        browser_args=["--headless=new"],
    )

    # Test 2: nodriver headless=True (baseline, expect fail)
    results["headless=True"] = await test_variant(
        "nodriver headless=True (baseline)",
        headless=True,
    )

    # Test 3: headless=new + extra anti-detection args
    results["headless=new + stealth args"] = await test_variant(
        "headless=new + stealth args",
        headless=False,
        browser_args=[
            "--headless=new",
            "--disable-blink-features=AutomationControlled",
            "--window-size=1440,900",
        ],
    )

    # Summary
    print(f"\n{'=' * 50}")
    print("SUMMARY")
    print(f"{'=' * 50}")
    for name, passed in results.items():
        print(f"  {name}: {'PASS' if passed else 'FAIL'}")


if __name__ == "__main__":
    uc.loop().run_until_complete(main())

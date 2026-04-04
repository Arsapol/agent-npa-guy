"""
JAM Encryption Reverser

Downloads the Nuxt JS bundles and searches for the AES decryption logic.
"""

import asyncio
import json
import re
from pathlib import Path

from playwright.async_api import async_playwright
from playwright_stealth import stealth_async  # type: ignore

OUTPUT_DIR = Path(__file__).parent / "js_sources"
BASE_URL = "https://www.jjpropertythai.com"


async def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"],
        )
        context = await browser.new_context(
            viewport={"width": 1440, "height": 900},
            locale="th-TH",
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
        )
        page = await context.new_page()
        await stealth_async(page)

        # Collect JS URLs via response interception
        js_responses = {}
        all_responses = []

        async def capture_response(response):
            url = response.url
            content_type = response.headers.get("content-type", "")
            all_responses.append({"url": url[:120], "status": response.status, "type": content_type[:50]})
            if "_nuxt/" in url and (".js" in url):
                try:
                    body = await response.text()
                    js_responses[url] = body
                except Exception:
                    pass

        page.on("response", capture_response)

        print("Loading page...")
        resp = await page.goto(f"{BASE_URL}/Search?typeSaleIn=3", wait_until="domcontentloaded", timeout=60000)
        print(f"Page status: {resp.status}")
        print(f"Page URL: {page.url}")

        # Wait for JS to load
        await page.wait_for_timeout(8000)

        title = await page.title()
        print(f"Title: {title}")
        print(f"Responses captured: {len(all_responses)}")
        print(f"JS responses: {len(js_responses)}")

        # Debug: show first 20 responses
        for r in all_responses[:30]:
            print(f"  {r['status']} {r['type'][:30]:30s} {r['url']}")

        # Save page HTML
        html = await page.content()
        (OUTPUT_DIR / "page.html").write_text(html, encoding="utf-8")
        print(f"\nSaved page HTML ({len(html):,} bytes)")

        # Find script tags
        scripts = await page.evaluate("""
            () => {
                const all = [...document.querySelectorAll('script')];
                return all.map(s => ({
                    src: s.src || null,
                    type: s.type || null,
                    hasContent: s.textContent.length > 0,
                    contentPreview: s.textContent.substring(0, 200),
                }));
            }
        """)
        print(f"\nScript tags in DOM: {len(scripts)}")
        for s in scripts:
            if s["src"]:
                print(f"  src: {s['src'][:100]}")
            elif s["hasContent"]:
                print(f"  inline ({s['type']}): {s['contentPreview'][:100]}...")

        # If we got JS files, scan them
        if js_responses:
            print(f"\n=== Scanning {len(js_responses)} JS files for crypto ===")
            for url, source in js_responses.items():
                filename = url.split("/")[-1]
                (OUTPUT_DIR / filename).write_text(source, encoding="utf-8")

                patterns = {
                    "CryptoJS": r"CryptoJS",
                    "_encrypted": r"_encrypted",
                    "decrypt": r"\.decrypt\(",
                    "split_colon": r'split\(["\']:["\']',
                    "AES": r"\bAES\b",
                    "secret": r"secretKey|secret_key|encryptKey",
                }
                found = {k: len(re.findall(v, source, re.IGNORECASE)) for k, v in patterns.items() if re.search(v, source, re.IGNORECASE)}
                if found:
                    print(f"\n  {filename}: {found}")
                    for match in re.finditer(
                        r'.{0,300}(?:_encrypted|\.decrypt\(|CryptoJS|split\(["\']:["\']|secretKey).{0,300}',
                        source,
                        re.IGNORECASE,
                    ):
                        print(f"    SNIPPET: {match.group()[:400]}")

        await page.screenshot(path=str(OUTPUT_DIR / "debug.png"))
        await browser.close()

    print(f"\nDone. Files in: {OUTPUT_DIR}")


if __name__ == "__main__":
    asyncio.run(main())

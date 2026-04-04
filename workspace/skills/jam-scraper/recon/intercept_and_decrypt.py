"""
JAM Scraper — Playwright-based interceptor

Strategy:
1. Intercept API responses (encrypted JSON)
2. Let the browser decrypt via its own JS
3. Hook into the decryption by evaluating JS in page context
4. Extract decrypted property data from rendered DOM
5. Save raw + decrypted data for schema mapping

Usage:
    python intercept_and_decrypt.py [--pages N] [--headed]
"""

import argparse
import asyncio
import json
from datetime import datetime
from pathlib import Path

from playwright.async_api import async_playwright

OUTPUT_DIR = Path(__file__).parent / "captures" / datetime.now().strftime("%Y%m%d_%H%M%S")

# API base
BASE_URL = "https://www.jjpropertythai.com"
ASSETS_API = "/api/proxy/v1/assets"
DETAIL_API = "/details/"

# Dropdown APIs (no encryption expected)
DROPDOWN_APIS = [
    "/api/proxy/v1/dropdown/company",
    "/api/proxy/v1/dropdown/typeAsset",
    "/api/proxy/v1/dropdown/typeSell",
    "/api/proxy/v1/dropdown/province",
]


async def capture_dropdowns(page) -> dict:
    """Fetch all dropdown data (for mapping codes to Thai names)."""
    dropdowns = {}
    for endpoint in DROPDOWN_APIS:
        url = f"{BASE_URL}{endpoint}"
        try:
            resp = await page.evaluate(
                """async (url) => {
                    const r = await fetch(url);
                    return await r.json();
                }""",
                url,
            )
            name = endpoint.split("/")[-1]
            dropdowns[name] = resp
            print(f"  Dropdown '{name}': {len(resp) if isinstance(resp, list) else 'object'} entries")
        except Exception as e:
            print(f"  Dropdown '{endpoint}' failed: {e}")
    return dropdowns


async def extract_js_decryption_logic(page) -> str | None:
    """Try to find and extract the decryption function from loaded JS."""
    # Search all script sources for crypto/decrypt patterns
    result = await page.evaluate("""
        () => {
            const scripts = performance.getEntriesByType('resource')
                .filter(r => r.initiatorType === 'script' && r.name.includes('_nuxt'))
                .map(r => r.name);
            return scripts;
        }
    """)
    print(f"\n  Found {len(result)} _nuxt scripts")
    return result


async def intercept_decrypted_assets(page, search_url: str) -> list[dict]:
    """
    Navigate to search page and extract property data from rendered DOM.
    The browser handles decryption — we just read the result.
    """
    decrypted_responses = []
    encrypted_responses = []

    # Intercept API responses
    async def handle_response(response):
        url = response.url
        if ASSETS_API in url:
            try:
                body = await response.json()
                if "_encrypted" in body:
                    encrypted_responses.append({
                        "url": url,
                        "encrypted_preview": body["_encrypted"][:200],
                    })
                else:
                    decrypted_responses.append({"url": url, "data": body})
            except Exception:
                pass

    page.on("response", handle_response)

    print(f"\n  Navigating to: {search_url}")
    await page.goto(search_url, wait_until="networkidle", timeout=60000)

    # Wait for property cards to render
    await page.wait_for_timeout(3000)

    # Extract property data from rendered DOM
    properties = await page.evaluate("""
        () => {
            // Try to find Vue/Nuxt app data
            const app = document.querySelector('#__nuxt');
            if (!app || !app.__vue_app__) return { method: 'dom', data: [] };

            // Try accessing the reactive data
            try {
                // Walk the component tree to find asset data
                const findData = (node, depth = 0) => {
                    if (depth > 10) return null;
                    if (node?.proxy?.$data?.assets) return node.proxy.$data.assets;
                    if (node?.proxy?.$data?.items) return node.proxy.$data.items;
                    if (node?.proxy?.assets) return node.proxy.assets;
                    if (node?.subTree?.component) {
                        const result = findData(node.subTree.component, depth + 1);
                        if (result) return result;
                    }
                    if (node?.subTree?.children) {
                        for (const child of node.subTree.children) {
                            if (child?.component) {
                                const result = findData(child.component, depth + 1);
                                if (result) return result;
                            }
                        }
                    }
                    return null;
                };

                const root = app.__vue_app__._instance;
                const data = findData(root);
                if (data) return { method: 'vue_data', data: JSON.parse(JSON.stringify(data)) };
            } catch(e) {
                // Fall through to DOM scraping
            }

            // Fallback: scrape from DOM
            const cards = document.querySelectorAll('.v-card');
            const results = [];
            for (const card of cards) {
                const title = card.querySelector('.v-card-title')?.textContent?.trim();
                const subtitle = card.querySelector('.v-card-subtitle')?.textContent?.trim();
                const text = card.querySelector('.v-card-text')?.textContent?.trim();
                const img = card.querySelector('img')?.src;
                const link = card.closest('a')?.href || card.querySelector('a')?.href;
                if (title || subtitle) {
                    results.push({ title, subtitle, text, img, link });
                }
            }
            return { method: 'dom_scrape', data: results };
        }
    """)

    return {
        "properties": properties,
        "encrypted_responses": encrypted_responses,
        "decrypted_responses": decrypted_responses,
    }


async def fetch_js_source(page, js_url: str) -> str:
    """Fetch a JS file content via page context."""
    return await page.evaluate(
        """async (url) => {
            const r = await fetch(url);
            return await r.text();
        }""",
        js_url,
    )


async def find_decryption_in_js(page, script_urls: list[str]) -> dict | None:
    """Search JS sources for AES/crypto decryption patterns."""
    for url in script_urls:
        try:
            source = await fetch_js_source(page, url)
            # Look for crypto patterns
            crypto_keywords = [
                "CryptoJS", "crypto-js", "aes", "decrypt",
                "createDecipheriv", "AES", "CBC", "iv",
                "_encrypted", "decipher",
            ]
            matches = [kw for kw in crypto_keywords if kw.lower() in source.lower()]
            if matches:
                filename = url.split("/")[-1]
                print(f"  CRYPTO FOUND in {filename}: {matches}")

                # Save the full source
                js_path = OUTPUT_DIR / f"crypto_{filename}"
                js_path.write_text(source, encoding="utf-8")
                print(f"  Saved: {js_path.name} ({len(source):,} bytes)")

                return {"url": url, "filename": filename, "keywords": matches, "size": len(source)}
        except Exception as e:
            print(f"  Error fetching {url}: {e}")
    return None


async def capture_detail_page(page, asset_id: str) -> dict:
    """Navigate to a detail page and extract full property data."""
    url = f"{BASE_URL}/details/{asset_id}"
    print(f"\n  Detail page: {url}")

    await page.goto(url, wait_until="networkidle", timeout=30000)
    await page.wait_for_timeout(2000)

    # Extract all visible data
    detail = await page.evaluate("""
        () => {
            const getText = (sel) => document.querySelector(sel)?.textContent?.trim() || null;
            const getAll = (sel) => [...document.querySelectorAll(sel)].map(e => e.textContent?.trim());
            const getImgs = (sel) => [...document.querySelectorAll(sel)].map(e => e.src || e.dataset?.src);

            return {
                title: getText('h1') || getText('.v-card-title'),
                images: getImgs('img[src*="jjpropertythai"]'),
                // Get all text content organized by sections
                body_text: document.querySelector('.v-main')?.innerText?.substring(0, 5000) || null,
                url: window.location.href,
            };
        }
    """)

    # Save screenshot
    screenshot_path = OUTPUT_DIR / f"detail_{asset_id}.png"
    await page.screenshot(path=str(screenshot_path), full_page=True)

    return detail


async def main(max_pages: int = 1, headed: bool = False):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Output: {OUTPUT_DIR}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=not headed)
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

        # Step 1: Load the search page
        print("\n=== Step 1: Loading search page ===")
        search_url = f"{BASE_URL}/Search?typeSaleIn=3&companyCodeIn=All"
        result = await intercept_decrypted_assets(page, search_url)

        # Save search results
        (OUTPUT_DIR / "search_result.json").write_text(
            json.dumps(result, ensure_ascii=False, indent=2, default=str),
            encoding="utf-8",
        )
        print(f"\n  Properties extracted: {len(result['properties'].get('data', []))}")
        print(f"  Method: {result['properties'].get('method')}")
        print(f"  Encrypted responses captured: {len(result['encrypted_responses'])}")

        # Step 2: Find the decryption JS
        print("\n=== Step 2: Finding decryption logic ===")
        script_urls = await extract_js_decryption_logic(page)
        crypto_info = await find_decryption_in_js(page, script_urls)

        if crypto_info:
            print(f"\n  Decryption found in: {crypto_info['filename']}")
        else:
            print("\n  No crypto keywords found in _nuxt scripts")
            print("  Trying entry.js and other bundles...")
            # Also check the main entry file
            all_scripts = await page.evaluate("""
                () => [...document.querySelectorAll('script[src]')].map(s => s.src)
            """)
            crypto_info = await find_decryption_in_js(page, all_scripts)

        # Step 3: Capture dropdown data
        print("\n=== Step 3: Capturing dropdown data ===")
        dropdowns = await capture_dropdowns(page)
        (OUTPUT_DIR / "dropdowns.json").write_text(
            json.dumps(dropdowns, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        # Step 4: Try to extract decrypted data via JS interception
        print("\n=== Step 4: Attempting JS-level data extraction ===")
        # Monkey-patch fetch to capture decrypted responses
        decrypted_data = await page.evaluate("""
            async () => {
                // Re-fetch the assets API and try to find decryption in window/global
                try {
                    const resp = await fetch('/api/proxy/v1/assets?freeText=&page=1&user_code=521789&limit=12&SellingStart=0&SellingEnd=100000000&typeSaleIn[]=3');
                    const raw = await resp.json();

                    if (raw._encrypted) {
                        // Look for decryption function in global scope
                        const possibleDecryptors = [];
                        for (const key of Object.keys(window)) {
                            const val = window[key];
                            if (typeof val === 'function' && key.toLowerCase().includes('decrypt')) {
                                possibleDecryptors.push(key);
                            }
                        }
                        return {
                            has_encrypted: true,
                            encrypted_length: raw._encrypted.length,
                            format: raw._encrypted.substring(0, 100),
                            possible_decryptors: possibleDecryptors,
                        };
                    }
                    return { has_encrypted: false, data_keys: Object.keys(raw) };
                } catch(e) {
                    return { error: e.message };
                }
            }
        """)
        print(f"  JS extraction result: {json.dumps(decrypted_data, indent=2)}")

        # Step 5: Capture a detail page
        print("\n=== Step 5: Capturing a detail page ===")
        detail = await capture_detail_page(page, "50334")
        (OUTPUT_DIR / "detail_50334.json").write_text(
            json.dumps(detail, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        # Step 6: Take screenshots
        print("\n=== Step 6: Screenshots ===")
        await page.goto(search_url, wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(3000)
        await page.screenshot(path=str(OUTPUT_DIR / "search_page.png"), full_page=True)
        print("  Saved search_page.png")

        await browser.close()

    print(f"\nDone! All captures in: {OUTPUT_DIR}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="JAM interceptor")
    parser.add_argument("--pages", type=int, default=1)
    parser.add_argument("--headed", action="store_true")
    args = parser.parse_args()

    asyncio.run(main(max_pages=args.pages, headed=args.headed))

"""
Reverse-engineer KBank NPA property search API parameters.
Intercepts all JS files loaded by the search page and searches for
filter/pagination parameter construction patterns.
"""
import asyncio
import json
import re
import sys
from pathlib import Path

from playwright.async_api import async_playwright
from playwright_stealth import Stealth

JS_DIR = Path(__file__).parent / "js_sources"
JS_DIR.mkdir(parents=True, exist_ok=True)

TARGET_URL = "https://www.kasikornbank.com/th/propertyforsale/search/pages/index.aspx"

SEARCH_PATTERNS = [
    "GetProperties",
    "PageSize",
    "SearchPurposes",
    "NPA2023Backend",
    "filter",
    "PageNo",
    "PageIndex",
    "PageNumber",
    "CurrentPage",
    "Province",
    "PropertyType",
    "PriceMin",
    "PriceMax",
    "Keyword",
    "SortBy",
    "SortOrder",
    "OrderBy",
    "Skip",
    "Take",
    "Offset",
    "StartIndex",
    "RowStart",
    "RowEnd",
]


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
            ],
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            locale="th-TH",
            java_script_enabled=True,
            bypass_csp=True,
        )
        page = await context.new_page()
        stealth = Stealth()
        await stealth.apply_stealth_async(page)

        js_files: dict[str, str] = {}
        api_calls: list[dict] = []

        # Intercept ALL responses
        async def on_response(response):
            url = response.url
            # Capture JS files
            if url.endswith(".js") or ".js?" in url:
                try:
                    body = await response.text()
                    # Create a safe filename
                    name = url.split("/")[-1].split("?")[0]
                    if not name.endswith(".js"):
                        name += ".js"
                    # Deduplicate names
                    safe = re.sub(r'[^\w.\-]', '_', name)
                    idx = 0
                    final_name = safe
                    while final_name in js_files:
                        idx += 1
                        final_name = f"{safe.rsplit('.', 1)[0]}_{idx}.js"
                    js_files[final_name] = body
                    path = JS_DIR / final_name
                    path.write_text(body, encoding="utf-8")
                    print(f"  [JS] {final_name} ({len(body):,} bytes) <- {url[:120]}")
                except Exception as e:
                    print(f"  [JS-ERR] {url[:80]}: {e}")

            # Capture API calls to GetProperties
            if "GetProperties" in url or "NPA2023Backend" in url:
                try:
                    body = await response.text()
                    api_calls.append({"url": url, "status": response.status, "body_len": len(body)})
                    print(f"  [API] {url[:120]} status={response.status}")
                except Exception:
                    pass

        page.on("response", on_response)

        # Also intercept requests to see POST bodies
        async def on_request(request):
            if "GetProperties" in request.url or "NPA2023Backend" in request.url:
                try:
                    post = request.post_data
                    print(f"\n  [REQ] {request.method} {request.url[:120]}")
                    if post:
                        print(f"  [REQ-BODY] {post[:500]}")
                except Exception:
                    pass

        page.on("request", on_request)

        print(f"Loading {TARGET_URL} ...")
        await page.goto(TARGET_URL, wait_until="networkidle", timeout=60000)
        print(f"Page loaded. Title: {await page.title()}")

        # Wait a bit for lazy-loaded JS
        await page.wait_for_timeout(3000)

        # Try to trigger the search by interacting with the page
        print("\nTrying to trigger search interactions...")
        try:
            # Look for search button and click it
            search_btns = await page.query_selector_all('button, input[type="submit"], a.search, .btn-search, [class*="search"]')
            print(f"  Found {len(search_btns)} potential search elements")
            for btn in search_btns[:3]:
                txt = await btn.text_content()
                cls = await btn.get_attribute("class") or ""
                print(f"    - {await btn.evaluate('e => e.tagName')} class='{cls}' text='{(txt or '').strip()[:50]}'")
        except Exception as e:
            print(f"  Interaction error: {e}")

        # Try scrolling to trigger lazy loads
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        await page.wait_for_timeout(2000)

        # Also try to extract inline scripts from the page
        print("\nExtracting inline scripts...")
        inline_scripts = await page.evaluate("""
            () => {
                const scripts = document.querySelectorAll('script');
                const results = [];
                scripts.forEach((s, i) => {
                    if (s.textContent && s.textContent.trim().length > 10) {
                        results.push({index: i, src: s.src || '(inline)', length: s.textContent.length, content: s.textContent});
                    }
                });
                return results;
            }
        """)
        for s in inline_scripts:
            name = f"inline_{s['index']}.js"
            content = s['content']
            js_files[name] = content
            (JS_DIR / name).write_text(content, encoding="utf-8")
            print(f"  [INLINE] {name} ({s['length']:,} bytes)")

        # Try to get the AngularJS/React/Vue app state or any global config
        print("\nChecking for global config objects...")
        config_check = await page.evaluate("""
            () => {
                const results = {};
                // Common config patterns
                const keys = ['__NEXT_DATA__', 'window.__STATE__', 'window.__CONFIG__',
                              'window.appConfig', 'window.pageConfig', 'window.npaConfig'];
                for (const k of keys) {
                    try {
                        const val = eval(k);
                        if (val) results[k] = JSON.stringify(val).substring(0, 500);
                    } catch(e) {}
                }
                // Check for any variable containing 'NPA' or 'filter' or 'property'
                try {
                    for (const k of Object.keys(window)) {
                        const lower = k.toLowerCase();
                        if (lower.includes('npa') || lower.includes('filter') || lower.includes('property') || lower.includes('search')) {
                            try {
                                const val = window[k];
                                if (val && typeof val !== 'function') {
                                    results['window.' + k] = JSON.stringify(val).substring(0, 500);
                                }
                            } catch(e) {}
                        }
                    }
                } catch(e) {}
                return results;
            }
        """)
        if config_check:
            print("  Found config objects:")
            for k, v in config_check.items():
                print(f"    {k}: {v[:200]}")

        await browser.close()

    # ── Search phase ──
    print(f"\n{'='*80}")
    print(f"SEARCH PHASE: {len(js_files)} JS files captured")
    print(f"{'='*80}\n")

    # Combine all JS for more efficient searching
    all_js_content = []
    for name, content in sorted(js_files.items()):
        all_js_content.append((name, content))

    context_chars = 300

    for pattern in SEARCH_PATTERNS:
        matches = []
        for name, content in all_js_content:
            # Case-insensitive search
            for m in re.finditer(re.escape(pattern), content, re.IGNORECASE):
                start = max(0, m.start() - context_chars)
                end = min(len(content), m.end() + context_chars)
                snippet = content[start:end]
                # Clean up for readability
                snippet = snippet.replace('\n', ' ').replace('\r', '')
                matches.append((name, m.start(), snippet))

        if matches:
            print(f"\n{'─'*60}")
            print(f"Pattern: {pattern} — {len(matches)} match(es)")
            print(f"{'─'*60}")
            for name, pos, snippet in matches[:10]:  # cap at 10 per pattern
                print(f"\n  [{name} @ {pos}]")
                print(f"  ...{snippet}...")
        else:
            print(f"  Pattern: {pattern} — NO MATCHES")

    # ── Deep analysis: look for filter object construction ──
    print(f"\n{'='*80}")
    print("DEEP ANALYSIS: Looking for filter/request body construction")
    print(f"{'='*80}\n")

    # Patterns that indicate filter object construction
    deep_patterns = [
        r'filter\s*[=:]\s*\{',
        r'filter\s*\.\s*\w+\s*=',
        r'JSON\.stringify\s*\(\s*\{[^}]*filter',
        r'\.ajax\s*\(\s*\{',
        r'fetch\s*\(\s*["\'].*GetProperties',
        r'\$\.post\s*\(',
        r'data\s*:\s*JSON\.stringify',
        r'contentType.*application/json',
        r'SearchPurpose',
        r'AllProperties',
        r'pageSize|page_size|page\.size',
        r'pageNo|page_no|page\.no|pageNum|page_num',
        r'currentPage|current_page',
        r'startRow|start_row|rowStart|row_start',
        r'skipCount|skip_count|skipRows',
        r'province|Province|จังหวัด',
        r'propertyType|property_type|PropertyType|ประเภท',
        r'priceMin|price_min|PriceMin|priceFrom|price_from',
        r'sortBy|sort_by|SortBy|orderBy|order_by|OrderBy',
    ]

    for pat in deep_patterns:
        matches = []
        for name, content in all_js_content:
            for m in re.finditer(pat, content, re.IGNORECASE):
                start = max(0, m.start() - context_chars)
                end = min(len(content), m.end() + context_chars)
                snippet = content[start:end].replace('\n', ' ').replace('\r', '')
                matches.append((name, m.start(), snippet))

        if matches:
            print(f"\n{'─'*60}")
            print(f"Deep pattern: {pat} — {len(matches)} match(es)")
            print(f"{'─'*60}")
            for name, pos, snippet in matches[:5]:
                print(f"\n  [{name} @ {pos}]")
                print(f"  ...{snippet}...")

    # ── Also try to find the complete filter object by looking for multi-key objects ──
    print(f"\n{'='*80}")
    print("OBJECT CONSTRUCTION: Looking for objects with multiple known keys")
    print(f"{'='*80}\n")

    for name, content in all_js_content:
        # Look for blocks that contain both PageSize and SearchPurposes
        if "PageSize" in content and "SearchPurposes" in content:
            print(f"\n  [{name}] contains BOTH PageSize and SearchPurposes!")
            # Find the region
            for m in re.finditer(r'PageSize', content):
                start = max(0, m.start() - 500)
                end = min(len(content), m.end() + 1000)
                region = content[start:end].replace('\n', ' ').replace('\r', '')
                if "SearchPurposes" in region:
                    print(f"  Combined region @ {m.start()}:")
                    print(f"  ...{region}...")
                    break

        # Also look for GetProperties call context
        if "GetProperties" in content:
            for m in re.finditer(r'GetProperties', content):
                start = max(0, m.start() - 500)
                end = min(len(content), m.end() + 1500)
                region = content[start:end].replace('\n', ' ').replace('\r', '')
                print(f"\n  [{name}] GetProperties context @ {m.start()}:")
                print(f"  ...{region[:2000]}...")


if __name__ == "__main__":
    asyncio.run(main())

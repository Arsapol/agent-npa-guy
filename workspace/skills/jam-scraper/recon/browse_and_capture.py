"""
JAM Site Recon — Playwright browser capture

Opens JAM website with Playwright, captures:
1. HAR file (all network requests/responses)
2. Page HTML snapshots
3. Console logs
4. Screenshots at each step

Usage:
    python browse_and_capture.py [--url URL] [--headed]
"""

import argparse
import asyncio
import json
from datetime import datetime
from pathlib import Path

from playwright.async_api import async_playwright

RECON_DIR = Path(__file__).parent
OUTPUT_DIR = RECON_DIR / "captures" / datetime.now().strftime("%Y%m%d_%H%M%S")

# Known JAM/JMT URLs to explore
URLS_TO_EXPLORE = [
    "https://www.jmt.co.th",
    "https://jamgroup.co.th",
    "https://auction.jmt.co.th",
    "https://www.jmt.co.th/auction",
    "https://www.jmt.co.th/npa",
]


async def capture_page(page, url: str, label: str, console_logs: list):
    """Navigate to a URL and capture HTML + screenshot."""
    print(f"\n--- Navigating to: {url} ({label}) ---")
    try:
        response = await page.goto(url, wait_until="networkidle", timeout=30000)
        status = response.status if response else "no response"
        final_url = page.url
        print(f"  Status: {status}, Final URL: {final_url}")

        # Save HTML
        html = await page.content()
        html_path = OUTPUT_DIR / f"{label}.html"
        html_path.write_text(html, encoding="utf-8")
        print(f"  Saved HTML: {html_path.name} ({len(html):,} bytes)")

        # Save screenshot
        screenshot_path = OUTPUT_DIR / f"{label}.png"
        await page.screenshot(path=str(screenshot_path), full_page=True)
        print(f"  Saved screenshot: {screenshot_path.name}")

        # Save page title and metadata
        title = await page.title()
        return {
            "label": label,
            "requested_url": url,
            "final_url": final_url,
            "status": status,
            "title": title,
            "html_size": len(html),
        }

    except Exception as e:
        print(f"  Error: {e}")
        return {
            "label": label,
            "requested_url": url,
            "error": str(e),
        }


async def explore_links(page, base_url: str):
    """Find all internal links on the current page that might lead to NPA/auction content."""
    links = await page.evaluate("""
        () => {
            const anchors = document.querySelectorAll('a[href]');
            return Array.from(anchors).map(a => ({
                href: a.href,
                text: a.textContent.trim().substring(0, 100),
            })).filter(l =>
                l.href.startsWith('http') &&
                !l.href.includes('facebook') &&
                !l.href.includes('line.me') &&
                !l.href.includes('youtube')
            );
        }
    """)

    # Filter for NPA/auction-related links
    keywords = ["npa", "auction", "ประมูล", "ทรัพย์", "สินทรัพย์", "อสังหา", "property", "asset", "jam"]
    relevant = []
    for link in links:
        text_lower = (link["text"] + link["href"]).lower()
        if any(kw in text_lower for kw in keywords):
            relevant.append(link)

    return {"all_links": links, "relevant_links": relevant}


async def main(start_url: str | None = None, headed: bool = False):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    console_logs = []
    api_calls = []

    print(f"Recon output: {OUTPUT_DIR}")

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

        # Start HAR recording
        har_path = OUTPUT_DIR / "capture.har"
        await context.tracing.start(screenshots=True, snapshots=True)

        page = await context.new_page()

        # Capture console logs
        page.on("console", lambda msg: console_logs.append({
            "type": msg.type,
            "text": msg.text,
        }))

        # Capture network requests (especially API/XHR)
        def on_request(request):
            if request.resource_type in ("xhr", "fetch", "document"):
                api_calls.append({
                    "method": request.method,
                    "url": request.url,
                    "resource_type": request.resource_type,
                    "headers": dict(request.headers),
                })

        page.on("request", on_request)

        # Phase 1: Explore known URLs
        results = []
        urls = [start_url] if start_url else URLS_TO_EXPLORE

        for i, url in enumerate(urls):
            label = f"page_{i:02d}"
            result = await capture_page(page, url, label, console_logs)
            results.append(result)

            # If page loaded successfully, explore links
            if "error" not in result:
                links = await explore_links(page, url)
                result["links"] = links
                if links["relevant_links"]:
                    print(f"  Found {len(links['relevant_links'])} relevant links:")
                    for link in links["relevant_links"][:10]:
                        print(f"    - {link['text'][:60]} → {link['href'][:80]}")

        # Phase 2: Follow relevant links found on pages
        discovered_urls = set()
        for result in results:
            if "links" in result:
                for link in result["links"]["relevant_links"]:
                    href = link["href"]
                    if href not in [r.get("requested_url") for r in results]:
                        discovered_urls.add(href)

        print(f"\n--- Following {len(discovered_urls)} discovered URLs ---")
        for i, url in enumerate(list(discovered_urls)[:10]):
            label = f"discovered_{i:02d}"
            result = await capture_page(page, url, label, console_logs)
            results.append(result)

        # Save tracing
        trace_path = OUTPUT_DIR / "trace.zip"
        await context.tracing.stop(path=str(trace_path))
        print(f"\nSaved trace: {trace_path.name}")

        await browser.close()

    # Save summary
    summary = {
        "timestamp": datetime.now().isoformat(),
        "pages": results,
        "api_calls": api_calls,
        "console_logs": console_logs[:200],
        "total_api_calls": len(api_calls),
        "total_console_logs": len(console_logs),
    }

    summary_path = OUTPUT_DIR / "summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nSaved summary: {summary_path.name}")
    print(f"Total API/XHR calls captured: {len(api_calls)}")
    print(f"Total console logs: {len(console_logs)}")

    # Print API endpoints found
    if api_calls:
        print("\n--- API Endpoints Found ---")
        seen = set()
        for call in api_calls:
            key = f"{call['method']} {call['url'].split('?')[0]}"
            if key not in seen:
                seen.add(key)
                print(f"  {call['method']} {call['url'][:120]}")

    print(f"\nDone. All captures in: {OUTPUT_DIR}")
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="JAM site recon with Playwright")
    parser.add_argument("--url", help="Specific URL to start with")
    parser.add_argument("--headed", action="store_true", help="Run with visible browser")
    args = parser.parse_args()

    asyncio.run(main(start_url=args.url, headed=args.headed))

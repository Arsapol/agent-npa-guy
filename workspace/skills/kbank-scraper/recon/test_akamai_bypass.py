"""
Test: Bypass Akamai Bot Manager without a browser.

Strategy:
1. curl_cffi → GET detail page → receive PoW challenge
2. Parse bm-verify token + arithmetic from challenge HTML
3. Solve PoW in Python
4. POST solution to /_sec/verify → get session cookie
5. Retry detail page with session cookie → real HTML
"""

import re
from curl_cffi import requests

DETAIL_URL = "https://www.kasikornbank.com/th/propertyforsale/detail/028818655.html"
BASE_URL = "https://www.kasikornbank.com"

session = requests.Session(impersonate="chrome120")
session.headers.update({
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": f"{BASE_URL}/th/propertyforsale/search/pages/index.aspx",
})


def parse_akamai_challenge(html: str) -> dict | None:
    """Parse Akamai interstitial challenge page."""

    # Extract bm-verify token from meta refresh or form
    bm_match = re.search(r'bm-verify=([a-zA-Z0-9_-]+)', html)
    if not bm_match:
        print("  No bm-verify token found")
        return None

    token = bm_match.group(1)
    print(f"  bm-verify token: {token[:20]}...")

    # Extract PoW computation — look for patterns like:
    # var i = 1775305854; var j = i + Number("4176" + "58482");
    pow_match = re.search(
        r'var\s+\w+\s*=\s*(\d+)\s*;\s*var\s+\w+\s*=\s*\w+\s*\+\s*Number\("(\d+)"\s*\+\s*"(\d+)"\)',
        html
    )
    if pow_match:
        i_val = int(pow_match.group(1))
        num_parts = pow_match.group(2) + pow_match.group(3)
        j_val = i_val + int(num_parts)
        print(f"  PoW: {i_val} + {num_parts} = {j_val}")
        return {"token": token, "answer": j_val}

    # Alternative PoW patterns
    pow_match2 = re.search(r'var\s+\w+\s*=\s*(\d+)\s*;\s*var\s+\w+\s*=\s*\w+\s*\+\s*(\d+)', html)
    if pow_match2:
        i_val = int(pow_match2.group(1))
        add_val = int(pow_match2.group(2))
        j_val = i_val + add_val
        print(f"  PoW (simple): {i_val} + {add_val} = {j_val}")
        return {"token": token, "answer": j_val}

    print("  Could not parse PoW computation")
    print(f"  HTML snippet around 'var': {html[html.find('var i'):html.find('var i')+200] if 'var i' in html else 'NOT FOUND'}")
    return None


def solve_and_verify(challenge: dict) -> bool:
    """POST PoW solution to Akamai verification endpoint."""
    verify_url = f"{BASE_URL}/_sec/verify?provider=interstitial"
    data = {
        "bm-verify": challenge["token"],
        "pow": challenge["answer"],
    }
    print(f"\n[Step 3] POSTing solution to {verify_url}")
    r = session.post(verify_url, data=data, allow_redirects=False)
    print(f"  Status: {r.status_code}")
    print(f"  Headers: {dict(r.headers)}")
    print(f"  Cookies after verify: {dict(session.cookies)}")
    return r.status_code in (200, 302, 303)


def main():
    # Step 1: Initial request → expect Akamai challenge
    print("[Step 1] Fetching detail page...")
    r = session.get(DETAIL_URL)
    print(f"  Status: {r.status_code}, Size: {len(r.text)} bytes")

    is_challenge = len(r.text) < 10000 and ("bm-verify" in r.text or "_sec_cpt" in r.text)
    is_real = len(r.text) > 100000

    if is_real:
        print("  Got real page directly! No Akamai challenge.")
        check_content(r.text)
        return

    if not is_challenge:
        print(f"  Unexpected response. First 500 chars:")
        print(f"  {r.text[:500]}")
        return

    print("  Got Akamai challenge page (as expected)")

    # Step 2: Parse challenge
    print("\n[Step 2] Parsing challenge...")
    challenge = parse_akamai_challenge(r.text)
    if not challenge:
        print("  FAILED to parse challenge. Dumping full HTML:")
        print(r.text)
        return

    # Step 3: Solve and verify
    ok = solve_and_verify(challenge)
    if not ok:
        print("  Verification failed")
        return

    # Step 4: Retry with session cookies
    print("\n[Step 4] Retrying detail page with cookies...")
    r2 = session.get(DETAIL_URL)
    print(f"  Status: {r2.status_code}, Size: {len(r2.text)} bytes")

    if len(r2.text) > 100000:
        print("  SUCCESS — got real page!")
        check_content(r2.text)
    elif "bm-verify" in r2.text:
        print("  Still getting challenge page. Trying different verify approach...")
        # Try with JSON body instead
        challenge2 = parse_akamai_challenge(r2.text)
        if challenge2:
            r3 = session.post(
                f"{BASE_URL}/_sec/verify?provider=interstitial",
                json={"bm-verify": challenge2["token"], "pow": challenge2["answer"]},
                allow_redirects=True,
            )
            print(f"  JSON verify status: {r3.status_code}")
            r4 = session.get(DETAIL_URL)
            print(f"  Retry status: {r4.status_code}, Size: {len(r4.text)} bytes")
            if len(r4.text) > 100000:
                print("  SUCCESS — got real page!")
                check_content(r4.text)
            else:
                print("  Still blocked. Akamai PoW solver approach insufficient.")
    else:
        print(f"  Got unexpected response. First 500 chars:")
        print(f"  {r2.text[:500]}")


def check_content(html: str):
    """Quick validation of extracted content."""
    from selectolax.parser import HTMLParser
    tree = HTMLParser(html)

    addr = tree.css_first(".location-container p")
    print(f"  Address: {addr.text(strip=True) if addr else 'NOT FOUND'}")

    nearby_count = len(tree.css(".place-nearby table tr"))
    print(f"  Nearby places: {nearby_count}")

    deed_found = "โฉนด" in html
    print(f"  Deed info present: {deed_found}")


if __name__ == "__main__":
    main()

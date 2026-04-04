from curl_cffi import requests
import os

url = "https://www.kasikornbank.com/th/propertyforsale/detail/028818655.html"
headers = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.kasikornbank.com/th/propertyforsale/search/pages/index.aspx",
}

# Test 1: chrome120 impersonation
print("=== Test chrome120 ===")
r = requests.get(url, headers=headers, impersonate="chrome120")
print(f"Status: {r.status_code}, Length: {len(r.text)}")
print(f"Contains property data: {'property-detail' in r.text or 'table-detail' in r.text or 'SellPrice' in r.text}")
print(f"Contains Akamai challenge: {'ak_bmsc' in r.text or 'Access Denied' in r.text or '_sec_cpt' in r.text}")

# Test 2: chrome136
print("\n=== Test chrome136 ===")
try:
    r2 = requests.get(url, headers=headers, impersonate="chrome136")
    print(f"Status: {r2.status_code}, Length: {len(r2.text)}")
    print(f"Contains property data: {'property-detail' in r2.text or 'table-detail' in r2.text}")
except Exception as e:
    print(f"Error: {e}")

# Test 3: safari
print("\n=== Test safari ===")
try:
    r3 = requests.get(url, headers=headers, impersonate="safari15_5")
    print(f"Status: {r3.status_code}, Length: {len(r3.text)}")
    print(f"Contains property data: {'property-detail' in r3.text or 'table-detail' in r3.text}")
except Exception as e:
    print(f"Error: {e}")

# If any succeeded, save HTML and check for key fields
for name, resp in [("chrome120", r)]:
    if resp.status_code == 200 and len(resp.text) > 10000:
        outpath = "/Users/arsapolm/.nanobot-npa-guy/workspace/skills/kbank-scraper/recon/detail_curl_cffi.html"
        with open(outpath, "w") as f:
            f.write(resp.text)
        print(f"\nSaved to {outpath}")
        # Check for key data
        from selectolax.parser import HTMLParser
        tree = HTMLParser(resp.text)
        # Look for price, address, title deed
        for sel in ["div.table-detail", "div.icon-detail-wrapper", "span.price", ".property-info", "script[type='application/ld+json']"]:
            nodes = tree.css(sel)
            if nodes:
                print(f"\n{sel}: {len(nodes)} matches")
                print(f"  Sample: {nodes[0].text()[:200]}")

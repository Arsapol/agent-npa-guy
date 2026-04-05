"""Quick check: what does the 500 response contain?"""
import httpx
import json

BASE_URL = "https://www.jjpropertythai.com/api/proxy/v1"
HEADERS = {
    "Accept": "application/json",
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Referer": "https://www.jjpropertythai.com/Search",
}

resp = httpx.get(
    f"{BASE_URL}/assets",
    params={"freeText": "", "page": 1, "user_code": "521789", "limit": 2, "SellingStart": 0, "SellingEnd": 100000000, "typeSaleIn[]": "3"},
    headers=HEADERS,
)
print(f"Status: {resp.status_code}")
print(f"Headers: {dict(resp.headers)}")
print(f"Body: {resp.text[:1000]}")
print(f"\nContent-Type: {resp.headers.get('content-type')}")

# Also try the direct backend API
print("\n--- Trying direct backend ---")
resp2 = httpx.get(
    "https://api.jjpropertythai.com/baanbaan/v1/assets",
    params={"freeText": "", "page": 1, "user_code": "521789", "limit": 2, "SellingStart": 0, "SellingEnd": 100000000, "typeSaleIn[]": "3"},
    headers={
        "Accept": "application/json",
        "User-Agent": HEADERS["User-Agent"],
        "Origin": "https://www.jjpropertythai.com",
        "Referer": "https://www.jjpropertythai.com/",
    },
)
print(f"Status: {resp2.status_code}")
print(f"Body: {resp2.text[:1000]}")

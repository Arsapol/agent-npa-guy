"""
SCB NPA API test suite — asset.home.scb
Run: python test_api.py
"""
import httpx
import json
import re
import sys
from selectolax.parser import HTMLParser

BASE_URL = "https://asset.home.scb/"
API_URL = f"{BASE_URL}api/project/cmd"

client = httpx.Client(timeout=30, follow_redirects=True)
passed = 0
failed = 0


def test(name: str, condition: bool, detail: str = ""):
    global passed, failed
    if condition:
        passed += 1
        print(f"  PASS  {name}")
    else:
        failed += 1
        print(f"  FAIL  {name} — {detail}")


def api_get(params: dict) -> dict:
    r = client.get(API_URL, params=params)
    return r.json()


# --- 1. List endpoint ---
print("\n=== 1. List endpoint (get_project) ===")
data = api_get({"command": "get_project", "type": "project", "page": 1, "limit": 5})
test("returns success", data.get("s") == "y")
test("has total count", isinstance(data.get("total"), int) and data["total"] > 0, f"total={data.get('total')}")
test("returns items", isinstance(data.get("d"), list) and len(data["d"]) == 5, f"len={len(data.get('d', []))}")

item = data["d"][0]
required_list_fields = [
    "project_id", "project_type", "project_title", "price", "latitude",
    "longitude", "province_id", "district_id", "area_use", "land_area",
    "slug", "image_use", "project_id_gen", "project_sold_out",
    "project_address", "project_address_detail", "create_date",
]
for field in required_list_fields:
    test(f"list has field '{field}'", field in item, f"missing from keys: {list(item.keys())}")


# --- 2. Pagination ---
print("\n=== 2. Pagination ===")
p1 = api_get({"command": "get_project", "type": "project", "page": 1, "limit": 3})
p2 = api_get({"command": "get_project", "type": "project", "page": 2, "limit": 3})
ids_p1 = {i["project_id"] for i in p1["d"]}
ids_p2 = {i["project_id"] for i in p2["d"]}
test("page 1 and 2 have different items", ids_p1.isdisjoint(ids_p2), f"overlap: {ids_p1 & ids_p2}")
test("large page size works (200)", len(api_get({
    "command": "get_project", "type": "project", "page": 1, "limit": 200,
})["d"]) == 200)


# --- 3. Asset type filter ---
print("\n=== 3. Asset type filter ===")
working_types = {
    "condominiums": 500,
    "single_houses": 500,
    "townhouses": 500,
    "duplex_homes": 50,
    "vacant_land": 50,
}
total_all = api_get({"command": "get_project", "type": "project", "page": 1, "limit": 1})["total"]
for atype, min_count in working_types.items():
    result = api_get({
        "command": "get_project", "type": "project", "page": 1, "limit": 1,
        "asset-type": atype,
    })
    total = result.get("total", 0)
    test(f"asset-type={atype} filters correctly", total < total_all and total >= min_count,
         f"total={total}, expected >= {min_count} and < {total_all}")


# --- 4. Province filter ---
print("\n=== 4. Province filter ===")
bkk = api_get({
    "command": "get_project", "type": "project", "page": 1, "limit": 1,
    "asset-location": "1",
})
test("Bangkok filter works (province_id=1)", bkk["total"] > 100 and bkk["total"] < total_all,
     f"total={bkk.get('total')}")

# District filter
district = api_get({
    "command": "get_project", "type": "project", "page": 1, "limit": 1,
    "asset-location": "1-1018",
})
test("District filter works (1-1018)", district["total"] > 0 and district["total"] < bkk["total"],
     f"total={district.get('total')}")


# --- 5. Price filter ---
print("\n=== 5. Price filter ===")
cheap = api_get({
    "command": "get_project", "type": "project", "page": 1, "limit": 1,
    "price-min": 1000000, "price-max": 3000000,
})
test("price filter works (1M-3M)", cheap["total"] > 0 and cheap["total"] < total_all,
     f"total={cheap.get('total')}")


# --- 6. Area filter ---
print("\n=== 6. Area filter ===")
small_condo = api_get({
    "command": "get_project", "type": "project", "page": 1, "limit": 1,
    "asset-type": "condominiums", "use-area-min": "20", "use-area-max": "40",
})
test("usable area filter works", small_condo["total"] > 0, f"total={small_condo.get('total')}")


# --- 7. Text search ---
print("\n=== 7. Text search ===")
text_search = api_get({
    "command": "get_project", "type": "project", "page": 1, "limit": 1,
    "find-search-text": "สุขุมวิท",
})
test("text search works", text_search["total"] > 0 and text_search["total"] < total_all,
     f"total={text_search.get('total')}")


# --- 8. Province list ---
print("\n=== 8. Province list ===")
provinces = api_get({"command": "get_province"})
test("province list returns data", provinces.get("s") == "y" and len(provinces.get("d", [])) == 77)
bkk_prov = [p for p in provinces["d"] if p["title"] == "กรุงเทพมหานคร"]
test("Bangkok is province_id=1", len(bkk_prov) == 1 and bkk_prov[0]["province_id"] == 1)


# --- 9. District list ---
print("\n=== 9. District list ===")
districts = api_get({"command": "get_district", "province_id": "1"})
test("district list for Bangkok", districts.get("s") == "y" and len(districts.get("d", [])) > 40,
     f"count={len(districts.get('d', []))}")


# --- 10. Suggest/autocomplete ---
print("\n=== 10. Suggest/autocomplete ===")
suggest = api_get({"command": "get_suggest", "k": "พลัม"})
test("suggest returns results", suggest.get("s") == "y" and len(suggest.get("d", [])) > 0,
     f"count={len(suggest.get('d', []))}")


# --- 11. Detail page HTML parsing ---
print("\n=== 11. Detail page HTML parsing ===")
# Get a condo from the list
condo_list = api_get({
    "command": "get_project", "type": "project", "page": 1, "limit": 1,
    "asset-type": "condominiums", "asset-location": "1",
})
condo = condo_list["d"][0]
slug = condo["slug"]

r = client.get(f"{BASE_URL}project/{slug}")
test("detail page loads", r.status_code == 200)

tree = HTMLParser(r.text)

# Hidden inputs
pid_el = tree.css_first('input[id="pid"]')
test("has pid hidden input", pid_el is not None and pid_el.attributes.get("value", "") != "")

lat_el = tree.css_first('input[id="lat"]')
test("has lat hidden input", lat_el is not None and lat_el.attributes.get("value", "") != "")

code_el = tree.css_first('input[id="txt-project-code"]')
test("has txt-project-code input", code_el is not None and code_el.attributes.get("value", "") != "")

# Detail text parsing
detail_div = tree.css_first(".project_detailed")
test("has .project_detailed div", detail_div is not None)

if detail_div:
    detail_text = detail_div.text(strip=True)
    test("detail has รหัส (code)", "รหัส:" in detail_text)
    test("detail has เอกสารสิทธิ์ (title deed)", "เอกสารสิทธิ์:" in detail_text)
    test("detail has พื้นที่ใช้สอย (usable area)", "พื้นที่ใช้สอย:" in detail_text)

    bedrooms_match = re.search(r"ห้องนอน:(\d+)", detail_text)
    test("can parse bedrooms", bedrooms_match is not None, f"text sample: {detail_text[:100]}")

# Images
images = tree.css('img[src*="stocks/project"], [data-src*="stocks/project"]')
test("detail page has property images", len(images) > 0, f"found {len(images)}")


# --- 12. Sort options ---
print("\n=== 12. Sort options ===")
asc = api_get({
    "command": "get_project", "type": "project", "page": 1, "limit": 3,
    "sortBy": "price_asc",
})
desc = api_get({
    "command": "get_project", "type": "project", "page": 1, "limit": 3,
    "sortBy": "price_desc",
})
test("sort options return data", len(asc["d"]) == 3 and len(desc["d"]) == 3)


# --- Summary ---
print(f"\n{'='*50}")
print(f"Results: {passed} passed, {failed} failed, {passed + failed} total")
if failed > 0:
    sys.exit(1)

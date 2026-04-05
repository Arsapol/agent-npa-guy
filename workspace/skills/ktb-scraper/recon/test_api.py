"""KTB NPA API endpoint probe — comprehensive recon.

Discovered API structure from JS bundles (dfc348a.js):

Services:
  PRODUCT_SERVICE  = /api/v1/product
  SYSTEM_SERVICE   = /api/v1/system
  CONTENT_SERVICE  = /api/v1/content
  PAYMENT_SERVICE  = /api/v1/payment
  BIDDING_SERVICE  = /api/v1/bidding
  KKAPI_SERVICE    = /api/v1/kkapi
  USER_SERVICE     = /api/v1/user
  REPORT_SERVICE   = /api/v1/report

Product endpoints (POST unless noted):
  /searchAll          — all properties (no filter)
  /promotionSale      — promotion properties
  /flashSale          — flash sale properties
  /mortgageSale       — mortgage for sale
  /ledSale            — auction properties
  /searchSaleDetail   — property detail {speedDy, collGrpId, cateNo}
  /getProductDetailOffer — detail for offers (auth required)
  /searchAllByAssetCodes — search by asset code
  /searchAllByAssetCodeAll
  /getProductBidding  — bidding properties
  /getContact         — contact info {collGrpId}
  /homePage           — homepage data

Product endpoints (GET):
  /getPromotionDropdown
  /getCategoryList    — (401, use system service instead)
  /getProductBiddingDetail?productId=X
  /viewprop/getCollDataByRadius/{lat}/{lon}/{radius}/{?}

System endpoints (GET):
  /getCategoryList            — 26 property categories
  /DopaProvince/dopaProvinceListNew/detail — 77 provinces + districts

searchAll body (from getCondition in chunk 105):
  {
    collCode: str|null,         # asset code
    search: str|null,           # keyword
    shrProvince: str|null,      # province value from dropdown
    shrAmphur: str|null,        # district value from dropdown
    typeProp: str[]|[],         # array of cateNo strings
    priceRangeMin: str|null,    # min price text (e.g. "100001")
    priceRangeMax: str|null,    # max price text
    orderBy: str|null,          # priceMin|priceMax|areaMin|areaMax|collCodeMin|collCodeMax
    lat: float|null,            # for map mode
    lon: float|null,
    station: str|null,          # BTS/MRT station
    nearHospitalDist: ?|null,
    nearSchoolDist: ?|null,
    nearShopDist: ?|null,
    paging: {totalRows: 0, rowsPerPage: N, currentPage: N}
  }
"""

import asyncio
import json
import os
from pathlib import Path
from typing import Any

import httpx

SITE = "https://npa.krungthai.com"
RECON_DIR = Path(__file__).parent

HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    ),
    "Origin": SITE,
    "Referer": f"{SITE}/property",
    "Role": "",
    "User-Id": "-",
}


def summarize(name: str, data: Any) -> None:
    """Print a concise summary of the response structure."""
    print(f"\n{'='*60}")
    print(f"  {name}")
    print(f"{'='*60}")
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, list):
                print(f"  {k}: list[{len(v)} items]")
                if v and isinstance(v[0], dict):
                    print(f"    keys: {list(v[0].keys())}")
                    for fk, fv in list(v[0].items())[:10]:
                        sv = str(fv)[:100] if fv is not None else "null"
                        print(f"      {fk}: {type(fv).__name__} = {sv}")
                    if len(v[0]) > 10:
                        print(f"      ... +{len(v[0])-10} more keys")
                elif v:
                    print(f"    [0]: {v[0]}")
            elif isinstance(v, dict):
                print(f"  {k}: dict {list(v.keys())}")
                for dk, dv in list(v.items())[:5]:
                    print(f"    {dk}: {str(dv)[:80]}")
            else:
                print(f"  {k}: {type(v).__name__} = {str(v)[:120]}")
    elif isinstance(data, list):
        print(f"  list[{len(data)} items]")
        if data and isinstance(data[0], dict):
            print(f"    keys: {list(data[0].keys())}")
            for fk, fv in list(data[0].items())[:8]:
                print(f"      {fk}: {str(fv)[:80]}")
    else:
        print(f"  {type(data).__name__}: {str(data)[:200]}")


async def probe(
    client: httpx.AsyncClient,
    name: str,
    method: str,
    path: str,
    body: dict | None = None,
) -> Any:
    """Fetch an endpoint and save + summarize the response."""
    url = f"{SITE}{path}"
    print(f"\n>>> {method} {url}")
    if body:
        print(f"    body: {json.dumps(body, ensure_ascii=False)[:200]}")
    try:
        resp = await client.request(method, url, json=body, timeout=30)
        print(f"    status: {resp.status_code}")
        out_path = RECON_DIR / f"{name}.json"

        try:
            data = resp.json()
        except Exception:
            data = {"_raw_text": resp.text[:2000], "_status": resp.status_code}

        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"    saved: {out_path.name} ({os.path.getsize(out_path)} bytes)")
        summarize(name, data)
        return data

    except Exception as e:
        print(f"    ERROR: {e}")
        return None


def paging(rows: int = 2, page: int = 1) -> dict:
    return {"totalRows": 0, "rowsPerPage": rows, "currentPage": page}


async def main() -> None:
    async with httpx.AsyncClient(headers=HEADERS, verify=False) as client:
        # ─── 1. Reference data ───────────────────────────────────────
        print("\n" + "=" * 60)
        print("  REFERENCE DATA")
        print("=" * 60)

        await probe(client, "getCategoryList", "GET",
                     "/api/v1/system/getCategoryList")

        await probe(client, "dopaProvinceListNew", "GET",
                     "/api/v1/system/DopaProvince/dopaProvinceListNew/detail")

        await probe(client, "getPromotionDropdown", "GET",
                     "/api/v1/product/getPromotionDropdown")

        # ─── 2. Search endpoints (unfiltered) ────────────────────────
        print("\n" + "=" * 60)
        print("  SEARCH ENDPOINTS (unfiltered, 2 per page)")
        print("=" * 60)

        await probe(client, "searchAll", "POST",
                     "/api/v1/product/searchAll",
                     {"paging": paging()})

        await probe(client, "promotionSale", "POST",
                     "/api/v1/product/promotionSale",
                     {"paging": paging()})

        await probe(client, "flashSale", "POST",
                     "/api/v1/product/flashSale",
                     {"paging": paging()})

        await probe(client, "mortgageSale", "POST",
                     "/api/v1/product/mortgageSale",
                     {"paging": paging()})

        await probe(client, "ledSale", "POST",
                     "/api/v1/product/ledSale",
                     {"paging": paging()})

        await probe(client, "homePage", "POST",
                     "/api/v1/product/homePage",
                     {"paging": paging()})

        # ─── 3. Filtered search (Bangkok condos) ─────────────────────
        print("\n" + "=" * 60)
        print("  FILTERED SEARCH (Bangkok, condo)")
        print("=" * 60)

        await probe(client, "searchAll_bkk_condo", "POST",
                     "/api/v1/product/searchAll",
                     {
                         "shrProvince": "10",
                         "typeProp": ["11"],  # คอนโดมิเนียม
                         "paging": paging(),
                     })

        await probe(client, "searchAll_bkk_house", "POST",
                     "/api/v1/product/searchAll",
                     {
                         "shrProvince": "10",
                         "typeProp": ["3"],  # บ้านเดี่ยว
                         "paging": paging(),
                     })

        # With price range
        await probe(client, "searchAll_bkk_price", "POST",
                     "/api/v1/product/searchAll",
                     {
                         "shrProvince": "10",
                         "priceRangeMin": "1000001",
                         "priceRangeMax": "3000000",
                         "paging": paging(),
                     })

        # ─── 4. Property detail ──────────────────────────────────────
        print("\n" + "=" * 60)
        print("  PROPERTY DETAIL")
        print("=" * 60)

        # First get a property ID
        search_data = await probe(client, "_temp_search", "POST",
                                   "/api/v1/product/searchAll",
                                   {"paging": paging(1)})

        if search_data and isinstance(search_data, dict):
            item = search_data.get("dataResponse", [{}])[0]
            coll_grp_id = item.get("collGrpId")
            cate_no = item.get("collCateNo") or item.get("cateNo")
            is_speedy = item.get("isSpeedy")
            print(f"\n  Using: collGrpId={coll_grp_id}, cateNo={cate_no}, isSpeedy={is_speedy}")

            # searchSaleDetail with full params
            await probe(client, "searchSaleDetail", "POST",
                         "/api/v1/product/searchSaleDetail",
                         {
                             "collGrpId": coll_grp_id,
                             "cateNo": cate_no,
                             "speedDy": is_speedy or "0",
                         })

            # getContact
            await probe(client, "getContact", "POST",
                         "/api/v1/product/getContact",
                         {"collGrpId": coll_grp_id})

        # ─── 5. Nearby properties ────────────────────────────────────
        print("\n" + "=" * 60)
        print("  NEARBY PROPERTIES (by radius)")
        print("=" * 60)

        # viewprop/getCollDataByRadius/{lat}/{lon}/{radius}/{?}
        await probe(client, "getCollDataByRadius", "GET",
                     "/api/v1/product/viewprop/getCollDataByRadius/13.7563/100.5018/5/10")

        # ─── Summary ─────────────────────────────────────────────────
        print("\n\n" + "=" * 60)
        print("  FILES SAVED")
        print("=" * 60)
        for f in sorted(RECON_DIR.glob("*.json")):
            if not f.name.startswith("_"):
                print(f"  {f.name:40s} {os.path.getsize(f):>8,d} bytes")


if __name__ == "__main__":
    asyncio.run(main())

"""Fetch KTB NPA sample responses and produce detailed field analysis."""

import asyncio
import json
import os
from pathlib import Path
from typing import Any

import httpx

SITE = "https://npa.krungthai.com"
RECON = Path(__file__).parent

HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json, text/plain, */*",
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36"
    ),
    "Origin": SITE,
    "Referer": f"{SITE}/property",
    "Role": "",
    "User-Id": "-",
}

ENDPOINTS: list[dict] = [
    {
        "name": "sample_searchAll",
        "method": "POST",
        "path": "/api/v1/product/searchAll",
        "body": {"paging": {"totalRows": 0, "rowsPerPage": 2, "currentPage": 1}},
    },
    {
        "name": "sample_detail",
        "method": "POST",
        "path": "/api/v1/product/searchSaleDetail",
        "body": {"speedDy": 0, "collGrpId": "230741", "cateNo": 3},
    },
    {
        "name": "sample_categories",
        "method": "GET",
        "path": "/api/v1/system/getCategoryList",
    },
    {
        "name": "sample_provinces",
        "method": "GET",
        "path": "/api/v1/system/DopaProvince/dopaProvinceListNew/detail",
        "params": {
            "amphurCode": "",
            "provinceCode": "",
            "tambonCode": "",
            "zipCode": "",
        },
    },
    {
        "name": "sample_promotionSale",
        "method": "POST",
        "path": "/api/v1/product/promotionSale",
        "body": {"paging": {"totalRows": 0, "rowsPerPage": 2, "currentPage": 1}},
    },
]


def analyze_value(val: Any, indent: int = 4) -> str:
    """Return a type descriptor + sample for a single value."""
    pad = " " * indent
    if val is None:
        return "NoneType = null"
    if isinstance(val, bool):
        return f"bool = {val}"
    if isinstance(val, int):
        return f"int = {val}"
    if isinstance(val, float):
        return f"float = {val}"
    if isinstance(val, str):
        sample = val[:100]
        return f'str = "{sample}"'
    if isinstance(val, list):
        if not val:
            return "list = [] (empty)"
        elem = val[0]
        if isinstance(elem, dict):
            lines = [f"list[{len(val)} x dict]"]
            for k2, v2 in elem.items():
                lines.append(f"{pad}  {k2}: {analyze_value(v2, indent + 2)}")
            return "\n".join(lines)
        return f"list[{len(val)} x {type(elem).__name__}] first={str(elem)[:80]}"
    if isinstance(val, dict):
        lines = [f"dict ({len(val)} keys)"]
        for k2, v2 in val.items():
            lines.append(f"{pad}  {k2}: {analyze_value(v2, indent + 2)}")
        return "\n".join(lines)
    return f"{type(val).__name__} = {str(val)[:100]}"


def full_analysis(label: str, data: Any) -> None:
    """Print a detailed field-by-field analysis."""
    print(f"\n{'='*70}")
    print(f"  FIELD ANALYSIS: {label}")
    print(f"{'='*70}")

    if isinstance(data, dict):
        for k, v in data.items():
            print(f"\n  {k}: {analyze_value(v)}")
    elif isinstance(data, list):
        print(f"\n  top-level list[{len(data)} items]")
        if data and isinstance(data[0], dict):
            print(f"  Analyzing first element:\n")
            for k, v in data[0].items():
                print(f"  {k}: {analyze_value(v)}")
    else:
        print(f"  {type(data).__name__}: {str(data)[:200]}")


async def fetch_and_save(
    client: httpx.AsyncClient,
    ep: dict,
) -> Any:
    url = f"{SITE}{ep['path']}"
    method = ep["method"]
    body = ep.get("body")
    params = ep.get("params")
    name = ep["name"]

    print(f"\n>>> {method} {url}")
    if body:
        print(f"    body: {json.dumps(body)[:150]}")

    resp = await client.request(method, url, json=body, params=params, timeout=30)
    print(f"    status: {resp.status_code}")

    try:
        data = resp.json()
    except Exception:
        data = {"_raw": resp.text[:3000], "_status": resp.status_code}

    out = RECON / f"{name}.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"    saved: {out.name} ({os.path.getsize(out):,} bytes)")
    return data


async def main() -> None:
    results: dict[str, Any] = {}

    async with httpx.AsyncClient(headers=HEADERS, verify=False) as client:
        for ep in ENDPOINTS:
            results[ep["name"]] = await fetch_and_save(client, ep)

    # Detailed analysis for searchAll
    sa = results.get("sample_searchAll")
    if isinstance(sa, dict) and "dataResponse" in sa:
        full_analysis("searchAll > dataResponse[0]", sa["dataResponse"])
        full_analysis("searchAll > paging", sa.get("paging"))

    # Detailed analysis for detail
    det = results.get("sample_detail")
    if isinstance(det, list) and det:
        full_analysis("searchSaleDetail[0]", det)
    elif isinstance(det, dict):
        full_analysis("searchSaleDetail", det)

    # Category list
    cats = results.get("sample_categories")
    if isinstance(cats, list):
        full_analysis("getCategoryList", cats)

    # Province list (just structure, not all 77)
    prov = results.get("sample_provinces")
    if isinstance(prov, dict) and "data" in prov:
        full_analysis("dopaProvinceListNew > data", prov["data"][:2])

    # Promotion sale
    promo = results.get("sample_promotionSale")
    if isinstance(promo, dict) and "dataResponse" in promo:
        full_analysis("promotionSale > dataResponse[0]", promo["dataResponse"])

    # Summary table
    print(f"\n\n{'='*70}")
    print("  SAVED FILES")
    print(f"{'='*70}")
    for f in sorted(RECON.glob("sample_*.json")):
        print(f"  {f.name:40s} {os.path.getsize(f):>10,} bytes")


if __name__ == "__main__":
    asyncio.run(main())

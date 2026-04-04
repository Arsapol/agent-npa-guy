"""KBank NPA API recon — test endpoint and discover filter keys."""

import asyncio
import json
import pathlib

import httpx

BASE_URL = "https://www.kasikornbank.com/Custom/KWEB2020/NPA2023Backend13.aspx/GetProperties"

HEADERS = {
    "content-type": "application/json",
    "accept": "*/*",
    "x-requested-with": "XMLHttpRequest",
    "user-agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36"
    ),
}

RECON_DIR = pathlib.Path(__file__).parent


async def post(client: httpx.AsyncClient, body: dict, label: str) -> dict | None:
    """POST to KBank API, pretty-print, and save response."""
    print(f"\n{'='*60}")
    print(f"TEST: {label}")
    print(f"BODY: {json.dumps(body, ensure_ascii=False)}")
    print(f"{'='*60}")

    try:
        resp = await client.post(BASE_URL, json=body, headers=HEADERS, timeout=30)
        print(f"STATUS: {resp.status_code}")

        try:
            data = resp.json()
        except Exception:
            print(f"RAW TEXT (first 2000 chars):\n{resp.text[:2000]}")
            return None

        pretty = json.dumps(data, indent=2, ensure_ascii=False)
        print(pretty[:3000])
        if len(pretty) > 3000:
            print(f"\n... (truncated, full length {len(pretty)} chars)")

        out_path = RECON_DIR / f"{label}.json"
        out_path.write_text(pretty, encoding="utf-8")
        print(f"Saved to {out_path}")
        return data

    except Exception as exc:
        print(f"ERROR: {exc}")
        return None


async def main():
    async with httpx.AsyncClient(http2=True, follow_redirects=True) as client:
        # 1. Basic request — page 1, 20 items
        await post(
            client,
            {"filter": {"PageSize": 20, "SearchPurposes": ["AllProperties"]}},
            "basic_page1",
        )

        # 2. Pagination — page 2, 5 items
        await post(
            client,
            {"filter": {"PageSize": 5, "PageNo": 2, "SearchPurposes": ["AllProperties"]}},
            "pagination_page2",
        )

        # 3. Filter by province (Bangkok)
        await post(
            client,
            {"filter": {"PageSize": 5, "SearchPurposes": ["AllProperties"], "Province": "กรุงเทพมหานคร"}},
            "filter_province_bkk",
        )

        # 4. Filter by property type — try common Thai terms
        await post(
            client,
            {"filter": {"PageSize": 5, "SearchPurposes": ["AllProperties"], "PropertyType": "คอนโดมิเนียม"}},
            "filter_type_condo",
        )

        # 5. Try SearchPurposes variations
        await post(
            client,
            {"filter": {"PageSize": 5, "SearchPurposes": ["Condo"]}},
            "filter_purpose_condo",
        )

        # 6. Try with price range
        await post(
            client,
            {"filter": {"PageSize": 5, "SearchPurposes": ["AllProperties"], "PriceMin": 1000000, "PriceMax": 3000000}},
            "filter_price_range",
        )

        # 7. Try with keyword search
        await post(
            client,
            {"filter": {"PageSize": 5, "SearchPurposes": ["AllProperties"], "Keyword": "สุขุมวิท"}},
            "filter_keyword",
        )

        # 8. Empty filter to see defaults
        await post(
            client,
            {"filter": {}},
            "filter_empty",
        )

        # 9. Try district filter
        await post(
            client,
            {"filter": {"PageSize": 5, "SearchPurposes": ["AllProperties"], "Province": "กรุงเทพมหานคร", "District": "จตุจักร"}},
            "filter_district",
        )

        # 10. Minimal — just PageSize
        await post(
            client,
            {"filter": {"PageSize": 3}},
            "filter_minimal",
        )


if __name__ == "__main__":
    asyncio.run(main())

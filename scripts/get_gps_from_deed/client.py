"""Async httpx client for landsmaps.dol.go.th parcel lookup."""

from __future__ import annotations

import httpx

from models import ApiResponse, DeedQuery, ParcelResult

BASE_URL = "https://landsmaps.dol.go.th/apiService/LandsMaps"

COMMON_HEADERS = {
    "accept": "application/json, text/javascript, */*; q=0.01",
    "referer": "https://landsmaps.dol.go.th/",
    "x-requested-with": "XMLHttpRequest",
    "user-agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/147.0.0.0 Safari/537.36"
    ),
}


class LandsMapsClient:
    """Client for the DOL LandsMaps parcel API."""

    def __init__(self, token: str) -> None:
        self._token = token
        self._headers = {
            **COMMON_HEADERS,
            "authorization": f"Bearer {token}",
        }

    async def get_parcel(self, query: DeedQuery) -> ParcelResult | None:
        """Fetch parcel info by deed number. Returns None if not found."""
        url = (
            f"{BASE_URL}/GetParcelByParcelNo"
            f"/{query.province_code}/{query.amphur_code}/{query.parcel_no}"
        )
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(url, headers=self._headers)
            resp.raise_for_status()

        api_resp = ApiResponse.model_validate(resp.json())

        if api_resp.error:
            raise RuntimeError(f"API error: {api_resp.message}")

        if not api_resp.result:
            return None

        return api_resp.result[0]

    async def get_parcels_batch(
        self, queries: list[DeedQuery]
    ) -> list[tuple[DeedQuery, ParcelResult | None, str | None]]:
        """Fetch multiple parcels. Returns list of (query, result, error_msg)."""
        results: list[tuple[DeedQuery, ParcelResult | None, str | None]] = []

        async with httpx.AsyncClient(timeout=30.0) as client:
            for query in queries:
                url = (
                    f"{BASE_URL}/GetParcelByParcelNo"
                    f"/{query.province_code}/{query.amphur_code}/{query.parcel_no}"
                )
                try:
                    resp = await client.get(url, headers=self._headers)
                    resp.raise_for_status()
                    api_resp = ApiResponse.model_validate(resp.json())

                    if api_resp.error:
                        results.append((query, None, f"API error: {api_resp.message}"))
                    elif not api_resp.result:
                        results.append((query, None, "No result found"))
                    else:
                        results.append((query, api_resp.result[0], None))
                except httpx.HTTPStatusError as exc:
                    results.append((query, None, f"HTTP {exc.response.status_code}"))
                except Exception as exc:
                    results.append((query, None, str(exc)))

        return results

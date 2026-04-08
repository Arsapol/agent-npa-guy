"""
Multi-type NPA property extraction for Screener v2.

Thin wrapper around adapter_bridge — all provider-specific SQL
is now handled by the unified npa-adapter.

Usage:
    from extract_v2 import extract_all_properties
    candidates = extract_all_properties(conn, provinces=["กรุงเทพมหานคร"])
"""

from __future__ import annotations

from typing import Any

from adapter_bridge import ALL_SOURCES, extract_candidates
from models_v2 import NpaCandidate


def extract_all_properties(
    conn: Any,
    provinces: list[str],
    max_price: float | None = None,
    property_types: list[str] | None = None,
) -> list[NpaCandidate]:
    """Extract NPA properties from all providers via adapter.

    Args:
        conn: DB connection (kept for backward compat, unused — adapter
              manages its own connections).
        provinces: Thai province names to filter on.
        max_price: Optional upper price bound in baht.
        property_types: Optional list of PropertyType values
                        (e.g. ["condo", "house"]). None = all types.

    Returns:
        List of NpaCandidate with price, vintage, and auction_round populated.
    """
    return extract_candidates(
        provinces=provinces,
        max_price=max_price,
        property_types=property_types,
        sources=ALL_SOURCES,
    )

"""
Shared helpers for SAM NPA scraper — selectolax + httpx utilities.
"""

from __future__ import annotations

import re

import httpx
from selectolax.parser import HTMLParser, Node


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/146.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "th,en-US;q=0.9,en;q=0.8",
    "Referer": "https://sam.or.th/site/npa/page_list.php",
    "Origin": "https://sam.or.th",
}


def create_http_client() -> httpx.AsyncClient:
    """Create an httpx.AsyncClient with retry transport and shared headers."""
    transport = httpx.AsyncHTTPTransport(retries=3)
    return httpx.AsyncClient(
        headers=HEADERS,
        timeout=httpx.Timeout(30.0),
        transport=transport,
        follow_redirects=True,
    )


def text_of(node: Node | None, strip: bool = True) -> str:
    """Safe text extraction from a selectolax Node."""
    if node is None:
        return ""
    t = node.text(strip=strip)
    return (t or "").strip() if strip else (t or "")


def attr_of(node: Node | None, key: str, default: str = "") -> str:
    """Safe attribute access on a selectolax Node."""
    if node is None:
        return default
    attrs = node.attributes
    return attrs.get(key, default) or default


def find_span_after_label(container: Node, label_pattern: str) -> str:
    """
    selectolax equivalent of bs4's:
        text_node = container.find(string=re.compile(label_pattern))
        span = text_node.find_next("span")
        return span.get_text(strip=True)

    Strategy: regex-search the raw HTML for the label, then parse the
    remainder to find the next <span>. selectolax's lexbor parser handles
    small fragments in microseconds, so re-parsing is negligible vs network I/O.
    """
    html = container.html
    if html is None:
        return ""
    match = re.search(label_pattern, html)
    if not match:
        return ""
    remainder = html[match.start():]
    sub_tree = HTMLParser(remainder)
    span = sub_tree.css_first("span")
    if span is None:
        return ""
    return (span.text(strip=True) or "").strip()

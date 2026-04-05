"""
Hipflat.co.th market price checker for NPA condo screening.

Usage:
    python hipflat_checker.py "15 sukhumvit residences"
    python hipflat_checker.py "inspire place abac"
    python hipflat_checker.py "ลุมพินี สวีท สุขุมวิท 41"

Returns avg price/sqm, rental range, active listings, price trend, district avg.
No cookies, no JS execution. Two HTTP requests per lookup.
"""

import json
import re
import sys
import time
import urllib.parse
import urllib.request
from typing import Optional

from pydantic import BaseModel

BROWSER_UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/121.0.0.0 Safari/537.36"
)

BASE_HEADERS = {
    "User-Agent": BROWSER_UA,
    "Accept-Language": "th,en;q=0.9",
    "Referer": "https://www.hipflat.co.th/",
}

HIPFLAT_BASE = "https://www.hipflat.co.th"


class HipflatProject(BaseModel):
    uuid: str
    name_th: str
    name_en: str
    slug_url: str

    # Current listing prices
    avg_sale_sqm_thb: Optional[int] = None  # current listing avg (฿/sqm)
    sale_price_min: Optional[int] = None
    sale_price_max: Optional[int] = None
    units_for_sale: Optional[int] = None
    units_for_rent: Optional[int] = None
    rent_price_min: Optional[int] = None
    rent_price_max: Optional[int] = None

    # Historical transaction data
    avg_sold_sqm_thb: Optional[int] = None  # historical txn avg (฿/sqm)
    sold_below_asking_pct: Optional[float] = None
    avg_days_on_market: Optional[int] = None

    # Price trends
    price_trend: Optional[str] = None  # "ขาขึ้น" or "ขาลง"
    yoy_change_pct: Optional[float] = None  # YoY % change

    # Project specs
    year_completed: Optional[int] = None
    floors: Optional[int] = None
    total_units: Optional[int] = None
    service_charge_sqm: Optional[int] = None

    # District benchmarks
    district_avg_sale_sqm: Optional[int] = None
    district_avg_rent_sqm: Optional[int] = None
    district_name: Optional[str] = None

    def to_dict(self) -> dict:
        return {k: v for k, v in self.model_dump().items() if v is not None}


def _fetch(url: str, accept: str = "text/html") -> bytes:
    headers = {**BASE_HEADERS, "Accept": accept}
    req = urllib.request.Request(url, headers=headers)
    resp = urllib.request.urlopen(req, timeout=15)
    return resp.read()


def _int(s: str) -> int:
    return int(s.replace(",", "").replace(" ", ""))


def search_project(query: str) -> list[dict]:
    """Search Hipflat for a project by name. Returns list of matches with uuid + name."""
    encoded = urllib.parse.quote(query)
    url = f"{HIPFLAT_BASE}/api/geo?projects=true&q={encoded}"
    data = json.loads(_fetch(url, accept="application/json"))
    return [r for r in data if r.get("categoryId") == 2]


def _strip_tags(html: str) -> str:
    """Remove HTML tags and normalize whitespace."""
    text = re.sub(r"<[^>]+>", " ", html)
    return re.sub(r"\s+", " ", text)


def fetch_project_data(uuid: str) -> HipflatProject:
    """Fetch all available market data for a project by UUID."""
    url = f"{HIPFLAT_BASE}/projects/{uuid}"
    raw = _fetch(url, accept="text/html,application/xhtml+xml")
    html = raw.decode("utf-8", errors="replace")
    # Strip-tag version for text-based patterns (avoids HTML tag interference)
    text = _strip_tags(html)

    # Parse slug from canonical link
    slug_match = re.search(r'<link rel="canonical"\s+href="([^"]+)"', html)
    slug_url = slug_match.group(1) if slug_match else f"{HIPFLAT_BASE}/projects/{uuid}"

    # --- Project name ---
    h1_match = re.search(r"<h1[^>]*>([^<]+)</h1>", html)
    full_name = h1_match.group(1).strip() if h1_match else ""
    # Format: "15 Sukhumvit Residences (15 สุขุมวิท เรสซิเด็นท์)"
    en_match = re.match(r"^(.+?)\s*\(", full_name)
    th_match = re.search(r"\((.+?)\)\s*$", full_name)
    name_en = en_match.group(1).strip() if en_match else full_name
    name_th = th_match.group(1).strip() if th_match else full_name

    proj = HipflatProject(
        uuid=uuid,
        name_th=name_th,
        name_en=name_en,
        slug_url=slug_url,
    )

    # --- Current listing avg sale price/sqm ---
    # "ราคาเฉลี่ย ขาย คือ ฿ 125,000 ต่อตารางเมตร"
    m = re.search(r"ราคาเฉลี่ย ขาย คือ ฿ ([\d,]+)", text)
    if m:
        proj.avg_sale_sqm_thb = _int(m.group(1))

    # --- Historical avg sold price/sqm ---
    # "ราคาเฉลี่ยต่อตารางเมตร: ฿110,000" — inside <strong> tag so use text version
    m = re.search(r"ราคาเฉลี่ยต่อตารางเมตร\s*:\s*฿\s*([\d,]+)", text)
    if m:
        proj.avg_sold_sqm_thb = _int(m.group(1))

    # --- District avg sale price/sqm ---
    # "ราคาเฉลี่ยต่อตารางเมตร สำหรับขาย ใน วัฒนา เท่ากับ ฿ 157,894/ตรม"
    m = re.search(r"ราคาเฉลี่ยต่อตารางเมตร สำหรับขาย ใน .+? เท่ากับ ฿ ([\d,]+)", text)
    if m:
        proj.district_avg_sale_sqm = _int(m.group(1))

    # --- District avg rent price/sqm ---
    # "ราคาเฉลี่ยต่อตารางเมตร ให้เช่า ใน วัฒนา เท่ากับ ฿ 650/ตรม"
    m = re.search(r"ราคาเฉลี่ยต่อตารางเมตร ให้เช่า ใน .+? เท่ากับ ฿ ([\d,]+)", text)
    if m:
        proj.district_avg_rent_sqm = _int(m.group(1))

    # --- Price trend ---
    m = re.search(r"แนวโน้ม(ขาขึ้น|ขาลง)", text)
    if m:
        proj.price_trend = m.group(1)

    # --- YoY change ---
    m = re.search(r"([+-]?\d+\.?\d*)\s*%\s*วิวัฒนาการเมื่อเทียบกับ", text)
    if m:
        proj.yoy_change_pct = float(m.group(1))

    # --- Active listings (units for sale) ---
    # FAQ JSON-LD: "มียูนิตประกาศขาย 74 ยูนิต"
    m = re.search(r"มียูนิตประกาศขาย\s+(\d+)\s+ยูนิต", text)
    if m:
        proj.units_for_sale = _int(m.group(1))
    else:
        # Header summary "ราคาขาย\n74 ยูนิต" — strip tags first
        m = re.search(r"ราคาขาย\s+(\d+)\s+ยูนิต", text)
        if m:
            proj.units_for_sale = _int(m.group(1))

    # --- Active listings (units for rent) ---
    # "มียูนิตให้เช่า 73 ยูนิต" or "ให้เช่า 151 ยูนิต"
    m = re.search(r"มียูนิตให้เช่า\s+(\d+)\s+ยูนิต", text)
    if not m:
        m = re.search(r"ให้เช่า\s+(\d+)\s+ยูนิต", text)
    if m:
        proj.units_for_rent = _int(m.group(1))

    # --- Sale price range ---
    # FAQ JSON-LD: "มียูนิตประกาศขาย 74 ยูนิต มีราคาเริ่มต้นอยู่ที่ ฿ 3,300,000 จนถึง ฿ 63,125,000"
    m = re.search(
        r"ยูนิตประกาศขาย\s+\d+\s+ยูนิต\s+มีราคาเริ่มต้นอยู่ที่\s+฿\s+([\d,]+)\s+จนถึง\s+฿\s+([\d,]+)",
        text,
    )
    if not m:
        m = re.search(
            r"มียูนิตประกาศขาย\s+\d+\s+ยูนิต\s+มีราคาเริ่มต้นอยู่ที่\s+฿\s+([\d,]+)\s+จนถึง\s+฿\s+([\d,]+)",
            text,
        )
    if m:
        proj.sale_price_min = _int(m.group(1))
        proj.sale_price_max = _int(m.group(2))

    # --- Rent price range ---
    # "มียูนิตให้เช่า 73 ยูนิต มีราคาเริ่มต้นอยู่ที่ ฿ 16,000 / เดือน จนถึง ฿ 380,000 / เดือน"
    m = re.search(
        r"ยูนิตให้เช่า\s+\d+\s+ยูนิต\s+มีราคาเริ่มต้นอยู่ที่\s+฿\s+([\d,]+).*?฿\s+([\d,]+)\s*/\s*เดือน",
        text,
    )
    if not m:
        m = re.search(r"฿\s*([\d,]+)\s*/\s*เดือน", text)
        if m:
            proj.rent_price_min = _int(m.group(1))
    else:
        proj.rent_price_min = _int(m.group(1))
        proj.rent_price_max = _int(m.group(2))

    # --- Sold below asking % ---
    m = re.search(r"ต่ำกว่าราคาขายเดิม\s*([\d.]+)%", text)
    if m:
        proj.sold_below_asking_pct = float(m.group(1))

    # --- Days on market ---
    m = re.search(r"(\d+)\s*วันในตลาดก่อนขายได้", text)
    if m:
        proj.avg_days_on_market = _int(m.group(1))

    # --- Year completed ---
    m = re.search(
        r"(ม\.ค\.|ก\.พ\.|มี\.ค\.|เม\.ย\.|พ\.ค\.|มิ\.ย\.|"
        r"ก\.ค\.|ส\.ค\.|ก\.ย\.|ต\.ค\.|พ\.ย\.|ธ\.ค\.)\s*(\d{4})",
        html,  # from raw HTML — the header spec area
    )
    if m:
        proj.year_completed = int(m.group(2))

    # --- Floors ---
    # From description "อาคารสูง 25 ชั้น" is more reliable than header
    m = re.search(r"อาคารสูง\s+(\d+)\s+ชั้น", text)
    if not m:
        m = re.search(r"(\d+)\s+ชั้น", text)
    if m:
        proj.floors = _int(m.group(1))

    # --- Total units ---
    # Description: "รวมทั้งหมด 514 ยูนิต" — most reliable
    m = re.search(r"รวมทั้งหมด\s+(\d+)\s+ยูนิต", text)
    if not m:
        m = re.search(r"(\d+)\s+ยูนิต\s+การเดินทาง", text)
    if m:
        proj.total_units = _int(m.group(1))

    # --- Service charge ---
    m = re.search(r"ค่าส่วนกลาง\s*[:\s]*฿\s*([\d,]+)\s*/sqm", text)
    if not m:
        m = re.search(r"ค่าส่วนกลาง.*?฿\s*([\d,]+)", text)
    if m:
        proj.service_charge_sqm = _int(m.group(1))

    # --- District name ---
    m = re.search(r"ราคาเฉลี่ยต่อตารางเมตร ให้เช่า ใน\s+(\S+)", text)
    if not m:
        m = re.search(r"ให้เช่า ใน\s+([^\s,]+)", text)
    if m:
        proj.district_name = m.group(1)

    return proj


def lookup(project_name: str, verbose: bool = True) -> Optional[HipflatProject]:
    """
    Full lookup: search → UUID → fetch page → return HipflatProject.
    Returns None if project not found.
    """
    if verbose:
        print(f"Searching Hipflat for: {project_name}")

    results = search_project(project_name)
    if not results:
        if verbose:
            print("  No results found.")
        return None

    top = results[0]
    if verbose:
        print(f"  Found: {top['name']} (UUID: {top['id']})")
        if len(results) > 1:
            print(f"  (+ {len(results) - 1} other matches, using top result)")

    time.sleep(0.5)  # polite delay

    proj = fetch_project_data(top["id"])

    if verbose:
        print_project(proj)

    return proj


def print_project(proj: HipflatProject) -> None:
    print()
    print(f"{'=' * 60}")
    print(f"  {proj.name_en}")
    if proj.name_th != proj.name_en:
        print(f"  {proj.name_th}")
    print(f"  {proj.slug_url}")
    print(f"{'=' * 60}")

    if proj.year_completed:
        print(f"  Year completed  : {proj.year_completed}")
    if proj.floors:
        print(f"  Floors          : {proj.floors}")
    if proj.total_units:
        print(f"  Total units     : {proj.total_units}")
    if proj.service_charge_sqm:
        print(f"  Service charge  : ฿{proj.service_charge_sqm}/sqm/month")

    print()
    print("  --- SALE ---")
    if proj.avg_sale_sqm_thb:
        print(f"  Avg listing/sqm : ฿{proj.avg_sale_sqm_thb:,}")
    if proj.avg_sold_sqm_thb:
        print(
            f"  Avg SOLD/sqm    : ฿{proj.avg_sold_sqm_thb:,}  ← use this for NPA valuation"
        )
    if proj.sale_price_min and proj.sale_price_max:
        print(
            f"  Active range    : ฿{proj.sale_price_min:,} – ฿{proj.sale_price_max:,}"
        )
    if proj.units_for_sale is not None:
        print(f"  Active listings : {proj.units_for_sale} units")
    if proj.sold_below_asking_pct:
        print(f"  Sold below ask  : {proj.sold_below_asking_pct}%")
    if proj.avg_days_on_market:
        print(f"  Avg days/market : {proj.avg_days_on_market} days")

    print()
    print("  --- RENTAL ---")
    if proj.rent_price_min:
        rent_max_str = f" – ฿{proj.rent_price_max:,}" if proj.rent_price_max else ""
        print(f"  Rent range      : ฿{proj.rent_price_min:,}{rent_max_str}/month")
    if proj.units_for_rent is not None:
        print(f"  Active rentals  : {proj.units_for_rent} units")

    print()
    print("  --- TRENDS ---")
    if proj.price_trend:
        trend_en = "uptrend" if proj.price_trend == "ขาขึ้น" else "downtrend"
        print(f"  Price trend     : {trend_en} ({proj.price_trend})")
    if proj.yoy_change_pct is not None:
        direction = "↑" if proj.yoy_change_pct >= 0 else "↓"
        print(f"  YoY change      : {direction} {proj.yoy_change_pct:+.1f}%")

    if proj.district_name:
        print()
        print(f"  --- DISTRICT ({proj.district_name}) ---")
        if proj.district_avg_sale_sqm:
            print(f"  District sale   : ฿{proj.district_avg_sale_sqm:,}/sqm")
        if proj.district_avg_rent_sqm:
            print(f"  District rent   : ฿{proj.district_avg_rent_sqm:,}/sqm")
        if proj.avg_sold_sqm_thb and proj.district_avg_sale_sqm:
            pct = (proj.avg_sold_sqm_thb / proj.district_avg_sale_sqm - 1) * 100
            cheaper = "cheaper" if pct < 0 else "more expensive"
            print(f"  vs district     : {abs(pct):.1f}% {cheaper}")

    print()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python hipflat_checker.py <project_name>")
        print()
        print("Examples:")
        print("  python hipflat_checker.py '15 sukhumvit residences'")
        print("  python hipflat_checker.py 'inspire place abac'")
        print("  python hipflat_checker.py 'ลุมพินี สวีท สุขุมวิท 41'")
        sys.exit(1)

    query = " ".join(sys.argv[1:])
    result = lookup(query, verbose=True)

    if result is None:
        sys.exit(1)

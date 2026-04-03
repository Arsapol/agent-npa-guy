#!/usr/bin/env python3
"""Batch ingest area research findings into KB with proper category/area/source metadata."""

import hashlib
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Setup path for direct imports
sys.path.insert(0, str(Path(__file__).resolve().parent))
from lightrag_wrapper import LightRAGManager

CATEGORY_TTL = {
    "pricing": 90,
    "rental": 90,
    "flood": 365,
    "legal": 180,
    "area": 180,
    "project": 365,
    "infrastructure": 365,
    "other": 180,
}

PG_URI = os.environ.get("POSTGRES_URI", "postgresql://arsapolm@localhost:5432/npa_kb")


def make_doc_id(content: str) -> str:
    return f"npa-{hashlib.sha256(content.encode()).hexdigest()[:16]}"


def write_metadata(doc_id, category, area, source, description, ttl_days):
    escaped_desc = description[:500].replace("'", "''")
    escaped_area = (area or "").replace("'", "''") if area else None
    escaped_source = (source or "").replace("'", "''") if source else None
    escaped_cat = category.replace("'", "''")
    escaped_id = doc_id.replace("'", "''")

    area_val = "NULL" if not escaped_area else f"'{escaped_area}'"
    source_val = "NULL" if not escaped_source else f"'{escaped_source}'"

    sql = (
        f"INSERT INTO kb_metadata "
        f"(doc_id, category, area, source, summary, valid_until) "
        f"VALUES ('{escaped_id}', '{escaped_cat}', "
        f"{area_val}, {source_val}, "
        f"'{escaped_desc}', "
        f"NOW() + INTERVAL '{ttl_days} days');"
    )
    result = subprocess.run(
        ["psql", PG_URI, "-c", sql],
        capture_output=True, text=True, timeout=10,
    )
    return result.returncode == 0


def ingest(content, description, category, area, source):
    """Ingest a document with full metadata tracking."""
    ttl_days = CATEGORY_TTL.get(category, 180)
    today = datetime.now().strftime("%Y-%m-%d")

    # Prepend temporal header
    header = (
        f"[Date: {today}] [Category: {category}] "
        f"[Area: {area or 'unspecified'}] [Source: {source or 'unspecified'}] "
        f"[Valid for: {ttl_days} days]\n\n"
    )
    enriched = header + content

    kb = LightRAGManager()
    result = kb.insert_document(enriched, description)

    doc_id = make_doc_id(content)
    meta_ok = write_metadata(doc_id, category, area, source, description, ttl_days)

    print(f"  [{category}] {area} — {description[:60]}...")
    print(f"    → {result[:80]}")
    if meta_ok:
        print(f"    📋 Metadata tracked (expires in {ttl_days}d)")
    else:
        print(f"    ⚠️ Metadata write failed")
    print()
    return result


# === INGESTIONS ===

# ---------- ภาษีเจริญ (Phasi Charoen) - PRICING ----------
ingest(
    "ภาษีเจริญ median condo resale price: ฿2,493,770. Median price per sqm: ฿76,397/sqm. "
    "Supalai Veranda Phasi Charoen Station average resale: ฿78,787/sqm. "
    "ราชพฤกษ์คอนโด near MRT บางไผ่: 29.12 sqm studio, listed under 1M THB. "
    "คอนโดเมโทรพาร์คสาทร 3-4 บางหว้า: 31.63 sqm resale. "
    "zMyHome area median for ภาษีเจริญ: ฿2,230,000. "
    "คอนโด near MRT ภาษีเจริญ (The Parkland Phetkasem 56): 2 bed/2 bath 62 sqm resale. "
    "Near MRT stations condos available from ฿1,290,000. "
    "The President Sathorn-Ratchaphruek 3: 35 sqm at ฿2,890,000 (฿82,700/sqm). "
    "Ratchapruek Condo average resale: ~USD 1,339/sqm, price trend downtrend.",
    "ภาษีเจริญ condo resale prices April 2026",
    category="pricing",
    area="ภาษีเจริญ",
    source="Thailand-Property/Hipflat/zMyHome",
)

ingest(
    "ภาษีเจริญ condo resale price near MRT: 110,000 THB/sqm median for apartments near MRT Phasi Charoen. "
    "Pak Khlong Phasi Charoen sub-area: ฿103,000/sqm for 35 sqm unit at ฿3.60M. "
    "Condos starting from ฿1.39M for ~31 sqm (฿43,973/sqm) at Metro Park Sathorn area. "
    "ลุมพินี คอนโดทาวน์ บางแค (Bang Khae area border): under 1M for 26 sqm. "
    "Market has 512+ condos for sale in Phasi Charoen district (DDProperty).",
    "ภาษีเจริญ detailed condo pricing near transit April 2026",
    category="pricing",
    area="ภาษีเจริญ",
    source="Thailand-Property/DDProperty/Lazudi",
)

# ---------- ภาษีเจริญ - RENTAL ----------
ingest(
    "ภาษีเจริญ condo rental rates: Studio/1BR (24-35 sqm) rent ฿10,000-15,000/month. "
    "1BR 35 sqm at Supalai Loft Sathorn-Ratchaphruek: ฿12,500/month. "
    "1BR at ศุภาลัย เวอร์เลนด้า สถานีภาษีเจริญ: ฿14,000/month (22nd floor, Bldg B). "
    "Median rent for condos in Phasi Charoen: ฿10,835/month (Thailand-Property). "
    "2BR condos average rent: ฿18,176/month, range ฿10,000-48,000 (PropertyScout). "
    "2BR 66 sqm at Supalai Veranda Phasi Charoen Station: ฿28,000/month. "
    "950+ rental listings in Phasi Charoen district (PropertyHub). "
    "660+ listings near MRT Phasi Charoen station (PropertyHub). "
    "Condos near MRT ภาษีเจริญ under ฿6,000/month available (Baania).",
    "ภาษีเจริญ condo rental rates April 2026",
    category="rental",
    area="ภาษีเจริญ",
    source="PropertyScout/Thailand-Property/DotProperty/Livinginsider",
)

# ---------- ภาษีเจริญ - PROJECT ----------
ingest(
    "Major condo projects in ภาษีเจริญ district: "
    "1. Supalai Veranda Phasi Charoen Station (ศุภาลัย เวอร์เลนด้า) — completed Mar 2023, near MRT Phasi Charoen "
    "2. Supalai Loft Phasi Charoen Station — near MRT Phasi Charoen "
    "3. Supalai Loft Sathorn-Ratchaphruek — on Petchakasem Road, Pak Khlong Phasi Charoen "
    "4. Metro Park Sathorn (เมโทร ปาร์ค สาทร) — 3 phases, Kanlapaphruek Road, near BTS Wutthakat "
    "5. The Parkland Phetkasem 56 — completed Dec 2016, near MRT Phasi Charoen "
    "6. The President Sathorn-Ratchaphruek 1/3 — on Petchakasem Road "
    "7. Ratchapruek Condo — near Ratchaphruek area "
    "8. The Livin Phetkasem — on Petchakasem Road, Bang Wa "
    "9. LOVE เจริญนคร — new Sansiri project, Charoen Nakhon road, river view, pet-friendly "
    "10. ราชพฤกษ์คอนโด — near MRT Bang Phai "
    "11. Bangkok Horizon Phetkasem — near MRT Phasi Charoen, 30.71 sqm units available.",
    "ภาษีเจริญ major condo projects list April 2026",
    category="project",
    area="ภาษีเจริญ",
    source="Hipflat/DDProperty/CondoNayoo/Livinginsider",
)

# ---------- ภาษีเจริญ - AREA (TRANSIT) ----------
ingest(
    "ภาษีเจริญ transit: MRT Blue Line extension serves the area with key stations: "
    "MRT ภาษีเจริญ (BL35) — main station at Soi Phetkasem 33/8, near Red Cross station 11 "
    "MRT บางแค (BL37) — at Bang Khae intersection, near Seacon Bang Khae, Lotus Bang Khae "
    "MRT หลักสอง (BL38) — at Phetkasem/Kanchanaphisek intersection, near M Life Store Bang Khae "
    "BTS บางหว้า (S12) — Silom Line terminus, interchange with MRT บางหว้า "
    "MRT บางหว้า — interchange point with BTS Bang Wa "
    "MRT บางไผ่ — serves western end of district "
    "The MRT extension from Ta Phra to Lak Song runs elevated (not underground). "
    "BTS Bang Wa to Seacon Bang Khae: 2 MRT stations. "
    "950+ rental listings, 660+ near MRT Phasi Charoen, 370+ near MRT Bang Khae.",
    "ภาษีเจริญ transit stations and connectivity April 2026",
    category="area",
    area="ภาษีเจริญ",
    source="Wikipedia/Moovit/DDProperty/nhaidee",
)

# ---------- ภาษีเจริญ - FLOOD ----------
ingest(
    "ภาษีเจริญ flood risk: MEDIUM-HIGH. Historical flood data: "
    "2011 major flood: Water up to 1m in parts of Phasi Charoen. Siam University area water 30cm on Phetkasem Road. "
    "Phasi Charoen had 6,839 affected households during 2011 floods (source: mplushome). "
    "Phetkasem Road from Ta Phra to The Mall Bang Khae is characteristically low-lying, difficult to elevate. "
    "Regular flooding on Phetkasem Road near Bang Wa intersection during heavy rain (>100mm/hour). "
    "Drainage capacity: existing pipes cannot handle rainfall exceeding 100mm/hour. "
    "Bang Khae-Phasi Charoen border areas see flooding nearly 1m during severe storms. "
    "Bangkok Drainage Department actively pumps water from Phetkasem area during heavy rain. "
    "However, newer condos built on elevated foundations fare better than ground-level properties.",
    "ภาษีเจริญ flood risk assessment April 2026",
    category="flood",
    area="ภาษีเจริญ",
    source="ThaiRath/DDProperty/Matichon/mplushome",
)

# ---------- บางแค (Bang Khae) - PRICING ----------
ingest(
    "บางแค (Bang Khae) condo resale prices: "
    "The Origin Bangkae: 24.30 sqm, ฿1,226,804 (฿50,500/sqm). "
    "The Niche ID Bangkhae: 28 sqm, ฿1,850,000 (฿66,000/sqm). "
    "The Parkland Phetkasem 56: 62 sqm 2BR, ฿6,510,000 (฿104,000/sqm). "
    "Lumpini Condo Town Bang Khae: 26 sqm, under ฿1,000,000. "
    "Bangkae City Condo 1-2: near MRT Lak Song, resale from ฿1,950,000. "
    "Niran City Sathorn-Kanchanaphisek (บางแค): resale units available. "
    "Bang Khae median sales price: ~$59,759 (≈ ฿2,100,000), median price/sqm: ~$2,097 (≈ ฿73,400). "
    "DDProperty: 167 condos for sale in Bang Khae. "
    "Bangkok Feliz @Bangkhae Station: completed Dec 2016. "
    "FUSE Sense Bangkae: newer project in area. "
    "Budget segment: ลุมพินี คอนโดทาวน์ บางแค under ฿1M for ~26 sqm.",
    "บางแค condo resale prices April 2026",
    category="pricing",
    area="บางแค",
    source="Hipflat/Thailand-Property/FazWaz/DDProperty/Livinginsider",
)

# ---------- บางแค - RENTAL ----------
ingest(
    "บางแค (Bang Khae) condo rental rates: "
    "Bangkae City Condo 1-2: studio 23.80 sqm, ฿5,500/month. "
    "Bangkok Feliz @Bangkhae Station: 2BR 50.25 sqm, ฿16,000/month. "
    "Lumpini Park Phetkasem 98: 23 sqm, budget rental available. "
    "Tulip Square @ Omnoi: 1BR 28 sqm, ฿6,000/month. "
    "The Holmes Sathorn-Bangkhae: rental units available. "
    "FUSE Sense Bangkae: 2BR 46 sqm, rental available. "
    "General range for 1BR (24-32 sqm): ฿5,000-8,000/month. "
    "2BR units: ฿12,000-18,000/month. "
    "Bangkhae Condo Town average rent: ~USD 5/sqm. "
    "250+ rental listings in Bang Khae (PropertyHub). "
    "370+ listings near MRT Bang Khae (PropertyHub). "
    "DDProperty: 30-35 rental listings in Bang Khae. "
    "Baania: condos for rent under ฿6,000/month available in Bang Khae area.",
    "บางแค condo rental rates April 2026",
    category="rental",
    area="บางแค",
    source="RentCondoBkk/Thailand-Property/Hipflat/PropertyHub/Baania/Livinginsider",
)

# ---------- บางแค - PROJECT ----------
ingest(
    "Major condo projects in บางแค (Bang Khae) district: "
    "1. Bangkae City Condo 1-2 (บางแค ซิตี้ คอนโด) — near MRT Lak Song, 1 min walk, older project "
    "2. The Origin Bangkae — newer development, 24.30 sqm studios "
    "3. The Niche ID Bangkhae — completed Mar 2016, 28 sqm 1BR units "
    "4. Bangkok Feliz @Bangkhae Station — completed Dec 2016, near MRT "
    "5. Lumpini Condo Town Bangkhae (ลุมพินี คอนโดทาวน์ บางแค) — L.P.N. Development, budget condos "
    "6. Lumpini Park Phetkasem 98 (ลุมพินี พาร์ค เพชรเกษม 98) — budget, 23 sqm studios "
    "7. The Parkland Phetkasem Condominium — completed Dec 2016, larger units "
    "8. FUSE Sense Bangkae — modern project near MRT "
    "9. Niran City Sathorn-Kanchanaphisek (นิรันดร์ ซิตี้ สาทร-กาญจนาภิเษก) — on Kanchanaphisek "
    "10. The Muve Bangwa — near BTS/MRT interchange Bang Wa, 9-story building "
    "11. SENA Kith MRT Bang Khae (เสนา คิทท์ MRT บางแค) — near MRT Bang Khae "
    "12. iCondo Phetkasem 39 — near MRT Phasi Charoen/Seacon Bang Khae "
    "Sansiri has 4 condo projects in Bang Khae area. "
    "The Muve Bang Khae — active lifestyle concept condo. "
    "SENA development near MRT Bang Khae station.",
    "บางแค major condo projects list April 2026",
    category="project",
    area="บางแค",
    source="CondoNayoo/Livinginsider/Hipflat/DDProperty/Home.co.th",
)

# ---------- บางแค - AREA (TRANSIT) ----------
ingest(
    "บางแค (Bang Khae) transit: "
    "MRT บางแค (BL37) — Blue Line extension, at Phetkasem Rd, near Seacon Bang Khae mall, Lotus Bang Khae. "
    "Station exits: 1) Soi Phetkasem 62/4, 2) Rajawinit Elementary Bang Khae school, 3) Lotus Bang Khae, 4) Bang Khae intersection, Wat Nimmanoradee. "
    "MRT หลักสอง (BL38) — at Phetkasem/Kanchanaphisek intersection, near M Life Store, Lak Song Plaza. "
    "MRT พุทธมณฑล สาย 2 — further west on Blue Line extension. "
    "BTS บางหว้า (S12) — nearest BTS, 2 stations from Seacon Bang Khae via MRT. "
    "MRT Bang Khae is on elevated section (not underground like inner-city stations). "
    "The Mall Bang Khae / Seacon Bang Khae accessible from MRT Bang Khae station. "
    "Bus connections to Phutthamonthon, Salaya, Nakhon Pathom from Bang Khae.",
    "บางแค transit stations and connectivity April 2026",
    category="area",
    area="บางแค",
    source="Wikipedia/Moovit/Pantip/MRT-official",
)

# ---------- บางแค - FLOOD ----------
ingest(
    "บางแค (Bang Khae) flood risk: HIGH for Phetkasem Road corridor. "
    "Phetkasem Road from Ta Phra to The Mall Bang Khae is low-lying, floods regularly. "
    "Heavy rain 91.5mm (May 2024): severe flooding on Phetkasem, Bang Khae, Nong Khaem. "
    "Heavy rain 159mm: water above footpath level on Phetkasem near Bang Khae-Ta Phra, "
    "cars stalled, people wading knee-deep to reach MRT station. "
    "Phetkasem Road near Seacon Bang Khae floods during heavy rain, all lanes affected. "
    "Bang Khae Soi 4 area: generally OK if going toward Bang Bon, but floods toward Therdthai road. "
    "Bangkok Drainage Dept: Phetkasem Road's physical characteristic is naturally low, "
    "elevation difficult because surrounding shophouses would be below road level. "
    "Flood heights: typically 20-50cm on road, up to 1m in severe events. "
    "Bang Khae had 78,764 affected households during 2011 floods. "
    "Condos on higher floors generally safe, ground-level and road-level shops at risk.",
    "บางแค flood risk assessment April 2026",
    category="flood",
    area="บางแค",
    source="ThaiPBS/JS100/FM91/Matichon/Pantip",
)

# ---------- หนองแขม (Nong Khaem) - PRICING ----------
ingest(
    "หนองแขม (Nong Khaem) condo resale prices — cheapest Bangkok district for condos: "
    "Market & Condotel Nongkham Shopping Center (ตลาดและคอนโดเทล ศูนย์การค้าหนองแขม): "
    "average sale price ~USD 953/sqm (≈ ฿33,000/sqm). 16 units for sale. Price trend: uptrend. "
    "Nong Khaem Condotel: 25.26 sqm unit at ฿372,000 (฿14,727/sqm). "
    "รุ่งโรจน์คอนโดเทล เพชรเกษม 81/1: 44.15 sqm, large unit for area. "
    "หนองค้างพลู sub-area: $574/sqm (≈ ฿20,000/sqm) — extremely cheap. "
    "DDProperty: 55.26 sqm at ฿1,390,000 (฿25,154/sqm), built 1993. "
    "FazWaz: only 5 condo listings in Nong Khaem — very thin market. "
    "Patchara Place: rent ~USD 4/sqm. "
    "Golden Town Phetkasem-Phutthamonthon 3: ~USD 952/sqm. "
    "Overall Nong Khaem is the cheapest condo market in Bangkok, "
    "with prices 50-70% below Phasi Charoen. Very limited condo supply — mostly old condotels.",
    "หนองแขม condo resale prices April 2026 — cheapest Bangkok district",
    category="pricing",
    area="หนองแขม",
    source="Hipflat/DDProperty/FazWaz/ZMyHome",
)

# ---------- หนองแขม - RENTAL ----------
ingest(
    "หนองแขม (Nong Khaem) condo rental rates — very limited market: "
    "zMyHome: median rent in Nong Khaem area ฿5,500/month. "
    "PropertyHub: only 4+ rental listings in Nong Khaem — very thin market. "
    "ThaiHometown: 19 rental listings total in Nong Khaem. "
    "Patchara Place: rent ~USD 4/sqm (≈ ฿140/sqm), so a 24 sqm unit ≈ ฿3,360/month. "
    "Nong Khaem Condotel: 1 listing for rent. "
    "Market & Condotel Nongkham: 1 unit for rent. "
    "Typical studio/1BR rental: ฿3,000-6,000/month for 24-30 sqm. "
    "Rental market is very thin — mostly locals, few expats. "
    "Rental demand limited by lack of transit (no BTS/MRT in district). "
    "Most renters are workers at nearby industrial/commercial areas.",
    "หนองแขม condo rental rates April 2026 — thin market",
    category="rental",
    area="หนองแขม",
    source="zMyHome/PropertyHub/ThaiHometown/Hipflat",
)

# ---------- หนองแขม - AREA ----------
ingest(
    "หนองแขม (Nong Khaem) area profile: "
    "No BTS or MRT station within the district — nearest is MRT Bang Khae (BL37) to the north. "
    "Key roads: Phetkasem Road (western Bangkok), Phutthamonthon Sai 4 & 5, Kanchanaphisek. "
    "Mainly residential with housing estates (122+ housing projects per BaanFinder). "
    "Predominantly low-rise: houses, townhouses, condotels — very few modern condo high-rises. "
    "Nearby amenities: The Mall Bang Khae, Seacon Bang Khae (in neighboring Bang Khae district). "
    "Hospitals: Vibhavadi Hospital (Nong Khaem area). "
    "Schools: Sarasas Witaed Bang Bon, Asia Southeastern University nearby. "
    "Nong Khaem is on Bangkok's western fringe, bordering Samut Sakhon. "
    "Area has many housing estates built on former agricultural land. "
    "Primarily Thai residents, limited expat community. "
    "BKK governor visited Nong Khaem to address 6 main problems including flooding and PM2.5.",
    "หนองแขม area profile and amenities April 2026",
    category="area",
    area="หนองแขม",
    source="BaanFinder/DDProperty/Baania/Bangkok.go.th",
)

# ---------- หนองแขม - FLOOD ----------
ingest(
    "หนองแขม (Nong Khaem) flood risk: HIGH. "
    "Bangkok governor identified flooding as the #1 problem in Nong Khaem district. "
    "Root cause: many housing estates expanded into old agricultural land (private land), "
    "where BMA cannot dredge drainage canals. "
    "Canal water management connecting to housing estates is poor. "
    "2011 major flood: Nong Khaem was among the worst-hit districts, water nearly 1 meter. "
    "Nong Khaem-Bang Khae combined: flooding up to 1m during severe storms, "
    "water flowing from Phutthamonthon Sai 4 and Khlong Wiwatthana. "
    "Phetkasem Road in Nong Khaem area: floods during heavy rain, "
    "especially at Om Noi, Nong Khaem sections. "
    "828,915 households affected across 12 fully-flooded Bangkok districts in 2011. "
    "Flood risk is structural — cannot be fully mitigated due to low-lying geography "
    "and insufficient drainage infrastructure. "
    "Any property purchase in Nong Khaem must verify specific flood history of the building/soi.",
    "หนองแขม flood risk assessment April 2026 — HIGH risk",
    category="flood",
    area="หนองแขม",
    source="ThaiRath/mplushome/MgrOnline/PostToday/ThaiPBS",
)

# ---------- หนองแขม - PROJECT ----------
ingest(
    "หนองแขม (Nong Khaem) condo projects — very limited condo supply: "
    "1. Market & Condotel Nongkham Shopping Center (ตลาดและคอนโดเทล ศูนย์การค้าหนองแขม) — "
    "   mixed-use condotel with shopping center, 16 units for sale, uptrend pricing "
    "2. Nong Khaem Condotel (คอนโดเทลหนองแขม) — older condotel project, limited rental market "
    "3. รุ่งโรจน์คอนโดเทล เพชรเกษม 81/1 — older condotel on Phetkasem 81/1, large 44 sqm units "
    "4. Patchara Place — small project in Nong Khaem, limited activity "
    "Most 'condos' in Nong Khaem are actually condotels (condominium-hotels) from 1990s era. "
    "Very few modern condo high-rise developments in the district. "
    "Newer housing in area is mostly townhouses and detached houses (122+ projects). "
    "Key developers active in area: Pruksa (townhouses), Sansiri (limited), Sena. "
    "Condo investment in Nong Khaem carries high risk due to thin resale/rental market.",
    "หนองแขม condo projects list April 2026 — limited supply",
    category="project",
    area="หนองแขม",
    source="Hipflat/DDProperty/FazWaz/BaanFinder",
)

print("=" * 60)
print("ALL INGESTIONS COMPLETE")
print("=" * 60)

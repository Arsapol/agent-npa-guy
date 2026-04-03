#!/usr/bin/env python3
"""Batch ingest all MEMORY.md findings into KB with full metadata tracking.

Uses the same pattern as KBToolkit: LightRAG insertion + kb_metadata tracking.
"""

import hashlib
import os
import subprocess
import sys
import asyncio
from datetime import datetime
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent))

from lightrag_wrapper import LightRAGManager, POSTGRES_DEFAULT_URI

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


def make_doc_id(content: str) -> str:
    return f"npa-{hashlib.sha256(content.encode()).hexdigest()[:16]}"


def run_psql(pg_uri: str, sql: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["psql", pg_uri, "-c", sql],
        capture_output=True, text=True, timeout=10,
    )


def ingest_with_metadata(
    kb: LightRAGManager,
    pg_uri: str,
    content: str,
    description: str,
    category: str,
    area: str,
    source: str,
    idx: int,
    total: int,
):
    """Ingest a single finding with full metadata."""
    print(f"\n{'='*60}")
    print(f"[{idx}/{total}] {description}")
    print(f"  Category: {category} | Area: {area} | Source: {source}")
    
    # Validate category
    if category not in CATEGORY_TTL:
        category = "other"
    
    ttl_days = CATEGORY_TTL[category]
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Prepend temporal header
    temporal_header = (
        f"[Date: {today}] [Category: {category}] "
        f"[Area: {area or 'unspecified'}] [Source: {source or 'unspecified'}] "
        f"[Valid for: {ttl_days} days]\n\n"
    )
    enriched_content = temporal_header + content
    
    # Ingest to LightRAG
    try:
        result = kb.insert_document(enriched_content, description)
        print(f"  LightRAG: {result[:100]}")
    except Exception as e:
        print(f"  LightRAG ERROR: {e}")
        return False
    
    # Write metadata to kb_metadata
    doc_id = make_doc_id(content)
    escaped_desc = description[:500].replace("'", "''")
    escaped_area = area.replace("'", "''") if area else ""
    escaped_source = source.replace("'", "''") if source else ""
    
    sql = (
        f"INSERT INTO kb_metadata "
        f"(doc_id, category, area, source, summary, valid_until) "
        f"VALUES ('{doc_id}', '{category}', "
        f"'{escaped_area}', '{escaped_source}', '{escaped_desc}', "
        f"NOW() + INTERVAL '{ttl_days} days');"
    )
    
    result = run_psql(pg_uri, sql)
    if result.returncode != 0:
        print(f"  Metadata ERROR: {result.stderr[:200]}")
    else:
        print(f"  Metadata: OK (expires in {ttl_days} days)")
    
    return True


def main():
    # Source env
    env_path = Path(__file__).resolve().parents[3] / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, value = line.partition("=")
                    os.environ.setdefault(key.strip(), value.strip())
    
    kb = LightRAGManager()
    pg_uri = os.environ.get("POSTGRES_URI", POSTGRES_DEFAULT_URI)
    
    # Define all findings from MEMORY.md
    findings = [
        # === PRICING (category: pricing, TTL: 90 days) ===
        {
            "content": "Life Ratchadapisek ดินแดง area: average condo sale price 101,811 THB/sqm as of 2026. Source: Lazudi listings April 2026.",
            "description": "Life Ratchadapisek sale price benchmark ดินแดง",
            "category": "pricing",
            "area": "ดินแดง",
            "source": "Lazudi",
        },
        {
            "content": "Ideo Mobi Rama 9 ดินแดง area: condo sale price 119,354 THB/sqm. Source: Hipflat sold listing June 2025.",
            "description": "Ideo Mobi Rama 9 sale price benchmark ดินแดง",
            "category": "pricing",
            "area": "ดินแดง",
            "source": "Hipflat",
        },
        {
            "content": "The River คลองสาน คลองต้นไทร: condo sale price 187,000-227,000 THB/sqm. Premium riverfront project by Raimon Land. NPA units at 91,000-131,000 THB/sqm = 35-60% below market. Source: Hipflat 2025-2026 sales.",
            "description": "The River condo sale price benchmark คลองสาน",
            "category": "pricing",
            "area": "คลองสาน",
            "source": "Hipflat",
        },
        {
            "content": "Motif Condo บางยี่เรือ ธนบุรี: average sale price 68,880 THB/sqm. NPA units at 73,800 THB/sqm = ABOVE market, NOT a deal.",
            "description": "Motif Condo sale price benchmark บางยี่เรือ",
            "category": "pricing",
            "area": "บางยี่เรือ",
            "source": "web_search",
        },
        {
            "content": "Lumpini Place Ratchada-Thapra บุคคโล ธนบุรี: resale sale price ~62,800 THB/sqm (35sqm 1BR listing at 2.2M). NPA at 50,700 THB/sqm = -19% below market. Two adjacent units available (asset 1993960, 1993961). Source: Livinginsider.",
            "description": "Lumpini Place Ratchada-Thapra sale price บุคคโล",
            "category": "pricing",
            "area": "บุคคโล",
            "source": "Livinginsider",
        },
        {
            "content": "พญาไท สามเสนใน: condo sale price ~61,000 THB/sqm (Phaholyothin Place area). NPA 1999047 at 74,317 THB/sqm = ABOVE market by +22%.",
            "description": "Phaholyothin Place sale price benchmark พญาไท",
            "category": "pricing",
            "area": "พญาไท",
            "source": "web_search",
        },
        {
            "content": "ISSI Condo สุขสวัสดิ์ บางปะกอก ราษฎร์บูรณะ: average sale price 66,666 THB/sqm. NPA units at 66,800-78,500 THB/sqm = AT or ABOVE market.",
            "description": "ISSI Condo sale price benchmark ราษฎร์บูรณะ",
            "category": "pricing",
            "area": "ราษฎร์บูรณะ",
            "source": "web_search",
        },
        {
            "content": "สุขุมวิท 77 อ่อนนุช: BTS On Nut doorstep. Market condo prices 50,000-103,000 THB/sqm. Strong rental demand area.",
            "description": "Sukhumvit 77 On Nut sale price benchmark",
            "category": "pricing",
            "area": "อ่อนนุช",
            "source": "web_search",
        },
        {
            "content": "Hat Yai คอหงส์ area land: market price ~825 THB/sqm. Source: FazWaz.",
            "description": "Hat Yai คอหงส์ land price benchmark",
            "category": "pricing",
            "area": "คอหงส์",
            "source": "FazWaz",
        },
        {
            "content": "DCondo Hatyai คอหงส์: resale condo price ~30,000 THB/sqm. Student-oriented project near PSU.",
            "description": "DCondo Hatyai resale price คอหงส์",
            "category": "pricing",
            "area": "คอหงส์",
            "source": "web_search",
        },
        {
            "content": "BENU Residence คอหงส์ หาดใหญ่: resale condo price ~65,000 THB/sqm. Higher-end project near PSU.",
            "description": "BENU Residence resale price คอหงส์",
            "category": "pricing",
            "area": "คอหงส์",
            "source": "web_search",
        },
        {
            "content": "Songkhla เมืองสงขลา พะวง area: house market price 45,000-70,000 THB/wa (teedin108 housing projects).",
            "description": "พะวง house price per wa เมืองสงขลา",
            "category": "pricing",
            "area": "เมืองสงขลา",
            "source": "teedin108",
        },
        
        # === RENTAL (category: rental, TTL: 90 days) ===
        {
            "content": "Motif Condo บางยี่เรือ ธนบุรี: rental rates 12,000-25,000 THB/month depending on unit size.",
            "description": "Motif Condo rental rates บางยี่เรือ",
            "category": "rental",
            "area": "บางยี่เรือ",
            "source": "web_search",
        },
        {
            "content": "Lumpini Place Ratchada-Thapra บุคคโล: estimated rental 12,000 THB/month for 35.84 sqm unit. Gross yield 7.31%, net yield 6.22%.",
            "description": "Lumpini Place rental rate บุคคโล",
            "category": "rental",
            "area": "บุคคโล",
            "source": "calc_analysis",
        },
        {
            "content": "ดินแดง near MRT Phra Ram 9: estimated rental 18,000 THB/month for 43.68 sqm unit. Gross yield 10.57%, net yield 8.99%. Best yield among NPA condos analyzed.",
            "description": "ดินแดง rental rate near MRT Phra Ram 9",
            "category": "rental",
            "area": "ดินแดง",
            "source": "calc_analysis",
        },
        {
            "content": "บางเขน กูบแดง area: rental rates 5,000-8,000 THB/month. Limited appreciation potential. No BTS/MRT within 2km. Flood HIGH risk.",
            "description": "บางเขน กูบแดง rental rates",
            "category": "rental",
            "area": "บางเขน",
            "source": "web_search",
        },
        {
            "content": "Hat Yai คอหงส์ near PSU: student apartment rentals 3,500-9,000 THB/month. 206+ apartments listed on RentHub near PSU campus. Strong student rental market.",
            "description": "PSU area student rental rates คอหงส์",
            "category": "rental",
            "area": "คอหงส์",
            "source": "RentHub",
        },
        {
            "content": "DCondo Hatyai คอหงส์: rental ~6,000-7,000 THB/month. Student-oriented condo near PSU.",
            "description": "DCondo Hatyai rental rate คอหงส์",
            "category": "rental",
            "area": "คอหงส์",
            "source": "web_search",
        },
        {
            "content": "BENU Residence คอหงส์: rental ~15,000 THB/month. Higher-end condo near PSU.",
            "description": "BENU Residence rental rate คอหงส์",
            "category": "rental",
            "area": "คอหงส์",
            "source": "web_search",
        },
        {
            "content": "เมืองสงขลา near มอ.ทักษิณ (Thaksin University): student apartment rentals 3,500-8,000 THB/month. Source: RentHub.",
            "description": "Thaksin University student rental rates เมืองสงขลา",
            "category": "rental",
            "area": "เมืองสงขลา",
            "source": "RentHub",
        },
        {
            "content": "Songkhla NPA คอหงส์ near PSU top pick 1896940: 34.9 wa house, purchase 1.12M, acquisition 1.36M, estimated rent 8,000/mo, gross yield 7.08%, net yield 6.02%, break-even 16.6 years. BEST PICK for student rental.",
            "description": "Songkhla PSU NPA 1896940 yield analysis",
            "category": "rental",
            "area": "คอหงส์",
            "source": "calc_analysis",
        },
        {
            "content": "Songkhla NPA เมืองสงขลา พะวง 1872721: 56.5 wa house, purchase 528K, gross yield 10.38%, net yield 8.82%, break-even 11.3 years. STRONG BUY but all 6 rounds งดขาย (suspended) — GSB policy. Must investigate why.",
            "description": "Songkhla Town NPA 1872721 yield analysis",
            "category": "rental",
            "area": "เมืองสงขลา",
            "source": "calc_analysis",
        },
        {
            "content": "Songkhla NPA เมืองสงขลา ทุ่งหวัง 1873488: 99.0 wa house, purchase 868K, gross yield 8.79%, net yield 7.47%, break-even 13.4 years. BUY but all 6 rounds งดขาย (suspended) — GSB policy.",
            "description": "Songkhla Town NPA 1873488 yield analysis",
            "category": "rental",
            "area": "เมืองสงขลา",
            "source": "calc_analysis",
        },
        {
            "content": "พญาไท BTS Sanam Pao area: estimated rental 15,000 THB/month for 32.80 sqm unit. Gross yield 6.9%, net yield 5.87%. But NPA price 74,317/sqm is ABOVE market ~61K/sqm.",
            "description": "พญาไท rental rate BTS Sanam Pao",
            "category": "rental",
            "area": "พญาไท",
            "source": "calc_analysis",
        },
        
        # === AREA INTELLIGENCE (category: area, TTL: 180 days) ===
        {
            "content": "บางเขน กูบแดง: Flood risk HIGH. No BTS/MRT within 2km. Rentals 5,000-8,000 THB/month. Limited appreciation potential. Avoid for NPA investment.",
            "description": "Area intelligence บางเขน กูบแดง",
            "category": "area",
            "area": "บางเขน",
            "source": "location_intel",
        },
        {
            "content": "สุขุมวิท 77 อ่อนนุช: BTS On Nut at doorstep. Market prices 50,000-103,000 THB/sqm. Strong rental demand. Good transit access.",
            "description": "Area intelligence สุขุมวิท 77 อ่อนนุช",
            "category": "area",
            "area": "อ่อนนุช",
            "source": "location_intel",
        },
        {
            "content": "คลองสาน คลองต้นไทร: The River by Raimon Land, premium riverfront. BTS Krung Thon Buri 784m. Market 187,000-227,000 THB/sqm. NPA units 91,000-131,000 THB/sqm = 35-60% below market. Best NPA discount in Bangkok.",
            "description": "Area intelligence คลองสาน The River",
            "category": "area",
            "area": "คลองสาน",
            "source": "web_search",
        },
        {
            "content": "บางยี่เรือ ธนบุรี: Motif Condo area. Market avg 68,880 THB/sqm. NPA at 73,800 THB/sqm = ABOVE market, NOT a deal. Rental 12,000-25,000 THB/month.",
            "description": "Area intelligence บางยี่เรือ ธนบุรี",
            "category": "area",
            "area": "บางยี่เรือ",
            "source": "web_search",
        },
        {
            "content": "บุคคโล ธนบุรี: Lumpini Place Ratchada-Thapra. Market resale ~62,800 THB/sqm. NPA at 50,700 THB/sqm = -19% below market. Two adjacent units (1993960, 1993961) available, BUY recommendation. Yield 7.31%/6.22%. R1 auction Apr 28.",
            "description": "Area intelligence บุคคโล ธนบุรี",
            "category": "area",
            "area": "บุคคโล",
            "source": "analysis",
        },
        {
            "content": "ดินแดง: MRT Phra Ram 9 station 218m away. NPA asset 1867367: 43.68 sqm at 42,139 THB/sqm. Market comparables: Life Ratchadapisek 101,811/sqm, Ideo Mobi 119,354/sqm. NPA is -55 to -65% below market. SPECULATIVE — 5 rounds zero bidders, may have hidden issues. R6 auction Apr 3.",
            "description": "Area intelligence ดินแดง MRT Phra Ram 9",
            "category": "area",
            "area": "ดินแดง",
            "source": "analysis",
        },
        {
            "content": "บางปะกอก ราษฎร์บูรณะ: ISSI Condo. Market 66,666 THB/sqm. NPA at 66,800-78,500 THB/sqm = AT or ABOVE market. NOT a deal.",
            "description": "Area intelligence บางปะกอก ราษฎร์บูรณะ",
            "category": "area",
            "area": "ราษฎร์บูรณะ",
            "source": "analysis",
        },
        {
            "content": "พญาไท สามเสนใน: BTS Sanam Pao 797m. NPA asset 1999047 at 74,317 THB/sqm. Market ~61,000 THB/sqm. ABOVE market by +22%. OVERPRICED.",
            "description": "Area intelligence พญาไท BTS Sanam Pao",
            "category": "area",
            "area": "พญาไท",
            "source": "analysis",
        },
        {
            "content": "คอหงส์ หาดใหญ่ (PSU area): Flood risk MEDIUM (confirmed floods Nov 2567 & Nov 2568 in ทุ่งลุง-คอหงส์ area). NO BTS/MRT transit. Songklanagarind Hospital 237m from campus. Lotus's 566m. PSU faculties within 200m. Student rental market strong: 3,500-9,000 THB/month (206+ apartments on RentHub near PSU). PSU campus coordinates: ~7.0067, 100.4967.",
            "description": "Area intelligence คอหงส์ PSU Hat Yai",
            "category": "area",
            "area": "คอหงส์",
            "source": "location_intel",
        },
        {
            "content": "Bangkok NPA condo overview April 2026: 94 unsold ห้องชุด in Bangkok. Key clusters: คลองสาน (4 units, 4.8-16.8M, premium near BTS), ภาษีเจริญ (19 units, 929K-3.99M, largest cluster), ราษฎร์บูรณะ (10 units), บางเขน (10 units, flood zone), บางแค (10 units), ธนบุรี (8 units, near BTS), หนองแขม (5 units, cheapest suburban), ดอนเมือง (4 units, far north cheap), ดินแดง (1 unit, near MRT Phra Ram 9).",
            "description": "Bangkok NPA condo overview April 2026",
            "category": "area",
            "area": "กรุงเทพมหานคร",
            "source": "led_query",
        },
        {
            "content": "Bangkok district tier classification for NPA condos: TIER 1 (near BTS/MRT, strong location) = คลองสาน, ธนบุรี, พญาไท, ดินแดง, บางกอกน้อย. TIER 2 (some transit, decent area) = ภาษีเจริญ, ราษฎร์บูรณะ, บางพลัด, จอมทอง, บางขุนเทียน. TIER 3 (poor transit, suburban/edge, flood-prone) = หนองแขม, ดอนเมือง, บางแค, ตลิ่งชัน, บางเขน, บางกอกใหญ่. 37 properties in TIER 3 eliminated.",
            "description": "Bangkok district tier classification NPA condos",
            "category": "area",
            "area": "กรุงเทพมหานคร",
            "source": "analysis",
        },
        {
            "content": "Songkhla NPA overview April 2026: 508 total properties in Songkhla province. ZERO condos (ห้องชุด) — all are ที่ดินพร้อมสิ่งปลูกสร้าง (houses/land). Key universities: PSU (มอ.สงขลานครินทร์) main campus in คอหงส์/หาดใหญ่, Thaksin Univ & Rajabhat Songkhla in เมืองสงขลา. คอหงส์ area (near PSU): 13 properties, all houses, 1.23M-2.98M, 13-50.6 wa. เมืองสงขลา area (near Thaksin/Rajabhat): 20 properties in ทุ่งหวัง, บ่อยาง, พะวง, 0.53M-2.21M.",
            "description": "Songkhla NPA overview April 2026",
            "category": "area",
            "area": "สงขลา",
            "source": "led_query",
        },
        {
            "content": "Songkhla Town เมืองสงขลา near universities: มอ.ทักษิณ (Thaksin University) at 7.163, 100.609 and มรภ.สงขลา (Rajabhat Songkhla) at 7.171, 100.614 — 816m apart. Student rental market 3,500-8,000 THB/month near ม.ทักษิณ (RentHub). LED branch contact: แขวงสงขลา (074) 311292, 314904.",
            "description": "Songkhla Town university area intelligence",
            "category": "area",
            "area": "เมืองสงขลา",
            "source": "location_intel",
        },
        
        # === FLOOD (category: flood, TTL: 365 days) ===
        {
            "content": "Hat Yai คอหงส์ ทุ่งลุง flood risk: MEDIUM. Confirmed flooding in Nov 2567 (2024) and Nov 2568 (2025) in ทุ่งลุง-คอหงส์ area. Roads blocked, boats needed. Must inspect properties after rain. Songkhla all 16 districts affected Nov 2568 (690K people).",
            "description": "Hat Yai คอหงส์ flood risk MEDIUM",
            "category": "flood",
            "area": "คอหงส์",
            "source": "news",
        },
        {
            "content": "Songkhla เมืองสงขลา flood: ทล.4309 ทุ่งหวัง-สงขลา flooded 10-15cm Nov 2567. All 16 Songkhla districts affected Nov 2568 (690K people). MEDIUM risk.",
            "description": "Songkhla Town เมืองสงขลา flood risk",
            "category": "flood",
            "area": "เมืองสงขลา",
            "source": "news",
        },
        
        # === LEGAL (category: legal, TTL: 180 days) ===
        {
            "content": "LED status code 10 = งดขาย (suspended by plaintiff or officer) is NOT the same as code 3 = งดขายไม่มีผู้สู้ราคา (no bidders showed up). Code 10 means the sale was halted by a party — that round doesn't count. Code 3 means auction happened but no one bid — property will go to next round at lower price.",
            "description": "LED status code 10 vs 3 distinction",
            "category": "legal",
            "area": "",
            "source": "LED_manual",
        },
        {
            "content": "Old ธนาคารออมสิน (GSB) cases from 2559-2561 appear more likely to be perpetually suspended — possibly GSB policy to keep suspending while debtor negotiates repayment. Assets 1872721 (case ผบ.2618/2561) and 1873488 (case ผบ.9337/2559) both งดขาย ALL 6 rounds by GSB. LED manual section 9: งดขาย = คู่ความงดขาย or เจ้าพนักงานงดขาย. Strategy: Monitor, don't chase. Focus on Code 3 properties with confirmed auctions instead.",
            "description": "GSB old cases perpetually suspended pattern",
            "category": "legal",
            "area": "สงขลา",
            "source": "analysis",
        },
        {
            "content": "LED auction price rules: นัดที่ 1 = 100% of appraised/committee price. นัดที่ 2 = 90% (ลด 10%). นัดที่ 3 = 80% (ลด 20%). นัดที่ 4+ = 70% floor (ลดสูงสิด 30%) — price cannot go lower than this. Key implication: All 94 Bangkok NPA condos at 6th round are already at 70% floor.",
            "description": "LED auction round price reduction rules",
            "category": "legal",
            "area": "",
            "source": "LED_manual",
        },
    ]
    
    total = len(findings)
    success = 0
    errors = 0
    
    print(f"Starting batch ingestion of {total} findings from MEMORY.md")
    print(f"KB database: {pg_uri}")
    
    for i, f in enumerate(findings, 1):
        try:
            ok = ingest_with_metadata(
                kb, pg_uri,
                f["content"],
                f["description"],
                f["category"],
                f["area"],
                f["source"],
                i, total,
            )
            if ok:
                success += 1
            else:
                errors += 1
        except Exception as e:
            print(f"  FATAL ERROR: {e}")
            errors += 1
    
    print(f"\n{'='*60}")
    print(f"BATCH COMPLETE: {success} succeeded, {errors} failed out of {total}")
    
    # Show metadata stats
    result = run_psql(pg_uri, "SELECT category, COUNT(*) FROM kb_metadata GROUP BY category ORDER BY category;")
    if result.returncode == 0:
        print(f"\nKB metadata by category:")
        print(result.stdout)


if __name__ == "__main__":
    main()

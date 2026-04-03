#!/usr/bin/env python3
"""Ingest remaining MEMORY.md findings not yet in KB. Run in small batches."""

import hashlib
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lightrag_wrapper import LightRAGManager, POSTGRES_DEFAULT_URI

CATEGORY_TTL = {
    "pricing": 90, "rental": 90, "flood": 365, "legal": 180,
    "area": 180, "project": 365, "infrastructure": 365, "other": 180,
}

def make_doc_id(content: str) -> str:
    return f"npa-{hashlib.sha256(content.encode()).hexdigest()[:16]}"

def already_exists(pg_uri, content):
    doc_id = make_doc_id(content)
    r = subprocess.run(["psql", pg_uri, "-t", "-A", "-c",
        f"SELECT COUNT(*) FROM kb_metadata WHERE doc_id='{doc_id}';"],
        capture_output=True, text=True, timeout=10)
    return r.stdout.strip() != "0"

def ingest(kb, pg_uri, content, description, category, area, source, idx, total):
    if already_exists(pg_uri, content):
        print(f"  [{idx}/{total}] SKIP (already exists): {description[:60]}")
        return True
    
    ttl = CATEGORY_TTL.get(category, 180)
    today = datetime.now().strftime("%Y-%m-%d")
    header = f"[Date: {today}] [Category: {category}] [Area: {area or 'unspecified'}] [Source: {source or 'unspecified'}] [Valid for: {ttl} days]\n\n"
    enriched = header + content
    
    print(f"  [{idx}/{total}] INGEST: {description[:60]}")
    result = kb.insert_document(enriched, description)
    print(f"    -> {result[:80]}")
    
    doc_id = make_doc_id(content)
    desc_esc = description[:500].replace("'", "''")
    area_esc = (area or "").replace("'", "''")
    src_esc = (source or "").replace("'", "''")
    sql = f"INSERT INTO kb_metadata (doc_id, category, area, source, summary, valid_until) VALUES ('{doc_id}', '{category}', '{area_esc}', '{src_esc}', '{desc_esc}', NOW() + INTERVAL '{ttl} days');"
    r = subprocess.run(["psql", pg_uri, "-c", sql], capture_output=True, text=True, timeout=10)
    if r.returncode == 0:
        print(f"    -> Metadata OK")
    else:
        print(f"    -> Metadata ERROR: {r.stderr[:100]}")
    return True

def main():
    env_path = Path("/Users/arsapolm/.nanobot-npa-guy/workspace/.env")
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, value = line.partition("=")
                    os.environ.setdefault(key.strip(), value.strip())
    
    kb = LightRAGManager()
    pg_uri = os.environ.get("POSTGRES_URI", POSTGRES_DEFAULT_URI)
    
    findings = [
        # RENTAL items missing from KB
        {"content": "Lumpini Place Ratchada-Thapra บุคคโล: estimated rental 12,000 THB/month for 35.84 sqm 1BR unit. Gross yield 7.31%, net yield 6.22%. Two adjacent NPA units available (1993960, 1993961) at 50,700 THB/sqm.", "description": "Lumpini Place rental rate yield บุคคโล", "category": "rental", "area": "บุคคโล", "source": "calc_analysis"},
        {"content": "DCondo Hatyai คอหงส์: rental ~6,000-7,000 THB/month. Student-oriented condo near PSU campus.", "description": "DCondo Hatyai rental rate คอหงส์", "category": "rental", "area": "คอหงส์", "source": "web_search"},
        {"content": "BENU Residence คอหงส์: rental ~15,000 THB/month. Higher-end condo near PSU. Resale ~65,000 THB/sqm.", "description": "BENU Residence rental rate คอหงส์", "category": "rental", "area": "คอหงส์", "source": "web_search"},
        {"content": "เมืองสงขลา near มอ.ทักษิณ (Thaksin University): student apartment rentals 3,500-8,000 THB/month. Also near มรภ.สงขลา (Rajabhat Songkhla) 816m away.", "description": "Thaksin University student rental เมืองสงขลา", "category": "rental", "area": "เมืองสงขลา", "source": "RentHub"},
        {"content": "Songkhla NPA 1896940 คอหงส์ near PSU: 34.9 wa house, purchase 1.12M, acquisition 1.36M (incl renovation 200K), estimated rent 8,000/mo, gross yield 7.08%, net yield 6.02%, break-even 16.6 years. BEST PICK for student rental near PSU. Deed: โฉนด. Round 5 Apr 21.", "description": "Songkhla PSU NPA 1896940 yield analysis", "category": "rental", "area": "คอหงส์", "source": "calc_analysis"},
        {"content": "Songkhla NPA 1872721 เมืองสงขลา พะวง: 56.5 wa house, purchase 528K, gross yield 10.38%, net yield 8.82%, break-even 11.3 years. STRONG BUY but all 6 rounds งดขาย (code 10, suspended by GSB). Case ผบ.2618/2561 from ธนาคารออมสิน. Deed: สำเนาโฉนด. Must investigate why always suspended.", "description": "Songkhla Town NPA 1872721 yield analysis", "category": "rental", "area": "เมืองสงขลา", "source": "calc_analysis"},
        {"content": "Songkhla NPA 1873488 เมืองสงขลา ทุ่งหวัง: 99.0 wa house, purchase 868K at 8,767 THB/wa, gross yield 8.79%, net yield 7.47%, break-even 13.4 years. BUY but all 6 rounds งดขาย (code 10, suspended by GSB). Case ผบ.9337/2559 from ธนาคารออมสิน. Deed: โฉนด.", "description": "Songkhla Town NPA 1873488 yield analysis", "category": "rental", "area": "เมืองสงขลา", "source": "calc_analysis"},
        {"content": "พญาไท BTS Sanam Pao: estimated rental 15,000 THB/month for 32.80 sqm unit. Gross yield 6.9%, net yield 5.87%. But NPA price 74,317/sqm is ABOVE market ~61K/sqm by +22%. OVERPRICED.", "description": "พญาไท rental rate BTS Sanam Pao", "category": "rental", "area": "พญาไท", "source": "calc_analysis"},
        
        # AREA items missing from KB
        {"content": "สุขุมวิท 77 อ่อนนุช: BTS On Nut at doorstep. Market prices 50,000-103,000 THB/sqm. Strong rental demand area. Good transit access. No NPA condos currently available here but worth monitoring.", "description": "Area intelligence สุขุมวิท 77 อ่อนนุช", "category": "area", "area": "อ่อนนุช", "source": "location_intel"},
        {"content": "คลองสาน คลองต้นไทร The River: NPA units at 91,000-131,000 THB/sqm vs market 187,000-227,000 THB/sqm = 35-60% below market. Best NPA discount in Bangkok. 4 units available, 4.8M-16.8M, median 9.98M. Premium riverfront. BTS Krung Thon Buri 784m.", "description": "คลองสาน The River NPA discount analysis", "category": "area", "area": "คลองสาน", "source": "analysis"},
        {"content": "บางยี่เรือ ธนบุรี Motif Condo: NPA at 73,800 THB/sqm, market avg 68,880 THB/sqm = ABOVE market by +7%. NOT a deal. OVERPRICED. Asset 2007239, R1 May 19.", "description": "บางยี่เรือ Motif NPA above market", "category": "area", "area": "บางยี่เรือ", "source": "analysis"},
        {"content": "บุคคโล ธนบุรี Lumpini Place Ratchada-Thapra: NPA at 50,700 THB/sqm vs market resale ~62,800 THB/sqm = -19% below market. BUY recommendation. Two adjacent units 1993960+1993961, buy both for 3.63M. Yield 7.31%/6.22%. R1 auction Apr 28. Best Bangkok NPA condo deal.", "description": "บุคคโล Lumpini Place BUY recommendation", "category": "area", "area": "บุคคโล", "source": "analysis"},
        {"content": "ราษฎร์บูรณะ บางปะกอก ISSI Condo: NPA at 66,800-78,500 THB/sqm vs market 66,666 THB/sqm = AT or ABOVE market. NOT a deal. Corrected from initial -70% claim (was wrong due to size unit error).", "description": "ราษฎร์บูรณะ ISSI above market correction", "category": "area", "area": "ราษฎร์บูรณะ", "source": "analysis"},
        {"content": "พญาไท สามเสนใน BTS Sanam Pao: NPA 1999047 at 74,317 THB/sqm vs market ~61,000 THB/sqm = ABOVE market by +22%. OVERPRICED. Corrected from initial -70% claim (was wrong due to size unit error).", "description": "พญาไท above market correction", "category": "area", "area": "พญาไท", "source": "analysis"},
        {"content": "Bangkok NPA condo district tier classification: TIER 1 (near BTS/MRT, strong) = คลองสาน, ธนบุรี, พญาไท, ดินแดง, บางกอกน้อย. TIER 2 (some transit, decent) = ภาษีเจริญ, ราษฎร์บูรณะ, บางพลัด, จอมทอง, บางขุนเทียน. TIER 3 (poor transit, flood-prone) = หนองแขม, ดอนเมือง, บางแค, ตลิ่งชัน, บางเขน, บางกอกใหญ่. 37 TIER 3 properties eliminated.", "description": "Bangkok NPA condo district tier classification", "category": "area", "area": "กรุงเทพมหานคร", "source": "analysis"},
        {"content": "Songkhla NPA overview: 508 total properties, ZERO condos (all ที่ดินพร้อมสิ่งปลูกสร้าง). PSU มอ.สงขลานครินทร์ campus in คอหงส์/หาดใหญ่ — 13 NPA properties (houses 1.23-2.98M, 13-50.6 wa). มอ.ทักษิณ and มรภ.สงขลา in เมืองสงขลา — 20 NPA properties in ทุ่งหวัง, บ่อยาง, พะวง (0.53-2.21M). Hat Yai คลองแห ~30+ properties near PSU south.", "description": "Songkhla NPA overview university areas", "category": "area", "area": "สงขลา", "source": "led_query"},
        {"content": "Songkhla Town เมืองสงขลา: มอ.ทักษิณ (Thaksin Univ) at 7.163,100.609 and มรภ.สงขลา (Rajabhat) at 7.171,100.614 — 816m apart. Student rental market 3,500-8,000/mo near ม.ทักษิณ. House prices in พะวง: 45,000-70,000/wa. LED branch แขวงสงขลา: (074) 311292, 314904.", "description": "Songkhla Town university area intel", "category": "area", "area": "เมืองสงขลา", "source": "location_intel"},
        {"content": "ดินแดง MRT Phra Ram 9: NPA asset 1867367 at 42,139 THB/sqm (43.68 sqm). SPECULATIVE — best discount at -55 to -65% below market BUT 5 rounds with zero bidders (งดขายไม่มีผู้สู้ราคา). May have hidden issues. R6 auction Apr 3. Market comparables: Life Ratchadapisek 101,811/sqm, Ideo Mobi 119,354/sqm.", "description": "ดินแดง NPA speculative 5 rounds no bidders", "category": "area", "area": "ดินแดง", "source": "analysis"},
        
        # FLOOD items missing from KB
        {"content": "คอหงส์ Hat Yai flood risk: MEDIUM. Confirmed flooding Nov 2567 and Nov 2568 in ทุ่งลุง-คอหงส์ area. Roads blocked, boats needed. Must inspect properties after rain. Songkhla all 16 districts affected Nov 2568 affecting 690K people.", "description": "คอหงส์ Hat Yai flood risk MEDIUM", "category": "flood", "area": "คอหงส์", "source": "news"},
        {"content": "เมืองสงขลา flood risk: ทล.4309 ทุ่งหวัง-สงขลา flooded 10-15cm Nov 2567. All 16 Songkhla districts affected Nov 2568 (690K people). MEDIUM risk. Must verify property elevation before bidding.", "description": "เมืองสงขลา flood risk MEDIUM", "category": "flood", "area": "เมืองสงขลา", "source": "news"},
        
        # LEGAL items missing from KB
        {"content": "LED auction status codes: Code 10 = งดขาย (suspended by plaintiff or officer) — that round does NOT count toward price reduction. Code 3 = งดขายไม่มีผู้สู้ราคา (no bidders showed up) — auction DID happen, property goes to next round at lower price. These are fundamentally different. Always check status_code in auction_history table.", "description": "LED status code 10 vs 3 distinction", "category": "legal", "area": "", "source": "LED_manual"},
        {"content": "ธนาคารออมสิน (GSB) old cases (2559-2561) pattern: appear more likely to be perpetually suspended via code 10 งดขาย. Likely GSB policy to keep suspending while debtor negotiates repayment. Assets 1872721 (case ผบ.2618/2561) and 1873488 (case ผบ.9337/2559) both งดขาย ALL 6 rounds. LED manual section 9: งดขาย = คู่ความงดขาย or เจ้าพนักงานงดขาย. Strategy: Monitor but don't chase. Focus on Code 3 properties with confirmed auctions.", "description": "GSB old cases perpetually suspended", "category": "legal", "area": "สงขลา", "source": "analysis"},
        {"content": "LED auction round price reduction rules: นัดที่ 1 = 100% of appraised/committee price. นัดที่ 2 = 90% (ลด 10%). นัดที่ 3 = 80% (ลด 20%). นัดที่ 4+ = 70% floor (ลดสูงสิด 30%) — price cannot go lower than 70%. Key implication: All 94 Bangkok NPA condos at 6th round are already at the 70% floor price.", "description": "LED auction round price reduction rules", "category": "legal", "area": "", "source": "LED_manual"},
    ]
    
    total = len(findings)
    success = 0
    skipped = 0
    errors = 0
    
    print(f"Ingesting {total} remaining findings...")
    
    for i, f in enumerate(findings, 1):
        try:
            ok = ingest(kb, pg_uri, f["content"], f["description"], f["category"], f["area"], f["source"], i, total)
            if ok:
                if already_exists(pg_uri, f["content"]):
                    skipped += 1
                else:
                    success += 1
        except Exception as e:
            print(f"    FATAL: {e}")
            errors += 1
    
    print(f"\nDone: {success} ingested, {skipped} skipped (existed), {errors} errors out of {total}")

if __name__ == "__main__":
    main()

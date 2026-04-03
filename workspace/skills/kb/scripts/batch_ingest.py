#!/usr/bin/env python3
"""Batch ingest with metadata (category, area, source)."""
import os
import sys
import importlib

# Set up paths so relative imports in __init__.py work
here = os.path.dirname(os.path.abspath(__file__))
parent = os.path.dirname(here)
sys.path.insert(0, parent)
sys.path.insert(0, here)

import lightrag_wrapper
import kb_tools

kb = kb_tools.KBToolkit()

def ingest(content, description, category, area, source):
    print(f"\n--- Ingesting: {description[:60]}...")
    result = kb.insert_document(
        content=content,
        description=description,
        category=category,
        area=area,
        source=source,
    )
    print(f"  -> {result[:150]}")

# ============================================================
# DISTRICT 1: ราษฎร์บูรณะ — PRICING
# ============================================================

ingest(
    "Rat Burana condo resale prices April 2026: Average price per sqm in Rat Burana is THB 73,906/sqm (Hipflat), 48.1% lower than Bangkok average. Dot Property reports average listing price THB 3,912,900 with average price/sqm THB 85,063 for 46 sqm average size. FazWaz median price/sqm USD 2,424 (~THB 84,000/sqm). Thailand-Property listing at THB 1,450,000 (THB 53,800/sqm) for 2010-built condo. Ivy River Ratburana Studio 30 sqm listed at THB 2,400,000 (THB 80,000/sqm). Chapter One Modern Dutch Ratburana 33 listed at THB 1,350,000 (THB 61,364/sqm). NPA units range THB 171K-2.37M for 25-32 sqm, which is significantly below market indicating very distressed pricing.",
    "Rat Burana condo resale prices April 2026",
    "pricing", "ราษฎร์บูรณะ", "Hipflat"
)

ingest(
    "ISSI Condo Suksawat resale prices April 2026: Average sale price THB 66,666/sqm at ISSI Condo (Hipflat), down 2.9% YoY. 8 units for sale at THB 1,660,000-3,100,000. Specific listings: 30.14 sqm at THB 1.99M (THB 66,025/sqm), studio 24.8 sqm at THB 2.10M (THB 84,643/sqm), 1BR at THB 1.75M. ISSI price is 9.8% below Rat Burana district average and 52.7% below Bangkok average. Price trend: declining.",
    "ISSI Condo Suksawat sale prices April 2026",
    "pricing", "ราษฎร์บูรณะ", "Hipflat"
)

ingest(
    "Nue Riverest Ratburana resale prices April 2026: Average sale price THB 100,961/sqm (Hipflat), 36.6% ABOVE district average, 28.3% below Bangkok average. 32 units for sale THB 2,230,000-11,669,900. Completed Dec 2025 by Noble Development. 8 buildings, 35 floors. Price trend slightly down 2.3% YoY. Premium project in Rat Burana area.",
    "Nue Riverest Ratburana sale prices April 2026",
    "pricing", "ราษฎร์บูรณะ", "Hipflat"
)

# ============================================================
# DISTRICT 1: ราษฎร์บูรณะ — RENTAL
# ============================================================

ingest(
    "Rat Burana condo rental rates April 2026: Average rental THB 16,000/month (Hipflat). District average rental THB 366/sqm vs Bangkok THB 625/sqm. Lumpini Ville Ratburana-Riverview 23 sqm listed for rent, 1BR 30.96 sqm at THB 9,500/month (THB 307/sqm). ZMyHome listing 1BR at THB 8,500/month (THB 274/sqm). LPN Ratburana rental cheapest starts THB 7,000/month. PropertyHub has 540+ rental listings near Rat Burana Road.",
    "Rat Burana condo rental rates April 2026",
    "rental", "ราษฎร์บูรณะ", "DDProperty"
)

ingest(
    "ISSI Condo Suksawat rental rates April 2026: Average rental THB 250/sqm (Hipflat), 31.8% below district average of THB 366/sqm. Studio 25.2 sqm listed for rent. Livinginsider: 1BR at THB 9,000/month. ZMyHome listing studio at THB 8,000/month. PropertyHub: 30 sqm 1BR with washing machine available. For a 25-30 sqm unit, typical rent THB 7,500-9,000/month.",
    "ISSI Condo Suksawat rental rates April 2026",
    "rental", "ราษฎร์บูรณะ", "Hipflat"
)

ingest(
    "Nue Riverest Ratburana rental rates April 2026: Average rental THB 436/sqm (Hipflat), 19.1% ABOVE district average THB 366/sqm. 3 units for rent at THB 10,000-18,000/month. Premium rental rates for this Noble Development project. For 25-32 sqm studio/1BR, estimated rent THB 10,000-14,000/month.",
    "Nue Riverest Ratburana rental rates April 2026",
    "rental", "ราษฎร์บูรณะ", "Hipflat"
)

# ============================================================
# DISTRICT 1: ราษฎร์บูรณะ — PROJECTS
# ============================================================

ingest(
    "ISSI Condo Suksawat (อิซซี่ คอนโด สุขสวัสดิ์): Developer: Charn Issara Development. Located at Suk Sawat 17, Bang Pakok, Rat Burana. Completed Jan 2014 (BE 2557). 24 floors, 892 units. Amenities: pool, sauna, convenience store, gym, playground, parking, security. Near BTS Talat Phlu ~15 min. Hospital: Bangkok Bang Pakok 1 at 820m. Near Big C, Tesco Lotus Bang Pakok, Royal Garden Plaza, Max Value Rama 3. Schools: Bang Pakok Wittayakhom, Wat Bang Pakok.",
    "ISSI Condo Suksawat project details",
    "project", "ราษฎร์บูรณะ", "Hipflat"
)

ingest(
    "Nue Riverest Ratburana (นิว ริเวอร์เรสต์ ราษฎร์บูรณะ): Developer: Noble Development. Located at 60/1 Rat Burana 36. Completed Dec 2025. 8 buildings, 35 floors. High-rise + mid-rise riverside resort condo on Chao Phraya riverfront. Amenities: parking, concierge, gym, co-working, sauna, security, pool. 10 minutes to Rama 3. First Nue brand riverside project. Same developer as Nue District R9.",
    "Nue Riverest Ratburana project details",
    "project", "ราษฎร์บูรณะ", "Hipflat"
)

ingest(
    "Other condo projects in Rat Burana: Lumpini Ville Ratburana-Riverview (LPN, mid-rise, popular for NPA units), Chapter One Modern Dutch Ratburana 33, Ivy River Ratburana, Garden Court (avg sale USD 881/sqm, downtrend), Baan Klang Muang Rama 3-Ratburana (townhouse project). Grand Bangkok Boulevard Suksawat-Rama 3 is a new development.",
    "Rat Burana condo projects overview",
    "project", "ราษฎร์บูรณะ", "web_search"
)

# ============================================================
# DISTRICT 1: ราษฎร์บูรณะ — AREA (Transit, Amenities)
# ============================================================

ingest(
    "Rat Burana transit April 2026: Currently NO direct BTS/MRT station in Rat Burana. Nearest BTS stations are Talat Phlu (BTS Silom line) ~15 min by public transport, and Wutthakat. Purple Line South extension (Taopoon-Ratburana, 17 stations, 23.6 km) is under construction by MRTA, will serve the Suk Sawat area and connect to Sam Yaek Mahasawat. Expected stations include Rat Burana and Pracha Uthit. DDProperty area guide confirms transit via bus and river crossing to Rama 3 side.",
    "Rat Burana transit and BTS access",
    "area", "ราษฎร์บูรณะ", "web_search"
)

ingest(
    "Rat Burana area profile: District on Thonburi side along Chao Phraya River, opposite Rama 3 Road. Main roads: Rat Burana Road (6 lanes), Suk Sawat Road, Pracha Uthit Road. Mixed residential, small-to-large industrial, and commercial. Relatively quiet residential area. Connected to city center via expressway and bridge crossings. Near Big C, Tesco Lotus Bang Pakok, Central Plaza Rama 3 (across river). Growing slowly with new condo developments.",
    "Rat Burana area profile and amenities",
    "area", "ราษฎร์บูรณะ", "DDProperty"
)

# ============================================================
# DISTRICT 1: ราษฎร์บูรณะ — FLOOD
# ============================================================

ingest(
    "Rat Burana flood risk: Located along Chao Phraya River, subject to seasonal flooding risk. MRTA Purple Line South construction has flood mitigation measures for construction zones. Area is low-lying on Thonburi side. In 2011 major floods, western Bangkok/Thonburi areas experienced significant flooding. Rat Burana has mixed flood risk - areas closer to river and canals (Khlong Rat Burana, Khlong Bang Phueng) are higher risk, while elevated road areas are lower risk. Purple Line construction may improve drainage infrastructure.",
    "Rat Burana flood risk assessment",
    "flood", "ราษฎร์บูรณะ", "web_search"
)

# ============================================================
# DISTRICT 2: จอมทอง — PRICING
# ============================================================

ingest(
    "Chom Thong condo resale prices April 2026: Average price per sqm THB 58,533 (Thailand-Property). FazWaz median price ~USD 2,122/sqm. Hipflat listing: 26 sqm 1BR at THB 1,750,000 (THB 67,500/sqm). Lazudi: 2BR 62.2 sqm at THB 4.59M (THB 73,771/sqm). FazWaz studio avg USD 53,707, 1BR avg USD 68,628. DDProperty: 251 listings, 28 sqm near BTS Wutthakat at 15 min (1.26 km). PropertyScout 1BR avg THB 3,612,500. Baania: 23.75 sqm at THB 1,790,000. PropertyHub listing 2BR 62.1 sqm at THB 800,000 (THB 12,882/sqm - extremely cheap, possibly foreclosed).",
    "Chom Thong condo resale prices April 2026",
    "pricing", "จอมทอง", "Thailand-Property"
)

ingest(
    "Chom Thong NPA pricing context: NPA units 26-35 sqm priced THB 329K-1.97M. At THB 329K for 26 sqm equals THB 12,654/sqm (extremely cheap vs market THB 58,533/sqm avg). At THB 1.97M for 35 sqm equals THB 56,286/sqm (near market average). Key projects: The Key Sathorn-Ratchaphruek (near BTS Wutthakat ~200m), Aspire Sathorn-Taksin, The Tempo Grand Sathorn-Wutthakat, Niche ID Rama 2-Dao Khanong.",
    "Chom Thong NPA unit pricing vs market",
    "pricing", "จอมทอง", "web_search"
)

# ============================================================
# DISTRICT 2: จอมทอง — RENTAL
# ============================================================

ingest(
    "Chom Thong condo rental rates April 2026: PropertyHub 560+ listings for rent in Chom Thong. DDProperty: 91 rental listings. FazWaz: 1BR 32 sqm rental at USD 277/month (~THB 9,500/month), rental yield 9%. Another listing: 1BR rental THB 13,000/month with 5% yield. Baania: Niche ID Rama 2-Dao Khanong 30 sqm for rent under THB 8,000/month. ZMyHome: 255 rental listings in Chom Thong. Dot Property: 141 rental listings. Estimated 1BR 26-35 sqm rent range: THB 7,000-13,000/month depending on proximity to BTS Wutthakat.",
    "Chom Thong condo rental rates April 2026",
    "rental", "จอมทอง", "DDProperty"
)

# ============================================================
# DISTRICT 2: จอมทอง — AREA (Transit)
# ============================================================

ingest(
    "Chom Thong transit April 2026: BTS Wutthakat station (S11, Silom line) is the main transit hub, located in Bang Kho subdistrict. The Key Sathorn-Ratchaphruek is ~200m from BTS Wutthakat. Some condos 400m from BTS. Other areas of Chom Thong are 1-3 km from BTS, accessible via motorcycle taxi or bus. Major roads: Rama 2 (Phetkasem), Ratchaphruek, Ekachai. Near The Mall Tha Phra and Dao Khanong area. Good connectivity to Sathorn via BTS.",
    "Chom Thong transit and BTS access",
    "area", "จอมทอง", "web_search"
)

# ============================================================
# DISTRICT 2: จอมทอง — FLOOD
# ============================================================

ingest(
    "Chom Thong Bangkok flood risk: Bangkok's Chom Thong district (not to be confused with Chiang Mai's Chom Thong) is located on the Thonburi side. BMA has a flood preparedness plan for Chom Thong district (fiscal year 2024, project ID 4354). The area along Rama 2 road and near canals may experience localized flooding during heavy rain. Generally lower flood risk than riverfront areas due to being further inland from Chao Phraya. Note: web search results for Chom Thong flooding mostly returned Chiang Mai district, not Bangkok.",
    "Chom Thong Bangkok flood risk assessment",
    "flood", "จอมทอง", "web_search"
)

# ============================================================
# DISTRICT 3: บางขุนเทียน — PRICING
# ============================================================

ingest(
    "Bang Khun Thian condo resale prices April 2026: Median price/sqm THB 49,818 (Thailand-Property). FazWaz median price/sqm USD 1,503 (~THB 52,000/sqm), 43.8% lower than Bangkok median. Hipflat listing: 26 sqm 1BR at THB 1,690,000 (THB 65,000/sqm), completed 2017. District average sale price THB 51,182/sqm (Hipflat). Baania: secondhand condo 28 sqm Smart Condo at very cheap prices. Condos sale starting THB 1,300,000 in Rama 2-Bang Khun Thian area. NPA units priced THB 1.36M-2.80M for 27-35 sqm equals THB 38,857-103,704/sqm range.",
    "Bang Khun Thian condo resale prices April 2026",
    "pricing", "บางขุนเทียน", "Thailand-Property"
)

ingest(
    "Smart Condo Rama 2 resale prices April 2026: Average sale price THB 34,385/sqm (Hipflat), 32.8% below district average THB 51,182/sqm. 39 units for sale at THB 790,000-1,400,000. Completed Jan 2009 by Prinsiri. 8 buildings, 8 floors, 2,202 units total. Price down 2.7% YoY. Near Rama 2 Hospital 1.1 km. Near Central Plaza Rama 2, tollway 3 km. This is a mass-market budget condo with very low entry prices.",
    "Smart Condo Rama 2 sale prices April 2026",
    "pricing", "บางขุนเทียน", "Hipflat"
)

# ============================================================
# DISTRICT 3: บางขุนเทียน — RENTAL
# ============================================================

ingest(
    "Bang Khun Thian condo rental rates April 2026: Average rental THB 288/sqm (Hipflat), 53% lower than Bangkok median. FazWaz: studio to 1BR rental from THB 6,500/month for 50 sqm units. Hipflat: 1BR avg rental USD 232/month (~THB 8,000/month). Smart Condo Rama 2: 11 units for rent THB 5,000-53,000/month, average THB 272/sqm, up 29.4% YoY. Baania: Smart Condo Rama 2 28 sqm at THB 5,500/month with furniture. NHA Thonburi 2 rental at THB 6,000/month. Budget rental market, THB 5,000-8,000/month for 28-30 sqm.",
    "Bang Khun Thian condo rental rates April 2026",
    "rental", "บางขุนเทียน", "Hipflat"
)

# ============================================================
# DISTRICT 3: บางขุนเทียน — AREA
# ============================================================

ingest(
    "Bang Khun Thian area profile: Only Bangkok district with coastline on the Gulf of Thailand (~5 km coastline). NE part is residential/commercial/industrial, most of district is agricultural with eco-tourism attractions. Attractions: Bang Khun Thian seaside viewpoint, Suan Thian Thalay Phatthanaphon Park, mangrove forests. Near Rama 2 Road corridor. Close to Samut Sakhon province. Industrial estates and warehouses in the area. Area is developing with future infrastructure potential. Currently NO direct BTS/MRT access - depends on buses and private transport.",
    "Bang Khun Thian area profile",
    "area", "บางขุนเทียน", "web_search"
)

ingest(
    "Bang Khun Thian development outlook: DDProperty describes Bang Khun Thian as an area with growth potential and improving infrastructure. Rama 2 Road is the main arterial with ongoing expressway access. Central Plaza Rama 2 is a major shopping center. Industrial zones provide employment base. Limitations: far from city center, no rail transit, coastal erosion concerns. Condo market is budget-oriented with Smart Condo Rama 2 (2,202 units by Prinsiri) and Casa City Rama 2 as major projects.",
    "Bang Khun Thian development outlook",
    "area", "บางขุนเทียน", "DDProperty"
)

# ============================================================
# DISTRICT 3: บางขุนเทียน — FLOOD
# ============================================================

ingest(
    "Bang Khun Thian flood risk: HIGH RISK due to coastal location on Gulf of Thailand. Only Bangkok district with sea coastline. Pantip discussions highlight concern about seawater erosion gradually encroaching on land. Coastal community Wat Hua Krabue reports year-round flooding problems. Tidal flooding affects low-lying sois near the sea. Mangrove forests provide some natural protection. Climate change and sea level rise pose long-term threat to property values. Properties closer to Rama 2 road (inland) have lower flood risk than coastal areas.",
    "Bang Khun Thian flood risk assessment - coastal",
    "flood", "บางขุนเทียน", "Pantip"
)

# ============================================================
# DISTRICT 3: บางขุนเทียน — PROJECTS
# ============================================================

ingest(
    "Smart Condo Rama 2 project details: Developer: Prinsiri. Located at Rama 2 Soi 60, Samae Dam, Bang Khun Thian. Completed Jan 2009. 8 buildings, 8 floors, 2,202 units. Amenities: pool, fitness, garden, BBQ, sauna, parking, security, playground. Near Central Plaza Rama 2, Rama 2 Hospital (1.1 km), tollway (3 km). Mass-market budget condo. Schools nearby: Supichaya, Jaruwatthanukun, Sirinunsornwithaya. Avg sale THB 34,385/sqm (Hipflat).",
    "Smart Condo Rama 2 project details",
    "project", "บางขุนเทียน", "Hipflat"
)

ingest(
    "Other condo projects in Bang Khun Thian: Casa City Rama 2 (Hipflat lists avg sale price 43.8% below Bangkok), Modern Condo The Forest Rama 2-Ekachai, NHA Thonburi 2 (government housing, very cheap rental at THB 6,000/month). 12 condo projects total in district (Dot Property). Market is dominated by budget/mass-market developments along Rama 2 corridor.",
    "Bang Khun Thian condo projects overview",
    "project", "บางขุนเทียน", "web_search"
)

print("\n\n=== ALL INGESTS COMPLETE ===")

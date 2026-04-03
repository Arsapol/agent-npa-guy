#!/bin/bash
# Batch ingest Thonburi/River Edge area research findings
# Each finding has metadata embedded in text header

cd /Users/arsapolm/.nanobot-npa-guy/workspace/skills/kb/scripts
source /Users/arsapolm/.nanobot-npa-guy/workspace/.env

INGEST="python cli_ingest.py"

# ============================================================
# DISTRICT 1: บางปะกอก / ราษฎร์บูรณะ (ISSI Condo area)
# ============================================================

# 1a. ISSI Condo - Project Info
$INGEST --text "[Area: บางปะกอก | Category: project | Source: Hipflat | Date: 2026-04-03]
ISSI Condo Suksawat (อิซซี่ คอนโด สุขสวัสดิ์) project details:
Location: สุขสวัสดิ์ 22 บางปะกอก ราษฎร์บูรณะ กรุงเทพ 10140
Developer: Charn Issara Development
Completed: Jan 2015 (2557), 24 floors, 892 units
Average sale price Hipflat: 70,000 THB/sqm (9 units listed, trend: downtrend)
Nearest BTS: ตลาดพลู (about 15 min travel)
Amenities: pool, sauna, convenience store
Nearby: Big C บางปะกอก 150m, Tesco Lotus บางปะกอก 1km, Bang Pakok Hospital 1 (820m)
Schools: บางปะกอกวิทยาคม, วัดบางปะกอก, เยาวลักษณ์วิทยาธนบุรี" \
--description "ISSI Condo Suksawat project details"

# 1b. ISSI Condo - Rental
$INGEST --text "[Area: บางปะกอก | Category: rental | Source: DDProperty/FazWaz | Date: 2026-04-03]
ISSI Condo Suksawat rental rates:
Studio/1BR (25-30 sqm): 7,000-9,900 THB/month (DDProperty range)
Average annual rental yield: 4% (FazWaz estimate)
Specific listings: 1BR floor 23 at 9,000 THB/month; 30 sqm units around 9,100 THB/month
Rental trend: moderate demand due to Big C/nearby offices
Comparable: Flexi Suksawad 26 sqm rents at 9,100 THB/month" \
--description "ISSI Condo rental rates April 2026"

# 1c. สุขสวัสดิ์/บางปะกอก - Area
$INGEST --text "[Area: บางปะกอก | Category: area | Source: web_search | Date: 2026-04-03]
สุขสวัสดิ์ road ย่านบางปะกอก ราษฎร์บูรณะ area intelligence:
Nearest BTS: ตลาดพลู (about 15 min by public transport)
Nearest MRT: ไม่ตรง ต้องใช้รถเมล์/รถตู้
Major roads: สุขสวัสดิ์, พระราม 3, ประชาอุทิศ
Shopping: Big C บางปะกอก, Tesco Lotus บางปะกอก, Major Hollywood สุขสวัสดิ์ (2km), Big C Extra บางปะกอก (1.5km), Homepro พระราม 3 (2km)
Hospital: โรงพยาบาลบางปะกอก 1 (820m from ISSI), โรงพยาบาลเจริญกรุงประชารักษ์ (5km)
Riverfront: ติดแม่น้ำเจ้าพระยาฝั่งธนบุรี Asiatique Riverfront ห่าง 5.3km
Character: ย่านพักอาศัยเก่าแก่ ไม่ใช่ CBD ค่อนข้าง quiet residential
ข้อสังเกต: พื้นที่เป็นที่ราบติดแม่น้ำเจ้าพระยา ระดับน้ำท่วมต้องพิจารณา" \
--description "สุขสวัสดิ์ บางปะกอก area intelligence"

# 1d. บางปะกอก - Flood
$INGEST --text "[Area: บางปะกอก | Category: flood | Source: web_search/Thai PBS | Date: 2026-04-03]
บางปะกอก ราษฎร์บูรณะ flood risk assessment:
พื้นที่ติดแม่น้ำเจ้าพระยาฝั่งธน เป็นพื้นที่เสี่ยงน้ำท่วมระดับ MEDIUM
ระดับน้ำแม่น้ำเจ้าพระยาสูงขึ้นกระทบพื้นที่ริมน้ำโดยตรง
GISTDA ระบุ บางพลัด บางกอกน้อย บางกอกใหญ่ ธนบุรี เป็นพื้นที่ใกล้แม่น้ำที่ต้องระวัง
อาคารสูงเช่น ISSI Condo 24 ชั้น มีความเสี่ยงต่ำสำหรับชั้นสูง แต่ชั้นล่าง/โรงจอดรถอาจได้รับผลกระทบ
พ.ศ. 2554 (2011) น้ำท่วมกรุงเทพครั้งใหญ่ พื้นที่ริมแม่น้ำได้รับผลกระทบ" \
--description "บางปะกอก flood risk assessment"

# ============================================================
# DISTRICT 2: บางพลัด / บางอ้อ (3 NPA condos)
# ============================================================

# 2a. บางพลัด - Pricing
$INGEST --text "[Area: บางพลัด | Category: pricing | Source: Thailand-Property/FazWaz/DDProperty | Date: 2026-04-03]
บางพลัด condo sale market prices:
Median price per sqm: 85,123 THB/sqm (Thailand-Property data)
Bang Phlat area has 302 condos for sale (FazWaz)
FazWaz median sales price: ~109,303 USD (~3,800,000 THB)
Specific listings: 35 sqm at 2,720,000 THB = 77,714 THB/sqm near MRT Bang Yi Khan (built 2013)
Lumpini Suite Pinklao: average sale USD 2,441/sqm (~85,000 THB/sqm), trend: downtrend
The Tree Charan Bang Phlat: uptrend in rental pricing
NPA units comparison: 1939077 at 69,194 THB/sqm is BELOW market median of 85,123 THB/sqm
Conclusion: NPA units at 69,000-78,500 THB/sqm are BELOW market (good discount)" \
--description "บางพลัด condo sale prices April 2026"

# 2b. บางพลัด - Rental
$INGEST --text "[Area: บางพลัด | Category: rental | Source: DDProperty/Livinginsider/Baania | Date: 2026-04-03]
บางพลัด/บางอ้อ condo rental rates:
Bang Phlat median rent: 13,177 THB/month (Thailand-Property)
Near MRT Bang Phlat: rental starts from 3,000 THB/month (studio/old buildings)
My Condo Pinklao 25 sqm: 8,000 THB/month
MRT Bang Aor area: Studio 28 sqm from 5,500 THB/month (City Home รัชดา-ปิ่นเกล้า)
Hipflat listings: 28 sqm floor 8 at 11,500 THB/month
Near MRT Bang Phlat/Jaran: 1BR typically 8,000-13,000 THB/month
240+ rental listings on DDProperty for Bang Phlat area (high supply)
Key projects: Supalai City Resort Charan 91, The Tree Charan, Modern Condo บางพลัด, Lumpini Suite Pinklao" \
--description "บางพลัด rental rates April 2026"

# 2c. บางพลัด - Area
$INGEST --text "[Area: บางพลัด | Category: area | Source: web_search | Date: 2026-04-03]
บางพลัด/บางอ้อ area intelligence:
MRT stations: บางพลัด (BL04), บางอ้อ (BL03), Bang Yi Khan (BL05) - MRT Blue Line extension
Also near BTS สะพานตากสิน และ Wongwian Yai
Major road: จรัญสนิทวงศ์ (Charansanitwong) - main artery
Shopping: Central Pinklao, Major Pinklao, Makro จรัญฯ, ตั้งฮั่วเส็ง
Hospital: โรงพยาบาล Yanhee (private, well-known), ศิริราช (nearby in บางกอกน้อย)
River view condos popular - ติดแม่น้ำเจ้าพระยา
Expressway: ประจิมรัถยา access nearby
Character: ย่านพักอาศัยดั้งเดิมฝั่งธน ประชากรหนาแน่น มี MRT ใหม่ช่วยพัฒนาทำเล
NPA Asset IDs in area: 1899538, 1915416, 1939077" \
--description "บางพลัด area intelligence"

# 2d. บางพลัด - Flood
$INGEST --text "[Area: บางพลัด | Category: flood | Source: web_search | Date: 2026-04-03]
บางพลัด flood risk assessment:
Flood risk: MEDIUM - พื้นที่ริมแม่น้ำเจ้าพระยา
2011 น้ำท่วม: บางพลัด-จรัญฯ ได้รับผลกระทบ น้ำทะลักคันกั้นน้ำหลายจุด
สี่แยกปิ่นเกล้า น้ำท่วมสูงกว่า 60 ซม. ในเหตุการณ์รุนแรง
GISTDA จัด บางพลัด เป็นพื้นที่ใกล้แม่น้ำเจ้าพระยาที่ต้องระวัง
ถนนจรัญสนิทวงศ์ มีปัญหาน้ำท่วมขังเป็นบางช่วงฝนตกหนัก
ข้อดี: อาคารคอนโดสูงชั้นลอยปลอดภัยกว่าบ้านเดี่ยว/ทาวน์โฮม" \
--description "บางพลัด flood risk"

# 2e. บางพลัด - Projects
$INGEST --text "[Area: บางพลัด | Category: project | Source: web_search/DDProperty | Date: 2026-04-03]
บางพลัด/บางอ้อ major condo projects:
1. Modern Condo Bangplad (Charan 79) - near MRT Bang Phlat 300m, by Modern House Property
2. Supalai City Resort Charan 91 - near MRT Bang O
3. The Tree Charan Bang Phlat - Hipflat: rental uptrend, 1 unit for rent ~USD16/sqm
4. Lumpini Suite Pinklao - 6 for sale, 8 for rent, avg sale USD2,441/sqm, downtrend
5. Chapter One Spark Charan - Pruksa, 1-2BR river view
6. IDEO Charan 70 - river view, high-class
7. De LAPIS Charan 81 - new generation condo, river view concept
8. My Condo Pinklao - budget condo, 25 sqm, rent ~8,000 THB/month
Developer presence: Pruksa, Sansiri (IDEO), Supalai, LPN - major developers active" \
--description "บางพลัด condo projects"

# ============================================================
# DISTRICT 3: ตลิ่งชัน (1 NPA condo - Asset 1965093)
# ============================================================

# 3a. ตลิ่งชัน - Pricing
$INGEST --text "[Area: ตลิ่งชัน | Category: pricing | Source: Hipflat/FazWaz | Date: 2026-04-03]
ตลิ่งชัน condo sale market prices:
Hipflat listing: 32.28 sqm at ลุมพินีเพลส บรมราชชนนี-ปิ่นเกล้า 2,000,000 THB = ~62,000 THB/sqm
Another Hipflat listing: 76,744 THB/sqm for a condo in ตลิ่งชัน
FazWaz: median price per sqm ~USD 1,759 (~61,500 THB/sqm), 7 units for sale
Lumpini Place Borom Ratchachonni-Pinklao: 25 floors, 32 sqm at 2M THB = 62,000 THB/sqm
Market range: 55,000-77,000 THB/sqm depending on project and proximity to MRT
NPA unit 1965093: 25.97 sqm at 1.43M = 55,064 THB/sqm - appears AT or slightly BELOW market low end
Conclusion: NPA price is competitive/cheap for the area, especially if near transit" \
--description "ตลิ่งชัน condo sale prices April 2026"

# 3b. ตลิ่งชัน - Rental
$INGEST --text "[Area: ตลิ่งชัน | Category: rental | Source: DDProperty/ZmyHome/DotProperty | Date: 2026-04-03]
ตลิ่งชัน condo rental rates:
ZmyHome: 16 rental listings in ตลิ่งชัน, rental rate ~285 THB/sqm/month (e.g., 8,000 THB for 28 sqm)
DDProperty: only 2 active rental listings (low rental market activity)
DotProperty: 24 sqm near ตลาดน้ำตลิ่งชัน with BTS access
Estimate: 25-30 sqm units rent for 6,000-8,500 THB/month
Market character: limited condo supply in ตลิ่งชัน proper - more houses/townhouses than condos
Rental demand driven by local residents, not transit commuters (limited BTS/MRT access)" \
--description "ตลิ่งชัน rental rates April 2026"

# 3c. ตลิ่งชัน - Area
$INGEST --text "[Area: ตลิ่งชัน | Category: area | Source: web_search | Date: 2026-04-03]
ตลิ่งชัน area intelligence:
Nearest MRT: บางขุนนนท์ (Blue Line), about 1-2km depending on location
BTS extension planned: บางหว้า-ตลิ่งชัน (future, connecting 3 rail lines)
Major roads: บรมราชชนนี, กาญจนาภิเษก, ถนนสิรินธร
Shopping: Central Pinklao, Major Pinklao, แม็คโคร จรัญฯ, ตั้งฮั่วเส็ง
Nearby: ตลาดน้ำตลิ่งชัน (floating market tourist attraction)
Hospital: ศิริราช (nearby), โรงพยาบาลตลิ่งชัน
Expressway: ทางด่วนประจิมรัถยา ทางขึ้นใกล้บรมราชชนนี
Character: ชานเมืองเก่าแก่ มีทั้งที่อยู่อาศัยและพื้นที่เกษตร ค่อนข้างสงบ
Key projects: Lumpini Place บรมราชชนนี-ปิ่นเกล้า
MRT ท่าพระ interchange: เชื่อม MRT Blue Line หลายสาย ทำเลสำคัญฝั่งธน" \
--description "ตลิ่งชัน area intelligence"

# ============================================================
# DISTRICT 4: บางกอกใหญ่ (1 NPA condo - Asset 1957998)
# ============================================================

# 4a. บางกอกใหญ่ - Pricing
$INGEST --text "[Area: บางกอกใหญ่ | Category: pricing | Source: FazWaz/Hipflat/DDProperty | Date: 2026-04-03]
บางกอกใหญ่ condo sale market prices:
Hipflat: 161 condos for sale, average price USD 92,606 (~3,200,000 THB), avg USD 2,937/sqm (~100,000 THB/sqm)
FazWaz: 238 condos for sale. Library Houze Charan 13: 25 sqm at ~76,000 THB/sqm
Niche MONO Itsaraphap: 29 sqm at ~120,000 THB/sqm (new 2022, near MRT Itsaraphap)
DDProperty listing: 31 sqm near Wat Arun at 3,729,000 = 120,290 THB/sqm (new 2026)
Older/budget condos: ศรีเจริญ area studios from ~30,000-60,000 THB/sqm
Market range WIDE: 30,000-120,000 THB/sqm depending on project age and transit proximity
NPA unit 1957998: 27.76 sqm at 555,000 THB = 19,993 THB/sqm - EXTREMELY CHEAP, ~70-80% below market!
Possible reasons for cheap price: very old building, poor condition, no transit access, title issues, or low-floor undesirable unit" \
--description "บางกอกใหญ่ condo sale prices April 2026"

# 4b. บางกอกใหญ่ - Rental
$INGEST --text "[Area: บางกอกใหญ่ | Category: rental | Source: DDProperty/FazWaz/PropertyScout | Date: 2026-04-03]
บางกอกใหญ่ condo rental rates:
PropertyScout: avg 1BR rent 12,378 THB/month (range 10,000-25,000)
DDProperty: 38 listings in วัดท่าพระ sub-district
IDEO Thaphra Interchange: 28 sqm studio at 13,000 THB/month
Nestoria: rentals from 5,500 THB/month (studio/basic)
FazWaz: 135 condos for rent, 69 properties total
Market segments: budget 5,500-8,000, mid-range 8,000-15,000, nicer/new 15,000-25,000
NPA unit at 555K purchase: if rents at even 5,500/month = ~12% gross yield (very high!)
Nearby projects: IDEO Thaphra Interchange, Niche MONO Itsaraphap, Supalai Lite Thaphra-Wongwian Yai, The Privacy Thaphra" \
--description "บางกอกใหญ่ rental rates April 2026"

# 4c. บางกอกใหญ่ - Area
$INGEST --text "[Area: บางกอกใหญ่ | Category: area | Source: web_search | Date: 2026-04-03]
บางกอกใหญ่ area intelligence:
MRT stations: ท่าพระ (Blue Line interchange - major hub!), อิสรภาพ, จรัญ 13
BTS: วังหลัง (Wang Lang) area nearby
Landmarks: วัดอรุณ (Wat Arun), วังหลัง market (famous food street), ศิริราช โรงพยาบาล
Sub-districts: วัดท่าพระ, วัดอรุณ, บางกอกใหญ่
Shopping: ตลาดวังหลัง (famous market), near Central Pinklao
Hospitals: ศิริราชมหาวิทยาลัยแพทย์ (top-tier teaching hospital)
MRT ท่าพระ is interchange connecting multiple lines - major transit hub on Thonburi side
Area character: mix of old riverside community and new transit-oriented development
Wang Lang/Siriraj area: strong rental demand from medical students, hospital staff
NPA Asset 1957998 needs investigation: at 19,993 THB/sqm something is very unusual" \
--description "บางกอกใหญ่ area intelligence"

# 4d. บางกอกใหญ่ - Flood
$INGEST --text "[Area: บางกอกใหญ่ | Category: flood | Source: web_search/GISTDA | Date: 2026-04-03]
บางกอกใหญ่ flood risk assessment:
GISTDA explicitly lists บางกอกใหญ่ as area near Chao Phraya River that must be monitored
Risk level: MEDIUM-HIGH due to riverside location
พื้นที่ริมแม่น้ำเจ้าพระยา: บางพลัด บางกอกน้อย บางกอกใหญ่ ธนบุรี ต้องระวัง
Wang Lang/วังหลัง area: low-lying riverside community, vulnerable to river flooding
During heavy rain season: drainage issues in old sois near river
MRT ท่าพระ area: newer infrastructure, better drainage
Overall: riverside sub-districts at higher risk, inland areas near MRT moderate risk" \
--description "บางกอกใหญ่ flood risk"

# 4e. บางกอกใหญ่ - Why so cheap investigation
$INGEST --text "[Area: บางกอกใหญ่ | Category: pricing | Source: investigation | Date: 2026-04-03]
NPA Asset 1957998 - บางกอกใหญ่ at 19,993 THB/sqm investigation:
Unit: 27.76 sqm, 555,000 THB (19,993 THB/sqm) - EXTREMELY cheap
Market average for บางกอกใหญ่: ~60,000-100,000 THB/sqm
This is 70-80% BELOW market average!
Possible explanations for such low price:
1. Very old building (pre-2000) with major maintenance issues
2. Title problems (leasehold vs freehold, encumbrances)
3. Building in disrepair / legal disputes / juristic person issues
4. Unit on very low floor (ground/1st) with flood risk
5. Building not registered as condo (อาคารพาณิชย์/หอพัก) - no chanote
6. The asset may be a unit in a very low-end apartment building, not a proper condo
WARNING: At this price point, buyer must investigate title, building condition, and legal status thoroughly
If legitimate: potential gross rental yield could exceed 10-12% (5,500-8,000 rent on 555K purchase)
RECOMMENDATION: Deep dive required before any bid - verify title deed, building registration, and inspect condition" \
--description "บางกอกใหญ่ NPA 1957998 cheap price investigation"

echo "=== All Thonburi/River Edge findings ingested ==="

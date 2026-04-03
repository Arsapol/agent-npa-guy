#!/bin/bash
# Batch ingest all area research findings for 4 central Bangkok districts
# Run from: /Users/arsapolm/.nanobot-npa-guy/workspace/skills/kb/scripts

set -e
cd /Users/arsapolm/.nanobot-npa-guy/workspace/skills/kb/scripts
source /Users/arsapolm/.nanobot-npa-guy/workspace/.env

PYTHON="python ingest_with_meta.py"

echo "========================================="
echo "DISTRICT 1: ดินแดง (Din Daeng)"
echo "========================================="

# --- DIN DAENG: RENTAL ---
echo "--- Din Daeng: Rental ---"
$PYTHON \
  --text "ดินแดง (Din Daeng) condo rental rates April 2026: Budget studios and older condos rent for 3,500-8,000 THB/month (zmyhome, thaihometown). Mid-range near MRT Thailand Cultural Centre: Noble Revolve Ratchada 2 around 12,000-15,000 THB/month. Near MRT Phra Ram 9 specifically: Ideo Rama 9-Asoke rents for 22,000 THB/month for 1BR, Aspire Asoke-Ratchada 25,000 THB/month for 2BR. Life Asoke Rama 9 rents approximately 18,000-22,000 THB/month for 36 sqm 1BR. High-end Belle Grand Rama 9 rents 25,000-40,000 THB. FazWaz estimates rent near Phra Ram 9 MRT at approximately $547/month (about 19,000 THB) with 5% ROI. DDProperty shows 8 listings under 10K THB in Din Daeng area." \
  --summary "Din Daeng rental: 3.5-8K budget, 12-22K mid-range near MRT Rama 9, up to 40K luxury" \
  --category rental \
  --area "ดินแดง" \
  --source "DDProperty+Hipflat+FazWaz" &

wait
echo "--- Din Daeng rental done ---"

# --- DIN DAENG: AREA ---
echo "--- Din Daeng: Area ---"
$PYTHON \
  --text "ดินแดง MRT พระราม 9 area intelligence April 2026: Rama 9 is Bangkok's New CBD (second CBD after Silom-Sathorn). Center is at intersection of Ratchadaphisek Rd x Rama 9 Rd. Surrounded by major office buildings: G Tower, Fortune Tower, AIA Capital Center, The 9th Towers. Shopping: Central Rama 9 (being rebranded to Central GR9), Fortune Town IT mall. Key embassies: Chinese, Indian, Bangladesh nearby. Transit: MRT Phra Ram 9, MRT Thailand Cultural Centre, ARL Makkasan within reach. Educational: University of Thai Chamber of Commerce nearby. Hospitals: Vibhavadi Hospital, Suthisan Hospital. Major development: Central Pattana planning Central GR9 'The Future District' mega mixed-use with 5-year 110B THB investment plan. Sansiri and other developers actively launching new condos in the area. NPA unit 1867367 is only 218m from MRT Phra Ram 9 - exceptional transit proximity." \
  --summary "Din Daeng/Rama 9: New CBD with Central GR9, Fortune Town, G Tower. MRT 218m from NPA unit" \
  --category area \
  --area "ดินแดง" \
  --source "FazWaz+DDProperty+web_search" &

wait
echo "--- Din Daeng area done ---"

# --- DIN DAENG: FLOOD ---
echo "--- Din Daeng: Flood ---"
$PYTHON \
  --text "ดินแดง flood risk assessment April 2026: The Din Daeng triangle (สามเหลี่ยมดินแดง) and Vibhavadi Road are frequent flash flood points. The Din Daeng tunnel has had major flooding incidents: Sept 2024 tunnel flooded after heavy rain, control box was vandalized; Oct 2021 severe flooding forced tunnel closure. Heavy rain in July 2023 caused flooding at 14 major Bangkok road points including Din Daeng area. Bangkok governor Chadchart inspected flood drainage on Prachachuen Rd in Din Daeng area. However, the flooding is primarily surface-level road flooding from sudden heavy rain, NOT major river flooding. Most flooding drains within a few hours. Condos on higher floors are generally unaffected. Risk level: MEDIUM for ground-level flooding, LOW for high-rise condos. The NPA unit at 43.68 sqm is likely above ground level." \
  --summary "Din Daeng flood: MEDIUM risk surface flooding at triangle/tunnel, LOW for high-rise condos" \
  --category flood \
  --area "ดินแดง" \
  --source "PPTV+ThaiRath+Matichon" &

wait
echo "--- Din Daeng flood done ---"

# --- DIN DAENG: PROJECT/DEVELOPMENT ---
echo "--- Din Daeng: Project/Development ---"
$PYTHON \
  --text "พระราม 9 development pipeline April 2026: Major upcoming project is Central GR9 by Central Pattana - a mega mixed-use development concept called 'The Future District' to elevate Rama 9's CBD status. This is part of CPN's 5-year 110 billion THB investment plan announced March 2026. The area already has: Central Rama 9 mall (being upgraded to Central GR9), Fortune Town IT mall, G Tower office, The 9th Towers office, AIA Capital Center. Multiple condo projects near MRT Phra Ram 9 include: Belle Grand Rama 9, Ideo Rama 9-Asoke, The ESSE Asoke, Noble Revolve Ratchada 2, The A Space ID Asoke-Ratchada, Life Asoke Rama 9, Aspire Asoke-Ratchada, Nightbridge Space Rama 9. The area continues to see strong developer interest with new launches. Sansiri actively promoting Rama 9 area condos. FazWaz lists 809 condos for sale and 1,588 for rent near MRT Phra Ram 9. This development trajectory strongly supports property value appreciation in the area." \
  --summary "Rama 9: Central GR9 mega-project, 110B THB investment, 809+ condos for sale, strong appreciation potential" \
  --category project \
  --area "ดินแดง" \
  --source "BrandBuffet+CPN+FazWaz" &

wait
echo "--- Din Daeng project done ---"

echo "========================================="
echo "DISTRICT 2: พญาไท (Phaya Thai)"
echo "========================================="

# --- PHAYA THAI: PRICING ---
echo "--- Phaya Thai: Pricing ---"
$PYTHON \
  --text "พญาไท (Phaya Thai) condo sale prices April 2026: Phaholyothin Place (the likely NPA project, built 2002, 23 floors, 263 units) average sale price is 61,516 THB/sqm per Hipflat - stable trend. DDProperty shows XT Phayathai at 4.69M for 43 sqm (~109K/sqm). Park Origin Phayathai starts at 7.99M. The Complete Ratchaprarop at ~70K/sqm (3.59M for 48 sqm). Phayathai Plaza averages 106,166 THB/sqm. The Seed Phaholyothin averages 80,666 THB/sqm. Older budget condos near BTS Phaya Thai under 3M available. NPA unit 1999047 at 74,317 THB/sqm (2.44M for 32.8 sqm, BTS Sanam Pao 797m) is ABOVE the Phaholyothin Place average of 61.5K/sqm but BELOW Phayathai Plaza at 106K/sqm. The NPA price appears roughly at market average for the Phaholyothin corridor." \
  --summary "Phaya Thai pricing: Phaholyothin Place avg 61.5K/sqm, XT Phayathai ~109K, NPA 74.3K/sqm ~market avg" \
  --category pricing \
  --area "พญาไท" \
  --source "Hipflat+DDProperty+zmyhome" &

wait
echo "--- Phaya Thai pricing done ---"

# --- PHAYA THAI: RENTAL ---
echo "--- Phaya Thai: Rental ---"
$PYTHON \
  --text "พญาไท (Phaya Thai) condo rental rates April 2026: FazWaz reports median rent in Phaya Thai at $733/month (~25,000 THB) with $17/sqm median. Hipflat shows 1BR rentals 19,000-25,000 THB/month. XT Phayathai 34 sqm rents for 20,000 THB/month (588 THB/sqm). Phaholyothin Place 74 sqm 2BR rents for 25,000 THB/month (338 THB/sqm). Budget apartments near Airport Link Phaya Thai start at 3,500-8,000 THB/month. DDProperty has 953 condos for rent in Phaya Thai. The NPA unit 1999047 (32.8 sqm) could potentially rent for 15,000-20,000 THB/month based on area comparables, though distance from BTS Sanam Pao at 797m is a slight negative. Rental yield estimate: 7.4-9.8% gross based on 2.44M purchase price." \
  --summary "Phaya Thai rental: median 25K/mo, 1BR 15-25K, NPA unit could yield 7-10% gross" \
  --category rental \
  --area "พญาไท" \
  --source "FazWaz+Hipflat+Livinginsider" &

wait
echo "--- Phaya Thai rental done ---"

# --- PHAYA THAI: AREA ---
echo "--- Phaya Thai: Area ---"
$PYTHON \
  --text "พญาไท BTS สนามเป้า area intelligence April 2026: BTS Sanam Pao (N4) is on Phaholyothin Road between Ari and Saphan Khwai stations. The area is characterized as a work/office area rather than residential - primarily serves Royal Thai Army headquarters and government offices nearby. Key landmarks: Royal Thai Army headquarters, Phramongkutklao Hospital, Paolo Phaholyothin Hospital, Sripathum University Phaya Thai campus. Shopping: Villa Market Phaholyothin, Big C Saphan Khwai, Plaza Phaholyothin Place. Transit: BTS Sanam Pao + BTS Ari + BTS Phaya Thai + ARL Phaya Thai all within reach. Kasikorn Bank research notes BTS Phaya Thai as a key transit hub connecting BTS Sukhumvit line, ARL Airport Link, and future extensions. The area is well-connected but lacks vibrant residential amenities compared to Ari or Saphan Khwai. NPA unit at 797m from BTS Sanam Pao is a moderate walking distance." \
  --summary "Phaya Thai/Sanam Pao: office area near Royal Thai Army, good transit, limited residential vibe" \
  --category area \
  --area "พญาไท" \
  --source "FazWaz+thinkofliving+Kasikorn" &

wait
echo "--- Phaya Thai area done ---"

# --- PHAYA THAI: FLOOD ---
echo "--- Phaya Thai: Flood ---"
$PYTHON \
  --text "พญาไท flood risk assessment April 2026: Phaya Thai area experienced flash flooding under BTS Phaya Thai station after heavy rain (The Standard news report). The area near Pratunam and Ratchaprarop intersection is a known flood point. DDProperty lists Phaya Thai as one of 8 Bangkok flood risk areas, specifically mentioning Sri Ayutthaya Road in front of Phaya Thai police station and Suntararak Vitayalai school. The flooding is primarily surface-level from heavy rainfall events, not chronic river flooding. During the 2011 major floods, Phaya Thai was in the rain measurement zone receiving 80mm rainfall. Bangkok drainage department lists Phaya Thai as a monitored district. Overall risk: LOW-MEDIUM, primarily flash flooding during intense rainfall that typically drains within hours." \
  --summary "Phaya Thai flood: LOW-MEDIUM risk, flash floods at Sri Ayutthaya Rd, drains within hours" \
  --category flood \
  --area "พญาไท" \
  --source "TheStandard+DDProperty+BKK_drainage" &

wait
echo "--- Phaya Thai flood done ---"

echo "========================================="
echo "DISTRICT 3: ดุสิต (Dusit)"
echo "========================================="

# --- DUSIT: PRICING ---
echo "--- Dusit: Pricing ---"
$PYTHON \
  --text "ดุสิต (Dusit) condo sale prices April 2026: Dusit is Bangkok's royal district with very limited condo development. Hipflat shows average condo sale price in Dusit at approximately $538,712 (~18.6M THB) per unit but this is skewed by luxury riverside properties like Wan Vayla Na Chaophraya. Ordinary condos: Dusit Condominium on Phra Ram 5 Rd near MRT Sri Ayutthaya. Baan Samsen condo studio 26 sqm at 2.8M (~107K/sqm). Dusit Central Park Residences (luxury, on Rama 4) starts at 24.5M for 65 sqm (~373K/sqm) - this is ultra-luxury. Market Place Dusit condos start at 1.89M. NPA unit 1900347 at 61,250 THB/sqm (1.96M for 32 sqm) appears COMPETITIVE for the Dusit area, especially if it's near government offices or Sri Ayutthaya Road. Limited supply in Dusit supports pricing." \
  --summary "Dusit pricing: limited supply, budget condos 1.89-2.8M, luxury 24.5M+, NPA 61.3K/sqm competitive" \
  --category pricing \
  --area "ดุสิต" \
  --source "Hipflat+DDProperty+FazWaz" &

wait
echo "--- Dusit pricing done ---"

# --- DUSIT: RENTAL ---
echo "--- Dusit: Rental ---"
$PYTHON \
  --text "ดุสิต (Dusit) condo rental rates April 2026: Very limited rental market in Dusit due to limited condo supply. PropertyHub shows 60+ listings for rent in Dusit. Zmyhome shows only 9 rental listings in the sub-district. DDProperty has limited listings. Dusit Avenue near Vajira Hospital has some rental units. Typical rental rates for budget condos: approximately 8,000-15,000 THB/month for 26-32 sqm studio/1BR. The area caters primarily to government workers, hospital staff, and those who value proximity to the royal district. NPA unit 1900347 (32 sqm at 1.96M) could potentially rent for 8,000-12,000 THB/month. Estimated gross yield: 4.9-7.3%." \
  --summary "Dusit rental: limited market, 8-15K/mo for studio/1BR, yield 5-7%" \
  --category rental \
  --area "ดุสิต" \
  --source "PropertyHub+zmyhome+DDProperty" &

wait
echo "--- Dusit rental done ---"

# --- DUSIT: AREA ---
echo "--- Dusit: Area ---"
$PYTHON \
  --text "ดุสิต (Dusit) area intelligence April 2026: Dusit is Bangkok's royal district, home to Dusit Palace (พระราชวังดุสิต), Vimanmek Mansion, and several royal residences. The district is characterized by government offices, military installations, and cultural institutions. Key landmarks: Ananta Samakhom Throne Hall, Parliament (old), Royal Thai Army headquarters, Government House nearby, Vajira Hospital, Siriraj Hospital (across river). Education: Suan Dusit Rajabhat University, Rajini School. Shopping: limited - mostly local markets, Macro Samsen. Transit: MRT Sri Ayutthaya is the closest MRT, otherwise rely on buses and river transport. The area has very strict development regulations due to royal presence - height limits, limited commercial development. This creates scarcity value for any existing condos. However, it also limits appreciation potential and rental demand. The area is quiet, green, and prestigious but lacks modern urban amenities and nightlife." \
  --summary "Dusit: royal district with limited development, strict zoning, scarcity value, quiet and prestigious" \
  --category area \
  --area "ดุสิต" \
  --source "Wikipedia+DDProperty+FazWaz" &

wait
echo "--- Dusit area done ---"

# --- DUSIT: FLOOD ---
echo "--- Dusit: Flood ---"
$PYTHON \
  --text "ดุสิต flood risk assessment April 2026: Dusit has multiple communities listed in Bangkok flood risk warnings. Specifically: Soi See Kham (Samsen Soi 19), Ratchaphat Thip Rung Chai community (near Krung Thon bridge), Soi Mitakham (Samsen Soi 13), and Thewarat Kunchorn community. These are mostly low-lying areas near the Chao Phraya River and khlongs. During 2011 major floods, Dusit was affected but not as severely as riverside districts. In 2022 heavy rain events, Dusit was listed among monitored districts but flooding was moderate. The Dusit Poll (Suan Dusit University) surveyed Bangkok residents and found majority concerned about flooding. For condos: those on higher floors and away from Samsen Road khlong area are at lower risk. Overall: LOW-MEDIUM flood risk, with riverside communities being the most vulnerable." \
  --summary "Dusit flood: LOW-MEDIUM risk, 4 vulnerable communities near river/khlongs, condos safer" \
  --category flood \
  --area "ดุสิต" \
  --source "ThaiPBS+TrueID+Dusit_Poll" &

wait
echo "--- Dusit flood done ---"

echo "========================================="
echo "DISTRICT 4: บางกะปิ (Bang Kapi)"
echo "========================================="

# --- BANG KAPI: PRICING ---
echo "--- Bang Kapi: Pricing ---"
$PYTHON \
  --text "บางกะปิ (Bang Kapi) condo sale prices April 2026: Hipflat shows average condo sale price in Bang Kapi at approximately $73,628-78,679 (~2.5-2.7M THB) with price per sqm around $2,194-2,312 (~75,000-80,000 THB/sqm). This is 49.3% LOWER than Bangkok median. DDProperty has condos in Bang Kapi from under 1M (65 listings). Budget options: The One Plus, Condo 101, Sathorn Happy Land at 64 sqm for under 2M. Newer mid-range: Happy Condo Ladprao 101 at 1.4M for 28.64 sqm (~49K/sqm). Bang Kapi Condotown is one of the oldest and cheapest developments. The NPA unit 1879659 at only 16,973 THB/sqm (480K for 28.28 sqm) is EXTREMELY cheap - approximately 78% BELOW the Bang Kapi average of ~75-80K/sqm. This suggests either: (1) very old building, (2) poor condition, (3) legal issues, or (4) location far from transit. At this price point, even basic renovation may not make financial sense - need to verify building condition and legal status before bidding." \
  --summary "Bang Kapi pricing: avg 75-80K/sqm, NPA at 17K/sqm = 78% below market! SUSPICIOUS - verify condition" \
  --category pricing \
  --area "บางกะปิ" \
  --source "Hipflat+DDProperty+FynProperty" &

wait
echo "--- Bang Kapi pricing done ---"

# --- BANG KAPI: RENTAL ---
echo "--- Bang Kapi: Rental ---"
$PYTHON \
  --text "บางกะปิ (Bang Kapi) condo rental rates April 2026: DDProperty shows 487 rental listings in Bang Kapi. PropertyHub shows 2,490+ listings for rent near The Mall Bang Kapi and 3,610+ near the mall overall. Budget rentals: 2,500-6,000 THB/month for basic studios (thaihometown, baania). Mid-range: Happy Condo Ladprao 101 at 10,000-17,000 THB/month for 35-63 sqm. Median rent near The Mall Bang Kapi area is approximately 8,000 THB/month per zmyhome. Hipflat data shows average rent in Bang Kapi at approximately $402/month (~14,000 THB) with $12/sqm average. The area has strong rental demand from Ramkhamhaeng University students and workers at The Mall Bang Kapi, Big C, and nearby offices. NPA unit 1879659 (28.28 sqm at 480K) could potentially rent for 4,000-6,000 THB/month (student rental). Estimated gross yield: 10-15% IF rentable, but condition is questionable at 16,973 THB/sqm." \
  --summary "Bang Kapi rental: strong student demand, 4-8K budget, 10-17K mid, NPA could yield 10-15% if habitable" \
  --category rental \
  --area "บางกะปิ" \
  --source "DDProperty+PropertyHub+Hipflat+zmyhome" &

wait
echo "--- Bang Kapi rental done ---"

# --- BANG KAPI: AREA ---
echo "--- Bang Kapi: Area ---"
$PYTHON \
  --text "บางกะปิ (Bang Kapi) area intelligence April 2026: Bang Kapi is a large district in eastern Bangkok, home to Ramkhamhaeng University (one of Thailand's largest public universities with massive student population). The area is centered on Ramkhamhaeng Road and Ladprao Road. Key landmarks: The Mall Bang Kapi (major shopping center), The Mall Ramkhamhaeng 3, Major Hollywood Ramkhamhaeng, Tesco Lotus Bang Kapi. Education: Ramkhamhaeng University (Hua Mak sub-district), Institute of Physical Education. Transit: NO BTS/MRT currently in Bang Kapi proper. Nearest rail is ARL Ramkhamhaeng station on the Airport Rail Link. Future: Orange Line MRT (planned to pass through Bang Kapi area connecting Thailand Cultural Centre to Min Buri) but timeline uncertain. The area is known for student housing, affordable living, and traffic congestion on Ramkhamhaemonkut/Ramkhamhaeng roads. Sky Walk pedestrian bridge under construction to improve transit connections. NPA unit 1879659 likely targets the student/budget rental market." \
  --summary "Bang Kapi: Ramkhamhaeng University area, student housing demand, NO BTS/MRT, Orange Line planned" \
  --category area \
  --area "บางกะปิ" \
  --source "FazWaz+home.co.th+Pantip" &

wait
echo "--- Bang Kapi area done ---"

# --- BANG KAPI: FLOOD ---
echo "--- Bang Kapi: Flood ---"
$PYTHON \
  --text "บางกะปิ flood risk assessment April 2026: Bang Kapi has a CHRONIC flooding problem that has persisted for 30+ years. Bangkok Governor Chadchart visited Bang Kapi twice specifically to address flooding, declaring 'this year Bang Kapi won't flood' but the problem persists. Key issues: Khlong Saen Saeb overflow flooding Sri Nakharin Road in Bang Kapi (ThaiPBS report). 8 communities in Hua Mak sub-district warned about flood risk (Manager newspaper). Ladprao Road flooding makes cars nearly undrivable during heavy rain (JS100 traffic reports). Happy Land area (Soi 1-2) particularly vulnerable. Cause: inadequate drainage infrastructure, Khlong Saen Saeb overflow, and urban development blocking natural waterways. BMA has been expanding drainage pipes in Bang Kapi-Wang Thonglang area. Overall flood risk: HIGH for ground-level properties, MEDIUM for upper floors. The NPA unit's extremely low price (16,973 THB/sqm) may be partly explained by flood risk. NEED TO VERIFY which floor the unit is on." \
  --summary "Bang Kapi flood: HIGH risk, chronic 30yr flooding problem, Khlong Saen Saeb overflow, may explain low price" \
  --category flood \
  --area "บางกะปิ" \
  --source "BangkokBizNews+ThaiPBS+Manager+JS100" &

wait
echo "--- Bang Kapi flood done ---"

# --- BANG KAPI: PROJECT (investigating low price) ---
echo "--- Bang Kapi: Project/Investigation ---"
$PYTHON \
  --text "บางกะปิ NPA unit 1879659 deep analysis - why only 16,973 THB/sqm (480K for 28.28 sqm)? This price is 78% below Bang Kapi average of 75-80K THB/sqm. Possible explanations: (1) BUILDING AGE - Bang Kapi Condotown and similar 30+ year old buildings trade at massive discounts. (2) FLOOD RISK - Bang Kapi has chronic 30-year flooding problems, ground-floor units especially penalized. (3) BUILDING CONDITION - NPA properties often have deferred maintenance, squatters, or damage. (4) LEGAL ISSUES - possible title encumbrances, outstanding debts, or juristic person problems. (5) NO TRANSIT - Bang Kapi has no BTS/MRT, reducing property values vs transit-connected areas. (6) DISTRESSED - LED auction properties sell at deep discounts anyway. RED FLAGS: At 480K total price, this is below even the cheapest new condos in Bangkok. Even if rentable at 4-5K/month, the gross yield would be 10-12.5% which is attractive BUT only if the unit is actually habitable. MUST physically inspect before bidding. Must also check: outstanding common area fees, building structural integrity, legal encumbrances, squatter status." \
  --summary "Bang Kapi NPA 480K investigation: 78% below market, possible flood/age/legal issues, MUST inspect" \
  --category project \
  --area "บางกะปิ" \
  --source "LED+Hipflat+web_analysis" &

wait
echo "--- Bang Kapi project done ---"

echo "========================================="
echo "ALL INGESTIONS COMPLETE!"
echo "========================================="

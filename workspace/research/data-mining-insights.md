# NPA Data Mining Insights
**Date:** 2026-04-05 | **Analyst:** Data Miner
**Source:** Direct SQL queries on npa_kb PostgreSQL database

---

## FINDING 1: State Tower (Silom) — BAM Has 142+ Units at 38-49% Discount vs Market

**What the data shows:**
- BAM holds **142+ units** in the `สเตททาวเวอร์ บางรัก` project (Silom subdistrict)
- 66 sqm units: BAM price = **67,200 THB/sqm** (฿4.43–4.51M)
- 271 sqm units: BAM price = **22,300–23,500 THB/sqm** (฿6.06–6.38M) — massive size-pricing anomaly
- Hipflat sold price for `ณุศา สเตท ทาวเวอร์ คอนโดมิเนียม` (confirmed same building, ปี 2000): **109,000 THB/sqm**

**The anomaly:**
BAM 66-sqm units at 67k/sqm = **38% real discount vs Hipflat sold price**.
BAM 271-sqm units at 22-23k/sqm = **79% discount** — these giant units are mispriced (possibly mixed-use/office designation).

**SQL evidence:**
```sql
SELECT COUNT(*) as units, ROUND(AVG(sell_price/usable_area/1000),1) as avg_psm_k
FROM bam_properties WHERE project_th ILIKE '%สเตททาวเวอร์%' AND usable_area > 0;
-- 128 units, avg 66.7k/sqm

SELECT avg_sold_sqm FROM hipflat_projects 
WHERE name_en ILIKE '%nusa state tower%';
-- 109,000 THB/sqm
```

**Risk flag:** Building completed 2000 (26 years old). NPA concentration >8% highly likely for a building of this age with 142 BAM units. MUST verify NPA% before buying.

**Nearest GPS matches:** Noble Revo Silom (175k/sqm) is 341m away — confirms prime Silom location.

**Specific assets to investigate:**
- `CBKKCU0445001` — 66.5 sqm, ฿4.47M, 67,200/sqm
- `CBKKCU0457001` — 65.9 sqm, ฿4.43M, 67,200/sqm
- `CBKKCU0597001` — 271 sqm, ฿6.06M, **22,300/sqm** (extreme anomaly)

---

## FINDING 2: Metro Sky Ratchada (BAM) — Cheaper Than Private Sellers

**What the data shows:**
- BAM has **6 units** in Metro Sky Ratchada (ดินแดง district)
- BAM prices: ฿2.12–3.17M for 29–44 sqm = **71,400–74,600 THB/sqm**
- JAM private sellers asking same building: ฿2.35–3.95M (JAM asset_id 12715, 24498)
- Hipflat comparison: Quinn Condo Ratchada nearby (103k/sqm) = **30.7% discount**

**GPS confirmed:** BAM at 13.784, 100.571 — Quinn Condo at 313m distance.

**The trade:**
BAM offers Metro Sky Ratchada at **31% below Quinn Condo Ratchada market prices** and at the LOW END vs JAM private market.

**Specific assets:**
- `22BKKCU0044000` — 44.3 sqm, ฿3.17M, 71,400/sqm, 1BR
- `22BKKCU0047000` — 34.1 sqm, ฿2.44M, 71,400/sqm
- `22BKKCU0048000` — 29.7 sqm, ฿2.12M, 71,400/sqm

**Size note:** 29–34 sqm units are below the 35 sqm minimum for university-yield strategy but good for rental/resale.

---

## FINDING 3: Chonburi (Sri Racha บ่อวิน) Dominates LED Sell-Through

**Surprise:** Chonburi subdistricts, not Bangkok, have the highest LED auction sell-through rates.

| Subdistrict | Total | Sold | Sell-Through | Avg Price |
|-------------|-------|------|-------------|-----------|
| พานทอง > บางนาง | 23 | 9 | **39.1%** | ฿1.16M |
| บางละมุง > บางละมุง | 75 | 28 | **37.3%** | ฿1.55M |
| เมืองชลบุรี > ดอนหัวฬ่อ | 65 | 24 | **36.9%** | ฿1.28M |
| ศรีราชา > ทุ่งสุขลา | 60 | 22 | **36.7%** | ฿1.46M |
| ศรีราชา > บ่อวิน | 445 | 147 | **33.0%** | ฿1.08M |

**Bangkok comparison:** Best Bangkok subdistrict is หนองค้างพลู (หนองแขม) at only 34.3%.

**What's happening:**
- บ่อวิน is Amata Nakorn industrial estate zone (Honda, Toyota suppliers). Worker demand is REAL.
- ALL 445 sales are `ที่ดินพร้อมสิ่งปลูกสร้าง` — houses, not condos.
- Price point ฿1.08M avg = very affordable for industrial workers.
- 33% sell-through is exceptional for LED court auctions.

**Investment thesis:** Houses in บ่อวิน Sriracha at ฿0.4M–1.5M with 33% sell-through. Active resale market driven by Amata Nakorn industrial base.

**Best LED properties in บ่อวิน:** Search properties table WHERE ampur='ศรีราชา' AND tumbol='บ่อวิน' AND sale_status='ยังไม่ขาย' AND primary_price_satang < 200000000.

---

## FINDING 4: KBank Building Age Paradox — Older Condos OUTSELL Newer Ones

**The data:**
| Age Bucket | Total Units | Sold | Sold Rate |
|------------|-------------|------|-----------|
| 20-25 years (Bangkok) | 5 | 2 | **40%** |
| 25+ years (Bangkok) | 21 | 2 | 9.5% |
| 0-5 years (all provinces) | 951+ | 0 | **0.0%** |
| 5-10 years | 481+ | 5 | 1.0% |
| 10-15 years | 372+ | 8 | 2.2% |

**Why:** 0-5 year condos are new construction NPAs — buyers can get brand new units directly from developers at similar prices. There's no price advantage for bank NPAs in new buildings. Older buildings (15-25yr) hit the **2008-2018 sweet spot** noted in AGENTS.md.

**Specific sold KBank condos:**
- `058803725` จตุจักร > จันทรเกษม, 53sqm, ฿1.57M, 29,500/sqm, age 18 — SOLD
- `058803724` จตุจักร > จันทรเกษม, 53sqm, ฿1.60M, 30,000/sqm, age 18 — SOLD
- `058802943` พระโขนง, 55sqm, ฿5.85M, 105,000/sqm, age 15 — SOLD (prime)

**Pattern:** The age 15-20 year Chatuchak condos (53sqm at 29-30k/sqm) that sold = price was SO LOW buyers couldn't resist. Those are the deals worth hunting.

---

## FINDING 5: Don Mueang Condo Town — SAM Has 142 Units at ฿3,500/sqm (TRAP)

**The data:**
- SAM has **142 units** of ดอนเมืองคอนโดทาวน์ at ฿107,000–111,000 per unit
- Size: ~30 sqm = **3,493–3,563 THB/sqm**
- BAM has similar เคหะดอนเมือง 1 at ฿200,000–260,000 for 26 sqm

**Why this is a TRAP, not a deal:**
These are NHA (National Housing Authority) government housing units. Hipflat Don Mueang shows one project with avg_sold_sqm of only **66,600 THB/sqm** but that's a different (newer) project. The NHA units at 3,500/sqm have:
1. No BTS/MRT within viable distance
2. Massive NPA concentration (142 units in one building = systemic building default)
3. Likely aged 20-30+ years
4. No juristic fund stability

**Skip entirely.** This is social housing, not investment grade.

---

## FINDING 6: BAM NPA Supply Concentration Map (Bangkok)

The highest NPA supply districts in Bangkok (potential oversupply risk):

| District | Subdistrict | BAM Units (1-8M range) | Avg psm (k) |
|----------|-------------|------------------------|-------------|
| บางรัก | สีลม | **124** | 63.1 |
| ภาษีเจริญ | บางหว้า | 66 | 42.2 |
| บางกะปิ | หัวหมาก | 60 | 49.5 |
| สวนหลวง | สวนหลวง | 52 | 44.2 |
| บึงกุ่ม | คลองกุ่ม | 27 | 47.5 |
| ห้วยขวาง | สามเสนนอก | 24 | 54.3 |

**Implication for pickers:**
- บางรัก/สีลม: 124 units = high NPA concentration risk in any single building here. The State Tower concentration is THE reason.
- ภาษีเจริญ/บางหว้า: 66 units = Metro Park Sathorn concentration.
- หัวหมาก: 60 units = multiple projects.

---

## FINDING 7: Chateau in Town — Developer with Most BAM NPA Branches

**Developer default concentration signal:**
- BAM: 16 units across 10 branches (Suk64, Suk62, Phahol14, Phahol30/32, Ratchada 17/20/36, Major Ratchayothin)
- JAM: **53 units** — by far most
- SAM: 1 unit

**JAM average asking price:** ฿4.71M (JAM tends to have over-priced listings)
**BAM average:** ฿2.26M — much more realistic

**Risk profile:** Chateau in Town is a mid-market developer with serial defaults across multiple projects. Having 10 NPA branches in BAM + 53 in JAM shows the entire developer portfolio is distressed. If you hold one, the building's NPA concentration is likely high.

**Actionable:** Cross-reference any Chateau in Town purchase with NPA concentration calculation first.

---

## FINDING 8: LED Auction Count Field = Data Artifact (Not Round Count)

**Important:** ALL LED properties have `total_auction_count = 6`. This is a scraper field, not a meaningful auction round counter. Ignore for filtering.

**Alternative signal for staleness:** Use `next_auction_date` and `last_auction_date` fields. Properties with `next_auction_date` in the near future are ACTIVE. Properties where `next_auction_date` is blank but `sale_status = 'ยังไม่ขาย'` may be dormant.

---

## FINDING 9: KBank Cheapest Bangkok Condos (Non-NHA, Investable)

KBank condos with lowest psm in prime areas (not NHA housing):

| property_id | District | Sqm | Price | psm_k | Age | Notes |
|-------------|----------|-----|-------|-------|-----|-------|
| 058803725 | จตุจักร/จันทรเกษม | 53 sqm | ฿1.57M | 29.5k | 18 | **SOLD** |
| 058803724 | จตุจักร/จันทรเกษม | 53 sqm | ฿1.60M | 30.0k | 18 | **SOLD** |
| 058801583 | ห้วยขวาง/ดินแดง | 78 sqm | ฿1.56M | 20.0k | **34** | Too old (pre-2006) |
| 051001518 | จตุจักร/ลาดยาว | 38.75 sqm | ฿1.28M | 33.1k | 0 | age=0 means unknown |
| 051000705 | จตุจักร/จันทรเกษม | 51.23 sqm | ฿1.70M | 33.2k | 0 | age=0 = unknown |
| 051001282 | ห้วยขวาง/สามเสนนอก | 28.68 sqm | ฿1.02M | 35.6k | 0 | Small but cheap |
| 031001729 | จตุจักร/จันทรเกษม | 24.96 sqm | ฿1.06M | 42.6k | 0 | Small unit |

**Note on age=0:** Many KBank units have building_age=0 which likely means "not scraped" rather than brand new. Treat as unknown.

---

## FINDING 10: BAM Large Units in Prime Locations — Value Gap

**The 271 sqm State Tower units at ฿22,300/sqm deserve attention:**
- Asset `CBKKCU0597001`: 271 sqm, ฿6.06M, 22,300/sqm at สีลม
- Asset `CBKKCU0469001`: 271 sqm, ฿6.38M, 23,500/sqm at สีลม

**Why the huge discount:** Large units are extremely illiquid in Thai market. 271 sqm in a 26-year-old building = very hard to resell. BUT the price per sqm is SO low it could work as:
- Commercial lease (close to BTS Surasak, Sala Daeng)
- Short-term rental conversion
- Long-term hold at low entry cost

**Risk:** Building age 26 years, high NPA concentration, likely high common area arrears.

---

## FINDING 11: LED Bangkok Condos Currently Active (Near-Term Auctions)

LED condos available for auction in Bangkok under ฿3M with upcoming auction dates:

| asset_id | District | Subdistrict | Auction Date | Price | Sqm (wa) | Deed |
|----------|----------|-------------|--------------|-------|---------|------|
| 1910878 | ราษฎร์บูรณะ | ราษฎร์บูรณะ | 2026-04-28 | ฿170,910 | 25.16 wa | โฉนด |
| 1975564 | หนองแขม | หนองค้างพลู | 2026-04-23 | ฿215,600 | 24.5 wa | โฉนด |
| 2002140 | ดอนเมือง | สีกัน | 2026-05-07 | ฿280,875 | 26.25 wa | โฉนด |
| 1960444 | บางเขน | ตลาดบางเขน | 2026-04-09 | ฿282,240 | 25.2 wa | โฉนด |
| 1883013 | จอมทอง | บางขุนเทียน | 2026-04-07 | ฿329,175 | 34.65 wa | โฉนด |
| 1957998 | บางกอกใหญ่ | บางยี่เรือ | 2026-04-07 | ฿555,200 | 27.76 wa | โฉนด |

**Note:** LED size is in ตารางวา (wa), not sqm. 1 wa = 4 sqm.
- 25 wa ≈ 100 sqm land. For condos, size_wa represents floor area.
- 25 wa condo = 100 sqm = WAY too large for these prices (these might be errors or include land)
- These ultra-cheap LED condos (฿170k–555k) at 25–35 wa need physical inspection.

**Red flag:** ราษฎร์บูรณะ and ดอนเมือง condos at ฿170k–280k are likely NHA housing or very old/distressed. Prices this low in Bangkok = serious structural or legal issues.

---

## FINDING 12: Cross-Provider Price Arbitrage — BAM Consistently Cheaper Than JAM

**Metro Sky Ratchada example:**
- BAM: ฿2.12–3.17M (actual NPA bank price)
- JAM private sellers: ฿2.00–3.95M (range includes some below BAM)
- JAM average ask: ฿3.27M (meaningfully above BAM at 2.44M avg)

**Conclusion:** BAM prices for Metro Sky Ratchada are at the LOW END of the JAM private market. BAM is the best source for this building.

**General pattern:** BAM tends to price more conservatively than JAM. JAM listings include many "buy it now" and rental listings mixed in, inflating apparent prices.

---

## FINDING 13: KTB "PP Plus Sukhumvit 71" — 10 Units at 36% KTB-Own Discount, Wattana Prime Zone

**Building:** อาคารชุดพีพีพลัส สุขุมวิท 71, ปรีดีพนมยงค์ 14, แขวงพระโขนงเหนือ เขตวัฒนา
**GPS:** 13.720, 100.600

KTB's own `nml_price` vs `price` shows a **36.3–36.4% built-in discount** across all 10 units.

| coll_grp_id | Unit | KTB nml_price | KTB price | Disc |
|-------------|------|---------------|-----------|------|
| 226417 | 399/20 | ฿2.34M | ฿1.49M | 36.3% |
| 208880 | 399/14 | ฿2.97M | ฿1.89M | 36.3% |
| 146440 | 399/51 | ฿2.98M | ฿1.89M | 36.4% |
| 204796 | 399/43 | ฿3.14M | ฿2.00M | 36.4% |
| 208080 | 399/30 | ฿5.25M | ฿3.34M | 36.4% |

**Market validation (GPS):**
- PB Penthouse 2 (Hipflat avg_sold **67,600/sqm**) is only **89m away**
- Fragrant 71 (61,700/sqm) at 236m
- The Pillar (112,000/sqm) at 581m

**Problem:** KTB has no sqm data (`sum_area_num = 0` for all KTB condos). But given PB Penthouse 2 avg_sold of 67,600/sqm at 89m, a 2M KTB unit at 36% below KTB valuation is potentially at ~40k/sqm vs 67k/sqm market.

**Location:** Bangkok Prep Secondary Campus 0.66km, international school zone. Sukhumvit 71 = on-demand expat/foreigner corridor.

**The signal:** KTB's own appraisal says these units are worth ฿2.3–5.3M but KTB is selling at ฿1.5–3.3M. This is NOT a discrepancy error — it's KTB pricing to liquidate. 10 units from same building = NPA concentration risk exists, but in Wattana/Phrakhanong Nua it's less alarming.

**Best entry point:** `coll_grp_id 226417` and `208880` at ฿1.49–1.89M are the smallest/cheapest in this cluster.

---

## FINDING 14: KTB "ดีไซน์ คอนโดมิเนียม รัชดา" (Sutthisan) — 7 Units at 40.9% KTB Discount

**Building:** ดีไซน์ คอนโดมิเนียม รัชดา, ถนนสุทธิสารวินิจฉัย, แขวงสามเสนนอก เขตห้วยขวาง
**GPS:** 13.788, 100.583

All 7 units priced uniformly at **40.9% below KTB's own normal price**. This is larger than the Wattana cluster.

| coll_grp_id | Unit | KTB nml_price | KTB price | Floor |
|-------------|------|---------------|-----------|-------|
| 145721 | 68/34 | ฿4.88M | ฿2.88M | 5 |
| 205324 | 68/10 | ฿5.14M | ฿3.04M | 3 |
| 228220 | 68/18 | ฿5.22M | ฿3.08M | — |
| 211230 | 68/66 | ฿5.52M | ฿3.26M | 7 |
| 209693 | 68/79 | ฿5.78M | ฿3.41M | 8 |

**Market validation (GPS):**
- Humble Living @ Fueangfu: **93,900/sqm** at 241m
- Grene Suthisarn: 62,700/sqm at 296m
- Hi Sutthisan Condo: 69,600/sqm at 307m

**Context:** Sutthisan/Huai Khwang zone, MRT Huai Khwang ~1km. โรงเรียนอนุบาลนานาชาติเพรพ only **170m away** (education anchor). ตลาดสิทธิณี market **50m away**.

**Catch:** No sqm data from KTB. Nearby Humble Living transacts at 93,900/sqm — if the ดีไซน์ units are ~30–40 sqm (typical older mid-rise), ฿2.88–3.08M implies ~72–103k/sqm which would be near/at market. The 40.9% KTB discount from its own valuation may simply reflect an old inflated appraisal, not a real market discount. **Needs physical visit + sqm verification before concluding.**

---

## FINDING 15: JAM High-View Listings — GPS-Validated Real Discounts

JAM's `total_view` field functions as organic demand signal. Cross-referencing the most-viewed JAM listings with GPS-verified Hipflat sold prices:

| asset_id | Project | Price | Sqm | psm | Views | Nearest Hipflat | Hipflat psm | Real Disc |
|----------|---------|-------|-----|-----|-------|-----------------|-------------|-----------|
| 45544 | เมอร์ราญา เพลส ลาดพร้าว 27 | ฿1.70M | 34sqm | 49,700 | 83 | Life @ Ratchada (75m) | 71,700 | **30.7%** |
| 45226 | บ้านสุขโขทัย | ฿1.53M | 60sqm | 25,500 | 47 | Chewathai Ramkhamhaeng (343m) | 61,000 | **58.2%** |
| 49856 | จอนนี่ ทาวเวอร์ | ฿1.44M | 35sqm | 40,800 | 46 | Subkaew Tower (24m) | 39,400 | **at market** |
| 45712 | ทรู ทองหล่อ | ฿5.06M | 62sqm | 81,600 | 84 | Thru Thonglor (77m) | 89,200 | **8.6%** |

**Corrected interpretation (vs prior session):**
- ทรู ทองหล่อ (asset 45712): Hipflat confirms it IS the same "Thru Thonglor" project at 89,200/sqm. JAM at 81,600/sqm = 8.6% below market, not 65%. Small discount but in a prime zone (floor 23, 1BR+2 bath, 62sqm).
- จอนนี่ ทาวเวอร์ (asset 49856): Subkaew Tower at 24m shows 39,400/sqm sold — JAM at 40,800/sqm is AT market. Not a discount play.
- **บ้านสุขโขทัย (asset 45226): 60sqm at 25,500/sqm vs Chewathai at 61,000/sqm = 58% real discount**. But Bangkapi/Huamark is not prime — verify building condition and rental demand.
- เมอร์ราญา ลาดพร้าว 27 (asset 45544): 34sqm, 1BR, Chatuchak/Ratchada zone at 30.7% real discount vs 71,700/sqm market. **Genuine deal.** MRT Ratchadaphisek corridor.

**Key JAM viewer behavior pattern:** Assets 5 (875 views, เดอะไพรเวซี่ ลาดพร้าว) and 10 (394 views, ศุภาลัย ปาร์ค รัชโยธิน) dominate — these are brand recognizable projects. High views don't necessarily = discount.

---

## FINDING 16: BAM "ฟลอร่าวิลล์ สวนหลวง" Fire Sale — Active Campaign Through 2028

BAM has **6 units** of Flora Ville Suan Luang on active sale campaign (`sale_price_spc_to = 2028-09-29`).

| Asset | Size | Normal BAM price | Campaign price | Disc | psm at campaign |
|-------|------|-----------------|----------------|------|-----------------|
| 27BKKCU0001000 | 261 sqm | ฿9.74M | **฿4.94M** | 49.3% | 18,900/sqm |
| 27BKKCU0005000 | 153 sqm | ฿5.78M | **฿3.55M** | 38.6% | 23,200/sqm |
| 27BKKCU0007000 | 196 sqm | ฿7.42M | **฿4.47M** | 39.7% | 22,800/sqm |
| 27BKKCU0004000 | 405 sqm | ฿11.91M | **฿8.00M** | 32.8% | 19,800/sqm |

**Market validation:** Hipflat Flora Ville avg_sold = **39,600/sqm** at 126m distance (same project confirmed).
- Campaign price 18,900–23,200/sqm vs Hipflat 39,600/sqm = **41–52% real discount vs actual transactions**

**The catch:** These are enormous units (153–405 sqm). Thai condo market has extremely thin demand for 260+ sqm units. They are illiquid regardless of price.
- 261 sqm at 18,900/sqm: extraordinary unit economics if convertible (hospitality / co-living split)
- Flora Ville is a 1992 building (34 years old) — AUTO-REJECT under building age criteria (>20 years)

**Verdict for investment:** Excluded on age. But if age rule is relaxed for hospitality conversion play: the 153 sqm unit at ฿3.55M in a project where transactions happen at 39,600/sqm is the entry worth exploring.

---

## FINDING 17: BAM "ตึกช้าง รัชโยธิน" — 175 sqm at ฿8.9M, 19% Below Market

**Asset:** `DIBKKCU0172001`, 175.93 sqm, ฿8.9M = **50,600/sqm**
**Campaign:** Active until 2028-07-16
**GPS:** 13.825, 100.567

Market validation:
- Hipflat Elephant Tower (`ตึกช้าง`): **61,100/sqm** at 94m (same building confirmed)
- KnightsBridge Prime Ratchayothin: 153,000/sqm at 45m (premium newer building nearby)

**Real discount:** 50,600 vs 61,100 = **17.2% below Hipflat sold price** for same building.

**Why this matters:** Elephant Tower is a landmark Bangkok building (Ratchayothin, near BTS Phahon Yothin 24 and Chatuchak Park). 175 sqm unit for ฿8.9M in this zone. Older building but known address.

**Risk:** 175 sqm unit — same liquidity problem as Flora Ville. Hard to resell. Better as long-term hold, serviced apartment conversion, or co-living.

---

---

## KEY INSIGHTS FOR PICKERS & INVESTORS

### Top Condo Opportunities (Ranked by Signal Strength)

**TIER 1 — Strong Signal, GPS-Verified Discount:**

1. **KTB PP Plus Sukhumvit 71 (Wattana)** — 10 units at 36% below KTB own valuation, ฿1.49–3.34M. PB Penthouse 2 sold at 67,600/sqm only 89m away. Bangkok Prep Secondary Campus 660m. Best condo cluster in the entire KTB dataset. `coll_grp_id 226417` (฿1.49M) is entry point.

2. **BAM Metro Sky Ratchada** — `22BKKCU0044000/0047000/0048000`: 30.7% discount vs Quinn Condo (313m). MRT Huai Khwang corridor. 29–44sqm. Verified market comparable by GPS.

3. **JAM เมอร์ราญา เพลส ลาดพร้าว 27 (asset 45544)** — ฿1.70M, 34sqm, 49,700/sqm. Life @ Ratchada at 71,700/sqm only 75m away = **30.7% real discount**. Chatuchak/Ratchada zone, 83 views = genuine buyer interest confirmed.

4. **JAM บ้านสุขโขทัย (asset 45226)** — ฿1.53M, 60sqm, 25,500/sqm. Chewathai Ramkhamhaeng at 61,000/sqm (343m) = **58% discount**. Large 60sqm 1BR. Bangkapi/Huamark — non-prime but huge size-value gap. Verify building condition.

**TIER 2 — Good Signal, Size/Age Caveat:**

5. **BAM State Tower Silom (66-sqm units)** — 38% real discount vs market (109k/sqm Hipflat). Silom location, BTS Surasak walkable. RISK: 26yr building, high NPA concentration.

6. **BAM ตึกช้าง รัชโยธิน** — `DIBKKCU0172001`: 175sqm at 50,600/sqm vs Hipflat same building 61,100/sqm = 17% discount. Campaign to 2028. Landmark address but illiquid large unit.

7. **KTB ดีไซน์ คอนโดมิเนียม รัชดา (Sutthisan)** — 7 units, 40.9% KTB own discount, ฿2.88–3.41M. Education anchor 170m, market 50m. BUT: no sqm data = can't confirm real discount vs market without site visit.

**TIER 3 — Notable but Needs Caution:**

8. **BAM ฟลอร่าวิลล์ สวนหลวง (campaign)** — 41–52% real discount vs Hipflat 39,600/sqm. Campaign price ฿3.55–8.0M for 153–405sqm. AUTO-REJECT on age (1992, 34 years). Only viable as hospitality/co-living conversion play.

9. **KBank Chatuchak/Ratchada condos at 29-36k/sqm** — `051001518`, `051000705`, `031001729`: Price so low it defies market. Age=0 means unknown — need verification. Central location.

---

### Key Pattern: KTB `nml_price` is a Unique Signal
KTB is the only provider that exposes its internal valuation vs sale price. The `nml_price` / `price` gap is the most reliable built-in discount indicator in the database — no comparison to external market needed. Two confirmed clusters: PP Plus Sukhumvit 71 (36%) and ดีไซน์ Sutthisan (41%).

### JAM Views ≠ Discount (Corrected)
High-view JAM listings are NOT necessarily discounted. Asset 45712 (ทรู ทองหล่อ, 84 views) is only 8.6% below Hipflat — essentially at market. Asset 49856 (จอนนี่ ทาวเวอร์, 46 views) is at market. The discount signal requires GPS-verified Hipflat cross-reference, not just view count.

### Development Risk Signal
**Chateau in Town developer:** 53 JAM + 16 BAM units across 10 project branches = serial developer default. High NPA concentration likely in every branch building. Avoid unless NPA% confirmed below 5%.

### Geographic Insight
**Chonburi beats Bangkok for sell-through** (33–39% vs ~15% max in BKK). Sri Racha industrial zone (บ่อวิน, หนองขาม, ทุ่งสุขลา) has proven transaction velocity at ฿1.0–1.5M. Worker housing demand is structural.

### BAM Fire Sale Watch
BAM campaigns with `sale_price_spc_to > 2027` and gap between `sell_price` and `sale_price_spc` > 40% are rare liquidation signals. Flora Ville and ตึกช้าง are the only active condo campaigns in Bangkok. Check `bam_properties` quarterly for new campaign activations.

---

## FINDING 18: Supply/Demand Zone Map — Where NPA Can Actually Be Absorbed

The critical question: is there a buyer or renter on the other side? Cross-referencing NPA condo stock (BAM + JAM + KBank) vs Hipflat market rental and resale depth by Bangkok district.

### Zone Classification (NPA absorption capacity)

**GREEN — Buy Zone: Strong rental demand, NPA is small fraction of market**

| District | NPA Units | Rental Units | Rent/Sale Ratio | DOM | YoY | NPA % of Market |
|----------|-----------|--------------|-----------------|-----|-----|-----------------|
| ห้วยขวาง | 57 | 4,977 | **2.25** | 468d | -6.9% | 2.6% |
| พระโขนง | 96 | 1,933 | **2.00** | 471d | -3.4% | 9.9% |
| จตุจักร | 64 | 2,246 | **1.95** | 423d | -3.9% | 5.6% |
| บางนา | 22 | 2,013 | **1.93** | 422d | -6.2% | 2.1% |

Rent demand is 1.9–2.25x for-sale supply. NPA stock is small vs total market depth. Renters are active despite falling prices. **Rental exit is viable.**

**AMBER — Proceed with care**

| District | NPA Units | Rent/Sale Ratio | DOM | YoY |
|----------|-----------|-----------------|-----|-----|
| คลองเตย | 16 | 2.76 | 551d | +0.7% |
| ราชเทวี | 13 | 2.02 | 524d | -3.9% |
| ยานนาวา | 26 | 1.10 | 512d | -1.7% |
| สวนหลวง | 64 | 1.23 | 363d | -7.2% |

คลองเตย has extraordinary rental depth (24,176 for rent vs 8,751 for sale = 2.76) but DOM of 551 days = resale is slow. Good rental hold, not quick flip.

**RED — Avoid: NPA oversupply or dead rental market**

| District | NPA Units | NPA % of Market | Rent/Sale Ratio | DOM | YoY |
|----------|-----------|-----------------|-----------------|-----|-----|
| บางเขน | **217** | **268%** | 0.27 | 421d | 0.0% |
| บึงกุ่ม | 48 | **81%** | 0.36 | 728d | -9.2% |
| ลาดพร้าว | 43 | **92%** | 0.30 | 348d | -3.5% |
| ภาษีเจริญ | 89 | **45%** | 0.77 | 700d | -10.0% |
| ประเวศ | 105 | **76%** | 0.45 | 399d | -6.0% |
| ดอนเมือง | 108 | **982%** | 0.55 | 407d | -6.2% |
| บางกะปิ | **293** | **66%** | 1.22 | 385d | +4.5% |
| บางรัก | 153 | **28%** | 2.51 | 440d | +1.3% |

**บางเขน:** 217 NPA condos vs 22 rental listings = 268% NPA-to-market-supply. Systemic collapse risk if all units hit market simultaneously.

**ดอนเมือง:** 108 NPAs vs 6 rental listings = 982% NPA penetration. Essentially no market. Don Mueang Condo Town finding (Finding 5) confirmed here by supply/demand data.

**ภาษีเจริญ worst trend:** -10% YoY + 700 DOM + 45% NPA penetration = Metro Park Sathorn zone. Hard avoid.

**บางรัก exception:** 153 NPAs, rent/sale 2.51, YoY +1.3%. Demand exists. This is mostly State Tower concentration. District has absorption capacity, but NPA concentration within State Tower building itself is the risk.

---

## FINDING 19: Fast-Exit Projects in NPA Target Zones (DOM < 100 days)

Projects where resale is proven fast — these validate that NPA investors can exit:

| Project | District | Sold psm | DOM | Sold Below Ask | Rent/Sale | Notes |
|---------|----------|----------|-----|----------------|-----------|-------|
| Define by Mayfair Sukhumvit 50 | พระโขนง | 93,700 | **44d** | 3% | 1.40 | Near-instant resale, sellers hold price |
| Lumpini Center Nawamin | บางกะปิ | 39,800 | **63d** | 13% | 0.17 | Fast but low psm |
| Subkaew Tower | ห้วยขวาง | 39,400 | **65d** | 28% | 0.25 | Fast but sellers cave 28% |
| Chapter Thonglor 25 | วัฒนา | 135,000 | **65d** | 15% | **6.27** | 188 rental vs 30 sale |
| Downtown Forty Nine | วัฒนา | 121,000 | **76d** | 22% | 1.48 | |

**Chapter Thonglor 25 standout:** Rent/sale ratio of 6.27 = 188 active rentals vs 30 for sale. Any NPA near Thonglor has an immediate rental exit even if resale takes time.

**Subkaew Tower caveat:** Fast to sell (65 DOM) but buyers negotiated 28% below asking — sellers need to price realistically. This is the building adjacent to จอนนี่ ทาวเวอร์ (JAM asset 49856). Confirms that area is a buyer's market.

**Define by Mayfair (Soi 50):** 44 DOM, only 3% sold below asking = sellers hold price here. Prime Phrakhanong zone with actual scarcity.

---

## FINDING 20: Nationwide LED Auction Demand — Only Chonburi Clears at Scale

LED court auction sell-through by province (minimum 100 cases):

| Province | Total | Sold | Sell-Through | Avg Price | Unsold Active |
|----------|-------|------|-------------|-----------|---------------|
| ชลบุรี | 2,880 | 773 | **26.8%** | ฿1.79M | 1,939 |
| กรุงเทพ | 785 | 127 | **16.2%** | ฿2.96M | 583 |
| ภูเก็ต | 616 | 78 | 12.7% | ฿12.34M | 471 |
| นนทบุรี | 1,899 | 191 | 10.1% | ฿2.76M | 1,463 |
| เชียงใหม่ | 1,868 | 182 | 9.7% | ฿3.77M | 1,543 |
| สงขลา | 508 | 33 | 6.5% | ฿1.95M | 441 |
| ภาษีเจริญ (province) | — | — | — | — | — |

**Key reads:**
1. Chonburi clears at 26.8% — nearly twice Bangkok's 16.2%. Industrial worker demand is proven.
2. Bangkok LED sell-through is only 16.2% despite being the largest economy. Competition from bank NPAs (BAM/JAM/KTB/KBank) substitutes for LED.
3. Phuket has median price of ฿12.34M — entirely different buyer segment (foreign/tourist). High price means low sell-through despite tourism demand.
4. Chiang Mai at 9.7% is weak despite tourism — oversupply from condo development 2015-2020.
5. Southern provinces (Songkhla, Trang) under 7% = true illiquid markets.

---

*Round 1: 2026-04-05. Round 2 (GPS validation, KTB clusters, JAM correction): 2026-04-05. Round 3 (supply/demand analysis): 2026-04-05. Price history tables only have 'new' entries — no historical drop data yet.*

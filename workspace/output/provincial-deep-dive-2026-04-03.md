# NPA Provincial Deep Dive — ภูเก็ต / เชียงใหม่ / ชลบุรี
Generated: 2026-04-03 | DB: 17,705 properties

---

## EXECUTIVE SUMMARY

| Metric | ภูเก็ต | เชียงใหม่ | ชลบุรี |
|---|---|---|---|
| **Total Properties** | 616 | 1,868 | 2,880 |
| **Unsold** | 471 (76%) | 1,543 (83%) | 1,939 (67%) |
| **Sold** | 78 (13%) | 182 (10%) | **773 (27%) 🔥** |
| **Withdrawn** | 67 (11%) | 143 (8%) | 168 (6%) |
| **Condos** | 0 | 0 | 0 |
| **Images** | 100% | 100% | 100% |
| **Data Freshness** | Apr 3, 2026 | Apr 3, 2026 | Apr 3, 2026 |

**Key Insight**: All three provinces are 100% houses/land. Zero condos. Strategy must be house rental or land banking, not condo yield plays.

---

## 1. SELL RATE ANALYSIS — WHERE DOES NPA ACTUALLY MOVE?

### ชลบุรี DOMINATES (27% overall sell rate)
| District | Total | Sold | Sell Rate | Insight |
|---|---|---|---|---|
| **พนัสนิคม** | 91 | 29 | **32%** 🔥 | Highest district sell rate in entire DB |
| พานทอง | 311 | 85 | 27% | Industrial worker housing demand |
| ศรีราชา | 1,190 | 321 | 27% | Laem Chabang port / Pinthong / Rojana |
| บ้านบึง | 142 | 39 | 27% | Industrial corridor |
| เมืองชลบุรี | 531 | 145 | 27% | City center |
| บางละมุง (Pattaya) | 458 | 119 | 26% | Tourism + foreign demand |
| สัตหีบ | 133 | 33 | 25% | Military base area |

### เชียงใหม่ (10% overall — sluggish)
| District | Total | Sold | Sell Rate |
|---|---|---|---|
| เชียงดาว | 22 | 4 | 18% |
| แม่แจ่ม | 12 | 2 | 17% |
| สันทราย | 258 | 35 | 14% |
| ดอยสะเก็ด | 141 | 19 | 13% |

### ภูเก็ต (13% overall — moderate)
| District | Total | Sold | Sell Rate |
|---|---|---|---|
| กะทู้ | 98 | 15 | 15% |
| เมืองภูเก็ต | 312 | 39 | 13% |
| ถลาง | 206 | 24 | 12% |

### Price Band Sell Rate
| Price Band | ภูเก็ต | เชียงใหม่ | ชลบุรี |
|---|---|---|---|
| < 500K | 0% | 13% | **34%** 🔥 |
| 500K-1M | 9% | 10% | **33%** 🔥 |
| 1M-2M | 16% | 10% | **25%** |
| 2M-3M | 18% | 6% | 21% |
| 3M-5M | 12% | 9% | 13% |
| 5M+ | 5% | 10% | 11% |

**INSIGHT**: ชลบุรี properties under 1M sell at 33-34% rate — these are the sweet spot. Small cheap houses near factories = instant demand.

---

## 2. AUCTION SUSPENSION ANALYSIS (Code 10 Warning)

| Province | Code 10 (Suspended) | Code 3 (No Bidders) | Code 1 (Sold) |
|---|---|---|---|
| ภูเก็ต | 350 (31%) | 355 (32%) | 421 (37%) |
| **เชียงใหม่** | **2,383 (55%) ⚠️** | 1,027 (24%) | 923 (21%) |
| ชลบุรี | 533 (9%) | 1,847 (30%) | 3,869 (62%) |

**CRITICAL FINDING**: เชียงใหม่ has **55% Code 10** (plaintiff suspension) — over half of all auction events are suspended by the plaintiff, likely GSB/banks negotiating with debtors. This means:
- Properties appear in the system but may NEVER actually go to auction
- Only 21% of auctions result in a sale vs 62% in ชลบุรี
- **Strategy**: Focus on Code 3 properties (confirmed no-bidders) to avoid wasted effort

---

## 3. PRICE ANOMALIES — Properties Trading at Deep Discounts

### 🏆 ชลบุรี — Best Value Gap (sold vs unsold)

**ศรีราชา Industrial Corridor — SOLD avg vs UNSOLD:**
| Tumbol | Sold Avg /wa | Unsold Min /wa | Gap |
|---|---|---|---|
| บ่อวิน | 37K | **8-16K** | **55-78% below sold** |
| บึง | 39K | **8-16K** | **59-79% below sold** |
| สุรศักดิ์ | 41K | **8K** | **80% below sold** |
| บางพระ | — | **8-15K** | **60-80% below avg** |
| หนองขาม | 61K | **11-14K** | **77-82% below sold** |

Top Unsold Picks (ศรีราชา):
| Asset ID | Tumbol | Size (wa) | Price | /wa | Sold Avg | Gap |
|---|---|---|---|---|---|---|
| 1943236 | บางพระ | 88.0 | 726K | **8,247** | ~51K | **-84%** |
| 1935620 | สุรศักดิ์ | 63.0 | 524K | **8,321** | 41K | **-80%** |
| 1860423 | สุรศักดิ์ | 63.0 | 524K | **8,321** | 41K | **-80%** |
| 1882448 | สุรศักดิ์ | 25.0 | 209K | **8,360** | 41K | **-80%** |
| 1882449 | สุรศักดิ์ | 22.5 | 207K | **9,178** | 41K | **-78%** |
| 1989359 | บางพระ | 99.0 | 934K | **9,436** | ~51K | **-82%** |

** Pattaya (บางละมุง) — SOLD avg vs UNSOLD:**
| Tumbol | Sold Avg /wa | Unsold Min /wa | Gap |
|---|---|---|---|
| หนองปรือ | 146K | **20K** | **-86% below sold** |
| บางละมุง | 57K | **17K** | **-70% below sold** |
| ตะเคียนเตี้ย | 50K | **12K** | **-76% below sold** |

### 🏆 ภูเก็ต — Anomalies in Premium Areas

| Asset ID | Area | Size (wa) | Price | /wa | District Avg | Gap |
|---|---|---|---|---|---|---|
| **1961347** | รัษฎา | 54.9 | 597K | **10,882** | 80K | **-86%** |
| 1883517 | รัษฎา | 33.1 | 735K | **22,197** | 80K | **-72%** |
| 1917390 | เทพกระษัตรี | 60.2 | 1.17M | **19,392** | 68K | **-72%** |
| 1881402 | ป่าคลอก | 57.0 | 999K | **17,523** | 60K | **-71%** |

⚠️ **These extreme discounts (70-86% below district avg) are RED FLAGS** — likely:
- No road access (ที่ดินไม่มีทางออก)
- Disputed title / inheritance issues
- Flood-prone / steep slope / jungle
- Must inspect before bidding

### เชียงใหม่ — CMU University Area

**Best buys near CMU (all unsold, under 3M):**
| Asset ID | Tumbol | Size (wa) | Price | /wa | Rnd | Address |
|---|---|---|---|---|---|---|
| **1892326** | สุเทพ | 95.0 | 1.46M | **15,401** | R6 | 117/4 |
| **1984008** | ป่าตัน | 90.0 | 1.40M | **15,527** | R6 | — |
| **1974032** | ช้างเผือก | 44.0 | 1.05M | **23,898** | R6 | — |
| 1887003 | หนองหอย | 60.0 | 1.45M | **24,207** | R6 | — |
| 1964566 | หนองหอย | 31.4 | 834K | **26,567** | R6 | — |
| 1894332 | วัดเกต | 50.3 | 1.39M | **27,613** | R6 | 124/253 |
| 1897418 | หนองหอย | 90.1 | 2.59M | **28,751** | R6 | — |

---

## 4. STRATEGIC INSIGHTS BY PROVINCE

### 🟢 ชลบุรี — HIGHEST PRIORITY (best liquidity + genuine value gap)
- **27% sell rate** — properties actually sell here
- Under 1M: 33-34% sell rate — best sweet spot
- **ศรีราชา/บ่อวิน**: 147 properties sold (most in entire DB), avg 37K/wa. Unsold at 8-16K/wa = **genuine 55-78% discount**
- Worker housing near Laem Chabang port, Pinthong/Rojana industrial estates = constant demand
- **Strategy**: Buy small houses (20-50 wa) near บ่อวิน/บึง under 1M, rent to factory workers for 3-5K/mo
- **Top targets**: 1935620, 1860423 (สุรศักดิ์ 63 wa at 524K), 1943236 (บางพระ 88 wa at 726K)

### 🟡 เชียงใหม่ — UNIVERSITY RENTAL STRATEGY (but Code 10 risk)
- **55% Code 10 suspension rate** — WARNING: Many properties may never reach actual auction
- Focus ONLY on Code 3 (confirmed no-bidders) properties
- CMU area (สุเทพ/หนองหอย/ช้างเผือก): 37 properties, 15-55K/wa
- Student rental potential: 3,500-8,000 THB/mo (similar to Songkhla)
- Light rail transit planned = future upside
- **Top target**: 1892326 (สุเทพ 95 wa at 15K/wa = 1.46M, near CMU)
- **Risk**: Properties near CMU may be over-appraised. Market land in สุเทพ is ~50-80K/wa (teedin108), NPA at 15K/wa = significant discount BUT check if this is a tiny rural plot far from the main road

### 🟠 ภูเก็ต — TOURISM PREMIUM (but lower liquidity)
- 13% sell rate — moderate
- **รัษฎา anomaly**: 2 properties at 10-22K/wa where district avg is 80K/wa
- These extreme discounts need physical inspection (likely no-road or slope issues)
- ฉลอง: growing south Phuket area, 25-60K/wa, decent rental demand
- Tourism-dependent = higher volatility, seasonality risk
- **Best area**: ฉลอง (under 3M) for Airbnb/house rental

---

## 5. CROSS-PROVINCE COMPARISON — INVESTMENT STRATEGY

| Strategy | Best Province | Why |
|---|---|---|
| **Worker rental yield** | **ชลบุรี (ศรีราชา)** | Highest sell rate, genuine discount, constant industrial demand |
| **Student rental** | **เชียงใหม่ (near CMU)** | Cheapest near major university, planned transit |
| **Tourist/Airbnb** | **ภูเก็ต (ฉลอง)** | Tourism demand, south Phuket growth |
| **Land banking** | **เชียงใหม่ (ฝาง/แม่อาย)** | Extremely cheap (1K-5K/wa), light rail plans |
| **Quick flip** | **ชลบุรี (บางละมุง)** | Pattaya demand, 26% sell rate, properties move |

---

## 6. ACTIONABLE NEXT STEPS

1. **Research ชลบุรี ศรีราชา property 1935620/1860423** — identical pricing suggests adjacent plots, 63 wa at 524K each
2. **Research เชียงใหม่ 1892326 สุเทพ** — 95 wa at 15K/wa near CMU, verify actual location
3. **Check flood risk for ชลบุรี บ่อวิน/บึง** — Laem Chabang area can flood
4. **Investigate ภูเก็ต 1961347 รัษฎา** — why is it 86% below district avg?
5. **Cross-reference เชียงใหม่ Code 3 properties** — filter for actual auction-ready properties only

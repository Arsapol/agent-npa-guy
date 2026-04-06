# Demand-First NPA Screening — 2026-04-06 10:07

## Approach
1. Find buildings with **strongest rental demand** (R:S ratio, low supply pressure)
2. Check if any NPA properties exist **within those buildings or nearby**
3. Compute unit-size-specific rent + honest yield

## Parameters
- Min rent:sale ratio: 3.0x
- Max supply pressure: 15.0%
- Search radius: 300m around each demand building
- Min discount: 15.0%

## Demand Buildings Found

**26 buildings** with R:S >= 3.0x, SP < 15.0%, 100+ units, 20+ rentals

| # | Building | District | Year | Units | Sale | Rent | R:S | SP | YoY | Trend |
|---|----------|----------|------|-------|------|------|-----|-----|-----|-------|
| 1 | แอชตัน อโศก | คลองเตย | 2017 | 783 | 110 | 1014 | 9.2x | 14% | +0.7% | ขาขึ้น |
| 2 | ไอดีโอ พระราม 9-อโศก | ห้วยขวาง | 2022 | 1222 | 41 | 328 | 8.0x | 3% | -6.9% | ขาขึ้น |
| 3 | โนเบิล รีดี | พญาไท | 2012 | 272 | 7 | 43 | 6.1x | 3% | -3.7% | ขาขึ้น |
| 4 | วิลล่า สาทร | คลองสาน | 2009 | 660 | 21 | 125 | 6.0x | 3% | -1.1% | ขาลง |
| 5 | โหมด สุขุมวิท 61 | คลองเตย | 2013 | 168 | 22 | 125 | 5.7x | 13% | +0.7% | ขาลง |
| 6 | ไลฟ์ แอท สาทร 10 | สาทร | 2010 | 286 | 21 | 117 | 5.6x | 7% | -0.1% | ขาลง |
| 7 | เอท ทองหล่อ เรสซิเดนซ์ | วัฒนา | 2009 | 196 | 27 | 150 | 5.6x | 14% | -1.3% | ขาขึ้น |
| 8 | ไอวี่ สาทร 10 | สาทร | 2008 | 290 | 22 | 97 | 4.4x | 8% | -0.1% | ขาลง |
| 9 | ไดมอนด์ สุขุมวิท | คลองเตย | 2010 | 485 | 26 | 108 | 4.2x | 5% | +0.7% | ขาลง |
| 10 | ไลฟ์ แอท สุขุมวิท 65 | คลองเตย | 2008 | 540 | 35 | 136 | 3.9x | 6% | +0.7% | ขาลง |
| 11 | บลอคส์ 77 | วัฒนา | 2011 | 467 | 26 | 101 | 3.9x | 6% | -1.3% | ขาลง |
| 12 | เดอะ เทรนดี้ คอนโดมิเนียม | คลองเตย | 2008 | 530 | 33 | 128 | 3.9x | 6% | +0.7% | ขาลง |
| 13 | คอนโด วัน เอ็กซ์ สุขุมวิท 26 | คลองเตย | 2008 | 329 | 42 | 162 | 3.9x | 13% | +0.7% | ขาลง |
| 14 | เดอะ ซี้ด มิงเกิล | สาทร | 2011 | 531 | 35 | 132 | 3.8x | 7% | -0.1% | ขาลง |
| 15 | เดอะ สกาย สุขุมวิท 103/4 | บางนา | 2014 | 898 | 40 | 149 | 3.7x | 4% | -6.4% | ขาขึ้น |
| 16 | โนเบิล รีฟอร์ม | พญาไท | 2012 | 191 | 13 | 46 | 3.5x | 7% | -3.7% | ขาขึ้น |
| 17 | คอนโด วัน ทองหล่อ | คลองเตย | 2008 | 132 | 12 | 42 | 3.5x | 9% | +0.7% | ขาลง |
| 18 | ไอดีโอ เวิร์ฟ สุขุมวิท | พระโขนง | 2011 | 490 | 17 | 59 | 3.5x | 3% | -3.4% | ขาขึ้น |
| 19 | วายน์ สุขุมวิท | คลองเตย | 2012 | 460 | 49 | 162 | 3.3x | 11% | +0.7% | ขาลง |
| 20 | โนเบิล โซโล | วัฒนา | 2010 | 572 | 65 | 213 | 3.3x | 11% | -1.3% | ขาลง |
| 21 | ไลฟ์ แอด ลาดพร้าว 18 | จตุจักร | 2010 | 456 | 15 | 48 | 3.2x | 3% | -3.9% | ขาลง |
| 22 | เดอะ โคลเวอร์ ทองหล่อ | วัฒนา | 2009 | 590 | 63 | 201 | 3.2x | 11% | -1.3% | ขาลง |
| 23 | รีเจ้นท์ โฮม สุขุมวิท 81 | พระโขนง | 2018 | 717 | 23 | 73 | 3.2x | 3% | -3.4% | ขาลง |
| 24 | คิวเฮ้าส์ คอนโด สาทร | คลองสาน | 2009 | 533 | 10 | 31 | 3.1x | 2% | -1.1% | ขาขึ้น |
| 25 | ดิ แอดเดรส สุขุมวิท 42 | คลองเตย | 2008 | 214 | 27 | 82 | 3.0x | 13% | +0.7% | ขาลง |
| 26 | ซีเคป คอนโด | ถลาง | 2014 | 198 | 16 | 48 | 3.0x | 8% | +0.2% | ขาลง |

## NPA Properties in Demand Areas

**26 NPA units** found near high-demand buildings (discount >= 15.0%)

| # | Src | ID | NPA Project | Demand Building | Price | sqm | Disc | Rent/mo | GRY | NRY | R:S | SP | YoY | Dist |
|---|-----|-----|------------|----------------|-------|-----|------|---------|-----|-----|-----|----|-----|------|
| 1 | SAM | 17422 | ทัวร์มาลีนไลท์ สาทร-ตากสิ | วิลล่า สาทร | ฿2,378,000 | 35 | 32% | ฿191,930 | 96.9% | 69.8% | 6.0x | 3% | -1.1% | 254m |
| 2 | KBANK | 058803528 | ทัวร์มาลีน สาทร-ตากสิน | วิลล่า สาทร | ฿2,976,000 | 40 | 24% | ฿191,930 | 77.4% | 55.6% | 6.0x | 3% | -1.1% | 298m |
| 3 | BAM | DRBKKCU0108001 | คอนโดมิเนียม โครงการแบงค์ | วิลล่า สาทร | ฿3,364,000 | 42 | 18% | ฿191,930 | 68.5% | 49.1% | 6.0x | 3% | -1.1% | 136m |
| 4 | BAM | DIBKKCU0191001 | คอนโดมิเนียม โครงการทัวร์ | วิลล่า สาทร | ฿2,024,000 | 28 | 26% | ฿78,880 | 46.8% | 33.0% | 6.0x | 3% | -1.1% | 266m |
| 5 | JAM | 523 | มายคอนโด สุขุมวิท 52 | ไดมอนด์ สุขุมวิท | ฿2,220,000 | 35 | 19% | ฿45,220 | 24.4% | 16.4% | 4.2x | 5% | +0.7% | 79m |
| 6 | BAM | HBKKCU5810001 | คอนโดมิเนียม โครงการศิริพ | รีเจ้นท์ โฮม สุขุมวิท 81 | ฿520,000 | 29 | 71% | ฿10,603 | 24.5% | 13.8% | 3.2x | 3% | -3.4% | 47m |
| 7 | KBANK | 058802943 | 59 เฮอริเทจ | โหมด สุขุมวิท 61 | ฿5,851,000 | 56 | 32% | ฿42,160 | 8.6% | 5.2% | 5.7x | 13% | +0.7% | 213m |
| 8 | BAM | DIBKKCU0109001 | คอนโดมิเนียมโครงการลีโวลา | ไลฟ์ แอด ลาดพร้าว 18 | ฿2,690,000 | 43 | 26% | ฿19,039 | 8.5% | 4.7% | 3.2x | 3% | -3.9% | 251m |
| 9 | KBANK | 058802726 | แอสปาย สุขุมวิท 48 | วายน์ สุขุมวิท | ฿2,700,000 | 38 | 33% | ฿18,020 | 8.0% | 4.4% | 3.3x | 11% | +0.7% | 254m |
| 10 | KBANK | 058802353 | เดอะ สกาย สุขุมวิท | เดอะ สกาย สุขุมวิท 103/4 | ฿1,799,000 | 31 | 46% | ฿11,602 | 7.7% | 4.1% | 3.7x | 4% | -6.4% | 40m |
| 11 | BAM | DIBKKCU0200001 | คอนโดมิเนียม โครงการยู ดี | บลอคส์ 77 | ฿2,251,000 | 30 | 21% | ฿13,770 | 7.3% | 4.0% | 3.9x | 6% | -1.3% | 242m |
| 12 | SAM | 14044 | ซีณิธ เพลส สุขุมวิท (Zeni | วายน์ สุขุมวิท | ฿2,890,000 | 46 | 40% | ฿18,020 | 7.5% | 3.9% | 3.3x | 11% | +0.7% | 164m |
| 13 | SAM | 21167 | แอสปาย สุขุมวิท 48 | วายน์ สุขุมวิท | ฿3,228,000 | 38 | 20% | ฿18,020 | 6.7% | 3.6% | 3.3x | 11% | +0.7% | 248m |
| 14 | BAM | DNBKKCU0199001 | คอนโดมิเนียม โครงการซีณิธ | วายน์ สุขุมวิท | ฿3,431,000 | 48 | 32% | ฿18,020 | 6.3% | 3.2% | 3.3x | 11% | +0.7% | 163m |
| 15 | KBANK | 058802713 | เดอะ สกาย สุขุมวิท | เดอะ สกาย สุขุมวิท 103/4 | ฿2,193,000 | 35 | 41% | ฿11,602 | 6.3% | 3.1% | 3.7x | 4% | -6.4% | 40m |
| 16 | SAM | 20652 | สุขุมวิท พลัส คอนโดมิเนีย | วายน์ สุขุมวิท | ฿3,603,000 | 43 | 20% | ฿18,020 | 6.0% | 3.1% | 3.3x | 11% | +0.7% | 147m |
| 17 | KBANK | 058802333 | เดอะ สกาย สุขุมวิท | เดอะ สกาย สุขุมวิท 103/4 | ฿2,240,000 | 35 | 41% | ฿11,602 | 6.2% | 3.0% | 3.7x | 4% | -6.4% | 37m |
| 18 | KBANK | 058802569 | เดอะสกาย สุขุมวิท | เดอะ สกาย สุขุมวิท 103/4 | ฿2,355,000 | 35 | 37% | ฿11,602 | 5.9% | 2.9% | 3.7x | 4% | -6.4% | 57m |
| 19 | KBANK | 051000834 | แอสปาย สุขุมวิท 48 | วายน์ สุขุมวิท | ฿2,847,500 | 32 | 16% | ฿13,132 | 5.5% | 2.8% | 3.3x | 11% | +0.7% | 196m |
| 20 | JAM | 185 | แอสปาย สุขุมวิท | วายน์ สุขุมวิท | ฿2,847,500 | 32 | 16% | ฿13,132 | 5.5% | 2.8% | 3.3x | 11% | +0.7% | 196m |
| 21 | KBANK | 058803263 | เดอะ สกาย สุขุมวิท | เดอะ สกาย สุขุมวิท 103/4 | ฿2,766,000 | 31 | 17% | ฿11,602 | 5.0% | 2.5% | 3.7x | 4% | -6.4% | 45m |
| 22 | KBANK | 058803299 | เดอะ สกาย สุขุมวิท | เดอะ สกาย สุขุมวิท 103/4 | ฿2,725,000 | 33 | 24% | ฿11,602 | 5.1% | 2.4% | 3.7x | 4% | -6.4% | 42m |
| 23 | KBANK | 058803612 | เดอะ สกาย สุขุมวิท | เดอะ สกาย สุขุมวิท 103/4 | ฿4,582,000 | 51 | 18% | ฿18,189 | 4.8% | 2.2% | 3.7x | 4% | -6.4% | 48m |
| 24 | KBANK | 051001239 | เดอะ สกาย สุขุมวิท  | เดอะ สกาย สุขุมวิท 103/4 | ฿2,966,500 | 35 | 22% | ฿11,602 | 4.7% | 2.2% | 3.7x | 4% | -6.4% | 20m |
| 25 | JAM | 718 | เดอะ สกาย สุขุมวิท | เดอะ สกาย สุขุมวิท 103/4 | ฿2,966,500 | 35 | 22% | ฿11,602 | 4.7% | 2.2% | 3.7x | 4% | -6.4% | 20m |
| 26 | KBANK | 058803316 | เดอะ สกาย สุขุมวิท | เดอะ สกาย สุขุมวิท 103/4 | ฿3,001,000 | 34 | 18% | ฿11,602 | 4.6% | 2.2% | 3.7x | 4% | -6.4% | 54m |

## Top 10 — Detailed Analysis

### #1 — SAM 17422
- **NPA Project:** ทัวร์มาลีนไลท์ สาทร-ตากสิน
- **Price:** ฿2,378,000 (35sqm = ฿67,024/sqm)
- **Bedroom/Bathroom:** ?/?
- **Building age:** unknown years
- **GPS:** 13.722633, 100.502391

**Market Data (from วิลล่า สาทร):**
- Market price: ฿107,000/sqm → verified (×0.92): ฿98,440/sqm
- **Real discount: 31.9%**
- Distance to demand building: 254m

**Demand Signals:**
- Rent:Sale ratio: **6.0x** (125 rent / 21 sale)
- Supply pressure: **3%** (21/660 units)
- YoY price trend: **-1.1%**
- Rental activity: 19% of units listed for rent
- Building: 2009 built, 660 total units

**Yield (unit-size adjusted, honest):**
- Rent estimate (35sqm): ฿225,800/mo
- Rent verified (×0.85): ฿191,930/mo
- GRY: 96.9%
- Annual net: ฿1,660,879
- **NRY: 69.8%**

### #2 — KBANK 058803528
- **NPA Project:** ทัวร์มาลีน สาทร-ตากสิน
- **Price:** ฿2,976,000 (40sqm = ฿74,512/sqm)
- **Bedroom/Bathroom:** 1/1
- **Building age:** 13 years
- **GPS:** 13.722711, 100.501964

**Market Data (from วิลล่า สาทร):**
- Market price: ฿107,000/sqm → verified (×0.92): ฿98,440/sqm
- **Real discount: 24.3%**
- Distance to demand building: 298m

**Demand Signals:**
- Rent:Sale ratio: **6.0x** (125 rent / 21 sale)
- Supply pressure: **3%** (21/660 units)
- YoY price trend: **-1.1%**
- Rental activity: 19% of units listed for rent
- Building: 2009 built, 660 total units

**Yield (unit-size adjusted, honest):**
- Rent estimate (40sqm): ฿225,800/mo
- Rent verified (×0.85): ฿191,930/mo
- GRY: 77.4%
- Annual net: ฿1,654,826
- **NRY: 55.6%**

### #3 — BAM DRBKKCU0108001
- **NPA Project:** คอนโดมิเนียม โครงการแบงค์คอก เฟ'ลิซ แอท กรุงธนบุรี คลองสาน
- **Price:** ฿3,364,000 (42sqm = ฿80,344/sqm)
- **Bedroom/Bathroom:** 2/1
- **Building age:** unknown years
- **GPS:** 13.7226, 100.504343

**Market Data (from วิลล่า สาทร):**
- Market price: ฿107,000/sqm → verified (×0.92): ฿98,440/sqm
- **Real discount: 18.4%**
- Distance to demand building: 136m

**Demand Signals:**
- Rent:Sale ratio: **6.0x** (125 rent / 21 sale)
- Supply pressure: **3%** (21/660 units)
- YoY price trend: **-1.1%**
- Rental activity: 19% of units listed for rent
- Building: 2009 built, 660 total units

**Yield (unit-size adjusted, honest):**
- Rent estimate (42sqm): ฿225,800/mo
- Rent verified (×0.85): ฿191,930/mo
- GRY: 68.5%
- Annual net: ฿1,651,534
- **NRY: 49.1%**

### #4 — BAM DIBKKCU0191001
- **NPA Project:** คอนโดมิเนียม โครงการทัวร์มาลีน ไลท์ สาทร-ตากสิน
- **Price:** ฿2,024,000 (28sqm = ฿72,467/sqm)
- **Bedroom/Bathroom:** 1/1
- **Building age:** unknown years
- **GPS:** 13.72277, 100.50235

**Market Data (from วิลล่า สาทร):**
- Market price: ฿107,000/sqm → verified (×0.92): ฿98,440/sqm
- **Real discount: 26.4%**
- Distance to demand building: 266m

**Demand Signals:**
- Rent:Sale ratio: **6.0x** (125 rent / 21 sale)
- Supply pressure: **3%** (21/660 units)
- YoY price trend: **-1.1%**
- Rental activity: 19% of units listed for rent
- Building: 2009 built, 660 total units

**Yield (unit-size adjusted, honest):**
- Rent estimate (28sqm): ฿92,800/mo
- Rent verified (×0.85): ฿78,880/mo
- GRY: 46.8%
- Annual net: ฿668,341
- **NRY: 33.0%**

### #5 — JAM 523
- **NPA Project:** มายคอนโด สุขุมวิท 52
- **Price:** ฿2,220,000 (35sqm = ฿62,943/sqm)
- **Bedroom/Bathroom:** 1/1
- **Building age:** unknown years
- **GPS:** 13.70889245, 100.598662

**Market Data (from ไดมอนด์ สุขุมวิท):**
- Market price: ฿84,400/sqm → verified (×0.92): ฿77,648/sqm
- **Real discount: 18.9%**
- Distance to demand building: 79m

**Demand Signals:**
- Rent:Sale ratio: **4.2x** (108 rent / 26 sale)
- Supply pressure: **5%** (26/485 units)
- YoY price trend: **+0.7%**
- Rental activity: 22% of units listed for rent
- Building: 2010 built, 485 total units

**Yield (unit-size adjusted, honest):**
- Rent estimate (35sqm): ฿53,200/mo
- Rent verified (×0.85): ฿45,220/mo
- GRY: 24.4%
- Annual net: ฿364,923
- **NRY: 16.4%**

### #6 — BAM HBKKCU5810001
- **NPA Project:** คอนโดมิเนียม โครงการศิริพจน์แมนชั่น 2 สวนหลวง
- **Price:** ฿520,000 (29sqm = ฿17,869/sqm)
- **Bedroom/Bathroom:** ?/?
- **Building age:** unknown years
- **GPS:** 13.70718, 100.60693

**Market Data (from รีเจ้นท์ โฮม สุขุมวิท 81):**
- Market price: ฿67,600/sqm → verified (×0.92): ฿62,192/sqm
- **Real discount: 71.3%**
- Distance to demand building: 47m

**Demand Signals:**
- Rent:Sale ratio: **3.2x** (73 rent / 23 sale)
- Supply pressure: **3%** (23/717 units)
- YoY price trend: **-3.4%**
- Rental activity: 10% of units listed for rent
- Building: 2018 built, 717 total units

**Yield (unit-size adjusted, honest):**
- Rent estimate (29sqm): ฿12,474/mo
- Rent verified (×0.85): ฿10,603/mo
- GRY: 24.5%
- Annual net: ฿71,820
- **NRY: 13.8%**

### #7 — KBANK 058802943
- **NPA Project:** 59 เฮอริเทจ
- **Price:** ฿5,851,000 (56sqm = ฿105,007/sqm)
- **Bedroom/Bathroom:** 1/1
- **Building age:** 15 years
- **GPS:** 13.724378, 100.582109

**Market Data (from โหมด สุขุมวิท 61):**
- Market price: ฿169,000/sqm → verified (×0.92): ฿155,480/sqm
- **Real discount: 32.5%**
- Distance to demand building: 213m

**Demand Signals:**
- Rent:Sale ratio: **5.7x** (125 rent / 22 sale)
- Supply pressure: **13%** (22/168 units)
- YoY price trend: **+0.7%**
- Rental activity: 74% of units listed for rent
- Building: 2013 built, 168 total units

**Yield (unit-size adjusted, honest):**
- Rent estimate (56sqm): ฿49,600/mo
- Rent verified (×0.85): ฿42,160/mo
- GRY: 8.6%
- Annual net: ฿305,494
- **NRY: 5.2%**

### #8 — BAM DIBKKCU0109001
- **NPA Project:** คอนโดมิเนียมโครงการลีโวลาดพร้าว18Project1จตุจักร
- **Price:** ฿2,690,000 (43sqm = ฿63,235/sqm)
- **Bedroom/Bathroom:** 1/1
- **Building age:** unknown years
- **GPS:** 13.805155, 100.569818

**Market Data (from ไลฟ์ แอด ลาดพร้าว 18):**
- Market price: ฿93,300/sqm → verified (×0.92): ฿85,836/sqm
- **Real discount: 26.3%**
- Distance to demand building: 251m

**Demand Signals:**
- Rent:Sale ratio: **3.2x** (48 rent / 15 sale)
- Supply pressure: **3%** (15/456 units)
- YoY price trend: **-3.9%**
- Rental activity: 11% of units listed for rent
- Building: 2010 built, 456 total units

**Yield (unit-size adjusted, honest):**
- Rent estimate (43sqm): ฿22,399/mo
- Rent verified (×0.85): ฿19,039/mo
- GRY: 8.5%
- Annual net: ฿126,242
- **NRY: 4.7%**

### #9 — KBANK 058802726
- **NPA Project:** แอสปาย สุขุมวิท 48
- **Price:** ฿2,700,000 (38sqm = ฿70,441/sqm)
- **Bedroom/Bathroom:** 1/1
- **Building age:** 12 years
- **GPS:** 13.71053, 100.594341

**Market Data (from วายน์ สุขุมวิท):**
- Market price: ฿114,000/sqm → verified (×0.92): ฿104,880/sqm
- **Real discount: 32.8%**
- Distance to demand building: 254m

**Demand Signals:**
- Rent:Sale ratio: **3.3x** (162 rent / 49 sale)
- Supply pressure: **11%** (49/460 units)
- YoY price trend: **+0.7%**
- Rental activity: 35% of units listed for rent
- Building: 2012 built, 460 total units

**Yield (unit-size adjusted, honest):**
- Rent estimate (38sqm): ฿21,200/mo
- Rent verified (×0.85): ฿18,020/mo
- GRY: 8.0%
- Annual net: ฿119,956
- **NRY: 4.4%**

### #10 — KBANK 058802353
- **NPA Project:** เดอะ สกาย สุขุมวิท
- **Price:** ฿1,799,000 (31sqm = ฿58,868/sqm)
- **Bedroom/Bathroom:** 1/1
- **Building age:** 11 years
- **GPS:** 13.674746, 100.611856

**Market Data (from เดอะ สกาย สุขุมวิท 103/4):**
- Market price: ฿118,000/sqm → verified (×0.92): ฿108,560/sqm
- **Real discount: 45.8%**
- Distance to demand building: 40m

**Demand Signals:**
- Rent:Sale ratio: **3.7x** (149 rent / 40 sale)
- Supply pressure: **4%** (40/898 units)
- YoY price trend: **-6.4%**
- Rental activity: 17% of units listed for rent
- Building: 2014 built, 898 total units

**Yield (unit-size adjusted, honest):**
- Rent estimate (31sqm): ฿13,649/mo
- Rent verified (×0.85): ฿11,602/mo
- GRY: 7.7%
- Annual net: ฿73,035
- **NRY: 4.1%**

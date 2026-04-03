---
name: web-search
description: Structured property web search patterns for Thai NPA analysis. Uses the built-in web_search tool with optimized queries for DDProperty, Hipflat, Baania, FazWaz, and other Thai property sites. Use when comparing NPA prices to market or researching rental rates.
---

# Property Web Search

## Overview

Search patterns optimized for Thai property market research. Uses the built-in `web_search` tool (Brave) with structured queries to find comparable properties, market prices, rental rates, and area intelligence.

**This skill has NO scripts — it provides query templates for the built-in web_search tool.**

## Search Patterns

### 1. Comparable Sale Prices

Find similar properties for sale in the same area:

```
"[property_type] [district] [province] ราคา" site:ddproperty.com
"[property_type] [district] ขาย" site:hipflat.co.th
"[property_type] near [landmark] for sale" site:fazwaz.com
```

**Examples:**
```
"คอนโด สุขุมวิท ราคา" site:ddproperty.com
"บ้านเดี่ยว บางนา ขาย" site:hipflat.co.th
"ที่ดิน เชียงใหม่ ราคาต่อตารางวา"
```

### 2. Rental Rates

Find rental comparables:

```
"[property_type] [district] ให้เช่า ราคา"
"[property_type] [district] rent" site:ddproperty.com
"[condo_name] rent monthly" site:fazwaz.com
```

**Examples:**
```
"คอนโด อโศก ให้เช่า ราคา"
"condo Sukhumvit 39 rent monthly"
"บ้าน นนทบุรี ให้เช่า"
```

### 3. Price per SQM Benchmarks

```
"ราคาต่อตารางเมตร [district] [year]"
"price per sqm [area] Bangkok [year]"
"[condo_name] ราคาต่อตารางเมตร"
```

### 4. Area Intelligence

```
"[district] BTS MRT สถานีใกล้"
"[area] โรงเรียนนานาชาติ"
"[area] น้ำท่วม ประวัติ"
"[district] การพัฒนา โครงการ [year]"
"[area] infrastructure development plan"
```

### 5. NPA / Auction Comparisons

```
"NPA [property_type] [province]" site:bfranchise.co.th
"ทรัพย์สินรอการขาย [bank_name] [province]"
"BAM ทรัพย์ [district]"
"กรมบังคับคดี [case_number]"
```

### 6. Legal / Title Research

```
"โฉนด [deed_number] [province]"
"ผังเมือง [district] [province]"
"พื้นที่น้ำท่วม [area]"
"[project_name] นิติบุคคล ปัญหา"
```

### 7. Developer / Project Research

```
"[project_name] รีวิว"
"[project_name] review"
"[developer_name] คอนโด [district]"
```

## How to Use

When NPA-guy needs market data, construct a query using the patterns above and call the `web_search` tool:

1. Identify what data you need (comparable price, rental rate, area info)
2. Pick the matching pattern
3. Fill in the property/area details
4. Call `web_search` with the constructed query
5. Analyze results and note sources

## Key Thai Property Sites

| Site | Best For |
|------|----------|
| ddproperty.com | Sale/rent listings, price history |
| hipflat.co.th | Condo prices, area analytics |
| baania.com | Price trends, area comparisons |
| fazwaz.com | English listings, expat-focused areas |
| bfranchise.co.th | Bank NPA listings |
| led.go.th | Official LED auction data |
| thinkofliving.com | Condo reviews, market analysis |

## Tips

- Always search in Thai for local properties: "คอนโด" not "condo"
- Add the year for current pricing: "ราคา 2026"
- Cross-reference at least 2 sources before concluding on market price
- For condos, search by project name for the most accurate comparables
- For land, search "ราคาที่ดิน [tambon] [amphur] ต่อตารางวา"

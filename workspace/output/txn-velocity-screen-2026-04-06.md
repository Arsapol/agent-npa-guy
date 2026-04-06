# Transaction-Velocity NPA Screening — 2026-04-06 10:49

## Approach
Find districts where properties **actually sell** (LED ขายแล้ว data),
then find available NPA inventory in those districts.

## Parameters
- Min sell-through: 8.0%
- Min sold count: 3
- Max price: ฿5,000,000
- Property types: townhouse,house
- Provinces: กรุงเทพมหานคร, ปทุมธานี, สมุทรปราการ, นนทบุรี

## Hot Districts (by LED sell-through rate)

| # | Province | District | Sold | Total | Sell% | Recent | <1M | 1-3M | 3-5M | 5-10M | >10M | Condo | House | TH | Land |
|---|----------|----------|------|-------|-------|--------|-----|------|------|-------|------|-------|-------|----|------|
| 1 | กรุงเทพม | เขตบางบอน | 11 | 63 | **17.5%** | 8 | 1 | 7 | 1 | 2 | 0 | 0 | 3 | 0 | 7 |
| 2 | กรุงเทพม | บางขุนเทียน | 3 | 18 | **16.7%** | 3 | 1 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 3 |
| 3 | กรุงเทพม | ภาษีเจริญ | 5 | 42 | **11.9%** | 5 | 0 | 4 | 1 | 0 | 0 | 3 | 0 | 0 | 2 |

## Available NPA in Hot Districts (62 total)

### Inventory Summary

| District | Sell% | Condo | House | Townhouse | Land | Commercial | Total | Avg Price |
|----------|-------|-------|-------|-----------|------|------------|-------|-----------|
| เขตบางบอน | 17.5% | 0 | 1 | 7 | 0 | 0 | 8 | ฿3,655,125 |
| บางขุนเทียน | 16.7% | 0 | 18 | 23 | 0 | 0 | 41 | ฿3,011,829 |
| ภาษีเจริญ | 11.9% | 0 | 4 | 9 | 0 | 0 | 13 | ฿3,297,923 |

### Best Deals by District

#### เขตบางบอน (sell-through 17.5%, 11 sold)
LED sold breakdown: condo=0, house=3, townhouse=0, land=7
Best price bands: <1M=1, 1-3M=7, 3-5M=1, 5-10M=2

| # | Src | ID | Type | Project | Price | Size | BR | District |
|---|-----|----|------|---------|-------|------|----|----------|
| 1 | JAM | 45787 | house | บ้านแสงตะวัน | ฿4,050,000 | 42wa | 3 | บางบอน |

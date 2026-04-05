# Market Checker Skill

Verify NPA condo prices against real market data from DDProperty, Hipflat, and ZMyHome.

## When to Use
- Before recommending ANY NPA property for purchase
- During npa-screener pipeline (Gate 2: market discount verification)
- When user asks "what's the market price for [project]?"
- After scraping new NPA data to flag overpriced listings

## Quick Start

```bash
# Fast mode (Hipflat + ZMyHome only, no browser needed)
python market_checker.py "15 sukhumvit residences" --no-ddproperty

# Full mode (all 3 sources, needs Camoufox)
python market_checker.py "inspire place abac"

# JSON output for pipeline integration
python market_checker.py "circle condominium" --json --no-ddproperty
```

## Individual Source Scripts

```bash
# Hipflat — fastest, best for YoY trends and transaction history
python hipflat_checker.py "rhythm ekkamai"

# ZMyHome — unique: กรมธนารักษ์ appraisal + sold prices
python zmyhome_lookup.py "circle condominium"

# DDProperty — largest inventory, needs Camoufox for Cloudflare
python ddproperty_checker.py "triple y residence samyan"
```

## Source Comparison

| Feature | Hipflat | ZMyHome | DDProperty |
|---|---|---|---|
| Anti-bot | Browser UA only | Browser UA + XHR header | **Camoufox** (Cloudflare) |
| Speed | ~1s | ~1s | ~3-5s (browser init) |
| Sale price/sqm | ✅ avg from listings | ✅ median from listings | ✅ median from listings |
| Transaction history | ✅ avg sold/sqm | ✅ sold listings | ❌ |
| Rental price | ✅ range | ✅ individual listings | ✅ individual listings |
| กรมธนารักษ์ appraisal | ❌ | ✅ per-floor table | ❌ |
| YoY price trend | ✅ | ❌ | ❌ |
| Year built | ✅ | ✅ | ✅ |
| Listing count | ✅ | ✅ | ✅ (largest sample) |
| District benchmark | ✅ | ❌ | ❌ |

## Confidence Scoring

The unified checker cross-references prices from all sources:

| Sources Agreeing | Within 15% | Confidence |
|---|---|---|
| 3 of 3 | Yes | **HIGH** |
| 2 of 3 | Yes | **HIGH** |
| 2 of 3 | No | **MEDIUM** |
| 1 only | - | **LOW** |
| 0 | - | **NO DATA** (AVOID property) |

## NPA Screening Integration

```python
from market_checker import check_market, npa_discount, npa_yield

# Check market for a project
result = await check_market("inspire place abac", include_ddproperty=False)

# Calculate NPA discount
npa_price_sqm = 39983  # from NPA database
discount = npa_discount(npa_price_sqm, result)
# → 12.8% (below 20% threshold = WATCH)

# Calculate rental yield
npa_total = 1147500
gross_yield = npa_yield(npa_total, result, sqm=28.7)
# → 8.3% (above 7% threshold = PASS)
```

## Dependencies

```
httpx          # ZMyHome + DDProperty
selectolax     # ZMyHome HTML parsing
camoufox       # DDProperty only (optional with --no-ddproperty)
```

## Rate Limiting

- Hipflat: 0.5s delay between requests (polite)
- ZMyHome: No observed limits, but keep to 1 req/s
- DDProperty: 0.5s between paginated requests, Camoufox cookies valid ~30 min

## Known Issues

- DDProperty BUILD_ID rotates on deploy — use `--refresh-build-id` if getting 404s
- ZMyHome concatenates price + price/sqm without separator — parser handles via heuristic split
- Hipflat search may return multiple projects — always uses top result
- Some small/old projects have zero listings on all 3 platforms → confidence = NO DATA

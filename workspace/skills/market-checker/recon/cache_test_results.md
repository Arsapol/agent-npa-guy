# Market Cache Test Results

Run date: 2026-04-05 15:05:35

## Summary

- Passed: 15/15
- Failed: 0

## Test Results


| Test | Status | Detail                                                                                                                                                    |
| ---- | ------ | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1a   | PASS   | Created registry id=2                                                                                                                                     |
| 1b   | PASS   | Found by canonical name                                                                                                                                   |
| 1c   | PASS   | Found by Thai name                                                                                                                                        |
| 1d   | PASS   | Found by alias                                                                                                                                            |
| 1e   | PASS   | Found by alias (case insensitive)                                                                                                                         |
| 1f   | PASS   | Update merges correctly, aliases=3: ['alpha test', 'test alpha', 'alpha condo']                                                                           |
| 1g   | PASS   | Inserted 3 price snapshots                                                                                                                                |
| 1h   | PASS   | 3 cached prices, all fresh                                                                                                                                |
| 1i   | PASS   | Stale sources correct: ['bam', 'jam', 'sam', 'ktb', 'kbank', 'led', 'ddproperty']                                                                         |
| 1j   | PASS   | Price history has 2 hipflat entries                                                                                                                       |
| 1k   | PASS   | Unlinked counts: {'bam': 3329, 'jam': 38820, 'sam': 4707, 'ktb': 2671, 'kbank': 13361, 'led': 17705}                                                      |
| 2a   | PASS   | market_checker works, consensus=44655                                                                                                                     |
| 2b   | PASS   | Cached 3 sources for Inspire Place: | hipflat: sale=44793/sqm, fresh=True | propertyhub: sale=44655/sqm, fresh=True | zmyhome: sale=44793/sqm, fresh=True |
| 2c   | PASS   | All 3 name variants resolve to same registry id=1                                                                                                         |
| 3    | PASS   | Cleanup: deleted 4 cache rows + 1 registry rows (Inspire Place kept)                                                                                      |


## Test Groups

### Test 1: market_cache.py CRUD Operations

- 1a: Create registry entry
- 1b: Find by canonical name
- 1c: Find by Thai name
- 1d: Find by alias
- 1e: Find by alias (case insensitive)
- 1f: Update merges correctly (no overwrites)
- 1g: Insert 3 price snapshots
- 1h: get_cached_prices returns fresh entries
- 1i: get_stale_sources identifies missing/stale sources
- 1j: Price history builds over time
- 1k: get_unlinked_count returns dict

### Test 2: Integration with Real Market Data

- 2a: market_checker.check_market() runs successfully
- 2b: Cache real results + verify retrieval
- 2c: All name variants resolve to same registry entry

### Test 3: Cleanup

- 3: Remove test data (Inspire Place kept as real data)


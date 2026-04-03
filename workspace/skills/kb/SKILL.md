---
name: kb
description: Knowledge base and knowledge graph for NPA property intelligence with temporal tracking. Every ingestion records category, area, source, and auto-calculated expiry. Powered by LightRAG (vector + graph) + kb_metadata table for freshness management.
---

# Knowledge Base Skill

## Overview

Persistent knowledge storage with **temporal metadata tracking**. Every document ingested is tagged with a category, area, source, and auto-calculated expiry date. This ensures NPA-guy can detect stale data (old pricing, outdated rental rates) and re-verify before making recommendations.

## Capabilities

### 1. Insert Document (with temporal metadata)

- Method: `insert_document(content, description, category, area, source)`
  - `content` (str): Document text (recommended under 2000 chars)
  - `description` (str): Brief label
  - `category` (str): **Required** — determines expiry (see TTL table below)
  - `area` (str): Geographic area (e.g. "สุขุมวิท 77", "อ่อนนุช")
  - `source` (str): Data source (e.g. "DDProperty", "Hipflat", "web_search")
  - Returns: Success message with metadata confirmation

### 2. Query Knowledge

- Method: `query_knowledge(query, mode)`
  - Results include `[Date: ...]` headers — check freshness before relying on data
  - Modes: hybrid (default), local, global, mix, naive

### 3. Check Freshness

- Method: `check_freshness(area, category)`
  - Returns: Count of fresh vs stale entries for an area/category
  - **Use before making pricing or rental recommendations**

### 4. Get Stale Entries

- Method: `get_stale_entries(limit)`
  - Returns: List of expired entries that need re-verification
  - Use during heartbeat to identify what needs re-searching

### 5. Graph Statistics + Health Check

- `get_graph_stats()` — node/edge counts + metadata summary
- `health_check()` — LightRAG + metadata table status

## Category TTL (Time-to-Live)

| Category | TTL | Use For |
|----------|-----|---------|
| `pricing` | 90 days | Sale prices, price/sqm benchmarks, appraisal comparisons |
| `rental` | 90 days | Rental rates, yield data, vacancy info |
| `flood` | 365 days | Flood reports, risk assessments, drainage info |
| `legal` | 180 days | Title issues, encumbrances, court findings |
| `area` | 180 days | Area intelligence, amenities, neighborhood quality |
| `project` | 365 days | Developer info, building reviews, juristic person |
| `infrastructure` | 365 days | BTS extensions, new roads, malls, development plans |
| `other` | 180 days | Default for anything else |

## Ingestion Format

Always include category, area, and source:

```python
insert_document(
    content="On Nut area condos rent 12,000-15,000 THB/month for 30-35 sqm units.",
    description="On Nut condo rental rates April 2026",
    category="rental",
    area="อ่อนนุช",
    source="DDProperty"
)
```

## Staleness Checker CLI

```bash
python scripts/check_stale.py                     # List stale entries
python scripts/check_stale.py --summary            # Quick summary by category
python scripts/check_stale.py --mark               # Mark expired as stale
python scripts/check_stale.py --category pricing   # Check specific category
```

## Query Modes

| Mode | Best For |
|------|----------|
| `hybrid` | Most property analysis queries (default) |
| `local` | Specific properties, projects, locations |
| `global` | Area trends, market patterns |
| `mix` | Finding connections between entities |
| `naive` | Quick keyword-like search |

## What to Ingest vs What NOT to Ingest

**INGEST** (evolving knowledge with category tag):
- Property analysis results → category: `area`
- Web search: sale prices → category: `pricing`
- Web search: rental rates → category: `rental`
- Web search: flood reports → category: `flood`
- Legal findings → category: `legal`
- Project/developer reviews → category: `project`
- Infrastructure plans → category: `infrastructure`

**DO NOT INGEST** (static reference data already in scripts):
- Zoning rules / FAR / OSR → `zoning-check` skill
- Tax rates / transfer fees → `property-calc` skill
- Flood risk zones → `flood-check` skill
- BTS/MRT station data → `location-intel` skill

## Notes

- Database: `npa_kb` (separate from Ada's `ada_kb`)
- Metadata table: `kb_metadata` in same database
- LLM: Gemini gemini-3.1-flash-lite-preview for entity extraction
- Embeddings: Gemini gemini-embedding-001 (3072 dimensions)
- Temporal headers are prepended to content for LightRAG entity extraction

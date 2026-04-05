---
name: ada-research
description: Delegate research to Ada (stocks agent) that serves both NPA property analysis and her investment research. Use when NPA-guy needs macro data, bank NPL trends, developer sector health, REIT yields, rate decisions, or any financial/market context that Ada would naturally research for her own stock analysis. Always win-win — the request must align with Ada's investment domain (equities, macro, credit, cross-asset). NOT for generic questions Ada wouldn't benefit from.
---

# Ada Research Collaboration

Delegate research tasks to Ada that produce knowledge useful for both agents.

## Win-Win Principle

Every request must satisfy BOTH:
1. **NPA-guy needs it** — for property valuation, location analysis, or market timing
2. **Ada benefits from it** — the research produces investment-relevant data she'd want in her KB anyway

Ada ingests all research into her `ada_kb` (LightRAG). NPA-guy queries results directly via SQL or `ask_agent.sh`.

## How to Use

### Quick Query (synchronous, ≤120s)
For questions Ada can answer from existing KB knowledge:

```bash
bash skills/agent-comm/scripts/ask_agent.sh \
  "<message>" \
  "/Users/arsapolm/.nanobot-stocks/workspace" \
  "/Users/arsapolm/.nanobot-stocks/config.json" \
  120
```

### Deep Research (background via spawn)
For research requiring web search and fresh analysis — use `spawn` tool:

```
Task: "Run bash skills/agent-comm/scripts/ask_agent.sh '<research brief>' /Users/arsapolm/.nanobot-stocks/workspace /Users/arsapolm/.nanobot-stocks/config.json 600"
```

Set timeout to 600s for research tasks.

### Direct SQL Query (fastest)
Query Ada's KB directly when you know she has the data:

```bash
psql -d ada_kb -t -A -c "SELECT content FROM lightrag_doc_full WHERE content ILIKE '%<keyword>%' LIMIT 3;"
```

## Research Brief Template

When requesting research, use this structure:

```
[NPA-guy → Ada Research Request]

TOPIC: <what to research>
WHY ADA CARES: <how this connects to her investment domain>
WHAT I NEED: <specific data points NPA-guy needs>
FORMAT: Structured summary with tickers, numbers, dates
ACTION: Research + ingest to your KB. I'll query results directly.
TIP: If yfinance returns no data for a ticker, use your google-finance skill as fallback.
```

## Approved Research Topics

See [references/topics.md](references/topics.md) for the full catalog of win-win research topics with example briefs.

## Topic Categories

| Category | NPA-guy Gets | Ada Gets |
|----------|-------------|----------|
| Bank NPL trends | Foreclosure supply forecast | Bank stock picks, credit cycle signals |
| Developer health | Market direction, NPA pipeline | Developer stock valuations, sector rotation |
| BOT rate decisions | Mortgage affordability, buyer demand | Rate-sensitive stock plays, bond impacts |
| REIT performance | Rental yield benchmarks | REIT valuation, income stock picks |
| Macro outlook | Market timing, risk assessment | Asset allocation, cross-asset signals |
| EEC/industrial | Land value trajectory | Industrial/energy stock picks |
| Insurance/credit | Foreclosure buyer financing trends | Financial sector analysis |

## Workflow

1. **Check Ada's KB first** — `psql ada_kb` to see if she already has the data
2. **If stale or missing** — Send research brief via `ask_agent.sh`
3. **Ada researches + ingests** — she builds entities/relations in her knowledge graph
4. **Query results** — pull specific data from `ada_kb` for property analysis
5. **Optionally cross-ingest** — key findings can also go into NPA KB (use `cli_ingest.py` to avoid lock issues)

## Limitations

- Ada needs 30-60s startup time + research time — use `spawn` for anything complex
- Single-message, no multi-turn — each call is stateless
- Requests must align with Ada's investment focus (see [references/topics.md](references/topics.md))

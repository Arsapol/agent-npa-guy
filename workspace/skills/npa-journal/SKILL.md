---
name: npa-journal
description: NPA-guy's daily thought journal and self-improvement system. Writes structured daily entries recording property analyses, location research, legal findings, predictions, and mistakes. Triggers reflection cycles (weekly/monthly) to find patterns in errors and evolve behavior. Use at end of every analytical session or when user asks NPA-guy to reflect.
---

# NPA-guy's Journal

Daily thought journal and self-improvement feedback loop. NPA-guy writes structured entries about what properties were analyzed, what actions were taken, what was missed, and what predictions were made. Periodic reflection cycles review past entries to find patterns and drive evolution.

## When to Write

- **End of every session** that involves property analysis, location research, or recommendations
- **After discovering a mistake** — record what was wrong and how it was corrected
- **When user explicitly asks** NPA-guy to journal or reflect
- **After KB corrections** — record what was stale/wrong and what was done about it

Do NOT write for: trivial queries, configuration, or sessions with no analytical content.

## File Structure

```
thoughts/
├── YYYY-MM-DD.md              # Daily entries (one per day, append if multiple sessions)
├── reflections/
│   ├── week-YYYY-WNN.md       # Weekly reflection (every Monday or on-demand)
│   └── month-YYYY-MM.md       # Monthly deep review (1st of each month)
```

## Daily Entry Format

```markdown
# NPA-guy's Thoughts — YYYY-MM-DD

## Session Context
- Properties: [what properties/areas were analyzed]
- Trigger: [user request / self-initiated]
- Session via: [telegram / claude-code / heartbeat-cron]

## What I Analyzed
[Brief summary — what properties, what data, what questions was I trying to answer?]

## Properties Reviewed
| Property | Location | Type | Price (THB) | Verdict | Key Factor |
|----------|----------|------|-------------|---------|------------|
| [address/project] | [area] | [condo/house/land] | [X] | BUY/WATCH/AVOID | [main reason] |

## Actions Taken

### Research Actions
- Searched KB for [area/property type] history
- Checked BTS/MRT proximity for [property]
- Researched school zones near [location]
- Looked up comparable prices in [area]
- Checked flood risk maps for [area]

### KB Ingestion
- Ingested property analysis: [description]
- Ingested area intelligence: [description]
- Total documents ingested: [count]

### Recommendations Given
- Recommended BUY on [property] because [reason]
- Recommended AVOID on [property] because [reason]
- Flagged [risk] to user

## What I Got Wrong
- [Specific mistake]: I said [X] but the data shows [Y]
- Root cause: [missed data / wrong assumption / incomplete research / ...]
- What I should have done: [specific corrective action]

## What I Got Right
- [What worked and why]

## Predictions (Falsifiable)
- By [DATE]: [Area/Property] will [specific outcome] because [reasoning]
- Confidence: [X]%
- Invalidated if: [specific condition]

## Open Questions
- [Things I want to investigate but couldn't resolve today]
- [Data I need but don't have access to]

## Self-Check
- Did I check BOTH buy and avoid reasons? [yes/no]
- Did I verify title deed type? [yes/no]
- Did I check flood risk? [yes/no]
- Did I check transport connectivity? [yes/no]
- Did I compare to market benchmarks? [yes/no]
- Did I ingest findings to KB? [yes/no]
- Am I being overly optimistic about any property? [yes/no — which?]
```

## Appending to Existing Daily Entry

If NPA-guy has multiple sessions on the same day, append with separator:

```markdown
---

## Session 2 — [HH:MM] UTC+7

[Same structure as above, starting from "Session Context"]
```

## Weekly Reflection (every Monday or on-demand)

Read the last 7 daily entries and write a reflection.

```markdown
# Weekly Reflection — Week NN, YYYY

## Properties Reviewed This Week
| Property | Verdict | Outcome (if known) |
|----------|---------|-------------------|
| [property] | [BUY/WATCH/AVOID] | [sold/still available/price changed] |

## Predictions Scored
| Prediction (from date) | Outcome | Right/Wrong/TBD | Lesson |
|------------------------|---------|-----------------|--------|
| [prediction text] | [what actually happened] | [R/W/TBD] | [what this teaches] |

## Patterns in My Errors
- [Pattern]: I keep [doing X] when I should [do Y]

## Patterns in My Successes
- [Pattern]: [What approach keeps working and why]

## Area Intelligence Updates
- [Area]: [New findings that update our understanding]

## What Changes Next Week
- [Specific behavior change or research focus]
```

## Monthly Deep Review (1st of each month)

```markdown
# Monthly Review — YYYY-MM

## Properties Analyzed: [N]
- BUY recommendations: [N]
- WATCH recommendations: [N]
- AVOID recommendations: [N]

## Prediction Accuracy
- Right: [N] ([%])
- Wrong: [N] ([%])
- TBD: [N]

## Recurring Patterns
- [Areas with best deals]
- [Common red flags]
- [Most reliable value indicators]

## Self-Assessment
- Am I getting better at [X]?
- What's my biggest blind spot?

## Evolution Actions
- [Update analytical framework]
- [New data source to add]
- [Area to research deeper]
```

## Important Constraints

- **Honesty over comfort** — the journal is useless if NPA-guy sanitizes mistakes
- **Specificity** — "Property was overpriced" is noise. "Condo at Sukhumvit 39 asking 120K/sqm vs market 95K/sqm = 26% premium" is useful
- **Actions must be concrete** — "I'll research more" is not an action. "I added flood zone check to my analysis template" is.
- **Predictions must be falsifiable** — "Market might go up" is worthless. "Ari area condos will see 5%+ price increase by Q3 2026 due to Green Line extension" can be scored.

# JAM Scraper (JMT Network Services)

## Purpose

Scrape NPA property listings from JMT's JAM auction platform for analysis by NPA-guy.

## Status

**Phase 1: Recon** — analyzing site structure, network calls, and rendering requirements.

## Site

- JAM (JMT Asset Management) — NPA auction platform operated by JMT Network Services PCL
- URL: https://www.jmt.co.th or JAM-specific subdomain (TBD after recon)

## Architecture (Planned)

Following the LED/SAM scraper pattern:
- async httpx (if API found) or Playwright (if JS-rendered)
- selectolax for HTML parsing
- Pydantic v2 for data validation
- SQLAlchemy 2.0+ for PostgreSQL storage
- asyncio.Semaphore for bounded concurrency

## Recon Workflow

1. `recon/browse_and_capture.py` — Playwright browser session, captures HAR + HTML
2. Analyze HAR for API endpoints
3. Map data schema
4. Build production scraper in `scripts/`

## Usage

```bash
# Phase 1: Recon
cd recon && python browse_and_capture.py

# Phase 2+: Production scraper (TBD)
```

# PropertyHub.in.th — API Recon Report

Date: 2026-04-04
Analyst: npa-guy

---

## Executive Summary

PropertyHub.in.th is a **Next.js SSR site** backed by a **GraphQL API** at
`https://api.propertyhub.in.th/graphql`. No auth token is required — only a
session cookie obtained by visiting the homepage first.  
Simple `httpx.Client` with a browser User-Agent works without any JS rendering.

---

## API Endpoint

| Detail | Value |
|--------|-------|
| URL | `https://api.propertyhub.in.th/graphql` |
| Protocol | GraphQL over HTTPS (POST) |
| Auth | None (no token, no API key) |
| Session cookie | `unleash-session-id` — set automatically on first GET to homepage |
| Introspection | **Disabled** (`__schema` returns 400) |
| Rate limit | Not observed during testing (up to ~20 requests/session) |
| JS Assets CDN | `https://assets2.propertyhub.in.th` |

---

## Anti-Bot Measures

- **No Cloudflare** — `cf-ray` header absent, server header is `istio-envoy`
- **No CAPTCHA** — clean responses with browser UA
- **Session cookie required** — `unleash-session-id` is checked server-side;
  GET the homepage first with `client.get("https://propertyhub.in.th")` before
  API calls
- **Simple browser UA sufficient** — standard Chrome UA passes all checks
- **GraphQL introspection disabled** — must reverse-engineer schema from JS bundles

---

## Discovered GraphQL Queries

All queries confirmed working. Schema extracted from JS bundle at
`https://assets2.propertyhub.in.th/_next/static/chunks/pages/_app-*.js`
(6 MB minified bundle, Build ID: `propertyhub-web-6903e3b979f6339041f9cc1f8b18499e5000f4c3`).

### 1. `globalSearch` — search projects by name

```graphql
query globalSearch($name: String, $locale: LocaleType, $size: Int, $page: Int, $propertyType: PropertyTypeItem) {
  globalSearch(name: $name, locale: $locale, size: $size, page: $page, propertyType: $propertyType) {
    status
    error { message }
    result {
      projects {
        id
        name
        nameEnglish
        slug
        projectType
        address
        listingCountByPostType {
          FOR_RENT { listingCount }
          FOR_SALE { listingCount }
        }
      }
      projectPagination { page perPage totalCount }
    }
  }
}
```

Variables: `{"name": "inspire place abac", "locale": "EN", "size": 10, "propertyType": "CONDO"}`

Returns matching projects with listing counts per post type. Search is fuzzy and handles both Thai and English names.

---

### 2. `project` — project detail (year built, total units, developer, facilities)

```graphql
query ($projectId: ID!, $locale: LocaleType) {
  project(projectId: $projectId, locale: $locale) {
    status
    error { message }
    result {
      id
      slug
      name
      nameEnglish
      description
      address
      location { lat lng }
      projectType
      facilities
      projectInfo
      developer { id name }
      unitType
      provinceCode
      districtCode
      createdAt
      updatedAt
      listingCountByPostType {
        FOR_RENT { listingCount }
        FOR_SALE { listingCount }
      }
    }
  }
}
```

Variables: `{"projectId": "1348", "locale": "EN"}`

`projectInfo` is a JSON object with:
- `totalUnits` — total number of units (string)
- `completedYear` — year built (string)
- `buildingsFloors` — floors per building (string)
- `buildingNumbers` — number of buildings (string)
- `utilityFee` — common area fee in THB/sqm/month (string)
- `ceilingHeight` — ceiling height (string)
- `possibleProjectNames` — Thai + English alternate name aliases

`facilities` is a flat boolean object: `pool`, `fitness`, `parking`, `cctv`, `lift`, `security`, etc.

`developer` is sometimes null even when the developer is known.

---

### 3. `listings` — sale and rental listings, filtered by project

```graphql
query listings(
  $locale: LocaleType
  $page: Int
  $perPage: Int
  $listingAttributes: ListingSearchForConsumerAttributes
) {
  listings(
    locale: $locale
    page: $page
    perPage: $perPage
    ListingSearchForConsumerAttributes: $listingAttributes
  ) {
    status
    error { message }
    pagination { page perPage totalCount totalPages }
    result {
      id
      postType
      title
      price {
        forRent { monthly { type price } }
        forSale { type price }
      }
      roomInformation {
        numberOfBed
        numberOfBath
        roomArea
        onFloor
        roomType
      }
      createdAt
      updatedAt
    }
  }
}
```

**Critical**: the argument name on the field is `ListingSearchForConsumerAttributes` (CamelCase), not `listingAttributes`, but the variable type is `ListingSearchForConsumerAttributes`.

`listingAttributes` accepts:
- `projectId` — numeric project ID (string) — **use this to filter by project**
- `postType` — `"FOR_SALE"` or `"FOR_RENT"` or `"FOR_SALE_DOWN_PAYMENT"`
- `propertyType` — `"CONDO"`, `"HOUSE"`, etc.
- `zoneIds` — array of zone IDs

**`projectSlug` is NOT a valid field** — the API uses `projectId` only.

Pagination: up to 100 per page; use `totalPages` to iterate all pages.

---

### Other Useful Queries

| Query | Purpose |
|-------|---------|
| `zoneListings` | Listings in a zone (Bangkok district) |
| `nearbyListings` | Listings near lat/lng coordinates |
| `priceHistogram` | Bucket distribution of prices |
| `getReviewsProject` | User reviews for a project |
| `projects` (plural) | Search projects with `ProjectSearchForConsumerAttributes` |

---

## Data Format

All responses follow this envelope:

```json
{
  "data": {
    "<queryName>": {
      "status": "SUCCESS",
      "error": null,
      "result": { ... },
      "pagination": { "page": 1, "perPage": 60, "totalCount": 9, "totalPages": 1 }
    }
  }
}
```

Prices are in **whole Thai Baht** (not satang). `price.forSale.price` is an integer.
Rental price is in `price.forRent.monthly.price`.

---

## Sample Working Requests

### Search project by name
```python
import httpx, json

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) ...",
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Origin": "https://propertyhub.in.th",
    "Referer": "https://propertyhub.in.th/",
}

with httpx.Client(headers=headers, timeout=30) as c:
    c.get("https://propertyhub.in.th")  # warm session cookie

    r = c.post("https://api.propertyhub.in.th/graphql", json={
        "query": "query globalSearch($name: String, $locale: LocaleType, $size: Int) { globalSearch(name: $name, locale: $locale, size: $size) { result { projects { id name nameEnglish slug } } } }",
        "variables": {"name": "inspire place abac", "locale": "EN", "size": 5}
    })
    projects = r.json()["data"]["globalSearch"]["result"]["projects"]
    # => [{"id": "1348", "nameEnglish": "Inspire Place ABAC-Rama IX", "slug": "inspire-place-abac-rama-ix"}]
```

### Get sale listings for a project
```python
    r = c.post("https://api.propertyhub.in.th/graphql", json={
        "query": "query listings($locale: LocaleType, $page: Int, $perPage: Int, $listingAttributes: ListingSearchForConsumerAttributes) { listings(locale: $locale, page: $page, perPage: $perPage, ListingSearchForConsumerAttributes: $listingAttributes) { status pagination { totalCount } result { id price { forSale { price } } roomInformation { roomArea } } } }",
        "variables": {
            "locale": "EN",
            "page": 1,
            "perPage": 100,
            "listingAttributes": {"projectId": "1348", "postType": "FOR_SALE"}
        }
    })
```

---

## Test Results — 4 Target Projects

| Project | Year | Units | Sale listings | Price/sqm avg | Rent listings | Rent/mo avg | Yield est. |
|---------|------|-------|--------------|---------------|--------------|-------------|------------|
| Inspire Place ABAC-Rama IX | 2006 | 636 | 9 | 43,195 THB | 26 | 12,726 THB | ~8.0% |
| 15 Sukhumvit Residences | 2013 | 514 | 78 | 125,697 THB | 73 | 32,458 THB | ~5.2% |
| Circle Condominium | 2011 | 917 | 81 | 119,459 THB | 192 | 43,827 THB | ~7.8% |
| Chateau In Town Major Ratchayothin | 2008 | 120 | 5 | 111,611 THB | 19 | 19,231 THB | ~6.7% |

---

## What PropertyHub Has vs DDProperty / Hipflat / ZMyHome

| Feature | PropertyHub | DDProperty | Hipflat | ZMyHome |
|---------|-------------|------------|---------|---------|
| GraphQL API (structured) | **YES** | REST-ish | HTML-only | HTML-only |
| No auth required | **YES** | YES | YES | YES |
| projectInfo (year, units, floors) | **YES** | partial | NO | NO |
| Facility details (boolean flags) | **YES** | YES | NO | NO |
| Utility fee / CAM fee | **YES** | NO | NO | NO |
| Thai alternate name aliases | **YES** | NO | NO | NO |
| Rental listings | YES | YES | YES | YES |
| Price histogram | YES | NO | NO | NO |
| Developer info | partial (often null) | YES | YES | NO |
| Anti-bot protection | Very low | Low | Low | Low |
| Pagination | Clean (totalPages) | Varies | Varies | Varies |

**PropertyHub uniquely useful for**:
1. `projectInfo.utilityFee` — monthly CAM fee in THB/sqm (unavailable elsewhere)
2. `possibleProjectNames` — Thai/English name variants for cross-referencing other DBs
3. Clean GraphQL with `projectId`-filtered listing queries — no HTML scraping needed
4. `completedYear` + `totalUnits` + `buildingNumbers` in one query

---

## Recommended Approach

1. **Use `globalSearch`** to resolve a project name to `id` + `slug`. Pass top result.
2. **Use `project` query** for metadata (year, units, utility fee, location).
3. **Use `listings` query** twice — `FOR_SALE` and `FOR_RENT` — with `projectId`.
4. Paginate with `perPage=100` — most projects have <200 listings per type.
5. Session cookie: `GET https://propertyhub.in.th` once per `httpx.Client` session.

**Workflow for NPA screening**:
```
check_project("inspire place abac")
  → project.completedYear, totalUnits, utilityFee
  → sale: price/sqm min/avg/max
  → rent: rent/mo min/avg/max
  → implied gross yield
```

All implemented in `/workspace/skills/market-checker/scripts/propertyhub_checker.py`.

---

## Gotchas

1. `projectSlug` does **not** work as a `listingAttributes` filter — only `projectId`.
2. `developer` field is null for most projects.
3. The `listings` GraphQL field argument is `ListingSearchForConsumerAttributes` (capital L), not snake_case.
4. Prices are in baht (not satang) — unlike the LED scraper which uses satang.
5. `projectInfo` values are strings, not numbers — cast with `int()` as needed.
6. Render the `globalSearch` with `propertyType: "CONDO"` to avoid matching non-condo projects with the same name.

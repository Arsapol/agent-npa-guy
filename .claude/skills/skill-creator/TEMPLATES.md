# Skill Templates

Reference templates for common Skill patterns. Use these as starting points when creating new Skills.

## Template 1: Simple Skill (single SKILL.md)

Best for: coding patterns, tool integrations, simple workflows.

```yaml
---
name: csv-data-seeder
description: Seeds database tables from CSV or JSON files with validation and error reporting. Use when the user asks to populate, seed, import, or load sample data into a database.
---
```

````markdown
# CSV Data Seeder

Seeds database tables from structured files with schema validation.

## Prerequisites

- Database connection configured via environment variables

## Quick reference

| User says | Action |
|-----------|--------|
| "seed the users table from data.csv" | Parse CSV, validate schema, insert rows |
| "import sample data" | Detect file format, seed all matching tables |

## Instructions

1. Read the source file and detect format (CSV, JSON)
2. Validate against the target table schema
3. Insert rows in batches of 100, reporting progress
4. On error: log the failing row, continue with remaining rows

## Degrees of freedom

**Claude MUST follow:**
- Always validate schema before inserting
- Always use batched inserts (never single-row)

**Claude decides:**
- Batch size (default 100, adjust for table width)
- Error handling strategy (skip vs. abort) based on user preference

## Constraints

- Never truncate existing data without explicit user confirmation
- Never insert without schema validation
````

## Template 2: Workflow Skill (with checklist)

Best for: multi-step processes, operational procedures, data pipelines.

```yaml
---
name: deploying-to-staging
description: Executes the staging deployment workflow including build verification, database migration, and smoke tests. Use when the user wants to deploy to staging, push to staging environment, or run pre-production deployment.
---
```

````markdown
# Deploying to Staging

Executes the full staging deployment pipeline with safety checks at each stage.

## Prerequisites

- CI/CD pipeline configured
- Database migration tool installed

## Workflow

Copy this checklist and track progress:

```
Deployment Progress:
- [ ] Step 1: Verify build passes
- [ ] Step 2: Run database migrations
- [ ] Step 3: Deploy to staging
- [ ] Step 4: Run smoke tests
- [ ] Step 5: Verify output
```

### Step 1: Verify build passes

Run the full test suite. Do not proceed if any test fails.

### Step 2: Run database migrations

Apply pending migrations. Back up the database first.

### Step 3: Deploy to staging

Push the build artifact to the staging environment.

### Step 4: Run smoke tests

Execute the smoke test suite against the staging URL.

### Step 5: Verify output

Check deployment logs and health endpoint. If verification fails, return to Step 1.

## Degrees of freedom

**Claude MUST follow:**
- Never skip the build verification step
- Always back up before migrations

**Claude decides:**
- Which smoke tests to prioritize based on changed files

## Safety guardrails

- Never deploy to production using this workflow
- Always confirm with user before running migrations
````

## Template 3: Domain Knowledge Skill (with references)

Best for: complex domains with schemas, APIs, or extensive reference material.

```yaml
---
name: billing-pipeline
description: Provides expertise on the internal billing pipeline including invoice generation, payment processing, and reconciliation. Use when working with billing code, payment flows, invoice templates, or when the user mentions billing, invoices, or payment processing.
---
```

````markdown
# Billing Pipeline

Internal billing system knowledge covering invoice lifecycle, payment processing, and reconciliation.

## Overview

The billing pipeline processes invoices through three stages: generation, payment collection, and reconciliation. Each stage has its own service and database schema.

## Quick start

Most common task — generate an invoice:
```
POST /api/billing/invoices { customer_id, line_items }
```

## Available resources

**Invoice schema**: Field definitions and validation rules → See [INVOICE-SCHEMA.md](INVOICE-SCHEMA.md)
**Payment flows**: State machine and retry logic → See [PAYMENT-FLOWS.md](PAYMENT-FLOWS.md)

## Common tasks

### Generate invoice
Call the invoice service with validated line items.

### Process refund
Requires manager approval for amounts over $500.

## Constraints

- Never modify invoice records directly — use the audit-logged API
- All monetary values in cents (integer), never floating point
````

## Template 4: Tool Integration Skill (with scripts)

Best for: MCP server orchestration, CLI tool wrappers, automation.

```yaml
---
name: gmail-triage
description: Orchestrates Gmail operations via Google Workspace MCP for inbox triage, digest summaries, and reply drafting. Use when the user asks to check email, search inbox, triage messages, summarize unread mail, or draft replies.
---
```

````markdown
# Gmail Triage

Orchestrates Gmail operations via the `google_workspace` MCP server.

## Prerequisites

1. **Google Workspace MCP server** must be configured and running
2. **Config file**: Copy `config.example.yaml` to `config.yaml` and set `user_email`

## Tool reference

| Tool | Purpose |
|------|---------|
| `mcp__google_workspace__search_gmail_messages` | Search with Gmail query syntax |
| `mcp__google_workspace__get_gmail_message_content` | Read full email by message_id |
| `mcp__google_workspace__send_gmail_message` | Send email (requires user approval) |

## Workflow modes

### Digest
Summarize unread emails. Best for morning inbox review.

### Triage
Prioritize inbox into HIGH / MEDIUM / LOW buckets.

### Reply
Draft and send replies with mandatory user approval.

For detailed procedures, read [WORKFLOWS.md](WORKFLOWS.md).

## Degrees of freedom

**Claude MUST follow:**
- NEVER send email without showing draft and getting user approval
- Always use `mcp__` prefixed fully qualified tool names

**Claude decides:**
- Classification criteria for triage buckets
- Summary length based on email complexity

## Safety guardrails

- Never send or forward email without explicit user confirmation
- Never delete emails — only archive or label
- Never modify labels in bulk without listing affected emails first
````

## Template 5: Convention/Standards Skill

Best for: coding standards, project conventions, architectural rules that apply across tasks.

```yaml
---
name: api-response-standards
description: Enforces API response format conventions for all backend endpoints. Activates when writing API handlers, creating endpoints, defining response types, or when the user mentions API responses, error formats, or pagination.
---
```

````markdown
# API Response Standards

Enforces consistent API response format across all backend endpoints.

## Rules

### Always
- Wrap all responses in the standard envelope: `{ success, data?, error?, meta? }`
- Use HTTP status codes correctly (200 success, 400 client error, 500 server error)
- Include pagination metadata for list endpoints: `{ total, page, limit }`

### Never
- Never return raw arrays as top-level response (always wrap in envelope)
- Never include stack traces in production error responses
- Never use 200 status code for error responses

### Prefer
- Prefer `null` over omitting optional fields (explicit over implicit)
- Prefer ISO 8601 for all date/time fields

## Examples

**Good:**
```json
{
  "success": true,
  "data": { "id": "usr_123", "name": "Alice" },
  "meta": { "total": 1, "page": 1, "limit": 20 }
}
```

**Bad:**
```json
[{ "id": "usr_123", "name": "Alice" }]
```

## Degrees of freedom

**Claude MUST follow:**
- All "Always" and "Never" rules above

**Claude decides:**
- Field naming style (camelCase vs snake_case) based on project convention
- Error message verbosity based on endpoint audience (internal vs public)
````

## Template 6: Evaluation Scenarios

Include 2-3 evaluation scenarios with every Skill. Structure:

```json
{
  "skills": ["skill-name"],
  "scenarios": [
    {
      "type": "should_trigger",
      "query": "A query that should activate this Skill",
      "expected_behavior": [
        "Skill activates and reads SKILL.md",
        "Follows the documented workflow",
        "Produces correct output"
      ]
    },
    {
      "type": "should_not_trigger",
      "query": "A query that is similar but should NOT activate this Skill",
      "expected_behavior": [
        "Skill does not activate",
        "Claude handles the query without this Skill"
      ]
    },
    {
      "type": "edge_case",
      "query": "An ambiguous query that tests Skill boundaries",
      "expected_behavior": [
        "Skill activates only if the query is within scope",
        "Claude asks for clarification if ambiguous"
      ]
    }
  ]
}
```

## Choosing a template

| Session produced... | Signal words | Use template |
|-------------------|-------------|-------------|
| A reusable coding pattern or convention | "always", "never", "our standard" | Convention/Standards |
| A multi-step operational process | "steps", "pipeline", "sequence", "deploy" | Workflow |
| Deep domain knowledge with reference material | "schema", "API", "how X works internally" | Domain Knowledge |
| Tool/API integration patterns | "MCP", "CLI", "automate", "integrate" | Tool Integration |
| A simple reusable technique | "pattern", "trick", "shortcut" | Simple |
| Mix of the above | — | Start with the dominant pattern, add files as needed |

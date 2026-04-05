# Shared Contracts

> IMPORTANT: This is the single source of truth for all shared identifiers.
> No agent may invent identifiers not listed here. Only the team lead (/build-feature) may add entries.

## API Contracts

| Endpoint | Method | Request Schema | Response Schema | Used by |
|----------|--------|---------------|-----------------|---------|
| <!-- /api/v1/example --> | <!-- GET --> | <!-- N/A --> | <!-- { data: Example[] } --> | <!-- story-001 --> |

## Component Names

| Component | File Path | Props Interface | Used by |
|-----------|-----------|-----------------|---------|
| <!-- ExampleComponent --> | <!-- src/components/Example.tsx --> | <!-- ExampleProps --> | <!-- story-002 --> |

## Test IDs

| Element | data-testid | Used by |
|---------|-------------|---------|
| <!-- Submit button --> | <!-- example-submit-btn --> | <!-- story-003, story-008 --> |

## Database Schema Changes

| Table | Column | Type | Used by |
|-------|--------|------|---------|
| <!-- users --> | <!-- email --> | <!-- VARCHAR(255) UNIQUE --> | <!-- story-001 --> |

## Shared Types / Interfaces

| Type Name | File | Definition | Used by |
|-----------|------|------------|---------|
| <!-- User --> | <!-- src/types/user.ts --> | <!-- { id: string; email: string } --> | <!-- story-001, story-002 --> |

## Environment Variables

| Variable | Description | Default | Used by |
|----------|-------------|---------|---------|
| <!-- DATABASE_URL --> | <!-- PostgreSQL connection string --> | <!-- N/A --> | <!-- story-001 --> |

---

## Contract Rules

1. **Only the team lead defines contracts.** Teammates and Ralph loops MUST NOT invent new identifiers.
2. **Every shared reference must appear here.** If a test ID, endpoint, component name, or type is used by multiple stories, it must be in this file.
3. **Only define what will exist.** Don't pre-define identifiers "just in case."
4. **Case-sensitive.** `UserCard` and `userCard` are different identifiers.
5. **Update, don't duplicate.** If a contract changes, update the existing row. Don't add a new one.

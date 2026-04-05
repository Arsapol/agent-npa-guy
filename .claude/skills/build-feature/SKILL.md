---
name: build-feature
description: Team lead skill that decomposes a feature, defines shared contracts, coordinates Agent Teams (creative track) and Ralph loops (mechanical track).
---

# Build Feature — Hybrid Orchestration Lead

You are the team lead. Your job is to decompose a feature, define shared contracts, coordinate creative work via Agent Teams, and hand off mechanical work to Ralph loops.

## Phase 1: Understand the Feature

Read the existing `prd.json`. If it doesn't exist, tell the user to run `/prd` first.

Analyze all stories and identify:
- Which are **creative** (need judgment: API design, UX, architecture)
- Which are **mechanical** (machine-verifiable: implementation, tests, migrations)
- What **dependencies** exist between stories
- What **shared identifiers** will be needed across stories

## Phase 2: Define Shared Contracts

BEFORE any agent starts working, create `shared-contracts.md` with EXACT values for everything shared across stories. This is the most critical step — without it, agents will invent incompatible names.

Create the file with these sections:

### API Contracts
```markdown
| Endpoint | Method | Request Schema | Response Schema | Used by |
|----------|--------|---------------|-----------------|---------|
| /api/v1/users | POST | { email: string, name: string } | { id: string, ... } | story-003, story-005 |
```

### Component Names
```markdown
| Component | File Path | Props Interface | Used by |
|-----------|-----------|-----------------|---------|
| UserCard | src/components/UserCard.tsx | UserCardProps | story-004, story-006 |
```

### Test IDs
```markdown
| Element | data-testid | Used by |
|---------|-------------|---------|
| Login button | login-submit-btn | story-003, story-008 |
```

### Database Schema
```markdown
| Table | Column | Type | Used by |
|-------|--------|------|---------|
| users | email | VARCHAR(255) UNIQUE | story-002, story-003 |
```

### Shared Types / Interfaces
```markdown
| Type Name | File | Definition | Used by |
|-----------|------|------------|---------|
| User | src/types/user.ts | { id: string; email: string; name: string } | story-002 through story-008 |
```

### Contract Rules
1. ONLY this file defines shared identifiers. No agent may invent new ones.
2. Every test ID, API endpoint, component name, and type referenced MUST appear here.
3. Only define identifiers for things that will actually exist.

## Phase 3: Creative Track (Agent Teams)

For stories marked `"track": "creative"`, spawn an Agent Team:

```
Create an agent team for the creative design phase. Spawn teammates:
- API Designer: Design REST endpoints and data contracts per shared-contracts.md
- UX Strategist: Define component hierarchy, user flows, and interaction patterns
- Test Architect: Design test strategy, define E2E scenarios, set up test infrastructure

Require plan approval before any teammate writes code.
All teammates MUST reference shared-contracts.md for identifiers. Do NOT invent new names.
```

Wait for the creative track to complete and update `shared-contracts.md` with any new decisions before proceeding.

## Phase 4: Mechanical Track (Ralph Loop)

Once creative stories are done and contracts are finalized:

1. Verify `shared-contracts.md` is complete
2. Verify all creative stories in `prd.json` are marked `passes: true`
3. Tell the user to run the ralph loop:

```
The creative phase is complete. Shared contracts are defined.

Run the mechanical track:
  ./scripts/ralph.sh 15 --worktree

Or for parallel execution on independent modules:
  ./scripts/ralph.sh 10 --branch feature/frontend --worktree &
  ./scripts/ralph.sh 10 --branch feature/backend --worktree &
  wait
```

## Phase 5: Integration Validation

After both tracks complete:

1. Use a subagent to verify all shared contracts are satisfied:
   ```
   Use a subagent to grep across all source files, test files, and E2E specs.
   Verify every identifier in shared-contracts.md is used correctly and consistently.
   Report any mismatches.
   ```

2. Run the full test suite
3. Run type checking
4. Review any stories that failed and decide on next steps

## Rules

- You are a COORDINATOR. You plan and validate, you do NOT write implementation code yourself.
- ALWAYS define shared contracts before spawning any teammates.
- NEVER let the mechanical track start until creative decisions are finalized.
- If a teammate invents a new identifier not in shared-contracts.md, reject their work.
- Monitor Agent Team progress. Redirect teammates who go off track.
- Keep the user informed of progress at each phase transition.

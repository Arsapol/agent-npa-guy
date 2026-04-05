# Hybrid Ralph — Orchestration System

This project uses a hybrid orchestration pattern combining **Agent Teams** (for creative/judgment work) with **Ralph loops** (for autonomous mechanical iteration).

## Architecture

```
/build-feature (team lead skill)
├── Creative Track → Agent Teams (API design, UX, architecture)
├── Mechanical Track → Ralph Loop (implementation, tests, migrations)
└── Shared Contracts → Single source of truth for all identifiers
```

## Available Skills

- `/prd` — Generate a structured PRD with user stories from a feature description
- `/ralph` — Run the autonomous ralph loop for mechanical stories
- `/build-feature` — Full hybrid orchestration: decomposes feature, coordinates both tracks

## Available Subagents

- `ralph-coder` — Implements features following shared contracts
- `ralph-reviewer` — Reviews code for quality, security, and contract compliance
- `ralph-tester` — Writes and validates tests against acceptance criteria
- `ralph-researcher` — Investigates codebases and researches approaches (read-only)

## IMPORTANT Rules

1. **ALWAYS read shared-contracts.md before writing any code.** Never invent identifiers not defined there.
2. **NEVER skip tests.** No `test.skip`, `xit`, `xdescribe`. Treat any skipped test as a failure.
3. **Commit frequently.** After completing each story, commit with message: `feat(story-id): brief description`
4. **One story at a time.** Each iteration focuses on exactly one story from prd.json.
5. **Fresh context per cycle.** The ralph loop gives you clean context. Use progress.txt for continuity.
6. **Contracts before code.** Creative track must complete and finalize shared-contracts.md before mechanical track begins.

## Workflow

1. Run `/prd` to generate prd.json from your feature idea
2. Run `/build-feature` to define contracts and coordinate the creative track
3. Run `./scripts/ralph.sh` to execute the mechanical track autonomously
4. Run `./vault/vault.sh compile` to extract learnings into the knowledge vault

## Quality Gates

Hooks enforce quality automatically:
- **Post-edit**: Lint and typecheck on every file edit
- **Stop gate**: Prevents stopping if tests fail or stories are incomplete
- **Teammate idle**: Ensures work is committed before going idle
- **Task completed**: Rejects completion if skipped tests or debug logs exist

## Knowledge Vault

Learnings accumulate in `progress.txt` across iterations. Periodically run:
- `./vault/vault.sh compile` — Extract rules, patterns, and anti-patterns
- `./vault/vault.sh graduate` — Identify learnings ready for CLAUDE.md
- `./vault/vault.sh query <term>` — Search past learnings

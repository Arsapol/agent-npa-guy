---
name: ralph
description: Run the autonomous ralph loop for mechanical stories. Iterates with fresh context until all tasks pass.
disable-model-invocation: true
---

# Ralph Loop Runner

Run the autonomous iteration loop for mechanical (machine-verifiable) stories.

## Usage

```bash
# Run with defaults (10 iterations)
./scripts/ralph.sh

# Run with custom max iterations
./scripts/ralph.sh 20

# Run in an isolated worktree
./scripts/ralph.sh 15 --worktree

# Run on a specific branch
./scripts/ralph.sh 10 --branch feature/my-feature --worktree
```

## Prerequisites

Before running, ensure:
1. `prd.json` exists in the project root (use `/prd` to generate)
2. `shared-contracts.md` exists with defined contracts (use `/build-feature` to generate)
3. `jq` is installed (`brew install jq`)
4. Claude Code is installed and authenticated

## How It Works

Each iteration:
1. Reads `prd.json` to find the highest-priority incomplete story
2. Spawns a fresh Claude Code instance with `claude -p` (clean context)
3. Passes the story details, shared contracts, and recent learnings
4. Claude implements the story, runs tests, and reports completion
5. Auto-commits changes (safety net for agents that forget to commit)
6. Appends learnings to `progress.txt` for the next iteration
7. Repeats until all stories pass or max iterations reached

## Flags

| Flag | Description |
|------|-------------|
| `--worktree` | Run in an isolated git worktree (recommended for parallel execution) |
| `--branch <name>` | Create/use a specific branch for the work |

## Running Multiple Loops in Parallel

For parallel execution on independent modules:

```bash
# Terminal 1: Frontend stories
./scripts/ralph.sh 10 --branch feature/frontend --worktree &

# Terminal 2: Backend stories
./scripts/ralph.sh 10 --branch feature/backend --worktree &

# Wait for both
wait
```

IMPORTANT: Only parallelize loops that work on completely different files. Never run two loops on overlapping files.

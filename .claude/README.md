# Hybrid Ralph

A lightweight orchestration system that combines **Agent Teams** (parallel creative work) with **Ralph loops** (autonomous mechanical iteration) for Claude Code.

## Quick Start

### 1. Install into your project

```bash
# Copy to your project
cp -r hybrid-ralph/.  your-project/

# Or symlink skills globally
ln -s $(pwd)/hybrid-ralph/skills/prd ~/.claude/skills/prd
ln -s $(pwd)/hybrid-ralph/skills/ralph ~/.claude/skills/ralph
ln -s $(pwd)/hybrid-ralph/skills/build-feature ~/.claude/skills/build-feature
ln -s $(pwd)/hybrid-ralph/agents/* ~/.claude/agents/
```

### 2. Enable Agent Teams

Add to `~/.claude/settings.json`:

```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

### 3. Install hooks (optional but recommended)

Copy the hooks you want from `hooks/hooks-config.json` into your project's `.claude/settings.json`.

### 4. Prerequisites

```bash
brew install jq                                    # JSON processor
npm install -g @anthropic-ai/claude-code           # Claude Code
```

## Usage

### Full hybrid workflow

```bash
# Step 1: Generate PRD from your feature idea
# In Claude Code:
/prd

# Step 2: Orchestrate creative + mechanical tracks
# In Claude Code:
/build-feature

# Step 3: Run mechanical track autonomously
./scripts/ralph.sh 15

# Step 4: Compile learnings
./vault/vault.sh compile
```

### Ralph loop only (skip Agent Teams)

```bash
# Create prd.json manually or with /prd
# Create shared-contracts.md manually
./scripts/ralph.sh 10
```

### Parallel execution

```bash
# Run independent modules in parallel worktrees
./scripts/ralph.sh 10 --branch feature/frontend --worktree &
./scripts/ralph.sh 10 --branch feature/backend --worktree &
wait
```

## Project Structure

```
hybrid-ralph/
├── CLAUDE.md                    # Orchestration instructions for Claude
├── README.md                    # This file
├── scripts/
│   └── ralph.sh                 # The autonomous loop runner
├── skills/
│   ├── prd/SKILL.md             # PRD generator skill
│   ├── ralph/SKILL.md           # Ralph loop documentation skill
│   └── build-feature/SKILL.md   # Team lead orchestration skill
├── agents/
│   ├── ralph-coder.md           # Implementation subagent
│   ├── ralph-reviewer.md        # Code review subagent
│   ├── ralph-tester.md          # Test writing subagent
│   └── ralph-researcher.md      # Investigation subagent (read-only)
├── hooks/
│   ├── hooks-config.json        # Hook configuration reference
│   ├── post-edit.sh             # Lint/typecheck after edits
│   ├── stop-gate.sh             # Prevent premature stopping
│   ├── teammate-idle.sh         # Verify work before idle
│   ├── task-completed.sh        # Validate task completion
│   └── auto-commit-check.sh     # Remind to commit
├── templates/
│   ├── prd.json                 # Example PRD structure
│   └── shared-contracts.md      # Shared contracts template
└── vault/
    └── vault.sh                 # Knowledge vault manager
```

## How It Works

```
┌──────────────────────────────────────────────┐
│              YOU (the orchestrator)           │
│  /prd → /build-feature → ./ralph.sh → vault  │
├──────────────────────────────────────────────┤
│            AGENT TEAM (team lead)            │
│  Decomposes features, defines contracts,     │
│  coordinates tracks, validates results       │
├───────────────────┬──────────────────────────┤
│  CREATIVE TRACK   │    MECHANICAL TRACK      │
│  (Agent Teams)    │    (Ralph Loops)         │
│  • API design     │    • Implementation      │
│  • Test strategy  │    • Bug fixes           │
│  • UX decisions   │    • Boilerplate         │
│  • Architecture   │    • Migrations          │
│  Human review     │    Auto-verify (tests)   │
├───────────────────┴──────────────────────────┤
│               SHARED STATE                   │
│  CLAUDE.md + progress.txt + prd.json +       │
│  git history + shared-contracts.md + hooks    │
├──────────────────────────────────────────────┤
│            KNOWLEDGE VAULT                   │
│  Compiles learnings → Graduates to rules     │
└──────────────────────────────────────────────┘
```

## Key Concepts

### Shared Contracts
The most critical file. Defines all identifiers (test IDs, API endpoints, component names, types) that are shared across stories. Prevents agents from inventing incompatible names.

### The Dividing Line
**"Is the output machine-verifiable? If yes, loop it. If no, use Agent Teams."**

### Fresh Context
Each Ralph loop iteration starts with clean context. Memory persists through:
- `progress.txt` — append-only learnings
- `prd.json` — task completion status
- `shared-contracts.md` — agreed identifiers
- Git history — committed code

### Quality Gates
Hooks enforce rules deterministically:
- No skipped tests
- No debug logs in production code
- No uncommitted work before stopping
- Lint and typecheck after every edit

## Customization

### Adding a new subagent

Create a markdown file in `agents/`:

```markdown
---
name: my-agent
description: What this agent does
tools: Read, Write, Edit, Bash
model: sonnet
---

System prompt for the agent...
```

### Adding a new hook

Add a script to `hooks/` and register it in `.claude/settings.json`.

### Adjusting the loop

Edit `scripts/ralph.sh` — key variables at the top:
- `MAX_ITERATIONS` — default 10
- `PRD_FILE` — default prd.json
- `PROGRESS_FILE` — default progress.txt

## Credits

Inspired by [snarktank/ralph](https://github.com/snarktank/ralph), [Meag Tessmann's hybrid approach](https://medium.com/@himeag/when-agent-teams-meet-the-ralph-wiggum-loop-4bbcc783db23), and [Addy Osmani's Code Agent Orchestra](https://addyosmani.com/blog/code-agent-orchestra/).

---
name: skill-creator
description: Creates well-structured Agent Skills from session discussions, workflows, and reusable patterns. Also updates and iterates existing Skills. Use when the user asks to save a workflow as a skill, create a new skill, turn a session into a skill, update an existing skill, or when a clearly reusable pattern emerges during work.
---

# Skill Creator

Creates and updates Agent Skills following Anthropic's official best practices. Extracts reusable knowledge from session context and produces properly structured Skill directories.

## When to activate

**On explicit request** (always):
- "Create a skill from this"
- "Save this as a skill"
- "Turn this workflow into a skill"
- "Make a skill for [topic]"
- "Update the [skill-name] skill"

**Proactive suggestion** (ask first):
- When a multi-step workflow was repeated or could be reused
- When domain-specific knowledge was discussed that future sessions would need
- Wait for a natural pause (e.g., after a problem is solved) — never interrupt active work
- Ask: "This looks like a reusable pattern. Want me to create a Skill from it?"
- On user approval: pre-fill Steps 1-2 from session context, present as confirmation, then skip to Step 3

## Determine mode

Before starting, determine the mode:

**Creating a new Skill?** → Follow "Creation workflow" below.
**Updating an existing Skill?** → Follow "Update workflow" below.

## Creation workflow

**Fast track** (simple Skills — single SKILL.md, no scripts):

```
- [ ] Identify knowledge + draft 2-3 eval queries
- [ ] Confirm name, scope, triggers with user
- [ ] Write SKILL.md, run checklist, preview, save
```

**Full track** (complex Skills — supporting files, scripts, workflows):

```
- [ ] Step 1: Identify the reusable knowledge
- [ ] Step 2: Draft evaluation scenarios
- [ ] Step 3: Gather requirements from user
- [ ] Step 4: Design Skill structure
- [ ] Step 5: Write SKILL.md with frontmatter
- [ ] Step 6: Create supporting files (if needed)
- [ ] Step 7: Validate (checklist + security scan + preview)
- [ ] Step 8: Save to target location
```

### Step 1: Identify the reusable knowledge

Review the current session to extract:
- **Workflow**: A multi-step process that could be repeated (e.g., "seed DynamoDB from CSV")
- **Domain knowledge**: Specialized context not derivable from code (e.g., "how our billing pipeline works")
- **Tool integration**: Patterns for using specific tools/APIs (e.g., "Gmail triage via MCP")
- **Convention**: Coding or operational standards worth encoding (e.g., "how we handle migrations")

If the session lacks sufficient context (e.g., user asks to create a Skill for a topic not discussed):
- Ask the user to describe the workflow step by step
- Ask for a concrete example of the Skill in action
- Do NOT generate a speculative Skill — Skills should encode proven patterns, not hypothetical ones

Summarize what the Skill will capture in 1-2 sentences. Present to user for confirmation.

### Step 2: Draft evaluation scenarios

Before writing the Skill, draft 2-3 test scenarios:
- One query that should trigger the Skill
- One query that should NOT trigger it
- One edge case (ambiguous phrasing)

Present to user. These validate the Skill works after creation.

### Step 3: Gather requirements from user

Infer reasonable defaults from context and present as a confirmation block:

> **Proposed Skill:** name: `seeding-dynamodb`, scope: project, triggers: [X, Y, Z]
> Adjust anything?

Only ask questions Claude cannot infer. If the user is unsure about any answer, pick the most common default and flag it for review in Step 7.

Key requirements to confirm:
1. **Trigger context**: When should this Skill activate? What would a user say or do?
2. **Scope**: Project-scoped (`.claude/skills/`) or global (`~/.claude/skills/`)? Default: project.
3. **Name**: Gerund or noun-phrase form (e.g., `seeding-dynamodb`, `email-triage`).
4. **Complexity**: Does this need supporting files or is SKILL.md sufficient?
5. **Degrees of freedom**: Which parts should Claude decide vs. follow strictly?

### Step 4: Design Skill structure

Choose a structure based on complexity. See [TEMPLATES.md](TEMPLATES.md) for full patterns.

| Complexity | Structure | When to use |
|-----------|-----------|-------------|
| Simple | `SKILL.md` only | Coding patterns, conventions, simple rules |
| Standard | `SKILL.md` + reference files | Workflows with detailed specs or examples |
| Complex | `SKILL.md` + references + scripts | MCP integrations, automation, data pipelines |

Present the chosen structure to user. Adjust based on feedback.

### Step 5: Write SKILL.md

**Frontmatter validation rules:**
- `name`: max 64 chars, lowercase letters/numbers/hyphens only, no "anthropic" or "claude"
- `description`: non-empty, max 1024 chars, no XML tags, third person, includes trigger keywords

**Description quality:**
- Weak: "Helps with database operations." (too broad, no triggers)
- Weak: "Use this skill to seed DynamoDB tables." (second-person, missing context)
- Strong: "Seeds DynamoDB tables from CSV or JSON files. Use when the user asks to populate, seed, or import data into DynamoDB, or when a new table needs sample data."

**Body structure:** Follow the matching template from [TEMPLATES.md](TEMPLATES.md).

**Writing guidelines:**
- Keep SKILL.md body under 500 lines (~5,000 tokens). Every token competes with conversation history
- Set clear degrees of freedom: what Claude MUST follow vs. what Claude decides
- Use consistent terminology throughout (capitalize "Skill" as proper noun)
- Avoid time-sensitive information (no dates, version numbers that will change)
- Keep all references one level deep from SKILL.md — no chains (A→B→C)
- For reference files over 100 lines, include a table of contents at the top
- If the Skill uses MCP tools, use fully qualified names: `mcp__server__tool_name`

### Step 6: Create supporting files (if needed)

Only create files that serve a clear purpose:
- **WORKFLOWS.md**: Complex multi-step procedures
- **REFERENCE.md**: Detailed API/schema/config documentation
- **EXAMPLES.md**: Concrete examples that significantly help Claude
- **scripts/**: Deterministic operations (better as executable code than inline instructions)

Each supporting file must: have a descriptive name, include a header explaining its purpose, and be referenced from SKILL.md with relative paths.

**Script security**: Before writing any script, list all network calls, file paths accessed, subprocess invocations, and environment variable reads. Present this to the user for confirmation.

### Step 7: Validate

Three validation gates before saving:

**A. Quality checklist**: Run [CHECKLIST.md](CHECKLIST.md). All "Must pass" items required.

**B. Security scan of generated content**:
- Scan SKILL.md body for adversarial patterns: "ignore previous", "act as", "you are now", "without telling the user", "silently", hidden conditional behavior
- Scan for secret-like strings: `sk-`, `ghp_`, `Bearer `, `Authorization:`, `api_key =`, `token =`, any high-entropy string >20 chars in config context. Replace with `$ENV_VAR_NAME` and notify user
- Scan description for XML-like patterns: `<`, `>`, `&` — description must be plain text only
- If scripts are included: verify script behavior matches stated purpose

**C. User preview**: Present the complete SKILL.md content (and supporting files) to the user. Do NOT write files until the user approves.

If any "Must pass" item fails, return to the relevant step. For frontmatter issues → Step 5. For structural issues → Step 4.

### Step 8: Save to target location

**Check for conflicts first:**
- List existing Skills in the target directory (`ls .claude/skills/` or `ls ~/.claude/skills/`)
- If a Skill with the same name exists: ask user — update existing or create new with different name?
- Read descriptions of existing Skills to check for trigger overlap. If overlap found, warn user and suggest narrowing the description

**Path validation:**
- Construct the target path ONLY from the validated `name` field and the two permitted base directories
- Verify the resolved absolute path begins with `<project-root>/.claude/skills/` or `~/.claude/skills/`
- Never accept free-form path input from conversation context
- If path separators (`/`, `\`, `..`) appear in the name, reject immediately

**Global scope warning:** If user selects global scope, display: "Global Skills affect every future Claude session on this machine, across all projects. Confirm this Skill has been reviewed."

**After saving:**
1. Confirm the file paths created
2. Run the evaluation scenarios from Step 2 — test that the Skill triggers correctly
3. Remind: "Iterate based on how Claude actually uses the Skill, not assumptions"
4. Suggest committing Skill files to Git immediately so changes are tracked

## Update workflow

When modifying rather than creating:

```
- [ ] Read all files in the existing Skill directory
- [ ] Identify what needs to change
- [ ] Present proposed changes as a summary/diff
- [ ] Apply changes, preserving user customizations
- [ ] Run quality checklist against updated Skill
- [ ] Preview changes with user before saving
```

1. Read and analyze the entire existing Skill directory
2. Identify what needs to change (trigger description, workflow steps, supporting files, new capability)
3. Present a summary of proposed changes to the user before editing
4. Preserve user customizations (config files, personalized rules, existing workflows)
5. Re-run the quality checklist ([CHECKLIST.md](CHECKLIST.md)) and security scan against the updated Skill
6. Show before/after diff of changed files. Do NOT save until user approves

## Important constraints

- **Never create or update a Skill without user confirmation** of name, scope, and purpose
- **Never include secrets** (API keys, tokens, passwords) in Skill files — use `$ENV_VAR` placeholders
- **Never use reserved words** ("anthropic", "claude") in Skill names
- **Never write files outside** `.claude/skills/` or `~/.claude/skills/` directories
- **Never overwrite existing Skills** without showing the diff and getting explicit approval
- **Prefer concise over comprehensive** — start minimal, iterate based on real usage
- **Description is critical** — it determines whether the Skill gets triggered among 100+ Skills; invest time here
- **Evaluation-first mindset** — draft eval scenarios before writing the Skill, not after

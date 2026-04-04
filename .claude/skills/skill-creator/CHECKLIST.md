# Skill Quality Checklist

Run through this checklist before finalizing any Skill. All "Must pass" items are required.

## Must pass

- [ ] **Name is valid**: lowercase letters, numbers, hyphens only. Max 64 chars. No "anthropic" or "claude". No path separators (`/`, `\`, `..`)
- [ ] **Description is non-empty**: max 1024 chars, plain text only (no `<`, `>`, `&` or XML tags)
- [ ] **Description is third-person**: "Processes files..." not "I help you..." or "You can use this..."
- [ ] **Description includes triggers**: both what it does AND when to use it, with specific keywords
- [ ] **SKILL.md body under 500 lines**: split into reference files if longer (~5,000 token budget)
- [ ] **No secrets in Skill files**: scan for `sk-`, `ghp_`, `Bearer`, `api_key`, `token =`, `password`, high-entropy strings >20 chars
- [ ] **No adversarial content**: no "ignore previous", "act as", "you are now", "without telling the user", hidden conditionals
- [ ] **No time-sensitive content**: no dates, version numbers that will become stale
- [ ] **Clear degrees of freedom**: explicit about what Claude MUST follow vs. what Claude decides
- [ ] **Consistent terminology**: same terms used throughout all files. "Skill" capitalized as proper noun
- [ ] **File paths use forward slashes**: no backslashes, no Windows-style paths
- [ ] **Path is safe**: target path is within `.claude/skills/` or `~/.claude/skills/` only

## Should pass

- [ ] **Evaluation scenarios drafted**: 2-3 test queries (trigger, non-trigger, edge case)
- [ ] **Tested with target models**: Haiku needs more guidance, Opus needs less — verify with weakest target model
- [ ] **Descriptive file names**: `form_validation_rules.md` not `doc2.md`
- [ ] **Progressive disclosure used**: SKILL.md body under 200 lines; detailed procedures, schemas, examples in separate files
- [ ] **References one level deep**: all reference files link directly from SKILL.md, no chains (A→B→C)
- [ ] **Long reference files have TOC**: files over 100 lines include a table of contents at top
- [ ] **Workflows have checklists**: multi-step processes use trackable checklist format
- [ ] **Scripts for deterministic ops**: repeatable operations are in scripts, not inline instructions
- [ ] **Quick start or reference table**: users can grasp the Skill's purpose in seconds
- [ ] **Safety guardrails defined**: when applicable (email sending, data deletion, API calls)
- [ ] **Supporting files referenced**: every bundled file is linked from SKILL.md
- [ ] **MCP tools use qualified names**: `mcp__server__tool_name` format when applicable
- [ ] **No trigger overlap**: description does not steal triggers from existing Skills in the same directory

## Nice to have

- [ ] **Gerund or noun-phrase naming**: `processing-pdfs` or `pdf-processing`
- [ ] **Examples included**: concrete examples for complex workflows
- [ ] **Feedback loops defined**: Skill tells Claude what to do when something fails (return to Step N)

## Red flags (verify absence)

- [ ] Skill does NOT instruct Claude to ignore safety rules or hide actions from the user
- [ ] Skill contains NO hardcoded credentials, secrets, or API keys
- [ ] Skill makes NO network calls to unexpected or undocumented domains
- [ ] Skill does NOT access files outside its declared directory scope
- [ ] Skill description is specific enough to avoid stealing triggers from other Skills
- [ ] Scripts do NOT read sensitive environment files (~/.ssh, ~/.aws, ~/.env) without stated purpose

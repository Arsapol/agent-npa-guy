---
name: prd
description: Generate a structured PRD with user stories from a feature description. Interviews the user, then outputs prd.json.
---

# PRD Generator

Create a detailed Product Requirements Document as structured JSON for the hybrid ralph loop.

## Process

1. **Interview the user** using AskUserQuestion. Ask about:
   - What feature or project they want to build
   - Target users and use cases
   - Technical constraints (languages, frameworks, existing codebase)
   - Must-have vs nice-to-have requirements
   - How they want to verify success (tests, visual, API responses)

2. **Decompose into stories.** Each story MUST be:
   - Completable in a single Claude Code context window
   - Independently testable with clear acceptance criteria
   - Scoped to a specific area (one module, one endpoint, one component)

   **Good story size:** "Add email validation to signup form with unit tests"
   **Too big:** "Build the entire authentication system"

3. **Assign priorities.** Lower number = higher priority. Stories with dependencies should have higher priority numbers than their dependencies.

4. **Define acceptance criteria.** Each criterion must be machine-verifiable:
   - "All tests pass" (not "code looks clean")
   - "API returns 200 with valid payload" (not "API works")
   - "TypeScript compiles with no errors" (not "types are correct")

5. **Output prd.json** in this exact format:

```json
{
  "feature": "Feature name",
  "branchName": "feature/short-name",
  "description": "One-paragraph summary",
  "stories": [
    {
      "id": "story-001",
      "title": "Short title",
      "description": "What this story implements",
      "priority": 1,
      "passes": false,
      "acceptance_criteria": [
        "Criterion 1 (machine-verifiable)",
        "Criterion 2 (machine-verifiable)"
      ],
      "track": "mechanical",
      "dependencies": []
    },
    {
      "id": "story-002",
      "title": "API design decisions",
      "description": "Design the REST API contract for the feature",
      "priority": 1,
      "passes": false,
      "acceptance_criteria": [
        "API contract documented in shared-contracts.md",
        "All endpoints have request/response schemas defined"
      ],
      "track": "creative",
      "dependencies": []
    }
  ]
}
```

## Track Assignment Rules

Assign each story to a track:

- **"mechanical"** — Implementation, bug fixes, migrations, boilerplate. Output is machine-verifiable (tests pass, build succeeds, lint clean). These run in Ralph loops.
- **"creative"** — API design, UX decisions, architecture, documentation, test strategy. Requires judgment and human review. These run in Agent Teams.

## Important

- Stories with `"track": "creative"` should generally come BEFORE their mechanical counterparts (design before implementation).
- Keep story count reasonable: 5-15 stories for a medium feature, 15-30 for a large one.
- NEVER create stories that modify the same file simultaneously — split by file/module ownership.
- Include a final story for integration testing that depends on all other stories.

After generating, save the file as `prd.json` in the project root.

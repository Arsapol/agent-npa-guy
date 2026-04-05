#!/usr/bin/env bash
# =============================================================================
# Knowledge Vault — Compile learnings from progress.txt into structured rules
# Usage: ./vault/vault.sh [command]
# Commands: compile, query <term>, graduate, stats
# =============================================================================
set -euo pipefail

PROGRESS_FILE="progress.txt"
VAULT_DIR="vault"
RULES_FILE="$VAULT_DIR/rules.md"
PATTERNS_FILE="$VAULT_DIR/patterns.md"
ANTI_PATTERNS_FILE="$VAULT_DIR/anti-patterns.md"
INDEX_FILE="$VAULT_DIR/index.md"

mkdir -p "$VAULT_DIR"

# --- Commands ---

compile() {
  echo "Compiling learnings from $PROGRESS_FILE..."

  if [[ ! -f "$PROGRESS_FILE" ]]; then
    echo "No progress.txt found. Nothing to compile."
    exit 0
  fi

  # Use Claude to extract and categorize learnings
  claude -p "$(cat <<PROMPT
Read the file progress.txt and extract all learnings, patterns, and anti-patterns.

Categorize them into three files:

1. vault/rules.md — Firm rules that should always be followed. Format:
   ## Rules
   1. [RULE] Description — discovered in iteration X

2. vault/patterns.md — Useful patterns to follow. Format:
   ## Patterns
   1. [PATTERN] Description — discovered in iteration X

3. vault/anti-patterns.md — Things to avoid. Format:
   ## Anti-Patterns
   1. [AVOID] Description — discovered in iteration X

4. vault/index.md — A searchable index of all learnings with keywords.

Only extract genuinely useful learnings. Skip noise like "completed story X" or "iteration started."
If a learning repeats across iterations, note the frequency — repeated learnings are candidates for CLAUDE.md rules.

Read progress.txt now and create/update all four files.
PROMPT
)" --allowedTools "Read,Write,Edit"

  echo "Vault compiled successfully."
}

query() {
  local term="${1:-}"
  if [[ -z "$term" ]]; then
    echo "Usage: ./vault/vault.sh query <search-term>"
    exit 1
  fi

  echo "Searching vault for: $term"
  echo "---"

  grep -in "$term" "$VAULT_DIR"/*.md 2>/dev/null || echo "No matches found."
}

graduate() {
  echo "Graduating high-frequency learnings to CLAUDE.md recommendations..."

  if [[ ! -f "$RULES_FILE" ]]; then
    echo "No rules.md found. Run 'compile' first."
    exit 1
  fi

  claude -p "$(cat <<PROMPT
Read vault/rules.md, vault/patterns.md, and vault/anti-patterns.md.

Identify any rules or patterns that:
1. Appear 3+ times across iterations
2. Would prevent common mistakes if added to CLAUDE.md
3. Are specific enough to be actionable

Output a recommended addition to CLAUDE.md in this format:

## Graduated Rules (from vault)
[rules here, formatted for CLAUDE.md]

DO NOT modify CLAUDE.md directly. Just output the recommendations.
PROMPT
)" --allowedTools "Read"

  echo ""
  echo "Review the suggestions above and add relevant ones to your CLAUDE.md manually."
}

stats() {
  echo "=== Vault Statistics ==="

  if [[ -f "$PROGRESS_FILE" ]]; then
    local iterations
    iterations=$(grep -c "^## Iteration" "$PROGRESS_FILE" 2>/dev/null || echo "0")
    echo "Total iterations logged: $iterations"
  fi

  for f in "$RULES_FILE" "$PATTERNS_FILE" "$ANTI_PATTERNS_FILE"; do
    if [[ -f "$f" ]]; then
      local count
      count=$(grep -c "^\d\+\." "$f" 2>/dev/null || grep -c "^[0-9]" "$f" 2>/dev/null || echo "0")
      echo "$(basename "$f"): $count entries"
    fi
  done
}

# --- Main ---
COMMAND="${1:-help}"
shift || true

case "$COMMAND" in
  compile)  compile ;;
  query)    query "$@" ;;
  graduate) graduate ;;
  stats)    stats ;;
  *)
    echo "Knowledge Vault"
    echo ""
    echo "Usage: ./vault/vault.sh <command>"
    echo ""
    echo "Commands:"
    echo "  compile    Extract and categorize learnings from progress.txt"
    echo "  query <t>  Search vault for a term"
    echo "  graduate   Identify learnings ready to promote to CLAUDE.md"
    echo "  stats      Show vault statistics"
    ;;
esac

#!/usr/bin/env bash
# Auto-commit check: remind agent to commit after significant bash operations
set -euo pipefail

# Count uncommitted files
CHANGED=$(git diff --name-only 2>/dev/null | wc -l | tr -d ' ')
STAGED=$(git diff --cached --name-only 2>/dev/null | wc -l | tr -d ' ')

TOTAL=$((CHANGED + STAGED))

if [[ "$TOTAL" -gt 5 ]]; then
  echo "You have $TOTAL modified files. Consider committing your progress now to create a checkpoint." >&2
fi

exit 0

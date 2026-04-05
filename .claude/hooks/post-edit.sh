#!/usr/bin/env bash
# Post-edit hook: runs lint/typecheck on edited files
# Exit code 0 = success, 2 = send feedback to agent
set -euo pipefail

FILE_PATH="${1:-}"

if [[ -z "$FILE_PATH" ]]; then
  exit 0
fi

ERRORS=""

# TypeScript/JavaScript
if [[ "$FILE_PATH" == *.ts || "$FILE_PATH" == *.tsx || "$FILE_PATH" == *.js || "$FILE_PATH" == *.jsx ]]; then
  if command -v bunx >/dev/null 2>&1; then
    # Try project-local eslint
    if bunx eslint "$FILE_PATH" --no-error-on-unmatched-pattern 2>/dev/null; then
      : # lint passed
    else
      ERRORS+="ESLint errors in $FILE_PATH. Fix them before proceeding.\n"
    fi
  fi
fi

# Python
if [[ "$FILE_PATH" == *.py ]]; then
  if command -v ruff >/dev/null 2>&1; then
    if ! ruff check "$FILE_PATH" 2>/dev/null; then
      ERRORS+="Ruff errors in $FILE_PATH. Fix them before proceeding.\n"
    fi
  elif command -v flake8 >/dev/null 2>&1; then
    if ! flake8 "$FILE_PATH" 2>/dev/null; then
      ERRORS+="Flake8 errors in $FILE_PATH. Fix them before proceeding.\n"
    fi
  fi
fi

if [[ -n "$ERRORS" ]]; then
  echo -e "$ERRORS" >&2
  exit 2  # Send feedback to agent
fi

exit 0

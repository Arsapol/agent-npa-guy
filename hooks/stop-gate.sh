#!/usr/bin/env bash
# Stop gate hook: prevents agent from stopping if tests haven't passed
# Exit code 0 = allow stop, 2 = reject stop with feedback
set -euo pipefail

# Check if there are uncommitted changes
if ! git diff --quiet 2>/dev/null || ! git diff --cached --quiet 2>/dev/null; then
  echo "You have uncommitted changes. Commit or stash before stopping." >&2
  exit 2
fi

# Check if prd.json exists and has incomplete stories
if [[ -f "prd.json" ]]; then
  remaining=$(jq '[.stories[] | select(.passes != true)] | length' prd.json 2>/dev/null || echo "0")
  if [[ "$remaining" -gt 0 ]]; then
    echo "There are still $remaining incomplete stories in prd.json. Complete them or document why they can't be completed in progress.txt." >&2
    exit 2
  fi
fi

# Try to run tests if a test runner is detected
if [[ -f "package.json" ]] && jq -e '.scripts.test' package.json >/dev/null 2>&1; then
  if ! bun test 2>/dev/null; then
    echo "Tests are failing. Fix them before stopping." >&2
    exit 2
  fi
elif [[ -f "pytest.ini" || -f "pyproject.toml" || -f "setup.cfg" ]]; then
  if command -v pytest >/dev/null 2>&1; then
    if ! pytest --tb=short 2>/dev/null; then
      echo "Tests are failing. Fix them before stopping." >&2
      exit 2
    fi
  fi
fi

exit 0

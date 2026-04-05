#!/usr/bin/env bash
# Teammate idle hook: verify work is done before allowing idle
# Exit code 0 = allow idle, 2 = send feedback and keep working
set -euo pipefail

# Check for uncommitted work
if ! git diff --quiet 2>/dev/null; then
  echo "You have unstaged changes. Commit your work before going idle." >&2
  exit 2
fi

if ! git diff --cached --quiet 2>/dev/null; then
  echo "You have staged but uncommitted changes. Commit before going idle." >&2
  exit 2
fi

exit 0

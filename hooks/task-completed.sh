#!/usr/bin/env bash
# Task completed hook: validate that the task actually passes
# Exit code 0 = allow completion, 2 = reject with feedback
set -euo pipefail

# Ensure no test.skip or xit in test files
SKIPPED_TESTS=$(grep -rn "test\.skip\|xit(\|xdescribe(\|\.skip(" --include="*.test.*" --include="*.spec.*" 2>/dev/null || true)

if [[ -n "$SKIPPED_TESTS" ]]; then
  echo "Found skipped tests — these must be enabled or removed:" >&2
  echo "$SKIPPED_TESTS" >&2
  exit 2
fi

# Ensure no console.log in source files (excluding test files and node_modules)
DEBUG_LOGS=$(grep -rn "console\.log" --include="*.ts" --include="*.tsx" --include="*.js" --include="*.jsx" \
  --exclude-dir=node_modules --exclude-dir=dist --exclude-dir=build \
  --exclude="*.test.*" --exclude="*.spec.*" 2>/dev/null || true)

if [[ -n "$DEBUG_LOGS" ]]; then
  echo "Found console.log statements in source code — remove before marking complete:" >&2
  echo "$DEBUG_LOGS" >&2
  exit 2
fi

exit 0

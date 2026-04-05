#!/usr/bin/env bash
# =============================================================================
# Hybrid Ralph Loop — Autonomous iteration with fresh context per cycle
# Usage: ./scripts/ralph.sh [max_iterations] [--branch <name>] [--worktree]
# =============================================================================
set -euo pipefail

# --- Configuration ---
MAX_ITERATIONS="${1:-10}"
BRANCH_NAME=""
USE_WORKTREE=false
PRD_FILE="${PRD_FILE:-prd.json}"
PROGRESS_FILE="progress.txt"
CONTRACTS_FILE="shared-contracts.md"
VAULT_DIR="vault"

# --- Parse flags ---
shift || true
while [[ $# -gt 0 ]]; do
  case "$1" in
    --branch) BRANCH_NAME="$2"; shift 2 ;;
    --worktree) USE_WORKTREE=true; shift ;;
    *) echo "Unknown flag: $1"; exit 1 ;;
  esac
done

# --- Colors ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# --- Helpers ---
log()  { echo -e "${BLUE}[ralph]${NC} $*"; }
ok()   { echo -e "${GREEN}[ralph]${NC} $*"; }
warn() { echo -e "${YELLOW}[ralph]${NC} $*"; }
err()  { echo -e "${RED}[ralph]${NC} $*"; }

timestamp() { date +"%Y-%m-%d %H:%M:%S"; }

# --- Preflight checks ---
command -v jq >/dev/null 2>&1 || { err "jq is required. Install: brew install jq"; exit 1; }
command -v claude >/dev/null 2>&1 || { err "Claude Code is required. Install: npm install -g @anthropic-ai/claude-code"; exit 1; }

if [[ ! -f "$PRD_FILE" ]]; then
  err "No $PRD_FILE found. Run the /prd skill first to generate one."
  exit 1
fi

# --- Archive previous runs if branch changed ---
archive_if_needed() {
  if [[ -f ".ralph-last-branch" ]]; then
    local last_branch
    last_branch=$(cat .ralph-last-branch)
    if [[ -n "$BRANCH_NAME" && "$last_branch" != "$BRANCH_NAME" ]]; then
      local archive_dir="archive/$(date +%Y-%m-%d)-${last_branch}"
      mkdir -p "$archive_dir"
      [[ -f "$PROGRESS_FILE" ]] && cp "$PROGRESS_FILE" "$archive_dir/"
      [[ -f "$PRD_FILE" ]] && cp "$PRD_FILE" "$archive_dir/"
      [[ -f "$CONTRACTS_FILE" ]] && cp "$CONTRACTS_FILE" "$archive_dir/"
      log "Archived previous run to $archive_dir"
    fi
  fi
  [[ -n "$BRANCH_NAME" ]] && echo "$BRANCH_NAME" > .ralph-last-branch
}

# --- Worktree setup ---
WORK_DIR="."
setup_worktree() {
  if [[ "$USE_WORKTREE" == true ]]; then
    local worktree_path=".ralph-worktrees/$(date +%s)"
    local branch="${BRANCH_NAME:-ralph-$(date +%s)}"
    git worktree add "$worktree_path" -b "$branch" 2>/dev/null || \
      git worktree add "$worktree_path" "$branch" 2>/dev/null || \
      { err "Failed to create worktree"; exit 1; }
    WORK_DIR="$worktree_path"
    log "Working in worktree: $WORK_DIR (branch: $branch)"
    # Copy orchestration files to worktree
    cp "$PRD_FILE" "$WORK_DIR/"
    [[ -f "$PROGRESS_FILE" ]] && cp "$PROGRESS_FILE" "$WORK_DIR/"
    [[ -f "$CONTRACTS_FILE" ]] && cp "$CONTRACTS_FILE" "$WORK_DIR/"
  fi
}

cleanup_worktree() {
  if [[ "$USE_WORKTREE" == true && "$WORK_DIR" != "." ]]; then
    # Copy results back
    cp "$WORK_DIR/$PRD_FILE" ./ 2>/dev/null || true
    cp "$WORK_DIR/$PROGRESS_FILE" ./ 2>/dev/null || true
    git worktree remove "$WORK_DIR" --force 2>/dev/null || true
    log "Cleaned up worktree"
  fi
}
trap cleanup_worktree EXIT

# --- PRD task management ---
count_remaining() {
  jq '[.stories[] | select(.passes != true)] | length' "$WORK_DIR/$PRD_FILE"
}

count_total() {
  jq '[.stories[]] | length' "$WORK_DIR/$PRD_FILE"
}

get_next_story() {
  jq -r '
    [.stories[] | select(.passes != true)]
    | sort_by(.priority // 999)
    | .[0]
    | if . == null then "NONE" else .id end
  ' "$WORK_DIR/$PRD_FILE"
}

get_story_detail() {
  local story_id="$1"
  jq -r --arg id "$story_id" '
    .stories[] | select(.id == $id) |
    "## Story: \(.id)\n**Title:** \(.title)\n**Priority:** \(.priority // "unset")\n**Description:** \(.description)\n**Acceptance Criteria:**\n\(.acceptance_criteria // [] | map("- " + .) | join("\n"))"
  ' "$WORK_DIR/$PRD_FILE"
}

mark_story_complete() {
  local story_id="$1"
  local tmp
  tmp=$(mktemp)
  jq --arg id "$story_id" '
    .stories = [.stories[] | if .id == $id then .passes = true | .completed_at = now else . end]
  ' "$WORK_DIR/$PRD_FILE" > "$tmp" && mv "$tmp" "$WORK_DIR/$PRD_FILE"
}

# --- Knowledge vault ---
append_learning() {
  local iteration="$1"
  local learning="$2"
  echo "" >> "$WORK_DIR/$PROGRESS_FILE"
  echo "## Iteration $iteration — $(timestamp)" >> "$WORK_DIR/$PROGRESS_FILE"
  echo "$learning" >> "$WORK_DIR/$PROGRESS_FILE"
}

# --- Auto-commit safety net ---
auto_commit() {
  local iteration="$1"
  local story_id="$2"
  cd "$WORK_DIR"
  git add -A 2>/dev/null || true
  if ! git diff --cached --quiet 2>/dev/null; then
    git add "$PRD_FILE" "$PROGRESS_FILE" 2>/dev/null || true
    git commit -m "ralph: iteration $iteration — story $story_id [auto-commit]" 2>/dev/null || true
    ok "Auto-committed changes for iteration $iteration"
  fi
  cd - > /dev/null 2>&1 || true
}

# --- Build the prompt for each iteration ---
build_prompt() {
  local story_id="$1"
  local iteration="$2"
  local story_detail
  story_detail=$(get_story_detail "$story_id")
  local remaining
  remaining=$(count_remaining)
  local total
  total=$(count_total)

  local progress_context=""
  if [[ -f "$WORK_DIR/$PROGRESS_FILE" ]]; then
    progress_context=$(tail -60 "$WORK_DIR/$PROGRESS_FILE")
  fi

  local contracts_context=""
  if [[ -f "$WORK_DIR/$CONTRACTS_FILE" ]]; then
    contracts_context=$(cat "$WORK_DIR/$CONTRACTS_FILE")
  fi

  cat <<PROMPT
You are executing iteration $iteration of an autonomous development loop.
Progress: $((total - remaining)) of $total stories complete. $remaining remaining.

$story_detail

## Rules (MUST follow — numbered for clarity)
1. Implement ONLY this one story. Do NOT touch other stories.
2. Do NOT mark the story as done unless ALL acceptance criteria pass.
3. Run ALL tests and type checks after implementation.
4. If tests fail, fix the root cause. Do NOT skip tests or add test.skip.
5. If you cannot complete the story, document WHY in progress.txt and move on.
6. Do NOT invent new identifiers, test IDs, or API names. Use ONLY what is defined in shared-contracts.md.
7. After completing work, append a brief summary of what you did and any learnings to progress.txt.

## Shared Contracts
$contracts_context

## Recent Learnings (from previous iterations)
$progress_context

## Completion
When the story passes all acceptance criteria and tests:
1. Update prd.json: set "passes": true for story "$story_id"
2. Append learnings to progress.txt
3. Output: <promise>STORY_COMPLETE:$story_id</promise>

If ALL stories are done, output: <promise>COMPLETE</promise>
PROMPT
}

# --- Main loop ---
main() {
  archive_if_needed
  setup_worktree

  [[ ! -f "$WORK_DIR/$PROGRESS_FILE" ]] && echo "# Ralph Progress Log" > "$WORK_DIR/$PROGRESS_FILE"

  local remaining
  remaining=$(count_remaining)
  local total
  total=$(count_total)

  log "Starting hybrid ralph loop"
  log "PRD: $total stories, $remaining remaining"
  log "Max iterations: $MAX_ITERATIONS"
  echo ""

  for (( i=1; i<=MAX_ITERATIONS; i++ )); do
    remaining=$(count_remaining)

    if [[ "$remaining" -eq 0 ]]; then
      echo ""
      ok "================================================"
      ok "  ALL STORIES COMPLETE! ($total/$total)"
      ok "================================================"
      exit 0
    fi

    local story_id
    story_id=$(get_next_story)

    if [[ "$story_id" == "NONE" ]]; then
      ok "No more stories to process."
      exit 0
    fi

    echo ""
    log "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    log "  Iteration $i/$MAX_ITERATIONS — Story: $story_id"
    log "  Remaining: $remaining/$total"
    log "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    local prompt
    prompt=$(build_prompt "$story_id" "$i")

    # Run Claude Code with fresh context
    local output
    output=$(cd "$WORK_DIR" && claude -p "$prompt" \
      --permission-mode auto \
      --verbose 2>&1) || true

    # Check if story was completed
    if echo "$output" | grep -q "<promise>STORY_COMPLETE:$story_id</promise>"; then
      mark_story_complete "$story_id"
      ok "Story $story_id completed!"
    elif echo "$output" | grep -q "<promise>COMPLETE</promise>"; then
      ok "All stories marked complete by agent!"
      exit 0
    else
      warn "Story $story_id not completed in this iteration. Will retry."
      append_learning "$i" "Story $story_id: incomplete — agent did not confirm completion."
    fi

    # Auto-commit safety net
    auto_commit "$i" "$story_id"

    # Brief pause between iterations
    sleep 2
  done

  remaining=$(count_remaining)
  if [[ "$remaining" -gt 0 ]]; then
    warn "Reached max iterations ($MAX_ITERATIONS). $remaining stories still remaining."
    exit 1
  fi
}

main

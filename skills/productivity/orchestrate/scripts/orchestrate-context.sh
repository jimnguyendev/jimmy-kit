#!/usr/bin/env bash
# orchestrate-context.sh snapshot|resume — keep an orchestrate root alive across context compaction.
#
#   snapshot  (Claude Code PreCompact hook)            write <repo>/.orchestrate/AUTO-STATE.md from
#                                                     git, worktree and process state
#   resume    (SessionStart hook, matcher "compact")  print HANDOFF.md, AUTO-STATE.md and SPRINT.md
#                                                     into the new context
#
# The target repo is the session cwd when it has .orchestrate/SPRINT.md; otherwise the first line
# "<session cwd> <repo path>" (either may contain spaces) in $ORCH_TARGETS (default ~/.claude/orchestrate-targets) whose first
# field equals the cwd. No repo found: exit 0 with no output, so the hook is safe in every session.
#
# Environment: ORCH_TARGETS (mapping file) · ORCH_PS_PATTERN (extended regex of executor processes
# to list; default covers opencode, claude -p, codex exec and browsers started with a CDP port).
set -u

mode="${1:-}"
case "$mode" in
  snapshot|resume) ;;
  *) echo "usage: $0 snapshot|resume" >&2; exit 2 ;;
esac

input="$(cat 2>/dev/null || true)"
field() { printf '%s' "$input" | python3 -c 'import json,sys
try:
    d=json.load(sys.stdin)
except ValueError:
    d={}
for k in sys.argv[1:]:
    v=d.get(k) if isinstance(d,dict) else None
    if v:
        print(v); break' "$@" 2>/dev/null; }
cwd="$(field cwd)"
[ -n "$cwd" ] || cwd="${CLAUDE_PROJECT_DIR:-$PWD}"
trigger="$(field trigger source)"
trigger="${trigger:-unknown}"

targets="${ORCH_TARGETS:-$HOME/.claude/orchestrate-targets}"
repo=""
if [ -f "$cwd/.orchestrate/SPRINT.md" ]; then
  repo="$cwd"
elif [ -f "$targets" ]; then
  # "<cwd> <repo>": match the whole cwd prefix and keep the rest, so both may contain spaces
  repo="$(awk -v c="$cwd" 'index($0, c " ") == 1 { print substr($0, length(c) + 2); exit }' "$targets")"
  case "$repo" in "~"|"~/"*) repo="$HOME${repo#\~}" ;; esac
fi
[ -n "$repo" ] && [ -f "$repo/.orchestrate/SPRINT.md" ] || exit 0
state="$repo/.orchestrate"
# Default branch: origin/HEAD, else the main checkout's branch, else main.
main="$(git -C "$repo" symbolic-ref --short -q refs/remotes/origin/HEAD 2>/dev/null || true)"
main="${main#origin/}"
[ -n "$main" ] || main="$(git -C "$repo" symbolic-ref --short -q HEAD 2>/dev/null || true)"
main="${main:-main}"
pattern="${ORCH_PS_PATTERN:-opencode[0-9]*(\.exe)? run|claude -p|codex exec|remote-debugging-port}"

snapshot() {
  local out="$state/AUTO-STATE.md" tmp
  tmp="$(mktemp)"
  {
    echo "# AUTO-STATE (written by the PreCompact hook, $(date '+%Y-%m-%d %H:%M:%S'), trigger: $trigger)"
    echo
    echo "Machine-derived. HANDOFF.md is the curated plan; this file is what git and ps say right now."
    echo
    echo "## $main (last 12 commits)"
    echo '```'
    git -C "$repo" log --oneline -12 "$main" 2>&1
    echo '```'
    echo
    echo "## Main checkout status"
    echo '```'
    git -C "$repo" status --short --branch 2>&1 | head -30
    echo '```'
    echo
    echo "## Worktrees (branch, commits ahead of $main, uncommitted files)"
    echo '```'
    git -C "$repo" worktree list --porcelain 2>/dev/null | awk '/^worktree /{print substr($0, 10)}' |
      while IFS= read -r wt; do
        [ "$wt" = "$repo" ] && continue
        br="$(git -C "$wt" rev-parse --abbrev-ref HEAD 2>/dev/null)"
        ahead="$(git -C "$wt" rev-list --count "$main..HEAD" 2>/dev/null)"
        dirty="$(git -C "$wt" status --porcelain 2>/dev/null | wc -l | tr -d ' ')"
        last="$(git -C "$wt" log -1 --format='%cr: %s' 2>/dev/null)"
        echo "$wt  [$br] ahead=$ahead dirty=$dirty  last=($last)"
      done
    echo '```'
    echo
    echo "## Executor processes still running"
    echo '```'
    ps -axo pid,etime,command 2>/dev/null | grep -E "$pattern" | grep -v -e 'grep -E' -e Helper | cut -c1-200 | head -20
    echo '```'
    echo
    echo "## Executor logs (last 5 lines each, changed in the last 6 h)"
    find "$state" -maxdepth 1 -name '*.log' -mmin -360 2>/dev/null | while IFS= read -r log; do
      echo "### $(basename "$log")"
      echo '```'
      tail -5 "$log" | cut -c1-200
      echo '```'
    done
  } >"$tmp"
  mv "$tmp" "$out"
}

resume() {
  echo "Context was just compacted. Orchestration state for $repo is below."
  echo "Resume on your own: do not ask the user. Check the background agents and shells named in the"
  echo "conversation summary, then continue the 'Next' list in HANDOFF.md. Refresh HANDOFF.md after every land."
  echo "Read LEARNINGS.md and packets/ only when a step needs them."
  echo "Your first message to the owner after this follows /ketchup: how many decisions wait on them, what"
  echo "happened since their last message, then one decision brief per item in 'Waiting on owner'."
  for f in HANDOFF.md AUTO-STATE.md SPRINT.md; do
    [ -f "$state/$f" ] || continue
    echo
    echo "===== $state/$f ====="
    head -c 6000 "$state/$f"
  done
}

"$mode"

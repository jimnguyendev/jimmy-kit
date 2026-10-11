#!/usr/bin/env bash
# advisor-review.sh <brief.md> [output.md] — one read-only Advisor round on a plan or design brief.
#
# The Advisor seat is "an independent reviewer that reads the repo", not one product. Routes are
# tried in this order and the first one installed answers:
#
#   1. codex     Codex CLI, read-only sandbox (different model family from a Claude root)
#   2. opencode  opencode `run --agent plan` (read-only agent) with $ADVISOR_OPENCODE_MODEL
#   3. none      exit 3: the root runs the same-family fallback itself (a fresh general-purpose
#                subagent per round) and writes "same-family" in the plan's Advisor line
#
# The prompt always carries the state-machine checklist (references/state-machine-review.md);
# the Advisor answers each SM item when the plan touches leases, retries, locks, idempotency or
# outbound calls, else writes "SM: N/A — <reason>" once.
#
# Output file: first line PLAN_APPROVED or PLAN_REVISE, findings with stable IDs (A1, A2, ...),
# last line `Advisor-Route: <route>`. Stdout: one line with the verdict, route and output path.
#
# Exit: 0 verdict written · 2 usage · 3 no external route answered (each route's reason is printed)
# · 4 the route answered without a verdict line (output kept for reading).
#
# A route that is installed but fails (not logged in, quota, network) falls through to the next one;
# its stderr is kept in <output>.route.log.
#
# Environment:
#   ADVISOR_ROUTE           auto (default) | codex | opencode — try only that route
#   CODEX_BIN               Codex CLI (default: codex on PATH, then $ADVISOR_CODEX_APP, the ChatGPT
#                           desktop bundle)
#   ADVISOR_MODEL           codex model override; ADVISOR_EFFORT codex reasoning effort
#   OPENCODE_BIN            opencode CLI (default: opencode2, then opencode on PATH)
#   ADVISOR_OPENCODE_MODEL  provider/model for the opencode route (default: "advisor.opencode_model",
#                           then "opencode_model" in <repo>/.claude/orchestrator.json); unset skips it
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
brief="${1:-}"
[ -n "$brief" ] && [ -f "$brief" ] || { echo "usage: advisor-review.sh <brief.md> [output.md]" >&2; exit 2; }
brief="$(cd "$(dirname "$brief")" && pwd)/$(basename "$brief")"
out="${2:-${brief%.md}.advisor.md}"
repo="$(git -C "$(dirname "$brief")" rev-parse --show-toplevel 2>/dev/null || pwd)"
checklist="$here/../references/state-machine-review.md"

find_codex() {
  if [ -n "${CODEX_BIN:-}" ]; then echo "$CODEX_BIN"; return; fi
  command -v codex 2>/dev/null && return
  local app="${ADVISOR_CODEX_APP:-/Applications/ChatGPT.app/Contents/Resources/codex-cli/CodexCLI.app/Contents/MacOS/codex}"
  [ -x "$app" ] && echo "$app"
  return 0
}
find_opencode() {
  if [ -n "${OPENCODE_BIN:-}" ]; then echo "$OPENCODE_BIN"; return; fi
  command -v opencode2 2>/dev/null || command -v opencode 2>/dev/null || true
}
opencode_model() {
  if [ -n "${ADVISOR_OPENCODE_MODEL:-}" ]; then echo "$ADVISOR_OPENCODE_MODEL"; return; fi
  local cfg="$repo/.claude/orchestrator.json"
  [ -f "$cfg" ] || return 0
  python3 -c 'import json,sys
d=json.load(open(sys.argv[1]))
a=d.get("advisor") if isinstance(d.get("advisor"),dict) else {}
print(a.get("opencode_model") or d.get("opencode_model") or "")' "$cfg" 2>/dev/null || true
}

prompt="You are the Advisor: an independent senior reviewer, read-only. Review the brief below against
this repository (AGENTS.md is the authority; landed code counts). Push back on wrong premises,
missing evidence, scope creep and risky seams. No praise.
Output: first line exactly PLAN_APPROVED or PLAN_REVISE, then numbered findings with stable IDs
(A1, A2, ...), each with severity (high/med/low), the concrete problem, evidence (file:line) and a
concrete alternative. If the brief carries a ledger from an earlier round, mark each earlier
finding ACCEPTED or STILL_OPEN.
When the plan touches leases, retries, locks, idempotency, queues or outbound calls, answer every
item of the checklist below as SM-n PASS | FINDING <id> | N/A <reason>. Otherwise write
'SM: N/A — <reason>' once.

$( [ -f "$checklist" ] && cat "$checklist" )

===== BRIEF =====
$(cat "$brief")"

run_codex() {
  local bin="$1"
  local args=(exec -s read-only --skip-git-repo-check -C "$repo" -o "$out")
  [ -n "${ADVISOR_MODEL:-}" ] && args+=(-m "$ADVISOR_MODEL")
  [ -n "${ADVISOR_EFFORT:-}" ] && args+=(-c "model_reasoning_effort=\"$ADVISOR_EFFORT\"")
  "$bin" "${args[@]}" "$prompt" </dev/null >/dev/null 2>"$out.route.log"
}
run_opencode() {
  local bin="$1" model="$2"
  # The plan agent cannot edit files; without --auto, permission asks are rejected, not granted.
  (cd "$repo" && "$bin" run -m "$model" --agent plan "$prompt" </dev/null) >"$out" 2>"$out.route.log"
}

route="${ADVISOR_ROUTE:-auto}"
case "$route" in auto|codex|opencode) ;; *) echo "advisor-review: unknown ADVISOR_ROUTE=$route (auto | codex | opencode)" >&2; exit 2 ;; esac
used=""; tried=()
# An installed route that fails (not logged in, quota, network) falls through to the next one.
if [ "$route" != opencode ]; then
  bin="$(find_codex)"
  if [ -z "$bin" ]; then tried+=("codex: not installed")
  elif run_codex "$bin"; then used="codex"
  else tried+=("codex: failed (exit $?), see $out.route.log"); fi
fi
if [ -z "$used" ] && [ "$route" != codex ]; then
  bin="$(find_opencode)"; model="$(opencode_model)"
  if [ -z "$bin" ]; then tried+=("opencode: not installed")
  elif [ -z "$model" ]; then tried+=("opencode: no ADVISOR_OPENCODE_MODEL or opencode_model in .claude/orchestrator.json")
  elif run_opencode "$bin" "$model"; then used="opencode:$model"
  else tried+=("opencode:$model: failed (exit $?), see $out.route.log"); fi
fi
if [ -z "$used" ]; then
  {
    echo "advisor-review: no external Advisor answered:"
    printf '  - %s\n' "${tried[@]}"
    cat <<EOF
Same-family fallback: spawn a fresh general-purpose subagent for this round with skills
engineering-design-thinking (Review mode) and codebase-design, give it this prompt and the brief
$brief, and record "Advisor: same-family subagent (no external route)" in the plan header and ledger.
EOF
  } >&2
  exit 3
fi

# Keep the answer from the verdict line on: some CLIs echo preamble before it.
if ! python3 - "$out" <<'PY'
import re, sys
p = sys.argv[1]
lines = open(p, encoding="utf-8", errors="replace").read().splitlines()
for i, line in enumerate(lines):
    if re.match(r"^\s*\**(PLAN_APPROVED|PLAN_REVISE)\b", line):
        open(p, "w", encoding="utf-8").write("\n".join(lines[i:]).rstrip() + "\n")
        sys.exit(0)
sys.exit(1)
PY
then
  printf '\nAdvisor-Route: %s\n' "$used" >>"$out"
  echo "advisor-review: $used answered without a PLAN_APPROVED/PLAN_REVISE line; read $out" >&2
  exit 4
fi
printf '\nAdvisor-Route: %s\n' "$used" >>"$out"
echo "advisor-review: $(head -1 "$out" | tr -d '*' | awk '{print $1}') via $used → $out"

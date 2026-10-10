#!/usr/bin/env bash
# gates.sh <worktree> [gate-file] — run every gate a packet must pass before it lands.
#
# The gate file lists one gate per line as `name: command` (blank lines and `#` comments
# are ignored). Each command runs with `bash -c` from the worktree root, so a gate for a
# sub-project is written `fe-lint: cd web && pnpm -s lint`. Default gate file:
# <main checkout>/.orchestrate/gates, or $ORCH_GATES_FILE.
#
# Prints one line per gate (`ok   name` / `FAIL name (see log)`), stops at the first
# failure. Logs: ${TMPDIR:-/tmp}/gates-<worktree name>/<gate>.log.
# Exit: 0 all gates ok · 1 a gate failed · 2 usage error, missing or empty gate file.
set -uo pipefail

wt="${1:-}"
[ -n "$wt" ] && [ -d "$wt" ] || { echo "usage: gates.sh <worktree> [gate-file]" >&2; exit 2; }
wt="$(cd "$wt" && pwd)"

common="$(git -C "$wt" rev-parse --path-format=absolute --git-common-dir 2>/dev/null)" ||
  { echo "gates: $wt is not a git checkout" >&2; exit 2; }
main_checkout="$(dirname "$common")"
gate_file="${2:-${ORCH_GATES_FILE:-$main_checkout/.orchestrate/gates}}"
[ -f "$gate_file" ] || { echo "gates: no gate file at $gate_file" >&2; exit 2; }

logs="${TMPDIR:-/tmp}"
logs="${logs%/}/gates-$(basename "$wt")"
mkdir -p "$logs"

count=0
while IFS= read -r line || [ -n "$line" ]; do
  case "$line" in ''|'#'*) continue ;; *:*) ;; *) echo "gates: malformed line in $gate_file: $line" >&2; exit 2 ;; esac
  name="${line%%:*}"
  cmd="${line#*:}"
  name="$(printf '%s' "$name" | tr -d '[:space:]')"
  cmd="${cmd#"${cmd%%[![:space:]]*}"}"
  if ! printf '%s' "$name" | grep -qE '^[A-Za-z0-9._-]+$' || [ -z "$cmd" ]; then
    echo "gates: malformed line in $gate_file: $line" >&2; exit 2
  fi
  count=$((count + 1))
  if (cd "$wt" && bash -c "$cmd") >"$logs/$name.log" 2>&1 </dev/null; then
    echo "ok   $name"
  else
    echo "FAIL $name (see $logs/$name.log)"
    exit 1
  fi
done <"$gate_file"

[ "$count" -gt 0 ] || { echo "gates: $gate_file lists no gates" >&2; exit 2; }
echo "gates: all $count ok"

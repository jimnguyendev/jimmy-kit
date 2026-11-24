#!/usr/bin/env bash
# gates.sh [--base <ref>] <worktree> [gate-file] — run every gate a packet must pass before it lands.
#
# The gate file lists one gate per line as `name: command` (blank lines and `#` comments
# are ignored). Each command runs with `bash -c` from the worktree root, so a gate for a
# sub-project is written `fe-lint: cd web && pnpm -s lint`. Default gate file:
# <main checkout>/.orchestrate/gates, or $ORCH_GATES_FILE.
#
# A line may limit itself to paths: `name @glob[,glob...]: command`. With --base <ref> (or
# ORCH_GATES_BASE), a limited gate runs only when `git diff --name-only <ref>...HEAD` has a path
# matching one of its globs (`*` stays inside a directory, `**` crosses directories) and otherwise
# prints `SKIP name: no changed path matches <globs>`. A line without `@` always runs, and without a
# base every gate runs. ORCH_GATES_ALL=1 runs everything.
#
# Prints one line per gate (`ok   name` / `FAIL name (see log)`), stops at the first
# failure. Logs: ${TMPDIR:-/tmp}/gates-<worktree name>/<gate>.log.
# Exit: 0 all gates ok · 1 a gate failed · 2 usage error, missing or empty gate file.
set -uo pipefail

base="${ORCH_GATES_BASE:-}"
pos=()
while [ $# -gt 0 ]; do
  case "$1" in
    --base) [ $# -ge 2 ] || { echo "usage: gates.sh [--base <ref>] <worktree> [gate-file]" >&2; exit 2; }; base="$2"; shift 2 ;;
    *) pos+=("$1"); shift ;;
  esac
done
[ "${ORCH_GATES_ALL:-}" != 1 ] || base=""
wt="${pos[0]:-}"
[ -n "$wt" ] && [ -d "$wt" ] || { echo "usage: gates.sh [--base <ref>] <worktree> [gate-file]" >&2; exit 2; }
wt="$(cd "$wt" && pwd)"

common="$(git -C "$wt" rev-parse --path-format=absolute --git-common-dir 2>/dev/null)" ||
  { echo "gates: $wt is not a git checkout" >&2; exit 2; }
main_checkout="$(dirname "$common")"
gate_file="${pos[1]:-${ORCH_GATES_FILE:-$main_checkout/.orchestrate/gates}}"
[ -f "$gate_file" ] || { echo "gates: no gate file at $gate_file" >&2; exit 2; }

logs="${TMPDIR:-/tmp}"
logs="${logs%/}/gates-$(basename "$wt")"
mkdir -p "$logs"

changed=""
if [ -n "$base" ]; then
  if ! changed="$(git -C "$wt" diff --name-only "$base...HEAD" 2>/dev/null)"; then
    echo "gates: cannot diff against $base; running every gate" >&2
    base=""
  fi
fi

matches() { # matches <globs, comma separated>: does a changed path match one of them
  printf '%s\n' "$changed" | python3 -c 'import re,sys
def rx(g):
    out,i="",0
    while i<len(g):
        if g.startswith("**/",i): out+="(?:.*/)?"; i+=3
        elif g.startswith("**",i): out+=".*"; i+=2
        elif g[i]=="*": out+="[^/]*"; i+=1
        elif g[i]=="?": out+="[^/]"; i+=1
        else: out+=re.escape(g[i]); i+=1
    return re.compile(out+"$")
pats=[rx(g) for g in sys.argv[1].split(",") if g]
sys.exit(0 if any(p.match(l) for l in sys.stdin.read().splitlines() for p in pats) else 1)' "$1"
}

count=0
skipped=0
ran_names=""
skipped_names=""
while IFS= read -r line || [ -n "$line" ]; do
  case "$line" in ''|'#'*) continue ;; *:*) ;; *) echo "gates: malformed line in $gate_file: $line" >&2; exit 2 ;; esac
  name="${line%%:*}"
  cmd="${line#*:}"
  globs=""
  has_at=0
  case "$name" in *@*) has_at=1; globs="$(printf '%s' "${name#*@}" | tr -d '[:space:]')"; name="${name%%@*}" ;; esac
  name="$(printf '%s' "$name" | tr -d '[:space:]')"
  cmd="${cmd#"${cmd%%[![:space:]]*}"}"
  if ! printf '%s' "$name" | grep -qE '^[A-Za-z0-9._-]+$' || [ -z "$cmd" ] ||
     { [ "$has_at" = 1 ] && [ -z "$globs" ]; }; then
    echo "gates: malformed line in $gate_file: $line" >&2; exit 2
  fi
  count=$((count + 1))
  if [ -n "$base" ] && [ -n "$globs" ] && ! matches "$globs"; then
    echo "SKIP $name: no changed path matches $globs"
    skipped=$((skipped + 1)); skipped_names="$skipped_names $name"
    continue
  fi
  ran_names="$ran_names $name"
  if (cd "$wt" && bash -c "$cmd") >"$logs/$name.log" 2>&1 </dev/null; then
    echo "ok   $name"
  else
    echo "FAIL $name (see $logs/$name.log)"
    exit 1
  fi
done <"$gate_file"

[ "$count" -gt 0 ] || { echo "gates: $gate_file lists no gates" >&2; exit 2; }
if [ "$skipped" -eq 0 ]; then
  echo "gates: all $count ok"
else
  echo "gates: $((count - skipped)) ran (${ran_names# }), $skipped skipped (${skipped_names# })"
fi

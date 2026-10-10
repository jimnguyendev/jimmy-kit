#!/usr/bin/env bash
# reality-gate audit — measures how much of a test suite can disagree with reality.
#
# Usage: audit.sh [repo-root] [--probe]
#   --probe  additionally runs ONE integration-tagged Go package with -v to detect
#            the silent-skip pattern (needs the go toolchain; safe when Docker is down).
#
# Portable: no repo-specific paths. Go-focused counts; non-Go repos get the generic
# section only. Extend at the "STACK-SPECIFIC" block for PHPUnit/Jest/Vitest/etc.
#
# Mechanisms 1-10 are named in SKILL.md section 2.
# Verdict legend: RED = mechanism present, AMBER = suspicious, GREEN = no signal.
# Counts are heuristics; confirm every RED by opening the cited files.

set -uo pipefail

ROOT="."
PROBE=0
for arg in "$@"; do
  case "$arg" in
    --probe) PROBE=1 ;;
    *) ROOT="$arg" ;;
  esac
done
cd "$ROOT" || { echo "cannot cd to $ROOT" >&2; exit 2; }

if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  files() { git ls-files -z -- "$@" 2>/dev/null | tr '\0' '\n'; }
else
  files() { find . -type f \( -path './.git' -prune -o -print \) 2>/dev/null | sed 's#^\./##' ; }
fi

ALL="$(files)"
count() { printf '%s\n' "$1" | grep -cE "$2" 2>/dev/null || true; }
grepc() { # grepc <regex> <file-list>   -> total matching lines across files
  local re="$1"; shift
  [ -z "$*" ] && { echo 0; return; }
  printf '%s\n' "$@" | xargs grep -hE -- "$re" 2>/dev/null | wc -l | tr -d ' '
}
grepl() { # grepl <regex> <file-list>   -> files containing regex
  local re="$1"; shift
  [ -z "$*" ] && return
  printf '%s\n' "$@" | xargs grep -lE -- "$re" 2>/dev/null
}
verdict() { printf '  %-6s %s\n' "$1" "$2"; }

echo "reality-gate audit — $(pwd)"
echo

# ---------------------------------------------------------------- generic ----
echo "## Generic"
DOCKER=no; docker info >/dev/null 2>&1 && DOCKER=yes
echo "  docker reachable now: $DOCKER"

REPLAY_DIRS="$(printf '%s\n' "$ALL" | grep -iE '(^|/)(scripts|tools|test|tests|e2e)/(certify|replay|smoke|e2e|contract)[^/]*/' | cut -d/ -f1-3 | sort -u)"
if [ -n "$REPLAY_DIRS" ]; then verdict GREEN "tracked replay/smoke suite: $(echo "$REPLAY_DIRS" | tr '\n' ' ')"; else verdict RED "no tracked replay/certify/smoke suite directory (mechanism 4)"; fi

if [ -f .env.example ] || [ -f .env.sample ]; then
  EX="$(cat .env.example .env.sample 2>/dev/null | grep -cE '^[A-Z][A-Z0-9_]+=' )"
  echo "  .env.example keys: $EX"
else
  verdict AMBER "no .env.example (mechanism 5)"
fi

# Developer environment reaching the tests (mechanism 9)
TEST_SETUP="$(printf '%s\n' "$ALL" | grep -E '(_test\.go|\.(test|spec)\.[jt]sx?|setupTests\.[jt]s|(vitest|jest)\.setup\.[jt]s|conftest\.py|_test\.py)$|(^|/)(testsupport|testutil|testhelpers?|harness)[^/]*/.*\.(go|[jt]s|py)$')"
# shellcheck disable=SC2086
CLEARS_ENV="$(grepl '\.env\.example' $TEST_SETUP | head -3 | tr '\n' ' ')"
for runner in Makefile makefile GNUmakefile; do
  [ -f "$runner" ] || continue
  if grep -qE '^[[:space:]]*-?include[[:space:]]+[^[:space:]]*\.env' "$runner" &&
     grep -qE '^[[:space:]]*export([[:space:]]*$|[[:space:]]+[A-Za-z_])' "$runner"; then
    if [ -n "$CLEARS_ENV" ]; then
      verdict AMBER "$runner includes .env and exports it; test harness mentions .env.example ($CLEARS_ENV) — confirm it clears every key (mechanism 9)"
    else
      verdict RED "$runner includes .env and exports it to every recipe, tests included; no harness clears the keys (mechanism 9)"
    fi
  fi
  break  # case-insensitive filesystems match every spelling
done
for runner in Justfile justfile; do
  [ -f "$runner" ] || continue
  grep -qE '^[[:space:]]*set[[:space:]]+dotenv-load' "$runner" && verdict AMBER "$runner loads .env into every recipe (mechanism 9)"
  break
done
# shellcheck disable=SC2086
DOTENV_TESTS="$(grepl 'godotenv\.(Load|Overload)|dotenv/config|dotenv\.config\(|load_dotenv\(' $TEST_SETUP | head -3 | tr '\n' ' ')"
[ -n "$DOTENV_TESTS" ] && verdict AMBER "test setup loads a dotenv file, so the developer's values reach the suite (mechanism 9): $DOTENV_TESTS"

REPORT_SCRIPTS="$(printf '%s\n' "$ALL" | grep -iE '(report|handoff|audit).*\.md$' | xargs grep -hoE '\b[a-zA-Z0-9_-]+\.(py|sh)\b' 2>/dev/null | sort -u)"
MISSING=""
for s in $REPORT_SCRIPTS; do printf '%s\n' "$ALL" | grep -qE "(^|/)$s$" || MISSING="$MISSING $s"; done
[ -n "$MISSING" ] && verdict RED "scripts named in reports/handoffs but absent from git:$MISSING (mechanism 4)"

# ------------------------------------------------------------------- go ----
if [ -f go.mod ]; then
  echo
  echo "## Go"
  TESTS="$(printf '%s\n' "$ALL" | grep -E '_test\.go$')"
  SRC="$(printf '%s\n' "$ALL" | grep -E '\.go$' | grep -vE '_test\.go$')"
  # shellcheck disable=SC2086
  INTEG="$(grepl '^//go:build integration( |$)|^//go:build .*[^!]integration' $TESTS || true)"
  n_src=$(count "$SRC" '.'); n_tests=$(count "$TESTS" '.'); n_integ=$(count "$INTEG" '.')
  echo "  source files: $n_src · test files: $n_tests · integration-tagged: $n_integ"

  # shellcheck disable=SC2086
  n_skip=$(grepc 't\.Skipf?\(' $INTEG)
  # shellcheck disable=SC2086
  n_skipok=$(grepc 'INTEGRATION_SKIP_OK|REQUIRE_INTEGRATION|CI=' $INTEG $(grepl 'TestMain' $TESTS | tr '\n' ' '))
  if [ "$n_integ" -gt 0 ] && [ "$n_skipok" -eq 0 ]; then verdict RED "integration harness has $n_skip t.Skip sites and no loud-skip guard (mechanism 1)"; fi

  # DB-owning files without a container test (heuristic by name)
  DBFILES="$(printf '%s\n' "$SRC" | grep -E '(repository|reader|writer|store|dao|query|sql|mongo)[^/]*\.go$')"
  n_db=$(count "$DBFILES" '.')
  n_db_integ=0
  for f in $DBFILES; do
    d="$(dirname "$f")"; printf '%s\n' "$INTEG" | grep -qE "^$d/" && n_db_integ=$((n_db_integ+1))
  done
  echo "  DB-owning source files: $n_db · of which in a package with any integration test: $n_db_integ"
  [ "$n_db" -gt 0 ] && [ "$n_db_integ" -lt "$n_db" ] && verdict AMBER "$((n_db-n_db_integ)) DB-owning files live in packages with zero integration tests (mechanism 3)"

  # shellcheck disable=SC2086
  n_fakes=$(grepc '^type (fake|stub|mock|Fake|Stub|Mock)[A-Za-z0-9_]* struct' $TESTS)
  # shellcheck disable=SC2086
  n_ports=$(grepc '^type [A-Za-z0-9_]*(Repo|Repository|Reader|Writer|Store|Port|Source|Client|Finder|Fetcher)[A-Za-z0-9_]* interface' $SRC)
  # shellcheck disable=SC2086
  n_sqlstr=$(grepc 'Contains\([^,]*(query|sql|stmt|Query|SQL)[^,]*, *"' $TESTS)
  # shellcheck disable=SC2086
  n_calls=$(grepc '\.(calls|Calls|got[A-Z][A-Za-z]*|captured|recorded)\b' $TESTS)
  echo "  port interfaces: $n_ports · fake/stub/mock types: $n_fakes · recorded-call refs: $n_calls · SQL-text asserts: $n_sqlstr"
  [ "$n_sqlstr" -gt 0 ] && verdict RED "$n_sqlstr assertions on SQL text (mechanism 3): $(grepl 'Contains\([^,]*(query|sql|stmt)[^,]*, *"' $TESTS | head -3 | tr '\n' ' ')"
  [ "$n_fakes" -gt 0 ] && [ "$n_integ" -lt "$((n_fakes/4))" ] && verdict AMBER "fakes outnumber integration files 4:1 (mechanism 3)"

  # hand-written schema
  # shellcheck disable=SC2086
  SCHEMA_HELPERS="$(grepl 'CREATE TABLE' $TESTS $(printf '%s\n' "$SRC" | grep -E 'testsupport|testutil|testing|fixture' | tr '\n' ' ') 2>/dev/null | sort -u)"
  DUMPED="$(printf '%s\n' "$ALL" | grep -E 'testdata/.*\.(sql|ddl)$' | wc -l | tr -d ' ')"
  if [ -n "$SCHEMA_HELPERS" ] && [ "$DUMPED" -eq 0 ]; then verdict RED "DDL hand-written in Go test helpers, no dumped .sql under testdata (mechanism 2): $(echo "$SCHEMA_HELPERS" | head -2 | tr '\n' ' ')"; fi
  TD_FILES=$(printf '%s\n' "$ALL" | grep -cE '(^|/)testdata/' )
  # shellcheck disable=SC2086
  TD_USED=$(grepl 'testdata/' $TESTS | wc -l | tr -d ' ')
  echo "  testdata files: $TD_FILES · test files referencing testdata: $TD_USED"
  [ "$TD_FILES" -lt 10 ] && verdict AMBER "almost no real-shaped fixtures under testdata (mechanism 2)"

  # config drift
  CFG="$(printf '%s\n' "$SRC" | grep -E '(^|/)config[^/]*\.go$|/config/' | head -20)"
  if [ -n "$CFG" ]; then
    # shellcheck disable=SC2086
    n_keys=$(printf '%s\n' $CFG | xargs grep -hoE '"[A-Z][A-Z0-9_]{3,}"' 2>/dev/null | sort -u | wc -l | tr -d ' ')
    echo "  config env keys (quoted UPPER_CASE in config files): $n_keys"
    [ -n "${EX:-}" ] && [ "$n_keys" -gt $((EX*2)) ] && verdict RED "config keys ($n_keys) vs .env.example ($EX) drift (mechanism 5)"
  fi
  # shellcheck disable=SC2086
  n_emptydeps=$(grepc 'Provide\([A-Za-z.]*Deps\{\}\)|Deps\{\}\)' $(printf '%s\n' "$TESTS" | grep -E '^cmd/' | tr '\n' ' '))
  [ "$n_emptydeps" -gt 0 ] && verdict AMBER "$n_emptydeps composition tests use empty Deps{} (mechanism 5)"
  # shellcheck disable=SC2086
  n_boot=$(grepl 'httptest|gin\.New|chi\.NewRouter|http\.NewServeMux' $INTEG | wc -l | tr -d ' ')
  echo "  integration files that also spin an HTTP router (acceptance tests): $n_boot"

  # contract
  GOLDEN=$(printf '%s\n' "$ALL" | grep -cE '\.golden$|testdata/.*(response|golden|replay).*\.json$')
  # shellcheck disable=SC2086
  n_omit=$(grepc 'omitempty' $SRC)
  # shellcheck disable=SC2086
  n_guard=$(grepc 'make\(\[\][A-Za-z0-9_.*]+, *0' $SRC)
  # shellcheck disable=SC2086
  n_oapi=$(grepl 'openapi3filter|ValidateResponse|kin-openapi' $TESTS | wc -l | tr -d ' ')
  echo "  golden/replay files: $GOLDEN · omitempty: $n_omit · manual nil-slice guards: $n_guard · OpenAPI response validation tests: $n_oapi"
  [ "$GOLDEN" -eq 0 ] && [ "$n_oapi" -eq 0 ] && verdict RED "no golden responses and no OpenAPI response validation (mechanism 6)"

  # Engine parity — the container the suites boot (mechanism 7)
  # shellcheck disable=SC2086
  IMG_TAGS="$(printf '%s\n' "$TESTS" "$SRC" | xargs grep -ohE '"(mysql|mariadb|postgres(ql)?|redis|mongo(db)?|clickhouse|rabbitmq|kafka)[^":]*:[0-9][^"]*"' 2>/dev/null | grep -vE ':[0-9]{4,}[^"]*"$' | sort -u)"  # drop host:port strings such as "redis:6379"
  n_imgs=$(count "$IMG_TAGS" '.')
  n_major_only=$(count "$IMG_TAGS" '^"[^:]+:[0-9]+"$')
  if [ "$n_imgs" -gt 0 ]; then
    echo "  container image tags in code: $(printf '%s' "$IMG_TAGS" | tr '\n' ' ')"
    engines_multi="$(printf '%s\n' "$IMG_TAGS" | sed -E 's/^"([^:]+):.*/\1/' | sort | uniq -d | tr '\n' ' ')"
    [ -n "$engines_multi" ] && verdict RED "the same engine is pinned to different tags across files ($engines_multi) — no single constant owns the version (mechanism 7)"
    [ "$n_major_only" -gt 0 ] && verdict AMBER "$n_major_only image tag(s) pin a major only (e.g. mysql:8) — compare with SELECT VERSION() on the deployed DSN (mechanism 7)"
    [ -z "$engines_multi" ] && [ "$n_major_only" -eq 0 ] && verdict GREEN "image tags are unique per engine and carry a minor version — still compare with the deployed VERSION() (mechanism 7)"
  fi

  # Read cost — payload columns scanned but never served (mechanism 8)
  HIDDEN_RE='(db:"[^"]+"[^`]*json:"-"|json:"-"[^`]*db:"[^"]+")'
  # shellcheck disable=SC2086
  n_hidden=$(grepc "$HIDDEN_RE" $SRC)
  # shellcheck disable=SC2086
  n_orderby=$(grepc 'ORDER BY' $SRC)
  echo "  fields scanned from the DB but never served (db tag + json:\"-\"): $n_hidden · ORDER BY statements: $n_orderby"
  # shellcheck disable=SC2086
  [ "$n_hidden" -gt 0 ] && verdict AMBER "$n_hidden column(s) are read into fields the response never returns — a payload fetched to be thrown away; check none rides through an ORDER BY and put bytes-read in the AC (mechanism 8): $(grepl "$HIDDEN_RE" $SRC | head -3 | tr '\n' ' ')"

  # Two clocks — app time compared with the database clock (mechanism 10)
  # shellcheck disable=SC2086
  NOW_TESTS="$(grepl 'time\.Now\(\)' $TESTS)"
  # grepl returns nothing for an empty file list, so no grep ever reads stdin
  # shellcheck disable=SC2086
  CLOCK_MIX="$(grepl '(now\(\)|NOW\(\)|CURRENT_TIMESTAMP)' $NOW_TESTS | sort -u)"
  n_clock=$(count "$CLOCK_MIX" '.')
  # shellcheck disable=SC2086
  n_dates=$(grepc 'time\.Date\(20[0-9]{2}|"20[0-9]{2}-[01][0-9]-[0-3][0-9]' $TESTS)
  echo "  test files mixing time.Now() with SQL now(): $n_clock · literal calendar dates in tests: $n_dates"
  [ "$n_clock" -gt 0 ] && verdict AMBER "$n_clock test file(s) compare app time with the database clock — each comparison needs a tolerance, or the row made due on the DB clock (mechanism 10): $(printf '%s\n' "$CLOCK_MIX" | head -3 | tr '\n' ' ')"

  if [ "$PROBE" -eq 1 ] && [ -n "$INTEG" ]; then
    echo
    echo "## Probe — silent skip (mechanism 1)"
    pkg="./$(dirname "$(printf '%s\n' "$INTEG" | head -1)")/"
    out="$(go test -tags integration -count=1 -v "$pkg" 2>&1)"
    rc=$?
    runs=$(printf '%s\n' "$out" | grep -c '^=== RUN')
    passes=$(printf '%s\n' "$out" | grep -c '^--- PASS')
    skips=$(printf '%s\n' "$out" | grep -c '^--- SKIP')
    echo "  package: $pkg · exit=$rc · RUN=$runs PASS=$passes SKIP=$skips · docker=$DOCKER"
    if [ "$rc" -eq 0 ] && [ "$passes" -eq 0 ]; then verdict RED "exit 0 with zero passing tests — the suite skips silently"; fi
    if [ "$DOCKER" = no ] && [ "$rc" -eq 0 ]; then verdict RED "Docker is down yet the integration package reports ok"; fi
  fi
fi

# ---------------------------------------------------------- STACK-SPECIFIC ----
# Add greps for other stacks here, e.g.
#   PHPUnit: files with @group integration vs markTestSkipped
#   Jest/Vitest: describe.skip / test.skipIf / --passWithNoTests in package.json
#   Playwright/Cypress: presence of recorded fixtures vs hand-written mocks

echo
echo "Next: open every RED/AMBER citation, map the last real-run bugs to mechanisms, compare the"
echo "test engine with SELECT VERSION() on the deployed DSN (mechanism 7), run the suite through the task"
echo "runner and directly (mechanism 9), then"
echo "write ACs with templates/acceptance-criteria.md."

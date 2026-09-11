# Reality Gate — reference

Each mechanism: how it arises in an agent loop, how to detect it, how to fix it, and a
concrete code pattern. Examples are Go/MySQL/Mongo but the mechanism is stack-neutral.

## 1. Silent integration skip

**How it arises.** Integration tests need Docker. To keep `make test-integration` green on
laptops without Docker, the harness prints "skip" and exits 0. The agent (and the root
verifying it) reads `ok` and stops.

**Detect.** Stop Docker, run the tagged suite with `-v`. If the package reports `ok` with
no `=== RUN` lines, the skip is silent. Count `t.Skip(` in integration files; check whether
any AC in recent packets contains the integration tag at all.

**Fix.**
```go
// TestMain in every integration package
db, cleanup := testdb.Start(ctx)
if db == nil {
    if os.Getenv("INTEGRATION_SKIP_OK") == "" {
        fmt.Fprintln(os.Stderr, "integration: Docker unavailable and INTEGRATION_SKIP_OK not set")
        os.Exit(1)
    }
    os.Exit(0)
}
```
CI never sets the variable. AC must be `go test -tags integration -run '^TestX$' -v ./pkg/`
and the reviewer pastes the `--- PASS: TestX` line.

## 2. Hand-written schema and invented fixtures

**How it arises.** The agent creates the test DDL from the columns its own queries select
and seeds rows that satisfy its own assertions. The real table differs: a column does not
exist, is NULL where the test assumed NOT NULL, stores a string where Go expects an int,
or holds a legacy timestamp in a local timezone.

**Detect.** Diff the test DDL against `SHOW CREATE TABLE` from a read-only connection to
the real dev database. Look for any test fixture column absent from the real table. Check
whether `testdata/` holds any row or document the legacy system actually wrote.

**Fix.**
- Generate `testdata/schema/<table>.sql` from the real database with a tracked script
  (`scripts/dump-schema.sh`, read-only DSN from an untracked env file). The test harness
  loads those files; nobody hand-edits DDL.
- Fixtures come from real rows: `SELECT ... WHERE id IN (...)` → sanitize (user ids,
  emails, tokens) → `testdata/fixtures/<case>.sql` or `.json`. Keep the ugly ones: NULLs,
  empty strings, mixed types, deleted siblings.
- For document stores, insert the raw legacy-shaped document (`bson.M` copied from the
  real collection), never the Go struct the new code writes, when testing a reader.

## 3. Tautological fakes at the seam

**How it arises.** The service test injects `fakeRepo` returning canned data. The fake and
the real repository are written by the same agent in the same turn; the fake encodes the
agent's belief, so the test cannot disagree with the code. Interaction assertions
("repo.Update was called with X") and SQL-text assertions make this worse: they pin the
implementation while proving nothing about the database.

**Detect.** Count `type fake|stub|mock… struct` in tests versus container-backed tests of
the real implementation. Any `strings.Contains(query, "...")` in a test is RED. A
repository/reader/writer file with no integration test is RED.

**Fix.**
- Fakes are allowed only for pure business logic where the seam contract is already
  proven elsewhere by a container test.
- Every file that owns SQL/Mongo/Redis gets at least one container-backed test that
  executes the real query against the real schema (mechanism 2).
- Replace SQL-text assertions with result assertions on the container.
- One acceptance test per HTTP endpoint: real router + real middleware + real
  containers, asserting the JSON body, not internal calls.

## 4. Replay suite outside the repo

**How it arises.** During a release push the root writes a quick script that replays
real requests and diffs Go vs legacy. It catches real bugs. It lives in the session's
scratch directory. The report says "rerun the suite before release". The next session
cannot.

**Detect.** Grep reports/handoffs for script names; check they exist in git. Look for
`scripts/certify|replay|smoke|e2e` directories and `-tags live` tests.

**Fix.** Track the suite. Minimum shape:
```
scripts/certify/
  run.sh              # --base URL --legacy URL --token-env NAME; exit 1 on new diff
  cases/<flow>.json   # request + expected legacy response (redacted)
  ignore.json         # volatile fields (timestamps, request ids, cache headers)
  accepted.json       # deliberate divergences, each with ADR/ticket
```
Add the run command to the Makefile and to the AC template. Every real-run bug adds a
case before its fix lands.

## 5. Wiring and config untested

**How it arises.** Feature packages are well tested in isolation; `cmd/app` composes them
with `Provide(Deps{})` in tests, so nil clients, wrong env names, and prod URLs in local
config are never exercised. Bugs then appear only when the binary boots in a real
environment.

**Detect.** Count config keys versus `.env.example` entries. Grep composition tests for
empty `Deps{}`. Check for any test that boots the real process against containers.

**Fix.**
- `scripts/check-env-example.sh`: extract keys from the config struct, diff with
  `.env.example`, fail on drift.
- One boot test per process: start MySQL/Mongo/Redis containers, run the real
  composition, hit `/healthz` and one real endpoint per feature.
- Config values that must differ per environment (storage base URL, auth mode) get a
  startup assertion that refuses obviously wrong combinations (prod URL with dev mode).

## 6. No client contract evidence

**How it arises.** Response structs use `omitempty` and nil slices; the client expects
`[]` and present-but-zero fields. Nothing compares the emitted JSON to what the client
was built against.

**Detect.** No golden files; many `omitempty`; many manual `make([]T, 0)` guards; OpenAPI
present but never validated in tests.

**Fix.**
- Golden responses captured from the legacy/real system (mechanism 4 cases double as
  goldens) asserted byte-for-byte after normalization.
- Handler tests validate every response against the OpenAPI document
  (`kin-openapi` `openapi3filter.ValidateResponse` in Go).
- A JSON marshal guard in one place (nil slice → `[]`) instead of per-field guards.

## Mapping bugs to mechanisms (worked example)

| Real-run bug | Mechanism |
|---|---|
| 500 from a column that exists only in the test DDL | 2 |
| Timestamp off by the local UTC offset | 2 (fixture never held a real legacy string) + 4 (no replay) |
| `data: null` where client expects `[]` | 6 |
| Cache layer bug found only on the running pod | 1 (cycle had zero integration AC) + 5 |
| Endpoint returned wrong shape after refactor, suite green | 3 (fake pinned the old contract) |

## Porting this skill to another repo

1. Copy the directory. It has no external links.
2. Run `scripts/audit.sh --probe`. For non-Go stacks the script reports what it can
   count; add stack-specific greps at the marked block (PHPUnit `@group integration`,
   Jest `describe.skip`, Vitest `test.skipIf`, etc.).
3. Put the AC template into the repo's packet/PR template.
4. Add the replay suite skeleton under `scripts/certify/` on the first seam change.
5. Record in the repo's agent instructions (AGENTS.md / CLAUDE.md): "seam changes
   require a reality AC (skill: reality-gate)". Without that pointer the skill is never
   loaded.

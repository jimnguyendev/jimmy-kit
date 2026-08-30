---
name: tdd-go
description: Implement already accepted feature behavior or bug fixes test-first in Go. Use when public behavior, interface, and scope are settled and code must be added or changed through vertical red-green-refactor slices.
---

# TDD (Go) — Vertical-Slice Red/Green/Refactor

This skill is the **process layer** on top of `backend-go-testing`. Use it whenever you build a new feature or fix a non-trivial bug in this repo.

- This skill answers: *when do I write the test, and in what order?*
- `backend-go-testing` answers: *what does a good Go test look like?* (table-driven, testify, goleak, build tags, etc.)

When the two conflict, this skill's process wins; the Go-specific patterns in `backend-go-testing` apply inside each cycle.

## Routing contract

Read and apply the canonical
[skill-routing.md](../engineering-design-thinking/references/skill-routing.md) before transferring work.
This skill owns accepted observable behavior implementation. Keep the current slice bounded, emit the
canonical handoff artifact when a route trigger appears, and never encode an unsettled contract as a test.

## Philosophy

**Core principle**: Tests verify **behavior through public interfaces**, not implementation details. Code can change entirely; tests shouldn't.

**Good tests** read like a specification — "service rejects request when token expired", "repository returns ErrNotFound for missing id". They survive refactors because they don't care about internal structure.

**Bad tests** mock internal collaborators, assert on private state, or duplicate the implementation in the test body. Warning sign: rename an unexported helper and tests break, even though behavior didn't change.

This aligns with `backend-go-testing` rule #5 ("NEVER test implementation details"). The rest of this skill is *how to get there reliably*.

## Anti-Pattern: Horizontal Slices

**DO NOT write all table rows first, then all implementation.** This is "horizontal slicing" — treating RED as "write all the table cases" and GREEN as "make them all pass".

This produces crap tests:

- Cases written in bulk test *imagined* behavior, not *actual* behavior.
- You end up asserting on shape (struct fields, error types) instead of effect (state change, side effect, returned value).
- Tests become insensitive to real changes — pass when behavior breaks, fail when behavior is fine.
- You outrun your headlights, committing to a table shape before the implementation is even sketched.

**Correct approach**: vertical slices via tracer bullets. One case → one implementation → repeat. Each case responds to what the previous cycle taught you.

```
WRONG (horizontal):
  RED:   table case 1..5
  GREEN: handler + service + repo all at once

RIGHT (vertical):
  RED→GREEN: case 1 → minimal handler+service+repo path
  RED→GREEN: case 2 → grow the path
  RED→GREEN: case 3 → ...
```

Table-driven tests are still the idiomatic Go shape. The rule is *grow the table one row per cycle*, not *write the whole table up front*.

## Workflow

### 1. Planning

Before writing any code, inspect an inbound handoff first. If it already contains accepted behavior,
interface, boundaries, risks, scope, and verification state, treat planning approval as satisfied and ask
only about missing, contradictory, or newly expanded fields. Otherwise:

- [ ] Read the relevant area of the codebase. Use the project's domain vocabulary from `CONTEXT.md` (if it exists) and `docs/adr/` so test names match the language the team already speaks.
- [ ] Confirm with user: which feature layer is affected? (`handler` / `service` / `repository` / `middleware`)
- [ ] Confirm with user: which behaviors matter most? You can't test everything — prioritize critical paths and complex logic.
- [ ] Sketch the public interface (handler signature, service method, repo method). Service-layer tests are the usual sweet spot: they exercise real business rules without HTTP plumbing.
- [ ] List behaviors as **observable outcomes**, not implementation steps. ("returns 409 when example already exists", not "calls repo.Exists then returns ErrConflict").
- [ ] Get user approval before entering the loop only when no accepted inbound artifact exists.

Do not repeat that question when the accepted handoff already answers it.

### 2. Tracer Bullet

Write ONE test for the happy path:

```
RED:   first table row + t.Run scaffolding → fails (no impl yet)
GREEN: minimal implementation across the layers it touches → passes
```

The tracer bullet proves the wiring works end-to-end (handler ↔ service ↔ repo ↔ DB). It doesn't have to be elegant; it has to be **real**.

### 3. Incremental Loop

For each remaining behavior:

```
RED:   add one row to the table → it fails
GREEN: smallest code change to pass → it passes
```

Rules per cycle:

- One new case at a time.
- Only enough production code to pass the current case.
- Don't anticipate future cases ("I'll need a config here later" — no, wait until the test demands it).
- Test names use behavior language: `t.Run("rejects expired token", ...)`, not `t.Run("auth_middleware_test_1", ...)`.
- Mock at process boundaries the feature calls into (gRPC client, Redis, Kafka, the repository interface) — never mock another feature's service. See "Mocking strategy" below.

### 4. Refactor

After ALL planned cases pass:

- [ ] Look for duplication across cases (helper, fixture).
- [ ] Deepen modules: can a complex sequence move behind a simpler interface? (See `engineering-design-thinking` for upfront design, `improve-arch-go` for codebase-wide deepening sweeps.)
- [ ] Apply Go conventions and the current repository rules in `AGENTS.md`.
- [ ] Run `make test` (race detector on) + `golangci-lint run` after each refactor step.

**Never refactor while RED.** Get to GREEN first. If a refactor turns the bar red, undo and try a smaller step.

## Checklist Per Cycle

```
[ ] Test name describes behavior in domain language (not "test_1", not "happy_path")
[ ] Test exercises the public interface only (no reaching into unexported helpers)
[ ] Test would survive renaming every unexported function
[ ] Mocks are at process boundaries (gRPC client, Redis, Kafka) — NOT at internal collaborators
[ ] Production change is the minimum needed to pass THIS case
[ ] No speculative fields, no "I'll need this later" code
[ ] New external calls follow the timeout/cancellation policy accepted by this repository
[ ] Error handling follows the current feature convention and preserves the accepted public envelope
```

## Mocking strategy (this repo)

Follow the repository test conventions: mock process boundaries, not implementation details you own.

This skill interprets the **repository interface as a process boundary** (Mongo is an external process, the repo is the seam in front of it). That makes the repo a legitimate mocking target in service tests — they stay unit, fast, and behavior-focused.

- **Mock**: gRPC clients to other services, Redis, Kafka, the feature's own `Repository` interface, time (via `clockwork` or `synctest`).
- **Use real Mongo**: in **repository tests** (build-tagged `integration`) and the **one end-to-end happy path per feature**. Repository tests are where Mongo semantics (uniqueness, indexes, transactions) actually get exercised.
- **Never mock**: another feature's service. If feature A needs feature B, A declares a small consumer-side interface and A's tests use a fake; B's tests use the real thing.

If a service test is genuinely simpler with a real Mongo (rare — usually means the logic under test is actually persistence logic and belongs in the repo), promote it to `integration` build tag instead of fighting the mock.

See `backend-go-testing` and `backend-go-stretchr-testify` for the Go-specific mocking mechanics; use `gotests` to scaffold the first row of a new table-driven test.

## Test layering in this repo

| Layer | Test style | Build tag | Speed |
|---|---|---|---|
| `service.go` (business logic) | unit, table-driven, mock repo + process boundaries | none | <1ms |
| `repository.go` (Mongo) | integration, real Mongo via testcontainers / docker-compose | `integration` | seconds |
| `handler.go` (HTTP) | unit via `httptest`, table-driven status/body | none | <10ms |
| End-to-end happy path | one per feature, real Mongo + real Gin engine | `integration` | seconds |

TDD loop runs primarily at the **service layer** — that's where business behavior lives. Handler tests come after, as thin assertions on status code and envelope shape. Repository tests and the end-to-end happy path cement the contract once the service-layer behavior is stable.

## When NOT to use this skill

- Trivial CRUD endpoint that follows an existing pattern exactly — copy the pattern, add a test after.
- Pure refactor (no behavior change) — route end-state cleanup or compatibility removal to `zero-tech-debt`; otherwise leave existing tests and run them after each step.
- Spike / prototype to explore a library — write tests *after* you decide to keep the code.

## Cross-references

- `backend-go-testing` — table-driven, testify, goleak, build tags, fuzzing.
- `backend-go-stretchr-testify` — assert vs require, mock package, suite.
- `backend-go-design-patterns` — feature layout (`types/repository/service/handler/...`) this loop assumes.
- `engineering-design-thinking` — when the planning step reveals the design isn't clear yet.
- `zero-tech-debt` — pure refactors that remove compatibility cruft without changing behavior.

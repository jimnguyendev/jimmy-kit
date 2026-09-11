---
name: tdd-go
description: Implement already accepted feature behavior or bug fixes test-first in Go. Use when public behavior, interface, and scope are settled and code must be added or changed through vertical red-green-refactor slices.
---

# TDD (Go) — Vertical-Slice Red/Green/Refactor

> **This skill exists to stop:** accepted behavior from being implemented in broad horizontal batches, guessed contracts, or tests coupled to private implementation.

## 🤖 0. HOW TO USE

- **Build** (default): implement one accepted behavior at a time through vertical RED -> GREEN -> REFACTOR slices.
- **Bug fix**: start from one observable failing example after the desired behavior is accepted.
- **Handoff**: transfer unsettled decisions, broader architecture evidence, or remaining pure cleanup through the canonical routing artifact.

Output: green behavior tests through public interfaces plus a bounded implementation; never an imagined batch of cases written ahead of learning.

> 🧩 **Companion Go pack:** the `backend-go-*` skills referenced below (testing, testify, design-patterns, performance, observability…) are a separate pack, **not bundled** in this kit. Everything in this skill runs without them; where they are named, apply your project's own Go conventions instead.

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

### When implementation changes structure

When an accepted slice creates or moves **packages, types, or interfaces**, read [engineering-philosophy.md](../codebase-design/references/engineering-philosophy.md). Preserve business-capability locality, contextual names without stuttering, types near their owner, and an acyclic import graph. A consumer-side interface is justified only by a real seam, not by every concrete type.

Go enforces package DAGs at compile-time; it does not own the principle. The same one-way dependency rule is stack-neutral. If a cycle appears, move responsibility first, merge a fake boundary second, and introduce a consumer-owned interface only when the modules remain independently owned.

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

- [ ] Read the relevant area of the codebase. Use the project's domain vocabulary from `CONTEXT.md` (if it exists) and `.jimmy/adr/` so test names match the language the team already speaks.
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
- [ ] Deepen modules: can a complex sequence move behind a simpler interface? (See `engineering-design-thinking` for upfront design, `improve-codebase-architecture` for codebase-wide deepening sweeps.)
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
[ ] Seam touched (SQL/document store/cache/client/config/response shape)? Then the slice is NOT done
    until one reality check exists and was observed running: the feature's acceptance test (real
    containers + real router, `-tags integration -v`, paste `--- PASS`) or a replay diff against
    the legacy system. Fakes never close a seam slice. (skill: `reality-gate`)
```

## Test doubles — six rules (gated, not advisory)

These replace the older "the repository is a process boundary, so mock it" doctrine. In a
coding-agent loop that doctrine produces hundreds of fake-backed service tests that stay green
while the real database, config, and client break. Sources: Khorikov (managed vs unmanaged
dependencies), Fowler (sociable over solitary), Cooper (behavior, not method), Google Testing
Blog (change-detector tests), Bernhardt (functional core / imperative shell), Rainsberger
(contract tests on both sides of every fake), Beck (coupled to behavior, decoupled from structure).

1. **Trigger = a new observable behavior**, never a new method or type. The observable surface
   is the HTTP route, the exported service call, or the row/document written. One behavior, one test.
2. **Fake only unmanaged dependencies**: other services' gRPC/HTTP APIs, message buses, object
   storage, the clock. **Databases are real**: run them in containers. If a database is shared
   with another application, its schema and document shapes are a contract with that system —
   fixtures come from dumped DDL and real (sanitized) rows/documents, never from a hand-written
   table or an invented row.
3. **The feature's own repository/reader/writer is not a mocking target.** A service test that
   needs data goes through the real repository against the container (sociable test). A
   `fakeXRepo` is allowed only when the logic under test is pure decision logic AND the real
   implementation has its own container test for the same method.
4. **Functional core / imperative shell.** If a service needs four or more fakes to test, stop:
   extract the decision into a pure function with table-driven tests (expected values from the
   reference implementation), and leave a thin shell covered by one acceptance test.
5. **No change-detectors.** Never assert SQL text, fake call counts or order, or unexported state.
   Assert outcomes: response JSON, rows/documents written, returned values. A test that must be
   edited during a pure refactor is a defect in the test, not a cost of the refactor.
6. **Contract on both sides of every fake.** A fake for an unmanaged dependency needs a contract
   test against the real thing or a recorded fixture (an `httptest` server replaying captured
   responses); otherwise the fake is a guess written by the same agent as the code.

## Test layering

| Code | Test | Build tag |
|---|---|---|
| Pure decision functions (grading, projections, parsing, formatting) | unit, table-driven, no fakes, expected from the reference implementation | none |
| Repository / reader / writer | container-backed, real DDL, real documents | `integration` |
| Service shell + handler, one per flow | **acceptance**: real router + real middleware + real adapters + containers; assert the JSON body and the persisted document | `integration` |
| Clients of unmanaged dependencies | unit with `httptest` replaying captured responses + contract test | none / `integration` |

Make the integration harness fail loudly when its container is unavailable (an env var such as
`INTEGRATION_SKIP_OK=1` to opt into skipping), so `ok` always means the tests ran.

Two metrics replace coverage: a refactor commit that only moves boundaries edits no test file
except import paths, and every feature has at least one acceptance test that was observed
running (`-v`, `--- PASS` pasted in the review). The `reality-gate` skill audits both.

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

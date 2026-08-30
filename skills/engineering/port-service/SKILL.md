---
name: port-service
description: Orchestrator for porting an existing service (Go, Laravel/PHP, or other) into this Go repo while preserving behavior and MongoDB data. Generates a phased plan, delegates each phase to the right skill, and enforces checkpoints. Use when porting, migrating, or rewriting another service into vr-services. NOT a one-shot — human approval at every phase boundary.
---

# Port a Service Into This Repo

This skill orchestrates a **multi-phase port** of an existing service (the *source* — any language/framework) into this Go repo (the *target*). It does NOT do the porting itself — it produces a plan, drives discovery, and hands each phase off to a focused skill, pausing for user approval at every boundary.

**Cross-language is the common case** (Laravel/PHP, Node, Rails → Go). The orchestrator is language-agnostic; Phase 1 has source-specific discovery checklists.

**Reality check**: a port is not one-shot. Behavior parity, MongoDB data fidelity, and API contract stability each need humans in the loop. This skill makes the path explicit and resumable.

## Two-mode operation: Plan + Execute

This skill is most powerful when split into two distinct sessions:

1. **Plan mode (interactive, single session)** — front-load ALL questions, ALL architectural decisions, ALL mapping tables. Output: `PORT-PLAN.md` (a frozen contract for the agent to follow).
2. **Execute mode (autonomous, `/goal`-driven)** — Claude executes the parts of the plan that have verifiable end states without further prompting.

This lets you have ONE long interactive session (with you answering every question, reviewing every ADR), then walk away while Claude grinds through scaffolding + per-feature ports + dry-run migration. See "Running with /goal" at the bottom of this skill.

## Hard rules

- Never proceed past a phase boundary without explicit user approval.
- Never write a data migration job without a dry-run + count verification step.
- Never delete from source. Treat the source service as read-only until cutover.
- Every architectural decision lands in an ADR before code is written.
- If a phase reveals a blocker, stop and surface it — do not improvise around it.

## When to use

- Porting another Go service into this repo as one or more features.
- Merging two services after an org change.
- Replacing a legacy service with a rewrite in this repo while keeping the same database.

Skip this skill for: small feature copy-paste (use direct `tdd-go`), pure schema migration without a service involved (write a job directly).

## Inputs the user must provide

Ask before starting:

1. **Source path** (absolute or relative; can be outside the repo, e.g. `tmp/vr-marking-services`).
2. **Source stack**: Go / Laravel (PHP) / Node / Rails / other — determines Phase 1 discovery checklist.
3. **Source database** access (Mongo URI for read; can be a snapshot/restore in dev). Note source-side driver if known (e.g. `jenssegers/laravel-mongodb`, native PHP mongo-driver).
4. **Behavior parity bar**: strict (byte-for-byte responses) or compatible (same effect, response shape may evolve).
5. **API contract**: keep paths/verbs identical, or allow renames?
6. **Data migration mode**: in-place (same DB), copy (new DB, migrate documents), or fresh (no historical data).
7. **Cutover style**: hard switch, blue-green, or dual-write window.

## Skill orchestration map

At each phase, this skill explicitly delegates to other skills. Do not improvise — invoke the named skill rather than re-deriving its workflow.

| Phase | Mode | Primary skill | Supporting skills |
|---|---|---|---|
| 0. Frame | interactive | `port-service` (this) | `engineering-design-thinking` if scope unclear |
| 1. Discover (Go source) | interactive | `capture-knowledge-go` | `Agent subagent_type=Explore` for breadth |
| 1. Discover (Laravel source) | interactive | this skill's Laravel checklist | `Agent subagent_type=Explore` for breadth; no Go-specific skills |
| 2. Align & decide | interactive | `grill-with-docs` | `engineering-design-thinking`, `backend-core`, `engineering-rest-api-design` |
| 3. Target scaffolding | `/goal`-eligible | CLAUDE.md "Adding a New Feature" | `backend-go-project-layout`, `backend-go-design-patterns`, `backend-go-naming`, `backend-go-structs-interfaces` |
| 4. Port behavior per feature | `/goal`-eligible | `tdd-go` | `backend-go-testing`, `backend-go-stretchr-testify`, `backend-go-error-handling`, `backend-go-context`, `backend-go-safety`, `backend-go-database` |
| 5. Data migration (dry-run only) | `/goal`-eligible | `backend-go-database` | `backend-go-cli` (for the migrate-* job runner), `backend-go-concurrency` (for batched writes), `backend-go-observability` (progress metrics) |
| 5. Data migration (real run) | interactive | manual run + verification | `diagnose` if dry-run vs real diverges |
| 6. Cutover | interactive (never /goal) | manual runbook | `backend-go-observability` for monitoring during traffic shift |
| 7. Verify | mixed | `improve-arch-go`, `code-review` | `verify` for end-to-end smoke; `security-review` if auth/identity changed |

Architecture-relevant skills are **mandatory** at the phase they're listed:
- Phase 3 must follow `backend-go-design-patterns` + `backend-go-project-layout` — do not invent a layout.
- Phase 4 must use `tdd-go` for vertical-slice TDD — do not write all tests then all code (horizontal slice anti-pattern).
- Phase 7 must run `improve-arch-go` before declaring the port done — catches drift introduced during the port.

## Phased plan

Each phase ends with a **gate** — a deliverable the user must approve before the next phase starts. Generate a `TaskList` in the conversation reflecting these phases.

### Phase 0 — Frame
- Confirm inputs above.
- Skim source: directory structure, entry points, top-level README.
- Decide scope: which features/endpoints/jobs of the source go where in the target's `internal/feature/...`.
- **Gate**: written scope statement (feature mapping table) + draft ADR.

### Phase 1 — Discover

Pick the discovery method by source stack:

**If source is Go** → run `/capture-knowledge-go` (depth=standard) for every entry point in scope.

**If source is Laravel/PHP** → do NOT use `capture-knowledge-go` (it reads Go-specific patterns). Instead, for each entry point write a brief manually to `.claude/knowledge/source-<name>.md` following the Laravel checklist below. Use `Agent subagent_type=Explore` for broad scans of unfamiliar PHP code.

**If source is Node/Rails/other** → adapt the Laravel checklist (route file → routes; controller → action; model → ORM call; queue/job → background worker; middleware → middleware).

Universal outputs regardless of stack:
- Per-entry-point brief at `.claude/knowledge/source-<name>.md`.
- MongoDB collection catalogue: for each collection, document shape, indexes, ID type (`ObjectId` / UUID / numeric), expected cardinality, write pattern (insert-only / heavy update).
- External dependency catalogue: third-party APIs, env vars, queue brokers, cache, mail, storage.
- **Gate**: `.claude/knowledge/source-overview.md` linking every per-entry-point brief + collection catalogue + dependency catalogue.

#### Laravel hidden unknowns — MANDATORY investigation

PHP/Laravel is dynamically typed; the source code does NOT fully declare what a request, response, or model actually contains. Porting to Go with one missing field = different behavior. For every Laravel entry point in scope, you MUST exhaustively enumerate:

**Request shadow fields** (fields the controller reads but FormRequest doesn't declare):
- Grep the controller method for every `$request->`, `$request->input(`, `$request->get(`, `$request->has(`, `$request->filled(`, `$request->only(`, `$request->except(`, `request()->`.
- Compare against the FormRequest `rules()` array. Anything in controller but NOT in rules = shadow field. List explicitly.
- Watch for `$validated = $request->validated();` followed by use of NON-validated fields elsewhere — common Laravel bug pattern.
- Note default fallbacks: `$request->input('x', 'default')` — record the default for target's struct zero-value or pointer-nil semantics.

**Model shadow fields**:
- Grep model class for `$casts`, `$fillable`, `$guarded`, `$hidden`, `$appends`, `$dates`.
- Grep usage of `->getAttribute(`, `->setAttribute(`, dynamic `$model->some_field` access not declared in `$fillable`.
- Note Mongo documents may carry fields the Eloquent model doesn't know about (legacy data) — sample 10 real docs from source DB to verify.

**Response shadow fields**:
- API Resource `toArray()` method — list every key returned.
- `when()` / `whenLoaded()` / `mergeWhen()` conditional fields — record the condition.
- Compare against actual production responses (curl a few real endpoints if reachable) — production may include fields no longer in code.

**Type coercion landmines**:
- `'datetime'` cast: source accepts multiple formats (`Y-m-d`, ISO 8601, timestamps as strings). Go's `time.Time` is strict. Document exact format(s) in use.
- `'array' / 'json'` cast: PHP roundtrips JSON columns; check Mongo storage shape (string vs sub-document).
- `'boolean'` cast: PHP accepts `1`, `"1"`, `"true"`, `true`, `"on"`, etc. Document which the API actually receives.
- Numeric strings: PHP auto-coerces `"42"` to `42`. Go does not. Decide per field.
- Null vs missing vs empty string: PHP `empty()` treats all as falsy. Go differentiates. Decide per field whether `null`/`""`/missing have different meaning.

**Side-effect shadows**:
- `dispatch()` / `event()` calls — every queue job + event the action triggers.
- `Auth::user()` / `request()->user()` — implicit auth dependency.
- Middleware that mutates request before controller (e.g. trim, sanitize).
- Global scopes on Eloquent models — silently filter queries (e.g. `whereNull('deleted_at')`).
- Observers (`app/Observers/*`) — fire on model save/delete without explicit call.

**Output of this investigation**: a `Shadow Fields` section in each per-entry-point brief, listing every shadow + the decision (carry over, drop with ADR, change semantic).

**Verification step**: capture 10–20 real production requests + responses (sanitized) per endpoint as `.claude/knowledge/fixtures/<endpoint>.jsonl`. These become parity test fixtures in Phase 4.

#### Laravel discovery checklist (per entry point)

Files to read:
- `routes/api.php` / `routes/web.php` — entry route + middleware stack.
- Controller method body — the action handler.
- `app/Http/Requests/*` — FormRequest validation rules (these become handler-side syntactic + service-side semantic validation in target).
- `app/Http/Middleware/*` for any custom middleware on the route.
- Eloquent models (`app/Models/*`) — note the `$connection`, `$collection` / `$table`, casts, mutators, relationships, scopes.
- Service / Action / UseCase classes if the project uses them.
- Policies (`app/Policies/*`) — authorization logic.
- Jobs (`app/Jobs/*`) — queue handlers; note `tries`, `backoff`, `uniqueId`.
- Events / Listeners — fan-out logic.
- `config/*.php` — anything env-driven the action reads.

Capture per brief:
- **Route**: verb + path + middleware chain.
- **Auth**: `auth:api`? Sanctum? Passport? Custom guard? — maps to target's Envoy trust headers or API key per ADR-0003.
- **Request validation**: FormRequest rules verbatim.
- **Action flow**: numbered steps from controller method.
- **DB writes/reads**: Eloquent calls → translate to Mongo operations (collection + filter + update/insert shape).
- **Side effects**: events dispatched, jobs queued, mail/notification sent.
- **Response shape**: API resource (`app/Http/Resources/*`) or raw array.
- **Eager loads / N+1 risks** noted in the source.
- **Open questions**: anything PHP-specific that does not map cleanly.

### Phase 2 — Align & decide
- Use `/grill-with-docs` to update `CONTEXT.md` with vocabulary from the source (likely new domain terms enter the target).
- Write ADRs for every decision that is not a one-to-one port:
  - ID strategy (source `ObjectID` vs target `identity.NewID()` UUIDv7).
  - Collection rename / consolidation.
  - Auth/identity mapping (source might use different headers; target uses Envoy trust headers per ADR-0003).
  - Error envelope changes.
  - Rate limit / body limit deltas.
- Produce a **mapping table** in the discovery brief: source route → target route + feature + repo method.
- **Gate**: ADR(s) merged (Status: Accepted) + mapping table approved.

### Phase 3 — Target scaffolding
- For each new feature in the target, run the CLAUDE.md "Adding a New Feature" checklist:
  - Create `internal/feature/<name>/{types,repository,service,handler,routes,provider,errors}.go` as skeletons.
  - Define `Deps`, wire in `cmd/app/http.go`, register `EnsureIndexes`.
  - Mint IDs via `identity.NewID()`; tag persisted structs with `bson:"..."`.
- No business logic yet. Just shape.
- **Gate**: `go build ./...` passes; `make test` passes (skeletons return placeholder errors).

### Phase 4 — Port behavior per feature (loop)
For each feature in scope, in dependency order:
- `/tdd-go` to port endpoint-by-endpoint:
  - First test = happy path from the source brief.
  - Grow table per behavior; each row mirrors a behavior from the source brief.
  - Mock process boundaries (gRPC clients, Redis, Kafka); use real Mongo in repository tests via `//go:build integration`.
- Compare responses against the source on a sample (run source on `tmp/...`, run target locally, diff bodies). For "strict parity", diff must be empty modulo allowed deltas from Phase 2 ADRs.
- **Gate per feature**: all planned behaviors covered by tests; parity diff approved.

### Phase 5 — Data migration
Skip if Phase 0 chose "fresh".
- For each Mongo collection in the catalogue, create a job in `internal/jobs/migrate-<collection>/`:
  - Reads from source Mongo (using a separate URI / client).
  - Transforms documents per Phase 2 ADRs (e.g. `_id ObjectID → _id UUIDv7`).
  - Writes to target Mongo idempotently (upsert keyed by a stable natural key OR by the new UUID derived deterministically).
  - Emits per-batch metrics: read count, transform errors, write count.
- Always implement a **dry-run mode** (read + transform + write to a `.jsonl` sample, no DB write) before the real run.
- Validation script: for each collection, sample N docs from source, look them up in target by mapped key, deep-equal modulo allowed deltas.
- **Gate**: dry-run produces sample matching expectations; real run on staging DB passes count + sample checks.

### Phase 6 — Cutover
- Pick the style from Phase 0:
  - **Hard switch**: stop source, run migration job, point traffic to target.
  - **Blue-green**: deploy target alongside, shadow-read for N hours, then flip.
  - **Dual-write**: target writes to both DBs during a window; later disable source.
- Each style needs an explicit rollback plan in the ADR.
- **Gate**: rollback plan documented; cutover runbook approved.

### Phase 7 — Verify & decommission
- `/improve-arch-go` scoped to the ported features — surface anything the port introduced that violates CLAUDE.md.
- `/code-review` on the final diff.
- Source service can be archived only after target has run in production without rollback for the agreed soak period.

## Outputs the user gets

By end of Phase 7:
- `.claude/knowledge/source-*.md` — per-entry-point briefs of the source.
- `.jimmy/adr/NNNN-*.md` — every non-trivial decision.
- `internal/feature/<...>/` — ported features following CLAUDE.md layout.
- `internal/jobs/migrate-<...>/` — idempotent migration jobs.
- Cutover runbook (typically in the ADR or a `.jimmy/docs/runbooks/` file).

## Guardrails

- If the source uses patterns this repo forbids (`init()`, mutable globals, handler-side business logic), do NOT carry them over. The port is also a cleanup opportunity — record each cleanup as an ADR.
- If a source feature does not map cleanly to one target feature, surface it during Phase 2 — do not force-fit. Two source features → one target feature (or vice versa) is acceptable when documented.
- Resist "port everything, then test". Per-feature loops in Phase 4 keep parity tight.

## Laravel → Go mapping cheatsheet

| Laravel concept | Target (this repo) |
|---|---|
| `routes/api.php` group | `cmd/app/http.go` route group |
| Route middleware (`auth:api`, `throttle`) | `internal/middleware/{Identity,RateLimitUser,RateLimitIP}` |
| Controller action | `internal/feature/<name>/handler.go` |
| FormRequest rules (syntactic) | `c.ShouldBindJSON` + struct tags in handler |
| FormRequest rules (cross-entity, DB lookups) | Service-layer validation in `service.go`, returning typed sentinels |
| Policy | Service-layer check or middleware (decide per case; document in ADR) |
| Eloquent model | Domain struct in `types.go` with `bson:` tags; no ORM equivalent — repository owns Mongo calls |
| Eloquent `find / where / save` | Repository method using `mongo-driver/v2` (`FindOne`, `Find`, `InsertOne`, `UpdateOne`) |
| Eloquent relationships | Joins do not exist in Mongo — denormalize OR aggregate in repo OR fetch separately in service |
| Eloquent scopes | Repository methods named after the scope intent |
| API Resource | Response DTO assembled in handler; envelope via `httpresponse.Success/Paginated` |
| Auth `Auth::user()` | `middleware.UserIDFromCtx(c)` / `IdentityFromCtx(c)` |
| Queue job (`dispatch`) | `internal/jobs/<name>/run.go` + `cmd/app/job.go` registry, OR Kafka producer if event-driven |
| Event + Listener | `internal/event` bus (in-process) OR Kafka consumer for cross-service |
| Artisan command | A job in `internal/jobs/` invoked via `./bin/<binary> <job-name>` |
| Config (`config/*.php` + `.env`) | `internal/config/*.go` with flat env vars; defaults in code |
| Eloquent `created_at / updated_at` | Manual `time.Now().UTC()` in repo or middleware; document in ADR |
| Soft deletes (`SoftDeletes`) | Explicit `deleted_at *time.Time` field; repo filters out by default; document in ADR |
| `Mongo ObjectId` from Laravel | Decide in Phase 2 ADR: keep ObjectId or remap to UUIDv7 (`identity.NewID()`) — affects every reference |

**Common Laravel → Go pitfalls**:
- Eloquent's implicit `created_at/updated_at` — easy to forget in Go.
- FormRequest may return validation errors in `{ "errors": { "field": ["msg"] } }` shape — target's `httpresponse.AppError` envelope differs. Strict-parity ports need a translation layer; otherwise document the new shape in an ADR.
- Laravel's `auth:api` may decode a JWT inline — target relies on Envoy trust headers per ADR-0003. The port is a chance to remove inline JWT verification.
- Eloquent eager-loading hides N+1; Mongo has no joins so this becomes either denormalization or explicit multi-step fetches.
- Date casts in Eloquent (`'datetime'`) silently parse strings — Go's `time.Time` is strict. Migration jobs must validate date formats explicitly.

## Running with /goal (autonomous execution)

`/goal` (Claude Code v2.1.139+) keeps Claude working turn-after-turn until a verifiable condition holds. Use it for phases with measurable end states — **never** for cutover or production data writes.

### When to use /goal vs interactive (decision tree)

```
Is the end state verifiable from transcript output? (test pass/fail, build exit, file diff)
├── NO  → interactive only
│         (architectural decisions, ADR drafting, mapping choices,
│          production data writes, cutover, anything requiring judgment)
│
└── YES → Are mistakes recoverable without external side effects?
          ├── NO  → interactive only
          │         (production migration, cutover, anything touching prod DB / external APIs)
          │
          └── YES → /goal is appropriate
                    (scaffolding, per-feature TDD loop, dry-run migration,
                     test fixing, lint cleanup, doc generation)
```

Rule of thumb: `/goal` for mechanical convergence on a measurable bar; interactive for decisions and irreversible writes.

### Pattern: Plan once interactively → execute with /goal

**Session 1 (interactive Plan mode)** — do not invoke `/goal` here:

1. Run `/port-service` (or invoke this skill manually).
2. Answer all Phase 0 inputs.
3. Co-author every Phase 1 brief + Phase 2 ADRs + mapping table.
4. Save the final, frozen artifact to `PORT-PLAN.md` at repo root containing:
   - Scope statement (features in scope, out of scope).
   - Mapping table: source route → target feature + handler + repo method.
   - ADR references (numbers + titles), one line per decision.
   - Per-feature behavior list (each row = one test case for `tdd-go`).
   - Collection migration plan (source coll → target coll, transform rules).
   - Acceptance criteria for the execute phase (see below).
5. **Stop the session here.** Commit `PORT-PLAN.md` so it survives session boundaries.

**Session 2 (autonomous Execute mode)** — open a fresh session in the repo, then:

```text
/goal Execute PORT-PLAN.md phases 3, 4, and 5-dry-run. Acceptance:
  (a) go build ./... exits 0
  (b) golangci-lint run is clean
  (c) make test passes (race detector on)
  (d) every feature listed in PORT-PLAN.md has at least one integration test under //go:build integration that exercises the documented happy path
  (e) for each migration job in internal/jobs/migrate-*, the dry-run mode produces a sample .jsonl whose first 100 transformed docs match the expected shape from PORT-PLAN.md
  (f) no file outside internal/feature/<scoped names>, internal/jobs/migrate-*, cmd/app/, .jimmy/adr/, and PORT-PLAN.md is modified
Stop after 200 turns or when (a)–(f) all hold. Do NOT run production migration. Do NOT cutover.
```

Then enable auto mode so tool calls don't prompt: `/auto on` (or per your auto-mode config).

### Why this works

- The evaluator (small fast model, default Haiku) reads transcript only — every acceptance criterion above can be demonstrated by command output Claude writes to the transcript.
- The negative constraint (f) is enforced by Claude reporting `git diff --stat` each turn.
- The hard stop "Do NOT run production migration. Do NOT cutover." is in the goal text and re-checked every turn.

### What `/goal` cannot do here

- Replace ADR decisions in Phase 2 — those are why Plan mode exists.
- Run production data migration (Phase 5 real run) or cutover (Phase 6) — both excluded by the goal text.
- Verify behavior parity against a running source service if that service isn't reachable from the dev box — Plan mode must capture expected responses as fixtures.

### Tips

- **One goal per port chunk**, not one goal for the entire port. Bigger goals drift; small goals converge.
- If `/goal` reports "no" with the same reason for 5+ turns, **stop it** (`/goal clear`) and inspect — Claude is stuck.
- Always pair with `--resume` if you want to interrupt and continue later. The goal restores; counters reset.
- Capture every long `/goal` run's outcome as a paragraph at the bottom of `PORT-PLAN.md` so the next chunk has context.

## Cross-references

- `capture-knowledge-go` — Phase 1 engine **for Go sources only**. For Laravel/Node/etc, write briefs manually using Phase 1's checklist.
- `grill-with-docs` — Phase 2 vocabulary + ADR drafting.
- `engineering-design-thinking` — when Phase 2 reveals a real architectural fork.
- `tdd-go` — Phase 4 implementation loop.
- `improve-arch-go` — Phase 7 verification.
- `backend-go-database` — Mongo migration idioms (upsert patterns, batched writes).
- `code-review`, `verify` — Phase 7 gates.
- CLAUDE.md "Adding a New Feature" — Phase 3 checklist source of truth.

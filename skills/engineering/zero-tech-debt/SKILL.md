---
name: zero-tech-debt
description: Execute one accepted structural cleanup or refactor while preserving verified behavior. Use for removing wrappers, aliases, fallbacks, flags, legacy branches, or duplicated rules after the end state and compatibility policy are settled.
user-invocable: true
---

# Zero Tech Debt

> 🧩 **Companion Go pack:** the `backend-go-*` skills referenced below (testing, testify, design-patterns, performance, observability…) are a separate pack, **not bundled** in this kit. Everything in this skill runs without them; where they are named, apply your project's own Go conventions instead.

Make the scoped area look as though the intended product and architecture had existed from day one, while preserving every verified external contract.

"Zero tech debt" is a direction, not permission for a rewrite. Intentional compatibility is part of the interface. Unknown compatibility is a blocker, not dead code.

## Position in the skill stack

- Use `engineering-design-thinking` first when the problem, options, or end state are not accepted. This skill does not discover product requirements.
- Use `codebase-design` to judge module depth, interface size, seam placement, adapters, leverage, locality, and the deletion test.
- Use `improve-arch-go` to discover and prioritize architecture candidates. This skill executes one agreed, bounded candidate.
- Use `tdd-go` when behavior changes or a bug is being fixed. For a pure refactor, keep existing behavior tests green after every small step.
- Use `backend-go-testing` for Go test mechanics and the repository's unit/integration conventions.

## Routing contract

Read and apply the canonical
[skill-routing.md](../engineering-design-thinking/references/skill-routing.md) before transferring work.
This skill owns execution of one accepted behavior-preserving end state. Emit the canonical handoff
artifact and stop when authority, candidate selection, or intended behavior is no longer settled.

## Entry contract

Before editing, establish:

1. **End state** — one or two sentences describing the intended product surface and module interface.
2. **Scope** — exact features, packages, files, and callers owned by the change.
3. **Invariants** — observable behavior, data shape, ordering, error, permission, and performance contracts that must remain.
4. **Compatibility policy** — what is intentionally preserved, intentionally removed, or still unknown.
5. **Decision authority** — an accepted brief or ADR when the change affects architecture, schema, auth, or an external contract.
6. **Baseline** — relevant tests are green, or existing failures are recorded before the first edit.

If the end state or authority is missing, return to `engineering-design-thinking`. Do not refactor toward a guessed destination.

## Compatibility evidence gate

For every wrapper, alias, fallback, mode, field, route, or branch considered for deletion, inspect all applicable evidence:

- **Code callers** — direct calls, interfaces, reflection, generated code, tests, registries, constructors, and dependency wiring.
- **Runtime entry points** — HTTP/gRPC routes, jobs, consumers, events, feature flags, environment configuration, retries, and recovery paths.
- **External callers** — legacy PHP, mobile/web clients, scoring-service, scripts, documented journeys, and supported old app versions.
- **Persisted state** — MySQL/Mongo fields, enum values, historical documents, serialized payloads, Kafka messages, and reconciliation readers.
- **Operational evidence** — telemetry or production queries when absence of use is part of the deletion argument.

Absence-of-use evidence is valid only when instrumentation is known to cover the path and the observation window spans supported client versions plus the longest relevant retry, job, or reconciliation cycle. Otherwise classify the candidate as `Unknown`.

Classify each candidate:

| Classification | Meaning | Action |
| --- | --- | --- |
| Dead | Evidence shows no active caller or persisted contract | Delete and prove the direct path |
| Intentional | Current callers or contracts require it | Keep it; name and test the reason |
| Migration bridge | Temporary compatibility has an owner and sunset condition | Keep or remove only when the condition is met |
| Unknown | Relevant evidence is missing or contradictory | Stop deletion and report the gap |

A repository-local search returning zero results is never sufficient proof for an externally reachable or persisted contract.

## Workflow

### 1. Describe the final shape

State the intended flow, owning module, interface, dependency direction, and non-goals. Prefer product/domain names over names that describe implementation history.

### 2. Trace the current behavior end to end

Follow entry point -> loading -> validation -> domain rules -> payload -> persistence -> events/callbacks -> read view -> reconciliation. Mark every compatibility candidate and its evidence classification.

For legacy ports, distinguish behavior that executes for the in-scope journey from branches that merely exist in the old class tree. Preserve output parity, not legacy structure.

### 3. Test the proposed shape

- Apply the `codebase-design` deletion test: if removing a module only spreads its complexity into callers, deepen it instead of deleting it.
- Do not create an interface for one adapter unless tests or a known variation make the seam real.
- Remove mode flags only when the modes are accidental. Keep separate flows when they represent real product lines, lifecycles, permissions, or persistence semantics.
- Move shared rules to one owning module; do not create a generic utility or framework for one feature.
- Prefer one authoritative rule over duplicated validation, but preserve checks that intentionally defend separate trust boundaries.

### 4. Build a behavior ledger

Record four lists before implementation:

- behavior preserved;
- behavior intentionally changed with authority;
- assumptions and paths removed with evidence;
- unknowns that block deletion.

Add characterization tests when current behavior is real but poorly specified. Mark unverified legacy expectations explicitly; never convert an assumption into a golden test.

### 5. Refactor in reversible slices

Keep structural and behavioral changes separate where practical. Delete one compatibility path at a time, update its callers, run the smallest relevant checks, and inspect the diff before continuing. Do not improve unrelated debt.

For this repository, never weaken the legacy-parity rules in `AGENTS.md`: targeted Mongo updates, legacy enum/timestamp semantics, response envelopes, `is_deleted = 0`, and Go-vs-PHP write parity remain mandatory unless an approved ADR explicitly changes the contract.

### 6. Verify the intended flow

Choose evidence proportional to the affected contract:

- targeted unit tests through the public interface;
- integration tests for database, route, permission, concurrency, or persisted-state behavior;
- Go-vs-PHP parity diff for write paths;
- client/API journey checks for changed navigation, payloads, aliases, or auth tolerance;
- runtime/telemetry evidence when deleting a supposedly unused production path;
- `make test`, scoped lint, a final caller search, and `git diff` review.

Passing tests prove only what they exercise. Report local, integration, parity, client, and runtime evidence separately.

## Hard stop rules

- Do not delete an externally reachable or persisted path whose callers are unverified.
- Do not collapse distinct domain lifecycles merely to produce one flow.
- Do not preserve a dead wrapper by making it cleaner.
- Do not add speculative extension points, adapters, or generic frameworks.
- Do not cross an ADR, schema, auth, or public-contract boundary without explicit authority.
- Stop and report when legacy behavior is ambiguous or contradictory; do not guess.

## Return format

Report:

1. intended end state;
2. paths deleted and the evidence for each;
3. compatibility deliberately retained and why;
4. changed files and verification evidence by tier;
5. remaining unknowns, migration conditions, rollout risk, and rollback path.

## Example

An unused wrapper with no code caller, registration, serialized reference, configuration, or external journey can be deleted once tests exercise the direct interface. A tolerant auth form or legacy payload field with no local caller is not dead until supported clients and persisted data have been checked.

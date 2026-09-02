# Complexity and Dosage Design

**Status:** Approved in conversation on 2026-09-02.

## Problem

Jimmy Kit currently contains two semantic gaps:

1. The operating workflow says skills are dosed by risk, while the README, usage guide, and eager dispatcher still imply that every build or pitch must pass through `product-council`.
2. The engineering kernel has deep-module and testability vocabulary, but it does not explicitly distinguish essential from accidental complexity, scan the five common complexity axes, or explain when functional and object-oriented techniques reduce versus isolate complexity.

## Decision

- Keep the kit paradigm-neutral. Do not add standalone OOP, FP, React, or TypeScript framework skills.
- Add a focused complexity-management reference to `codebase-design`.
- Treat Functional Core / Imperative Shell as a heuristic, not a mandatory architecture.
- Preserve OOP as a first-class option for TypeScript backends: design messages, roles, and contracts before classes; use objects for state ownership, lifecycle, coordination, DI boundaries, and adapters; prefer composition over inheritance.
- Interpret "FP reduces complexity" narrowly: explicit data flow reduces hidden mutation, temporal coupling, unnecessary effects, and implicit dependencies; it does not remove essential rules or guarantee less code.
- Interpret "OOP isolates complexity" conditionally: use encapsulated roles for necessary state/effects; keep state ownership shallow and avoid free-form mutable object graphs.
- Keep React coverage to one boundary example: pure state transitions in the core and hooks/effects/adapters in the shell.
- Keep `tdd-go` as the Go implementation owner. Non-Go implementations use the target project's test-first workflow; the kit must not route TypeScript or React code to `tdd-go` merely because behavior is accepted.
- Make `product-council` conditional: Tier 3, explicit red-team/pitch requests, or consequential product/platform decisions. Tier 1 may use no skill; Tier 2 normally uses one or two.

## Required behavior

### Complexity decision

When complexity is central to a design or refactor, the agent records:

- essential versus accidental complexity;
- relevant axes: shared mutable state, side effects, dependencies, control flow, code size;
- treatment per axis: reduce, isolate, or accept;
- core/shell boundary when useful;
- messages, roles, and contracts before class hierarchy;
- verification by layer: direct tests for pure core, boundary fakes or integration tests for shell/adapters, and critical-flow end-to-end tests.

The agent must not force Functional Core / Imperative Shell onto simple CRUD or other already-local, low-risk code.

### Dosage decision

- Tier 1: act directly or use one short skill; no council by default.
- Tier 2: announce and proceed with one or two relevant skills; council only when the decision itself needs red-team review.
- Tier 3: use the full intake and council gate.
- Stop when the current skill resolves the decision; linked skills are conditional routes, not a pipeline.
- Native skill discovery follows the same rule: `product-council` metadata must not trigger on ordinary feature work, Tier 1 edits, or already-approved Tier 2 implementation.

## Verification

- Deterministic audit rejects unconditional council language, stale inventory counts, missing complexity fields, and non-Go routing to `tdd-go`.
- Scenario checks cover a trivial UI edit, a normal tracking change, a Tier 3 product decision, a TypeScript backend design, a Go design, and a simple CRUD counterexample.
- Existing routing, orchestration, metadata, link, language, path, and syntax checks remain green.

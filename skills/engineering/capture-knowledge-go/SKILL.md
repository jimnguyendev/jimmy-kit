---
name: capture-knowledge-go
description: Capture structured understanding of a Go entry point (file, package, feature, endpoint, job) into a Markdown brief under .jimmy/knowledge/. Use when onboarding to unfamiliar code, before refactoring something you have not worked with, or as the discovery step of a larger task like `port-service`. Project-local, no database required.
---

# Capture Knowledge (Go, project-local)

Build structured understanding of a Go entry point and save it as `.jimmy/knowledge/<name>.md`. Analysis-first: do not write the brief until exploration is complete.

This is a **stripped-down adaptation** of the generic capture-knowledge skill — no SQLite, no FTS, no cross-session DB. Just one Markdown file per entry point, version-controlled or git-ignored as the team prefers.

## Hard rules

- Do not write the brief until step 1–4 are done.
- If the entry point does not exist or is ambiguous, stop and ask. Never guess.
- Honest gaps beat false confidence — list unresolved questions explicitly.

## When to use

- Before refactoring code you have not touched (`zoom-out` is for in-conversation context; this skill produces a durable artifact).
- During onboarding to an unfamiliar package / feature.
- As the **discovery step** inside `port-service`, `improve-arch-go`, or a large `tdd-go` planning round.
- When the user says "understand this", "map this module", "document how X works", "capture knowledge".

## Workflow

### 1. Gather + validate

- Confirm the entry point with the user. Acceptable: file path, package path, feature name (`internal/feature/<name>`), endpoint (`POST /v1/...`), job name, gRPC method.
- Confirm depth: **shallow** (overview + top deps), **standard** (overview + deps depth 2 + risks), **deep** (overview + deps depth 3 + diagrams + improvements).
- Check if a brief already exists at `.jimmy/knowledge/<name>.md`. If yes, surface it and ask: refresh, update sections, or start fresh?

### 2. Collect source context

Read just enough to characterize, not every line. Use `grep`/`Read` directly (small scope) or launch `Agent subagent_type=Explore` (large scope).

- For a **file**: exports, key types, who imports it.
- For a **feature**: every file under `internal/feature/<name>/` (the layout is fixed by CLAUDE.md), the `Deps` struct, route registration in `cmd/app/http.go`.
- For an **endpoint**: handler → service → repo chain, middleware applied at the route group, error shapes returned.
- For a **job**: `internal/jobs/<name>/run.go` + registry entry in `cmd/app/job.go`.
- For a **gRPC method**: proto file + server impl + interceptors.

Note the framework boundaries: Gin, mongo-driver/v2, prep-go-log, franz-go (Kafka), go-redis. Anything outside these is unusual and worth a note.

### 3. Analyze dependencies (depth = chosen scope)

- Internal imports: other `internal/feature/*`, `internal/*`, `pkg/*`.
- External: third-party Go modules — flag any not in `backend-go-popular-libraries` recommendations.
- Runtime deps: Mongo collections accessed, Redis keys, Kafka topics, gRPC clients, env vars consumed.
- Flag: circular imports, feature-to-feature direct imports (violates CLAUDE.md), middleware importing a feature's full surface.

### 4. Synthesize

Identify:
- **Purpose** — what the entry point does in one sentence, in domain language from `CONTEXT.md` if present.
- **Core logic** — execution flow, key branches, error paths.
- **Patterns** — which CLAUDE.md / team skill-pack patterns are followed; which deviate.
- **Risks** — missing `context.WithTimeout`, repo returning raw `bson.M`, handler doing semantic validation, no rate limit, no idempotency, etc.
- **Improvements** — concrete next steps (cross-ref `improve-arch-go` candidates).
- **Open questions** — things you could not resolve from the code alone.

### 5. Write the brief

`mkdir -p .jimmy/knowledge && write .jimmy/knowledge/<kebab-name>.md` using the template below. Normalize the name (`internal/feature/example` → `feature-example`; `POST /v1/scores` → `endpoint-post-v1-scores`).

Include Mermaid only when a flow has ≥3 decision points or the dependency graph is non-trivial — otherwise prose + lists are clearer and cheaper.

## Output template

````markdown
# Knowledge: <entry point>

> <one-line summary in domain language>

## Overview
- **Entry point**: <path / identifier>
- **Kind**: file / package / feature / endpoint / job / gRPC method
- **Depth**: shallow / standard / deep
- **Date captured**: <YYYY-MM-DD>
- **Captured by**: <git user>

## Purpose
<1-2 sentences>

## Execution flow
<numbered steps from entry to response/return; or a Mermaid sequenceDiagram for ≥3 branches>

## Dependencies
### Internal
- `internal/...` — why
### External (Go modules)
- `github.com/...` — why
### Runtime
- Mongo collections: `...`
- Redis keys / patterns: `...`
- Kafka topics: `...`
- gRPC clients: `...`
- Env vars: `...`

## Patterns observed
- ✅ Follows: <CLAUDE.md / skill name>
- ⚠️ Deviates: <where + why noted>

## Risks
- <severity> <one-line description>

## Improvements (deferred)
- <suggestion> → candidate for `/improve-arch-go` or `/tdd-go`

## Open questions
- <question>

## Related briefs
- `[[other-brief-name]]` — relationship
````

## Guardrails

- Cap each section short. The brief is a launchpad, not a textbook.
- Cross-link related briefs with `[[name]]` — even if not written yet.
- Re-running this skill on the same entry point updates the brief; preserve `Date captured` history by appending a "Revisions" subsection.

## Cross-references

- `port-service` — uses this skill as the discovery step for each entry point in scope.
- `improve-arch-go` — turns the "Improvements" section into formal candidates.
- `grill-with-docs` — owns `CONTEXT.md`; this skill consumes its vocabulary.
- `tdd-go` — pre-reads the brief during planning step.
- `zoom-out` — in-conversation alternative when you do not need a durable artifact.

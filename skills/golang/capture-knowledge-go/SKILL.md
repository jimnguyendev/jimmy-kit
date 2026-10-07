---
name: capture-knowledge-go
description: >-
  Capture a durable brief of how one Go entry point (file, package, feature, endpoint, job,
  gRPC method) works. Use when onboarding to unfamiliar Go code, before refactoring code you
  have not worked with, or as the discovery step of a migration or architecture review.
---

# Capture Knowledge (Go, project-local)

> **This skill exists to stop:** a refactor or port starting from a guessed picture of the code, and the understanding from one session evaporating before the next.

## 🤖 0. HOW TO USE

- **Capture** (default): one entry point → one brief at `.jimmy/docs/knowledge/<name>.md`.
- **Refresh**: an existing brief → update changed sections and append a Revisions entry.

Output: one Markdown brief per entry point. Done when every section is filled or its gap is listed under Open questions.

Build structured understanding of a Go entry point and save it as `.jimmy/docs/knowledge/<name>.md`. Analysis-first: do not write the brief until exploration is complete.

No database or index: one Markdown file per entry point, version-controlled or git-ignored as the team prefers.

## Hard rules

- Do not write the brief until step 1–4 are done.
- If the entry point does not exist or is ambiguous, stop and ask. Never guess.
- Honest gaps beat false confidence — list unresolved questions explicitly.

## When to use

- Before refactoring code you have not touched (`zoom-out` is for in-conversation context; this skill produces a durable artifact).
- During onboarding to an unfamiliar package / feature.
- As the **discovery step** inside a migration, an `improve-codebase-architecture` review, or a large `tdd-go` planning round.
- When the user says "understand this", "map this module", "document how X works", "capture knowledge".

## Workflow

### 1. Gather + validate

- Confirm the entry point with the user. Acceptable: file path, package path, feature name (`internal/feature/<name>`), endpoint (`POST /v1/...`), job name, gRPC method.
- Confirm depth: **shallow** (overview + top deps), **standard** (overview + deps depth 2 + risks), **deep** (overview + deps depth 3 + diagrams + improvements).
- Check if a brief already exists at `.jimmy/docs/knowledge/<name>.md`. If yes, surface it and ask: refresh, update sections, or start fresh?

### 2. Collect source context

Read just enough to characterize, not every line. Use `grep`/`Read` directly (small scope) or launch `Agent subagent_type=Explore` (large scope).

- For a **file**: exports, key types, who imports it.
- For a **feature**: every file in the feature's package (the layout the repo's AGENTS.md or CLAUDE.md fixes), its dependency struct, and where its routes or handlers are registered.
- For an **endpoint**: handler → service → repo chain, middleware applied at the route group, error shapes returned.
- For a **job**: the job's run function and where it is registered or scheduled.
- For a **gRPC method**: proto file + server impl + interceptors.

Note the framework boundaries the repo declares (router, database driver, logger, message client, cache client) from its instructions and `go.mod`. A dependency outside that set is unusual and worth a note.

### 3. Analyze dependencies (depth = chosen scope)

- Internal imports: other `internal/feature/*`, `internal/*`, `pkg/*`.
- External: third-party Go modules — flag any not in `backend-go-popular-libraries` recommendations.
- Runtime deps: tables or collections accessed, cache keys, topics, gRPC clients, env vars consumed.
- Flag: circular imports, feature-to-feature direct imports the repo's rules forbid, middleware importing a feature's full surface.

### 4. Synthesize

Identify:
- **Purpose** — what the entry point does in one sentence, in domain language from `CONTEXT.md` if present.
- **Core logic** — execution flow, key branches, error paths.
- **Patterns** — which repo rules (AGENTS.md / CLAUDE.md) and `backend-go-*` conventions are followed; which deviate.
- **Risks** — missing `context.WithTimeout`, a repository leaking driver types (`bson.M`, `sql.Rows`), a handler doing domain validation, no rate limit, no idempotency, etc.
- **Improvements** — concrete next steps (candidates for `improve-codebase-architecture`).
- **Open questions** — things you could not resolve from the code alone.

### 5. Write the brief

`mkdir -p .jimmy/docs/knowledge && write .jimmy/docs/knowledge/<kebab-name>.md` using the template below. Normalize the name (`internal/feature/example` → `feature-example`; `POST /v1/scores` → `endpoint-post-v1-scores`).

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
- Tables / collections: `...`
- Cache keys / patterns: `...`
- Topics: `...`
- gRPC clients: `...`
- Env vars: `...`

## Patterns observed
- ✅ Follows: <repo rule / skill name>
- ⚠️ Deviates: <where + why noted>

## Risks
- <severity> <one-line description>

## Improvements (deferred)
- <suggestion> → candidate for `improve-codebase-architecture` or `tdd-go`

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

- `improve-codebase-architecture` — turns the "Improvements" section into formal candidates.
- `grill-with-docs` — owns `CONTEXT.md`; this skill consumes its vocabulary.
- `tdd-go` — pre-reads the brief during planning step.
- `zoom-out` — in-conversation alternative when you do not need a durable artifact.

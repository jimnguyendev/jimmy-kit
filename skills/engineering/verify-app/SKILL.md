---
name: verify-app
description: >-
  Build or maintain a project-local verification skill that drives the real app the way its user or
  client does and keeps the proof. Use when a repo has no scripted way for an agent to prove UI, CLI,
  API, webhook or consumer behavior, when agents keep asking a human to run the app and paste results,
  or when an existing verify skill or its feature map has drifted from the app.
---

# Verify App

> **This skill exists to stop:** a change being reported done from a green suite or the agent's own summary while a human starts the app, clicks through it, and pastes screenshots and logs back — the human becomes the verifier and nothing can run in parallel.

## 🤖 0. HOW TO USE

- **Create** (default when the repo has no `verify-<app>` skill): interview the repo, generate the skill and its feature map, run it once end to end. Sections 1–4.
- **Maintain** (an existing `verify-<app>` skill, or "audit the verify skill"): follow [references/maintain.md](references/maintain.md).

Output of Create: `<target skills dir>/verify-<app>/SKILL.md` plus `features/` in the target repo's own agent skills directory (the one its agents already load: `.claude/skills/`, `.agents/skills/`, `.cursor/skills/`; ask if none exists), and evidence from the proving run under `.jimmy/work/verify-<app>/evidence/<run-id>/`. The generated skill lives with the project's skills because agents must load it; it is the one Jimmy Kit output that does not sit under `.jimmy/`.

Done when the generated skill ran once end to end, its evidence survived cleanup, and its feature map passes the checker. A generated skill that never ran is a draft.

## 1. Interview the repo, not the user

Answer from the code first. Ask only for what cannot be observed: credentials, provisioned test accounts or purchases, which of several surfaces matters most.

| Question | Where to look |
|---|---|
| Surface: what does a user or client touch? | routes, CLI commands, screens, public API, consumed topics, inbound webhooks |
| Run: how does it start locally? | README quickstart, Makefile, package scripts, compose files, env examples, migrations, seed data |
| Drive: how can an agent act on it? | existing e2e or integration harnesses first; then CDP or a device tool for UI, a PTY or tmux session for CLI/TUI, HTTP for APIs, recorded messages for consumers |
| Observe: what proves an outcome? | responses, screen state, exit codes, stored rows, emitted messages, logs |
| Isolate: can two runs coexist? | ports, data directories, database names, topic and consumer-group names |

If the checkout does not build or start, fix that or report it precisely before generating anything. A recipe written against a broken base teaches wrong steps.

## 2. Generate the skill

Write `verify-<app>/SKILL.md` following the target repo's own skill conventions (if it uses Jimmy Kit's, open with the failure statement and HOW TO USE) with frontmatter (`name: verify-<app>` and a description naming the app, the surface and when to use it) and these sections, every command taken from this repo, no placeholders:

- **Launch** — the exact start command, the readiness signal (log line, port, health route), and teardown. A short-lived CLI has no server: build once, then give each drive its own session.
- **Doctor** — one read-only check that answers "is this instance worth driving?": process up, expected build or commit, ports owned by this run, dependencies reachable, and required versions *compared*, not just printed (database engine, migration state; see `reality-gate` mechanism 7). Run it before the first drive and after any surprising result.
- **Drive** — the harness recipe with stable handles: accessible names, data attributes, prompt strings, routes, message keys. No screen coordinates or tab order. Every probe carries its own time limit (`curl --max-time`, a deadline around container and database calls), so one hung call cannot outlast the run's polling deadline.
- **Evidence** — what to capture and where (`.jimmy/work/verify-<app>/evidence/<run-id>/`). Capture the action and the resulting state, including side effects (rows written, messages emitted, files created). Drive the real user path, not internal setters or test-only routes. When the safe path is a dry-run or sandbox mode, observe what it actually skips instead of trusting its name.
- **Cleanup** — stop only what this run started (never kill by process name), remove scratch data, keep the evidence.
- **Helpers** — every shipped script is executable and its invocation appears in the skill body. Where the repo has a task runner, add one target that runs launch, doctor, the mapped checks and cleanup in sequence, so a later agent can prove a change with one command and still open the per-step evidence. Copy this skill's `scripts/check_feature_map.py` into `verify-<app>/scripts/` so Maintain mode can run it without Jimmy Kit installed.

Backend services, webhooks, async pipelines and time-dependent states need more than this list: read [references/service-recipes.md](references/service-recipes.md) before writing Drive and Evidence for them.

## 3. Seed the feature map

Create `features/README.md` (baseline preconditions, driving conventions, proof rules, an index) and one file per user- or client-visible feature, three to five to start. Each feature file has exactly these H2 sections, in order:

1. `Sub-features` — one short ID per behavior (`renewal-extends`, `renewal-duplicate`).
2. `How to get to it` — every entry point a user or client uses.
3. `Driving it with <harness>` — starts with `Preconditions:`, then each action paired with its exact command and the observable result.
4. `Gotchas` — traps that waste or invalidate a run.

Name user paths, stable handles, required state, commands and observable proof; keep implementation detail out. A skipped entry point is reported as skipped, never as verified through another path. See [references/feature-map-example/](references/feature-map-example/README.md) for a service-shaped example, then run `python3 verify-<app>/scripts/check_feature_map.py verify-<app>/features` from the target skills directory. Every sub-feature ID must appear next to a Drive step or on a `Skipped: \`id\` — reason` line.

## 4. Prove it before handing over

Follow the generated skill end to end once: Launch, Doctor, drive one mapped feature, capture evidence, Cleanup. Confirm the evidence still exists at its named location after cleanup. Then prove the failure path once and keep it as evidence: one deliberately wrong expectation must report failure with the reason and a non-zero exit, and a Doctor run against a stopped or tampered instance must refuse to pass; Cleanup must still leave nothing running. Run the generated Cleanup after every failed attempt too, so broken runs do not strand processes or ports. A prerequisite you could not obtain (credentials, a sandbox purchase) is reported as incomplete coverage with what was tried.

Then point the user at Maintain mode for keeping the map honest as the app changes.

## 5. Hand-offs

- `reality-gate` decides what counts as acceptable evidence for a seam; this skill supplies the executable recipe that produces it.
- `diagnose` Phase 1 reuses a matching Drive recipe as its feedback loop, keeping a narrower failing test where one is cheaper.
- `quality-gates` reads the evidence directory; a run without it is exit 2.

## Applied context (edtech)

For a course app's subscription service, typical features are: account token issue, purchase verify, store renewal notification, expiry and grace, entitlement read. The feature-map example uses exactly that shape.

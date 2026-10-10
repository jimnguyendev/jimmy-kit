# Scenario — verify-app (written BEFORE the skill)

**Rationale:** agents finish a change, report it done from a green suite or their own summary, and leave a human to start the app, click through it, and paste screenshots or logs back. The human becomes the verifier and the bottleneck, so work cannot run in parallel. The skill must produce a project-local recipe that lets the next agent drive the real app the way its user or client does and keep the proof.

## Case 1 — Create, backend service with store webhooks

**Sample input:** "This repo is a Go subscription service (PostgreSQL, outbox to Kafka, an entitlement consumer, App Store and Google Play notifications). Make it verifiable by agents: I want an agent to prove a renewal end to end without me."

**Expected behaviors:**
- [ ] Interviews the repo, not the user: finds the documented run command, ports, env, migrations, existing integration harnesses, and asks only what the code cannot answer (sandbox credentials, provisioned purchases).
- [ ] Writes the generated skill into the target repo's own agent skills directory with Launch, Doctor, Drive, Evidence, Cleanup and Helpers sections, and evidence under `.jimmy/work/verify-<app>/evidence/<run-id>/`.
- [ ] Doctor compares (not just prints) the running PostgreSQL version and migration state with what the repo requires, and checks topic, consumer group, provider configuration and clock mode.
- [ ] Does not treat Apple `TEST` or Google `testNotification` as renewal proof; uses a genuine sandbox renewal or replays captured signed renewal bytes through the production handler, never by disabling signature checks.
- [ ] Waits on observables with a bounded timeout (subscription row, outbox row, topic message with key and offset, entitlement read), never a fixed sleep.
- [ ] Seeds a feature map with one file per client-visible behavior, each with the four required sections, and passes `scripts/check_feature_map.py`.
- [ ] Runs the generated skill once end to end and confirms the evidence survives cleanup; a missing prerequisite is reported as incomplete coverage, not as a pass.

## Case 2 — Maintain after drift

**Sample input:** "The verify skill for our web app is three months old and the settings page moved. Audit it."

**Expected behaviors:**
- [ ] Reads the source per feature file (bounded concurrency, serial fallback), then drives every mapped feature live at least once.
- [ ] Sorts findings into doc drift (fix the map), harness gap (fix the harness), product gap (report, do not paper over in docs).
- [ ] Ships at most one change set limited to the verify skill's own directory, or reports `clean` or `blocked` with the reason.

## Case 3 — Should NOT trigger

**Sample input:** "Write a unit test for this pure function."

**Expected behavior:** `tdd-go` or the project's test workflow handles it; verify-app is not loaded.

**Status:** Case 1 generic-service path [PASS — 2026-10-07, blind run below]; Case 1 webhook-specific behaviors and Case 2 [EXIT 2 — not yet exercised: the target had no store integration, and no stale verify skill existed to maintain].

## Run 2026-10-07 — blind comparison against a no-skill baseline

- **Target:** two clean copies of a Go HTTP service template (Gin, PostgreSQL/MySQL, Redis, migrations, an example CRUD feature), neutral names, separate ports. Variant B had this skill installed (without SCENARIO.md) and one dispatcher row in AGENTS.md; variant A had nothing.
- **Prompt (both):** "Every time an agent changes this service, I have to start it myself, call the endpoints, check the database and paste the output back. I want agents to be able to prove a change actually works on the running service by themselves. Set that up in this repo, and show me it works by actually running it once."
- **Candidates:** same model, same tools, run in parallel. **Judge:** a different model family, saw diffs, new files, evidence and summaries under labels A/B with a seven-criterion rubric. **Limitation:** B's files name the skill, so the judge could infer which variant used it.
- **Result:** B 19/21, A 11/21. B produced a project-local skill with a version-comparing Doctor, per-run containers and cache prefix, 48 numbered evidence files kept after cleanup, a feature map passing the checker with two explicit skips, and three real service defects reported but not patched. It followed the repo's own path mapping for `.jimmy/work/` (evidence under the repo's mapped work folder), which is the intended precedence. A produced a solid one-command runner with bounded readiness waits and a deliberate failing check, but kept no evidence beyond terminal output and had no comparing Doctor or coverage map.
- **Changes from this run:** Drive now requires a per-probe time limit; section 4 requires a recorded failure-path proof; Helpers suggests a one-command target (the strongest part of A).


## Case 4 — Delegated verification on a shared machine (written BEFORE the 2026-10-10 change)

**Sample input:** "Five frontend packets just landed while two executors still run. Verify every page against the design on the real service."

**Expected behaviors:**
- [ ] The orchestrating agent hands driving to ONE verification subagent that owns one browser (its own CDP port and profile directory) and its own service ports; it does not open a browser per page or per packet.
- [ ] The subagent returns a verdict per page and evidence paths, not DOM dumps or inline screenshots; the orchestrator reads the evidence and drives itself only where a judgement is needed.
- [ ] No executor opens a browser; the verification run never attaches to a browser another agent uses.

**Status:** [EXIT 2 — specified] Origin evidence: on one machine about ten executor browsers overloaded it, and a tool that acts on the active tab read another packet's screen; the root's own driving filled most of a 1M-token context. One verification agent with one browser then verified 16 pages in two rounds.

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

**Status:** [EXIT 2 — scenario specified; no independent fresh-agent run recorded yet].

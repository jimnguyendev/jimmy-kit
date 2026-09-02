# Scenario — orchestrate (written BEFORE the self-contained-test correction)

**Rationale:** a bundled linter test must not depend on one developer's gitignored `.orchestrate/` runtime state.

**Sample input:** "Clone Jimmy Kit into a clean directory and run the orchestration linter unit tests."

**Expected behaviors:**
- [ ] Tests load contract, plan, packet, and document-coverage sources bundled under the skill.
- [ ] A valid review and dispatch fixture passes.
- [ ] Each planted contract, metadata, approval, and document-coverage defect fails with the expected code.
- [ ] No repository-root `.orchestrate/` state is required or created.

**Status:** [PASS — exit 0] Baseline 2026-09-02: 17/17 tests errored because `.orchestrate/contracts/100-orchestrate-flow-v2.json` was absent. Fixed run 2026-09-02: 17/17 passed in 0.521s using bundled fixtures.

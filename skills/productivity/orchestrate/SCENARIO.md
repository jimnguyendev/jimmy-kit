# Scenario — orchestrate (written BEFORE the self-contained-test correction)

**Rationale:** a bundled linter test must not depend on one developer's gitignored `.orchestrate/` runtime state.

**Sample input:** "Clone Jimmy Kit into a clean directory and run the orchestration linter unit tests."

**Expected behaviors:**
- [ ] Tests load contract, plan, packet, and document-coverage sources bundled under the skill.
- [ ] A valid review and dispatch fixture passes.
- [ ] Each planted contract, metadata, approval, and document-coverage defect fails with the expected code.
- [ ] No repository-root `.orchestrate/` state is required or created.

**Status:** [PASS — exit 0] Baseline 2026-09-02: 17/17 tests errored because `.orchestrate/contracts/100-orchestrate-flow-v2.json` was absent. Fixed run 2026-09-02: 17/17 passed in 0.521s using bundled fixtures.

## External routing adapter removal

**Sample input:** "Remove the external role-routing plugin integration from Jimmy Kit and the Go starter kit; keep unrelated skills."

**Expected behaviors:**
- The generic orchestrate skill remains available with its local packet and verification templates.
- The removed adapter and its required references are absent from source and installed skills.
- Both symlink and copy installations retain all 94 skills, including Go testing and reality-gate.
- The Go starter kit rejects an older skill source containing the removed integration before changing its destination.

**Status:** [PASS — exit 0, structural distribution checks] 2026-10-08: `python3 scripts/audit-repository-contract.py` passed with 94 skills, nine vendored skills, and both symlink/copy installation smoke checks. `go test -count=1 -v . ./internal/scaffold` in the Go starter kit passed: stale adapter and stale reference sources were refused without changing the destination; updated source sync/install and default skill rendering passed. The retained orchestration linter passed 17/17 tests. This verifies distribution and references, not a new model-behavior evaluation.

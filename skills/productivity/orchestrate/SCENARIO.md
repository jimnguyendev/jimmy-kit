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

## Bounded live workflow corrections

**Sample input:** "Fix reachable workflow failures without restoring the removed role-routing plugin."
**Expected:** recon observations match expected fields before review; draft plan/packet/contract metadata is checked before a reviewer call; executor workspace and temporary-directory access are checked before dispatch; review findings separate material impacts from editorial preferences; progress names files, test results, and real blockers. Explicit approval requirements remain binding.
**Status:** [UNVERIFIED — exit 2 for instruction behavior] 2026-10-08: automated linter checks passed 20/20 and Go Advisor launcher checks passed 4/4. Before the code fixes, the missing/wrong-observation checks and stale-plan/pending-recon launcher checks failed because the unsafe inputs were accepted. Plain briefs, consistent contracts, and extra observed evidence remain supported. No model-behavior evaluation was run for the instruction changes; explicit approvals remain required.

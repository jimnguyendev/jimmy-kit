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

## Multi-packet build on a shared machine (written BEFORE the 2026-10-10 skill changes)

**Rationale:** a root orchestrating a Go service plus a React admin (about 40 packets, three executor routes, one machine, one 1M-token root context) hit failures the skill did not prevent: executor worktrees created in the wrong repository, packets landed on executor gate reports because the land script ran no gates, a clean git merge that did not compile, a queue plan with 15 advisor findings the root considered done, a backend column never persisted while every test was green, about ten executor browsers on one machine, a root context filled with DOM trees and screenshots, a background `opencode run` hung on stdin, every subagent stopped by a session limit, and a first load test after 35 packets that found four bottlenecks the packets themselves caused.

**Sample input:** "Orchestrate the rest of this service: 12 backend packets (one is a dispatcher with leases and retries), 6 frontend packets from a claude.ai Design project. Run what can run in parallel. The session cwd is a different repo."

**Expected behaviors:**
- [ ] Root creates one `git worktree add` per packet in the target repo and puts the absolute worktree and packet paths in the dispatch prompt; it does not rely on the Agent tool's worktree isolation.
- [ ] Auth/context seams that several packets need land on main first, with a local-only mock, before the parallel wave.
- [ ] The dispatcher plan goes to an Advisor from a different model family that reads the repo; contract-level findings land as contract + ADR changes on main before the packet is written.
- [ ] Every packet carries `Volume and budget`; the send-path and ledger-query packets state data volume at 13 months, a latency/throughput target, and the load run or EXPLAIN that proves it, and the linter rejects a packet without the section.
- [ ] Land runs the bundled `land.sh`: merge main, run every gate from the gate list, merge with the head SHA after the forge reports mergeable, remove the worktree only after the merge succeeded.
- [ ] Executors never open a browser; one verification subagent with one browser drives the frontend on the real service before landing and returns a verdict and evidence paths; root looks at every frontend land in that one browser.
- [ ] Easy backend packets go to opencode with `-m <model>`, `< /dev/null`, and inputs copied into the worktree; all frontend goes to Sonnet; hard packets and root use Opus.
- [ ] FE packets point at a design spec the root exported to the repo with DesignSync `get_file` and `scripts/extract-design.py`, not at canvas screenshots.
- [ ] HANDOFF.md is refreshed after every land; the PreCompact / SessionStart:compact hook restores state after compaction; after a session limit the root resumes each stopped agent with SendMessage.

**Status:** [EXIT 2 — scripts PASS, instruction behavior unverified] The rules come from the origin run's learnings log (one run, one root; not an independent fresh-agent run of this revision). Bundled scripts are covered by `scripts/test_orchestrate_scripts.py` and the linter change by `scripts/test_orchestration_lint.py`.
2026-10-10 runs: `test_orchestrate_scripts.py` 15/15 passed (gates pass/fail/usage; land refuses a dirty worktree, the main checkout and a failing gate with nothing pushed, merges with the head SHA after merging a moved main, keeps the worktree when the merge is refused; context hook snapshot/resume/targets/silent; design export byte-exact, refuses path escape). Mutations confirmed the tests bite: with the gate call removed from `land.sh` the gate-failure test failed, and with `--match-head-commit` removed the success test failed. `test_orchestration_lint.py` 25/25 passed; with the Volume and budget check disabled, three of its new tests failed. No model-behavior evaluation of the instruction changes was run.

## Owner questions as decision briefs (written BEFORE the 2026-10-11 change)

**Rationale:** in the same multi-packet build the root asked the owner to decide with one-liners: "open the PR on the skill kit? accept ADR-0017?", six tech-debt items each one line long with jargon, and "this way, or limit per week?". The owner had to ask what each question meant. The root also resumed after compactions straight into new questions without saying what had happened.

**Sample input:** "Wave 3 has landed. Report, and tell me what you need from me." Four items are pending; two are the root's own engineering calls.

**Expected behaviors:**
- [ ] The root decides its own engineering calls and reports them as decided, with a one-line reason.
- [ ] Each remaining question is a decision brief from skill `ketchup`, in chat, in AskUserQuestion (brief in the message, decision sentence as the question), and in HANDOFF's `Waiting on owner` section.
- [ ] `orchestration_lint.py --phase handoff --handoff .orchestrate/HANDOFF.md` passes; a brief missing a part, an option without cost or effect, or a bare id like `ADR-0017` that the brief never explains fails it.
- [ ] After a compaction-resume or a long silence, the first owner-facing message follows `/ketchup`: action-item count, what happened, then the briefs.

**Status:** [EXIT 2 — specified; no run recorded yet].

# Scenario — write-a-skill

## 2026-09-16 refactor scenario (written BEFORE skill changes)

**Status:** [EXIT 2 — specified; independent application not yet recorded for this revision].

**Input 1:** Create a Jimmy Kit skill from a demonstrated failure with a clear user request.

**Expected:** Read local conventions, write SCENARIO first, include failure statement and HOW TO USE, validate links and behavior; do not ask again for supplied requirements.

**Input 2:** Improve a description without changing the workflow.

**Expected:** Keep a precise trigger and proportionate validation, not a universal full test pipeline.

## 2026-10-07 blind evaluation scenario (written BEFORE skill changes)

**Status:** [EXIT 2 — specified; independent application not yet recorded for this revision].

**Input 3:** Evaluate whether a changed skill improves agent behavior, comparing it with the previous version and a no-skill baseline.

**Expected:** Follows `references/blind-eval.md`: the candidate workspace contains the skill without its SCENARIO.md or evals; the prompt reads like an ordinary request; expected outputs and the label-to-variant map stay with the coordinator; a judge from a different model family scores outputs by neutral label when one is available, and the limitation is recorded when not; tool use is graded from transcripts, not from the candidate's own account; the coordinator reads every output and reconciles disagreements with the judge.

**Application 2026-10-07 (by the protocol's author, so not an independent run):** used for the `verify-app` comparison recorded in that skill's SCENARIO: separate neutral workspaces, the skill copied without its SCENARIO, one ordinary prompt, same candidate model, a judge from another model family scoring by label with the rubric held back, and the coordinator reading both outputs before accepting the verdict. Gap found: the candidate's own files named the skill, which a neutral label cannot hide. Status unchanged: exit 2 until a fresh agent applies the protocol.


# Scenario — handoff

## Pending owner decisions as decision briefs (written BEFORE the 2026-10-11 change)

**Rationale:** a handoff that lists "waiting on owner: accept ADR-0017? open the PR?" passes the same uninformative question to the next session, which then asks the owner the same way. The next agent cannot explain what it did not write.

**Sample input:** "Write a handoff; the next session continues the notification service. Two things are waiting on me."

**Expected behaviors:**
- [ ] A "Waiting on owner" section with one decision brief per pending decision (decision sentence, what it is, why now, options with cost and visible effect, recommendation, what happens with no answer, evidence), or `None.`
- [ ] Terms and ids in the briefs are explained, so the next agent can relay them without re-deriving them.
- [ ] Decisions the session already took are listed as decided, not as questions.

**Status:** [EXIT 2 — specified; no run recorded yet].

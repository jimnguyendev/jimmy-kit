# Scenario — change-tiers dosage (written BEFORE related routing revisions)

**Rationale:** tiering fails if diff size or the word "build" overrides reversibility, ambiguity, blast radius, and decision cost.

**Sample input:** "Classify these without running a full workflow: fix a typo in an internal label; add an approved tracking event; choose whether to replace the authentication platform."

**Expected behaviors:**

- [ ] The internal typo is Tier 1 and receives no mandatory ceremony.
- [ ] The approved tracking event is Tier 2 because it changes behavior and creates a reviewable contract.
- [ ] Replacing the authentication platform is Tier 3 because it is ambiguous, consequential, and hard to reverse.
- [ ] Skill count grows only with unresolved risk: zero/one for Tier 1, one/two for Tier 2, full intake plus council for Tier 3.
- [ ] The response does not treat every task as a mandatory four-phase chain.

**Status:** [EXIT 2 — scenario specified; no independent fresh-agent run recorded yet].

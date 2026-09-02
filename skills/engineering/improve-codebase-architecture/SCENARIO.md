# Scenario — improve-codebase-architecture (written BEFORE the routing revision)

**Rationale:** architecture discovery can accidentally decide an unsettled product contract, or return a broad refactor recommendation without bounded evidence.

**Sample input:** "Three modules appear to own notification preferences. Rank the architecture candidates, but the public opt-out behavior and migration authority are still undecided."

**Expected behaviors:**
- [ ] Owns discovery and candidate ranking, with files, friction, boundaries, and deletion-test evidence.
- [ ] Classifies essential versus accidental complexity and states whether each candidate reduces, isolates, accepts, or merely relocates it.
- [ ] Does not silently decide the public behavior or migration authority.
- [ ] Routes the open decision to `engineering-design-thinking` with the canonical handoff artifact.
- [ ] Returns to cleanup or TDD only after one candidate and its behavior delta are accepted.

**Status:** [EXIT 2 — scenario specified; no independent fresh-agent run recorded yet].

## Cycle-discovery extension (written BEFORE the philosophy revision)

When discovery finds a module cycle, it must not reflexively extract `common` or add interfaces. It ranks moving responsibility, merging a fake boundary, and introducing a consumer-owned contract at a real seam, then shows whether locality and dependency direction actually improve.

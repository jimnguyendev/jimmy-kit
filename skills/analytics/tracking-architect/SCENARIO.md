# Scenario — tracking-architect (added for the de-branding audit)

## Current revision — 2026-09-16 (K16)

**Status: EXIT 2 — prospective cases; no independent run recorded for this revision.**

**Static baseline finding (not a behavioral run):** Universal Zod/field naming requirements conflict with preserving an existing tracking contract.

**Sample input:** Add an event in a Go service using an existing Protobuf registry with PascalCase names and a versioned envelope; the production funnel export is unavailable.

**Expected behavior:** Extend the existing registry and validation stack; map 5W1H semantics without imposing Zod or renaming events. Mark missing production data unavailable, never zero or verified.

**Validation needed:** run the case with a fresh agent, paste its output and grade each expectation. Static checks alone do not promote this revision to PASS.

## Historical scenarios and results (unchanged)


**Rationale:** bundled templates must remain reusable and brand-neutral.

**Sample input:** "Use the bundled event-schema and funnel-query examples in a generic practice product."

**Expected behaviors:**
- [ ] Examples use generic edtech language.
- [ ] No source-company or internal repository name appears in generated comments.
- [ ] Tracking semantics remain unchanged.

**Status:** [EXIT 2 — scenario specified; no independent fresh-agent run recorded yet].

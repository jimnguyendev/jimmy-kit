---
name: ux-plan-tasks
description: >-
  Use when a full ARCHITECT development plan needs usability validation, accessibility checks, or design review tasks for consequential user-facing flows.
version: "1.0.0"
modes: [architect]
---

# UX Plan Tasks

> **This skill exists to stop:** implementation plans that omit meaningful UX evidence or add ceremonial checks to every component.

## 🤖 0. HOW TO USE

Only ARCHITECT needs dedicated UX planning tasks. BUILD keeps relevant UX acceptance and verification in existing tasks, without invoking the full task sequence below. Input is the current plan plus supplied requirements, user context, and prior findings; named artifact files are optional. Output a scoped task patch, with evidence and dependencies, in the existing plan or `.jimmy/work/<feature>/ux-tasks.md`.

Reuse completed research and accepted scope. Select tasks by unresolved risk in the affected user flow; a phase already supported by adequate evidence needs no duplicate test. Each chosen task names the journey/states, method, completion evidence, and any blocking dependency. A walkthrough is expert evidence, never a claim of actual user research.

Adds UX-specific tasks to an existing development plan. Only activates in ARCHITECT mode — BUILD mode plans are
lightweight and don't need separate UX tasks.

## Mode: ARCHITECT (full)

Review the plan and select relevant UX tasks at appropriate points. The sequence below is a menu; add all phases only when each resolves an actual uncertainty.

### Pre-Implementation UX Tasks

When design uncertainty could cause costly rework, add before the dependent implementation:

**Usability test the design (before code):**
- Task: "Conduct paper prototype / wireframe walkthrough with 3-5 users"
- Inputs: journey map, persona profiles, wireframes (if available)
- Method: Give users the core tasks from the journey map. Watch where they
  get stuck. Note confusion, hesitation, wrong turns.
- Output: Observed usability issues, prioritized by severity (up to 3 highest-impact findings)
- Time: 2-4 hours (including setup and debrief)
- Dependency: Blocks only the implementation whose design decision depends on the findings

If real user testing isn't feasible, substitute:
- Expert walkthrough using the persona + journey map as evaluation lens
- Cognitive walkthrough: step through each task as the primary persona

### Mid-Implementation UX Checkpoints

Insert at meaningful flow milestones, especially async submission, destructive actions, or shared interaction changes. Group related components into one check:

**Heuristic spot-check:**
- Task: "Review [affected user flow] against the Critical Four heuristics"
- Check: feedback, user control, error prevention, error messages
- Time: Estimate from the affected flow and available test environment
- Dependency: Block dependent work only when an unresolved finding would invalidate it

### Post-Implementation UX Tasks

When implementation introduces new interaction or accessibility risk, add before the relevant release decision:

**Usability test the implementation (after code):**
- Task: "Conduct usability test on the implemented feature with 3-5 users"
- Method: Same core tasks as pre-implementation test
- Compare: Did we fix the issues found in the prototype test?
- New issues: Anything the real implementation reveals that the prototype didn't?
- Output: Observed findings report, prioritized fixes, and comparison with prior evidence; use the expert/cognitive walkthrough fallback above when real users are unavailable
- Time: 2-4 hours

**Accessibility audit:**
- Task: "Run automated accessibility checks + manual keyboard navigation test"
- Tools: axe-core, Lighthouse accessibility, manual tab-through
- Check: All interactive elements keyboard-reachable, ARIA labels present,
  contrast ratios met, screen reader announcements work
- Time: 1-2 hours

### Task Ordering

```
illustrative full-flow plan (include only relevant tasks)...
+ [UX] Prototype usability test (before implementation)
  existing implementation tasks...
  + [UX] Heuristic spot-check on [affected flow / risky milestone]
  existing implementation tasks...
+ [UX] Implementation usability test (after implementation)
+ [UX] Accessibility audit
existing verification tasks...
```

## Completion evidence

For each selected task, record what was observed and the result: PASS, FAIL, or UNVERIFIABLE. Evidence may be observed walkthrough notes, actual user-test findings, screenshots, a keyboard/focus trace, screen-reader observations, or accessibility tool output appropriate to the requirement. List unavailable checks rather than claiming completion. Automated accessibility scans alone do not establish compliance. Resolve launch-blocking failures in the affected flow; assign remaining findings and expose material unverified checks for the release decision.

## References

Use `ux-review` heuristic mode for the Critical Four/full review and `ux-discovery`'s interview reference for study planning. The walkthrough methods and task criteria above are sufficient without an external runtime.

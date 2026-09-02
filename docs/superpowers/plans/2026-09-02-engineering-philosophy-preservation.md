# Engineering Philosophy Preservation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Preserve the predecessor engineering philosophy and stack-neutral DAG/cycle-breaking model inside Jimmy Kit.

**Architecture:** Keep a concise human manifesto in README and one operational progressive-disclosure reference under `codebase-design`. Add only context-specific hooks to the engineering owners that make architecture and implementation decisions.

**Tech Stack:** Markdown skills and scenarios, Python standard-library audit, JSON eval specifications.

**Spec:** `docs/superpowers/specs/2026-09-02-engineering-philosophy-preservation-design.md`

## Global Constraints

- No new skill and no inventory change.
- DAG and circular-dependency resolution are stack-neutral; Go is only the compile-time enforcement example.
- Preserve dosage, existing complexity guidance, and user-owned worktree changes.
- Changed skills receive scenario expectations before body edits and stay exit 2 until an independent run is recorded.

---

### Task 1: Scenario-first baseline and audit

**Files:**
- Modify: `skills/engineering/codebase-design/SCENARIO.md`
- Modify: `skills/engineering/engineering-design-thinking/SCENARIO.md`
- Modify: `skills/engineering/improve-codebase-architecture/SCENARIO.md`
- Modify: `skills/engineering/tdd-go/SCENARIO.md`
- Create: `scripts/audit-engineering-philosophy.py`

**Interfaces:**
- Consumes: philosophy and dependency-direction contracts from the spec.
- Produces: observable Go/TypeScript scenarios and deterministic failure evidence.

- [x] Write the pressure scenarios before skill-body edits.
- [x] Run fresh agents on the current kit and record the missing behaviors.
- [x] Write the audit and verify it fails for the missing philosophy.

### Task 2: Canonical philosophy and owner integration

**Files:**
- Modify: `README.md`
- Create: `skills/engineering/codebase-design/references/engineering-philosophy.md`
- Modify: `skills/engineering/codebase-design/SKILL.md`
- Modify: `skills/engineering/engineering-design-thinking/SKILL.md`
- Modify: `skills/engineering/improve-codebase-architecture/SKILL.md`
- Modify: `skills/engineering/tdd-go/SKILL.md`
- Modify: `CONTEXT.md`
- Modify: `docs/DECISIONS.md`

**Interfaces:**
- Consumes: scenario failures from Task 1.
- Produces: one canonical operational philosophy plus short, problem-specific hooks.

- [x] Add the manifesto, seven principles, and stack-neutral cycle remedies.
- [x] Integrate them at design, codebase, architecture-discovery, and Go implementation decision points.
- [x] Keep performance and quality-gate ownership intact without duplicating their workflows.

### Task 3: Behavioral and repository verification

**Files:**
- Modify: scenario files with pasted fresh-run evidence.
- Create: `docs/AUDIT-2026-09-02-ENGINEERING-PHILOSOPHY.md`

**Interfaces:**
- Consumes: integrated philosophy.
- Produces: benchmark, independent review verdict, and merge evidence.

- [x] Run the same Go and TypeScript scenarios with the updated kit.
- [x] Run the new audit and all existing repository gates.
- [x] Request independent review and fix all Critical/Important findings.
- [x] Commit the verified working tree and push the current branch.

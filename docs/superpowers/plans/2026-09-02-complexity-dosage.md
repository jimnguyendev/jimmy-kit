# Complexity and Dosage Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Align Jimmy Kit with risk-based skill dosage and add a paradigm-neutral complexity model that preserves appropriate OOP use in TypeScript backends.

**Architecture:** Extend the existing engineering kernel through one progressive-disclosure reference rather than new paradigm/framework skills. Repair dosage at its three user-facing routing surfaces and enforce both contracts with deterministic checks plus scenario evidence.

**Tech Stack:** Markdown skills and scenarios, Python standard-library audit scripts, JSON eval specifications.

**Spec:** `docs/superpowers/specs/2026-09-02-complexity-dosage-design.md`

## Global Constraints

- Keep canonical upstream skill bodies close to upstream; place kit-specific guidance in appendices or self-authored engineering skills.
- All changed skills have a `SCENARIO.md` written before body changes; status remains exit 2 until a fresh run is recorded.
- Do not add OOP, FP, React, or TypeScript framework skills.
- Keep React coverage to one concise core/shell example.
- Preserve all user-owned worktree changes; commit the combined worktree only after the owner's explicit approval.

---

### Task 1: Scenario-first contracts and failing audit

**Files:**
- Create: `skills/process/routing/SCENARIO.md`
- Create: `skills/process/change-tiers/SCENARIO.md`
- Create: `skills/engineering/codebase-design/SCENARIO.md`
- Modify: `skills/engineering/engineering-design-thinking/SCENARIO.md`
- Modify: `skills/engineering/improve-codebase-architecture/SCENARIO.md`
- Create: `scripts/audit-complexity-dosage.py`

**Interfaces:**
- Consumes: approved behavior in the spec.
- Produces: executable static checks and pressure scenarios for the documentation changes.

- [x] **Step 1: Write scenario expectations before changing skill bodies.**
- [x] **Step 2: Run fresh-context baselines without the new guidance and record the observed failures.**
- [x] **Step 3: Write the deterministic audit for dosage, complexity, stack routing, and documentation consistency.**
- [x] **Step 4: Run the audit and verify that it fails on the current semantic gaps.**

### Task 2: Complexity management and stack-neutral design

**Files:**
- Create: `skills/engineering/codebase-design/references/complexity-management.md`
- Modify: `skills/engineering/codebase-design/SKILL.md`
- Modify: `skills/engineering/engineering-design-thinking/SKILL.md`
- Modify: `skills/engineering/engineering-design-thinking/references/skill-routing.md`
- Modify: `skills/engineering/improve-codebase-architecture/SKILL.md`
- Modify: `skills/engineering/zero-tech-debt/SKILL.md`
- Modify: `skills/engineering/engineering-design-thinking/evals/evals.json`
- Modify: `skills/engineering/improve-codebase-architecture/evals/evals.json`
- Modify: `CONTEXT.md`

**Interfaces:**
- Consumes: complexity fields and stack decisions in Task 1 scenarios.
- Produces: shared `reduce | isolate | accept` model and conditional Go/non-Go implementation handoff.

- [x] **Step 1: Add the minimal complexity reference with essential/accidental, five axes, treatments, core/shell, OOP roles, and testing layers.**
- [x] **Step 2: Link it conditionally from design and architecture discovery rather than imposing it on every task.**
- [x] **Step 3: Make `tdd-go` explicitly Go-only and define a non-Go project-workflow handoff.**
- [x] **Step 4: Add TypeScript backend and counterexample eval cases.**
- [x] **Step 5: Run the focused audit until the complexity and stack checks pass.**

### Task 3: Dosage consistency and final benchmark

**Files:**
- Modify: `templates/eager-dispatcher.md`
- Modify: `docs/OPERATING-WORKFLOW.md`
- Modify: `skills/process/routing/SKILL.md`
- Modify: `skills/product/product-council/SKILL.md`
- Modify: `skills/product/product-council/SCENARIO.md`
- Modify: `README.md`
- Modify: `docs/USAGE.md`
- Modify: `docs/DECISIONS.md`
- Create: `docs/AUDIT-2026-09-02-COMPLEXITY-DOSAGE.md`

**Interfaces:**
- Consumes: dosage scenario contract from Task 1.
- Produces: one consistent Tier 1/2/3 policy across all routing surfaces and an evidence-separated audit report.

- [x] **Step 1: Replace unconditional council language with an observable Tier 3/explicit-red-team condition.**
- [x] **Step 2: Correct inventory and maximal-map language in public documentation.**
- [x] **Step 3: Align native `product-council` discovery with dosage, then run fresh-context post-change scenarios and keep scenario status at exit 2 unless the run is pasted and scored.**
- [x] **Step 4: Run focused and full repository checks, inspect the diff, and record before/after evidence without overstating behavioral proof.**

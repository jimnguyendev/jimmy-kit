---
name: engineering-design-thinking
description: >-
  Decide and approve non-trivial engineering changes before implementation. Use for /design,
  scoping or reviewing a proposed change, solution-shaped requests, new public contracts,
  multi-file features, and unsettled architecture choices.
user-invocable: true
license: MIT
compatibility: "Stack-agnostic; designed for AI coding agents."
metadata:
  version: "1.1.0"
allowed-tools: Read Edit Write Glob Grep Bash(git:*) Agent WebFetch WebSearch AskUserQuestion
---

# Engineering Design Thinking

> **This skill exists to stop:** solution-shaped requests, familiar patterns, and elegant diagrams from replacing a verified problem and an evidence-backed engineering decision.

## 🤖 0. HOW TO USE

Choose one mode:

- **Think** (default): pass all five gates, then present a design brief for acceptance.
- **Review**: score an existing proposal against the gates; do not repair skipped gates silently.
- **Scope**: identify the smallest investigation that can settle the highest-risk gate.
- **First principles**: use when the system is unfamiliar, high-risk, novel, or a familiar pattern conflicts with evidence. Read [first-principles.md](references/first-principles.md).

Outputs: a Problem Frame, option comparison, architecture sketch, accepted-decision handoff, and a post-delivery model update. Do not implement before the design is accepted. Skip the full flow for a small, reversible question whose behavior and boundary are already clear.

## 1. Gate 1 — Frame the problem

Complete [problem-frame.md](references/problem-frame.md). The gate fails unless the frame names:

- the decision owner and affected stakeholders;
- actual state with evidence, expected state, and the gap between them;
- why the gap matters, at the right abstraction level;
- constraints, labelled assumptions, cause hypotheses, and success evidence.

Write the problem without the proposed solution. A stakeholder expectation can be wrong or poorly designed; closing the gap may mean changing reality, expectation, or both.

## 2. Gate 2 — Read the current system

Inspect relevant code, data flow, dependencies, recent history, deployment constraints, and accepted ADRs. Separate:

- `[VERIFIED]` current evidence;
- `[ASSUMPTION]` claims with a way to check;
- conventions or patterns that are useful precedent but not proof.

If architecture health or ownership is unknown, route a bounded evidence question to `improve-codebase-architecture`. Do not invent the missing map.

## 3. Gate 3 — Derive and compare options

List at least two materially different options. If analogy or convention is doing the reasoning, switch to [first-principles.md](references/first-principles.md) and rebuild the options from fundamentals and interactions.

Compare each option using:

```text
Solution Ideality = Benefits / (Resources Required + Harmful Effects)
```

Count time, people, money, infrastructure, coupling, operational load, migration risk, and unknown harmful effects. Do not choose novelty, familiarity, or a numeric ratio without explaining the evidence behind it.

When two desirable properties appear to conflict, apply [contradiction-resolution.md](references/contradiction-resolution.md) before accepting a compromise. Some trade-offs are real; others are removable coupling.

## 4. Gate 4 — Make the architecture decision

When state, effects, dependencies, control flow, or code size are central, read [complexity-management.md](../codebase-design/references/complexity-management.md). Classify essential versus accidental complexity and choose `reduce`, `isolate`, or `accept` per relevant axis. Functional Core / Imperative Shell is one possible result, not the default. Design messages and roles before choosing classes.

When package/module ownership or placement is in scope, read [engineering-philosophy.md](../codebase-design/references/engineering-philosophy.md). Default to business-capability locality, fewer units, short contextual names, types near their owner, and a dependency DAG. A repository's accepted alternative may override feature-first organization, but it must preserve explicit ownership and one-way dependencies. Classify contention as convergent or distributed when concurrency affects the architecture.

Produce a compact sketch:

```text
Feature: user-visible capability
Modules: responsibility and owner of each boundary
Structure: capability locality, evidence for each split, names and type placement
Dependencies: one-way DAG, allowed edges, forbidden reverse edges, cycle treatment
Data flow: happy path and error path
Failure modes: timeout, partial failure, inconsistency, rollback
Decisions: 1-3 non-obvious choices and losing alternatives
```

Prefer fewer, deeper modules; split when evidence shows a distinct capability or change boundary. Resolve a cycle by moving responsibility, merging a fake boundary, or—only at a real independent seam—introducing a consumer-owned contract wired from the composition root. Make external contracts, migration/compatibility policy, contention, observability, and rollback explicit when relevant.

## 5. Gate 5 — Transfer ownership deliberately

Read [skill-routing.md](references/skill-routing.md). Select one current phase owner:

| Current state | Owner |
|---|---|
| Problem, option, contract, boundary, or authority unsettled | `engineering-design-thinking` |
| Architecture evidence or candidate ranking needed | `improve-codebase-architecture` |
| Accepted observable behavior needs Go implementation | `tdd-go` |
| Accepted observable behavior needs non-Go implementation | Target project's test-first workflow |
| Accepted behavior-preserving cleanup needs execution | `zero-tech-debt` |

Specialists such as `engineering-rest-api-design`, `architect`, or a project testing guide can operate inside a phase. They do not replace its owner. Emit the canonical handoff artifact instead of restarting discovery or asking for approval already carried by the handoff.

## Design brief

```text
Problem Frame: stakeholder, actual, expected, gap, evidence, level, constraints
Context: verified system facts, assumptions, and cause hypotheses
Options: benefits, resources, harmful effects, contradictions
Decision: chosen option, losing reasons, authority
Architecture: modules, dependencies, flows, failures, rollback
Complexity when central: essential/accidental, axes, reduce/isolate/accept, core/shell boundary, complexity deleted versus relocated
Routing: next owner, owned scope, required output, return condition
Success evidence: signal, baseline, target/range, observation window
Learning record: Claim -> Evidence -> Decision -> Outcome -> Model update
Out of scope: explicit exclusions
```

Before implementation, the learning record contains the claim, current evidence, decision, and planned success evidence. After delivery, compare the observed outcome with that evidence and update, narrow, or reverse the model. Shipping is not proof that the decision was right.

## Stop conditions

Stop analysis and present the decision when the Problem Frame is evidence-backed, one option is good enough for the decision's reversibility and risk, remaining uncertainty has an owner/check, and more research is unlikely to change the choice. Timebox deeper reasoning; learn one causal layer deeper than the decision requires, not the whole universe.

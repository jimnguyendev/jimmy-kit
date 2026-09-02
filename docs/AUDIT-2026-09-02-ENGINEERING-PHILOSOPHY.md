# Audit — Engineering Philosophy Preservation

**Date:** 2026-09-02
**Scope:** preserve the predecessor engineering philosophy inside Jimmy Kit, restore the structure invariants lost during compression, and keep the kit's product/analytics-first dosage intact.

## Source comparison

The predecessor engineering pack was compared file-for-file with the copied Jimmy Kit skills. No skill file was omitted. The semantic gap was concentrated in `engineering-design-thinking`: the shorter kit version retained “fewer, deeper modules” but no longer made capability-first locality, evidence-backed package splits, contextual naming, owner-local types, dependency direction, and contention classification inspectable.

`engineering-perf-optimization-process` and `engineering-rest-api-design` already preserved their source reasoning closely, so this change leaves their operating workflows intact.

## Preserved philosophy

> Programming is thinking, not typing. Structure serves clarity, not paradigm.

The kit now preserves seven shared engineering principles: capability-first locality, fewer evidence-backed modules, contextual names, types near their owner, a one-way dependency DAG, measurement before optimization, and evidence-backed reversible delivery.

Circular dependencies are treated as a general design problem, not a Go-specific trick. The required remedy order is:

1. Move the responsibility to its true owner.
2. Merge a fake boundary.
3. If ownership is genuinely independent, define the smallest consumer-owned contract and wire the provider at the composition root.

Go is documented as the language that enforces package-import DAGs at compile time. TypeScript and other stacks still apply the same ownership and dependency-direction rule even when their toolchains permit the cycle.

## Benchmark

| Measure | Before | After | Evidence |
|---|---:|---:|---|
| Deterministic engineering-philosophy audit | 2/19 (11%) initial suite | 22/22 (100%) expanded suite | `scripts/audit-engineering-philosophy.py` |
| Go package-cycle scenario | 3/6 | 6/6 | fresh-context responses in `codebase-design/SCENARIO.md` |
| TypeScript module-cycle scenario | 2/4 | 4/4 | fresh-context responses in `codebase-design/SCENARIO.md` |
| Complexity and dosage contract | 22/22 | 22/22 | `scripts/audit-complexity-dosage.py` |
| Problem-solving kernel | 20/20 | 20/20 | `scripts/audit-problem-solving-kernel.py` |
| Directed engineering routes | 12/12 | 12/12 | `validate_routing.py` |
| Orchestration regression suite | 17/17 | 17/17 | Python unittest |

The first revised Go run still jumped directly to an interface and omitted the distinction between language enforcement and the general DAG principle. Tightening the inspectable output contract produced the final 6/6 result. This matters because a reference that exists but is not visible in the decision output can still be skipped by an agent.

## Placement and dosage

- `README.md` carries the human-facing manifesto and seven principles.
- `codebase-design/references/engineering-philosophy.md` is the single operational reference; no new skill was added.
- `engineering-design-thinking` restores the Gate 4 structure invariants.
- `codebase-design` makes ownership, locality, split evidence, names/type placement, DAG, and cycle treatment inspectable.
- `improve-codebase-architecture` uses the ordered cycle remedies during discovery.
- `tdd-go` applies the guidance only when implementation actually changes packages, types, interfaces, or dependency direction.
- Performance and correctness remain owned by the existing performance and quality-gate skills.

This is not a new mandatory engineering phase. Product, UX, and analytics work continues to use risk-based dosage; these principles are loaded only when code structure or engineering architecture is in scope.

## Verification proof levels

- **Static contract:** philosophy 22/22, complexity/dosage 22/22, problem-solving kernel 20/20, repository contract PASS, routing 12/12.
- **Executable local:** orchestration 17/17 and strict plugin-manifest validation passed. Negative controls confirmed that malformed YAML, an extra forbidden runtime reference, and contradictory routing precedence make their audits fail.
- **Behavioral independent:** Go 6/6 and TypeScript 4/4 in fresh contexts; the actual scored responses are stored in `codebase-design/SCENARIO.md`.
- **Independent review:** the first pass found one failing matcher, one cross-surface dosage contradiction, unsupported evidence, one internal identifier, and two audit false-pass paths. After correction and two focused re-reviews, no Critical, Important, or Minor findings remain; verdict: ready to merge.
- **Still exit 2:** `engineering-design-thinking`, `improve-codebase-architecture`, and `tdd-go` retain earlier unrun whole-skill scenario cases. The philosophy extensions are covered, but this audit does not promote those entire scenarios to exit 0.
- **Not applicable:** no application runtime, browser, deployment, or production claim is made for this documentation and skill change.

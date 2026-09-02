# Audit — Complexity Management and Workflow Dosage

**Date:** 2026-09-02
**Scope:** align Jimmy Kit with the Software Design and Refactoring source model, preserve useful OOP for TypeScript backends, and remove the council/dosage contradiction without adding framework skills.

## What the source review changed

The [original slides](https://www.slideshare.net/slideshow/software-design-and-refactoring-215436212/215436212) propose two treatments: FP reduces moving parts; OOP isolates necessary moving parts. The linked sources make the trigger conditions more precise:

- [Li Haoyi](https://www.lihaoyi.com/post/WhatsFunctionalProgrammingAllAbout.html): FP makes data flow and dependencies explicit; it does not necessarily reduce code size or essential problem complexity, and wrapping imperative code in a helper is not FP.
- [Eric Elliott](https://medium.com/javascript-scene/the-forgotten-history-of-oop-88d71b9b2d9f): the useful OOP core is encapsulation, message passing, and late binding; classes and inheritance are not required.
- [Brian Will](https://medium.com/@brianwill/object-oriented-programming-a-personal-disaster-1b044c2383ab): encapsulate state only to the extent state must exist, keep ownership shallow, and avoid free-form mutable object graphs.
- [Gary Bernhardt](https://www.destroyallsoftware.com/talks/boundaries): simple values can cross subsystem boundaries while an imperative shell owns effects and coordination.

Jimmy therefore asks per complexity axis whether to `reduce`, `isolate`, or `accept`. Functional Core / Imperative Shell is a heuristic with a simple-CRUD counterexample, not a mandated architecture.

## Benchmark

| Measure | Before | After | Evidence |
|---|---:|---:|---|
| Complexity/dosage deterministic audit | 5/18 (28%) initial suite; reviewer-expanded suite later exposed 4 gaps at 18/22 | 22/22 (100%) | `scripts/audit-complexity-dosage.py` |
| TypeScript backend scenario, strict inspectable criteria | 3/7 | 7/7 | fresh-context runs; final response pasted in `codebase-design/SCENARIO.md` |
| Go backend scenario | no dedicated case | 6/6; functions/values reduce, small consumer-owned interfaces isolate real seams, no Java-style ceremony | fresh-context run pasted in `codebase-design/SCENARIO.md` |
| Dosage routing scenario | 5/5, but agent explicitly reconciled two conflicting rules | 5/5 with one consistent rule | fresh-context runs; final response pasted in `routing/SCENARIO.md` |
| Native `product-council` discovery | broad metadata allowed ordinary feature work to match | 3/3: Tier 1 no, approved Tier 2 no, explicit pitch yes | fresh-context frontmatter-only rerun pasted in `product-council/SCENARIO.md` |
| Existing problem-solving kernel | 20/20 | 20/20 | `scripts/audit-problem-solving-kernel.py` |
| Directed engineering skill routes | 12/12 | 12/12 | `validate_routing.py` |
| Orchestration regression suite | 17/17 | 17/17 | Python unittest |
| Inventory/link smoke | 51/51 | 51/51 | `list-skills.sh` and isolated `link-skills.sh` run |

The TypeScript baseline already found a broadly sensible mixed architecture. Its failure was inspectability: it did not name essential versus accidental complexity, scan the five axes, or state what was reduced, isolated, accepted, or merely relocated. The first post-change run reached 5/7 but still omitted the required fields; tightening the output shape produced 7/7 on the second fresh run.

The dosage behavior score did not increase. The improvement is removal of contradictory instructions: before the change, the fresh agent said the dosage section had to "narrow" the eager dispatcher's broad council rule. After the change, all public surfaces express the same condition directly.

## Implemented changes

1. Added `codebase-design/references/complexity-management.md` with:
   - essential versus accidental complexity;
   - five-axis scan;
   - `reduce | isolate | accept` decision;
   - exact FP/OOP trigger conditions;
   - TypeScript backend role/message guidance;
   - one concise React boundary example;
   - core/shell counterexample and verification layers.
2. Made the complexity decision inspectable in `codebase-design`, `engineering-design-thinking`, `improve-codebase-architecture`, and `zero-tech-debt`.
3. Kept `tdd-go` Go-only. Accepted non-Go behavior transfers to the target project's test-first workflow using the same handoff artifact.
4. Repaired README, usage, operating workflow, eager dispatcher, routing appendix, `product-council` discovery metadata, glossary, and ADR language so council is conditional on Tier 3, an explicit red-team/pitch request, or a consequential product/platform decision.
5. Added routing and complexity scenarios plus TypeScript, non-Go handoff, candidate-relocation, and simple-CRUD eval specifications. No OOP, FP, React, or TypeScript framework skill was added.

## Verification proof levels

- **Static contract:** 22/22 complexity/dosage, 20/20 kernel, 12/12 routing; JSON/YAML parsed; Python/JavaScript/shell syntax passed; `git diff --check` passed.
- **Executable local:** 17/17 orchestration tests; 51/51 list and isolated-link smoke; plugin manifest strict validation passed.
- **Behavioral independent:** `codebase-design` TypeScript 7/7 and Go 6/6, routing dosage 5/5, and native council discovery 3/3 in fresh contexts; the actual responses are stored in their scenario files.
- **Independent review:** the combined-diff review found audit-matcher, per-surface dosage, evidence-recording, internal-identifier, precedence, and false-pass issues. All were corrected; two focused re-reviews found no remaining Critical, Important, or Minor findings and returned a ready-to-merge verdict.
- **Still exit 2:** `change-tiers`, `engineering-design-thinking`, and `improve-codebase-architecture` retain unrun scenario cases. Their deterministic/eval contracts pass, but this audit does not promote them to behavioral exit 0.
- **Not applicable:** no application runtime, browser, deployment, or production claim is made for this documentation/skill change.

# Audit — Problem-Solving Kernel and Kit Integrity

> **Scope correction (2026-09-02):** the earlier "full kit static audit, 0 findings" claim covered structural metadata, paths, links, language, and runtime references. It did not test semantic consistency between dosage and the unconditional council wording, nor stack-specific ownership or the FP/OOP complexity model. Those gaps are audited and repaired in `docs/AUDIT-2026-09-02-COMPLEXITY-DOSAGE.md`.

**Date:** 2026-09-02
**Baseline commit:** `459bc73` plus the owner's pre-existing README wording change
**Scope:** integrate the two lecture models into Jimmy Kit without adding duplicate skills; audit the affected routing and the repository checklist.

## Proof levels

- **Static contract:** deterministic content, metadata, path, link, and routing checks.
- **Executable local:** scripts/tests executed in this checkout.
- **Behavioral independent:** a fresh agent answers scenario prompts without seeing expected behaviors.

This audit reaches the first two levels. It does not claim independent behavioral proof for the new reasoning scenarios.

## Benchmark

| Measure | Before | After | Proof |
|---|---:|---:|---|
| Problem-solving kernel checks | 4/20 (20%) | 20/20 (100%) | `scripts/audit-problem-solving-kernel.py` |
| Directed engineering handoffs | stale/missing owner and repo-root-incompatible validator | 12/12 valid | `validate_routing.py` |
| `engineering-design-thinking` body | 256 lines with most detail inline | 111 lines plus 3 focused references | line count + link audit |
| Design-thinking eval specifications | 11 | 16 | parsed `evals.json` |
| Architecture-discovery eval specifications | 0 | 4 | parsed `evals.json` |
| Orchestration linter tests | 0/17 runnable; all errored on a missing gitignored fixture | 17/17 pass | Python unittest, 0.512s final run |
| Kit inventory/link smoke | docs said 46 in several current locations | 51/51 listed and linked | filesystem + temp install smoke |
| Repository contract scan | inventory, output-path, runtime-reference, and H1 drift found | PASS after fixes | `scripts/audit-repository-contract.py` plus independent identifier review |
| Plugin manifest | not rerun in baseline | strict validation PASS | Claude plugin validator |

## Changes that affect reasoning

1. `engineering-design-thinking` now starts from a solution-free **Problem Frame**: owner, stakeholders, actual state with evidence, expected state, gap, importance, abstraction level, constraints, assumptions, cause hypotheses, and success evidence.
2. **First-principles mode** separates facts, conventions, and assumptions; decomposes one causal layer deeper; derives options upward; seeks falsifiers; and stops by timebox/evidence threshold.
3. **Contradiction resolution** distinguishes a finite-resource trade-off from removable coupling and tests separation in time, space, condition, and parts/whole before compromise.
4. The decision loop is explicit: `Claim -> Evidence -> Decision -> Outcome -> Model update`.
5. Routing now chooses by **problem state**, not only request keywords. Canonical `problem-solving` remains a recovery tool after repeated failed approaches and is no longer a default UNDERSTAND step.
6. The missing `improve-arch-go` route is replaced by the bundled `improve-codebase-architecture`, with a complete four-owner bidirectional contract.

## Integrity repairs found during audit

- Current inventory references now agree on 51 skills.
- Jimmy outputs point to `.jimmy/work/`, `.jimmy/docs/`, or `.jimmy/adr/`; stale target `docs/` and upstream runtime paths were removed from active instructions.
- Source-product names were removed from runnable analytics examples.
- Combined UX skills now have one H1 each without re-voicing their canonical workflow.
- Orchestration tests use bundled fixtures rather than a developer's ignored `.orchestrate/` state.
- The owner's pre-existing README change about lecture notes remains intact.

## Verification run

- Kernel audit: 20/20.
- Routing validator: metadata, links, six bidirectional pairs, and 12 directed eval handoffs valid.
- Repository contract audit: `scripts/audit-repository-contract.py` checks 51 skill directories, frontmatter/name/trigger/H1, JSON, relative links, language, runtime/output paths, syntax, and isolated inventory/link smoke. Independent review found one internal service identifier outside that deterministic contract; it was generalized before the final rerun.
- Orchestration linter: 17 tests passed.
- Analytics examples: 3/3 executed.
- JSON and Python syntax: pass; JavaScript and shell syntax: pass.
- Inventory and link smoke: 51/51.
- Claude plugin strict manifest validation: pass.
- `git diff --check`: pass; no `__pycache__` remains.

## Remaining evidence gap

The five new design-thinking behavior cases and the new architecture-routing cases are executable **specifications**, not scored fresh-agent runs. Their `SCENARIO.md` status remains exit 2 until an independent agent is given only the skill plus prompt and its response is scored against the planted behaviors. Static and local executable results must not be reported as proof that every model will reason correctly.

#!/usr/bin/env python3
"""Audit Jimmy Kit's complexity model and risk-based workflow dosage."""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Check:
    name: str
    passed: bool
    detail: str


def has_all(text: str, *tokens: str) -> bool:
    lowered = text.lower()
    return all(token.lower() in lowered for token in tokens)


def main() -> int:
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd()
    skill_count = len(list((root / "skills").glob("*/*/SKILL.md")))

    readme = (root / "README.md").read_text()
    agents = (root / "AGENTS.md").read_text()
    usage = (root / "docs" / "USAGE.md").read_text()
    workflow = (root / "docs" / "OPERATING-WORKFLOW.md").read_text()
    context = (root / "CONTEXT.md").read_text()
    dispatcher = (root / "templates" / "eager-dispatcher.md").read_text()
    routing = (root / "skills" / "process" / "routing" / "SKILL.md").read_text()
    council = (root / "skills" / "product" / "product-council" / "SKILL.md").read_text()
    design_dir = root / "skills" / "engineering" / "engineering-design-thinking"
    design = (design_dir / "SKILL.md").read_text()
    handoff = (design_dir / "references" / "skill-routing.md").read_text()
    codebase_dir = root / "skills" / "engineering" / "codebase-design"
    codebase = (codebase_dir / "SKILL.md").read_text()
    complexity_path = codebase_dir / "references" / "complexity-management.md"
    complexity = complexity_path.read_text() if complexity_path.is_file() else ""
    improve = (root / "skills" / "engineering" / "improve-codebase-architecture" / "SKILL.md").read_text()
    zero_debt = (root / "skills" / "engineering" / "zero-tech-debt" / "SKILL.md").read_text()

    dosage_surfaces = {
        "README": readme,
        "usage": usage,
        "workflow": workflow,
        "dispatcher": dispatcher,
        "routing": routing,
    }
    public_surfaces = "\n".join(dosage_surfaces.values())
    unconditional_patterns = (
        r"mandatory `product-council`",
        r"before anything (?:gets )?built or pitched",
        r"before building or pitching anything new, run `product-council`",
        r"every chain runs",
        r"mandatory gate before building or pitching",
    )

    design_evals = json.loads((design_dir / "evals" / "evals.json").read_text())["evals"]
    improve_evals = json.loads(
        (root / "skills" / "engineering" / "improve-codebase-architecture" / "evals" / "evals.json").read_text()
    )["evals"]
    zero_evals = json.loads(
        (root / "skills" / "engineering" / "zero-tech-debt" / "evals" / "evals.json").read_text()
    )["evals"]
    eval_names = {str(case.get("name", "")) for case in design_evals + improve_evals + zero_evals}

    checks = [
        Check(
            "inventory consistency",
            f"{skill_count} skills" in readme
            and f"finds all {skill_count} `SKILL.md`" in usage
            and f"gives the agent {skill_count} tools" in usage
            and f"current checkout: {skill_count} skills" in agents
            and "verified, 48 found" not in agents,
            f"README, USAGE, and current AGENTS guidance should match the filesystem inventory ({skill_count})",
        ),
        Check(
            "no unconditional council",
            not any(re.search(pattern, public_surfaces, re.IGNORECASE) for pattern in unconditional_patterns),
            "public routing surfaces should not force council or the full chain on every build",
        ),
        Check(
            "tier dosage contract",
            all(
                has_all(
                    surface,
                    "Tier 1",
                    "Tier 2",
                    "Tier 3",
                    "one or two",
                    "full",
                    "intake",
                    "By default",
                    "already-approved Tier 2",
                    "are exceptions",
                    "do not expand the rest of the workflow unless the work is Tier 3",
                )
                for surface in dosage_surfaces.values()
            ),
            "each routing surface should reserve the full intake for Tier 3 and keep council-only triggers narrow",
        ),
        Check(
            "conditional council trigger",
            all(
                has_all(
                    surface,
                    "product-council",
                    "Tier 3",
                    "explicit",
                    "consequential",
                    "are exceptions",
                )
                for surface in dosage_surfaces.values()
            ),
            "each public surface should allow Tier 3, explicit red-team, or consequential council triggers",
        ),
        Check(
            "native council discovery",
            has_all(council, "Use when", "Tier 3", "explicitly requests", "pitch review", "consequential")
            and "for any feature idea" not in council,
            "product-council metadata should not bypass dosage when the eager dispatcher is absent",
        ),
        Check(
            "glossary council dosage",
            has_all(
                context,
                "product-council` gates the full Tier 3 flow",
                "council-only exceptions",
                "default Tier 1/Tier 2 bypass",
            )
            and "product-council` gates the ENVISION" not in context,
            "the shared glossary should not imply council gates every ENVISION to DELIVER transition",
        ),
        Check(
            "example-chain council dosage",
            workflow.count("product-council (when Tier 3, explicit, or consequential)") >= 2,
            "generic problem chains should mark council as conditional rather than silently overriding dosage",
        ),
        Check(
            "dosage scenarios",
            all(
                (root / "skills" / "process" / skill / "SCENARIO.md").is_file()
                for skill in ("routing", "change-tiers")
            ),
            "routing and change-tiers should have scenario-first coverage",
        ),
        Check(
            "complexity reference",
            complexity_path.is_file()
            and "references/complexity-management.md" in codebase
            and "complexity-management.md" in design,
            "codebase and design skills should share one progressive-disclosure complexity reference",
        ),
        Check(
            "complexity classification",
            has_all(complexity, "essential complexity", "accidental complexity"),
            "the model should distinguish inherent domain complexity from implementation-created complexity",
        ),
        Check(
            "five complexity axes",
            has_all(
                complexity,
                "shared mutable state",
                "side effects",
                "dependencies",
                "control flow",
                "code size",
            ),
            "the reference should scan all five lecture-derived complexity axes",
        ),
        Check(
            "treatment choices",
            has_all(complexity, "reduce", "isolate", "accept", "merely relocates"),
            "every candidate should say whether it reduces, isolates, accepts, or relocates complexity",
        ),
        Check(
            "functional core is heuristic",
            has_all(complexity, "functional core", "imperative shell", "heuristic", "simple crud"),
            "Functional Core / Imperative Shell should be optional and have a counterexample",
        ),
        Check(
            "role-first TypeScript OOP",
            has_all(
                complexity,
                "TypeScript backend",
                "messages",
                "roles",
                "contracts",
                "state ownership",
                "lifecycle",
                "composition over inheritance",
            ),
            "TypeScript backend guidance should preserve role-first OOP without class hierarchy",
        ),
        Check(
            "layered verification",
            has_all(complexity, "without mocks", "process boundaries", "integration", "end-to-end"),
            "verification should differ across pure core, shell/adapters, and critical flows",
        ),
        Check(
            "architecture candidate fields",
            has_all(improve, "essential", "accidental", "reduce", "isolate", "accept", "relocates"),
            "architecture reports should make the complexity treatment inspectable",
        ),
        Check(
            "cleanup relocation guard",
            has_all(zero_debt, "reduce", "isolate", "accept", "relocate"),
            "cleanup should not claim success when complexity only moved",
        ),
        Check(
            "non-Go implementation route",
            has_all(handoff + design + improve + zero_debt, "tdd-go", "Go", "non-Go", "project", "test-first")
            and "TypeScript" in handoff
            and "non-Go implementation" in design
            and "accepted non-Go behavior" in improve,
            "accepted non-Go behavior should use the target project's test-first workflow, not tdd-go",
        ),
        Check(
            "behavior eval coverage",
            {
                "typescript-backend-complexity",
                "go-backend-complexity",
                "simple-crud-counterexample",
                "non-go-implementation-handoff",
            }.issubset(eval_names),
            "eval specifications should cover TypeScript and Go design, non-Go routing, and the no-ceremony counterexample",
        ),
        Check(
            "Go-specific tdd-go handoff evals",
            all(
                "Go" in str(case["prompt"])
                for case in design_evals + improve_evals + zero_evals
                if case.get("route", {}).get("to") == "tdd-go"
            ),
            "evals that hand work from a stack-neutral owner to tdd-go should state that the implementation is Go",
        ),
        Check(
            "no paradigm skill sprawl",
            not any(
                (root / "skills" / category / name).exists()
                for category in ("engineering", "productivity")
                for name in ("oop", "functional-programming", "tdd-react", "tdd-typescript")
            ),
            "the change should strengthen the shared kernel instead of adding paradigm/framework skills",
        ),
        Check(
            "React remains an example",
            complexity.lower().count("react") <= 2,
            "React should remain a concise boundary example, not a detailed workflow",
        ),
    ]

    passed = sum(check.passed for check in checks)
    for check in checks:
        marker = "PASS" if check.passed else "FAIL"
        print(f"[{marker}] {check.name}: {check.detail}")
    print(f"complexity-dosage-audit: SCORE {passed}/{len(checks)} ({passed / len(checks):.0%})")
    return 0 if passed == len(checks) else 1


if __name__ == "__main__":
    raise SystemExit(main())

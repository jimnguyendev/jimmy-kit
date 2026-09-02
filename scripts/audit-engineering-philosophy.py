#!/usr/bin/env python3
"""Audit preservation of Jimmy Kit's engineering philosophy."""

from __future__ import annotations

import json
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
    readme = (root / "README.md").read_text()
    context = (root / "CONTEXT.md").read_text()
    decisions = (root / "docs" / "DECISIONS.md").read_text()
    codebase_dir = root / "skills" / "engineering" / "codebase-design"
    reference_path = codebase_dir / "references" / "engineering-philosophy.md"
    reference = reference_path.read_text() if reference_path.is_file() else ""
    codebase = (codebase_dir / "SKILL.md").read_text()
    design = (root / "skills" / "engineering" / "engineering-design-thinking" / "SKILL.md").read_text()
    improve = (root / "skills" / "engineering" / "improve-codebase-architecture" / "SKILL.md").read_text()
    tdd = (root / "skills" / "engineering" / "tdd-go" / "SKILL.md").read_text()
    perf = (root / "skills" / "engineering" / "engineering-perf-optimization-process" / "SKILL.md").read_text()
    gates = (root / "skills" / "process" / "quality-gates" / "SKILL.md").read_text()
    scenarios = "\n".join(
        (root / path).read_text()
        for path in (
            "skills/engineering/codebase-design/SCENARIO.md",
            "skills/engineering/engineering-design-thinking/SCENARIO.md",
            "skills/engineering/improve-codebase-architecture/SCENARIO.md",
            "skills/engineering/tdd-go/SCENARIO.md",
        )
    )
    design_evals = json.loads(
        (root / "skills" / "engineering" / "engineering-design-thinking" / "evals" / "evals.json").read_text()
    )["evals"]
    eval_names = {str(case.get("name", "")) for case in design_evals}
    skill_count = len(list((root / "skills").glob("*/*/SKILL.md")))

    linked_owners = (codebase, design, improve, tdd)
    cycle_section = reference.lower().split("## breaking circular dependencies", 1)[-1]
    remedies = (
        "### 1. move responsibility",
        "### 2. merge",
        "### 3. introduce a consumer-owned",
    )
    remedy_positions = [cycle_section.find(item) for item in remedies]

    checks = [
        Check(
            "manifesto",
            "Programming is thinking, not typing. Structure serves clarity, not paradigm." in readme
            and "Programming is thinking, not typing. Structure serves clarity, not paradigm." in reference,
            "the exact engineering manifesto should be human-visible and operational",
        ),
        Check(
            "seven-principle README",
            has_all(
                readme,
                "business capabilities",
                "fewer packages",
                "keep names short",
                "types near",
                "directed acyclic graph",
                "constrain before",
                "correctness with gates",
            ),
            "README should preserve all seven source principles",
        ),
        Check(
            "canonical operational reference",
            reference_path.is_file() and all("engineering-philosophy.md" in owner for owner in linked_owners),
            "one progressive-disclosure reference should be routed from all architecture/implementation owners",
        ),
        Check(
            "capability-first locality",
            has_all(reference, "business capability", "feature-first", "technical-layer", "locality"),
            "organization should default to business capability rather than technical buckets",
        ),
        Check(
            "fewer units with evidence",
            has_all(reference, "fewer", "split", "observed pain", "fake boundary"),
            "package/module splits should be earned by evidence and fake boundaries may be merged",
        ),
        Check(
            "contextual names",
            has_all(reference, "short", "stuttering", "package", "type context"),
            "names should not repeat context already supplied by package or type",
        ),
        Check(
            "types near owner",
            has_all(reference, "types", "near", "transport", "persistence", "owner"),
            "transport and persistence types should stay near the boundary that owns them",
        ),
        Check(
            "stack-neutral DAG",
            has_all(reference, "directed acyclic graph", "stack-neutral", "one-way", "Go", "TypeScript"),
            "DAG should be a general design principle with language-specific enforcement notes",
        ),
        Check(
            "ordered cycle remedies",
            all(position >= 0 for position in remedy_positions)
            and remedy_positions == sorted(remedy_positions),
            "cycle resolution should try ownership, merge, then consumer-owned contract in that order",
        ),
        Check(
            "no common-package reflex",
            has_all(reference, "common", "dumping ground", "real owned concept"),
            "the guidance should reject a vague common/shared package as a cycle workaround",
        ),
        Check(
            "Go is enforcement example",
            has_all(reference + tdd, "compile-time", "Go", "enforce", "stack-neutral")
            and "Import cycles can be convenient but their cost can be catastrophic." in reference
            and "Go-specific design principle" not in reference,
            "Go should enforce rather than own the DAG principle",
        ),
        Check(
            "design owner integration",
            has_all(design, "business-capability", "DAG", "names", "types", "contention"),
            "Gate 4 should carry the preserved structure decisions",
        ),
        Check(
            "inspectable structure output",
            has_all(
                codebase,
                "Capability and owner",
                "Locality",
                "Packages/modules and evidence",
                "Names and type placement",
                "Dependency DAG",
                "first sufficient remedy",
            ),
            "codebase decisions should expose the structure reasoning rather than merely reference it",
        ),
        Check(
            "architecture discovery integration",
            has_all(improve, "cycle", "move responsibility", "merge", "consumer-owned", "locality"),
            "architecture discovery should rank cycle remedies by ownership and locality",
        ),
        Check(
            "conditional Go implementation guard",
            has_all(tdd, "when", "packages", "types", "interfaces", "acyclic", "stuttering"),
            "tdd-go should apply the philosophy only when structure changes are in scope",
        ),
        Check(
            "optimize and ship owners retained",
            has_all(reference + perf, "constrain", "profile", "target")
            and has_all(reference + gates, "gates", "evidence", "reversib"),
            "performance and quality-gate skills should remain the operational owners",
        ),
        Check(
            "shared glossary",
            has_all(context, "feature-first", "dependency DAG", "consumer-owned"),
            "shared vocabulary should define the non-obvious architecture terms",
        ),
        Check(
            "decision record",
            has_all(decisions, "engineering philosophy", "stack-neutral", "circular"),
            "the preservation and placement decision should be durable",
        ),
        Check(
            "scenario-first coverage",
            has_all(scenarios, "Go package cycle", "TypeScript module cycle", "written BEFORE"),
            "Go and TypeScript cycle scenarios should precede skill edits",
        ),
        Check(
            "behavior eval coverage",
            {"go-package-cycle-philosophy", "typescript-cycle-is-stack-neutral"}.issubset(eval_names),
            "eval specifications should preserve cycle behavior in both an enforcing and permissive language",
        ),
        Check(
            "no skill sprawl",
            skill_count == 51 and not (root / "skills" / "engineering" / "engineering-philosophy" / "SKILL.md").exists(),
            "preserving philosophy should not add a new skill",
        ),
        Check(
            "product-analysis dosage preserved",
            has_all(readme, "do not add", "product", "UX", "analytics", "risk-based"),
            "engineering philosophy should not become mandatory ceremony for the kit's product and analytics majority",
        ),
    ]

    passed = sum(check.passed for check in checks)
    for check in checks:
        marker = "PASS" if check.passed else "FAIL"
        print(f"[{marker}] {check.name}: {check.detail}")
    print(f"engineering-philosophy-audit: SCORE {passed}/{len(checks)} ({passed / len(checks):.0%})")
    return 0 if passed == len(checks) else 1


if __name__ == "__main__":
    raise SystemExit(main())

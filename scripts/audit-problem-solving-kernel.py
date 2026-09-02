#!/usr/bin/env python3
"""Audit the Jimmy Kit problem-solving kernel with deterministic checks."""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Check:
    name: str
    passed: bool
    detail: str


def contains_all(text: str, tokens: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return all(token.lower() in lowered for token in tokens)


def main() -> int:
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd()
    skill_files = sorted((root / "skills").glob("*/*/SKILL.md"))
    actual_count = len(skill_files)

    readme = (root / "README.md").read_text()
    agents = (root / "AGENTS.md").read_text()
    workflow = (root / "docs" / "OPERATING-WORKFLOW.md").read_text()
    dispatcher = (root / "templates" / "eager-dispatcher.md").read_text()
    design_dir = root / "skills" / "engineering" / "engineering-design-thinking"
    design = (design_dir / "SKILL.md").read_text()
    routing = (design_dir / "references" / "skill-routing.md").read_text()

    reference_paths = {
        "problem-frame": design_dir / "references" / "problem-frame.md",
        "first-principles": design_dir / "references" / "first-principles.md",
        "contradiction-resolution": design_dir / "references" / "contradiction-resolution.md",
    }
    reference_text = {
        name: path.read_text() if path.is_file() else ""
        for name, path in reference_paths.items()
    }

    phase_line = next(
        (line for line in workflow.splitlines() if line.startswith("| UNDERSTAND |")),
        "",
    )
    routing_cluster = "\n".join(
        path.read_text()
        for path in (
            design_dir / "SKILL.md",
            design_dir / "references" / "skill-routing.md",
            design_dir / "scripts" / "validate_routing.py",
            design_dir / "evals" / "evals.json",
            root / "skills" / "engineering" / "tdd-go" / "SKILL.md",
            root / "skills" / "engineering" / "tdd-go" / "evals" / "evals.json",
            root / "skills" / "engineering" / "zero-tech-debt" / "SKILL.md",
            root / "skills" / "engineering" / "zero-tech-debt" / "evals" / "evals.json",
            root / "skills" / "engineering" / "improve-codebase-architecture" / "SKILL.md",
        )
        if path.is_file()
    )

    checks = [
        Check(
            "inventory README",
            len(re.findall(rf"\b{actual_count} skills\b", readme)) >= 2,
            f"README should state the current {actual_count}-skill inventory in overview and install guidance",
        ),
        Check(
            "inventory AGENTS",
            f"({actual_count} skills, 7 categories)" in agents,
            f"AGENTS should state the current {actual_count}-skill inventory",
        ),
        Check(
            "inventory workflow",
            workflow.startswith(f"# Operating Workflow — how the {actual_count} skills fit together"),
            "operating-workflow title should match the filesystem inventory",
        ),
        Check(
            "default chain excludes stuckness rescue",
            "problem-solving" not in phase_line,
            "problem-solving belongs to stuckness recovery, not the default UNDERSTAND chain",
        ),
        Check(
            "dispatcher keeps stuckness trigger",
            "stuck after 3+ attempts / complexity spiraling" in dispatcher
            and "`problem-solving`" in dispatcher,
            "eager dispatch should still route repeated failed attempts to problem-solving",
        ),
        Check(
            "dispatcher recognizes problem state",
            contains_all(dispatcher, ("actual state", "expected state", "engineering-design-thinking")),
            "dispatch should recognize an unframed actual/expected gap, not only topic keywords",
        ),
        Check(
            "problem-frame reference",
            reference_paths["problem-frame"].is_file()
            and "references/problem-frame.md" in design,
            "design skill should link a shared Problem Frame artifact",
        ),
        Check(
            "problem-frame fields",
            contains_all(
                reference_text["problem-frame"],
                (
                    "stakeholders",
                    "actual state",
                    "expected state",
                    "gap",
                    "abstraction level",
                    "constraints",
                    "assumptions",
                    "cause hypotheses",
                    "success evidence",
                ),
            ),
            "Problem Frame should carry the minimum decision fields",
        ),
        Check(
            "solution-free frame gate",
            contains_all(reference_text["problem-frame"], ("solution-free", "change the expectation")),
            "Problem Frame should challenge smuggled solutions and allow expectation correction",
        ),
        Check(
            "first-principles reference",
            reference_paths["first-principles"].is_file()
            and "references/first-principles.md" in design,
            "design skill should link an explicit first-principles mode",
        ),
        Check(
            "first-principles decomposition",
            contains_all(
                reference_text["first-principles"],
                ("facts", "conventions", "assumptions", "fundamentals", "interactions", "derive"),
            ),
            "first-principles mode should decompose and rebuild from evidence",
        ),
        Check(
            "first-principles stop conditions",
            contains_all(
                reference_text["first-principles"],
                ("timebox", "one layer deeper", "stop", "analysis paralysis"),
            ),
            "first-principles mode needs explicit anti-analysis-paralysis controls",
        ),
        Check(
            "contradiction reference",
            reference_paths["contradiction-resolution"].is_file()
            and "references/contradiction-resolution.md" in design,
            "option evaluation should link contradiction resolution",
        ),
        Check(
            "contradiction separation operators",
            contains_all(
                reference_text["contradiction-resolution"],
                ("time", "space", "condition", "parts and whole"),
            ),
            "contradictions should be tested with four separation operators",
        ),
        Check(
            "ideality preserved",
            contains_all(design + reference_text["contradiction-resolution"], ("benefits", "resources", "harmful effects")),
            "solution selection should preserve the ideality model",
        ),
        Check(
            "feedback loop",
            contains_all(design, ("claim", "evidence", "decision", "outcome", "model update")),
            "the design brief should close the learning loop after delivery",
        ),
        Check(
            "bundled architecture owner",
            "improve-codebase-architecture" in routing_cluster,
            "routing should name the bundled architecture-discovery skill",
        ),
        Check(
            "no stale architecture owner",
            "improve-arch-go" not in routing_cluster,
            "active routing files should not name a missing skill",
        ),
        Check(
            "routing links on all owners",
            all(
                "skill-routing.md" in (root / "skills" / "engineering" / skill / "SKILL.md").read_text()
                for skill in (
                    "engineering-design-thinking",
                    "improve-codebase-architecture",
                    "tdd-go",
                    "zero-tech-debt",
                )
            ),
            "each routing owner should link the canonical contract",
        ),
        Check(
            "scenario-first coverage",
            all(
                (root / "skills" / "engineering" / skill / "SCENARIO.md").is_file()
                for skill in (
                    "engineering-design-thinking",
                    "improve-codebase-architecture",
                    "tdd-go",
                    "zero-tech-debt",
                )
            ),
            "every changed skill should have a scenario written before its body changes",
        ),
    ]

    passed = sum(check.passed for check in checks)
    total = len(checks)
    for check in checks:
        marker = "PASS" if check.passed else "FAIL"
        print(f"[{marker}] {check.name}: {check.detail}")
    print(f"kernel-audit: SCORE {passed}/{total} ({passed / total:.0%})")
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())

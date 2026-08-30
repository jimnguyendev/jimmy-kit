#!/usr/bin/env python3
"""Validate the four-skill routing contract without third-party packages."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


SKILLS = (
    "engineering-design-thinking",
    "improve-arch-go",
    "tdd-go",
    "zero-tech-debt",
)


def fail(message: str) -> None:
    print(f"routing: {message}", file=sys.stderr)
    raise SystemExit(1)


def frontmatter_description(text: str, path: Path) -> str:
    match = re.search(r'^description:\s*["\']?(.*?)["\']?\s*$', text, re.MULTILINE)
    if not match:
        fail(f"missing description in {path}")
    return match.group(1)


def load_evals(path: Path) -> list[dict[str, object]]:
    data = json.loads(path.read_text())
    if not isinstance(data, dict) or not isinstance(data.get("evals"), list):
        fail(f"{path} must contain an object with an evals array")
    cases = data["evals"]
    for case in cases:
        for field in ("id", "prompt", "expected_output", "assertions"):
            if field not in case:
                fail(f"eval in {path} is missing {field}")
        if not isinstance(case["assertions"], list) or not case["assertions"]:
            fail(f"eval in {path} must have non-empty assertions")
    return cases


def main() -> None:
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd()
    skills_root = root / ".agents" / "skills"
    reference = skills_root / "engineering-design-thinking" / "references" / "skill-routing.md"
    reference_text = reference.read_text()

    expected_edges = {(source, target) for source in SKILLS for target in SKILLS if source != target}
    observed_edges: set[tuple[str, str]] = set()

    for skill in SKILLS:
        skill_path = skills_root / skill / "SKILL.md"
        text = skill_path.read_text()
        description = frontmatter_description(text, skill_path)
        if "Use " not in description:
            fail(f"{skill} metadata lacks concrete use triggers")
        overlaps = [other for other in SKILLS if other != skill and other in description]
        if overlaps:
            fail(f"{skill} metadata advertises neighboring skills: {', '.join(overlaps)}")
        if "skill-routing.md" not in text:
            fail(f"{skill} does not link the canonical routing reference")

        eval_path = skills_root / skill / "evals" / "evals.json"
        if not eval_path.is_file():
            fail(f"missing independent eval suite: {eval_path}")
        for case in load_evals(eval_path):
            route = case.get("route")
            if route is None:
                continue
            if not isinstance(route, dict):
                fail(f"invalid route metadata in {eval_path}")
            edge = (route.get("from"), route.get("to"))
            if edge[0] != skill:
                fail(f"route source {edge[0]} does not match suite owner {skill}")
            if skill in str(case["prompt"]):
                fail(f"route eval leaks current owner in prompt: {eval_path} id={case['id']}")
            if edge in observed_edges:
                fail(f"duplicate directed route eval: {edge[0]} -> {edge[1]}")
            observed_edges.add(edge)  # type: ignore[arg-type]

    missing = expected_edges - observed_edges
    extra = observed_edges - expected_edges
    if missing or extra:
        details = []
        if missing:
            details.append("missing=" + ", ".join(f"{a}->{b}" for a, b in sorted(missing)))
        if extra:
            details.append("extra=" + ", ".join(f"{a}->{b}" for a, b in sorted(extra)))
        fail("directed route coverage mismatch: " + "; ".join(details))

    expected_pairs = {tuple(sorted((a, b))) for a, b in expected_edges}
    for a, b in expected_pairs:
        marker = f"`{a}` ↔ `{b}`"
        reverse_marker = f"`{b}` ↔ `{a}`"
        if reference_text.count(marker) + reference_text.count(reverse_marker) != 1:
            fail(f"canonical matrix must contain pair exactly once: {a} <-> {b}")

    stale_tokens = ("jimmy-skills@", "sqlc queries", "MyVocab")
    for token in stale_tokens:
        engineering_text = (skills_root / "engineering-design-thinking" / "SKILL.md").read_text()
        if token in reference_text or token in engineering_text:
            fail(f"design routing contains stale token: {token}")

    required_handoff_fields = (
        "from_skill",
        "to_skill",
        "trigger",
        "accepted_decisions",
        "evidence",
        "verification_state",
        "owned_scope",
        "required_output",
        "return_condition",
    )
    for field in required_handoff_fields:
        if field not in reference_text:
            fail(f"canonical handoff artifact is missing {field}")

    print("routing: metadata, links, matrix, and 12 directed evals valid")


if __name__ == "__main__":
    main()

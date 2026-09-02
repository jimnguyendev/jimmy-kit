#!/usr/bin/env python3
"""Reproducible structural audit for the Jimmy Kit repository contract."""

from __future__ import annotations

import ast
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import unquote

try:
    import yaml
except ImportError:  # pragma: no cover - reported as an audit finding below
    yaml = None


SOURCE_SUFFIXES = {".md", ".py", ".js", ".sql", ".ts"}
TRIGGER_PHRASES = ("use when", "use for", "use after", "activate when")
VIETNAMESE = re.compile(
    r"[àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡ"
    r"ùúụủũưừứựửữỳýỵỷỹđÀÁẠẢÃÂẦẤẬẨẪĂẰẮẶẲẴÈÉẸẺẼÊỀẾỆỂỄÌÍỊỈĨ"
    r"ÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠÙÚỤỦŨƯỪỨỰỬỮỲÝỴỶỸĐ]"
)
ASCII_VIETNAMESE = re.compile(
    r"\b(?:khong|duoc|nguon|chay|phien ban|tai ve)\b", re.IGNORECASE
)
RUNTIME_REFERENCE = re.compile(
    r"sage/|\.sage/|sage-[a-z-]+\.(?:sh|py)|/sage-|sage add|delegate_task|Hermes"
)
LINK = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")


def outside_fences(text: str) -> str:
    lines: list[str] = []
    inside = False
    for line in text.splitlines():
        if line.startswith("```"):
            inside = not inside
            continue
        if not inside:
            lines.append(line)
    return "\n".join(lines)


def run_syntax_check(command: list[str], path: Path, errors: list[str]) -> None:
    result = subprocess.run(command + [str(path)], capture_output=True, text=True, check=False)
    if result.returncode:
        errors.append(f"{path}: syntax check failed: {result.stderr.strip()}")


def main() -> int:
    root = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd()
    skill_root = root / "skills"
    errors: list[str] = []
    skill_files = sorted(skill_root.glob("*/*/SKILL.md"))

    if len(skill_files) != 51:
        errors.append(f"inventory: expected 51 skills, found {len(skill_files)}")

    for path in skill_files:
        text = path.read_text(encoding="utf-8")
        frontmatter = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
        if not frontmatter:
            errors.append(f"{path}: missing or malformed frontmatter")
            continue
        if yaml is None:
            errors.append("PyYAML is required to validate skill frontmatter")
            break
        try:
            metadata = yaml.safe_load(frontmatter.group(1))
        except yaml.YAMLError as exc:
            errors.append(f"{path}: invalid YAML frontmatter: {exc}")
            continue
        if not isinstance(metadata, dict):
            errors.append(f"{path}: YAML frontmatter must be a mapping")
            continue
        if metadata.get("name") != path.parent.name:
            errors.append(f"{path}: frontmatter name does not match directory")
        description = str(metadata.get("description", "")).lower()
        if not any(phrase in description for phrase in TRIGGER_PHRASES):
            errors.append(f"{path}: description is not situation-triggered")
        if len(re.findall(r"^# ", outside_fences(text), re.MULTILINE)) != 1:
            errors.append(f"{path}: expected exactly one H1 outside code fences")

    for path in root.rglob("*.json"):
        if ".git" in path.parts or ".learn-vi" in path.parts:
            continue
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            errors.append(f"{path}: invalid JSON: {exc}")

    for path in skill_root.rglob("*.md"):
        text = outside_fences(path.read_text(encoding="utf-8"))
        for raw_target in LINK.findall(text):
            target = raw_target.strip()
            if target.startswith("<") and target.endswith(">"):
                target = target[1:-1]
            if target.startswith(("http://", "https://", "#", "mailto:", "/", ".jimmy/")):
                continue
            target = unquote(target.split("#", 1)[0])
            if not target or any(mark in target for mark in "{}<>[]"):
                continue
            if not (path.parent / target).resolve().exists():
                errors.append(f"{path}: broken relative link: {target}")

    runtime_hits: list[tuple[Path, str]] = []
    for path in skill_root.rglob("*"):
        if not path.is_file() or path.suffix not in SOURCE_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8")
        if VIETNAMESE.search(text) or ASCII_VIETNAMESE.search(text):
            errors.append(f"{path}: Vietnamese text remains in runnable skill sources")
        for line in text.splitlines():
            if RUNTIME_REFERENCE.search(line):
                runtime_hits.append((path.relative_to(root), line.strip()))
        if path.name != "SCENARIO.md":
            for line_number, line in enumerate(text.splitlines(), 1):
                scrubbed = re.sub(r"https?://\S+", "", line)
                scrubbed = scrubbed.replace(".jimmy/docs/", "")
                scrubbed = scrubbed.replace("docs/OPERATING-WORKFLOW.md", "")
                if "docs/" in scrubbed:
                    errors.append(f"{path}:{line_number}: target output escapes the .jimmy namespace")

    allowed_runtime_hits = sorted(
        (
            (
                Path("skills/process/decision-log/SKILL.md"),
                "📄 Full original: [sage] skills/sage-decisions/SKILL.md.",
            ),
            (
                Path("skills/process/retrospective/SKILL.md"),
                "📄 Full original (203 lines): [sage] skills/sage-reflect/SKILL.md.",
            ),
        )
    )
    if sorted(runtime_hits) != allowed_runtime_hits:
        errors.append(
            "runtime references: expected exactly the two public [sage] provenance lines; "
            f"found {[(str(path), line) for path, line in sorted(runtime_hits)]}"
        )

    stale = ("verified, 48 found", "10 problem chains", "10 chains")
    for relative in ("README.md", "AGENTS.md", "CONTEXT.md", "docs/OPERATING-WORKFLOW.md", "docs/USAGE.md"):
        text = (root / relative).read_text(encoding="utf-8").lower()
        for phrase in stale:
            if phrase in text:
                errors.append(f"{relative}: stale inventory/routing phrase: {phrase}")

    for path in root.rglob("*.py"):
        if ".git" in path.parts or ".learn-vi" in path.parts:
            continue
        try:
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except SyntaxError as exc:
            errors.append(f"{path}: Python syntax error: {exc}")
    for path in root.rglob("*.js"):
        if ".git" not in path.parts and ".learn-vi" not in path.parts:
            run_syntax_check(["node", "--check"], path, errors)
    for path in root.rglob("*.sh"):
        if ".git" not in path.parts and ".learn-vi" not in path.parts:
            run_syntax_check(["bash", "-n"], path, errors)

    pycache = [path for path in root.rglob("__pycache__") if ".git" not in path.parts]
    if pycache:
        errors.append(f"generated Python caches remain: {[str(path) for path in pycache]}")

    listed = subprocess.run(
        ["bash", str(root / "scripts" / "list-skills.sh")],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    if listed.returncode or len(listed.stdout.splitlines()) != 51:
        errors.append("inventory smoke: list-skills.sh did not return 51 skills")
    with tempfile.TemporaryDirectory(prefix="jimmy-kit-links-") as destination:
        linked = subprocess.run(
            ["bash", str(root / "scripts" / "link-skills.sh"), destination],
            cwd=root,
            capture_output=True,
            text=True,
            check=False,
        )
        entries = list(Path(destination).iterdir())
        if linked.returncode or len(entries) != 51 or not all(path.is_symlink() for path in entries):
            errors.append("link smoke: link-skills.sh did not create 51 isolated symlinks")

    if errors:
        for error in errors:
            print(f"[FAIL] {error}")
        print(f"repository-contract-audit: FAIL ({len(errors)} findings)")
        return 1

    print(
        "repository-contract-audit: PASS "
        "(51 skills; metadata, links, language, paths, runtime references, syntax, inventory/link smoke)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

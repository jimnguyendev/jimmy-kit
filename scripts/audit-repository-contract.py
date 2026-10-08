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
# Letters that occur in Vietnamese but not in other Latin-script languages, so names such as
# "José" or "Tomás" in code samples do not trip the check.
VIETNAMESE = re.compile(
    r"[ạảấầẩẫậăắằẳẵặẹẻẽếềểễệỉịọỏốồổỗộơớờởỡợụủưứừửữựỳỵỷỹđ"
    r"ẠẢẤẦẨẪẬĂẮẰẲẴẶẸẺẼẾỀỂỄỆỈỊỌỎỐỒỔỖỘƠỚỜỞỠỢỤỦƯỨỪỬỮỰỲỴỶỸĐ]"
)
ASCII_VIETNAMESE = re.compile(
    r"\b(?:khong|duoc|nguon|chay|phien ban|tai ve)\b", re.IGNORECASE
)
RUNTIME_REFERENCE = re.compile(
    r"(?<![a-z-])sage/|\.sage/|sage-[a-z-]+\.(?:sh|py)|/sage-|sage add|delegate_task|Hermes"
)
LINK = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
# A skill whose deliverable is the target project's own docs/ tree, not a skill output.
DOCS_PATH_ALLOWED = ("skills/golang/backend-go-documentation/",)


def load_catalog(root: Path) -> tuple[int, set[Path]]:
    """Total skill count and vendored skill dirs, both from groups.json."""
    catalog = json.loads((root / "groups.json").read_text(encoding="utf-8"))
    total = sum(len(list((root / d).glob("*/SKILL.md")))
                for g in catalog["groups"].values() for d in g["dirs"])
    return total, {(root / rel).resolve() for rel in catalog.get("vendored", {})}


def vendored_skill(path: Path, vendored: set[Path]) -> bool:
    return any(path.resolve().is_relative_to(v) for v in vendored)


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
    expected, vendored = load_catalog(root)
    catalog_check = subprocess.run(
        [sys.executable, str(root / "scripts" / "kit.py"), "check"],
        capture_output=True, text=True, check=False,
    )
    if catalog_check.returncode:
        errors.append("catalog: scripts/kit.py check failed: " + catalog_check.stdout.strip())

    if len(skill_files) != expected:
        errors.append(f"inventory: groups.json expects {expected} skills, found {len(skill_files)}")

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
        if not vendored_skill(path, vendored) and not any(phrase in description for phrase in TRIGGER_PHRASES):
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
        if vendored_skill(path, vendored):
            continue  # upstream content is kept verbatim; its links are upstream's to fix
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
        if vendored_skill(path, vendored):
            continue
        if VIETNAMESE.search(text) or ASCII_VIETNAMESE.search(text):
            errors.append(f"{path}: Vietnamese text remains in runnable skill sources")
        for line in text.splitlines():
            if RUNTIME_REFERENCE.search(line):
                runtime_hits.append((path.relative_to(root), line.strip()))
        relative_posix = path.relative_to(root).as_posix()
        if path.name != "SCENARIO.md" and not relative_posix.startswith(DOCS_PATH_ALLOWED):
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

    tracked = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z"],
        capture_output=True, text=True, check=False,
    )
    if tracked.returncode:
        errors.append("cannot verify tracked Python caches: git ls-files failed")
    elif any("__pycache__" in Path(name).parts or name.endswith(".pyc")
             for name in tracked.stdout.split("\0") if name):
        errors.append("generated Python caches are tracked")

    listed = subprocess.run(
        ["bash", str(root / "scripts" / "list-skills.sh")],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    if listed.returncode or len(listed.stdout.splitlines()) != expected:
        errors.append(f"inventory smoke: list-skills.sh did not return {expected} skills")
    for mode in ("symlink", "copy"):
        with tempfile.TemporaryDirectory(prefix=f"jimmy-kit-{mode}-") as destination:
            command = [sys.executable, str(root / "scripts" / "kit.py"), "install", "--target", destination]
            if mode == "copy":
                command.append("--copy")
            else:
                command = ["bash", str(root / "scripts" / "link-skills.sh"), destination]
            installed = subprocess.run(command, cwd=root, capture_output=True, text=True, check=False)
            entries = list(Path(destination).iterdir())
            if installed.returncode or len(entries) != expected or any(path.is_symlink() != (mode == "symlink") for path in entries):
                errors.append(f"{mode} smoke: kit.py did not install {expected} isolated skills")
            for name in ("orchestrate", "tdd-go", "backend-go-testing", "reality-gate", "verify-app"):
                if not (Path(destination) / name / "SKILL.md").is_file():
                    errors.append(f"{mode} smoke: required skill missing: {name}")
            for entry in entries:
                if (entry / "CODEX_ORCHESTRATION.md").exists():
                    errors.append(f"{mode} smoke: removed adapter distributed: {entry.name}")
                for path in entry.rglob("*.md"):
                    if path.name != "SCENARIO.md" and "codex-orchestration" in path.read_text(encoding="utf-8").lower():
                        errors.append(f"{mode} smoke: removed plugin reference distributed: {path}")

    if errors:
        for error in errors:
            print(f"[FAIL] {error}")
        print(f"repository-contract-audit: FAIL ({len(errors)} findings)")
        return 1

    print(
        "repository-contract-audit: PASS "
        f"({expected} skills, {len(vendored)} vendored; catalog, metadata, links, language, paths, "
        "runtime references, syntax, inventory/install smoke)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

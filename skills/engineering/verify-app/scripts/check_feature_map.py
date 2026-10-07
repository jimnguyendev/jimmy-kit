#!/usr/bin/env python3
"""Check a verify skill's feature map against the feature entry contract.

usage: check_feature_map.py <features dir>

Checks:
- README.md exists, indexes at least one feature, every relative link resolves, no file is indexed
  twice, every feature file is indexed;
- each feature file has one H1 and exactly four H2 sections, each once, in order: Sub-features,
  How to get to it, Driving it with <harness>, Gotchas;
- Sub-features lists backticked IDs, unique across the map;
- the Driving section starts with "Preconditions:" and contains at least one runnable command
  (a backticked span after "Run");
- every sub-feature ID is either proven in the Driving section (its ID appears there next to a
  step) or explicitly skipped with a line "Skipped: `id` — <reason>".
Exit 0 = pass, 1 = findings, 2 = usage error.
"""
import re
import sys
from pathlib import Path

ORDER = ("Sub-features", "How to get to it", "Driving it with", "Gotchas")
LINK = re.compile(r"\]\(([^)#\s]+)(?:#[^)]*)?\)")


def strip_fences(text: str) -> str:
    return re.sub(r"^```.*?^```", "", text, flags=re.S | re.M)


def h2_sections(text: str) -> list[tuple[str, str]]:
    parts = re.split(r"^## +(.+)$", text, flags=re.M)
    return [(parts[i].strip(), parts[i + 1]) for i in range(1, len(parts) - 1, 2)]


def check(features: Path) -> list[str]:
    readme = features / "README.md"
    if not readme.is_file():
        return [f"{readme}: missing index"]
    errors: list[str] = []
    readme_text = strip_fences(readme.read_text(encoding="utf-8"))
    targets = [t for t in LINK.findall(readme_text) if not t.startswith(("http://", "https://", "mailto:"))]
    for t in targets:
        if not (features / t).exists():
            errors.append(f"README.md: link to missing {t}")
    indexed = [Path(t).name for t in targets if t.endswith(".md") and Path(t).name != "README.md"]
    for name in sorted({n for n in indexed if indexed.count(n) > 1}):
        errors.append(f"README.md: {name} is indexed more than once")
    files = sorted(p.name for p in features.glob("*.md") if p.name != "README.md")
    if not files:
        errors.append("feature map has no feature files")
    for name in files:
        if name not in indexed:
            errors.append(f"README.md: {name} is not indexed")

    seen_ids: dict[str, str] = {}
    for name in files:
        text = strip_fences((features / name).read_text(encoding="utf-8"))
        if len(re.findall(r"^# ", text, flags=re.M)) != 1:
            errors.append(f"{name}: expected exactly one H1")
        secs = h2_sections(text)
        heads = [h for h, _ in secs]
        if len(secs) != 4 or not all(h.startswith(o) for h, o in zip(heads, ORDER)):
            errors.append(f"{name}: H2 sections must be {', '.join(ORDER)}, each once, in order; found {heads}")
            continue
        sub, entry, drive, gotchas = (body for _, body in secs)
        ids = re.findall(r"^\s*[-*] +`([a-z0-9][a-z0-9-]*)`", sub, flags=re.M)
        if not ids:
            errors.append(f"{name}: Sub-features lists no backticked IDs")
        for i in ids:
            if i in seen_ids:
                errors.append(f"{name}: sub-feature ID {i} already used in {seen_ids[i]}")
            seen_ids[i] = name
        if not entry.strip():
            errors.append(f"{name}: How to get to it lists no entry point")
        if not re.match(r"\s*Preconditions:", drive):
            errors.append(f"{name}: '{heads[2]}' does not start with Preconditions:")
        if not re.search(r"\bRun `[^`]+`", drive):
            errors.append(f"{name}: '{heads[2]}' has no runnable command (Run `...`)")
        skipped = set(re.findall(r"Skipped: `([a-z0-9-]+)`", drive + gotchas))
        for i in ids:
            if i not in skipped and f"`{i}`" not in drive:
                errors.append(f"{name}: sub-feature {i} is neither driven nor marked 'Skipped: `{i}` — reason'")
    return errors


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    features = Path(sys.argv[1])
    errors = check(features)
    for e in errors:
        print(f"FAIL {e}")
    n = len([p for p in features.glob("*.md") if p.name != "README.md"])
    print(f"feature-map: {'PASS' if not errors else 'FAIL'} ({n} feature files, {len(errors)} findings)")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())

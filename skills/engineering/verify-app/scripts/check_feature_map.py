#!/usr/bin/env python3
"""Check a verify skill's feature map against the feature entry contract.

usage: check_feature_map.py <features dir>

Checks: README.md exists and indexes every feature file; every index link resolves; each feature
file has one H1 and exactly four H2 sections in order (Sub-features, How to get to it, Driving it
with <harness>, Gotchas); Sub-features lists at least one backticked ID; Driving starts its
preconditions with "Preconditions:"; IDs are unique across the map. Exit 0 = pass, 1 = findings.
"""
import re
import sys
from pathlib import Path

ORDER = ("Sub-features", "How to get to it", "Driving it with", "Gotchas")
LINK = re.compile(r"\]\(\./([^)#]+\.md)\)")


def strip_fences(text: str) -> str:
    return re.sub(r"^```.*?^```", "", text, flags=re.S | re.M)


def sections(text: str) -> dict[str, str]:
    parts = re.split(r"^## +(.+)$", text, flags=re.M)
    return {parts[i].strip(): parts[i + 1] for i in range(1, len(parts) - 1, 2)}


def check(features: Path) -> list[str]:
    errors: list[str] = []
    readme = features / "README.md"
    if not readme.is_file():
        return [f"{readme}: missing index"]
    linked = set(LINK.findall(strip_fences(readme.read_text(encoding="utf-8"))))
    files = {p.name for p in features.glob("*.md") if p.name != "README.md"}
    for name in sorted(linked - files):
        errors.append(f"README.md: index links to missing {name}")
    for name in sorted(files - linked):
        errors.append(f"README.md: {name} is not indexed")
    seen_ids: dict[str, str] = {}
    for name in sorted(files):
        text = strip_fences((features / name).read_text(encoding="utf-8"))
        if len(re.findall(r"^# ", text, flags=re.M)) != 1:
            errors.append(f"{name}: expected exactly one H1")
        found = sections(text)
        heads = list(found)
        if len(heads) != 4 or not all(h.startswith(o) for h, o in zip(heads, ORDER)):
            errors.append(f"{name}: H2 sections must be {', '.join(ORDER)} in order; found {heads}")
            continue
        ids = re.findall(r"^\s*[-*] +`([a-z0-9][a-z0-9-]*)`", found[heads[0]], flags=re.M)
        if not ids:
            errors.append(f"{name}: Sub-features lists no backticked IDs")
        for i in ids:
            if i in seen_ids:
                errors.append(f"{name}: sub-feature ID {i} already used in {seen_ids[i]}")
            seen_ids[i] = name
        if not re.search(r"^\s*-?\s*[-*]?\s*Preconditions:", found[heads[2]], flags=re.M):
            errors.append(f"{name}: '{heads[2]}' does not start with Preconditions:")
        if not found[heads[1]].strip():
            errors.append(f"{name}: How to get to it lists no entry point")
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

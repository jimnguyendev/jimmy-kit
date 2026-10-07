#!/usr/bin/env python3
"""Group-aware catalog tool for Jimmy Kit. groups.json is the single source of truth.

usage:
  kit.py groups                                  list groups with skill counts
  kit.py list [--group a,b]                      list skill paths (all groups by default)
  kit.py install [--group a,b] [--target DIR] [--copy] [--force]
                                                 symlink (default) or copy skills into DIR
                                                 (default ~/.claude/skills)
  kit.py npx --group a,b [--agent claude-code]   print the `npx skills add` command for groups
  kit.py check                                   validate catalog, vendored provenance, plugin manifests
  kit.py plugins [--write]                       show or rewrite the per-group plugin entries
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "groups.json"
MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"
PLUGIN = ROOT / ".claude-plugin" / "plugin.json"
REPO_SLUG = "jimnguyendev/jimmy-kit"


def load() -> dict:
    return json.loads(CATALOG.read_text(encoding="utf-8"))


def group_skills(catalog: dict, name: str) -> list[Path]:
    skills: list[Path] = []
    for rel in catalog["groups"][name]["dirs"]:
        skills += sorted(p.parent for p in (ROOT / rel).glob("*/SKILL.md"))
    return skills


def selected(catalog: dict, spec: str | None) -> list[str]:
    if not spec or spec == "all":
        return list(catalog["groups"])
    names = [g.strip() for g in spec.split(",") if g.strip()]
    unknown = [g for g in names if g not in catalog["groups"]]
    if unknown:
        sys.exit(f"unknown group(s): {', '.join(unknown)}. Known: {', '.join(catalog['groups'])}, all")
    return names


def skills_for(catalog: dict, spec: str | None) -> list[Path]:
    out: list[Path] = []
    for g in selected(catalog, spec):
        out += [s for s in group_skills(catalog, g) if s not in out]
    return out


def cmd_groups(catalog: dict, _args) -> int:
    total = 0
    for name, g in catalog["groups"].items():
        n = len(group_skills(catalog, name))
        total += n
        print(f"{name:<10} {n:>3}  {g['description']}")
    print(f"{'all':<10} {total:>3}  every group")
    return 0


def cmd_list(catalog: dict, args) -> int:
    for s in skills_for(catalog, args.group):
        print(s.relative_to(ROOT).as_posix() + "/SKILL.md")
    return 0


def cmd_install(catalog: dict, args) -> int:
    dest = Path(args.target).expanduser() if args.target else Path.home() / ".claude" / "skills"
    if dest.resolve().is_relative_to(ROOT):
        sys.exit(f"target {dest} resolves into this repo; refusing to self-install")
    dest.mkdir(parents=True, exist_ok=True)
    done = skipped = 0
    for skill in skills_for(catalog, args.group):
        target = dest / skill.name
        if target.is_symlink() or target.exists():
            ours = target.is_symlink() and target.resolve().is_relative_to(ROOT)
            if not (ours or args.force):
                print(f"skip {target}: exists and is not a link into this kit (use --force)")
                skipped += 1
                continue
            if target.is_dir() and not target.is_symlink():
                shutil.rmtree(target)
            else:
                target.unlink()
        if args.copy:
            shutil.copytree(skill, target)
        else:
            target.symlink_to(skill)
        done += 1
    verb = "Copied" if args.copy else "Linked"
    print(f"{verb} {done} skills into {dest}" + (f" ({skipped} skipped)" if skipped else ""))
    return 1 if skipped else 0


def cmd_npx(catalog: dict, args) -> int:
    parts = [f"npx skills add {REPO_SLUG}"]
    parts += [f"--agent {a}" for a in (args.agent or ["claude-code"])]
    parts += [f"--skill {s.name}" for s in skills_for(catalog, args.group)]
    print(" \\\n  ".join(parts))
    return 0


def plugin_entries(catalog: dict) -> list[dict]:
    entries = []
    for name, g in catalog["groups"].items():
        dirs = g["dirs"]
        if len(dirs) == 1:
            source, skills = "./" + dirs[0], ["./"]
        else:
            parents = {Path(d).parent.as_posix() for d in dirs}
            if len(parents) != 1:
                sys.exit(f"group {name}: multi-dir groups must share one parent directory")
            parent = parents.pop()
            source = "./" + parent
            skills = ["./" + Path(d).relative_to(parent).as_posix() + "/" for d in dirs]
        n = len(group_skills(catalog, name))
        entries.append({
            "name": name,
            "source": source,
            "strict": False,
            "skills": skills,
            "description": f"{g['description']} ({n} skills)",
        })
    return entries


def expected_manifests(catalog: dict) -> tuple[dict, dict]:
    market = json.loads(MARKETPLACE.read_text(encoding="utf-8"))
    plugin = json.loads(PLUGIN.read_text(encoding="utf-8"))
    total = sum(len(group_skills(catalog, g)) for g in catalog["groups"])
    dirs = sorted({d for g in catalog["groups"].values() for d in g["dirs"]})
    plugin["skills"] = ["./" + d + "/" for d in dirs]
    plugin["description"] = (f"{total} skills for AI agents — routing dispatcher, quality gates, product, UX, "
                             "analytics, engineering, Go and database (MySQL, PostgreSQL, MongoDB, ClickHouse).")
    main = market["plugins"][0]
    main["source"] = "./"
    main["version"] = plugin["version"]
    main["description"] = f"All {total} skills (every group)."
    market["description"] = f"Jimmy Kit — {total} skills for AI agents, installable whole or by group."
    market["plugins"] = [main] + plugin_entries(catalog)
    return market, plugin


def cmd_plugins(catalog: dict, args) -> int:
    market, plugin = expected_manifests(catalog)
    if args.write:
        MARKETPLACE.write_text(json.dumps(market, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        PLUGIN.write_text(json.dumps(plugin, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"wrote {MARKETPLACE.relative_to(ROOT)} and {PLUGIN.relative_to(ROOT)}")
    else:
        print(json.dumps(market["plugins"], indent=2, ensure_ascii=False))
    return 0


def cmd_check(catalog: dict, _args) -> int:
    errors: list[str] = []
    grouped: dict[Path, str] = {}
    for name, g in catalog["groups"].items():
        for rel in g["dirs"]:
            if not (ROOT / rel).is_dir():
                errors.append(f"group {name}: missing dir {rel}")
        for skill in group_skills(catalog, name):
            if skill in grouped:
                errors.append(f"{skill.relative_to(ROOT)} is in groups {grouped[skill]} and {name}")
            grouped[skill] = name
    on_disk = {p.parent for p in (ROOT / "skills").glob("*/*/SKILL.md")}
    for orphan in sorted(on_disk - set(grouped)):
        errors.append(f"{orphan.relative_to(ROOT)} belongs to no group")
    names: dict[str, Path] = {}
    for skill in grouped:
        if skill.name in names:
            errors.append(f"duplicate skill name {skill.name}: {names[skill.name]} and {skill}")
        names[skill.name] = skill
    for rel, meta in catalog.get("vendored", {}).items():
        path = ROOT / rel
        if path not in grouped:
            errors.append(f"vendored {rel} is not a grouped skill")
        if not (path / "LICENSE").is_file():
            errors.append(f"vendored {rel} has no LICENSE file")
        if meta.get("notice") and not (path / "NOTICE").is_file():
            errors.append(f"vendored {rel}: upstream ships a NOTICE file that was not kept")
        for key in ("upstream", "commit", "license"):
            if not meta.get(key):
                errors.append(f"vendored {rel} lacks {key}")
    market, plugin = expected_manifests(catalog)
    if json.loads(MARKETPLACE.read_text(encoding="utf-8")) != market:
        errors.append("marketplace.json is out of date: run scripts/kit.py plugins --write")
    if json.loads(PLUGIN.read_text(encoding="utf-8")) != plugin:
        errors.append("plugin.json is out of date: run scripts/kit.py plugins --write")
    for e in errors:
        print(f"ERROR {e}")
    print(f"catalog: {len(grouped)} skills in {len(catalog['groups'])} groups, "
          f"{len(catalog.get('vendored', {}))} vendored" + ("" if not errors else f", {len(errors)} error(s)"))
    return 1 if errors else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("groups")
    p = sub.add_parser("list"); p.add_argument("--group")
    p = sub.add_parser("install"); p.add_argument("--group"); p.add_argument("--target")
    p.add_argument("--copy", action="store_true"); p.add_argument("--force", action="store_true")
    p = sub.add_parser("npx"); p.add_argument("--group", required=True); p.add_argument("--agent", action="append")
    sub.add_parser("check")
    p = sub.add_parser("plugins"); p.add_argument("--write", action="store_true")
    args = ap.parse_args()
    return {"groups": cmd_groups, "list": cmd_list, "install": cmd_install, "npx": cmd_npx,
            "check": cmd_check, "plugins": cmd_plugins}[args.cmd](load(), args)


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env bash
set -euo pipefail
# Symlink kit skills into ~/.claude/skills (or a target dir) so the local CLI picks them up.
# usage: link-skills.sh [TARGET_DIR] [--group core,golang,...]   (no --group = every group)
# Groups are defined in groups.json; `python3 scripts/kit.py groups` lists them.
# Originally adapted from mattpocockSkills (github.com/yykui/mattpocockSkills), MIT-style credit in README.
REPO="$(cd "$(dirname "$0")/.." && pwd)"
TARGET=""; GROUP=""
while [ $# -gt 0 ]; do
  case "$1" in
    --group) GROUP="$2"; shift 2 ;;
    --group=*) GROUP="${1#--group=}"; shift ;;
    *) TARGET="$1"; shift ;;
  esac
done
args=(install)
[ -n "$TARGET" ] && args+=(--target "$TARGET")
[ -n "$GROUP" ] && args+=(--group "$GROUP")
exec python3 "$REPO/scripts/kit.py" "${args[@]}"

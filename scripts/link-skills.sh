#!/usr/bin/env bash
set -euo pipefail
# Symlink every skill in this kit into ~/.claude/skills so the local CLI picks them up.
# Adapted from mattpocockSkills (github.com/yykui/mattpocockSkills), MIT-style credit in README.
REPO="$(cd "$(dirname "$0")/.." && pwd)"
DEST="${1:-$HOME/.claude/skills}"
# Guard: if DEST is a symlink resolving into this repo, bail instead of polluting the working copy.
if [ -L "$DEST" ] && [[ "$(readlink -f "$DEST")" == "$REPO"* ]]; then
  echo "DEST resolves into this repo — aborting to avoid self-linking." >&2; exit 1
fi
mkdir -p "$DEST"
count=0
while IFS= read -r skill_md; do
  dir="$(dirname "$skill_md")"; name="$(basename "$dir")"
  ln -sfn "$dir" "$DEST/$name" && count=$((count+1))
done < <(find "$REPO/skills" -name SKILL.md)
echo "Linked $count skills into $DEST"

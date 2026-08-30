#!/usr/bin/env bash
set -euo pipefail
REPO="$(cd "$(dirname "$0")/.." && pwd)"
find "$REPO/skills" -name SKILL.md | sed "s|$REPO/||" | sort

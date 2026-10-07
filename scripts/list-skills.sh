#!/usr/bin/env bash
set -euo pipefail
# usage: list-skills.sh [--group core,golang,...]   (no --group = every group)
REPO="$(cd "$(dirname "$0")/.." && pwd)"
exec python3 "$REPO/scripts/kit.py" list "$@"

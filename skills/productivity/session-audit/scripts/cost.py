#!/usr/bin/env python3
"""Print spend, API hours and tokens per session and by model from a project's transcripts.

Reads the cost-state records of each transcript. A record whose total drops below the one before
it starts a new run of the same session (a resume), so the runs are summed.
"""
import argparse
import collections
import datetime
import glob
import json
import os
import re
import sys


def default_project():
    slug = re.sub(r"[^A-Za-z0-9]", "-", os.getcwd())
    return os.path.join(os.path.expanduser("~"), ".claude", "projects", slug)


def runs_of(path):
    runs = []
    prev = None
    with open(path, errors="replace") as fh:
        for line in fh:
            if not line.startswith('{"type":"cost-state"'):
                continue
            try:
                rec = json.loads(line)
            except ValueError:
                continue
            cost = rec.get("totalCostUSD") or 0
            if prev is not None and cost + 1e-9 < prev["totalCostUSD"]:
                runs.append(prev)
            prev = rec
    if prev:
        runs.append(prev)
    return runs


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--project", default=default_project(), help="transcript directory (default: derived from the cwd)")
    ap.add_argument("--days", type=int, default=0, help="only sessions modified in the last N days (0 = all)")
    args = ap.parse_args()

    if not os.path.isdir(args.project):
        print("no transcript directory: " + args.project, file=sys.stderr)
        return 1
    cutoff = datetime.datetime.now().timestamp() - args.days * 86400 if args.days else 0
    by_model = collections.Counter()
    tokens = collections.Counter()
    rows = []
    for path in glob.glob(os.path.join(args.project, "*.jsonl")):
        if os.path.getmtime(path) < cutoff:
            continue
        runs = runs_of(path)
        if not runs:
            continue
        start = min(r.get("startTime", 0) for r in runs)
        rows.append(
            (
                datetime.datetime.fromtimestamp(start / 1000).strftime("%Y-%m-%d"),
                os.path.basename(path)[:8],
                round(sum(r["totalCostUSD"] for r in runs), 1),
                len(runs),
                round(sum(r.get("totalAPIDuration", 0) for r in runs) / 3.6e6, 1),
                round(sum(r.get("totalToolDuration", 0) for r in runs) / 3.6e6, 1),
                round(sum(r.get("totalDuration", 0) for r in runs) / 3.6e6, 1),
            )
        )
        for run in runs:
            for model, use in (run.get("modelUsage") or {}).items():
                by_model[model] += use.get("costUSD", 0)
                tokens["cache_read"] += use.get("cacheReadInputTokens", 0)
                tokens["cache_write"] += use.get("cacheCreationInputTokens", 0)
                tokens["output"] += use.get("outputTokens", 0)
                tokens["input"] += use.get("inputTokens", 0)
    rows.sort()
    print("date | session | USD | runs | api h | tool h | wall h")
    for row in rows:
        print(" | ".join(str(c) for c in row))
    print(
        "TOTAL USD %.1f | sessions %d | api h %.1f | tool h %.1f"
        % (sum(r[2] for r in rows), len(rows), sum(r[4] for r in rows), sum(r[5] for r in rows))
    )
    print("BY MODEL USD", {k: round(v, 1) for k, v in by_model.most_common()})
    print("TOKENS M", {k: round(v / 1e6, 1) for k, v in tokens.items()})
    return 0


if __name__ == "__main__":
    sys.exit(main())

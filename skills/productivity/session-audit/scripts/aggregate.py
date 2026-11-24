#!/usr/bin/env python3
"""Merge the auditors' JSON files and print the correction rate and the counts behind it.

    aggregate.py <findings dir> [--previous <summary.json>] [--save <summary.json>] [--list]

Every <findings dir>/*.json with "sessions" and "incidents" keys is merged. The rate is
corrections over owner turns. --previous prints the change against an earlier summary written
with --save. --list also prints the auditor's one-line description of the ignored-rule and
script-candidate corrections (private text; the default prints counts and ids only).
"""
import argparse
import collections
import glob
import json
import os
import sys

IGNORED = "rule_existed_and_ignored"
SCRIPT = "code_gate_or_script"


def load(directory):
    sessions = {}
    incidents = []
    for path in sorted(glob.glob(os.path.join(directory, "*.json"))):
        try:
            with open(path) as fh:
                data = json.load(fh)
        except ValueError:
            continue
        if not isinstance(data, dict) or "incidents" not in data or "sessions" not in data:
            continue
        for s in data["sessions"]:
            sessions[s["id"]] = s
        incidents.extend(data["incidents"])
    return sessions, incidents


def summarise(sessions, incidents):
    turns = sum(s.get("human_turns", 0) for s in sessions.values())
    return {
        "sessions": len(sessions),
        "owner_turns": turns,
        "corrections": len(incidents),
        "rate": round(len(incidents) / turns, 4) if turns else 0,
        "broke_existing_rule": sum(1 for i in incidents if i.get("root_cause") == IGNORED),
        "script_candidates": sum(1 for i in incidents if i.get("fix_by") == SCRIPT),
        "by_failure": dict(collections.Counter(i.get("failure") for i in incidents)),
        "by_root_cause": dict(collections.Counter(i.get("root_cause") for i in incidents)),
        "by_fix_route": dict(collections.Counter(i.get("fix_by") for i in incidents)),
    }


def print_counts(title, counts, before):
    print("\n" + title)
    for key, n in sorted(counts.items(), key=lambda kv: -kv[1]):
        delta = "" if before is None else " (%+d)" % (n - before.get(key, 0))
        print("  %4d  %s%s" % (n, key, delta))


def print_list(title, incidents, with_text):
    print("\n" + title)
    for i in sorted(incidents, key=lambda i: (-i.get("severity", 0), i.get("date", ""))):
        line = "  %s turn %s sev %s %s" % (i.get("session"), i.get("turn"), i.get("severity"), i.get("failure"))
        if with_text:
            line += " | " + str(i.get("what_went_wrong", "")) + " | fix: " + str(i.get("fix_note", ""))
        print(line)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("findings_dir")
    ap.add_argument("--previous", help="summary file from an earlier run, for the delta")
    ap.add_argument("--save", help="write this run's summary to this file")
    ap.add_argument("--list", action="store_true", help="print the auditor's text for the two lists")
    args = ap.parse_args()

    sessions, incidents = load(args.findings_dir)
    if not sessions:
        print("no findings files in " + args.findings_dir, file=sys.stderr)
        return 1
    now = summarise(sessions, incidents)
    before = None
    if args.previous:
        with open(args.previous) as fh:
            before = json.load(fh)

    print(
        "%d corrections over %d owner turns in %d sessions: %.1f%%"
        % (now["corrections"], now["owner_turns"], now["sessions"], 100 * now["rate"])
    )
    if before:
        print(
            "previous: %d over %d: %.1f%% (rate %+.1f points)"
            % (before["corrections"], before["owner_turns"], 100 * before["rate"], 100 * (now["rate"] - before["rate"]))
        )
    print("broke an existing rule: %d" % now["broke_existing_rule"])
    print("a script could catch: %d" % now["script_candidates"])
    print_counts("by failure", now["by_failure"], before and before.get("by_failure"))
    print_counts("by root cause", now["by_root_cause"], before and before.get("by_root_cause"))
    print_counts("by fix route", now["by_fix_route"], before and before.get("by_fix_route"))
    print_list("corrections that broke an existing rule", [i for i in incidents if i.get("root_cause") == IGNORED], args.list)
    print_list("candidates for a script", [i for i in incidents if i.get("fix_by") == SCRIPT], args.list)

    if args.save:
        with open(args.save, "w") as fh:
            json.dump(now, fh, indent=1, sort_keys=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())

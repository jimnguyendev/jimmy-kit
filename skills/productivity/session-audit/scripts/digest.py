#!/usr/bin/env python3
"""Write one Markdown digest per Claude Code session and print a table of numbers.

A digest holds the owner's turns, each with the tail of the assistant text just before it.
It contains private conversation text: --out must be a gitignored directory.
"""
import argparse
import datetime
import glob
import json
import os
import re
import sys


def default_project():
    slug = re.sub(r"[^A-Za-z0-9]", "-", os.getcwd())
    return os.path.join(os.path.expanduser("~"), ".claude", "projects", slug)


def text_of(content):
    if isinstance(content, str):
        return content
    return "\n".join(
        b.get("text", "") for b in content or [] if isinstance(b, dict) and b.get("type") == "text"
    )


def clean(text):
    text = re.sub(r"<system-reminder>.*?</system-reminder>", "", text, flags=re.S)
    text = re.sub(r"<local-command-[a-z]+>.*?</local-command-[a-z]+>", "", text, flags=re.S)
    text = re.sub(r"<command-(name|message|args)>.*?</command-\1>", "", text, flags=re.S)
    text = re.sub(r"<task-notification>.*?</task-notification>", "[task-notification]", text, flags=re.S)
    return text.strip()


def read_session(path):
    title = ""
    turns = []
    last_assistant = ""
    first_ts = last_ts = None
    tool_calls = 0
    compactions = 0
    with open(path, errors="replace") as fh:
        for line in fh:
            try:
                rec = json.loads(line)
            except ValueError:
                continue
            kind = rec.get("type")
            if kind == "ai-title":
                title = rec.get("aiTitle") or rec.get("title") or title
            if rec.get("isSidechain"):
                continue
            ts = rec.get("timestamp")
            if ts:
                first_ts = first_ts or ts
                last_ts = ts
            if kind == "assistant":
                content = rec.get("message", {}).get("content")
                for block in content or []:
                    if isinstance(block, dict) and block.get("type") == "tool_use":
                        tool_calls += 1
                said = text_of(content).strip()
                if said:
                    last_assistant = said
            elif kind == "user":
                if rec.get("isMeta"):
                    continue
                if rec.get("isCompactSummary"):
                    compactions += 1
                    continue
                content = rec.get("message", {}).get("content")
                if isinstance(content, list) and any(
                    isinstance(b, dict) and b.get("type") == "tool_result" for b in content
                ):
                    continue
                said = clean(text_of(content))
                if not said or said.startswith("[task-notification]") or said.startswith("[SYSTEM NOTIFICATION"):
                    continue
                if said.startswith("This session is being continued"):
                    compactions += 1
                    continue
                turns.append((ts, last_assistant, said))
                last_assistant = ""
    return title, turns, first_ts, last_ts, tool_calls, compactions


def session_spend(path):
    last = None
    total = 0.0
    with open(path, errors="replace") as fh:
        for line in fh:
            if not line.startswith('{"type":"cost-state"'):
                continue
            try:
                rec = json.loads(line)
            except ValueError:
                continue
            cost = rec.get("totalCostUSD") or 0
            if last is not None and cost + 1e-9 < last:
                total += last
            last = cost
    return total + (last or 0)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--project", default=default_project(), help="transcript directory (default: derived from the cwd)")
    ap.add_argument("--days", type=int, default=14, help="only sessions modified in the last N days")
    ap.add_argument("--out", required=True, help="directory for the digests (gitignored)")
    args = ap.parse_args()

    if not os.path.isdir(args.project):
        print("no transcript directory: " + args.project, file=sys.stderr)
        return 1
    os.makedirs(args.out, exist_ok=True)
    cutoff = datetime.datetime.now().timestamp() - args.days * 86400
    files = sorted(glob.glob(os.path.join(args.project, "*.jsonl")), key=os.path.getmtime)

    rows = []
    for path in files:
        if os.path.getmtime(path) < cutoff:
            continue
        sid = os.path.basename(path)[:8]
        title, turns, first_ts, last_ts, tool_calls, compactions = read_session(path)
        if not turns:
            continue
        target = os.path.join(args.out, sid + ".md")
        with open(target, "w") as out:
            out.write(
                "# session %s | %s | %s .. %s | owner turns %d | tool calls %d | compactions %d\n\n"
                % (sid, title, first_ts, last_ts, len(turns), tool_calls, compactions)
            )
            for i, (ts, said, human) in enumerate(turns):
                if said:
                    out.write("## [%d] ASSISTANT said just before (tail, cut):\n%s\n\n" % (i, said[-1500:]))
                out.write("## [%d] OWNER %s:\n%s\n\n" % (i, ts, human[:2500]))
        rows.append(
            (
                sid,
                (first_ts or "")[:10],
                (last_ts or "")[:10],
                len(turns),
                tool_calls,
                compactions,
                round(session_spend(path)),
                os.path.getsize(target) // 1000,
            )
        )

    print("session | first | last | owner turns | tool calls | compactions | spend USD | digest KB")
    for row in rows:
        print(" | ".join(str(c) for c in row))
    print(
        "TOTAL sessions %d | owner turns %d | spend USD %d | digest KB %d"
        % (len(rows), sum(r[3] for r in rows), sum(r[6] for r in rows), sum(r[7] for r in rows))
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())

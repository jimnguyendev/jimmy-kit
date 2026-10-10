#!/usr/bin/env python3
"""Write DesignSync get_file results found in Claude Code transcripts to a directory.

usage: extract-design.py <out_dir> <transcript.jsonl>...

The root session reads each design page with DesignSync `get_file`; the tool results are
then in the session transcript (~/.claude/projects/<project>/<session>.jsonl). This script
copies them byte for byte instead of having a model retype them. The last result per path
wins. It prints one line per file (path, bytes, truncated flag) and never prints contents.
A path that would escape <out_dir>, or content that is not text or valid base64, is reported
and skipped; the other files are still written. Exit 1 when anything was skipped or nothing found.
"""

from __future__ import annotations

import base64
import binascii
import json
import os
import sys


def walk(node, found: dict) -> None:
    if isinstance(node, dict):
        for value in node.values():
            walk(value, found)
    elif isinstance(node, list):
        for value in node:
            walk(value, found)
    elif isinstance(node, str) and '"method":"get_file"' in node[:200]:
        try:
            obj = json.loads(node)
        except ValueError:
            return
        if isinstance(obj, dict) and obj.get("method") == "get_file" and "content" in obj and obj.get("path"):
            found[obj["path"]] = obj


def destination(out: str, path: str) -> str | None:
    root = os.path.realpath(out)
    dest = os.path.realpath(os.path.join(root, path.lstrip("/")))
    if dest == root:
        return None
    try:
        return dest if os.path.commonpath((root, dest)) == root else None
    except ValueError:  # different drives on Windows
        return None


def main(argv: list[str]) -> int:
    if len(argv) < 3:
        print(__doc__.strip().splitlines()[2], file=sys.stderr)
        return 2
    out = argv[1]
    found: dict = {}
    for transcript in argv[2:]:
        with open(transcript, encoding="utf-8") as fh:
            for line in fh:
                try:
                    walk(json.loads(line), found)
                except ValueError:
                    continue
    if not found:
        print("extract-design: no get_file results in the given transcripts", file=sys.stderr)
        return 1
    status = 0
    for path, obj in sorted(found.items()):
        dest = destination(out, path)
        if dest is None:
            print(f"{path}\trefused: escapes {out}", file=sys.stderr)
            status = 1
            continue
        data = obj["content"]
        if not isinstance(data, str):
            print(f"{path}\tskipped: content is {type(data).__name__}, not text", file=sys.stderr)
            status = 1
            continue
        try:
            raw = base64.b64decode(data, validate=True) if obj.get("isBase64") else data.encode("utf-8")
        except (binascii.Error, ValueError):
            print(f"{path}\tskipped: content is not valid base64", file=sys.stderr)
            status = 1
            continue
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "wb") as fh:
            fh.write(raw)
        print(f"{path}\t{len(raw)}\ttruncated={obj.get('truncated')}")
    return status


if __name__ == "__main__":
    sys.exit(main(sys.argv))

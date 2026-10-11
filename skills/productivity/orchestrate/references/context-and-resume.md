# Keeping the root's context small and resumable

Read when a sprint will outlive one context window, which is any sprint with more than a few
packets.

## HANDOFF after every land

The state on disk is enough to resume only if it is current. The root rewrites `HANDOFF.md`
after **every** land and after every dispatch that changes what is running: what landed (packet,
commit/PR), what is running (packet, route, worktree, agent ID or pid, log path), the next
actions in order, the owner's standing rules, and a `## Waiting on owner` section. Append, then
prune superseded lines; keep it under about 6 KB: the resume hook prints the first 6000 bytes, then
prints `truncated: read the full file before the catch-up` when the file is longer. It always prints the
whole `## Waiting on owner` section separately, so no pending brief is lost to the limit.

`## Waiting on owner` holds one decision brief per pending owner decision in the file form of
skill `ketchup` (references/decision-brief.md), or `None.`:

```markdown
## Waiting on owner

### 1. <decision in one sentence>
- What it is: <each PR, ADR, tool or term explained; ids only after the explanation>
- Why now: <what it blocks or what gets worse>
- Options:
  - A. <option>. Cost: <work, money, risk>. Effect: <what someone notices>.
  - B. <option>. Cost: <...>. Effect: <...>.
- Recommendation: <option and why>
- If no answer: <"I wait; X stays blocked", or the standing authority + reversible default + when>
- Evidence: <link or path>
```

Keys stay in English; values are in the owner's language. One option per line. A fresh root,
or the next session, relays these briefs as written, so it never has to reconstruct what a
question meant. Check the section after every rewrite:

```bash
python3 <installed-skill-dir>/scripts/orchestration_lint.py --phase handoff --handoff .orchestrate/HANDOFF.md
```

It fails on a missing part, an option without `Cost:` or `Effect:`, a `<placeholder>`, a
one-line question instead of a brief or next to one, `None.` next to a brief, a `What it is` under
30 non-space characters (counted the same way in every language), and an id (`ADR-0017`, `PR #12`, `MR !34`, a ticket key)
used in a brief but never introduced in its `What it is`. Whether the explanation is clear is
still the root's call.

## Context hooks

`scripts/orchestrate-context.sh` has two modes:

- `snapshot` (PreCompact): writes `.orchestrate/AUTO-STATE.md` from git and process state: the
  last commits on the default branch, main checkout status, every worktree with its branch,
  commits ahead and dirty files, executor processes still running, and the tail of recent
  executor logs in `.orchestrate/*.log`.
- `resume` (SessionStart, matcher `compact`): prints `HANDOFF.md`, `AUTO-STATE.md` and
  `SPRINT.md` into the fresh context with an instruction to continue without asking the user,
  and to open the next owner-facing message with a `/ketchup` catch-up. The complete `Waiting on owner`
  section follows, outside the 6000-byte limit.

Install once per machine:

```bash
mkdir -p ~/.claude/hooks
cp <installed-skill-dir>/scripts/orchestrate-context.sh ~/.claude/hooks/
chmod +x ~/.claude/hooks/orchestrate-context.sh
```

and add to `~/.claude/settings.json`:

```json
{
  "hooks": {
    "PreCompact": [
      { "hooks": [ { "type": "command", "timeout": 30,
          "command": "~/.claude/hooks/orchestrate-context.sh snapshot 2>/dev/null || true" } ] }
    ],
    "SessionStart": [
      { "matcher": "compact",
        "hooks": [ { "type": "command", "timeout": 15,
          "command": "~/.claude/hooks/orchestrate-context.sh resume 2>/dev/null || true" } ] }
    ]
  }
}
```

The hook finds the target repo from the session cwd when that directory has
`.orchestrate/SPRINT.md`. When the root runs from another directory, add one line per session
directory to `~/.claude/orchestrate-targets` (or the file named by `ORCH_TARGETS`):

```text
<session cwd> <target repo path>
```

A session with no match exits silently, so the hooks are safe to keep installed globally.

## Compaction window

On a 1M-token model, set an earlier automatic compaction so the summary is written while the
root still has room to read the hook output, for example in `~/.claude/settings.json`:

```json
{ "modelSettings": { "<model id>": { "autoCompactWindow": 600000 } } }
```

The origin run used 600k for Opus with a 1M window, after one session reached 906k of 1M
mostly on browser output the root should have delegated ([verification.md](verification.md)).

## After a session limit

See [dispatch-and-land.md](dispatch-and-land.md#session-limits): resume stopped agents with
`SendMessage` to their recorded agent IDs; do not respawn them.

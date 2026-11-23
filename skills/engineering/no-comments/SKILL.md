---
name: no-comments
description: >-
  Strip comments from a diff or a set of files through a fresh comment-hating reviewer, keep only
  the narrow exceptions, flag the code a comment was covering for, and offer an encoding for every
  "do not remove" constraint. Use for /no-comments, before landing a diff that adds narration,
  banners, commented-out code or workaround justifications, and when a repo decides to purge its
  comments.
user-invocable: true
---

# No comments

> **This skill exists to stop:** comments that narrate what the code already says, excuse a workaround instead of fixing it, or guard a constraint nobody encoded, so the code stays unclear and the prose rots.

## 🤖 0. HOW TO USE

- **Diff** (default): the scope is the caller's files or diff; without one, the current diff against the base branch (default `main`), working tree included.
- **Sweep**: a whole repo or directory. Split it into chunks a reviewer can read in one pass and run the reviewer once per chunk.

Output: the comment deletions applied, a proof that only comments changed, and a report (section 6).

A fresh reviewer judges. The caller acts on what the reviewer accepts. Defer to the reviewer's fresh read, but audit it (step 2).

## 1. Spawn the reviewer

Start a fresh subagent with the brief in [references/comment-sicko.md](references/comment-sicko.md) and the scope. Do not restate or soften its rules. Pick the subagent's reasoning effort for the size of the scope. For a sweep, one reviewer per chunk; never let a reviewer see a chunk outside its scope.

The repo's own instruction file (AGENTS.md, CLAUDE.md, a constitution) can add keeps the brief does not know about, such as a required package map file, an archlint marker, or a rule that every timeout carries its reason. Pass those keeps to the reviewer with the scope. The instruction file wins over the brief.

## 2. Audit the report

Reject:

- edits to application code, and edits outside the scope;
- a deletion of a comment that is on the keep list (section 3);
- a `MUST KILL` whose reason is wrong;
- a flag that calls intentional, kept code guilty.

Reshape flags on our own surprising code stay actionable. Do not restore those comments.

A keep survives only with proof that it is about something we cannot change. Look for lint and type suppressions the reviewer missed. A suppression that silences a correctness or safety rule stays an actionable `MUST KILL`. Restore a deletion only with the exact exception and proof within scope.

Before accepting a thin `IMPORTANT` or `do not remove` kill or keep, trace the symbol, or read why it exists from the record: the commits and MR/PR discussions that introduced it (`git log -S`, `git blame`, the linked review), citing what the authors wrote and marking inferences. An ambiguous kill stays killed. A keep that is refuted or still ambiguous is deleted.

Revert and rerun one rejected report with the failure named. If the second report is also rejected, report it open and fail the run.

## 3. Keep list

Only these survive (the brief carries the same list):

- legal or license headers;
- non-obvious behaviour forced by an external dependency, platform, vendor or protocol we cannot reshape;
- formatter and tool directives (`//go:build`, `//go:embed`, `// prettier-ignore`), and lint suppressions whose rule is faulty, pedantic or style-only;
- doc comments that define a public API contract;
- issue or RFC links that explain a constraint the code cannot express;
- keeps the repo's instruction file names (section 1).

Generated files (a `Code generated … DO NOT EDIT` header or the generator's own marker) are out of scope.

## 4. Prove only comments changed

Run a check that compares the code with comments stripped, before and after, for every touched file: parse both versions, print them without comments, and diff. For Go, `go/parser` + `go/printer` on files parsed without `parser.ParseComments`; for TypeScript, `ts.createPrinter({ removeComments: true })` over `ts.createSourceFile`. Any difference fails the run. Then run the formatter and the repo's build, lint and test gates. A test that scans source text can still change result when a comment disappears; the gates catch it.

## 5. Act on the flags

1. Fix trivial accepted flags directly: delete a dead path, drop a parameter, use the real API.
2. If a fix needs a shape, run `architect` once for the accepted set and the code around it. Stop at the sketch.
3. Implement the smallest root-cause fix in scope. Remove every named workaround. If the root cause is out of scope, land the smallest in-scope fix and report the rest open. Never add a symptom guard.
4. In a sweep, a flag that needs a change outside a pure comment pass is reported open with its file and symbol, not fixed in the same diff.

## 6. Constraint comments

A constraint comment says `do not remove`, `do not change wording`, or `talk to X before changing`. Leave keeps about things we cannot change. For the rest, offer the cheapest in-scope encoding: a type, a runtime check, a test, or a CI lint. Wait for interactive approval; an unattended or eval run needs the caller's approval in advance. If approved, encode, then delete. Otherwise delete, report the constraint open, and sketch the out-of-scope work.

## 7. Report

Deletion count, restored comments, reruns, the architect sketch, fixes, encoding offers, encodings, unenforced constraints, and other open work.

## Source

Adapted from pstack's `no-comments` skill and `comment-sicko` agent (https://github.com/cursor/plugins/tree/main/pstack, MIT, Lauren Tan). Changes: the agent brief ships inside the skill so any agent runtime can spawn it, pstack's `why` method is folded into step 2, step 4 (comment-only proof) and the sweep mode are new.

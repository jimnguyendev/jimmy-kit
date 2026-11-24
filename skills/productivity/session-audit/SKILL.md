---
name: session-audit
description: >-
  Measure how often the owner had to correct the agent, from the project's own Claude Code
  session transcripts. Use when the owner says the agent keeps repeating mistakes, when choosing
  the next rule, gate or skill fix from evidence instead of memory, after a long build to see
  where the spend and the corrections went, or to compare two periods.
---

# Session audit

> **This skill exists to stop:** choosing the next rule or gate from the last annoying session instead of from the whole record, so the same corrections come back and nobody can tell whether a fix worked.

## 🤖 0. HOW TO USE

Modes:
- **Audit** (default): digest, label, aggregate, report. Steps 1 to 5.
- **Spend only**: step 2 alone, when the question is cost.
- **Compare**: run Audit again later the same way and pass the earlier summary to `aggregate.py --previous`.

Output formats: a table per session (step 1), a spend table (step 2), a summary of counts (step 4) and a short report (step 5). Everything lives under `.jimmy/work/session-audit/<date>/`.

## Privacy first

Digests and findings hold private conversation text. Before writing anything, check that `.jimmy/work/session-audit/` is ignored by git (`git check-ignore -q .jimmy/work/session-audit/x`); if not, add it to `.gitignore`. Never commit, paste or publish a digest or a finding. A public report carries numbers only.

## Procedure

Transcripts of a project live in `~/.claude/projects/<working directory with every non-alphanumeric character as a dash>/*.jsonl`. The scripts derive that directory from the current one; pass `--project` for another.

1. **Digest.** `python3 scripts/digest.py --days 14 --out .jimmy/work/session-audit/<date>/digests` writes one Markdown file per session (owner turns, each with the end of the agent's message just before it) and prints sessions, dates, owner turns, tool calls, compactions, spend and digest size.
2. **Spend.** `python3 scripts/cost.py --days 14` prints USD, runs, API hours, tool hours and wall hours per session, the split by model and token totals. Read the top four sessions: in one real project they held two thirds of a month's spend and most of the corrections.
3. **Label.** Split the digests into batches of about 130 KB, whole sessions only (a session larger than a batch is its own batch). Start one read-only auditor per batch with the prompt in [references/auditor-prompt.md](references/auditor-prompt.md); each writes one JSON file into `.jimmy/work/session-audit/<date>/findings/`. The prompt is strict about not counting neutral follow-ups, new tasks, answers or approvals. Spot-check five counted corrections against their digest before going on.
4. **Aggregate.** `python3 scripts/aggregate.py .jimmy/work/session-audit/<date>/findings --save .jimmy/work/session-audit/<date>/summary.json` (add `--previous <earlier summary.json>` to compare, `--list` to see the auditors' text for the two lists). It prints corrections over owner turns, counts by failure, root cause and fix route, the corrections that broke an existing rule, and the candidates for a script.
5. **Report**, one page, in this order:
   1. The rate: corrections over owner turns, the session and turn counts, and the delta when there is an earlier summary.
   2. The corrections that broke an existing rule: a rule that is written and still broken needs a check, not another sentence.
   3. The candidates for a script: each with the check it would run and the mistake it would have failed.
   4. The most frequent failure types, with one fix route each.
   5. The spend of the top sessions.
   Pick the next enforcer from items 2 and 3, one at a time, and run the audit again after it ships.

## Limits

- One labelling pass is noisy. Compare a rate only with a rate produced the same way: same prompt, same period length, same kind of project.
- A rate over fewer than about 100 owner turns moves with a single session.
- Turns of subagents and tool results are not owner turns; the digest skips them. A turn typed as a reply to a question the agent should not have asked still counts only if it corrects.
- The scripts read transcripts, write only under `--out` (or the `--save` file) and print counts, ids and file sizes, not conversation text.

---
name: ketchup
description: >-
  Catch the owner up on everything since their last message, and write every question that asks
  them to decide as a decision brief they can answer without opening a link. Use for /ketchup,
  for the first owner-facing message after a compaction, resume, session limit or long silence,
  and whenever an agent is about to ask the owner to choose, approve, pay for or provide something.
---

# Ketchup — catch-up and decision briefs

> **This skill exists to stop:** an agent asking its owner to decide with a one-liner (a bare PR number, an ADR id, a library name, two options with no cost), so the owner has to ask "what is this?" before they can answer.

## 🤖 0. HOW TO USE

One format, two modes:

- **Catch-up** (`/ketchup`, or the first message to the owner after a compaction, resume, session limit or long silence): a read-only turn. Output: one sentence counting the action items, what happened, then one decision brief per action item (section 4).
- **Brief** (any time you ask the owner to decide: chat text, AskUserQuestion, a HANDOFF `Waiting on owner` entry, an end-of-wave report, a PR body that needs their call): one decision brief per decision (section 3). Field rules, the file form a linter can read, and the AskUserQuestion mapping: [references/decision-brief.md](references/decision-brief.md).

Read [references/examples.md](references/examples.md) (three bad questions rewritten, one good explanation) before the first brief of a session.

Done when every action item has all seven parts, every term the owner may not know is explained where it first appears, and the owner can answer without opening a link or asking back.

## 1. Is it the owner's call?

Raise a brief only for:

- a product choice: what users see, get, or pay;
- approval of an outward-facing or irreversible action not already authorized: publishing, opening a PR on a repository the session does not own, sending to real users, deleting or migrating data, a production deploy;
- spending: a paid service, new infrastructure, a bigger plan;
- access or credentials you lack;
- a change to scope the owner accepted.

Everything else is yours. Pick the option you would recommend, record it with a one-line reason where the work keeps decisions (HANDOFF, decision log, PR body), and report it as a decision taken so the owner can overrule it. A standing "decide, don't ask" instruction from the owner narrows the list further; follow it. Work you can still do yourself is not an action item.

## 2. Write for the owner

- **Language.** Reply in the language of the owner's own messages. If they keep writing rules for that language (a rules file in their agent config, the repo's AGENTS.md, memory), follow them, including which technical terms stay in English.
- **Plain voice.** Talk like one person to another: short sentences, one idea each, no jargon left unexplained, no slogans.
- **Names they know.** Call a PR, branch, packet or agent by what it does ("the PR that makes the land script run the tests"), not by a label invented during the work (wave B, P23, D4). An id may follow in parentheses, after the explanation.
- **Their memory.** Assume they remember their own last message and nothing after it. Notifications and subagent reports are not their messages.
- **Unknowns.** If you do not know a part, say so and say what would tell you. Do not guess.

## 3. The decision brief

Seven parts, in this order:

1. **Decision.** One sentence the owner can answer.
2. **What it is.** Each thing the decision is about, explained: a PR (repository, what changes, how big), an ADR (the rule it sets, in plain words), a tool or library (what it does and why it matters here), a term from the work. No bare ids.
3. **Why now.** What it blocks, or what gets worse while it waits.
4. **Options.** Two to four. Each with its cost (time, money, risk, backend and frontend work) and its visible effect (what users, the team or the system notices).
5. **Recommendation.** Which option, and why, in one or two sentences.
6. **If no answer.** The default you will take and when, or, for an irreversible action, that you will wait and what stays blocked meanwhile.
7. **Evidence.** A link or path to the detail. The brief must stand without it.

One brief per decision; several decisions get numbered briefs, the most blocking first. Never bundle ("answer these two"). Keep each brief short enough to read in a minute; the explanation of what it is gets the most room.

## 4. Catch-up

**Gather (read-only).** Collect your own work since the owner's last message, subagent reports, and messages from anyone else in the chat. After a compaction, read the saved state first (the orchestration HANDOFF, the auto-state snapshot, the conversation summary). Check the live state of every PR, CI run and agent the work touched; note which are still running and which you could not check. Include every action item still waiting, even one raised before their last message.

**Write.**

1. One sentence: how many action items wait on the owner, or none. If nothing happened and nothing waits, say so and stop.
2. What happened, most important first: each result and what it means for the owner. Skip steps that changed nothing.
3. Still running, and what you could not check.
4. Decisions you took yourself, one line each with the reason.
5. Work left that you can do yourself, in one line.
6. One decision brief per action item.

## 5. Check before sending

- [ ] The count in the first sentence matches the number of briefs.
- [ ] Every brief has all seven parts; options carry cost and visible effect.
- [ ] Every id, acronym, tool and library is explained where it first appears.
- [ ] The default and its timing are stated.
- [ ] Nothing in the briefs is a call you could have made yourself.
- [ ] Language and writing rules match the owner's.

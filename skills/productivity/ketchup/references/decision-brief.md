# Decision brief — field rules and forms

Read when writing a brief into a file, into AskUserQuestion, or when a part is hard to fill.

## Field rules

| Part | Must contain | Fails when |
|---|---|---|
| Decision | one answerable sentence | it is a topic ("Contract test") or two questions |
| What it is | each PR, ADR, tool, library, term: what it is and does, in plain words | an id or name appears without explanation; it repeats the decision |
| Why now | what it blocks, or what gets worse while waiting | "for completeness", or empty |
| Options | 2–4 options, each with cost and visible effect | an option has no cost, or the effect is only "better" |
| Recommendation | one option and the reason | "either works" without a pick |
| If no answer | the default and when it applies, or "I wait; X stays blocked" | silent, or a default with no time |
| Evidence | link or path to detail | the brief cannot be decided without opening it |

Cost is concrete: hours or days of work, money per month, which side (backend, frontend, ops) does the work, the risk taken. Visible effect is what someone notices: what a learner sees, what an admin can do, what breaks for a client, how the bill changes.

An id is an explanation's suffix, never its replacement: "the rule that retries failed sends in the dispatcher, not at enqueue (ADR-0017)".

## Chat form

Write the parts as short paragraphs or labelled lines in the owner's language. Number the briefs when there are several. Put the count sentence first.

## AskUserQuestion

The tool's fields are too short for a brief. Write the briefs in the message text first, then call the tool:

- question: the brief's decision sentence;
- options: the brief's options, recommended first, each label naming the option and its main cost;
- one question per decision; several decisions may share one call only when each has its own brief above.

## File form (HANDOFF, handoff documents)

Keys stay in English so a linter can read them; values are in the owner's language. One `###` per decision under one `## Waiting on owner` section. Write `None.` when nothing waits.

```markdown
## Waiting on owner

### 1. <decision in one sentence>
- What it is: <each PR, ADR, tool or term explained; ids only after the explanation>
- Why now: <what it blocks or what gets worse>
- Options:
  - A. <option>. Cost: <work, money, risk>. Effect: <what someone notices>.
  - B. <option>. Cost: <...>. Effect: <...>.
- Recommendation: <option and why>
- If no answer: <default and when, or what stays blocked>
- Evidence: <link or path>
```

Rules a linter can check on this form: every key present and filled; no `<placeholder>` left; at least two options, each with `Cost:` and `Effect:`; every id used anywhere in the brief (`ADR-0017`, `PR #12`, `MR !34`, `#123`, a ticket key like `ABC-42`) also appears in `What it is`. The orchestrate skill's `orchestration_lint.py --phase handoff` checks these. Whether the explanation is good is still a human or judge call.

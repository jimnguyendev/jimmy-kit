---
name: handoff
description: Compact the current conversation into a handoff document for another agent to pick up. Use when a session is ending, context is nearly full, or the work is being passed to another agent or teammate.
argument-hint: "What will the next session be used for?"
---

# Handoff

Write a handoff document summarising the current conversation so a fresh agent can continue the work. Save to the temporary directory of the user's OS - not the current workspace.

Include a "suggested skills" section in the document, which suggests skills that the agent should invoke.

Do not duplicate content already captured in other artifacts (PRDs, plans, ADRs, issues, commits, diffs). Reference them by path or URL instead.

Include a "Waiting on owner" section. Write each decision still waiting on the user as a decision brief (skill `ketchup`): the decision in one sentence; what it is, with every PR, ADR, tool or term explained (no bare ids); why now; options with cost and visible effect; recommendation and why; what happens with no answer; evidence. Write `None.` when nothing waits. List decisions the session already took as decided, with the reason, not as questions. The next session relays these briefs as written; it cannot explain what it did not write.

Redact any sensitive information, such as API keys, passwords, or personally identifiable information.

If the user passed arguments, treat them as a description of what the next session will focus on and tailor the doc accordingly.

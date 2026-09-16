---
name: grilling
description: Stress-test a plan or decision through an interview. Use when the user asks to be grilled or wants unresolved assumptions and choices challenged.
---

# Grilling

> **This skill exists to stop:** an interview from repeating discoverable facts or ending with decisions still hidden in the conversation.

## 🤖 0. HOW TO USE

Interview mode produces a decision summary with accepted choices, assumptions,
and open blocking questions. Documentation capture is available through
`grill-with-docs`; `grill-me` is a compatibility name for this interview.

Inspect the supplied plan and relevant environment first. Look up factual answers
instead of asking the user to repeat them. Identify the unresolved decisions and
their dependencies; start with the one that changes the most downstream choices.

Ask one decision question at a time, giving a recommendation and its trade-off.
Wait for that answer before taking the dependent branch. Reuse accepted decisions;
do not re-ask them solely because a different skill or phase begins.

Finish when no blocking branch remains, or the user asks to stop: summarize the
choices, evidence, assumptions, and deferred questions, and request confirmation
only for decisions not yet accepted. An interview alone does not authorize
implementation. If implementation was also requested and its decisions are
settled, hand off the accepted scope without another interview.

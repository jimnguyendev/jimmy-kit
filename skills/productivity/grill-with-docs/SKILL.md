---
name: grill-with-docs
description: Use when explicitly asked to interview about a plan and capture its resolved terminology and consequential decisions in durable records.
disable-model-invocation: true
---

# Grill With Docs

Use `grilling` for the interview and `domain-modeling` for qualifying records when
installed. These are skill names, not required slash commands.

Standalone fallback: inspect discoverable facts, ask one unresolved decision at
a time with a recommendation, and reuse settled answers. Capture agreed domain
terms in the target's glossary (`CONTEXT.md` by default). Write a numbered ADR
under `.jimmy/adr/` only for a consequential choice whose rationale or rejected
alternatives would help a future maintainer. Follow existing record conventions;
create files lazily and never turn guesses into accepted decisions.

Finish with the decision summary, open blockers, and links to records actually
updated. Recording the interview does not itself authorize implementation.

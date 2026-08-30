---
name: decision-log
description: Architecture Decision Records (ADRs) and Technical Decision Logging skill. Use when documenting technical decisions, recording architecture choices, logging trade-offs, explaining why a library or design pattern was selected over alternatives, or tracking decision history.
---

# Sage Decisions (Architecture Decision Records - ADRs)

> **This skill exists to stop:** decisions living in someone's head or a chat thread — three months later the team relitigates the same question with the same arguments (Chesterton's Fence).

> 📁 **Source convention:** `[sage]` = upstream Sage repo (github.com/xoai/sage); `[docs]` = your internal docs repo (optional deep-dives — adjust paths to your setup). Sources are for deeper reading: if a file is missing, the skill still runs on the rules inlined here. The ONLY exception: a step marked **MUST READ** — if that file is missing, STOP and ask the user instead of improvising.

## 🤖 0. HOW TO USE (agent workflow)
**A. Write a new ADR — the moment the decision is made, not at sprint end.** Three required parts: what was decided (one sentence) · why (reasoning, not restatement) · losing alternatives WITH the reason they lost. Prepend newest first; rotate to archive at ~200 lines.
**B. Look up before tearing down a fence:** when someone proposes reversing an old decision, read the original entry first and respond with the recorded reasoning instead of relitigating.
**Reference pattern:** a claim-window ADR — decision, reasoning, three rejected alternatives each with its losing reason.
📄 Full original: [sage] skills/sage-decisions/SKILL.md.
---

## 1. Why Keep Decision Logs?

- **Prevent Relitigation:** "We chose Postgres" is a fact in the lockfile. "We chose Postgres over DynamoDB because access patterns are relational and a join layer would eliminate cost savings" is an ADR. It stops someone reopening the debate next quarter without new facts.
- **Explicit Alternatives:** A decision without considered alternatives is not a decision — it's an accident.

---

## 2. Where Decisions Live

| Scope                             | Location                                | Example                                           |
| :-------------------------------- | :-------------------------------------- | :------------------------------------------------ |
| **Initiative / Feature Specific** | `.jimmy/work/<feature>/decisions.md`    | "Use TanStack Table for Virtualized Student Rows" |
| **Project-Wide / Global**         | `.jimmy/decisions.md`                   | "Monorepo Package Strategy with Vite-Plus"        |
| **Engineering ADR (numbered)**    | `.jimmy/adr/NNNN-slug.md`               | Written by `domain-modeling` / `port-service`; format in domain-modeling/ADR-FORMAT.md |

---

## 3. How to Write an ADR Entry

Always **PREPEND** (insert at the top, below `# Architecture Decision Records` header) so newest decisions appear first.

### Standard ADR Template:

```markdown
### ADR-[NNN]: [Clear, Action-Oriented Title]

**Date:** YYYY-MM-DD | **Author / Lead:** [Name/Role] | **Status:** Accepted | Deprecated | Superseded

#### 1. Context & Problem

[What problem or constraint triggered this decision?]

#### 2. Decision

[What is the chosen approach or technology?]

#### 3. Alternatives Considered & Why Rejected

- **Option A (Rejected):** [Reason it lost — e.g. too complex, missing SSR support]
- **Option B (Rejected):** [Reason it lost — e.g. high bundle size, vendor lock-in]

#### 4. Consequences & Trade-Offs

- **Positive:** [What benefits do we gain?]
- **Negative / Costs:** [What complexity, technical debt, or operational overhead do we accept?]
```

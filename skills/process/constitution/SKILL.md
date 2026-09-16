---
name: constitution
description: Apply engineering principles. Use when a project convention is unclear or a proposed change conflicts with its documented rules.
version: "1.0.0"
type: system
---

# The constitution

> 📁 **Source note:** `[sage]` = upstream Sage repo (github.com/xoai/sage, public) — optional deeper reading; this skill runs fully on the rules inlined here. A step marked **MUST READ** points at a file in *your own* project (e.g. an event registry) — if it is missing, stop and ask instead of improvising.

These are the kit's engineering defaults. Read the target project's applicable
AGENTS.md and `.jimmy/constitution.md` if present. The project controls its own
workflow and enforcement; a missing optional constitution is not a blocker.

## Engineering principles

The base set to apply to relevant changes:

| # | Principle | Verification mechanism to use when available |
|---|---|---|
| 1 | **Test changed behavior** — prefer tests before code for new behavior and regression fixes | Relevant automated tests; editorial changes use inspection/lint |
| 2 | **No silent failures** — errors handled, logged, or propagated | Tests and review of failure paths |
| 3 | **Secrets never in code** — env vars or a secret manager | Secret scan and review |
| 4 | **Dependencies explicit** — declared, pinned by the project's policy | Package manifest/lockfile and dependency checks |
| 5 | **Changes reversible** — migrations and deployments have a recovery path appropriate to risk | Migration/deployment checks and rollback review |

Principles 6+ come from the project's preset and its own
`.jimmy/constitution.md`. They are appended by the project, numbered
continuously, and they carry exactly the same weight as the base five. A
project addition is not a suggestion.

## The distinction that matters

The kit ships guidance, not runtime enforcement. Installing a skill does not
install a hook or CI check. Confirm which mechanisms the target actually has;
report absent checks as absent, and unrun verification as unverifiable.
Some principles need judgment even when checks exist. A passing script does not
prove every error path is handled or every migration is recoverable.

If a principle matters and has no mechanism, that is a gap in the mechanism —
not a reason to write the prose more forcefully.

## Process rules with no script behind them

These are enforced by the model reading them, which is a real but weaker thing.

**Rule 2 — Relevant skills.** Use a skill when its specific guidance changes the
work. Tier 1 may need none; Tier 2 normally uses one or two. Follow the current
problem state rather than a keyword chain, and stop when the decision is resolved.

**Rule 3 — Durable decisions.** Record consequential decisions and their reasons
where the next maintainer will find them. Reuse existing artifacts; a short Tier 2
record can be the change description. When separate kit artifacts help, use
`.jimmy/work/`, `.jimmy/docs/`, or `.jimmy/adr/`.

**Authority.** Accepted scope and authorization carry through skill handoffs.
Ask only for unresolved material decisions or actions beyond that authorization.
Continue authorized work through its relevant verification; do not add a new
approval checkpoint just because another skill loaded.

## Rationalizations

| The thought | Why it fails |
|---|---|
| "This principle does not apply to test code" | Test code is code. It is also the code you will trust the most and read the least. |
| "The project preset does not mention it, so it is optional" | The base five apply everywhere. Presets add; they do not subtract. |
| "I will follow the principle, just not right now" | The commit is the artifact. "Later" does not appear in it. |
| "It is a prototype" | Prototypes ship. That is what makes them prototypes rather than sketches. |


---

## Applied context (edtech)
> Principle + mechanism examples: "never lose the submission" is enforced by save-before-grade, not by a reminder; a required form field beats "please remember to fill in the source." 

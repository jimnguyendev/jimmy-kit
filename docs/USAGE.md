# Using Jimmy Kit

How to install the kit into a project or machine, start a session with it, and keep it updated. Works with Claude Code, Codex CLI and Cursor — all three read the same `SKILL.md` format; only the folder they look in differs.

## 1. Install

### Option A — global, one machine (fastest)
```bash
git clone https://github.com/jimnguyendev/jimmy-kit.git ~/jimmy-kit
~/jimmy-kit/scripts/link-skills.sh                     # Claude Code  → ~/.claude/skills
~/jimmy-kit/scripts/link-skills.sh ~/.agents/skills    # Codex CLI    → ~/.agents/skills
~/jimmy-kit/scripts/link-skills.sh ~/.cursor/skills    # Cursor       → ~/.cursor/skills
```
Update later with `git -C ~/jimmy-kit pull` — the symlinks follow automatically.

### Option B — per repo, shared with the team
```bash
# inside the target repo
git submodule add https://github.com/jimnguyendev/jimmy-kit.git vendor/jimmy-kit
vendor/jimmy-kit/scripts/link-skills.sh .claude/skills   # Claude Code
vendor/jimmy-kit/scripts/link-skills.sh .agents/skills   # Codex
vendor/jimmy-kit/scripts/link-skills.sh .cursor/skills   # Cursor
```
Commit the submodule and the symlinks. Pin a version with `git -C vendor/jimmy-kit checkout v0.1.0`. On Windows, use `cp -r vendor/jimmy-kit/skills/*/* .claude/skills/` instead of symlinks.

Only need a subset? Copy the folders you want: `cp -r vendor/jimmy-kit/skills/product/* .claude/skills/`.

| Tool | Per-project folder | Global folder |
|---|---|---|
| Claude Code | `.claude/skills/<name>/` | `~/.claude/skills/<name>/` |
| Codex CLI | `.agents/skills/<name>/` | `~/.agents/skills/<name>/` |
| Cursor | `.cursor/skills/<name>/` | `~/.cursor/skills/<name>/` |

`scripts/list-skills.sh` prints every skill with its one-line description.

## 2. Where the kit writes
Everything a skill produces goes under **`.jimmy/`** in the repo you are working in — never into your `docs/`:

| Path | Contents |
|---|---|
| `.jimmy/work/<feature>/` | in-progress artifacts: brief, spec, plan, screenshots, `decisions.md` for that feature |
| `.jimmy/docs/` | durable outputs: research briefs, audits, voice & tone, runbooks |
| `.jimmy/decisions.md` | project-wide ADR log (owned by `decision-log`) |
| `.jimmy/adr/NNNN-slug.md` | numbered engineering ADRs (`domain-modeling`, `port-service`) |
| `.jimmy/constitution.md` | project principles (`constitution`) |

Add `.jimmy/` to `.gitignore` if you don't want it tracked; most teams track `decisions.md`, `adr/` and `constitution.md` and ignore `work/`.

## 3. Start a session
1. **Don't pick a skill — describe the problem.** The `routing` skill is the dispatcher: "conversion is low", "audit this landing page", "retention is dropping", "review this PRD". It maps the request to one of the ten problem chains in `docs/OPERATING-WORKFLOW.md`.
2. Every chain runs **UNDERSTAND → ENVISION → DELIVER → REFLECT**, with the 7-question intake first and a mandatory `product-council` red-team before anything is built or pitched.
3. Skills refuse to run on guesses: expect to be asked for a sourced, dated number or a baseline. Answer with the number, or say "no baseline" — the skill then writes `[baseline TBD — measure first]` instead of inventing one.

Typical invocations (any tool; skills trigger on the situation, you can also name them):
- "Review these OKRs: …" → `okr-outcome-architect`
- "Red-team this idea: …" → `product-council`
- "Audit the pricing page" → `ux-cro-audit` · "Review this UI's usability" → `ux-review`
- "Which transition leaks retention?" → `growth-markov-duolingo` → `engagement-matrix-analytics` → `advanced-rfm-segmentation`
- "Independent review of this spec" → `independent-review` (runs in a fresh agent, read-only)
- "Which skill should I use?" → `routing`

## 4. Conventions you will see inside skills
- `> This skill exists to stop: …` — the mistake the skill prevents; if it doesn't apply to you, you are in the wrong skill.
- `## 🤖 0. HOW TO USE` — modes (audit / write / plan …) and the exact output format.
- Claim labels `[VERIFIED]` · `[ASSUMPTION]` · `[GUESS]`; exit codes 0 / 1 / 2 (pass / fail / unverifiable).
- `[sage]` / `[docs]` tokens mark optional deep-dives in external repos; every skill runs without them.
- Shared vocabulary: `CONTEXT.md`.

## 5. Keep it healthy
- Upgrading: `git pull` (Option A) or bump the submodule (Option B). Read `docs/DECISIONS.md` first if a skill moved or was renamed.
- Adding or changing a skill: write `SCENARIO.md` before the skill, run it with a fresh agent, paste the result (see `skills/product/product-council/SCENARIO.md` for the shape).
- Before publishing a change, run the review checklist in `AGENTS.md`.

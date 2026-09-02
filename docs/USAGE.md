# Using Jimmy Kit

How to install the kit into a project or machine, start a session with it, and keep it updated. Works with Claude Code, Codex CLI and Cursor — all three read the same `SKILL.md` format; only the folder they look in differs.

## 1. Install

### Fastest — one command, any agent (Claude Code, Codex, Cursor, Gemini, …)
```bash
npx skills add jimnguyendev/jimmy-kit            # interactive: pick agents + skills
npx skills add jimnguyendev/jimmy-kit -y -g      # everything, globally, no prompts
npx skills add jimnguyendev/jimmy-kit --skill product-council --skill okr-outcome-architect
```
Uses the open-source `skills` CLI (skills.sh). It clones the repo, finds all 48 `SKILL.md`, and writes them into the right folder for each agent you select (`.claude/skills`, `.agents/skills`, `.cursor/skills`, …). Re-run to update. No clone or symlink to manage.

### Claude Code plugin (namespaced skills, updates via `/plugin`)
```text
/plugin marketplace add jimnguyendev/jimmy-kit
/plugin install jimmy-kit@jimmy-kit
```
Skills then appear as `jimmy-kit:<skill>` (e.g. `/jimmy-kit:product-council`). Manifests live in `.claude-plugin/`; the marketplace pins the `v0.1.0` tag. To test a local checkout before publishing: `claude --plugin-dir /path/to/jimmy-kit`.

### Option A — global clone + symlinks (when you want `git pull` updates)
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

| Tool | Per-project folder | Global folder | Instructions file it reads |
|---|---|---|---|
| Claude Code | `.claude/skills/<name>/` | `~/.claude/skills/<name>/` | `CLAUDE.md` (→ `AGENTS.md`) |
| Codex CLI | `.agents/skills/<name>/` | `~/.agents/skills/<name>/` | `AGENTS.md` |
| OpenCode | `.opencode/skill/<name>/` (also picks up `.claude/skills/`) | `~/.config/opencode/skill/<name>/` | `AGENTS.md` |
| Cursor | `.cursor/skills/<name>/` | `~/.cursor/skills/<name>/` | `.cursor/rules`, `AGENTS.md` |

`npx skills add jimnguyendev/jimmy-kit -a codex,opencode,claude-code,cursor` writes to all of these at once (`-a '*'` = every agent it knows — 70+, incl. gemini-cli, windsurf, github-copilot, zed). Codex users can also install from inside Codex with its built-in `$skill-installer` skill by pasting the repo URL.

`scripts/list-skills.sh` prints every skill with its one-line description.

## 2. Where the kit writes
Everything a skill produces goes under **`.jimmy/`** in the repo you are working in — never into your `docs/`:

| Path | Contents |
|---|---|
| `.jimmy/work/<feature>/` | in-progress artifacts: brief, spec, plan, screenshots, `decisions.md` for that feature |
| `.jimmy/docs/` | durable outputs: research briefs, audits, voice & tone, runbooks |
| `.jimmy/decisions.md` | project-wide ADR log (owned by `decision-log`) |
| `.jimmy/adr/NNNN-slug.md` | numbered engineering ADRs (`domain-modeling`) |
| `.jimmy/constitution.md` | project principles (`constitution`) |

Add `.jimmy/` to `.gitignore` if you don't want it tracked; most teams track `decisions.md`, `adr/` and `constitution.md` and ignore `work/`.

## 3. Make routing always-on (recommended)
Installing skills gives the agent 48 tools it *can* pick up; it does not force routing through them. To get Sage-style "route every request" behavior, append the eager dispatcher block to your repo's instructions file once:
```bash
cat vendor/jimmy-kit/templates/eager-dispatcher.md >> AGENTS.md   # or ~/jimmy-kit/…
```
(Claude Code reads it via a `CLAUDE.md` containing "Read AGENTS.md"; Codex and OpenCode read `AGENTS.md` directly; Cursor: paste it into a `.cursor/rules` file.) Without this block, routing is on-demand: the agent matches skill descriptions, and the `product-council` gate is a convention rather than an instruction.

## 4. Start a session
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

## 5. Conventions you will see inside skills
- `> This skill exists to stop: …` — the mistake the skill prevents; if it doesn't apply to you, you are in the wrong skill.
- `## 🤖 0. HOW TO USE` — modes (audit / write / plan …) and the exact output format.
- Claim labels `[VERIFIED]` · `[ASSUMPTION]` · `[GUESS]`; exit codes 0 / 1 / 2 (pass / fail / unverifiable).
- `[sage]` marks optional deeper reading in the public upstream repo; skills carry no internal-doc links and run fully on their own.
- Shared vocabulary: `CONTEXT.md`.

## 6. Keep it healthy
- Upgrading: `git pull` (Option A) or bump the submodule (Option B). Read `docs/DECISIONS.md` first if a skill moved or was renamed.
- Adding or changing a skill: write `SCENARIO.md` before the skill, run it with a fresh agent, paste the result (see `skills/product/product-council/SCENARIO.md` for the shape).
- Before publishing a change, run the review checklist in `AGENTS.md`.

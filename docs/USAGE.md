# Using Jimmy Kit

How to install the kit into a project or machine, start a session with it, and keep it updated. Works with Claude Code, Codex CLI and Cursor — all three read the same `SKILL.md` format; only the folder they look in differs.

## 1. Install

### Fastest — one command, any agent (Claude Code, Codex, Cursor, Gemini, …)
```bash
npx skills add jimnguyendev/jimmy-kit            # interactive: pick agents + skills
npx skills add jimnguyendev/jimmy-kit -y -g      # everything, globally, no prompts
npx skills add jimnguyendev/jimmy-kit --skill product-council --skill okr-outcome-architect
python3 scripts/kit.py npx --group core,golang,database --agent codex   # from a clone: print the command for whole groups
```
Uses the open-source `skills` CLI (skills.sh). It clones the repo, finds all 94 `SKILL.md`, and writes them into the right folder for each agent you select (`.claude/skills`, `.agents/skills`, `.cursor/skills`, …). Re-run to update. No clone or symlink to manage.

### Claude Code plugin (namespaced skills, updates via `/plugin`)
```text
/plugin marketplace add jimnguyendev/jimmy-kit
/plugin install jimmy-kit@jimmy-kit        # everything
/plugin install golang@jimmy-kit           # or one group at a time: core, engineer, golang, database, product, ux, analytics, utilities
```
Skills then appear namespaced by plugin (e.g. `/jimmy-kit:product-council`, `/golang:backend-go-testing`). Install either `jimmy-kit` or groups, not both, or each skill loads twice. Manifests live in `.claude-plugin/` and are generated from `groups.json` by `python3 scripts/kit.py plugins --write`; plugin sources are relative, so they follow the marketplace's default branch. To test a local checkout before publishing: `claude --plugin-dir /path/to/jimmy-kit`.

### Option A — global clone + symlinks (when you want `git pull` updates)
```bash
git clone https://github.com/jimnguyendev/jimmy-kit.git ~/jimmy-kit
~/jimmy-kit/scripts/link-skills.sh                     # Claude Code  → ~/.claude/skills
~/jimmy-kit/scripts/link-skills.sh ~/.agents/skills    # Codex CLI    → ~/.agents/skills
~/jimmy-kit/scripts/link-skills.sh ~/.cursor/skills    # Cursor       → ~/.cursor/skills
~/jimmy-kit/scripts/link-skills.sh ~/.claude/skills --group core,golang,database   # only some groups
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
Installing skills gives the agent 94 tools it *can* pick up; it does not force routing through them. To get always-on problem-state and dosage routing, append the eager dispatcher block to your repo's instructions file once:
```bash
cat vendor/jimmy-kit/templates/eager-dispatcher.md >> AGENTS.md   # or ~/jimmy-kit/…
```
(Claude Code reads it via a `CLAUDE.md` containing "Read AGENTS.md"; Codex and OpenCode read `AGENTS.md` directly; Cursor: paste it into a `.cursor/rules` file.) Without this block, routing and dosage are on-demand: the agent matches skill descriptions rather than applying the shared Tier 1/2/3 policy automatically.

## 4. Start a session
1. **Don't pick a skill — describe the problem.** The `routing` skill is the dispatcher: "conversion is low", "audit this landing page", "retention is dropping", "review this PRD". It maps the request to a problem-shape chain in `docs/OPERATING-WORKFLOW.md`.
2. The four phases are a maximal map, not a pipeline. Tier 1 may use no skill, Tier 2 normally uses one or two, and Tier 3 uses the full intake plus `product-council`. By default, Tier 1 and already-approved Tier 2 bypass council. Explicit red-team/pitch requests and consequential product/platform decisions are exceptions: they invoke council directly but do not expand the rest of the workflow unless the work is Tier 3. Stop when the current skill settles the decision.
3. Skills distinguish evidence from assumptions. Missing baselines are reported as `[baseline TBD — measure first]`; they block conclusions that require measurement, while useful drafts and investigation may proceed. Accepted scope and authorization carry through handoffs.

Typical invocations (any tool; skills trigger on the situation, you can also name them):
- "Review these OKRs: …" → `okr-outcome-architect`
- "Red-team this idea: …" → `product-council`
- "Audit the pricing page" → `ux-cro-audit` · "Review this UI's usability" → `ux-review`
- "Which transition leaks retention?" → `growth-markov-duolingo` → `engagement-matrix-analytics` → `advanced-rfm-segmentation`
- "Independent review of this spec" → `independent-review` (runs in a fresh agent, read-only)
- "Which skill should I use?" → `routing`

## 5. Prove changes on the running app (`verify-app`)

`verify-app` (group `engineer`) builds a verify skill inside your repo. After that, any agent can start the real service, drive it, read back the database, cache and logs, keep the evidence and clean up, without asking you to run anything. The walkthrough below comes from the run recorded in `skills/engineering/verify-app/SCENARIO.md` on a Go HTTP service (Gin, PostgreSQL, Redis, one CRUD feature).

### Create it once per repo

Install `core` and `engineer` (plus `golang` and `database` for a Go service), append the eager dispatcher to the repo's `AGENTS.md` (section 3), then ask in plain words:

```text
Every time an agent changes this service, I have to start it myself, call the endpoints,
check the database and paste the output back. I want agents to be able to prove a change
actually works on the running service by themselves. Set that up and run it once.
```

The agent reads the repo first (run commands, pinned image versions, migrations, env), asks only for what the code cannot answer (sandbox credentials, test accounts), and produces:

| Path | What it is |
|---|---|
| `<skills dir>/verify-<app>/SKILL.md` | Launch, Doctor, Drive, Evidence, Cleanup, Helpers for this repo |
| `<skills dir>/verify-<app>/scripts/verify.sh` | one script with `up`, `doctor`, `call`, `last`, `sql`, `redis`, `logs`, `down` |
| `<skills dir>/verify-<app>/features/` | one recipe per user-visible feature; `README.md` indexes them |
| `<skills dir>/verify-<app>/scripts/check_feature_map.py` | validates the recipes |
| `.jimmy/work/verify-<app>/evidence/<run-id>/` | numbered evidence files from each run (or the repo's mapped work folder) |

`<skills dir>` is the folder the repo's agents already load (`.agents/skills/`, `.claude/skills/`, …). In the recorded run it also added a symlink so Claude Code loads the skill, one routing row in `AGENTS.md`, and finished a full launch → doctor → drive → cleanup pass with 48 evidence files left in place.

### Daily loop for an agent (or you)

```bash
V=<skills dir>/verify-<app>/scripts/verify.sh
RUN_ID=$(date +%Y%m%d-%H%M%S)

$V up $RUN_ID            # build the working tree, start per-run DB/cache containers, migrate, wait for /health
$V doctor $RUN_ID        # read-only; compares versions, migration head, build hash, port owner. FAIL = do not drive
$V call $RUN_ID create POST /api/v1/examples '{"name":"first"}'
ID=$($V last $RUN_ID .data.id)
$V sql   $RUN_ID row-after-create "select id, name from examples where id = '$ID'"
$V redis $RUN_ID cache-after-get EXISTS "verify-${RUN_ID}:example:$ID"
$V logs  $RUN_ID event-created "example created.*id=$ID"   # bounded poll, never a sleep
$V down $RUN_ID          # stops only this run's process and containers; evidence stays
```

Follow the feature file your change touches instead of improvising: each step names the command and the observable result, and each sub-feature is either driven or marked `Skipped: \`id\` — reason`. Report the evidence path, not a summary.

### What the run caught

- Three real service defects, reported and left for a separate change: a non-UUID path ID returned 500, a documented `per_page` parameter was ignored, timestamps came back in the host zone instead of the configured one.
- A defect in its own recipes: in zsh, `verify-$RUN_ID:example` expands `$RUN_ID:e` as a modifier. Recipes now write `${RUN_ID}`. Keep that form when you add steps.

### Keep it honest

- Doctor fails on `build` after you edit code: the binary is stale. Run `down`, then `up` with a new run ID.
- When a feature is added or its routes change, update `features/` in the same change and drive the new steps once; run `check_feature_map.py`.
- Every few weeks, or when recipes start failing for reasons outside your change, ask the agent to "audit the verify skill" (Maintain mode): it re-reads source per feature, drives every feature live, and ships one change set limited to the verify skill.

### Services with store webhooks or async pipelines

For a service that receives signed provider notifications and publishes through an outbox (for example a subscription service), Create mode also writes recipes from `skills/engineering/verify-app/references/service-recipes.md`: genuine sandbox events versus replayed captured payloads, a fresh push token through the run's own subscription, recorded provider API responses, ordered checks from row to outbox to message to read model, an injected clock for expiry and grace, and duplicate, out-of-order, crash-after-publish and reconciliation cases. Have sandbox credentials and a few captured notifications ready before asking; Doctor reports "incomplete coverage" without them.

## 6. Conventions you will see inside skills
- `> This skill exists to stop: …` — the mistake the skill prevents; if it doesn't apply to you, you are in the wrong skill.
- `## 🤖 0. HOW TO USE` — modes (audit / write / plan …) and the exact output format.
- Claim labels `[VERIFIED]` · `[ASSUMPTION]` · `[GUESS]`; exit codes 0 / 1 / 2 (pass / fail / unverifiable).
- `[sage]` marks optional deeper reading in the public upstream repo; skills carry no internal-doc links and run fully on their own.
- Shared vocabulary: `CONTEXT.md`.

## 7. Keep it healthy
- Upgrading: `git pull` (Option A) or bump the submodule (Option B). Read `docs/DECISIONS.md` first if a skill moved or was renamed.
- Adding or changing a skill: write `SCENARIO.md` before the skill, run it with a fresh agent, paste the result (see `skills/product/product-council/SCENARIO.md` for the shape).
- Before publishing a change, run the review checklist in `AGENTS.md`.

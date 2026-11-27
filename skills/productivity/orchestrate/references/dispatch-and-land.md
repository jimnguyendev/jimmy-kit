# Dispatch and land

Read before the first dispatch of a sprint and before every land. The rules come from one
origin run (a notification service with a React admin, about 40 packets over two days, one
machine, three executor routes); each cites the failure that earned it.

## Worktrees: the root creates them

For every packet the root runs, in the **target** repo:

```bash
git -C <repo> worktree add <repo>-wt/<NNN>-<slug> -b p<NNN>-<slug> <main>
```

and puts the absolute worktree path and the absolute packet path in the dispatch prompt:
`Work only in <worktree>. Read and execute the packet at <packet>.` Do not rely on the Agent
tool's `isolation: worktree`: it isolates the repository of the session's cwd, which is not
always the target (origin: the session ran from another repo; executors would have edited it).

A worktree is removed by `land.sh` after a confirmed merge, never by a cleanup chained with `;`
(origin: a `;`-chained cleanup removed the worktree of a branch whose merge had been refused).

## Wave integration branch

Wave mode (SKILL.md "Wave mode (default)") lands a set of packets at once. In the **target** repo:

```bash
git -C <repo> worktree add <repo>-wt/wave-<name> -b feat/<name> <main>
git -C <repo> worktree add <repo>-wt/<NNN>-<slug> -b p<NNN>-<slug> feat/<name>
```

The executor works in its packet worktree and runs the code-only checks of its packet. When the
root accepts the diff, it merges the packet branch into `feat/<name>` inside the wave worktree with
`git merge --no-ff p<NNN>-<slug>`: one merge commit per packet, so `git log --first-parent` names the
merge that broke a gate and the delta goes to that packet's resumed executor. Packets are merged in
the order the plan records; rerun the cheap code checks after a merge that touches a file another
packet changed.

The root then runs the full gates, container tests, the full frontend suite, migrations up and down,
`EXPLAIN` and the preflight in the wave worktree, once. `scripts/land.sh <wave worktree> "<title>"`
needs no change for this: it accepts any worktree on a branch other than the default branch, merges
the default branch in, runs every gate and merges the one PR/MR. The packet worktrees are removed by
hand after that land (`land.sh` removes only the one it was given).

Land a packet on its own, first, only in the four cases of Wave mode. While the machine is idle the
root may run one cheap container test on `feat/<name>` early; the full suites wait for the end of the wave.

## Model routing

A default for packets whose seat the user has not pinned. Explicit seat labels still win.

| Packet kind | Route | Conditions |
|---|---|---|
| Easy backend: CRUD or a small fix that copies a feature already in the repo | a low-cost model through opencode (GLM in the origin run) | the packet names the reference feature; never frontend |
| Normal backend, and **all** frontend | Sonnet | |
| Hard: auth/SSO, enqueue, dispatcher, lease/retry, rich editors, performance | Opus | the packet asks for a self mutation check of its key tests |
| Root | Opus | |

Origin evidence: the opencode route finished a device-CRUD packet complete on its first run
because the packet named the in-repo reference feature; Sonnet carried 11 packets including
every frontend one; Opus took SSO, enqueue, the dispatcher and the email editor.

### opencode in a worktree

```bash
mkdir -p <worktree>/.orchestrate
cp <repo>/.orchestrate/BRIEF.md <repo>/.orchestrate/packets/<NNN>-<slug>.md <worktree>/.orchestrate/
cd <worktree> && opencode run -m <provider>/<model> \
  "Read and execute the packet at .orchestrate/<NNN>-<slug>.md" \
  < /dev/null > <repo>/.orchestrate/p<NNN>-opencode.log 2>&1 &
```

Launch it detached instead of as a plain `&` job of the agent shell: `nohup setsid opencode run … < /dev/null
> <log> 2>&1 &` (macOS without `setsid`: plain `nohup`). A job owned by the agent shell dies at that shell's
background time limit, which cuts a long packet in half.

- `< /dev/null` is required. `opencode run` reads a non-TTY stdin to EOF and appends it to the
  prompt; a background shell keeps stdin open, so the run waits forever with an empty log
  (origin: 14 minutes lost; `sleep 100 | opencode run … PONG` stays silent, `< /dev/null` answers at once).
- `-m <provider>/<model>` is required. Without it `opencode run` falls back to a default model
  that may need another subscription and fails at once.
- Inputs live inside the worktree. In `run` mode a read outside the cwd is auto-rejected, so a
  packet path in the main checkout cannot be read. `.orchestrate/` must be gitignored so the copies
  never reach a commit. The same rejection hits writes to `/tmp`: give the executor a scratch
  directory inside the worktree.
- Watch the process by pid from a background shell; review the diff even when the run died. An
  interrupted run can leave correct, uncommitted work that the root gates and commits.
- Never run two opencode writers concurrently.
- Grep the log for provider limit messages ("Usage limit reached", HTTP 429) while it runs. On one,
  commit the WIP in the worktree and hand it to another executor ("review `git diff`, keep what is
  right") at once; waiting out a multi-hour reset costs more than the hand-over context.

## Shared-machine rules

Several executors, a verification agent and often the user's own dev stack share one machine.
Each packet derives its resources from its number and the packet lists them:

- service ports `base + NNN` (for example API `18000+NNN`, frontend dev server `5200+NNN`);
  never the ports of the user's dev stack or of the root's verification browser;
- binaries and scratch files under `/tmp/<repo>-NNN/` (or inside the worktree for opencode),
  never shared names;
- **no browser at all for executors** (see [verification.md](verification.md)). Origin: about
  ten executor Chromes overloaded the machine, and one executor attached to the shared Chrome and
  switched its active tab while the root was verifying, so the root read another packet's screen.

## Land: one script, gates included

`scripts/land.sh <worktree> "<title>"` is the only way a packet reaches the default branch:

1. refuses a dirty worktree;
2. fetches and merges `origin/<main>` into the packet branch; a conflict stops here;
3. runs `scripts/gates.sh <worktree>` on the merged result; any failure stops before a push;
4. pushes, opens a PR (GitHub, `gh`) or MR (GitLab API), waits until the forge reports it mergeable;
5. merges with the head SHA (`--match-head-commit` / `sha=`), so a commit pushed after the gates cannot land;
6. fast-forwards the main checkout, then removes the worktree and the local branch.

A gate may limit itself to paths: `name @glob[,glob...]: command`. `land.sh` runs the gates with the
default branch as base, so a limited gate runs only when `git diff --name-only <base>...HEAD` of the merged
result has a path matching one of its globs (`*` stays inside a directory, `**` crosses directories),
and otherwise prints `SKIP <name>: no changed path matches <globs>`. The gate output ends with the gates
that ran and the ones that were skipped. A line without `@` always runs; without a base (`gates.sh` called
by hand) every gate runs, and `ORCH_GATES_ALL=1` forces that in a land. `gates.sh --base <ref> <worktree>`
(or `ORCH_GATES_BASE`) sets the base by hand. Origin: a comment-only diff went through fifteen gates including
container suites.

The gate list lives in `<repo>/.orchestrate/gates`, one `name: command` per line, run from the
worktree root. List **every** gate the repo has, backend and frontend, including the slow
container-backed ones:

```text
build:      go build ./...
test:       make test
lint:       make lint
acceptance: make test-acceptance
fe-install: cd web && pnpm install --frozen-lockfile
fe-check:   cd web && pnpm -s typecheck && pnpm -s lint && pnpm -s test
fe-build:   cd web && pnpm -s build
```

Limited form, for a gate that only a part of the tree can break:

```text
acceptance @internal/**,db/**,go.mod: make test-acceptance
fe-check   @web/**:                   cd web && pnpm -s typecheck && pnpm -s lint && pnpm -s test
```

Why the script runs the gates itself: in the origin run the handoff said the land script
"merges main, builds, runs all gates"; it only pushed and merged. Packets landed on the
executor's own gate report until packet 28, which landed with one suite not re-run after its
last commit. Why build after every merge: two parallel packets changed the same client, git
merged both cleanly, and the result did not compile (one removed a field the other used).

### Landing under load

- WHEN a land starts · CHECK `land.sh` waits by itself until the 1-minute load average is at or
  below `ORCH_MAX_LOAD` (default: CPU count; `0` disables), polls every `ORCH_LOAD_POLL` seconds
  (15), prints one line a minute and exits 3 after `ORCH_LOAD_WAIT` seconds (900) · BECAUSE timing
  and performance tests with short waits failed three different ways under load 50 and each passed
  alone in seconds. Land one wave (or one packet that lands alone) at a time, and do not start executors that run gates while a
  land waits.
- WHEN the forge fails after the gates were green (the create call answered 400 seconds after the
  push once) · CHECK `land.sh` already retried the create call `ORCH_CREATE_TRIES` times (5), 5 s
  apart, reusing an MR/PR that appeared meanwhile, and printed the forge's response. Fix the cause,
  then rerun `land.sh --resume <worktree> "<title>"` (or `ORCH_SKIP_GATES_FOR_SHA=<sha>`): it skips
  the gates only when the merged HEAD equals the commit recorded in
  `${TMPDIR:-/tmp}/gates-<worktree name>/green-sha` by the run whose gates passed. A new commit, a
  moved default branch that changes HEAD, or no record runs every gate again; the merge still
  passes the head SHA. · BECAUSE a rerun repeated 15 minutes of gates that had already passed.
- WHEN a gate fails · CHECK rerun that single test alone 3 times before touching code; consistent
  passes mean load, so wait and rerun the gate · BECAUSE a fake red gate costs a land (about 25 min).
- WHEN a wall-clock budget sits in the parallel suite · CHECK it asserts server-side time or a
  query plan, not the client round trip.
- WHEN root builds or runs a worktree locally · CHECK never copy a `.env` into it; start the binary
  with an explicit env-file flag pointing outside the tree · BECAUSE config tests read `.env` and
  failed the land of a packet that was otherwise green.

Do not pipe `land.sh` into `tail` or `grep` before `&&`; the pipe hides its exit code.
Environment knobs (`ORCH_MAIN`, `ORCH_FORGE`, `GITLAB_TOKEN`, `GITLAB_PROJECT`, …) are listed
in the script header.

## Session limits

When a provider session or usage limit stops every running agent, worktrees keep their
uncommitted changes. After the reset, resume each stopped Claude agent with `SendMessage` to its
agent ID (its context is intact, and this works across Claude Code sessions) instead of
spawning a fresh agent that must rediscover the work. Restart an opencode run from the dirty
worktree. Record the agent IDs in HANDOFF.md so a compacted root can still find them.

When the **root's own** model is rate-limited, nothing wakes it. Before an unattended run (overnight,
away from the keyboard), schedule a wake-up or check after the known reset time (`schedule`/`loop`
skill, or a timer), and have it read HANDOFF.md. If the root stalled anyway, say so in the next
status: when it stopped, how long, what was idle. Do not present a stalled night as progress.

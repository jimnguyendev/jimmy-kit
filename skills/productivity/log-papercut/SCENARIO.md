# Scenario — log-papercut (written BEFORE the skill)

**Rationale:** in a long orchestrated build the agents met small breakages in skills and scripts: a script path that no longer existed, a gate that failed only on a busy machine, a step the skill never mentioned. Each agent worked around it and moved on, so the same breakage cost time again in the next session and the skill stayed wrong.

## Case 1 — a wrong path in a skill

**Sample input:** a skill says to run `scripts/check.sh`; the file is at `scripts/verify/check.sh`. The agent finds it and continues.

**Expected behaviors:**
- [ ] Appends one entry to `.jimmy/work/papercuts.md` with date, name, tried, expected, observed, fix.
- [ ] The entry is at most five lines and has no narrative.
- [ ] The task continues; the agent does not stop or ask the owner.
- [ ] The agent does not edit the skill in place.

## Case 2 — a hard task, not a papercut

**Sample input:** the instructions are right and followed, but the task is slow and the test suite is large.

**Expected behaviors:**
- [ ] No entry is written.

## Case 3 — the same breakage again

**Sample input:** the wrong path from case 1 is hit by a second agent.

**Expected behaviors:**
- [ ] No second entry; the headline of the first gets `(again, <date>)`.

Status: exit 2 (no fresh-agent run recorded yet).

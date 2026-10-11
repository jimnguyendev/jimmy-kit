# Scenario — ketchup (written BEFORE the skill)

**Rationale:** in one long orchestrated build (a notification service with a React admin, about 40 packets, subagents, several compactions), the owner said the decisions the agent asked them to make lacked the information needed to make them. Each question below is quoted in English; the owner and agent wrote in Vietnamese.

1. "Give me two answers: open the PR on the skill kit? Accept ADR-0017?" The owner replied "what is this?": neither the PR's contents nor the ADR's trade-offs were explained.
2. Six tech-debt decisions as one-liners ("Contract test: add kin-openapi"), each with a default, but no reason to decide now, no cost per option, nothing about what happens without an answer, and jargon (kin-openapi, ADR numbers) unexplained.
3. "Do you want me to go this way? Or limit per week like the old vendor?" Two options with no cost and no visible effect.

A counter-example from the same run worked: the explanation of the admin's limits card said what the feature does, what happens past the limit, what is wrong in the current UX, the proposal, and the backend and frontend work it needs. The owner decided at once.

The owner's standing rules: reply in their language and follow their writing rules for it (short sentences, English technical terms kept, no slogans); decide, don't ask, on build tasks, and raise only a true owner decision; long autonomous runs with subagents, compaction and resume.

## Case 1 — two decisions bundled in one line

**Sample input:** after fixing the kit's land script on a branch and drafting an ADR about where per-channel send quotas are enforced, the agent must ask the owner for both calls.

**Expected behaviors:**
- [ ] Two separate briefs, never "answer these two".
- [ ] The PR brief says which repo, what the three commits change, and why it is the owner's call (outward-facing, public repo).
- [ ] The ADR brief states the rule the ADR sets in plain words and the trade-off of each option; "ADR-0017" never appears without that explanation.
- [ ] Each brief has: decision sentence, what it is, why now, options with cost and visible effect, recommendation with reason, what happens with no answer (default and when), evidence link.
- [ ] Written in the owner's language with English technical terms kept.

## Case 2 — six tech-debt items

**Sample input:** six follow-ups after a wave (contract test library, rate-limit store, removing a legacy endpoint, send-log retention, a package rename, a Go upgrade).

**Expected behaviors:**
- [ ] Triage first: reversible engineering choices (library, rename, Go upgrade) are decided by the agent and reported in one line each as decisions taken, not asked.
- [ ] Only true owner decisions (removing an endpoint clients call, data retention, new paid infrastructure) get a brief.
- [ ] Every library or term is explained the first time it appears ("kin-openapi, a Go library that checks API responses against the OpenAPI spec").
- [ ] Each brief carries why now and cost per option.

## Case 3 — options without cost

**Sample input:** the admin's frequency cap counts sends per day per channel; the old vendor capped per week. The agent needs a direction.

**Expected behaviors:**
- [ ] Says what the cap does today and what a learner sees when it is hit.
- [ ] Each option (per day, per week, both) carries backend and frontend work, risk, and the visible effect for learners and admins.
- [ ] Recommends one with a reason and names the default and when it applies.

## Case 4 — catch-up after compaction

**Sample input:** `/ketchup` after a compaction; three packets landed, one gate failed, one executor still runs, and a decision raised before the owner's last message is still open.

**Expected behaviors:**
- [ ] Read-only turn; checks the live state of each PR, CI run and agent, and says which it could not check.
- [ ] Opens with one sentence counting the action items.
- [ ] What happened, most important first, with PRs named by what they do, not by labels invented during the work.
- [ ] The decision raised earlier is included as an action item with a full brief.

## Case 5 — nothing happened

**Sample input:** `/ketchup` with no new work and nothing waiting.

**Expected behavior:** one sentence saying so, then stop.

## Case 6 — should NOT ask

**Sample input:** while building, the agent must choose between two assertion libraries for a test helper.

**Expected behavior:** the agent decides, records the choice and reason, and does not raise a brief.

**Status:** [EXIT 2 — specified; no run recorded yet].

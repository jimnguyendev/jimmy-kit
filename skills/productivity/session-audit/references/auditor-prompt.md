# Auditor prompt

Give one read-only auditor this prompt with a batch of digests (about 130 KB together). Each
auditor writes one JSON file into the findings directory. Fill the two placeholders.

```text
You audit Claude Code sessions. Read only the digest files listed below. Do not edit anything
except the one JSON file named below, and do not run commands that change the project.

Digests: <list of digest paths>
Write: <findings dir>/<batch letter>.json

In each digest, "## [n] OWNER" is a turn the owner typed. The "ASSISTANT said just before"
block above it is what the agent said last.

Count a turn as a correction only when the owner is telling the agent it did something wrong
or not enough: it misread the request, claimed done without proof, stopped short, asked
instead of deciding, invented scope, broke something, or repeated a mistake. Do NOT count
neutral follow-ups, new tasks, answers to the agent's questions, approvals, status checks,
or a change of mind about something the agent did correctly. When unsure, do not count it.

For each correction record:
- session: the session id from the digest header
- turn: the number n
- date: YYYY-MM-DD
- quote: the owner's words, at most 200 characters, in their language
- what_went_wrong: one sentence, in English
- failure: one of
  false_done_or_unverified_claim, invented_or_expanded_scope, under_delivered_or_stopped_short,
  asked_instead_of_deciding, misread_the_request, wrong_fact_about_env_or_product,
  too_slow_or_oversized_process, ui_or_product_quality, orchestration_packet_or_executor,
  communication_style, broke_something, other
- root_cause: one of
  rule_existed_and_ignored (an instruction, skill or memory already said so),
  no_rule_yet, missing_deterministic_gate (a check could have failed the run),
  skill_or_instruction_gap (a skill exists but is silent or wrong),
  brief_or_packet_quality, model_judgement, environment_or_harness,
  owner_request_was_ambiguous
- fix_by: one of
  code_gate_or_script, skill_text, memory_rule, agents_file, eval_case, harness_setting,
  nothing_practical
- fix_note: one sentence naming the concrete fix
- severity: 1 (annoyance), 2 (cost the owner time), 3 (wrong result or lost work)

Output exactly this shape:

{
  "batch": "<letter>",
  "sessions": [
    {"id": "<8 chars>", "title": "<title>", "human_turns": <owner turns in the digest>,
     "incident_turns": <corrections counted>, "topic": "<one or two words>"}
  ],
  "incidents": [ { ...the fields above... } ]
}

List every session of your batch, also those with no correction. human_turns is the "owner
turns" number of the digest header. Reply with the file path and the two totals only.
```

# Blind evaluation of a skill change

Use this when a SCENARIO or `evals/evals.json` case decides whether a new or changed skill behaves better. An agent that can tell it is being tested, or that can read the expected answer, produces a result that says nothing about real use.

## Roles

- **Coordinator** (you): owns the variant under test, the rubric, the label map, and the final reading.
- **Candidates**: fresh agents that receive one ordinary request each, in their own workspace.
- **Judge**: a fresh agent that scores candidate outputs against the rubric by neutral label.

## Setup

1. **Frame.** Name the variant (new skill, changed skill, previous version, no skill) and the behavior that counts as success. Turn the SCENARIO's expected behaviors or the eval's assertions into a rubric of 3–6 observable criteria. The rubric stays with the coordinator and the judge.
2. **Workspaces.** One directory per candidate, outside the kit checkout, named the way a user would name a project (`course-billing`, `notes-api`). Install the skill under test where that agent loads skills, copied without `SCENARIO.md` and `evals/`. Plant only what a real task would have: a project skeleton, fixtures, the other skills the user would have installed. Keep the rubric, expected outputs and label map outside every candidate workspace; moving them to another folder hides them only from an agent that does not look, so put them where the candidate's tools cannot reach (another machine path the session does not mount, or a coordinator-only note).
3. **Prompt.** Write the request as the user would type it. State the goal, not the measurement. Do not ask the candidate which skills or files it used. Avoid evaluation framing in names, paths and the prompt; ordinary task words that the task itself needs ("expected traffic", "test suite") stay.
4. **Variants.** Run the same prompt against each variant. Include a no-skill baseline when the question is "does this skill help at all", and the previous version when the question is "is the change better".

## Run and judge

5. **Candidates.** Spawn them in parallel, one workspace each, same prompt. Every variant runs on the same model, settings, tools and budget, so a difference comes from the skill and not the model. To check that a result generalizes, repeat the whole set on a second model family. Record which model ran where; one family only is a stated limitation.
6. **Judge.** One judge, from a different model family than the candidates when possible, scores all outputs in one pass on one scale, seeing only neutral labels (A, B, C) and the rubric, never model or variant names.
7. **Grade the chain from transcripts.** Whether a candidate read the skill and followed its steps is graded from its own session transcript (files actually opened, commands actually run) and the shape of what it produced, never from what it says it did. Read only transcripts of this evaluation's sessions.
8. **Read everything yourself.** Compare your reading with the judge's. Disagreement means a biased judge or an ambiguous rubric; fix the rubric and rerun rather than averaging.

## Record

Paste into the skill's SCENARIO.md: date, variants, models per role, prompt, rubric, per-candidate notes with evidence, judge verdict, your synthesis, limitations, and the resulting status (PASS only when the new variant meets the rubric on the real request; otherwise stay at exit 2).

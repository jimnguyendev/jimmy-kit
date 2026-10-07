---
name: write-a-skill
description: Create or refine reusable agent guidance. Use when writing a skill or correcting a demonstrated skill discovery, workflow, or output failure.
---

# Writing Skills

> **This skill exists to stop:** reusable guidance from accumulating generic instructions, hidden dependencies, and untested claims about agent behavior.

## 🤖 0. HOW TO USE

- **Create:** turn a recurring task or observed failure into a small skill and its necessary resources.
- **Revise:** reproduce the selection or execution problem, then change the guidance responsible for it.
- **Review:** assess relevance, discovery, conditional detail, authority, and evidence without editing unless requested.

Output: the requested skill files plus a short validation report. In Jimmy Kit,
write or update `SCENARIO.md` before editing `SKILL.md`; leave new behavior at
exit 2 until a real application run is recorded. Historical passes retain their
original scope and date.

## 1. Establish the contract

Read applicable repository instructions and the existing skill. Reuse supplied
requirements, examples, and authorization. Ask only when a missing fact changes
the task or permission boundary.

Name the recurring decision this skill improves, when it applies, its output,
and what evidence counts as done. If ordinary agent behavior already handles the
task reliably, a short saved prompt or no skill may be sufficient.

Write a realistic positive case and a nearby case that should not trigger it.
For a behavior correction, capture the original failure before editing. Keep
expected criteria separate from the executing evaluator's inputs.

## 2. Write the smallest useful entrypoint

Use YAML `name` matching the folder and a concise `description` that distinguishes
the task from adjacent skills. Put the capability and actual trigger first;
move output inventories, implementation details, and synonym lists into the body.
Use a block scalar for descriptions containing quotes or YAML punctuation.

In Jimmy Kit, include its required failure statement and HOW TO USE section:

```markdown
---
name: example-skill
description: >-
  Validate a migration rollout. Use when adding or changing a database migration.
---

# Example Skill

> **This skill exists to stop:** a specific observed failure.

## 🤖 0. HOW TO USE

State modes, required inputs, output, completion evidence, and any real boundary.
```

Keep non-obvious invariants and decision criteria in the entrypoint. Put distinct
modes, long schemas, examples, and optional methods into local references; link
each with the condition for reading it. Split by relevance, not a universal line
count. Prefer a runnable helper when a repeated deterministic operation warrants it.

Respect accepted scope and prior authorization. Missing evidence lowers the
confidence of an output; it blocks only the conclusion or action that depends on
it. Preserve genuine user decisions and external-action boundaries.

## 3. Validate and finish

- Parse frontmatter, resolve links, check current skill names and output paths.
- Test the installation shape actually advertised, including selected-skill copies.
  Required resources must be local, explicitly installed dependencies, or have a
  usable fallback. Do not assume a source repository or agent-specific command.
- Run changed helpers on meaningful fixtures and check their real outputs.
- For changed behavior, use a fresh evaluator with the request, skill, and raw
  artifacts only. Compare against the original or a no-skill baseline when useful.
  Record the model, inputs, actual output, result, and limitations. A static lint
  pass is not an agent behavior pass. When the result decides whether a change
  ships or a SCENARIO flips to PASS, run it blind: follow
  [references/blind-eval.md](references/blind-eval.md).
- For description-only edits, check relevant and irrelevant discovery cases;
  do not rerun unrelated workflows or create tests that only echo wording.

Finish when the requested files and relevant validation are complete. Report any
unrun behavior as exit 2. Do not stop at an initial draft when revisions and checks
are already authorized, and do not publish or install globally without authorization.

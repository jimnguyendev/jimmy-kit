---
name: log-papercut
description: >-
  Record friction an agent hits in a skill, script or tool, in five lines, without stopping the
  task. Use when a skill, script or tool behaves differently from its instructions: a wrong
  path, a missing step, a gate that fails for an environmental reason, or an instruction you had
  to guess.
---

# Log a papercut

> **This skill exists to stop:** an agent working around a broken instruction in silence, so the next agent hits the same problem and the skill is never fixed.

## 🤖 0. HOW TO USE

One mode: append one entry to `.jimmy/work/papercuts.md` and keep working. Create the file when it does not exist. The format is fixed.

## Entry

```markdown
## <YYYY-MM-DD> <skill, script or tool name>
- Tried: <the command or step, as written>
- Expected: <what the instructions said would happen>
- Observed: <what happened>
- Fix: <the change you suggest, or "unknown">
```

## Rules

- At most five lines, headline included. No narrative, no blame, no apology.
- Log only when the thing differs from its own instructions. A task that is hard is not a papercut.
- Do not stop the task, ask the owner or fix the skill in place. Work around it, finish, and leave the entry.
- Quote the command or the error message, not your reading of it. Keep secrets, tokens and personal data out.
- If the same entry is already in the file, add `(again, <date>)` to its headline instead of a second entry.

## Reading the file

The owner of a wave reads `.jimmy/work/papercuts.md` at the end of it. An entry seen twice becomes a fix of the skill or script at its source (a branch and a pull request in the repository that owns it), then the entry is deleted. An entry that is not worth fixing is deleted with a one-line reason in the commit or the sprint notes.

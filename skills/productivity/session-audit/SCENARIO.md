# Scenario — session-audit (written BEFORE the skill)

**Rationale:** one owner ran a long orchestrated build with many subagents. After a month the owner said the agent kept making the same mistakes, and the agent answered by adding one more written rule each time. Nothing showed whether a rule worked or which mistakes were worth a check. A manual audit of 26 sessions of that project gave: 414 owner turns, 173 of them corrections (42 percent), 51 that broke a rule that already existed, and 34 that a script could have caught. The four longest sessions held two thirds of the month's spend. This skill packages that audit so it can be repeated and compared.

## Case 1 — first audit of a project

**Sample input:** "Look at the last two weeks and tell me why you keep getting corrected."

**Expected behaviors:**
- [ ] Checks that the output directory is ignored by git before writing a digest.
- [ ] Produces one digest per session and the table of owner turns, tool calls, compactions and spend.
- [ ] Splits sessions into batches of about 130 KB and uses one read-only auditor per batch with the fixed prompt.
- [ ] Aggregates the auditors' files and reports the rate first, then the corrections that broke an existing rule, then the candidates for a script.
- [ ] States that one labelling pass is noisy.
- [ ] Prints no conversation text into a public report.

## Case 2 — a rate after a fix

**Sample input:** "We added the check two weeks ago. Did it help?"

**Expected behaviors:**
- [ ] Runs the same procedure with the same prompt and a period of the same length.
- [ ] Passes the earlier summary to the aggregate and reports the change in the rate and in the counts per failure type.
- [ ] Says the comparison is weak when either period has fewer than about 100 owner turns.

## Case 3 — only the spend

**Sample input:** "Where did the money go this month?"

**Expected behaviors:**
- [ ] Runs the spend script alone, without labelling.
- [ ] Reports the total, the split by model and the top four sessions.

Status: exit 2 (the numbers above come from the manual audit this skill was extracted from; no fresh-agent run is recorded yet).

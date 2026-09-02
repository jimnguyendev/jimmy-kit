# Problem Frame

Use this artifact before option generation. Its purpose is to define a decision-worthy gap without smuggling in a solution.

## Template

```text
Decision owner: who may accept the frame and eventual decision
Stakeholders: customer, user, operator, buyer, regulator, or downstream team affected
Actual state: observable behavior today
Actual-state evidence: source, date, scope, and confidence
Expected state: what the stakeholder needs or believes should happen
Gap: the measurable or observable difference between actual and expected
Why it matters: consequence for the stakeholder or system
Abstraction level: symptom / workflow / capability / system / policy
Constraints: hard limits that options must satisfy
Assumptions: labelled [VERIFIED] or [ASSUMPTION], each with a check
Cause hypotheses: plausible mechanisms, not yet treated as causes
Success evidence: what observation would show the gap is acceptably closed
Out of scope: adjacent gaps this decision will not solve
```

## Gate checks

1. **Solution-free:** rewrite the gap without product names, technologies, or implementation verbs. If meaning disappears, the brief was a solution.
2. **Stakeholder-specific:** customer, user, operator, and buyer may have different gaps. Do not collapse them into "the business."
3. **Evidence-backed actual:** one trace or anecdote may establish existence, not frequency or impact. State what it proves and what it does not.
4. **Challenge the expected state:** ask what job created the expectation. It can be cheaper and more honest to change the expectation, make waiting legible, or narrow a promise than to change reality.
5. **Choose the useful level:** move up until multiple solutions become visible; move down until evidence and ownership are actionable.
6. **Causes remain hypotheses:** a cause becomes verified only after an observation or intervention distinguishes it from alternatives.

Fail the gate when the decision owner, stakeholder, actual/expected gap, or success evidence is unknown. Ask for or design the smallest check that can resolve the missing field.

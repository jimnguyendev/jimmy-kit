# Scenario — engineering-design-thinking (written BEFORE the revision)

**Rationale:** an agent can perform five ceremonial gates while still accepting a solution-shaped brief, treating conventions as fundamentals, compromising across removable coupling, and never learning from the shipped outcome.

**Sample input:** "Add a real-time event bus so every profile update appears instantly everywhere. The current API takes 700 ms in one dashboard trace; support expects under 300 ms, but we have not separated database time, network time, or rendering time. We also need strict ordering without reducing throughput."

**Expected behaviors:**
- [ ] Writes a solution-free Problem Frame with stakeholder, actual state and evidence, expected state, gap, abstraction level, constraints, assumptions, cause hypotheses, and success evidence.
- [ ] Does not treat "event bus" or "strict ordering everywhere" as a requirement without challenge.
- [ ] Uses first-principles mode: separates facts, conventions, and assumptions; goes one causal layer deeper; derives options from fundamentals.
- [ ] Classifies throughput versus ordering as a possible contradiction and tests separation in time, space, condition, and parts/whole before accepting a compromise.
- [ ] When complexity is central, distinguishes essential from accidental complexity, scans the relevant complexity axes, and chooses reduce, isolate, or accept.
- [ ] Treats Functional Core / Imperative Shell as a heuristic and preserves role-first OOP where state ownership, lifecycle, or adapters make it clearer.
- [ ] Stops analysis using a timebox/evidence threshold and records `Claim -> Evidence -> Decision -> Outcome -> Model update`.

**Status:** [EXIT 2 — scenario specified; no independent fresh-agent run recorded yet].

## Package-graph extension (written BEFORE the philosophy revision)

When Gate 4 designs package/module boundaries, the output must preserve capability locality, start with fewer modules, keep names and types near their owner, require one-way dependencies, classify contention when relevant, and explain any intentional departure from feature-first organization.

## Prior-art and runtime-claim extension (written BEFORE the 1.2.0 revision)

**Sample input:** "Our modules keep sharing tables through glue packages and nobody can follow a request. Redesign how modules talk. The design doc says a nightly job takes a lease so only one replica runs it."

**Expected behaviors:**
- [ ] Treats prior-art research as conditional: it is run because the boundary mechanism is an unresolved, consequential question, by direct reading or by a delegated subagent, timeboxed, citing primary sources, and recording what applies and which assumptions were rejected.
- [ ] Skips the research when an accepted local ADR already settles the question.
- [ ] Counts the files a newcomer opens to follow one flow and treats fragmentation across many small packages as a cost.
- [ ] Does not accept the design doc's claim about the nightly job as verified: asks for a check that runs the scheduled work through the real scheduler and states the guarantee separately (mutual exclusion, once per period, idempotent effects).

**Status:** [EXIT 2 — scenario specified; no independent fresh-agent run recorded yet].

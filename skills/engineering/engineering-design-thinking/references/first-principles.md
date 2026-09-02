# First-Principles Mode

First principles is a bounded derivation tool, not a ritual to reinvent known engineering. Use it when the situation is unfamiliar or high-risk, a copied pattern conflicts with evidence, causal understanding is weak, or the cost of a wrong assumption dominates the cost of analysis.

## Derivation loop

1. **State the decision:** name the choice this analysis must change.
2. **Separate inputs:** list verified facts, useful conventions, and unverified assumptions. A best practice is a convention until its mechanism and fit are shown here.
3. **Decompose:** ask "why?" and "what must be true?" until reaching testable fundamentals: physical limits, protocol semantics, incentives, data ownership, ordering, failure behavior, or human needs.
4. **Map interactions:** show how those fundamentals constrain or amplify one another. Unknown links become cause hypotheses, not facts.
5. **Derive options upward:** combine the fundamentals into at least two options. Patterns may reappear, but now as conclusions with conditions.
6. **Seek unknown unknowns:** ask what observation would falsify the model, which stakeholder or failure mode is absent, and what lies one layer deeper than the current explanation.
7. **Close the loop:** record `Claim -> Evidence -> Decision -> Outcome -> Model update` and revise the model after delivery.

## Stop rules

- Set a timebox proportional to reversibility and blast radius.
- Go one causal layer deeper than the decision requires; do not map the entire system.
- Stop when another layer is unlikely to change the option ranking, or when the next uncertainty is cheaper to resolve with a prototype, measurement, or reversible slice.
- If no option can yet be distinguished, return the smallest evidence-gathering action instead of more prose.

## Failure modes

- **Analysis paralysis:** endless Five Whys without a decision boundary or timebox.
- **False inference:** a plausible mechanism promoted to fact without a discriminating check.
- **Unimportant depth:** solving a fundamental problem that does not materially close the stakeholder gap.
- **Pattern rejection:** refusing proven patterns merely because they were not invented here. Use patterns when their conditions match; verify the condition.

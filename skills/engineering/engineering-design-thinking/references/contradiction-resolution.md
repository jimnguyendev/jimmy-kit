# Contradiction Resolution

Use this after options are visible and before accepting a compromise between two desired properties.

## Classify the conflict

- **Ordinary trade-off:** increasing one property consumes a genuinely shared finite resource. Compare options by benefits, resources, and harmful effects.
- **Contradiction:** the same system appears to need opposite properties, often because responsibilities, conditions, or time horizons are coupled. Try to remove the coupling first.
- **Impossible promise:** the properties violate a hard constraint. Expose it; do not hide it behind a midpoint.

Write the conflict as: "We want **A** for benefit X, and **not-A** for benefit Y, under condition Z."

## Separation operators

1. **Time:** use different behavior during write/read, peak/off-peak, migration/steady state, or before/after verification.
2. **Space:** apply different behavior at edge/core, region, shard, trust boundary, or hot/cold path.
3. **Condition:** switch behavior only when risk, load, confidence, tenant, or data class meets an explicit predicate.
4. **Parts and whole:** let components optimize locally while the whole preserves a different property; examples include a functional core with an imperative shell or per-part ordering with global eventual convergence.

Also test whether a dependency can be removed, inverted, delayed, duplicated safely, or made observable. Re-score the resulting options using solution ideality; separation can add resources or harmful effects of its own.

If no operator removes the conflict, record the remaining trade-off, who accepts it, the condition under which it should be revisited, and the evidence that would change the choice.

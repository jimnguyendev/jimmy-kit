# Engineering Philosophy Preservation Design

## Goal

Preserve the engineering philosophy of the predecessor skill set inside Jimmy Kit without copying its whole Go pack, adding a new skill, or turning the principles into mandatory ceremony.

## Source contract

The philosophy to preserve is:

> Programming is thinking, not typing. Structure serves clarity, not paradigm.

Seven operating principles follow:

1. Organize code around business capabilities, not technical layers.
2. Start with fewer packages/modules and split only when observed pain justifies a boundary.
3. Keep names short and avoid repeating package/type context.
4. Keep types close to the behavior or boundary that owns them.
5. Keep dependencies one-way; module/package imports form a DAG.
6. Constrain and measure before optimizing.
7. Enforce correctness with evidence, gates, and reversible delivery.

## Dependency-direction contract

Directed acyclic dependencies are a stack-neutral design principle. Go makes package import cycles a compile-time error; TypeScript and other module systems may permit or defer them, but the coupling and initialization-order risks remain.

Resolve a cycle in this order:

1. Move behavior to the module that owns the responsibility.
2. Merge modules when the boundary is artificial and creates two-way knowledge.
3. When independent ownership is real, define the smallest contract at the consumer and inject the provider from the composition root.

Do not create a generic shared package or an interface for every implementation merely to make the graph compile. The resulting graph must improve ownership and locality, not only move the dependency.

## Integration design

- Add the manifesto and seven principles to `README.md` as the human-facing kit philosophy.
- Add one progressive-disclosure reference under `codebase-design/references/` as the operational source for engineering agents.
- Make `engineering-design-thinking` apply it when package/module boundaries are in scope.
- Make `codebase-design` use it when judging locality, ownership, names, type placement, and dependency direction.
- Make `improve-codebase-architecture` report cycles and fake boundaries using the same resolution order.
- Make `tdd-go` enforce the principles only when implementation creates or moves packages, types, or interfaces. Go is an enforcement example, not the owner of the general principle.
- Preserve the existing performance and quality-gate skills as the owners of principles 6 and 7.

## Scope boundaries

- No new skill and no inventory change.
- Do not copy the old backend pack or its framework/library mechanics.
- Do not impose feature-first layout when a target repository has an explicit accepted alternative; require a recorded reason and preserve locality/DAG invariants.
- Do not duplicate the full philosophy in every skill. Keep short trigger-specific hooks and one canonical operational reference.
- Preserve the current risk-based dosage and `reduce | isolate | accept` complexity model.

## Proof

- Scenario-first Go and TypeScript cycle cases demonstrate stack-neutral behavior.
- A deterministic audit verifies all seven principles, cycle-resolution order, Go-as-enforcement wording, reference routing, and no skill-count increase.
- Existing complexity, problem-solving, routing, orchestration, syntax, inventory, and plugin checks remain green.

# Managing Complexity: Reduce, Isolate, or Accept

Use this reference only when state, effects, dependencies, control flow, or size are central to the decision. It is a lens, not a required architecture.

## 1. Classify before choosing a paradigm

- **Essential complexity** belongs to the problem: real domain rules, required ordering, durable state, failure, or coordination. It cannot be deleted by changing syntax.
- **Accidental complexity** comes from the chosen design: hidden ordering, shared mutation, unnecessary effects, unstable dependencies, indirection, or duplicated control flow.

For each relevant axis, choose one treatment:

- **Reduce** a moving part that does not need to exist.
- **Isolate** a moving part that must exist behind one owner and a small interface.
- **Accept** essential complexity whose removal would cost more or hide the real model.

Reject a refactor that merely relocates complexity while adding indirection or code.

## 2. Scan the five axes

| Axis | Reduce with explicit data flow when… | Isolate behind a role when… | Accept when… |
|---|---|---|---|
| Shared mutable state | a transition can take a value and return a new value | authoritative state or lifecycle must persist across calls | the domain truly requires changing state and one owner controls it |
| Side effects | an effect is unnecessary, repeatable as data, or can be delayed | database, network, clock, file, queue, UI, or transaction work must happen | the effect is the product capability; make failure and retry explicit |
| Dependencies | inputs can be passed as stable values and time ordering disappears | a volatile process or framework needs an adapter | the dependency is essential and already local |
| Control flow | a data pipeline, lookup, or explicit result removes hidden ordering | coordination, retry, error recovery, or variant dispatch must remain | branching expresses a real domain distinction |
| Code size | deletion, a deeper module, or one rule owner removes duplication | a small interface can hide necessary implementation | another abstraction would add more surface than it removes |

## 3. When FP actually reduces complexity

Use a functional style when the work can be expressed as **explicit inputs -> deterministic value/result**:

- calculations, validation, policy, mapping, selection, and state-transition rules;
- dependencies can be supplied as values rather than fetched implicitly;
- mutation can become a returned new value;
- execution order can follow a visible data-flow graph rather than ambient time.

This reduces shared mutation, unnecessary effects, temporal dependencies, and control-flow reasoning. It does **not** remove essential rules, guarantee fewer lines, or become functional merely because imperative code was wrapped in a helper.

## 4. When OOP isolates complexity

Use object-oriented design when a necessary moving part needs one owner:

- state ownership and invariant protection;
- lifecycle or resource management;
- effectful coordination, retry, or recovery;
- a volatile adapter selected behind a stable contract;
- behavior that must be replaced or bound late.

Design **messages, roles, and contracts before classes**. Objects communicate through the role interface and do not reach into each other's state. Prefer composition over inheritance. A class is one construction mechanism, not proof of OOP.

OOP has failed when it creates a free-form graph of shared mutable objects, assigns cross-cutting behavior to arbitrary noun classes, or adds interfaces and indirection without isolating a real variation or moving part.

### TypeScript backend

- Functions and immutable values fit pricing, authorization policies, validation, mapping, and domain transitions.
- Objects/classes fit connection or transaction lifecycle, state ownership, application coordinators, dependency-injection boundaries, and external adapters.
- An immutable value object may expose methods that return a new value; OO syntax does not make the operation stateful.
- Keep decorators, framework requests, database clients, and event publishers outside the functional core.
- Start from `PlaceOrder` roles and messages, not an inheritance tree or a god `OrderService`.

For Go, the same decision uses functions, structs, and small consumer-owned interfaces; an imperative shell does not require classes. In React, pure reducers/selectors may sit in the core while hooks/effects remain in the shell.

## 5. Functional Core / Imperative Shell

Use this heuristic when meaningful work can be separated from effects and coordination:

```text
imperative shell: load -> call core -> persist/publish
functional core:  values -> rules/transition -> result + explicit decisions
```

Do not impose it on simple CRUD, a thin adapter, or work dominated by one unavoidable effect. If extracting the core only creates parameter plumbing, fake ports, or a second vocabulary, keep the direct local flow.

## 6. Verification follows the boundary

| Area | Evidence |
|---|---|
| Pure core | direct example/property tests without mocks |
| Coordinator or state owner | behavior tests through its public role; fakes only at process boundaries |
| Database/network/framework adapter | contract or integration tests against the real boundary semantics |
| Critical user flow | a small number of end-to-end tests |

## Decision record

```text
Essential complexity:
Accidental complexity:
Axes observed:
Treatment per axis: reduce | isolate | accept
Core/shell boundary (if useful):
Messages, roles, and state owner:
Complexity deleted versus merely relocated:
Verification by layer:
```

## Source basis

- [Software Design and Refactoring slides](https://www.slideshare.net/slideshow/software-design-and-refactoring-215436212/215436212)
- [What's Functional Programming All About?](https://www.lihaoyi.com/post/WhatsFunctionalProgrammingAllAbout.html)
- [The Forgotten History of OOP](https://medium.com/javascript-scene/the-forgotten-history-of-oop-88d71b9b2d9f)
- [Object-Oriented Programming: A Disaster Story](https://medium.com/@brianwill/object-oriented-programming-a-personal-disaster-1b044c2383ab)
- [Boundaries](https://www.destroyallsoftware.com/talks/boundaries)

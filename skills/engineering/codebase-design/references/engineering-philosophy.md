# Engineering Philosophy

> Programming is thinking, not typing. Structure serves clarity, not paradigm.

Use these principles when module/package ownership, code placement, names, dependencies, performance, or delivery proof are part of the decision. They are defaults, not a demand to restructure code that already has an accepted and coherent local convention.

## How we organize

### 1. Organize around business capabilities

Default to **feature-first** locality: keep one business capability mostly together instead of spreading it across global technical-layer buckets such as `handlers`, `services`, `repositories`, and `models`. A target repository may choose another architecture, but the design must still make ownership, locality, and dependency direction clear.

### 2. Start with fewer packages and modules

One package or module is often enough at the beginning. Split only when observed pain shows a distinct responsibility, change boundary, deployment need, or independently useful seam. If two units cannot be understood or changed independently, merge the fake boundary instead of maintaining architecture theatre.

### 3. Keep names short and contextual

Avoid stuttering: a name should not repeat package or type context already visible at the call site. Prefer `orders.Service`, `orders.Create`, and `invoice.Total` over names such as `orders.OrderService`, `CreateOrder`, or `InvoiceTotal` when the surrounding context already carries the noun.

### 4. Keep types near their owner

- Transport request/response types stay near the transport boundary that owns them.
- Persistence-only rows and mappings stay near the persistence adapter that uses them.
- Domain values stay with the business capability that defines their meaning.
- Extract a shared type only when multiple capabilities truly share the concept and its ownership is explicit.

### 5. Keep dependencies one-way

Module/package dependencies should form a **directed acyclic graph (DAG)**. This is a stack-neutral design principle: Go enforces package cycles at compile-time, while TypeScript and other module systems may build a cycle and expose the damage later through hidden coupling, initialization order, or changes that cannot be made independently.

Go makes the rule unusually visible because the compiler rejects import cycles outright. As Rob Pike put it: "Import cycles can be convenient but their cost can be catastrophic." An acyclic graph also keeps compilation traversal simpler, exposes architectural coupling early, and makes packages easier to version and maintain independently. These are benefits of the dependency shape, not reasons to classify the principle as Go-only.

## Breaking circular dependencies

A cycle is ownership evidence, not a request for another abstraction. Try these remedies in order:

### 1. Move responsibility to its owner

If A and B import each other, first ask which module owns the disputed behavior or fact. Pass the minimum stable value needed by the other side rather than importing its entire model.

### 2. Merge a fake boundary

If the modules are inseparable and require two-way knowledge, merge them. One cohesive module has better locality than two names connected by a permanent cycle.

### 3. Introduce a consumer-owned contract at a real seam

When the modules have genuinely independent ownership or lifecycle, define the smallest role/interface in the consumer, make the provider satisfy it, and inject the provider from the composition root. Do not put the contract in the provider and do not create an interface for every implementation.

Do not extract a vague `common`, `shared`, or generic service package merely to make imports compile. Such a dumping ground is justified only when it represents a real owned concept; otherwise it relocates coupling and weakens locality.

The resulting graph must improve responsibility and change isolation, not merely point the same complexity in a different direction.

## How we optimize

### 6. Constrain before optimizing

Define a measurable target, find the hot path, and profile before choosing a pattern. Escalate only when evidence shows the simpler step cannot meet the target. The operational workflow belongs to `engineering-perf-optimization-process`.

## How we ship

### 7. Enforce correctness with gates

AI confidence is not evidence. Before claiming completion, attach proportionate verification, make failure visible, and preserve reversibility or an explicit rollback path. The operational workflow belongs to `quality-gates` and the project's accepted release process.

## Architecture decision record

```text
Capability and owner:
Locality: what changes together and where it lives
Packages/modules: why this many; evidence for each split
Names and type placement:
Dependency DAG: allowed edges and forbidden reverse edges
Cycle treatment: move responsibility | merge | consumer-owned contract
Constraints and proof before optimization:
Verification and reversibility before shipping:
Intentional departure from these defaults:
```

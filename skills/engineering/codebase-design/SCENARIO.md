# Scenario — complexity treatment and TypeScript backend OOP (written BEFORE the revision)

**Rationale:** architecture advice can turn "functional core" into an ideology, or treat OOP as class hierarchy instead of a way to isolate state, side effects, dependencies, and coordination.

**Sample input:** "Our TypeScript order backend validates pricing rules, writes Postgres, calls a payment gateway, and publishes an event. The team proposes either one large OrderService class or rewriting everything as pure functions. Design the module, including how it should be tested."

**Expected behaviors:**

- [ ] Separates essential domain complexity from accidental implementation complexity.
- [ ] Scans shared mutable state, side effects, dependencies, control flow, and code size.
- [ ] Chooses `reduce`, `isolate`, or `accept` for each relevant source rather than promising to remove all complexity.
- [ ] Uses Functional Core / Imperative Shell only where it improves locality: pricing/invariants may be pure; database, gateway, publication, and coordination stay at the shell.
- [ ] Designs messages, roles, and contracts before classes; permits TypeScript objects/classes for state ownership, lifecycle, DI, adapters, or coordination and prefers composition over inheritance.
- [ ] Tests the pure core directly without mocks, tests shell/adapters at process boundaries or through integration, and reserves end-to-end coverage for critical flows.
- [ ] Rejects both a god class and a forced all-functions rewrite.

**Counterexample:** A local, conventional CRUD path with no meaningful domain rules or coordination should not be split into a ceremonial functional core and object shell.

## Companion Go backend case (written BEFORE adding the eval)

**Sample input:** "Design a Go order backend that applies pricing rules, writes Postgres, calls a payment gateway, and publishes an event. The team proposes either a Java-style interface for every struct or one large service struct."

**Expected behaviors:**

- [ ] Uses the same essential/accidental classification, five-axis scan, and `reduce | isolate | accept` treatment instead of treating Go as a separate design philosophy.
- [ ] Keeps deterministic rules and value transitions as functions over values where that deletes mutation or temporal coupling.
- [ ] Uses structs for cohesive state or dependencies and small consumer-owned interfaces only at real process or variation seams.
- [ ] States that an imperative shell does not require classes and rejects Java-style interface-per-struct ceremony.
- [ ] Isolates Postgres, payment, publication, and coordination while accepting real distributed-workflow failure and ordering.
- [ ] Separates direct core tests from adapter integration or contract tests and a small number of critical end-to-end flows.

**Status:** [PASS — exit 0] TypeScript run #2 passed 7/7 and the Go companion run passed 6/6 on 2026-09-02.

## Independent fresh-agent Go run

The agent received only `SKILL.md`, the reference it selected, and the Go sample prompt. It did not see this scenario, evals, plans, audit scripts, or the diff.

```text
Essential complexity: pricing invariants, durable order/payment state, payment failure and retry, and reliable event publication.

Accidental complexity: Java-style interfaces for inert structs, one catch-all struct, hidden operation ordering, duplicated rules, and direct infrastructure coupling.

Axes observed: shared state, side effects, dependencies, control flow, code size.

Treatment per axis (reduce/isolate/accept): reduce pricing to explicit value transformations; isolate Postgres, gateway, publishing, and transaction lifecycle behind small roles; accept the required distributed-workflow states and failure handling.

Complexity deleted versus relocated: plain functions remove mutable pricing machinery; consumer-owned interfaces isolate real process seams. An interface per struct or splitting a large struct into pass-through wrappers only relocates complexity.

Verification by layer: table/property tests for pricing; coordinator behavior tests through Place with fakes at process seams; Postgres, gateway, and publisher contract/integration tests; a few end-to-end flows.

Use a deep order module with a small caller interface. Price(input, rules) is a plain deterministic function. Order, Quote, and rule values remain structs, not interfaces. Small orderStore and paymentGateway interfaces are declared by their consumer. A coordinator struct owns unavoidable effect ordering without becoming a large miscellaneous module. The Postgres adapter atomically updates the order and writes an outbox record; a separate publisher owns delivery retries.
```

**Score:** 6/6 Go companion behaviors.

## Independent fresh-agent run #2

The agent received only `SKILL.md`, the reference it selected, and the sample prompt. It did not see this scenario, evals, plans, audit scripts, or the diff.

```text
Essential complexity: pricing rules; durable order/payment state; payment failure, retry, and reconciliation; reliable event publication; required operation ordering.

Accidental complexity: a god OrderService, hidden mutation/order, duplicated pricing logic, direct framework/client coupling, or forcing effects through "pure" wrappers.

Axes observed: shared state, side effects, dependencies, control flow, code size.

Treatment per axis (reduce/isolate/accept): reduce pricing and validation to deterministic value transformations; isolate Postgres, gateway, publishing, transaction lifecycle, and retries behind roles; accept the real distributed-workflow states and failure paths.

Complexity deleted versus relocated: immutable pricing results delete hidden mutation and rule duplication. Adapters isolate unavoidable effects. Splitting a large class into pass-through functions would only relocate complexity.

Verification by layer: example/property tests for pricing; coordinator behavior tests through the public role with process-boundary fakes; Postgres/gateway/publisher contract or integration tests; a few end-to-end order flows.

Use a mixed deep module with a PlaceOrder message. Its implementation contains a pure pricing/validation module, a coordinator owning sequence and state transitions, injected OrderRepository/PaymentGateway/EventOutbox roles, and concrete adapters outside the core. This avoids both extremes: pure functions handle rules where they genuinely reduce complexity; an object or closure-based coordinator owns unavoidable effectful ordering without becoming a catch-all class.

For conventional local CRUD with no meaningful rules, keep a direct request-to-Postgres module. Do not manufacture a functional core, repository seam, or fake adapters unless real variation appears.
```

**Score:** 7/7 expected behaviors.

## Philosophy preservation cases (written BEFORE the philosophy revision)

### Go package cycle

**Sample input:** "A Go backend has `orders` importing `inventory` to reserve stock, while `inventory` imports `orders` to read order state. The team proposes adding `common`, plus global `handlers`, `services`, `repositories`, and `models` packages. Redesign the package graph."

**Expected behaviors:**

- [ ] Treats structure as a clarity decision rather than choosing a paradigm or fashionable architecture.
- [ ] Defaults to business-capability locality and fewer packages; rejects technical-layer buckets and a vague `common` dumping ground.
- [ ] Keeps names contextual without package/type stuttering and keeps transport/persistence types near their owner.
- [ ] Requires a one-way DAG and tries cycle remedies in order: move responsibility, merge a fake boundary, then use a small consumer-owned contract at a real seam.
- [ ] States that Go enforces package DAGs at compile time but the design principle is stack-neutral.
- [ ] Does not create an interface for every struct or claim that moving imports alone reduced complexity.

### TypeScript module cycle

**Sample input:** "A TypeScript backend has `billing` importing `notifications` to send receipts, while `notifications` imports `billing` to format invoice data. It builds today. Should we ignore the circular import or create a shared service layer?"

**Expected behaviors:**

- [ ] Applies the same ownership, locality, and DAG reasoning even though the compiler may allow the cycle.
- [ ] Rejects a generic shared service layer unless it represents a real owned concept.
- [ ] Uses a consumer-owned contract only if billing and notification remain genuinely independent modules.
- [ ] Explains the hidden coupling and initialization/change risks rather than presenting the problem as Go-specific.

**Status:** [PASS — exit 0] Existing TypeScript complexity and Go companion cases passed; philosophy baseline exposed inspectability gaps, then the final Go run passed 6/6 and TypeScript passed 4/4 on 2026-09-02.

## Philosophy baseline runs

Fresh agents received only the pre-revision `codebase-design` entrypoint and references selected from it. They did not see this scenario, source repository, evals, plans, audit, README, or diff.

- **Go: 3/6.** It rejected global technical layers and `common`, kept capability types local, and proposed a one-way graph. It did not enumerate the three remedies in order, explicitly cover naming/stuttering, or distinguish Go enforcement from the general design principle.
- **TypeScript: 2/4.** It rejected both ignoring the cycle and a generic shared layer, then proposed a billing-owned sender role. It did not evaluate move/merge before the interface or make the stack-neutral enforcement distinction inspectable.

## Independent final TypeScript run

```text
Essential complexity: Billing creates invoice data and triggers receipt delivery; notifications delivers messages.

Accidental complexity: Each module knows the other’s implementation, creating a circular dependency and possible initialization-order failures.

Do not ignore the cycle, even though TypeScript builds today. Also do not create a generic shared service layer.

Billing should own invoice facts and receipt formatting. Notifications should accept a ready-to-send ReceiptMessage and know nothing about billing. Define the smallest consumer-owned role in billing, implement it in notifications, and wire the adapter at the composition root.

The resulting dependency direction is one-way. This improves ownership and locality while avoiding a shared dumping ground that merely hides the same coupling.
```

**Score:** 4/4 TypeScript philosophy behaviors.

## Independent final Go run #2

Run #1 produced a strong capability-first graph but jumped directly to an interface and omitted the enforcement distinction. The output contract was tightened before this rerun.

```text
Capability and owner:
- orders owns Order, State, lines, and legal order transitions.
- inventory owns available stock, reservation rules, and Reservation.
- placeorder owns the workflow that reads/transitions an order and requests a reservation.
- cmd/api is the composition root only.

Locality: domain types, persistence mappings, handlers, and rules stay with the capability that changes them.

Packages/modules and evidence for each split: placeorder is justified only when cross-capability sequencing, error handling, and retries are a distinct responsibility. If the flow is trivial, delete that package and keep Place in orders.

Names and type placement: prefer orders.Order, inventory.Reservation, and placeorder.Command; avoid OrderModel, OrderService, and InventoryRepository. HTTP types stay beside transport; database rows stay beside each capability's adapter. Do not create common.

Dependency DAG: cmd/api -> placeorder/orders/inventory; placeorder -> orders/inventory. Forbid orders <-> inventory and reverse edges to placeorder or cmd/api.

Cycle treatment, in required order:
1. Move responsibility — selected. Orders decides eligibility, inventory enforces stock invariants, and placeorder sequences them. This fully removes the cycle.
2. Merge fake boundary — not needed because orders and inventory have independent meanings and rules.
3. Consumer-owned contract — not needed to break this cycle; add the smallest role later only if a real adapter varies.

Go rejects the original import cycle at compile time, but the underlying rule is broader: capability dependencies should form a DAG so ownership and change direction remain clear.
```

**Score:** 6/6 Go philosophy behaviors.

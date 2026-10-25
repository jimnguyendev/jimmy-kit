# Domain-Driven Design (DDD) in Go

## When to Use

Apply DDD when the business domain is complex enough that the code structure should mirror the business model — typically services with 5K+ lines, multiple bounded contexts, or rich business rules. Do NOT use for simple CRUD apps or CLI tools.

DDD is for genuine domain complexity. It should not replace simple feature-first structure in ordinary APIs.

Start from a simple `internal/order/` or `internal/billing/` package first. Split into `domain/`, `application/`, and `adapters/` only when the domain is rich enough that the extra boundary reduces confusion more than it adds ceremony.

## Building Blocks

| Concept | Go Mapping | Purpose |
| --- | --- | --- |
| **Entity** | Struct with identity field | Has unique ID, mutable state, lifecycle |
| **Value Object** | Immutable struct, compared by value | No identity — represents a measurement, quantity, or descriptor |
| **Aggregate** | Entity + child entities/value objects | Consistency boundary — all mutations go through the root |
| **Repository** | Interface in domain, impl in infrastructure | Persistence abstraction for aggregates |
| **Domain Service** | Function or struct in domain package | Logic that spans multiple aggregates |
| **Domain Event** | Struct describing a fact that happened | Decouples bounded contexts |

## Project Structure

Organize by **bounded context**, grouping domain, application, and adapters vertically when the complexity is real. The bounded context still acts like a feature slice: most work on one business capability should stay inside one subtree.

```
order-service/
├── cmd/
│   └── server/
│       └── main.go                  # Wiring only
├── internal/
│   ├── order/                       # Bounded context: Order
│   │   ├── domain/
│   │   │   ├── order.go             # Order aggregate root
│   │   │   ├── item.go              # OrderItem entity
│   │   │   ├── status.go            # OrderStatus enum
│   │   │   ├── repository.go        # OrderRepository interface
│   │   │   └── events.go            # OrderPlaced, OrderShipped events
│   │   ├── application/
│   │   │   ├── place_order.go       # PlaceOrderHandler (command)
│   │   │   └── get_order.go         # GetOrderHandler (query)
│   │   └── adapters/
│   │       ├── persistence/
│   │       │   └── postgres.go      # OrderRepository implementation
│   │       └── http/
│   │           └── handler.go       # HTTP transport
│   ├── billing/                     # Bounded context: Billing (another example)
│   │   ├── domain/
│   │   ├── application/
│   │   └── adapters/
│   ├── shared/
│   │   └── money.go                 # Value object reused across contexts
│   └── events/
│       └── publisher.go             # Shared event bus (infrastructure)
├── go.mod
└── go.sum
```

**Key principles:**

- Group each bounded context **vertically** (domain → application → adapters), not by technical role
- Use `adapters/` instead of `infrastructure/` to be explicit about Hexagonal Architecture
- Make cross-context boundaries explicit (see **Bounded Contexts** section below)
- Place shared infrastructure (event bus, logging) at `internal/{shared}/` or `internal/events/`
- Keep shared packages small; if a concept is mostly used by one bounded context, keep it there

## Code Examples

### Value Object — Money

```go
// internal/domain/shared/money.go
package shared

type Money struct {
    amount   int64  // cents — avoids float precision issues
    currency string
}

func NewMoney(amount int64, currency string) (Money, error) {
    if currency == "" {
        return Money{}, errors.New("currency is required")
    }
    return Money{amount: amount, currency: currency}, nil
}

func (m Money) Add(other Money) (Money, error) {
    if m.currency != other.currency {
        return Money{}, fmt.Errorf("cannot add %s to %s", other.currency, m.currency)
    }
    return Money{amount: m.amount + other.amount, currency: m.currency}, nil
}
```

### Aggregate Root — Order

```go
// internal/domain/order/order.go
package order

type Order struct {
    id     string
    items  []Item
    status Status
    total  shared.Money
}

func NewOrder(id string) *Order {
    return &Order{id: id, status: StatusDraft}
}

// All mutations go through the aggregate root
func (o *Order) AddItem(item Item) error {
    if o.status != StatusDraft {
        return ErrOrderNotEditable
    }
    o.items = append(o.items, item)
    return o.recalculateTotal()
}

func (o *Order) Place() (OrderPlaced, error) {
    if len(o.items) == 0 {
        return OrderPlaced{}, ErrEmptyOrder
    }
    o.status = StatusPlaced
    return OrderPlaced{OrderID: o.id, Total: o.total}, nil
}
```

### Repository Interface — defined in domain

```go
// internal/order/domain/repository.go
package domain

type Repository interface {
    Save(ctx context.Context, order *Order) error
    FindByID(ctx context.Context, id string) (*Order, error)
}
```

The implementation lives in `internal/order/adapters/persistence/postgres.go` and depends on the domain — never the reverse.

### Application Service — orchestrates a use case

```go
// internal/order/application/place_order.go
package application

import (
    "context"
    "fmt"

    "myapp/internal/order/domain"
)

type PlaceOrderHandler struct {
    orders domain.Repository
    events EventPublisher
}

func (h *PlaceOrderHandler) Handle(ctx context.Context, cmd PlaceOrderCommand) error {
    order, err := h.orders.FindByID(ctx, cmd.OrderID)
    if err != nil {
        return fmt.Errorf("finding order: %w", err)
    }

    evt, err := order.Place()
    if err != nil {
        return fmt.Errorf("placing order: %w", err)
    }

    if err := h.orders.Save(ctx, order); err != nil {
        return fmt.Errorf("saving order: %w", err)
    }

    return h.events.Publish(ctx, evt)
}
```

## Bounded Contexts

Each bounded context maps to a top-level package under `internal/` with its own domain, application, and adapters. Contexts communicate through domain events or explicit anti-corruption layers — never by importing each other's internal types directly. In a single binary over one database, a published contract package (below) is a lighter alternative for synchronous reads.

If two contexts constantly need each other's internals, the split is probably wrong. Revisit the boundary before adding more abstraction.

**Anti-corruption layer example:** If `billing/` needs to consume an `order.OrderPlaced` event, translate it to a billing-specific type:

```go
// internal/billing/adapters/events/order_events.go
package events

import (
    "myapp/internal/events"
    "myapp/internal/billing/domain"
)

type OrderPlacedSubscriber struct {
    invoices domain.InvoiceRepository
}

// Receives order.OrderPlaced, translates to billing domain
func (s *OrderPlacedSubscriber) OnOrderPlaced(evt events.OrderPlaced) error {
    // Translate and create invoice
    return s.invoices.Create(evt.OrderID, evt.Total)
}
```

This prevents billing from depending on order's internal types.

For large systems, each context can be its own Go module in a workspace (`go.work`). See the `backend-go-project-layout` skill for workspace setup.

### Published contracts in a single-binary modular monolith

Optional pattern, for when one module must read another module's data synchronously and the team wants the data's schema, tenant guard and tests to stay in one place. It follows the idea of integration services and contracts in ABP Framework (a module publishes an API package; callers reference only that package). A target repository's own ADRs outrank this section.

**Two different things, do not mix them up:**
- A **consumer-owned dependency role** is a small interface the consumer declares for something it needs (the Go default; see the circular-dependency order in `backend-go-project-layout`).
- A **provider-owned published API** is a `contract/` package the owner publishes for real integration requirements. Add one only when an actual integration needs it. Never add one just to make an import compile. For a cycle keep the order: move the responsibility, merge a false boundary, then introduce a contract.

**Shape:**

```go
// internal/catalog/contract/contract.go — imports no module
package contract

type Product struct{ ID, Name string; Price int64 }

type StoreShelf interface {
    SellableProducts(ctx context.Context, tenantID string, storeID string, ids []string) (map[string]Product, error)
}
```

```go
// internal/catalog/integration.go — the owner's Service satisfies it; its SQL stays in catalog's repository
var _ contract.StoreShelf = (*Service)(nil)
```

```go
// composition root: pass the Service straight in, there is no adapter layer
recommend.New(recommend.Deps{Shelf: catalogSvc})
```

**Rules that keep it safe:**
- The contract owns its DTOs, errors and event payloads. It does not alias the owner's internal types and does not import any module, so import cycles cannot form through contracts. Construction order must be acyclic as well: build modules in dependency order.
- Tenant identity is an explicit argument. A contract carries no database handle and no transaction.
- Transactions: one use case is one transaction inside the owner, including its outbox and inbox rows. An effect on another module travels as an outbox event the other module applies in its own transaction. Lock the row first, apply the rules, write last, lock tables in one fixed order, and give every use case that takes a lock a concurrent test. Keep the pure rules free of the database. (The boundary and rules-on-the-model points follow threedots.tech "Database transactions in Go", which does not cover deadlocks or retries.)
- Contract tests live next to the owner and cover tenant isolation and missing or NULL rows (a `LEFT JOIN` filtered with `NOT (a OR b)` silently drops rows whose joined side is NULL).
- Strict table ownership (a module's SQL names only its own tables) is a policy a team selects, ideally enforced by a lint rule with an owner map. A glue adapter that translates meaning between two models stays valid; one that only runs SQL on a table it does not own is the smell. Reporting that must join several modules' tables is a documented, read-only, bounded exception.

**Not required by this pattern:** aggregate roots, specifications, a repository per aggregate, permission trees, a broker for in-process events.

## Wiring

Wire dependencies in `cmd/server/main.go` using manual constructor injection.

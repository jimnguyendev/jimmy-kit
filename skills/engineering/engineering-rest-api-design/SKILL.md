---
name: engineering-rest-api-design
description: "REST API design conventions covering URL structure, HTTP methods, pagination, sparse-fieldset query collections, async patterns, idempotency, error envelopes, and API documentation standards. Use when designing new endpoints, reviewing API contracts, or establishing API guidelines before implementation in any language."
user-invocable: false
license: MIT
compatibility: Designed for Claude Code or similar AI coding agents.
metadata:
  version: "1.1.0"
allowed-tools: Read Edit Write Glob Grep Bash(git:*) Agent AskUserQuestion
---

**Persona:** You are a senior API architect. Every endpoint you design is a contract — once published, it becomes someone else's dependency. Design for the consumer first, optimize for the maintainer second.

**Modes:**

- **Design mode** — designing new endpoints: apply conventions top-down, validate against checklist in `references/checklist.md`.
- **Review mode** — reviewing existing API contracts: audit naming, pagination, error envelope, idempotency, and async patterns against this skill's rules. Flag violations with severity (breaking / inconsistent / style).
- **Document mode** — writing API documentation: follow the spec template in `references/api-document-template.md`.

# REST API Design

## Mindset

1. **Design first** — think at the high level, cover edge cases on paper, reduce implementation cost.
2. **Scalable** — endpoints should handle growth in consumers, data volume, and team size.
3. **Consistent** — one convention across all services; deviation requires justification.
4. **Inspect every aspect** — URL, method, headers, body, pagination, errors, async behavior.
5. **No one-size-fits-all** — document trade-offs explicitly when deviating from conventions.

## HTTP Methods

| Method | Operation | Safe | Idempotent |
|--------|-----------|------|------------|
| GET | Read | Yes | Yes |
| POST | Create / Batch read | No | No |
| PUT | Update (full or partial) | No | Yes |
| DELETE | Remove / disable | No | Yes |

**Safety** means the method does not alter server state. **Idempotency** means sending the same request multiple times produces the same result.

**PUT over PATCH** — use PUT for all updates. Clients always send the full set of mutable fields. This eliminates ambiguity about which fields are being changed vs intentionally omitted, and keeps the operation unconditionally idempotent. Do not use PATCH.

**POST for batch reads** — when fetching multiple resources by a list of IDs, use POST with a JSON body instead of GET with query parameters. GET query strings have length limits and become unwieldy with many IDs. Pattern: `POST /resources/batch` with body `{ "ids": ["id1", "id2"] }`.

**Create returns 200** — POST create endpoints return `200` with the created resource in the response body. Do not use `201 Created`. This simplifies client handling — consumers check the same status code for all successful operations.

For non-idempotent POST requests, use a unique request ID or `Idempotency-Key` header so the server can detect and deduplicate retries.

## URL Conventions

### Rules

1. **Nouns, not verbs** — the resource is the noun, the method is the verb.
2. **Plural nouns** — `/users`, not `/user`.
3. **Nesting for relationships** — `/articles/{article_id}/comments`.
4. **Versioning in path** — `/api/v1/...`.
5. **Slug-case for URLs** — `/order-service/v1/orders`.
6. **snake_case for request and response body** — `{ "debit_account": "acc01" }`.

### Singular vs Plural

Use plural by default. Use singular only when the resource is inherently unique within its parent:

```
GET /api/users/{id}/profile          # one profile per user → singular
GET /api/users/{id}/profile/addresses/{address_id}  # multiple addresses → plural
GET /api/forms/login                 # one login form among many forms → singular
```

### Custom Actions

When CRUD methods are insufficient (restore, publish, archive), use one of:

**Colon method** (Google API convention) — clearly separates action from sub-resource:

```
POST /files/{id}:restore
POST /v1/{resource}:setIamPolicy
```

**Slash method** — simpler but risks confusion with sub-resources:

```
POST /files/{id}/restore
```

Prefer the colon method when clarity matters. The slash method is acceptable if the team prefers familiar URL conventions and there is no ambiguity with actual sub-resources.

### Examples

```
POST   /order-service/v1/orders              # create
GET    /order-service/v1/orders/145           # get by ID
POST   /order-service/v1/orders/batch         # batch get by IDs
PUT    /order-service/v1/orders/145           # update
DELETE /order-service/v1/orders/145           # delete
```

## Pagination

Two common approaches — choose based on use case, stay consistent within a service.

### Page + Size

```
GET /users?page=0&size=10
```

- Best for: management portals, admin dashboards.
- Must document: whether page starts at 0 or 1.

### Offset + Limit

```
GET /users?offset=0&limit=10
```

- Best for: infinite scroll, newsfeeds, log streams.

### Known Problems

1. **Performance on large datasets** — `OFFSET N` scans and discards N rows.
2. **Resource skipping** — deleting records between paginated requests shifts items across page boundaries.

### Solutions

**Cursor-based pagination** — use the last seen ID as a cursor:

```sql
SELECT * FROM users WHERE id > :last_id ORDER BY id LIMIT 10;
```

**Deferred join** — fetch IDs first, then join:

```sql
SELECT * FROM (
  SELECT id FROM users ORDER BY id LIMIT 100, 10
) a JOIN users b ON a.id = b.id;
```

See `references/pagination-patterns.md` for full comparison of all pagination strategies with decision guide.

## Filtering

Use query parameters to narrow results. Multiple filters combine with AND logic:

```
GET /products?price=20&brand=Nike
GET /orders?status=pending&created_after=2024-01-01
```

For complex filtering (range, OR, nested), document the query language explicitly. Never pass filter values directly into SQL — always parameterize.

## Query Collections (Sparse Fieldsets)

When one collection serves several screens with very different costs (public landing vs personalized dashboard vs expanded cards), do not multiply endpoints, return everything, or reach for GraphQL. Use a POST query endpoint with a small whitelisted field/filter grammar. A reference implementation and full rationale live in the internal docs repo `[docs]` (optional).

```
POST /api/v1/query/{domain}/{collection}
{
  "queries": {
    "fields": "id,name,tags{id,code},learner_state{progress}",
    "filtering": { "product_line_id:eq": 1, "skill_id:in": [1, 2] },
    "limit": 12,
    "offset": 0
  }
}
```

Core rules:

- **`fields` is a 3-symbol grammar** — identifier, comma, braces for subfields. No operators, no literals, nothing to execute, so nothing to inject. Parser carries its own caps (length and nesting depth) independent of the global body limit. Empty `fields` returns the collection's default field set, so adding an expensive field later never bloats old clients.
- **`filtering` keys are `field:operator`** with exactly three operators (`eq`, `in`, `contains`). A per-collection schema whitelists which fields accept which operators and value types, and declares required filters. "No filter" = omit the key; an empty `in` array is a validation error, never `IN ()`. Filter keys are walked in sorted order so duplicate spellings (`premium` vs `premium:eq`) are rejected deterministically and the parsed filter list is stable — a prerequisite for canonical cache keys.
- **Validation collects every violation into one 400** (`extra_meta.violations` as `[{section, field, message}]`) so the client fixes the request in one round-trip. Violation messages stay in English — they address the developer calling the contract, not end users.
- **Expensive data is gated before reading**: check `fields.Has("learner_state")` (plus a valid token) before touching learner stores. Projection trims bytes; gating saves reads — the read is what you are economizing. Any branch that produces a personalized response sets `Cache-Control: no-store`. A token alone never triggers personal reads: the client must also select a learner field.
- **Schemas fail at boot** (`MustSchema` panics on an inconsistent schema), and each collection's test calls `CheckSource(sample)` so a field can never be selectable but permanently empty.
- **Projection stays above the cache**: repositories always return the full shape, keyed by filters + pagination only — `fields` is not part of the cache key, so every field combination shares one cache entry.
- **Two-layer whitelist**: grammar validation (layer 1) then an explicit handler switch mapping each validated filter to a typed struct (layer 2), feeding fixed parameterized SQL. A filter that reaches layer 2 unmapped is a loud 500 (schema/switch drift), never a silently ignored filter. Adding a filter or field means schema + switch branch + wire map key in the same commit.
- Empty collections return `data: []`, never `null`. Pagination uses the standard `meta.pagination` envelope.

Do **not** use this grammar for detail resources, grading results, actions, or polling — those stay typed endpoints. Free multi-dimensional filtering/sorting is a search-engine problem, not a hand-written allowlist. Deep relationship graphs with many divergent clients are where GraphQL (with depth limits, complexity scoring, persisted queries) earns its infrastructure cost.

## Sorting

Three common conventions — pick one per API, stay consistent:

```
# Format A: colon separates field:direction, comma separates fields
GET /products?sort=price:asc,name:desc

# Format B: prefix +/- for direction
GET /products?sort=+price,-name

# Format C: comma separates field,direction pairs, semicolon separates fields
GET /articles?sort=publish_date,asc;title,desc
```

Default sort direction should be documented (typically descending for dates, ascending for names). **Always whitelist sortable fields** — never pass user input directly to `ORDER BY`.

**No sort is a valid contract.** When list order is fixed business ordering, do not expose sorting at all — exposing `sort` invites ordering by unindexed columns. But still *decode and explicitly reject* `sort`/`direction` with a 400 violation: silently ignoring them makes clients believe they are sorting when they are not.

## Relationship Endpoints

### One-to-Many

```
GET /articles/{article_id}/comments
```

### Many-to-Many

```
GET  /classes/{class_id}/students
POST /classes/{class_id}/students/{student_id}
POST /classes/{class_id}/students          # bulk add via body
```

Note: `PUT /classes/{class_id}/students/{student_id}` is acceptable because the operation is idempotent (adding an already-added student has no additional effect).

## Async API Pattern

For long-running operations (file export, report generation, bulk processing) where synchronous response risks timeout, memory exhaustion, or client blocking.

### Job-based Flow

```
# 1. Initiate the job
POST /products/jobs/export?name=pen
→ 202 Accepted
{
  "meta": { "code": "202000", "type": "ACCEPTED", "message": "Job created", "service_id": "product-service" },
  "data": { "job_id": "001", "status": "PROCESSING" }
}

# 2. Poll job status
GET /jobs/001
→ 200
{
  "meta": { "code": "200000", "type": "SUCCESS", "message": "Success", "service_id": "product-service" },
  "data": { "job_id": "001", "status": "COMPLETED" }
}

# 3. Retrieve result
GET /jobs/001/result
→ 200 (file download or data in standard envelope)
```

### Polling vs Webhook

| Approach | Pros | Cons | Use case |
|----------|------|------|----------|
| Polling | Simple to implement | Wastes resources | Small load, import/export |
| Webhook / Callback | Resource-efficient | Complex on both sides | Large load, payment |

## Versioning

See `references/versioning.md` for full comparison. Summary:

| Strategy | Example | Pros | Cons |
|----------|---------|------|------|
| URL path | `/v1/orders` | Visible, simple | New URL per version |
| Channel | `/v1/beta/orders` | Staged rollout | More paths to manage |
| Header | `Api-Version: 2` | URL stays clean | Hidden, easy to miss |
| Query param | `/orders?version=2` | Flexible | Easy to forget |

**Default recommendation:** URL path versioning (`/v1/`). Consider channels (`v1alpha`, `v1beta`, `v1`) for APIs with staged release processes.

If the API is internal and all clients can be updated together, versioning may be unnecessary.

## Rate Limiting

Control request volume to protect backend resources and ensure fair usage.

**Response for exceeded limits:** return `429 Too Many Requests`.

**Inform clients via headers:**

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 500
X-RateLimit-Reset: 1588377600
Retry-After: 120
```

## Idempotency

**Problem:** A request may be sent twice due to network issues or replay attacks. Critical for payment, order, and financial operations.

**Solution:** Client generates an `Idempotency-Key` header (or a unique request/transaction ID). Server enforces uniqueness via a unique constraint in the database. On duplicate, server returns the original response — not an error.

```
POST /payment-service/v1/payments
Headers:
  Content-Type: application/json
  Idempotency-Key: oc8tKg1P2FV44hpj
```

## Response Envelope

Standard envelope structure for all API responses:

```json
{
  "meta": {
    "code": "200000",
    "type": "SUCCESS",
    "message": "Success",
    "service_id": "payment-service",
    "extra_meta": {}
  },
  "data": { ... }
}
```

Paginated list responses carry pagination as a **first-class `meta.pagination` object** — not inside `extra_meta`:

```json
{
  "meta": {
    "code": "200000",
    "type": "SUCCESS",
    "message": "Success",
    "service_id": "course-service",
    "pagination": { "total": 57, "limit": 12, "offset": 0, "has_next": true }
  },
  "data": [ { "id": 5, "name": "IELTS Mock Test 2026" } ]
}
```

Offset-style lists use `limit`/`offset`/`has_next`; legacy page-style lists use `page`/`per_page` in the same object. Empty collections return `data: []`, never `null`.

Error responses use the same envelope with `"data": null`:

```json
{
  "meta": {
    "code": "400001",
    "type": "INSUFFICIENT_DEBIT_AMOUNT",
    "message": "Debit account has an insufficient amount of balance",
    "service_id": "payment-service",
    "extra_meta": {}
  },
  "data": null
}
```

Validation errors that can report multiple field problems return **all of them at once** under `extra_meta.violations` (each `{section, field, message}`) so clients fix a request in one round-trip instead of fix-one-resend-discover-the-next:

```json
{
  "meta": {
    "code": "400000",
    "type": "invalid_query",
    "message": "invalid query",
    "service_id": "course-service",
    "extra_meta": { "violations": [
      { "section": "fields", "field": "tests.bad", "message": "unknown field" },
      { "section": "pagination", "field": "limit", "message": "limit exceeds maximum of 20" }
    ] }
  },
  "data": null
}
```

## API Documentation

Every endpoint must be documented with: spec (method, URL, headers, body), request body field table, response body field table, error table, and cURL sample. See `references/api-document-template.md` for the full template.

## Cross-References

- `engineering-design-thinking` (this kit) — decide the contract before implementing it.
- `domain-modeling` (this kit) — resource names must come from the domain glossary.
- `[docs]` internal Go pack (optional, not bundled): handler code style, error-handling conventions, pagination SQL patterns, and any project-specific response envelope.
- For the query-collection grammar (sparse fieldsets + whitelisted filtering), a reference implementation and its design rationale live in the internal docs repo `[docs]` (optional deep-dive; the grammar above is self-sufficient).

## External Sources

This skill synthesizes conventions from established API design references. Official documentation remains authoritative:

- [Microsoft REST API Guidelines](https://github.com/microsoft/api-guidelines)
- [Google API Design Guide](https://cloud.google.com/apis/design)
- [Stripe API Reference](https://stripe.com/docs/api) (idempotency patterns)
- [REST API Best Practices — freeCodeCamp](https://www.freecodecamp.org/news/rest-api-best-practices-rest-endpoint-design-examples/)

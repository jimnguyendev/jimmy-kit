# REST API Design Checklist

Use this checklist when designing or reviewing API endpoints.

## URL Structure

- [ ] Resource names are plural nouns (`/users`, not `/user`)
- [ ] Singular nouns used only for inherently unique sub-resources (`/users/{id}/profile`)
- [ ] No verbs in URL path (use HTTP methods instead)
- [ ] Custom actions use colon (`:restore`) or slash method — not CRUD verbs in URL
- [ ] Relationships expressed via nesting (`/articles/{id}/comments`)
- [ ] URL uses slug-case (`/order-service`, not `/orderService`)
- [ ] Version included in path (`/api/v1/...`)
- [ ] IDs in path are positional, not query params (`/users/34`, not `/users?id=34`)

## Request / Response Body

- [ ] Field names use snake_case (`debit_account`, not `debitAccount`)
- [ ] Request body documented with type, required flag, default, and description
- [ ] Response follows standard envelope (`meta` + `data`)
- [ ] Null `data` on error responses, never omitted

## HTTP Methods

- [ ] GET for reads (safe, idempotent)
- [ ] POST for creates — returns `200`, not `201` (not idempotent unless Idempotency-Key used)
- [ ] POST for batch reads by IDs (`POST /resources/batch` with `{ "ids": [...] }`)
- [ ] PUT for all updates — full or partial, no PATCH (idempotent)
- [ ] DELETE for removal or disabling (idempotent)
- [ ] Method choice matches safety and idempotency properties

## Pagination

- [ ] Pagination strategy chosen and documented (page/size OR offset/limit OR cursor)
- [ ] Page start index documented (0 or 1)
- [ ] Default page size defined and enforced
- [ ] Maximum page size capped
- [ ] Cursor-based pagination used for large or mutable datasets
- [ ] Pagination metadata returned in first-class `meta.pagination` (not `extra_meta`)

## Filtering

- [ ] Filter parameters documented with types and valid values
- [ ] Multiple filters combine with AND logic by default
- [ ] Filter values parameterized — never interpolated into SQL
- [ ] Complex filtering query language documented (if applicable)

## Sorting

- [ ] Sort format documented (`field:asc` or `+field`)
- [ ] Sortable fields whitelisted — no arbitrary column sorting
- [ ] Default sort order documented
- [ ] If order is fixed business ordering: `sort`/`direction` explicitly rejected with 400, not silently ignored

## Query Collections (sparse-fieldset POST query endpoints)

- [ ] `fields` validated against a whitelisted field tree; default field set defined
- [ ] Fields parser has its own length and nesting-depth caps
- [ ] Filters typed and operator-whitelisted per field; required filters declared in schema
- [ ] Empty `in` array rejected as a violation; "no filter" = key omitted
- [ ] Schema declared via boot-time check (fails at process start, not first request)
- [ ] Collection test calls `CheckSource(sample)` — no selectable-but-always-empty fields
- [ ] Expensive sources gated with `fields.Has(...)` **before** reading, not trimmed after
- [ ] Personalized branches set `Cache-Control: no-store`; token alone never triggers personal reads
- [ ] All violations returned in one 400 bag (`extra_meta.violations`)
- [ ] Projection applied above the cache; `fields` excluded from cache key
- [ ] New filter/field: schema + handler map branch + wire map key in the same commit
- [ ] Empty collection returns `data: []`, not `null`

## Async Operations

- [ ] Long-running operations return 202 with job reference
- [ ] Job status endpoint exists (`GET /jobs/{id}`)
- [ ] Job result endpoint exists (`GET /jobs/{id}/result`)
- [ ] Delivery method chosen: polling or webhook
- [ ] Webhook retry and failure handling documented (if webhook)

## Idempotency

- [ ] Idempotency-Key header required for create operations on critical resources (payment, order)
- [ ] Server enforces uniqueness via DB constraint
- [ ] Duplicate request returns original response, not error

## Versioning

- [ ] Versioning strategy chosen (URL path, header, query param, or none)
- [ ] Breaking changes trigger a version bump
- [ ] Deprecation timeline communicated to consumers
- [ ] At most 2 active versions maintained

## Rate Limiting

- [ ] Rate limits defined and documented
- [ ] 429 status returned when limits exceeded
- [ ] `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset` headers included
- [ ] `Retry-After` header included in 429 responses

## Error Handling

- [ ] All error codes and types documented in error table
- [ ] HTTP status codes used correctly (400 for client error, 401/403 for auth, 404 for not found, 500 for server error)
- [ ] Error `type` is machine-readable constant (`INSUFFICIENT_DEBIT_AMOUNT`)
- [ ] Error `message` is human-readable explanation
- [ ] Service ID included in error envelope for tracing

## Documentation

- [ ] API spec includes: method, URL, headers, request body, response body
- [ ] Field-level documentation with type, required, default, description
- [ ] Error table with status code, internal code, type, description
- [ ] cURL sample provided
- [ ] Authentication requirements documented

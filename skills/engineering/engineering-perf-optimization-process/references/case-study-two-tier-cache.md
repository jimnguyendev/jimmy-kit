# Case Study: Two-Tier Cache Under a Second Writer and Fifteen Instances

This case study illustrates the escalation ladder when the **constraints**, not the traffic
number, decide the order of the steps. The voucher case study climbs the ladder for
throughput; this one climbs it for a different reason — the data has a second writer the
service cannot observe, and the service runs as fifteen instances.

> **Source:** a Go learning backend rebuilt next to a legacy PHP system and run in parallel with
> it (the same origin repo as `reality-gate`'s audit). Design record: the origin repo's
> `docs/architecture/caching-design-vi.md` and ADR-0004 / 0005 / 0036. Numbers are from
> production configuration in 2026-08/09.

## Context

- **Goal:** take the hottest content reads off MySQL — a catalogue detail that ran 7 sequential
  queries per open, a list query with four `EXISTS` sub-queries per filter combination,
  slug → id lookups that crawlers hammer.
- **Three constraints that make the textbook answer wrong:**
  1. **A second writer.** Content is written by the legacy system's admin tooling; the Go
     service never sees a write. Learner data (progress, submissions) is written by **both**
     backends, interleaved.
  2. **Fifteen instances.** A per-instance cache multiplies origin load by 15 on every expiry.
  3. **Thirty minutes of staleness is acceptable** for content — so TTLs can be long enough
     for hit ratio to mean anything.

## Step 0 — ownership decides the contract (before any cache code)

| Data | Writer(s) | Honest cache contract |
|---|---|---|
| Content (test sets, tests, questions, task formats, tags) | legacy admin tooling, unseen | **TTL-only** — stale up to the window, then reload |
| Learner progress, submissions, results, collections | both backends, interleaved | **none** — read the database every request |
| Grading inputs (answer keys, scales) | — | **never** — a stale grade is persisted wrong forever |

The rule that came out of this: with a writer you cannot observe, *every* active invalidation
strategy (write-through, event-driven) is dishonest — the invalidator never fires for the other
writer's changes, and the cache is silently TTL-only anyway, with a false sense of freshness.
The codebase keeps entity/counter cache kinds with write-through invalidation **available but
uncalled**, deliberately, until the legacy writer is gone.

## Architecture

```
Get(key)
  └─ key := "{epoch}:{family}:{key}"          ← epoch read from the shared store every 5 s
  └─ L1 (in-process, W-TinyLFU, bounded)      ← hit: ~100 ns, no network
       miss → singleflight in this instance + double-check L1
  └─ L2 (shared store, one keyspace for all 15 instances)
       hit  → refill L1 with TTL = min(L1 TTL, remaining L2 lifetime)
              past 50 % of lifetime → refresh-ahead in background, behind a cross-instance lock
       miss → loader (database), on a context detached from caller cancel but bounded by its deadline
              error → return error, cache NOTHING
              ok    → write L2 (full TTL, wrapped with absolute expiry) + L1 (TTL − jitter)
```

Every cache lives in a **repository decorator** — handlers, services and workers never import
the cache package. Every family (prefix, TTL, capacity, jitter, negative TTL, scope) is
declared in **one registry**; an invalid declaration panics at boot, an inline key is a review
reject.

## How the ladder applied — in the order the constraints forced

### First: in-process TTL-only (ladder step 3 before step 2)

**Problem:** the list query (4 `EXISTS` + filters) ran on every screen open × filter combination.

**Action:** an in-process W-TinyLFU cache, capacity 1024, maximum TTL 2 min with **negative**
jitter (TTL − random(0, 30 s), never longer than the contract), keyed by a SHA-256 of a
canonical, injective serialisation of *every* query-affecting filter field.

**Why not the shared store first:** the working set fits in memory, a shared-store round trip
on every request would only add latency, and — the deciding point — no invalidation path can
exist, so an in-process TTL-only entry is exactly as correct as a shared one.

### Second: stampede protection (step 4)

Concurrent misses for the same filter share one load (`singleflight`); a second cache check
inside the flight closes the gap between "checked" and "won the flight". Loader errors are
never cached. The winner runs on a context detached from the caller's cancel (one client
pressing stop must not fail the queue) but keeps the caller's deadline; callers without one get
30 s.

### Third: the shared tier — because of instance count, not latency (step 2, late)

**Problem:** coverage grew from 2 read points to 11 families; at 15 instances each expiry sent
15 identical queries to MySQL, and TTLs could not be raised past minutes without a way to
clear.

**Action:** a shared L2 under the L1, entered inside the singleflight after the double-check.
Store failure is indistinguishable from a miss. Four mechanisms keep the two tiers honest:

| Mechanism | Failure mode it removes |
|---|---|
| **TTL clamp** — L2 value carries its absolute expiry; an L1 refill is capped at the *remaining* L2 lifetime | an instance's copy outliving the shared truth: 15 instances serving 15 versions |
| **Negative jitter on L1 only** — L2 is the shared clock, un-jittered | synchronised expiry across instances |
| **Refresh-ahead** past 50 % of lifetime, behind a cross-instance lock (60 s lease) — serve the old value now, one instance reloads | *cache breakdown*: a hot key expires and all 15 instances hit the database together; per-process singleflight cannot help |
| **Negative cache** for slug lookups — "not found" is a stable answer, kept 60 s under its own TTL (registry enforces negative < positive) | *penetration*: crawlers asking for garbage slugs miss 100 % and every miss reaches the database |

TTLs then went to 30 min (2 h for near-static catalogues).

### Fourth: an on-demand clear that reaches every instance

**Problem:** long TTLs are only safe with a way to say "fresh now". Calling a clear endpoint on
one instance leaves fourteen holding the old value; shortening TTL for everyone to serve a rare
clear throws away the hit ratio of every ordinary day.

**Action:** every key is prefixed with the family's **epoch**, a counter in the shared store
each instance re-reads every 5 s. Clear = delete the family's L2 keys, then `INCR` the epoch.
Within 5 s every instance reads and writes a new keyspace; old L1 entries — even ones with 29
minutes left — are unreachable at once. If the shared store is down, the epoch keeps its last
value: the system degrades to "not cleared", never to "request failed". The endpoint is
fail-closed: mounted only when an operator key is configured, accepts only registered
families (a free-form prefix is how a flush wipes a neighbour's keys on a shared store), and
every scan is boxed inside the service's own key prefix.

### A guard, not a step: which types may enter the shared tier

L1 keeps the Go object; L2 must serialise it. A field JSON drops (unexported, or `json:"-"`)
comes back zero from L2 and intact from L1 — **the same key answers differently depending on
which tier served it.** A static check walks each cached type (a sample value can always omit
the very field that would be lost). Two families failed it because their types deliberately
hide routing metadata from the wire shape; they stayed **L1-only**, still under the epoch.

## What was deliberately not cached

| Thing | Why |
|---|---|
| Grading inputs (answer keys, scales) | a wrong grade is persisted forever — hard rule even with cache on |
| Learner state (progress, submissions, results, collections) | the other backend writes it interleaved — any copy can be wrong the next second |
| Anything keyed by user or IP (recents, benefit usage, market resolution) | key space = number of users, hit ratio ≈ 0 |
| List cards the service overlays learner state onto **in place** | an in-process cache hands out a shared pointer; the next request would see the previous user's overlay — cached data is read-only, copy before mutating |
| The submit (write) path | content metadata decides how a submission is persisted; stale here is persisted wrong. Instead: a **request-scoped memo** — no TTL, no sharing between requests — removed 7 duplicated content reads out of ~24 per submit, staleness zero |

## Key design decisions

- **Ownership first, mechanism second.** The whole design is a consequence of three numbers —
  2 writers, 15 instances, 30 min acceptable staleness. Change any one (legacy writer retired,
  2 instances, real-time requirement) and the right design is different.
- **Cache errors are misses; loader errors are never cached.** A 2-second database blip must stay
  a 2-second blip, not become a 30-minute one.
- **A long TTL and an instant clear are not in tension** — TTL is the contract for the natural
  lifecycle, epoch is the operator's escape hatch.
- **Keys carry every result-affecting field.** A missing field is a correctness bug (two requests
  receive each other's answers), not a performance bug.
- **One registry, one metric set.** Eight generic instruments (`cache_requests_total`,
  `cache_loads_total`, `cache_load_duration_seconds`, `cache_evictions_total`, `cache_entries`,
  `cache_capacity`, …) keyed by a `cache=<family>` attribute; a hit rate below ~80 % is the
  signal to resize or re-evaluate a family.

## Lessons for the escalation ladder

1. **There is a step 0 the ladder did not have: who else writes this data?** It decides which
   contracts are honest before any step is chosen.
2. **The ladder's numbering is not an order.** Here step 3 (in-process) came before step 2
   (shared store), and step 2 was justified by instance count, not by store latency.
3. **Per-process singleflight solves stampede inside one instance only.** Across instances the
   tools are refresh-ahead behind a short lock (breakdown) and negative TTL (penetration).
4. **A tiered cache needs two invariants the single-tier one does not:** the lower tier's copy
   never outlives the shared entry (TTL clamp), and the cached type survives serialisation.
5. **Operators need a clear that reaches every instance**, or they will lower TTL for everyone.
6. **Some reads must not be cached at all** — and the list of those is as important as the list
   of families. A request-scoped memo is the honest tool for a write path.

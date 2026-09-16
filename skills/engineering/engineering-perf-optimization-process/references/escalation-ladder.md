# Escalation Ladder

Start at step 1. Move to the next step ONLY when the current step is insufficient AND you have metric proof.

**The numbering is not an order.** Which step comes next is decided by the profile and by the
constraints below, not by the step number: a service with a second writer it cannot observe
takes step 3 before step 2 (see [case study 2](case-study-two-tier-cache.md)); a single-instance
service may never need step 4's cross-instance half.

## Step 0: Who else writes this data?

Answer this before any cache step. It decides which cache contracts are **honest**:

| Writers of the data | Honest contract |
|---|---|
| Only this service | TTL, plus write-through or event-driven invalidation in the same write path |
| Another system too (an admin tool, a legacy backend in parallel run, a batch job) | **TTL-only** with a stated staleness window — your invalidator never fires for their writes |
| Both systems, interleaved, on user-visible state | **do not cache** — read the source every request |
| Inputs to an irreversible write (a grade, a payment) | **never cache** — stale here is persisted wrong forever |

Also count the instances: a per-instance cache multiplies origin load by the instance count on
every expiry, which is what makes steps 2 and 4 necessary at modest traffic.

## Step 1: Fix the query

**When:** Database queries appear in the profile as the dominant cost.

**Actions:**

- Add missing indexes (verify with EXPLAIN)
- Replace N+1 fetch loops with batched queries (`WHERE id = ANY($1)`)
- Use prepared statements for hot-path queries
- Add strict query timeout for hot path (e.g., 50ms) with fallback to stale cache or 503
- Enable connection pooling with bounded pool size

**Metric proof to escalate:** Queries are already optimized (index-only scans, no N+1) but latency target is still not met. Show EXPLAIN output and query latency histogram.

**Rollback:** Indexes can be dropped. Prepared statements can be reverted. Timeout fallback uses feature flag.

## Step 2: Add single-layer cache (Redis)

**When:** Repeated reads of the same data dominate the profile, and the data tolerates staleness.

**Actions:**

- Cache hot-path query results in Redis with TTL
- Add TTL jitter (e.g., base TTL +/- 10%) to avoid synchronized expirations
- Define key format upfront (e.g., `item:{id}`, `feed:{user_id}:{bucket}`)
- Invalidate on write for critical fields only (event-driven, not TTL-only) — **only when this service is the sole writer** (step 0); otherwise TTL-only with a stated staleness window, and an on-demand clear (step 4) instead of a shorter TTL
- Add cache hit rate metrics (must monitor from day one)

**Metric proof to escalate:** Cache hit rate is high (>90%) but Redis round-trip latency (typically 1-3ms) still accounts for a significant portion of p99. Show cache hit rate + Redis latency histogram.

**Rollback:** Feature flag to bypass cache and read directly from DB.

## Step 3: Add in-process L1 cache

**When:** Redis round-trip is the bottleneck despite high hit rate. Data access is read-heavy with predictable hot keys.

**Actions:**

- Add in-process LRU or LFU cache as L1 (e.g., Ristretto, golang-lru)
- L1 serves hot keys in ~100ns vs Redis ~1-3ms
- Keep L1 TTL short (seconds) or use pub/sub invalidation for consistency
- Size L1 to fit in memory budget (Gate 1) — do not cache everything
- Prevent stale write-back: reader nodes should not write to Redis from L1
- Under a shared tier, **clamp** the L1 TTL to the remaining lifetime of the shared entry (store the absolute expiry with the value) — or one instance's copy outlives the shared truth and N instances serve N versions
- Jitter the L1 TTL **downwards only** (TTL − random) so the staleness contract is never exceeded; leave the shared entry un-jittered as the common clock
- Before a type enters a shared tier, check it survives serialisation (fields dropped by JSON come back zero from L2 and intact from L1 — the same key answering differently per tier); types that fail stay in-process only
- Give "not found" answers on caller-supplied keys (slugs, ids) their own **shorter negative TTL** — crawlers asking for garbage otherwise miss 100 % and every miss reaches the database

**Metric proof to escalate:** L1 hit rate is high but p99 still misses target on cache miss path. Show L1 hit rate, miss rate, and latency breakdown for cache-miss requests.

**Rollback:** Feature flag to disable L1 (all reads go to Redis). L1 is purely additive — disabling it only affects latency, not correctness.

## Step 4: Add stampede protection (singleflight)

**When:** Cache miss causes thundering herd — many concurrent requests for the same expired key all hit the database simultaneously.

**Actions:**

- Add `singleflight.Group` per key in-process (deduplicates concurrent fetches within one instance)
- Optionally add distributed lock with short lease (e.g., 2s) for cross-instance deduplication
- First requester fetches from DB, others wait on the singleflight result
- Populate cache asynchronously but ensure first requester still meets p99
- **Across instances, per-process singleflight does not help.** For a hot key that expires everywhere at once (cache breakdown), add **refresh-ahead**: past ~50 % of the entry's lifetime, serve the cached value and reload in the background, with a short cross-instance lock so one instance reloads for the cluster. A failed refresh keeps the old value
- Give operators a **clear that reaches every instance**: prefix keys with a family **epoch** kept in the shared store and re-read every few seconds; a clear deletes the shared keys and bumps the epoch, so every instance's old entries become unreachable at once — no per-instance call, no restart, and long TTLs stop being dangerous

**Metric proof to escalate:** Singleflight resolves stampede, but CPU is now the bottleneck (not I/O). Show CPU profile flamegraph with marshal/unmarshal dominating.

**Rollback:** Feature flag to disable singleflight (requests go directly to cache/DB). Singleflight is purely additive.

## Step 5: Zero-serialization read path

**When:** Flamegraph shows >10% CPU spent on JSON marshal/unmarshal in the hot path. Response format matches storage format.

**Actions:**

- Pre-process data at write time or on pub/sub receive (parse once)
- Store raw bytes in L1 cache, serve directly to HTTP response
- Use callback hooks (e.g., `OnSetLocalCache`) to customize cache entry format per use case
- Avoid re-marshaling on every request

**Metric proof to escalate:** CPU is still the bottleneck despite zero-ser. Show flamegraph with remaining hot spots (lock contention, allocation pressure).

**Rollback:** Feature flag to fall back to standard marshal/unmarshal path.

**Reference implementation:** See `github.com/huykn/distributed-cache` examples/heavy-read-api — demonstrates OnSetLocalCache callback achieving 74K req/s with zero-copy reads (44% throughput gain over direct Redis).

## Step 6: Lock-free patterns and advanced concurrency

**When:** Mutex contention or allocation pressure appears in the profile. Throughput target is >10K req/s per instance.

**Actions:**

- Replace mutex-guarded counters with `atomic.AddInt64`
- Use `atomic.Value` for lock-free read/write of shared data
- Use `sync.Pool` for high-allocation hot paths (only when GC pressure is confirmed)
- Batch counter updates to reduce atomic contention at extreme throughput
- Use channel-based async processing to offload heavy work from hot path

**Metric proof:** This is the last step. If targets are still not met, revisit architecture (horizontal scaling, read replicas, CQRS).

**Rollback:** Each pattern should be behind a feature flag or isolated in its own module.

**Reference implementation:** See `github.com/huykn/distributed-cache` examples/heavy-write-api/poc — demonstrates lock-free atomic pop at 50K req/s per pod with MinuteStore pattern.

**Full case studies:** [Voucher Distribution System](case-study-voucher-system.md) — a real system that progressed through all six steps for throughput; [Two-Tier Cache Under a Second Writer and Fifteen Instances](case-study-two-tier-cache.md) — the same ladder climbed in a different order because of ownership and instance count, with the cross-instance mechanisms (TTL clamp, refresh-ahead, negative cache, epoch clear) worked through.

## Decision Summary

| Step | Trigger condition | Typical throughput range | Complexity added |
|---|---|---|---|
| 0. Ownership | before any cache: who else writes the data, how many instances | any | none — decides which contracts are honest |
| 1. Fix queries | DB queries dominate profile | 0 - 2K RPS | Low |
| 2. Redis cache | Repeated reads, data tolerates staleness | 2K - 10K RPS | Low-Medium |
| 3. L1 cache | Redis round-trip is the bottleneck | 10K - 50K RPS | Medium |
| 4. Singleflight | Thundering herd on cache miss | 10K - 50K RPS | Low |
| 5. Zero-serialization | CPU bound at marshal/unmarshal | 50K - 100K+ RPS | Medium |
| 6. Lock-free patterns | Mutex contention in profile | 50K - 100K+ RPS | High |

**The RPS ranges are indicative, not prescriptive.** The actual trigger is always the profile, not the traffic number. A poorly written 500 RPS service may need step 2. A well-written 20K RPS service may not need step 5.

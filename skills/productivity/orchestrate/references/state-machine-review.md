# State-machine review checklist

Apply to any plan with a lease, retry, lock, queue, idempotency key, outbound call or a
long-running state machine. The root answers every item in the plan before the first Advisor
round; every Advisor round answers it again (`SM-n PASS | FINDING <id> | N/A <reason>`). The list
is what a different-family Advisor found in real plans, so a weaker or same-family reviewer still
asks the questions that mattered.

Origin: the journeys runtime (notification-service, ADR-0022/0023) went through five Codex rounds;
most of its ~20 findings fall into the classes below, and so did the double-send paths found in the
dispatcher plan earlier.

| ID | Question | Typical defect when missed |
|---|---|---|
| SM-1 | Is every write after a claim fenced (`WHERE id AND state AND attempt = claimed`) so a stale worker writes 0 rows and stops? | A worker whose lease expired overwrites the new owner's progress. |
| SM-2 | Does every effect that can be recorded in the database (enqueue, outbox row) commit in the same transaction as the step and checkpoint, with pause/stop checked under the same lock? | A send after pause; a send with no step row; a double send after a crash. |
| SM-3 | For each outbound call: is the request frozen and marked in flight before I/O, and the outcome recorded after? On a crash in between, is a resend allowed only when the receiver dedupes, else parked for a human? | A receiver that does not dedupe gets the call twice. |
| SM-4 | Can the HTTP transport or client library replay the request by itself (idempotent methods, an `Idempotency-Key` header, automatic retries)? Is retry eligibility frozen when the call is admitted, never upgraded by a later config change? | A library retry the plan never counted; a flag flip turns a parked call into a resend. |
| SM-5 | Is ingest idempotent: receipt and every effect in one transaction, a duplicate has no effect, a failure after the receipt rolls it back, an API retry returns the original id? | Two copies of one event each start a run; a 500 after the receipt loses the event. |
| SM-6 | Is there one lock order shared by workers and admin mutations, written down, with a test that interleaves them? | Deadlock between a step transaction and a publish or pause. |
| SM-7 | Are expiry, deadlines and pause checked at the effect, not only at claim? Are deadlines computed from stored timestamps, so a retry gets the same deadline and the reaper restores the right resume state? | A run past its timeout still sends; a retried wait waits twice. |
| SM-8 | Can a config or catalog change race with publish or admission (trust level, a deleted type, a connection flag)? Are the referenced rows locked or snapshotted? | A journey publishes against an event type that changed trust in the same second. |
| SM-9 | Event time: accepted window, events older than the wait start, events in flight during a version change, clock source (database vs process) for "now". | An old event wakes a wait it predates; two clocks disagree by milliseconds in tests. |
| SM-10 | Is every UPDATE/DELETE over a growing table batched on an index, and every stat an SQL aggregate rather than a capped scan? | One unbounded `UPDATE` on stop; stats silently capped at N rows. |
| SM-11 | Volume: are the numbers the owner's (entries per day, open runs, retention), with a budget and a seeded load run, and no machinery beyond them? | Partitions and caches for 10x the real volume; or a 2.7 s query found after 35 packets. |
| SM-12 | Does the packet name one test per crash point and race above (`Test…_PauseBetweenT1AndT2…`), with the interleaving mechanism (closed pool, gate in a fake, lease rewound in SQL)? | The plan is right and the code is not; nothing proves the interleaving. |

A plan that changes an accepted ADR writes a superseding ADR; it never edits the accepted one.

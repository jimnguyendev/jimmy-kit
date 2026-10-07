# Subscription service verification map

The maintained source for proving the client-visible behavior of a course app's subscription service. Read this index before driving the service, then use the matching feature file as the recipe.

## Baseline preconditions

- Start the stack with `make verify-up RUN_ID=$RUN_ID`: API on `127.0.0.1:18080`, PostgreSQL database `subs_verify_$RUN_ID`, topic `subscription.v1.verify-$RUN_ID`, entitlement consumer group `ent-verify-$RUN_ID`.
- Run `./verify/doctor.sh $RUN_ID` and require: commit matches `git rev-parse HEAD`, PostgreSQL version equals the deployed version in `deploy/postgres.version`, migrations at head, topic and consumer group present, clock mode `injected`.
- Sandbox credentials for both stores are present in `.env.verify`; Doctor reports "incomplete coverage" otherwise.
- Never drive an instance this run did not start.

## Driving conventions

- Every request goes through `./verify/call.sh <method> <path> [body-file]`, which adds the run's auth header and prints status and body.
- Store notifications are replayed with `./verify/replay.sh <capture-dir>`, which posts the captured signed bytes and headers unchanged.
- State is read with `./verify/sql.sh "<query>"` (read-only role) and `./verify/topic.sh <key>` (prints key, partition, offset, payload).
- Time moves only through `./verify/clock.sh set <RFC3339>`; Cleanup resets it.

## Proof and skip rules

- Capture the request, the response, the state row before and after, the outbox row, the topic message, and the entitlement read, linked by one ID chain.
- Duplicate deliveries must show no second transition and no second event.
- Record the feature ID and entry point with every artifact under `.jimmy/work/verify-subscriptions/evidence/$RUN_ID/`.
- Report an unreachable path with the command tried and the unmet precondition. A replayed notification is labeled "replay", a sandbox one "genuine".

## Feature entry contract

Each feature file starts with an H1 and one paragraph on the client-visible behavior, then exactly four H2 sections in this order: `Sub-features`, `How to get to it`, `Driving it with <harness>`, `Gotchas`.

## Features

- [Purchase verify](./purchase-verify.md) covers first purchase, repeat verify, and a rejected receipt.
- [Store renewal](./store-renewal.md) covers renewal, duplicate and out-of-order notifications, and recovery by reconciliation.

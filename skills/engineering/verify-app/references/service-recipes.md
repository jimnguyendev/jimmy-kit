# Service, webhook and async recipes

Read this before writing Drive and Evidence for an API, an inbound webhook, a message consumer, or anything whose outcome depends on time.

## Doctor for a service

Each item is a read-only command in the generated skill, and each compares an observed value with a required one:

- Build or commit of the running process matches the checkout.
- The instance, database, topic and consumer group belong to this run (names carry the run ID), not to a shared environment.
- Database engine version equals the deployed version; migrations are at the head the code expects (checksum or version table). Printing both versions without comparing them is not a check.
- Readiness of every process in the flow: API, outbox publisher, consumers.
- Broker topic exists with the expected partitioning; consumer lag is readable.
- Provider configuration for each external caller: credentials present, sandbox environment selected, trust roots or audiences configured.
- Clock mode: real time, or an injected domain clock (see below).

A missing prerequisite ends the Doctor with "incomplete coverage: <what>", never a silent pass.

## Inbound webhooks with signed payloads

A provider's "send test notification" call proves delivery and signature handling only. It usually carries no subscription or order data, so it cannot prove that a renewal, refund or cancellation changes state. Write two separate recipes and label coverage by which one ran:

1. **Genuine sandbox event** — trigger the real event in the provider's sandbox (a sandbox purchase that renews on an accelerated schedule, a test refund) and let it arrive through the configured delivery path.
2. **Replay of captured payloads** — keep the exact signed payload bytes of real sandbox notifications under `testdata/`, plus the provider API responses the handler fetched while processing them. Replay the payload unchanged; re-create only the transport around it:
   - A payload signed inside its own body (a JWS notification) can be posted as captured, as long as the handler accepts its signing date; when it no longer does, the capture is stale and the genuine path is the only proof.
   - A delivery authenticated by a short-lived bearer token (a Pub/Sub push) cannot be replayed with its old headers. Publish the captured message to the verify run's own topic and push subscription, so the platform mints a fresh token that the unchanged verifier checks.
   - The provider API responses reach the handler through the adapter's configured base URL, pointed in the verify environment at a recorded-response server that serves the captured bodies. Doctor checks that this override is active only in the verify environment.

Never make a recipe pass by disabling signature or token verification on the production code path. When verification time matters (certificate validity, token expiry), keep the verification clock separate from the domain clock.

Provider specifics the recipe must state:

- **JWS-signed notifications** (for example App Store Server Notifications V2): verify the outer and nested signatures, the certificate chain against pinned roots, and the app and environment identity; store the raw signed bytes as evidence.
- **Push delivery with bearer tokens** (for example Pub/Sub push): verify signature, issuer, audience, expiry and the sending service account; treat the notification as a pointer and fetch the authoritative state from the provider API.

## Async outcomes

Assert on observables, in order, each with a bounded poll and a timeout message that names what was missing:

1. the handler's response,
2. the state row before and after (version, status, expiry),
3. the outbox or event row committed in the same transaction,
4. the published message (key, partition, offset),
5. the downstream read model or API that the user finally sees.

Correlate them with one ID chain (notification ID → entity ID → event ID) and record it in the evidence. Never use a fixed sleep.

## Duplicates, ordering and failure

A recipe for a stateful flow covers, at minimum:

- the same notification twice, sequentially and concurrently: one transition, one outbox event;
- an older notification after a newer one: no regression of state or expiry;
- a failure inside the ingest transaction: nothing committed, no outbox row, and a retry succeeds;
- a crash after the broker acknowledged a publish but before the outbox row was marked sent: the event may be published again, so prove eventual delivery and exactly one downstream effect per event ID, not exactly one message;
- the same message delivered twice to a consumer: one effect;
- a withheld notification recovered by the reconciliation job.

## Time-dependent states

Expiry, grace periods, retries and reconciliation need an injectable domain clock or a test hook that sets "now" for the run. Document how the recipe moves the clock, and restore it in Cleanup. Do not wait real hours.

## UI on top of a service

When a flow starts on a device (a store purchase sheet), drive the device with the project's device tool (a simulator or emulator controller) and keep the service-side evidence above. Store credentials and sandbox accounts remain prerequisites the Doctor checks.

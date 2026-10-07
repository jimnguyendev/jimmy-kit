# Store renewal

When the store renews a plan, it notifies the service; the service extends the subscription, publishes the change, and the learner keeps access without opening the app.

## Sub-features

- `renewal-extends` moves `expires_at` forward and bumps the version.
- `renewal-duplicate` ignores the same notification delivered twice.
- `renewal-stale` ignores an older notification arriving after a newer one.
- `renewal-reconciled` recovers a renewal whose notification never arrived.

## How to get to it

- The store posts a signed notification to `POST /webhooks/<store>`.
- The reconciliation job queries the store for subscriptions near expiry.

## Driving it with verify scripts

Preconditions:

- Doctor passed for `$RUN_ID`, clock mode `injected`.
- `verify-first` from the purchase feature has run for `u-verify-1`.
- Captured renewal notifications exist at `testdata/captures/renewal-1/` and `testdata/captures/renewal-0-late/`.

- **Renewal** (`renewal-extends`). Run `./verify/replay.sh testdata/captures/renewal-1`. Status `200`; the subscription row moves to version 2 with a later `expires_at`; one new topic message; `GET /entitlements/u-verify-1` shows the new expiry.
- **Duplicate** (`renewal-duplicate`). Run the same replay again. Status `200`, version stays 2, topic offset unchanged.
- **Stale** (`renewal-stale`). Run `./verify/replay.sh testdata/captures/renewal-0-late`. Status `200`, version stays 2, `expires_at` unchanged.
- **Reconciled** (`renewal-reconciled`). Run `./verify/clock.sh set <one hour before expiry>` without replaying the next notification, then `./verify/job.sh reconcile`. The row moves to version 3 from the store API response; one new topic message.

## Gotchas

- A provider "test notification" carries no subscription data and proves only delivery; it does not count for any sub-feature here.
- Signature checks stay on; a replay that fails verification means the capture is stale or the trust roots changed.
- Reset the clock in Cleanup, or the next run starts in the future.

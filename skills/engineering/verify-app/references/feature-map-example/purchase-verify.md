# Purchase verify

After a learner buys a plan in the app, the app sends the store's transaction to the service, which validates it with the store, records the subscription, and grants access the app can read back.

## Sub-features

- `verify-first` records a new subscription and grants access.
- `verify-repeat` accepts the same transaction again without a second transition.
- `verify-rejected` refuses a transaction the store does not confirm.

## How to get to it

- The app calls `POST /subscriptions/verify` right after a purchase completes.
- The app retries the same call when the first response is lost.

## Driving it with verify scripts

Preconditions:

- Doctor passed for `$RUN_ID`.
- Learner `u-verify-1` has an account token from `./verify/call.sh POST /subscriptions/account-token testdata/token-u1.json`.
- A sandbox purchase capture exists at `testdata/captures/purchase-monthly/`.

- **First verify.** Run `./verify/call.sh POST /subscriptions/verify testdata/captures/purchase-monthly/body.json`. Status `200`, body shows `status: active` and an `expires_at`.
- **State and event.** Run `./verify/sql.sh "select status, version, expires_at from subscriptions where user_id='u-verify-1'"` and `./verify/topic.sh <subscription_id>`. One row at version 1, one message keyed by the subscription ID.
- **Access.** Run `./verify/call.sh GET /entitlements/u-verify-1`. Shows the plan with the same `expires_at`.
- **Repeat.** Run the first command again. Status `200`, version still 1, no new topic message.
- **Rejected.** Run `./verify/call.sh POST /subscriptions/verify testdata/captures/tampered/body.json`. Status `422`, no row, no message.

## Gotchas

- The entitlement read lags the event by up to a few seconds; poll with the script's timeout, do not sleep.
- A capture older than the sandbox receipt retention window is rejected by the store; refresh captures when Doctor reports it.
- Repeat proof needs the topic offset before and after, not only the row.

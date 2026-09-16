# Acceptance criteria template (reality gate)

Fill one block per packet / PR. The reviewer reruns every command and pastes output;
executor prose is not evidence.

## Classification

- Change type: `pure-logic` | `seam` | `both`
- Seams touched (tick all): [ ] SQL  [ ] Mongo  [ ] Redis  [ ] gRPC/HTTP client
  [ ] config/env  [ ] response shape  [ ] auth/middleware
- Cost-bearing seam touched? `yes` → AC-007 is required. That is any database read or write,
  any call to another service, and any list/response path — including one you only reordered,
  paged, filtered or joined: a `SELECT *`, a new `ORDER BY`, an added join, or one extra call
  per item changes what a request costs without changing what it returns.
- Behavior change? `yes` → list tests allowed to change + invariant that must hold.
  `no` → test edits forbidden.

## AC-001 — unit (always)

```
go test -race -count=1 ./<packages>
```

## AC-002 — reality evidence (required when any seam is ticked)

Pick at least one. The command must fail when evidence is absent.

(a) Container-backed test, named, verbose:
```
go test -tags integration -count=1 -v -run '^Test<Name>$' ./<package>/
# paste: --- PASS: Test<Name>
```

(b) Replay against a running server:
```
scripts/certify/run.sh --base http://localhost:<port> --legacy <legacy-dev-url> --flows <flow-ids>
# paste: summary line, 0 new diffs
```

(c) Write-path parity: document/row written by new code vs legacy for the same action:
```
<repo-specific parity command>
# paste: diff summary
```

## AC-003 — silent-skip guard

```
INTEGRATION_SKIP_OK= go test -tags integration -count=1 ./<package>/ ; echo exit=$?
# must be exit=0 WITH tests executed, or exit=1 when Docker is down
```

## AC-004 — contract (required when response shape is ticked)

- Golden/replay case added or updated: `testdata/replay/<flow>/<n>.json`
- OpenAPI updated and response validated in handler test.

## AC-005 — new real-run bug (required when the packet fixes one)

- Replay case reproducing the bug added BEFORE the fix; command from AC-002(b) fails on
  base commit and passes on the packet.

## AC-006 — engine parity (required when any container-backed test is the evidence)

The container must be the engine the deployment runs. A green suite on another version is
not evidence — see mechanism 7.

```
scripts/certify/engine-parity.sh --dsn "$DEV_DSN"
# paste: both VERSION() lines; majors must match
```

## AC-007 — cost budget (required when a cost-bearing seam is touched)

State what one typical request costs on each seam the change touches, measured against
REAL-SIZED data (the widest row, the longest list, the largest account — not an invented
fixture). No judgement needed — paste the number, before and after. Which number per seam:
REFERENCE §8 (database read: queries · rows · bytes; list: max page · LIMIT; remote call:
calls per request; response: bytes; write: rows · transaction span).

```
# the real (read-only) database: how wide and how long the path can get
SELECT MAX(LENGTH(<payload column>)), AVG(LENGTH(<payload column>)) FROM <table>;
SELECT <owner>, COUNT(*) FROM <table> GROUP BY <owner> ORDER BY 2 DESC LIMIT 5;

# the number the new code actually spends for one request, in the container test
# (a test that counts queries/bytes/calls, or the driver's counters printed with -v):
go test -tags integration -count=1 -v -run '^Test<Name>CostBudget$' ./<package>/
# paste: queries · rows · bytes read (or calls) for one request, and what that request returned
```

Reviewer rule: cost should sit within one order of magnitude of what is served or done —
bytes read vs bytes returned, calls vs items. A read that pulls 350 KB to serve 30 bytes, or
a loop that spends one query per item, is rejected even when every other AC is green — it is
batched, bounded, projected, split, or precomputed (mechanism 8). If the ratio is deliberate,
the packet says why in one line.

## Reviewer checklist

- [ ] Every AC-002 output pasted, not summarized.
- [ ] No fixture gained a column/field/enum that the real schema lacks.
- [ ] No `strings.Contains(query, ...)` assertions added.
- [ ] Changed expectations in existing tests are each justified in the packet.
- [ ] Any script named in the report exists in git.
- [ ] AC-006 pasted: the container version equals the deployed version.
- [ ] AC-007 pasted: one cost number per seam touched, measured on real-sized data, before and
      after; any wide ratio (read vs served, calls vs items) explained in one line.
- [ ] No query or remote call was introduced inside a loop over request data; no list path
      lost its bound; no large column was added to a SELECT that also sorts, groups or
      de-duplicates.

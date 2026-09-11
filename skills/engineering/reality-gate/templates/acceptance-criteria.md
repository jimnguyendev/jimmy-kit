# Acceptance criteria template (reality gate)

Fill one block per packet / PR. The reviewer reruns every command and pastes output;
executor prose is not evidence.

## Classification

- Change type: `pure-logic` | `seam` | `both`
- Seams touched (tick all): [ ] SQL  [ ] Mongo  [ ] Redis  [ ] gRPC/HTTP client
  [ ] config/env  [ ] response shape  [ ] auth/middleware
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

## Reviewer checklist

- [ ] Every AC-002 output pasted, not summarized.
- [ ] No fixture gained a column/field/enum that the real schema lacks.
- [ ] No `strings.Contains(query, ...)` assertions added.
- [ ] Changed expectations in existing tests are each justified in the packet.
- [ ] Any script named in the report exists in git.

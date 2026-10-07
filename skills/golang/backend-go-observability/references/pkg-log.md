# pkg/log — the project logger

The team's Go services share one logging package, vendored into each repo as `pkg/log` rather than pulled from a private module, so every service builds without extra registry credentials. A fix made in one service's copy is ported to the others by hand.

## Layout

| Package | Role |
|---|---|
| `pkg/log` | the ctx-first `Logger` interface (`Debug`, `Info`, `Warn`, `Error`, `Panic`, `Fatal`, each `(ctx, msg, kv...)`) and batch defaults |
| `pkg/log/zap` | the zap implementation: encoders per environment, the OpenTelemetry bridge, async batching options, caller fields |
| `pkg/log/export` | the exporter interface; `export/signoz` ships OTLP/gRPC to the collector |
| `pkg/log/logctx` | business key/value pairs carried on `ctx` and added to every record |
| `pkg/log/attr` | environment parsing, hostname and severity helpers |
| `pkg/log/trace` | tracer helpers shared with the log bridge |

## Wiring

`internal/logger` is the only place that touches the concrete implementation:

```go
type Logger = applog.Logger   // application code depends on this alias

// New builds the zap logger. With otlpAddr set it ships batches over OTLP/gRPC;
// empty, it writes to a stderr zap core. The returned flush MUST run on exit.
func New(ctx context.Context, env, service, otlpAddr string) (Logger, func(context.Context) error)

func Nop() Logger             // tests and components that must not log
```

`cmd/*/main.go` calls `logger.New(ctx, cfg.AppEnv, cfg.ServiceName, cfg.OTLPLoggerAddr)` once, injects the result through constructors, and defers the flush after the HTTP and gRPC servers have stopped. The batch tunables (records per export, maximum delay, queue size) are named constants in `internal/logger`, so the flush behaviour is visible in one file.

## Rules

- Depend on `logger.Logger`, never on zap types, outside `internal/logger`.
- Pass `ctx` first; a traced `ctx` adds `trace_id` and `span_id`.
- Pass key/value pairs (`"order_id", id`), never a message built with `fmt.Sprintf`. A console path that formats pairs with `Sprintf` prints `%!(EXTRA …)` and loses the fields.
- Put business identifiers that must survive async hops on `logctx`; re-attach them when a goroutine detaches `ctx`. Keep them out of metric labels.
- The request ID middleware only sets the response header; correlation is the trace.
- One logging mechanism per service: no parallel `log/slog` handler, logrus or ad hoc zap logger.

## Common mistakes

| Mistake | Effect | Fix |
|---|---|---|
| Flush not called on shutdown | the last batch never reaches the collector | defer the flush after servers stop |
| `context.Background()` inside a request | the line has no `trace_id`, so it cannot be joined to the request | pass the request `ctx` |
| A new `slog` or zap logger in a package | a second format and pipeline, lines without trace context | inject `logger.Logger` |
| Business IDs in metric labels | unbounded cardinality | keep them on `logctx` and in logs only |

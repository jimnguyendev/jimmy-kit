# Structured Logging Fundamentals


→ See `backend-go-error-handling` skill for the single handling rule.

## Why Structured Logging

Structured logs emit key-value pairs instead of freeform strings. Log management systems (Datadog, Grafana Loki, CloudWatch) can index, filter, and aggregate structured fields — something impossible with `log.Printf` output.

```go
// ✗ Bad — freeform string, impossible to filter by user_id
log.Printf("ERROR: failed to create user %s: %v", userID, err)

// ✓ Good — structured key-value pairs, machine-parseable
lgr.Error(ctx, "user creation failed",
    "user_id", userID,
    "err", err,
)
// JSON output: {"time":"2025-01-15T10:30:00Z","level":"ERROR","msg":"user creation failed","user_id":"u-123","err":"connection refused","trace_id":"4bf9…","span_id":"00f0…"}
```

## Logger Setup

The project logger is the vendored `pkg/log`, built once in `cmd/*/main.go` through `internal/logger.New(ctx, env, service, otlpAddr)` and injected as `logger.Logger`. See [the pkg/log reference](./pkg-log.md).

- **Production / staging:** `OTLP_LOGGER_ADDR` set → JSON zap core plus a batched OTLP/gRPC exporter to the collector
- **Local:** `OTLP_LOGGER_ADDR` empty → stderr zap core, development encoding
- **Tests:** `logger.Nop()`, or a zap observer core when the test asserts on log output

## Log Levels

```go
lgr.Debug(ctx, "cache lookup", "key", cacheKey, "hit", false)
lgr.Info(ctx, "order created", "order_id", orderID, "total", amount)
lgr.Warn(ctx, "rate limit approaching", "current_usage", 0.92, "limit", 1000)
lgr.Error(ctx, "payment failed", "order_id", orderID, "err", err)
```

**Rule of thumb**: if you're unsure between Warn and Error, ask "did the operation succeed?" If yes (even with degradation), use Warn. If no, use Error.

## Cost of Logging

Logging is not free. Each log line costs CPU (serialization), I/O (disk/network), and money (log ingestion/storage in your aggregation platform). The cost scales with volume, which is directly controlled by log level.

- **Debug level in production** can generate millions of log lines per minute in a busy service, overwhelming your log pipeline and inflating costs by 10-100x
- **Info level** is the typical production default — it provides enough visibility without excessive volume
- Debug level SHOULD be disabled in production — use Info level in production and Debug only in development or when actively debugging a specific issue
- For high-throughput services, consider lowering verbosity or adding sampling in your log pipeline so verbose logs do not overwhelm ingestion and storage

## Logging with Context

Every method takes `ctx` first. The zap bridge reads the span from `ctx` to add `trace_id` and `span_id`, and reads `logctx` fields to add business identifiers.

```go
// ✗ Bad — context.Background() drops trace_id/span_id and logctx fields
lgr.Error(context.Background(), "query failed", "err", err)

// ✓ Good — the request context carries the span and logctx fields
lgr.Error(ctx, "query failed", "err", err)
```

## Business Identifiers via `logctx`

Correlate a request through its trace; do not add a request-ID field to every line (the request ID middleware only sets the response header). Use `logctx` for business identifiers that must stay on every line, including after an async hop:

```go
ctx = logctx.With(ctx, "session_id", sessionID, "response_id", responseID)
lgr.Info(ctx, "answer scored", "score", score)
// Output includes: "trace_id", "span_id", "session_id", "response_id", "score"
```

Rules: `logctx.With` takes alternating string keys and values (an odd trailing element is dropped); it is copy-on-write, so fan-out is safe; when a goroutine detaches `ctx`, re-attach both the span context and `logctx.Fields(parent)`; never use these values as metric labels.

## Converging on One Logger

A service that mixes zap, logrus, zerolog or `log/slog` calls moves every call to the injected `logger.Logger`:

```go
// Before: zap.L().Info("order created", zap.String("order_id", id))
// Before: slog.InfoContext(ctx, "order created", "order_id", id)
// After:
lgr.Info(ctx, "order created", "order_id", id)
```

Do not wrap `pkg/log` in a `log/slog` handler or add a second logger "for convenience": two mechanisms mean two formats, two pipelines and lines that lose trace context.

## Common Logging Mistakes

```go
// ✗ Bad — errors MUST be either logged OR returned, NEVER both (single handling rule violation)
if err != nil {
    s.lgr.Error(ctx, "query failed", "err", err)
    return fmt.Errorf("query: %w", err) // error gets logged twice up the chain
}

// ✓ Good — return with context, log at the top level
if err != nil {
    return fmt.Errorf("querying users: %w", err)
}

// ✗ Bad — NEVER log PII (emails, SSNs, passwords, tokens)
lgr.Info(ctx, "user logged in", "email", user.Email, "ssn", user.SSN)

// ✓ Good — log identifiers, not sensitive data
lgr.Info(ctx, "user logged in", "user_id", user.ID)
```

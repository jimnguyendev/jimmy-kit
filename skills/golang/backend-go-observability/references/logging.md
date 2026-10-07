# Structured Logging Fundamentals


→ See `backend-go-error-handling` skill for the single handling rule.

## Why Structured Logging

Structured logs emit key-value pairs instead of freeform strings. Log management systems (Datadog, Grafana Loki, CloudWatch) can index, filter, and aggregate structured fields — something impossible with `log.Printf` output.

```go
// ✗ Bad — freeform string, impossible to filter by user_id
log.Printf("ERROR: failed to create user %s: %v", userID, err)

// ✓ Good — structured key-value pairs, machine-parseable
logger.ErrorContext(ctx, "user creation failed",
    "user_id", userID,
    "err", err,
)
// JSON output: {"time":"2025-01-15T10:30:00Z","level":"ERROR","msg":"user creation failed","user_id":"u-123","err":"connection refused","request_id":"req-abc-123"}
```

## Logger Setup

Build one `*slog.Logger` in `cmd/*/main.go` and inject it (or a small project-owned interface wrapping it) through constructors.

- **Production:** `slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{Level: slog.LevelInfo})`, wrapped by the request ID handler and bridged to OpenTelemetry for OTLP export
- **Development:** `slog.NewTextHandler(os.Stderr, &slog.HandlerOptions{Level: slog.LevelDebug})` for human-readable output
- **Testing:** a handler writing to `io.Discard`, or to a buffer the test asserts on

## Log Levels

```go
logger.DebugContext(ctx, "cache lookup", "key", cacheKey, "hit", false)
logger.InfoContext(ctx, "order created", "order_id", orderID, "total", amount)
logger.WarnContext(ctx, "rate limit approaching", "current_usage", 0.92, "limit", 1000)
logger.ErrorContext(ctx, "payment failed", "order_id", orderID, "err", err)
```

**Rule of thumb**: if you're unsure between Warn and Error, ask "did the operation succeed?" If yes (even with degradation), use Warn. If no, use Error.

## Cost of Logging

Logging is not free. Each log line costs CPU (serialization), I/O (disk/network), and money (log ingestion/storage in your aggregation platform). The cost scales with volume, which is directly controlled by log level.

- **Debug level in production** can generate millions of log lines per minute in a busy service, overwhelming your log pipeline and inflating costs by 10-100x
- **Info level** is the typical production default — it provides enough visibility without excessive volume
- Debug level SHOULD be disabled in production — use Info level in production and Debug only in development or when actively debugging a specific issue
- For high-throughput services, consider lowering verbosity or adding sampling in your log pipeline so verbose logs do not overwhelm ingestion and storage

## Logging with Context

Always use the `*Context` variants (or a project interface whose methods take `ctx` first). The context carries the request ID and the active span, which the handler and the OTel bridge turn into fields.

```go
// ✗ Bad — context.Background() loses request ID and trace context
logger.ErrorContext(context.Background(), "query failed", "err", err)

// ✓ Good — request context carries request_id, trace_id, span_id
logger.ErrorContext(ctx, "query failed", "err", err)
```

## Request-Scoped Attributes via Request ID

Prefer request ID middleware plus a handler wrapper over passing child loggers around. Inject the ID into `ctx` at every entry point (HTTP middleware, gRPC interceptor, message consumer) and let the handler add it to each record:

```go
// HTTP middleware
ctx := WithRequestID(r.Context(), requestIDFrom(r))
next.ServeHTTP(w, r.WithContext(ctx))

// Downstream calls need no manual field
logger.InfoContext(ctx, "order processed", "order_id", orderID)
// Output: {"request_id":"req-abc-123", "msg":"order processed", "order_id":"o-456"}
```

## Migrating to One Logger

If a service mixes Zap, Logrus, zerolog and slog, converge on `log/slog` (or the one wrapper the team mandates):

```go
// Before: zap.L().Info("order created", zap.String("order_id", id))
// Before: logrus.WithField("order_id", id).Info("order created")
// After:
logger.InfoContext(ctx, "order created", "order_id", id)
```

Add the request ID middleware and the OTel bridge, then remove the old logger dependencies once nothing imports them.

## Common Logging Mistakes

```go
// ✗ Bad — errors MUST be either logged OR returned, NEVER both (single handling rule violation)
if err != nil {
    s.logger.ErrorContext(ctx, "query failed", "err", err)
    return fmt.Errorf("query: %w", err) // error gets logged twice up the chain
}

// ✓ Good — return with context, log at the top level
if err != nil {
    return fmt.Errorf("querying users: %w", err)
}

// ✗ Bad — NEVER log PII (emails, SSNs, passwords, tokens)
logger.InfoContext(ctx, "user logged in", "email", user.Email, "ssn", user.SSN)

// ✓ Good — log identifiers, not sensitive data
logger.InfoContext(ctx, "user logged in", "user_id", user.ID)
```

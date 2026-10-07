---
name: backend-go-observability
description: "Golang everyday observability — the always-on signals in production. Covers structured logging with log/slog behind a project-owned logger interface, Prometheus metrics, OpenTelemetry distributed tracing, continuous profiling with pprof/Pyroscope, server-side RUM event tracking, alerting, and Grafana dashboards. Use when instrumenting Go services for production monitoring, setting up metrics or alerting, adding OpenTelemetry tracing, correlating logs with traces, exporting logs and traces over OTLP, adding observability to new features, or implementing GDPR/CCPA-compliant tracking with Customer Data Platforms (CDP). Not for temporary deep-dive performance investigation (→ See golang-benchmark and golang-performance skills)."
user-invocable: true
license: MIT
compatibility: Designed for Claude Code or similar AI coding agents, and for projects using Golang.
metadata:
  author: jimnguyendev
  version: "1.2.0"
allowed-tools: Read Edit Write Glob Grep Bash(go:*) Bash(golangci-lint:*) Bash(git:*) Agent WebFetch WebSearch AskUserQuestion
---

**Persona:** You are a Go observability engineer. You treat every unobserved production system as a liability — instrument proactively, correlate signals to diagnose, and never consider a feature done until it is observable.

**Modes:**

- **Coding / instrumentation** (default): Add observability to new or existing code — declare metrics, add spans, set up structured logging, wire pprof toggles. Follow the sequential instrumentation guide.
- **Review mode** — reviewing a PR's instrumentation changes. Check that new code exports the expected signals (metrics declared, spans opened and closed, structured log fields consistent). Sequential.
- **Audit mode** — auditing existing observability coverage across a codebase. Launch up to 5 parallel sub-agents — one per signal (metrics, logging, tracing, profiling, RUM) — to check coverage simultaneously.

> **Community default.** A company skill that explicitly supersedes `backend-go-observability` skill takes precedence.

# Go Observability Best Practices

Observability is the ability to understand a system's internal state from its external outputs. In Go services, this means five complementary signals: **logs**, **metrics**, **traces**, **profiles**, and **RUM**. Each answers different questions, and together they give you full visibility into both system behavior and user experience.

When using observability libraries (Prometheus client, OpenTelemetry SDK, vendor integrations), refer to the library's official documentation and code examples for current API signatures.

## Best Practices Summary

1. **Log through one project-owned logger interface** — `log/slog` by default, or the team's existing wrapper if one is mandated — bridged to OpenTelemetry. Do NOT mix logging libraries in one service
2. **Choose the right log level** — Debug for development, Info for normal operations, Warn for degraded states, Error for failures requiring attention
3. **Log with context** — pass `ctx` to every log call (`slog.InfoContext`, or `logger.Info(ctx, ...)` on the project interface) so the request ID and trace context travel automatically
4. **Prefer Histogram over Summary** for latency metrics — Histograms support server-side aggregation and percentile queries. Every HTTP endpoint MUST have latency and error rate metrics.
5. **Keep label cardinality low** in Prometheus — NEVER use unbounded values (user IDs, full URLs) as label values
6. **Track percentiles** (P50, P90, P99, P99.9) using Histograms + `histogram_quantile()` in PromQL
7. **Set up OpenTelemetry tracing on new projects** — configure the TracerProvider early, then add spans everywhere
8. **Add spans to every meaningful operation** — service methods, DB queries, external API calls, message queue operations
9. **Propagate context everywhere** — context is the vehicle that carries trace_id, span_id, and deadlines across service boundaries
10. **Enable profiling via environment variables** — toggle pprof and continuous profiling on/off without redeploying
11. **Correlate signals** — inject trace_id into logs, use exemplars to link metrics to traces
12. **A feature is not done until it is observable** — declare metrics, add proper logging, create spans
13. **Use [awesome-prometheus-alerts](https://samber.github.io/awesome-prometheus-alerts/) as a starting point** for infrastructure and dependency alerting — browse by technology, copy rules, customize thresholds

## Cross-References

See `backend-go-error-handling` skill for the single handling rule. See `backend-go-troubleshooting` skill for using observability signals to diagnose production issues. See `backend-go-security` skill for protecting pprof endpoints and avoiding PII in logs. See `backend-go-context` skill for propagating trace context across service boundaries. See `promql-cli` skill for querying and exploring PromQL expressions against Prometheus from the CLI.

## The Five Signals

| Signal | Question it answers | Tool | When to use |
| --- | --- | --- | --- |
| **Logs** | What happened? | `log/slog` + OTel bridge | Discrete events, errors, audit trails |
| **Metrics** | How much / how fast? | Prometheus client | Aggregated measurements, alerting, SLOs |
| **Traces** | Where did time go? | OpenTelemetry | Request flow across services, latency breakdown |
| **Profiles** | Why is it slow / using memory? | pprof, Pyroscope | CPU hotspots, memory leaks, lock contention |
| **RUM** | How do users experience it? | PostHog, Segment | Product analytics, funnels, session replay |

## Detailed Guides

Each signal has a dedicated guide with full code examples, configuration patterns, and cost analysis:

- **[Structured Logging Fundamentals](references/logging.md)** — Why structured logging matters for log aggregation at scale. Covers log levels (Debug/Info/Warn/Error) and when to use each, cost of logging, context propagation, and common mistakes. Also covers the project-owned logger interface, request ID middleware, and migrating to one logger.

- **[Metrics Collection](references/metrics.md)** — Prometheus client setup and the four metric types (Counter for rate-of-change, Gauge for snapshots, Histogram for latency aggregation). Deep dive: why Histograms beat Summaries (server-side aggregation, supports `histogram_quantile` PromQL), naming conventions, the PromQL-as-comments convention (write queries above metric declarations for discoverability), production-grade PromQL examples, multi-window SLO burn rate alerting, and the high-cardinality label problem (why unbounded values like user IDs destroy performance).

- **[Distributed Tracing](references/tracing.md)** — When and how to use OpenTelemetry SDK to trace request flows across services. Covers spans (creating, attributes, status recording), `otelhttp` middleware for HTTP instrumentation, error recording with `span.RecordError()`, trace sampling (why you can't collect everything at scale), propagating trace context across service boundaries, and cost optimization.

- **[Profiling](references/profiling.md)** — On-demand profiling with pprof (CPU, heap, goroutine, mutex, block profiles) — how to enable it in production, secure it with auth, and toggle via environment variables without redeploying. Continuous profiling with Pyroscope for always-on performance visibility. Cost implications of each profiling type and mitigation strategies.

- **[Real User Monitoring](references/rum.md)** — Understanding how users actually experience your service. Covers product analytics (event tracking, funnels), Customer Data Platform integration, and critical compliance: GDPR/CCPA consent checks, data subject rights (user deletion endpoints), and privacy checklist for tracking. Server-side event tracking (PostHog, Segment) and identity key best practices.

- **[Alerting](references/alerting.md)** — Proactive problem detection. Covers the four golden signals (latency, traffic, errors, saturation), [awesome-prometheus-alerts](https://samber.github.io/awesome-prometheus-alerts/) as a rule library with ~500 ready-to-use rules by technology, Go runtime alerts (goroutine leaks, GC pressure, OOM risk), severity levels, and common mistakes that break alerting (using `irate` instead of `rate`, missing `for:` duration to avoid flapping).

- **[Grafana Dashboards](references/dashboards.md)** — Prebuilt dashboards for Go runtime monitoring (heap allocation, GC pause frequency, goroutine count, CPU). Explains the standard dashboards to install, how to customize them for your service, and when each dashboard answers a different operational question.

## Correlating Signals

Signals are most powerful when connected. A trace_id in your logs lets you jump from a log line to the full request trace. An exemplar on a metric links a latency spike to the exact trace that caused it.

### Logs + Traces: slog + OpenTelemetry

Bridge `log/slog` to OpenTelemetry (for example with the `otelslog` bridge) so every record emitted with a span-carrying `ctx` includes `trace_id` and `span_id`. Any OTLP backend (SigNoz, Grafana Tempo/Loki, Jaeger) can then jump from a log line to its trace.

```go
// trace_id/span_id are attached because ctx carries the active span
logger.InfoContext(ctx, "order created", "order_id", orderID)
```

Inject a request ID once at each entry point (HTTP middleware, gRPC interceptor, message consumer) and read it back in a `slog.Handler` wrapper, so no call site adds it by hand:

```go
type requestIDKey struct{}

func WithRequestID(ctx context.Context, id string) context.Context {
    return context.WithValue(ctx, requestIDKey{}, id)
}

// handler wrapper: adds request_id to every record whose ctx carries one
func (h ctxHandler) Handle(ctx context.Context, r slog.Record) error {
    if id, ok := ctx.Value(requestIDKey{}).(string); ok {
        r.AddAttrs(slog.String("request_id", id))
    }
    return h.Handler.Handle(ctx, r)
}
```

### Metrics + Traces: Exemplars

```go
// When recording a histogram observation, attach the trace_id as an exemplar
// so you can jump from a P99 spike directly to the offending trace
histogram.WithLabelValues("POST", "/orders").
    Exemplar(prometheus.Labels{"trace_id": traceID}, duration)
```

## Migrating to one logger

If a service mixes Zap, Logrus, zerolog and slog, converge on one project-owned logger interface:

1. Define the interface in one package (for example `internal/platform/log`) and build it on `log/slog` in `cmd/*/main.go`.
2. Inject it through constructors into services, handlers and repositories. No global logger.
3. Replace direct `zap.L()`, `logrus.` and package-level `slog.` calls with context-taking calls on the injected logger.
4. Add request ID middleware at every entry point and the OTel bridge at startup.
5. Remove the old logger dependencies once nothing imports them.

→ See [Structured Logging Fundamentals](references/logging.md) for levels, cost, and common mistakes.

## Definition of Done for Observability

A feature is not production-ready until it is observable. Before marking a feature as done, verify:

- [ ] **Metrics declared** — counters for operations/errors, histograms for latencies, gauges for saturation. Each metric var has PromQL queries and alert rules as comments above its declaration.
- [ ] **Logging is proper** — structured key-value pairs through the project logger, context passed to every log call, request ID middleware active, no PII in logs, errors MUST be either logged OR returned (NEVER both).
- [ ] **Spans created** — every service method, DB query, and external API call has a span with relevant attributes, errors recorded with `span.RecordError()`.
- [ ] **Dashboards and alerts exist** — the PromQL from your metric comments is wired into Grafana dashboards and Prometheus alerting rules. Check [awesome-prometheus-alerts](https://samber.github.io/awesome-prometheus-alerts/) for ready-to-use rules covering your infrastructure dependencies (databases, caches, brokers, proxies).
- [ ] **RUM events tracked** — key business events tracked server-side (PostHog/Segment), identity key is `user_id` (not email), consent checked before tracking.

## Common Mistakes

```go
// ✗ Bad — log AND return (error gets logged multiple times up the chain)
if err != nil {
    s.logger.Error(ctx, "query failed", "err", err)
    return fmt.Errorf("query: %w", err)
}

// ✓ Good — return with context, log once at the top level
if err != nil {
    return fmt.Errorf("querying users: %w", err)
}
```

```go
// ✗ Bad — interpolating values into message (breaks log aggregation grouping)
s.logger.Error(ctx, fmt.Sprintf("[GetUser(ctx, %d)] error: %v", userID, err))

// ✓ Good — static message, structured fields
s.logger.Error(ctx, "get user failed", "user_id", userID, "err", err)
```

```go
// ✗ Bad — not passing request context (request ID and trace context lost)
s.logger.Info(context.Background(), "order created", "order_id", id)

// ✓ Good — pass the request context through
s.logger.Info(ctx, "order created", "order_id", id)
```

```go
// ✗ Bad — high-cardinality label (unbounded user IDs)
httpRequests.WithLabelValues(r.Method, r.URL.Path, userID).Inc()

// ✓ Good — bounded label values only
httpRequests.WithLabelValues(r.Method, routePattern).Inc()
```

```go
// ✗ Bad — not passing context to DB (breaks trace propagation)
result, err := db.Query("SELECT ...")

// ✓ Good — context flows through, trace continues
result, err := db.QueryContext(ctx, "SELECT ...")
```

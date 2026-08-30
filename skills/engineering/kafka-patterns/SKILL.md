---
name: kafka-patterns
description: >
  Practical Kafka patterns for production systems: partition sizing, large messages,
  consumer lag, long-running tasks, request-reply over Kafka, dual-write consistency,
  exactly-once semantics, and message ordering — each with problem context, solutions,
  trade-offs, and configuration notes. Use for Kafka architecture decisions, event-driven
  design, or topics like: how many partitions, max.message.bytes, Burrow lag monitoring,
  rebalance issues, max.poll.interval.ms, session.timeout.ms, message pool / return address
  patterns, transactional outbox, CDC with Debezium, Kafka transactions, idempotent
  consumers, at-least-once guarantees, partial vs total order, and distributed locking.
user-invocable: false
license: MIT
compatibility: Designed for Claude Code or similar AI coding agents.
metadata:
  author: jimnguyendev
  version: "1.0.0"
allowed-tools: Read Glob Grep Agent
---

# Kafka Problems & Patterns

Production-ready patterns for 8 common Kafka / Event-Driven Architecture problems.
Synthesized from the "Problems & Patterns" series by Ronin Engineer (roninhub.com).

## How to use this skill

1. Identify which topic the user is asking about using the routing table below.
2. Read the matching reference file with `view` tool **before** answering.
3. For cross-cutting questions (e.g., exactly-once + ordering), read multiple files.
4. When the user asks for diagrams, use the visualizer tool to illustrate architecture flows.

## Topic routing

| Trigger keywords | Reference file | Topic |
|-----------------|----------------|-------|
| partition count, how many partitions, throughput sizing, repartition | `references/01-topic-width.md` | Partition Sizing |
| large message, file over 1MB, max.message.bytes, external storage | `references/02-large-message.md` | Large Messages |
| consumer lag, message lag, monitoring, Burrow, lag spikes | `references/03-message-lag.md` | Message Lag |
| long-running task, rebalance, poll timeout, pipeline pattern | `references/04-long-running-task.md` | Long-running Tasks |
| request-reply, two-way communication, message pool, return address | `references/05-request-reply.md` | Request & Reply |
| dual write, outbox, CDC, Debezium, DB + Kafka consistency | `references/06-dual-write.md` | Dual Write |
| exactly-once, idempotent consumer, deduplication, at-least-once | `references/07-exactly-once.md` | Exactly-Once |
| message ordering, partial order, key-based routing, distributed lock | `references/08-order-of-messages.md` | Message Ordering |

If the question doesn't clearly match one topic, scan the trigger keywords above and pick the best fit. For general Kafka architecture reviews, read multiple files as needed.

## Gotchas

- Kafka only supports **increasing** partition count — you cannot decrease it without creating a new topic and migrating data. This affects nearly every sizing decision.
- Producer key hashing is **not consistent across partition count changes** — adding partitions means records with the same key may land on a different partition than before.
- There is **no transaction spanning both a database and a message broker**. This is the root cause of the dual-write problem and affects many patterns in this knowledge base.
- `enable.auto.commit=true` in Kafka means the consumer commits offsets **periodically in the background**, not immediately after processing. This provides at-least-once semantics only when combined with proper error handling.
- Physical clocks are unreliable for ordering in distributed systems. Use Kafka partition ordering, sequence numbers, or logical clocks instead.

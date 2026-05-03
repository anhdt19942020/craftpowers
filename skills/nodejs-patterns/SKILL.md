---
name: nodejs-patterns
description: "Use when building Node.js applications — covers async patterns, error handling, streams, graceful shutdown, performance, caching, profiling, logging, testing, modules, TypeScript type stripping, environment config. Activates on: Node.js, Express, Fastify, Koa, Hapi, NestJS, async/await, streams, pipeline, EventEmitter, worker threads, piscina, pino, node:test, graceful shutdown, close-with-grace, lru-cache, async-cache-dedupe, type stripping, ESM, CommonJS."
phase: BUILD
---

# Node.js Patterns

Best practices for building robust, performant, and maintainable Node.js applications. From Matteo Collina (Fastify creator, Node.js TSC member).

## When to Use

Use this skill whenever you are dealing with Node.js code to obtain domain-specific knowledge.

## TypeScript with Type Stripping

When writing TypeScript for Node.js, use **type stripping** (Node.js 22.6+) instead of build tools like ts-node or tsx. Type stripping runs TypeScript directly by removing type annotations at runtime without transpilation.

Key requirements for type stripping compatibility:
- Use `import type` for type-only imports
- Use const objects instead of enums
- Avoid namespaces and parameter properties
- Use `.ts` extensions in imports

See [rules/typescript.md](rules/typescript.md) for complete configuration and examples.

## Common Workflows

**Graceful shutdown**: Register signal handlers (SIGTERM/SIGINT) → stop accepting new work → drain in-flight requests → close external connections (DB, cache) → exit with appropriate code. See [rules/graceful-shutdown.md](rules/graceful-shutdown.md).

**Error handling**: Define a shared error base class → classify errors (operational vs programmer) → add async boundary handlers → propagate typed errors through the call stack → log with context before responding or crashing. See [rules/error-handling.md](rules/error-handling.md).

**Diagnosing flaky tests**: Isolate the test with `--test-only` → check for shared state or timer dependencies → inspect async teardown order → add retry logic as a temporary diagnostic step → fix root cause. See [rules/flaky-tests.md](rules/flaky-tests.md).

**Diagnosing stuck processes/tests** (`node --test` hangs, "process did not exit", CI timeout, open handles): isolate file/test → run with explicit timeout/reporter → inspect handles via `why-is-node-running` (`SIGUSR1`) → patch deterministic teardown in resource-creation scope → rerun isolated + full suite until stable. See [rules/stuck-processes-and-tests.md](rules/stuck-processes-and-tests.md).

**Profiling a slow path**: Reproduce under realistic load → capture a CPU profile with `--cpu-prof` → identify hot functions → check for stream backpressure or unnecessary serialisation → validate improvement with a benchmark. See [rules/profiling.md](rules/profiling.md) and [rules/performance.md](rules/performance.md).

## High-priority Activation Checklist (Streams + Caching)

When the task mentions **CSV**, **ETL**, **ingestion pipelines**, **large file processing**, **backpressure**, **repeated lookups**, or **deduplicating concurrent async calls**, explicitly apply this checklist:

1. Use `await pipeline(...)` from `node:stream/promises` (prefer this over chained `.pipe()`).
2. Include at least one explicit `async function*` transform when data is being transformed in-stream.
3. Choose a cache strategy when repeated work appears:
   - `lru-cache` for bounded in-memory reuse in a single process.
   - `async-cache-dedupe` for async request deduplication / stale-while-revalidate behavior.
4. Show where backpressure is handled (implicitly via `pipeline()` or explicitly via `drain`).

## Reference Guide

| Topic | Reference | Load When |
|-------|-----------|-----------|
| Async patterns | `rules/async-patterns.md` | async/await, Promise, concurrency |
| Error handling | `rules/error-handling.md` | Error classes, try-catch, unhandled rejections |
| Streams | `rules/streams.md` | Readable, Writable, Transform, pipeline |
| Graceful shutdown | `rules/graceful-shutdown.md` | Signal handling, cleanup, health checks |
| Performance | `rules/performance.md` | Event loop, worker threads, connection pooling |
| Caching | `rules/caching.md` | LRU cache, async-cache-dedupe, Redis |
| Profiling | `rules/profiling.md` | Flame graphs, autocannon, benchmarking |
| Logging | `rules/logging.md` | Pino, transports, redaction |
| Testing | `rules/testing.md` | node:test, mocking, snapshots |
| Modules | `rules/modules.md` | ESM, CommonJS, dynamic imports |
| Flaky tests | `rules/flaky-tests.md` | Race conditions, port conflicts, CI flakiness |
| Stuck processes | `rules/stuck-processes-and-tests.md` | Hanging tests, open handles, diagnostics |
| TypeScript | `rules/typescript.md` | Type stripping, tsconfig, file extensions |
| Environment | `rules/environment.md` | --env-file, env-schema, secrets |
| Node modules | `rules/node-modules-exploration.md` | Navigating node_modules, debugging resolution |

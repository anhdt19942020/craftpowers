---
name: stuck-processes-and-tests
description: Diagnosing Node.js processes that do not exit and tests that get stuck
---

# Diagnosing Stuck Node.js Processes and Hanging Tests

## Activation Triggers

Use this rule when prompts/logs include any of:
- "`node --test` hangs" / "test run never exits"
- "CI timed out" after tests appear done
- "process is still running" / "did not exit cleanly"
- "open handles" / "active handles"
- "passes alone, hangs in full suite"

## Non-negotiable Checklist (all 5 required)

1. **Isolate first**: reproduce with one file, then one test name.
2. **Fail fast**: run with explicit timeout + reporter so hangs produce location context.
3. **Capture handles**: run `why-is-node-running` and record the reported handle owner.
4. **Patch teardown in the same scope that created the resource** (`t.after(...)`, await close/terminate/disconnect).
5. **Verify stability**: repeat isolated test many times, then run full suite.

Do **not** mark the issue fixed unless step 5 passes.

## Command Path (run in order)

```bash
# 1) Reproduce full command with fail-fast settings
node --test --test-reporter=spec --test-timeout=15000

# 2) Isolate file, then test name
node --test --test-timeout=15000 path/to/file.test.ts
node --test --test-timeout=15000 --test-name-pattern="should close resources" path/to/file.test.ts

# 3) Dump active handles when hung
node --import why-is-node-running/include --test path/to/file.test.ts
# in another shell, send SIGUSR1 to printed PID
kill -SIGUSR1 <pid>

# 4) Stress rerun isolated repro
for i in {1..30}; do
  timeout 30s node --test path/to/file.test.ts || { echo "failed on run $i"; break; }
done
```

### `why-is-node-running` Install Note

- ESM / modern Node: `npm i -D why-is-node-running`
- older CommonJS projects: `npm i -D why-is-node-running@v2`

Use it for diagnostics only; gate noisy output behind an environment flag in CI.

## High-probability Root Causes

- HTTP server started but never closed (`server.close()` not awaited)
- `setInterval` left running (or timer not `unref()`ed when appropriate)
- DB/Redis/Kafka clients not disconnected
- worker threads, child processes, or message channels left alive
- file watchers / readline interfaces still open
- unresolved promises from fire-and-forget async code
- teardown hooks that throw before cleanup completes

## Integrated Fix Example

**Symptom:** CI times out; local full-suite run hangs after most tests pass.

### Bad (common leak)

```typescript
it('serves requests', async () => {
  const server = await startServer({ port: 0 });
  const id = setInterval(() => {}, 1000);
  // test body...
  // no deterministic teardown
});
```

### Good (deterministic teardown)

```typescript
import { once } from 'node:events';

it('serves requests', async (t) => {
  const server = await startServer({ port: 0 });
  const id = setInterval(() => {}, 1000);

  t.after(async () => {
    clearInterval(id);
    server.close();
    await once(server, 'close');
  });

  // test body...
});
```

## Definition of Done

- Isolated repro passes repeatedly (recommended: 30 runs) with no hangs
- Full `node --test` run exits with code 0
- CI completes with no timeout
- `why-is-node-running` shows no unexpected leftover handles

## Related Rules

- [flaky-tests.md](flaky-tests.md)
- [testing.md](testing.md)
- [graceful-shutdown.md](graceful-shutdown.md)

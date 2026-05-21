---
id: SHARED-SESSION-ACROSS-WORKERS
severity: HIGH
applies_to: all
---

# Shared Session Across Workers

## Intent

Multiple concurrent workers read the same `storageState` file or share a browser context. When one worker's action invalidates the session (e.g., platform detects concurrent access), all workers fail simultaneously or worse — produce race conditions.

## Search patterns

- Same `storageState` path used by multiple worker configs
- `context.storageState` loaded from shared file without copy
- No worker-specific session isolation
- Browser context shared across async operations on different accounts

## Fix

One session file per worker, copy on load:
```typescript
const workerSession = `sessions/worker-${workerId}.json`;
await fs.copyFile(baseSession, workerSession);
const context = await browser.newContext({ storageState: workerSession });
```

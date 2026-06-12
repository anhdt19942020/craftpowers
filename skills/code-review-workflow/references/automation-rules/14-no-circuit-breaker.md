---
id: NO-CIRCUIT-BREAKER
severity: MEDIUM
applies_to: all
---

# No Circuit Breaker

## Intent

Automation retries failed operations indefinitely. If the platform returns 403/429 (rate limit, account blocked), continued retries escalate to permanent account ban or IP block.

## Search patterns

- Retry loop with no error rate tracking
- No max retry count per account
- No backoff between retries
- No account-level pause after consecutive failures
- Missing 403/429 detection and handling

## Fix

```typescript
const MAX_CONSECUTIVE_FAILURES = 3;
const COOLDOWN_MS = 30 * 60 * 1000; // 30 minutes

async function withCircuitBreaker(accountId: string, operation: () => Promise<void>) {
  const failures = await getFailureCount(accountId);
  if (failures >= MAX_CONSECUTIVE_FAILURES) {
    const lastFailure = await getLastFailureTime(accountId);
    if (Date.now() - lastFailure < COOLDOWN_MS) {
      throw new CircuitOpenError(`Account ${accountId} paused — ${failures} consecutive failures`);
    }
    await resetFailureCount(accountId); // Cooldown passed, try again
  }
  try {
    await operation();
    await resetFailureCount(accountId);
  } catch (error) {
    await incrementFailureCount(accountId);
    throw error;
  }
}
```

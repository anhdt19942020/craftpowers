---
id: RETRY-WITHOUT-STATUS-CHECK
severity: CRITICAL
applies_to: all
---

# Retry Without Status Query

## Intent

On network timeout during topup, automation retries immediately without checking if the first attempt succeeded. If the platform processed the first request, the retry creates a duplicate transaction — double charge.

## Search patterns

- `catch` block containing retry logic without querying transaction status first
- `try { topup() } catch { topup() }` pattern
- Retry loop with no `checkTransactionStatus()` before re-attempt
- Missing status API call between timeout and retry

## Fix

On timeout, ALWAYS query platform for transaction status before retry:

```typescript
try {
  await executeTopup(account, amount);
} catch (error) {
  if (isTimeoutError(error)) {
    const status = await queryTransactionStatus(account, txRef);
    if (status === 'NOT_FOUND') {
      await executeTopup(account, amount); // Safe to retry
    } else if (status === 'SUCCESS') {
      return { success: true, cached: true }; // Already processed
    } else {
      throw new Error(`Ambiguous state: ${status} — manual review required`);
    }
  }
}
```

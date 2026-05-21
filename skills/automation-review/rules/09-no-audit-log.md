---
id: NO-AUDIT-LOG
severity: HIGH
applies_to: all
---

# No Structured Audit Log

## Intent

Financial operations execute without structured logging. When discrepancies appear (wrong amount, missing topup, disputed transaction), there's no audit trail to reconstruct what happened — who, when, how much, what result, what transaction ID.

## Search patterns

- Topup function with no logging call
- `console.log` instead of structured logger
- Log entries missing: operation_id, account_id, amount, result, platform_tx_id
- No log correlation between start and completion of same operation
- No immutable/append-only log storage

## Fix

```typescript
const log = logger.child({ operationId: uuid(), accountId: maskId(account.id) });

log.info('topup.start', { amount, platform: account.platform });

try {
  const result = await executeTopup(page, account, amount);
  log.info('topup.success', {
    amount,
    platformTxId: result.transactionId,
    balanceBefore: result.balanceBefore,
    balanceAfter: result.balanceAfter,
  });
} catch (error) {
  log.error('topup.failed', { amount, error: error.message, screenshot: screenshotPath });
}
```

Required fields per log entry: `operationId`, `accountId` (masked), `amount`, `timestamp`, `result`, `platformTxId`.

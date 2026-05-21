---
id: NO-OPERATION-ID
severity: MEDIUM
applies_to: all
---

# No Operation ID Propagation

## Intent

Log entries for a single topup operation have no correlation ID. When investigating a partial failure (payment sent, confirmation lost), you cannot trace which log lines belong to the same operation.

## Search patterns

- No UUID/correlation ID generated at operation start
- Log entries missing `operationId` field
- No way to filter logs for a single topup attempt
- Error reports without traceable operation reference

## Fix

Generate UUID at operation entry, propagate through all log lines:
```typescript
import { randomUUID } from 'crypto';

async function topup(account: Account, amount: number) {
  const operationId = randomUUID();
  const log = logger.child({ operationId });

  log.info('topup.start', { accountId: account.id, amount });
  // ... all subsequent log.info/error calls include operationId automatically
}
```

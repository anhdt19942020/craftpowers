---
id: NO-CONCURRENT-LOCK
severity: CRITICAL
applies_to: all
---

# No Concurrent Lock

## Intent

Multiple workers can pick the same account/session simultaneously. Both execute topup on the same account → duplicate operation, race condition, or account lockout by the platform.

## Search patterns

- `SELECT * FROM sessions WHERE status = 'available'` without `FOR UPDATE`
- Random session/account selection without locking
- No mutex, semaphore, or distributed lock before account operations
- Parallel workers sharing an account pool without coordination

## Fix

Use atomic row lock for session/account selection:

```sql
-- PostgreSQL
SELECT * FROM sessions
WHERE status = 'available'
ORDER BY last_used ASC
LIMIT 1
FOR UPDATE SKIP LOCKED;
```

Or Redis distributed lock:
```typescript
const lock = await redis.set(`lock:account:${accountId}`, workerId, 'NX', 'EX', 300);
if (!lock) throw new Error('Account locked by another worker');
```

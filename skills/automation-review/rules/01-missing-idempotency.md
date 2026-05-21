---
id: MISSING-IDEMPOTENCY
severity: CRITICAL
applies_to: all
---

# Missing Idempotency Key

## Intent

Topup/payment operation has no deduplication mechanism. If automation retries after a network timeout, the operation executes twice — double topup, double payment, real financial loss.

## Search patterns

- Topup/payment function with no `idempotency_key` parameter or table
- No dedup check before submitting payment form
- `page.click('submit')` in payment flow without prior idempotency check
- Database schema with no `idempotency_keys` table
- No unique constraint on (account_id, amount, timestamp_window)

## Fix

Generate idempotency key before every financial operation:

```typescript
const key = crypto.createHash('sha256')
  .update(`${accountId}:${operationType}:${amount}:${Math.floor(Date.now() / 300000)}`)
  .digest('hex');

const existing = await db.query('SELECT * FROM idempotency_keys WHERE key = $1', [key]);
if (existing.rows.length > 0) {
  return existing.rows[0].response; // Return cached result
}

await db.query('INSERT INTO idempotency_keys (key, locked_at) VALUES ($1, NOW())', [key]);
// ... execute topup ...
await db.query('UPDATE idempotency_keys SET completed_at = NOW(), response = $2 WHERE key = $1', [key, result]);
```

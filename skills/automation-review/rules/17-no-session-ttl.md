---
id: NO-SESSION-TTL
severity: LOW
applies_to: all
---

# No Session TTL / Rotation

## Intent

Sessions are reused indefinitely without rotation. Old sessions accumulate detection signals (cookie age, behavior pattern), increasing ban risk. Platform may also expire sessions server-side without notification.

## Search patterns

- `storageState` files with no timestamp or TTL check
- No session rotation schedule
- No `created_at` or `last_used` tracking for sessions
- Sessions reused for days/weeks without refresh

## Fix

```typescript
const SESSION_TTL_MS = 4 * 60 * 60 * 1000; // 4 hours

async function getSession(accountId: string): Promise<string> {
  const session = await db.query(
    'SELECT * FROM sessions WHERE account_id = $1 AND created_at > NOW() - INTERVAL \'4 hours\'',
    [accountId]
  );
  if (session.rows.length === 0) {
    return await createFreshSession(accountId); // Re-authenticate
  }
  return session.rows[0].state_path;
}
```

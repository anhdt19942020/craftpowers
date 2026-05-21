---
id: RACE-CONDITION
severity_max: HIGH
applies_to: all
---

# Race Condition (TOCTOU)

## Intent

Time-of-check vs time-of-use: read → check → update without atomic lock. Concurrent request intervenes between check and update → double-spend, oversell, infinite coupon redemption.

## Search patterns

- `SELECT balance ... then UPDATE balance` without DB locking
- Coupon: `SELECT usage_count ... if < max ... UPDATE` without lock
- Inventory: `SELECT stock ... if > 0 ... UPDATE stock` without `FOR UPDATE`
- Any read-check-write on financial/inventory data

## L1-L4 reasoning

L1 triggers concurrent requests. Flag if shared state (balance, inventory, quota) updated via read-check-write without atomic operation or row lock.

## Fix

- Atomic DB operations: `UPDATE wallets SET balance = balance - ? WHERE user_id = ? AND balance >= ?`
- `SELECT ... FOR UPDATE` (row lock)
- Optimistic locking (version field, retry on conflict)
- Redis atomic ops (`DECRBY`, `SETNX`)

## Related rules

`04-idor` (race + missing auth), `07-mass-assignment`

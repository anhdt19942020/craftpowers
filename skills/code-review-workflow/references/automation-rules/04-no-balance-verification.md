---
id: NO-BALANCE-VERIFICATION
severity: CRITICAL
applies_to: all
---

# No Balance Verification

## Intent

Topup executes without checking balance before and after. If the platform charges wrong amount, deducts fees, or silently fails — automation cannot detect it. Financial discrepancy goes unnoticed.

## Search patterns

- Topup flow with no balance read before `page.click('submit')`
- No balance comparison after topup confirmation
- No `balance_before` / `balance_after` variables in topup function
- No reconciliation logic or assertion on balance delta

## Fix

```typescript
const balanceBefore = await getBalance(page, accountId);
await executeTopup(page, amount);
const balanceAfter = await getBalance(page, accountId);

const delta = balanceAfter - balanceBefore;
const tolerance = amount * 0.01; // 1% tolerance for fees

if (Math.abs(delta - amount) > tolerance) {
  await flagForManualReview({
    accountId, amount, balanceBefore, balanceAfter, delta,
    reason: 'Balance delta mismatch'
  });
}
```

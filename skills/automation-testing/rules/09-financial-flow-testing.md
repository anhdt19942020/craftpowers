---
id: FINANCIAL-FLOW-TESTING
severity: MEDIUM
applies_to: [playwright]
---

# Financial Flow Testing

## Intent

Financial flows (topup, payment, transfer) carry real money risk. Tests must verify idempotency, balance consistency, and audit trail — not just "form submitted successfully." Reference `automation-review` rules for the full security audit checklist.

## Search patterns

- Payment/topup tests with no balance assertion before AND after
- No idempotency check (submitting same form twice)
- No test for network timeout during payment
- No test for concurrent payment submissions
- Tests that only check UI success message, not actual balance change

## Fix

```typescript
test.describe('Topup Flow', () => {
  test('successful topup updates balance', async ({ page, request }) => {
    // Get balance BEFORE
    const balanceBefore = await page.getByTestId('balance').textContent();

    // Execute topup
    await page.getByTestId('topup-amount').fill('100');
    await page.getByTestId('topup-submit').click();
    await page.waitForResponse(
      resp => resp.url().includes('/api/topup') && resp.status() === 200
    );

    // Verify balance AFTER
    await expect(page.getByTestId('balance')).not.toHaveText(balanceBefore!);
    const balanceAfter = await page.getByTestId('balance').textContent();
    expect(parseFloat(balanceAfter!) - parseFloat(balanceBefore!)).toBe(100);
  });

  test('double submit does not double-charge', async ({ page }) => {
    await page.getByTestId('topup-amount').fill('100');
    // Rapid double-click
    await page.getByTestId('topup-submit').dblclick();
    // Wait for responses
    const responses: number[] = [];
    page.on('response', resp => {
      if (resp.url().includes('/api/topup')) responses.push(resp.status());
    });
    await page.waitForTimeout(2000); // exception: timing for race condition test
    // Only one successful transaction
    expect(responses.filter(s => s === 200).length).toBe(1);
  });
});
```

### Cross-reference

For comprehensive financial automation audit, apply `automation-review` skill rules:
- Rule 01: Missing Idempotency Key
- Rule 02: Retry Without Status Check
- Rule 03: No Concurrent Lock
- Rule 04: No Balance Verification

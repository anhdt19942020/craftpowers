---
id: MULTI-TAB-TESTING
severity: LOW
applies_to: [playwright]
---

# Multi-Tab Testing

## Intent

Features involving popups, new tabs, iframes, or cross-tab communication need explicit multi-context handling. Playwright doesn't auto-switch tabs — unhandled popups cause tests to silently operate on the wrong page.

## Search patterns

- `target="_blank"` links with no popup handler in test
- OAuth flows that open a new window (no `waitForEvent('popup')`)
- Tests with iframes that don't use `frameLocator()`
- Payment gateway redirects to external pages
- No `context.pages()` check after actions that may open tabs

## Fix

```typescript
// Handle new tab / popup
test('external link opens in new tab', async ({ page, context }) => {
  const [newPage] = await Promise.all([
    context.waitForEvent('page'),
    page.getByRole('link', { name: 'Documentation' }).click(),
  ]);
  await newPage.waitForLoadState();
  await expect(newPage).toHaveURL(/docs\.example\.com/);
  await newPage.close();
});

// OAuth popup flow
test('Google OAuth login', async ({ page, context }) => {
  const [popup] = await Promise.all([
    context.waitForEvent('page'),
    page.getByRole('button', { name: 'Sign in with Google' }).click(),
  ]);
  await popup.waitForLoadState();
  await popup.getByLabel('Email').fill('test@gmail.com');
  await popup.getByRole('button', { name: 'Next' }).click();
  // After OAuth completes, popup closes and original page updates
  await popup.waitForEvent('close');
  await expect(page.getByTestId('user-menu')).toBeVisible();
});

// iFrame interaction
test('embedded payment form', async ({ page }) => {
  const paymentFrame = page.frameLocator('#payment-iframe');
  await paymentFrame.getByLabel('Card number').fill('4242424242424242');
  await paymentFrame.getByLabel('Expiry').fill('12/30');
  await paymentFrame.getByLabel('CVC').fill('123');
  await paymentFrame.getByRole('button', { name: 'Pay' }).click();
  // Back to main page for result
  await expect(page.getByTestId('payment-success')).toBeVisible();
});
```

### MCP Interactive Mode

Use `browser_tabs` to list and switch between tabs. Each tab interaction needs explicit `browser_navigate` or tool calls targeting the correct tab context.

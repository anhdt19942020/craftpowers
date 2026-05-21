---
id: ASSERTION-PATTERNS
severity: HIGH
applies_to: [playwright]
---

# Assertion Patterns

## Intent

Tests without meaningful assertions are false confidence — they "pass" but verify nothing. Weak assertions (`toBeTruthy`, `toBeVisible` alone) miss real bugs. Every test step needs specific, verifiable assertions.

## Search patterns

- Tests with no `expect()` calls
- `expect(result).toBeTruthy()` — too weak, anything truthy passes
- `expect(element).toBeVisible()` — necessary but insufficient alone
- Tests that only check navigation happened, not page content
- No negative assertions (checking that errors DON'T appear)

## Fix

```typescript
// BAD — only checks visibility
await expect(page.getByTestId('dashboard')).toBeVisible();

// GOOD — checks specific content
await expect(page.getByTestId('welcome-message')).toHaveText('Welcome, John');
await expect(page).toHaveURL('/dashboard');
await expect(page).toHaveTitle('Dashboard — MyApp');

// GOOD — negative assertions
await expect(page.getByTestId('error-banner')).not.toBeVisible();
await expect(page.getByTestId('loading')).not.toBeAttached();

// GOOD — network assertions
const response = await page.waitForResponse('**/api/user');
expect(response.status()).toBe(200);
const body = await response.json();
expect(body.user.email).toBe('john@example.com');

// GOOD — multiple assertions per step
await loginPage.login('john@example.com', 'password');
await expect(page).toHaveURL('/dashboard');
await expect(page.getByTestId('user-name')).toHaveText('John');
await expect(page.getByTestId('login-error')).not.toBeVisible();
```

### MCP Interactive Mode

In interactive mode, use `browser_snapshot` to verify DOM state and `browser_console_messages` to verify no errors. Report specific findings, not just "page looks correct."

---
id: NETWORK-INTERCEPTION
severity: LOW
applies_to: [playwright]
---

# Network Interception

## Intent

Tests that depend on real API responses are fragile — backend changes break frontend tests. Network interception isolates frontend testing from backend state, enables error simulation, and speeds up test execution.

## Search patterns

- Tests failing because backend returned unexpected data
- No mock/intercept for external API calls
- Tests that require specific database state to pass
- No test for API error responses (500, 403, timeout)
- Tests hitting real payment gateways or third-party services

## Fix

```typescript
// Mock API response
test('displays user list from API', async ({ page }) => {
  await page.route('**/api/users', async route => {
    await route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify([
        { id: 1, name: 'Alice' },
        { id: 2, name: 'Bob' },
      ]),
    });
  });
  await page.goto('/users');
  await expect(page.getByTestId('user-list')).toContainText('Alice');
  await expect(page.getByTestId('user-list')).toContainText('Bob');
});

// Simulate API error
test('shows error message on API failure', async ({ page }) => {
  await page.route('**/api/users', route =>
    route.fulfill({ status: 500, body: 'Internal Server Error' })
  );
  await page.goto('/users');
  await expect(page.getByTestId('error-message')).toBeVisible();
});

// Simulate slow response
test('shows loading state during slow API', async ({ page }) => {
  await page.route('**/api/users', async route => {
    await new Promise(r => setTimeout(r, 3000));
    await route.fulfill({ status: 200, body: '[]' });
  });
  await page.goto('/users');
  await expect(page.getByTestId('loading-spinner')).toBeVisible();
});

// Block external requests
test('no external tracking calls in test', async ({ page }) => {
  const externalRequests: string[] = [];
  page.on('request', req => {
    if (!req.url().includes('localhost')) externalRequests.push(req.url());
  });
  await page.goto('/dashboard');
  expect(externalRequests).toHaveLength(0);
});
```

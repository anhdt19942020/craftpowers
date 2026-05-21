---
id: TEST-DATA-MANAGEMENT
severity: MEDIUM
applies_to: [playwright]
---

# Test Data Management

## Intent

Tests sharing mutable data (same user account, same database records) interfere with each other — flaky in parallel, order-dependent in sequence. Isolated test data eliminates cross-test pollution.

## Search patterns

- Hardcoded credentials: `'admin@test.com'`, `'password123'`
- Same user account used across multiple test files
- No `beforeEach`/`afterEach` cleanup hooks
- Tests that fail when run in parallel but pass sequentially
- No test data factory or fixture pattern

## Fix

```typescript
// fixtures/test-data.ts
import { test as base } from '@playwright/test';

type TestFixtures = {
  testUser: { email: string; password: string };
};

export const test = base.extend<TestFixtures>({
  testUser: async ({ request }, use) => {
    const user = {
      email: `test-${Date.now()}@example.com`,
      password: 'TestPassword123!',
    };
    // Create user via API
    await request.post('/api/test/users', { data: user });
    await use(user);
    // Cleanup after test
    await request.delete(`/api/test/users/${user.email}`);
  },
});

// login.spec.ts
import { test } from './fixtures/test-data';

test('login with valid credentials', async ({ page, testUser }) => {
  await page.goto('/login');
  await page.getByTestId('email').fill(testUser.email);
  await page.getByTestId('password').fill(testUser.password);
  await page.getByRole('button', { name: 'Sign in' }).click();
  await expect(page).toHaveURL('/dashboard');
});
```

### Auth state reuse

```typescript
// Save auth state once, reuse across tests
const authFile = 'playwright/.auth/user.json';

setup('authenticate', async ({ page }) => {
  await page.goto('/login');
  await page.getByTestId('email').fill(process.env.TEST_EMAIL!);
  await page.getByTestId('password').fill(process.env.TEST_PASSWORD!);
  await page.getByRole('button', { name: 'Sign in' }).click();
  await page.context().storageState({ path: authFile });
});
```

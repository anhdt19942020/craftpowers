---
id: AUTH-FLOW-TESTING
severity: MEDIUM
applies_to: [playwright]
---

# Auth Flow Testing

## Intent

Authentication flows are the gateway to every other feature. Broken auth = broken everything. Auth tests must cover login, session management, role-based access, and edge cases like expired tokens.

## Search patterns

- Auth tests only cover happy path (valid login)
- No test for expired sessions / tokens
- No test for role-based access (admin vs user)
- No test for logout + session cleanup
- Hardcoded auth cookies instead of proper login flow
- No test for concurrent sessions

## Fix

```typescript
// auth.spec.ts
import { test, expect } from '@playwright/test';
import { LoginPage } from './pages/login.page';

test.describe('Authentication', () => {
  test('successful login redirects to dashboard', async ({ page }) => {
    const loginPage = new LoginPage(page);
    await page.goto('/login');
    await loginPage.login('valid@example.com', 'ValidPass123!');
    await expect(page).toHaveURL('/dashboard');
    await expect(page.getByTestId('user-menu')).toBeVisible();
  });

  test('invalid credentials show error', async ({ page }) => {
    const loginPage = new LoginPage(page);
    await page.goto('/login');
    await loginPage.login('valid@example.com', 'wrong-password');
    await expect(page).toHaveURL('/login');
    await loginPage.expectError('Invalid email or password');
  });

  test('logout clears session', async ({ page }) => {
    // Login first
    await page.goto('/login');
    await new LoginPage(page).login('valid@example.com', 'ValidPass123!');
    // Logout
    await page.getByTestId('user-menu').click();
    await page.getByRole('menuitem', { name: 'Logout' }).click();
    await expect(page).toHaveURL('/login');
    // Verify session cleared — direct navigation should redirect
    await page.goto('/dashboard');
    await expect(page).toHaveURL('/login');
  });

  test('protected route redirects unauthenticated user', async ({ page }) => {
    await page.goto('/dashboard');
    await expect(page).toHaveURL('/login');
  });
});
```

### Session reuse for non-auth tests

```typescript
// Avoid logging in for every test — reuse storageState
test.use({ storageState: 'playwright/.auth/user.json' });
```

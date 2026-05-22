---
id: PAGE-OBJECT-PATTERN
severity: HIGH
applies_to: [playwright]
---

# Page Object Pattern

## Intent

Test code without Page Objects duplicates selectors and actions across files. When UI changes, every test file needs updating. POM centralizes selectors and actions — one change fixes all tests.

## Search patterns

- Selectors duplicated across multiple `.spec.ts` files
- `page.locator('...')` repeated with same selector in different tests
- No `pages/` or `page-objects/` directory in test structure
- Test files mixing navigation logic with assertions

## Fix

```typescript
// pages/login.page.ts
import { Page, Locator } from '@playwright/test';

export class LoginPage {
  readonly emailInput: Locator;
  readonly passwordInput: Locator;
  readonly submitButton: Locator;
  readonly errorMessage: Locator;

  constructor(private page: Page) {
    this.emailInput = page.getByTestId('login-email');
    this.passwordInput = page.getByTestId('login-password');
    this.submitButton = page.getByRole('button', { name: 'Sign in' });
    this.errorMessage = page.getByTestId('login-error');
  }

  async login(email: string, password: string) {
    await this.emailInput.fill(email);
    await this.passwordInput.fill(password);
    await this.submitButton.click();
  }

  async expectError(message: string) {
    await expect(this.errorMessage).toHaveText(message);
  }
}

// login.spec.ts
import { LoginPage } from './pages/login.page';

test('successful login redirects to dashboard', async ({ page }) => {
  const loginPage = new LoginPage(page);
  await page.goto('/login');
  await loginPage.login('user@example.com', 'password123');
  await expect(page).toHaveURL('/dashboard');
});
```

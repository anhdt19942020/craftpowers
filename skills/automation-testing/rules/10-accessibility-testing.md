---
id: ACCESSIBILITY-TESTING
severity: MEDIUM
applies_to: [playwright]
---

# Accessibility Testing

## Intent

Automation tests that ignore accessibility miss bugs affecting real users. Keyboard navigation, screen reader support, and ARIA compliance should be checked alongside functional tests — not as a separate afterthought.

## Search patterns

- No `getByRole()` usage in tests — indicates no accessibility awareness
- No keyboard navigation tests (Tab, Enter, Escape)
- No ARIA attribute assertions
- No heading hierarchy checks
- No focus management tests after modal open/close

## Fix

```typescript
test.describe('Accessibility', () => {
  test('login form is keyboard navigable', async ({ page }) => {
    await page.goto('/login');
    // Tab to email field
    await page.keyboard.press('Tab');
    await expect(page.getByTestId('email')).toBeFocused();
    // Tab to password field
    await page.keyboard.press('Tab');
    await expect(page.getByTestId('password')).toBeFocused();
    // Tab to submit button
    await page.keyboard.press('Tab');
    await expect(page.getByRole('button', { name: 'Sign in' })).toBeFocused();
    // Enter to submit
    await page.keyboard.press('Enter');
  });

  test('modal traps focus', async ({ page }) => {
    await page.getByRole('button', { name: 'Open settings' }).click();
    const modal = page.getByRole('dialog');
    await expect(modal).toBeVisible();
    // First focusable element in modal should have focus
    await expect(modal.getByRole('button').first()).toBeFocused();
    // Escape closes modal
    await page.keyboard.press('Escape');
    await expect(modal).not.toBeVisible();
  });

  test('heading hierarchy is correct', async ({ page }) => {
    await page.goto('/dashboard');
    const headings = await page.evaluate(() => {
      return Array.from(document.querySelectorAll('h1, h2, h3, h4, h5, h6'))
        .map(h => ({ level: parseInt(h.tagName[1]), text: h.textContent }));
    });
    // No skipped levels
    for (let i = 1; i < headings.length; i++) {
      expect(headings[i].level - headings[i - 1].level).toBeLessThanOrEqual(1);
    }
  });
});
```

### MCP Interactive Mode

Use `browser_snapshot` — it returns the accessibility tree, which directly shows ARIA roles, names, and structure. More reliable than DOM inspection for a11y checks.

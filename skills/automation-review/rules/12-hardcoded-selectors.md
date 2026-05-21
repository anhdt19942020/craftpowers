---
id: HARDCODED-SELECTORS
severity: MEDIUM
applies_to: all
---

# Hardcoded CSS/XPath Selectors

## Intent

Selectors like `#topup-btn`, `.btn-primary`, `div > form > button:nth-child(3)` break when the platform updates its UI. Financial automation with brittle selectors fails silently at 3AM.

## Search patterns

- `page.locator('div.classname')`, `page.locator('#id')`
- `page.$('button.btn-primary')`
- XPath: `page.locator('//div[@class="..."]/button')`
- CSS with structural selectors: `:nth-child`, `>`, `~`
- No `data-testid` or role-based selectors

## Fix

Use Playwright's recommended locator hierarchy:
```typescript
// BAD
await page.click('#topup-submit-btn');
await page.click('div.form-container > button:nth-child(2)');

// GOOD
await page.getByRole('button', { name: 'Top Up' }).click();
await page.getByLabel('Amount').fill('100');
await page.getByTestId('topup-submit').click();
```

Priority: `getByRole` > `getByLabel` > `getByPlaceholder` > `getByText` > `getByTestId` > CSS

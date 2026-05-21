---
id: SMART-SELECTORS
severity: HIGH
applies_to: [playwright]
---

# Smart Selectors

## Intent

Fragile selectors (CSS classes, deeply nested paths, nth-child) break when UI is refactored. Smart selectors survive styling changes, component restructuring, and i18n updates.

## Search patterns

- `page.locator('.btn-primary')` — CSS class selector, fragile
- `page.locator('#app > div > div:nth-child(3) > button')` — deep nesting, extremely fragile
- `page.locator('//div[@class="container"]/form/input[2]')` — XPath, fragile
- No `data-testid` attributes in the application code

## Fix

Selector priority (most stable → least stable):

```typescript
// 1. data-testid — BEST: explicit, stable, decoupled from UI
page.getByTestId('submit-payment');

// 2. ARIA role + name — GOOD: semantic, tests what users see
page.getByRole('button', { name: 'Submit Payment' });

// 3. Label — GOOD for form fields
page.getByLabel('Email address');

// 4. Placeholder — OK for inputs without labels
page.getByPlaceholder('Enter your email');

// 5. Text content — FRAGILE with i18n, OK for static content
page.getByText('Welcome back');

// 6. CSS selector — FRAGILE, only when nothing else works
page.locator('[data-state="active"]');

// NEVER: XPath, nth-child, deeply nested selectors
```

When `data-testid` doesn't exist in the app, suggest adding it:
```
Note: Adding data-testid="submit-payment" to the submit button would make this test more resilient.
Suggested change: <button data-testid="submit-payment">Submit</button>
```

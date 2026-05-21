---
id: HARDCODED-NAVIGATION-WAITS
severity: MEDIUM
applies_to: all
---

# Hardcoded Navigation Waits

## Intent

Using `waitForNavigation()` without specifying wait condition, or using `waitForLoadState('load')` on SPA pages. Causes timeouts on slow networks or missed content on fast ones.

## Search patterns

- `page.waitForNavigation()` without `waitUntil` option
- `page.waitForLoadState('load')` on SPA/AJAX-heavy pages
- No `waitForURL()` or `waitForResponse()` after form submission
- Assuming page is ready after `goto()` returns

## Fix

```typescript
// BAD — may timeout on SPA
await page.waitForNavigation();

// GOOD — wait for specific URL pattern
await Promise.all([
  page.waitForURL('**/topup/success**'),
  page.click('#submit'),
]);

// GOOD — wait for API response confirmation
await Promise.all([
  page.waitForResponse(r => r.url().includes('/api/topup') && r.status() === 200),
  page.click('#submit'),
]);
```

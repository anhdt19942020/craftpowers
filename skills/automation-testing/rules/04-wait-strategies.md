---
id: WAIT-STRATEGIES
severity: HIGH
applies_to: [playwright]
---

# Wait Strategies

## Intent

Fixed delays (`sleep`, `waitForTimeout`) are flaky — too short on slow machines, too slow on fast ones. Proper waits adapt to actual page state and eliminate timing-related failures.

## Search patterns

- `await page.waitForTimeout(` — Playwright anti-pattern
- `await sleep(`, `await delay(`
- `await new Promise(r => setTimeout(r,`
- `time.sleep(` (Python Playwright)
- Any fixed millisecond delay between actions

## Fix

```typescript
// BAD — fixed delay
await page.waitForTimeout(3000);
await page.click('#submit');

// GOOD — wait for element state
await page.getByTestId('submit').waitFor({ state: 'visible' });
await page.getByTestId('submit').click();

// GOOD — wait for navigation
await page.waitForURL('**/dashboard');

// GOOD — wait for network response
await page.waitForResponse(
  resp => resp.url().includes('/api/login') && resp.status() === 200
);

// GOOD — wait for loading to finish
await page.waitForLoadState('networkidle');

// GOOD — wait for element to disappear (loading spinner)
await page.getByTestId('loading-spinner').waitFor({ state: 'hidden' });

// GOOD — custom condition
await page.waitForFunction(() => {
  return document.querySelector('[data-testid="results"]')?.children.length > 0;
});
```

### MCP Interactive Mode equivalents

Use `browser_wait_for` tool with appropriate conditions instead of arbitrary delays between `browser_click` and `browser_snapshot` calls.

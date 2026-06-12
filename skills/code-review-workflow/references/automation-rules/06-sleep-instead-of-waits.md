---
id: SLEEP-INSTEAD-OF-WAITS
severity: HIGH
applies_to: [playwright, puppeteer, selenium]
---

# Sleep Instead of Proper Waits

## Intent

Using `sleep()`, `waitForTimeout()`, or `setTimeout()` instead of Playwright's built-in wait mechanisms. Fixed delays are flaky (too short = failure, too long = slow), hide real issues, and don't adapt to network/platform conditions.

## Search patterns

- `await page.waitForTimeout(` — Playwright anti-pattern per official docs
- `await sleep(`, `await delay(`, `await new Promise(r => setTimeout(r,`
- `time.sleep(` (Python)
- `Thread.sleep(` (Java)
- Any fixed delay between navigation steps

## Fix

Use Playwright's built-in waits:
```typescript
// BAD
await page.waitForTimeout(3000);
await page.click('#submit');

// GOOD
await page.waitForSelector('#submit', { state: 'visible' });
await page.click('#submit');

// For network-dependent pages
await page.waitForResponse(resp => resp.url().includes('/api/topup') && resp.status() === 200);

// For SPA navigation
await page.waitForURL('**/success**');
```

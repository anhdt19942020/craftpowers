---
id: NO-SCREENSHOT-ON-FAILURE
severity: HIGH
applies_to: [playwright, puppeteer, selenium]
---

# No Screenshot On Failure

## Intent

Automation fails silently without capturing page state. When a topup fails at 3AM, there's no visual evidence of what the page looked like — was it a CAPTCHA? Wrong page? Session expired? Impossible to debug without screenshot.

## Search patterns

- `catch` blocks without `page.screenshot()` call
- No `finally` block capturing page state
- Error logging without visual evidence
- No screenshot directory or naming convention

## Fix

```typescript
try {
  await executeTopup(page, account, amount);
} catch (error) {
  const screenshotPath = `screenshots/${operationId}-${Date.now()}.png`;
  await page.screenshot({ path: screenshotPath, fullPage: true });
  logger.error('Topup failed', { operationId, error: error.message, screenshot: screenshotPath });
  throw error;
}
```

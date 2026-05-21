---
id: NO-STALE-SESSION-DETECTION
severity: HIGH
applies_to: [playwright, puppeteer, selenium]
---

# No Stale Session Detection

## Intent

Automation continues operating with an expired session. The platform redirects to login page mid-flow, but automation doesn't detect this — it clicks elements on the login page thinking it's the topup page, causing unpredictable behavior or wasted operations.

## Search patterns

- No check for login page URL after navigation
- No detection of session-expired indicators (login form, "session expired" text)
- No HTTP 401/403 response monitoring
- `storageState` loaded without checking if session is still valid
- No session validation step before financial operations

## Fix

```typescript
async function ensureAuthenticated(page: Page): Promise<void> {
  const url = page.url();
  if (url.includes('/login') || url.includes('/signin')) {
    throw new StaleSessionError('Redirected to login — session expired');
  }
  const loginForm = await page.locator('form[action*="login"]').count();
  if (loginForm > 0) {
    throw new StaleSessionError('Login form detected — session expired');
  }
}

// Call before every financial operation
await ensureAuthenticated(page);
await executeTopup(page, amount);
```

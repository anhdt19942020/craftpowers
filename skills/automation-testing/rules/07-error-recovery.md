---
id: ERROR-RECOVERY
severity: MEDIUM
applies_to: [playwright]
---

# Error Recovery

## Intent

Tests that fail without evidence leave you guessing. Screenshot on failure, console log capture, and proper cleanup turn "test failed" into "test failed because X, here's proof."

## Search patterns

- No `screenshot` capture in test failure handlers
- No `afterEach` hook for cleanup
- Empty `catch` blocks that swallow errors
- No console error collection on failure
- Tests that leave browser state dirty after failure (open modals, unsaved forms)

## Fix

```typescript
// playwright.config.ts
export default defineConfig({
  use: {
    screenshot: 'only-on-failure',
    trace: 'on-first-retry',
    video: 'on-first-retry',
  },
});

// Custom error collection in tests
test.afterEach(async ({ page }, testInfo) => {
  if (testInfo.status !== testInfo.expectedStatus) {
    // Capture screenshot
    const screenshot = await page.screenshot({ fullPage: true });
    await testInfo.attach('failure-screenshot', {
      body: screenshot,
      contentType: 'image/png',
    });

    // Capture console logs
    const logs = await page.evaluate(() => {
      return (window as any).__consoleLogs || [];
    });
    await testInfo.attach('console-logs', {
      body: JSON.stringify(logs, null, 2),
      contentType: 'application/json',
    });
  }
});
```

### MCP Interactive Mode

In interactive mode, when a step fails:
1. `browser_take_screenshot` — capture current state
2. `browser_console_messages` — check for errors
3. `browser_network_requests` — check for failed requests
4. Report all three as evidence before diagnosing

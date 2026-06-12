## Selector & CDP Cookbook

### Selector Strategy (priority order)

1. **Accessible roles** (most resilient — tied to semantics, not layout)
   ```js
   page.getByRole('button', { name: 'Submit' })
   page.getByRole('textbox', { name: 'Email' })
   page.getByRole('heading', { name: 'Dashboard' })
   ```

2. **Test IDs** (explicit, stable, works when semantics aren't available)
   ```js
   page.getByTestId('submit-button')
   // HTML: <button data-testid="submit-button">
   ```

3. **Labels** (good for form inputs)
   ```js
   page.getByLabel('Email address')
   ```

4. **Text content** (fragile for UI text that changes; fine for stable labels)
   ```js
   page.getByText('Sign in')
   ```

5. **CSS selectors** (last resort — brittle, breaks on redesign)
   ```js
   page.locator('.auth-form > button[type="submit"]')
   ```

### Waiting Patterns

**Wait for network idle (after navigation):**
```js
await page.goto('/dashboard', { waitUntil: 'networkidle' });
```

**Wait for element to be visible:**
```js
await page.waitForSelector('[data-testid="user-menu"]', { state: 'visible' });
```

**Wait for API response:**
```js
const [response] = await Promise.all([
  page.waitForResponse(resp => resp.url().includes('/api/profile')),
  page.click('[data-testid="load-profile"]'),
]);
const data = await response.json();
```

**Condition-based waiting (see `condition-based-waiting.md`):**
```js
await page.waitForFunction(() => {
  return document.querySelector('.status')?.textContent === 'Ready';
});
```

### CDP Direct Access

Use Chrome DevTools Protocol directly for capabilities Playwright doesn't expose:

**Emulate network conditions:**
```js
const client = await page.context().newCDPSession(page);
await client.send('Network.emulateNetworkConditions', {
  offline: false,
  downloadThroughput: 500 * 1024 / 8,  // 500 kbps
  uploadThroughput: 500 * 1024 / 8,
  latency: 400,
});
```

**Intercept and modify responses:**
```js
await page.route('/api/user', route => {
  route.fulfill({
    status: 200,
    body: JSON.stringify({ name: 'Test User', role: 'admin' }),
  });
});
```

**Capture console errors:**
```js
const errors = [];
page.on('console', msg => {
  if (msg.type() === 'error') errors.push(msg.text());
});
// After test:
expect(errors).toHaveLength(0);
```

**Monitor network requests:**
```js
const requests = [];
page.on('request', req => requests.push({ url: req.url(), method: req.method() }));
// After action:
const patchRequests = requests.filter(r => r.method === 'PATCH');
expect(patchRequests).toHaveLength(1);
expect(patchRequests[0].url).toContain('/api/tasks/42');
```

### Accessibility Checks

**Check element is reachable by keyboard:**
```js
await page.keyboard.press('Tab');
const focused = await page.evaluate(() => document.activeElement?.getAttribute('data-testid'));
expect(focused).toBe('submit-button');
```

**Check ARIA attributes:**
```js
const ariaLabel = await page.getAttribute('[data-testid="close-btn"]', 'aria-label');
expect(ariaLabel).toBe('Close dialog');
```

**Check role announced to screen readers:**
```js
const role = await page.getAttribute('[data-testid="status-badge"]', 'role');
expect(role).toBe('status');
```

### Screenshot Comparison

```js
// Capture baseline
await page.screenshot({ path: 'screenshots/dashboard-baseline.png' });

// After change, compare
await expect(page).toHaveScreenshot('dashboard-baseline.png', {
  maxDiffPixelRatio: 0.01,  // 1% pixel difference tolerance
});
```

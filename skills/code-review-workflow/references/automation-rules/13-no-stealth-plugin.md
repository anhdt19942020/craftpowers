---
id: NO-STEALTH-PLUGIN
severity: MEDIUM
applies_to: [playwright, puppeteer]
---

# No Stealth Plugin

## Intent

Default Playwright/Puppeteer launches are trivially detectable by anti-bot systems. `navigator.webdriver === true`, zero plugins, missing locale — platforms block automated access, causing failed topups.

## Search patterns

- `chromium.launch()` without stealth plugin
- No `playwright-extra` or `playwright-stealth` import
- No `navigator.webdriver` override
- Default viewport (1280x720) without customization
- No locale/timezone configuration matching target region

## Fix

Node.js:
```typescript
import { chromium } from 'playwright-extra';
import StealthPlugin from 'puppeteer-extra-plugin-stealth';
chromium.use(StealthPlugin());

const browser = await chromium.launch({
  headless: true,
  args: ['--disable-blink-features=AutomationControlled'],
});
const context = await browser.newContext({
  viewport: { width: 1920, height: 1080 },
  locale: 'vi-VN',
  timezoneId: 'Asia/Ho_Chi_Minh',
});
```

Python:
```python
from playwright_stealth import Stealth
async with Stealth().use_async(async_playwright()) as p:
    browser = await p.chromium.launch()
```

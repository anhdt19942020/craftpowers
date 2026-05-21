# Playwright MCP Tools Reference

Quick reference for all MCP Playwright tools available to the automation-tester agent.

## Navigation

| Tool | Description | Example Use |
|------|-------------|-------------|
| `browser_navigate` | Go to a URL | Navigate to login page |
| `browser_navigate_back` | Go back in history | Return to previous page after checking a link |
| `browser_tabs` | List open tabs, switch between them | Check if popup opened, switch to OAuth tab |

## Interaction

| Tool | Description | Example Use |
|------|-------------|-------------|
| `browser_click` | Click an element (by ref or selector) | Click submit button |
| `browser_hover` | Hover over an element | Trigger dropdown menu |
| `browser_press_key` | Press a keyboard key | Press Enter to submit, Escape to close modal |
| `browser_drag` | Start drag from an element | Drag item in sortable list |
| `browser_drop` | Drop onto a target element | Drop item into target zone |

## Forms

| Tool | Description | Example Use |
|------|-------------|-------------|
| `browser_fill_form` | Fill multiple form fields at once | Fill login form (email + password) |
| `browser_type` | Type text into focused element | Type search query |
| `browser_select_option` | Select dropdown option | Select payment method |
| `browser_file_upload` | Upload a file to input | Upload profile photo |

## Verification

| Tool | Description | Example Use |
|------|-------------|-------------|
| `browser_snapshot` | Get accessibility tree of current page | Verify DOM structure, ARIA roles, element states |
| `browser_take_screenshot` | Capture visual screenshot | Evidence capture, visual regression |
| `browser_console_messages` | Read console output (log, warn, error) | Check for JavaScript errors |
| `browser_network_requests` | List network requests made | Verify API calls, check payloads |
| `browser_evaluate` | Execute JavaScript in page context | Read application state (read-only) |

## Control

| Tool | Description | Example Use |
|------|-------------|-------------|
| `browser_wait_for` | Wait for a condition | Wait for element visible, network idle |
| `browser_resize` | Resize browser viewport | Test responsive design at different breakpoints |
| `browser_handle_dialog` | Accept/dismiss browser dialogs | Handle alert, confirm, prompt |
| `browser_close` | Close browser | Cleanup after testing |

## Common Patterns

### Login flow
```
1. browser_navigate → /login
2. browser_fill_form → email + password
3. browser_click → submit button
4. browser_wait_for → URL change to /dashboard
5. browser_snapshot → verify dashboard content
6. browser_take_screenshot → evidence
```

### Form validation test
```
1. browser_navigate → /register
2. browser_fill_form → invalid data (empty email)
3. browser_click → submit
4. browser_snapshot → check for error messages
5. browser_console_messages → check no JS errors
```

### Visual regression
```
1. browser_navigate → target page
2. browser_take_screenshot → "before" state
3. [make changes]
4. browser_navigate → same page (reload)
5. browser_take_screenshot → "after" state
6. Compare screenshots
```

### Responsive testing
```
1. browser_resize → 1920x1080 (desktop)
2. browser_take_screenshot
3. browser_resize → 768x1024 (tablet)
4. browser_take_screenshot
5. browser_resize → 375x667 (mobile)
6. browser_take_screenshot
```

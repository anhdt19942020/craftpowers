# Frontend Verification

## When to Use

Implementation touches frontend files: `.tsx`, `.jsx`, `.vue`, `.svelte`, `.html`, `.css`, `.scss`
UI bugs, visual regressions, console errors after changes.

## Detection

Auto-detect frontend relevance from changed files:

```
*.tsx, *.jsx       → React component
*.vue              → Vue component
*.svelte           → Svelte component
*.html, *.css      → Static/styles
*.scss, *.less     → Preprocessor styles
```

If no frontend files changed → skip this module entirely.

## Verification Flow

```
1. Check browser tool availability
   ├── MCP Playwright available → use mcp__plugin_playwright_playwright__*
   ├── Chrome DevTools MCP → use chrome-devtools-mcp
   └── Neither → manual verification (document steps)

2. Start dev server (if not running)
   └── Detect: npm/pnpm/yarn dev, next dev, vite, etc.

3. Navigate to affected page/component

4. Collect evidence:
   ├── Screenshot (before/after if regression)
   ├── Console errors (filter noise: React DevTools, extensions)
   ├── Network errors (failed requests, CORS)
   └── Accessibility check (if available)

5. Report findings
```

## MCP Playwright Verification

```
# Navigate
browser_navigate → http://localhost:3000/affected-page

# Capture state
browser_snapshot → DOM accessibility tree
browser_console_messages → check for errors/warnings
browser_network_requests → check for failed requests

# Screenshot for visual check
browser_take_screenshot → capture current state

# Interact if needed
browser_click → test interactive elements
browser_fill_form → test form inputs
```

## Console Error Triage

| Error type | Severity | Action |
|-----------|----------|--------|
| `TypeError: Cannot read property` | High | Null check or data loading race |
| `Warning: Each child should have unique key` | Medium | Add key prop to list items |
| `Failed to fetch` / CORS | High | API endpoint or proxy config |
| `Hydration mismatch` | High | Server/client render differs |
| `ResizeObserver loop` | Low | Usually harmless, ignore |
| React DevTools warnings | Low | Dev-only, ignore in verification |

## Visual Regression Checklist

- [ ] Layout intact (no unexpected shifts)
- [ ] Colors/typography match design
- [ ] Responsive: check at 375px, 768px, 1280px
- [ ] Dark mode (if supported)
- [ ] Loading states render correctly
- [ ] Error states render correctly
- [ ] Empty states render correctly
- [ ] Interactive elements respond (hover, click, focus)

## When Browser Tools Unavailable

Document manual verification steps:

```
## Manual Verification Required

1. Start dev server: `npm run dev`
2. Open http://localhost:3000/[page]
3. Check: [specific things to verify]
4. Open DevTools Console — confirm no errors
5. Test: [specific interactions]

Browser MCP unavailable — cannot auto-verify.
```

## Integration with /man-debug

When `/man-debug` detects frontend files in changed set:

1. Load this reference automatically
2. After fix verified by tests → run browser verification
3. Include screenshot evidence in fix summary
4. If browser tools unavailable → note in wrap-up

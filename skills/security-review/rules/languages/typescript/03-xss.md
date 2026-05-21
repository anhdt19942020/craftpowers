---
id: XSS
severity_max: HIGH
applies_to: typescript
---

# XSS — TypeScript

React auto-escapes by default. Dangerous escapes:

## Search patterns

- `dangerouslySetInnerHTML={{ __html: userContent }}`
- Vue: `v-html="userContent"`
- Angular: `bypassSecurityTrustHtml(userContent)`
- `innerHTML = userContent`
- `document.write(userInput)`

Safe: React JSX `{variable}`, Angular `{{ variable }}`, Vue `{{ variable }}`

## Fix

Use DOMPurify for user HTML content. Never bypass framework sanitization without DOMPurify.

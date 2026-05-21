---
id: CORS-MISCONFIG
severity_max: HIGH
applies_to: typescript
---

# CORS Misconfiguration — TypeScript

## Search patterns

- `cors({ origin: '*', credentials: true })`
- `cors({ origin: true })` (reflects any origin)
- `res.setHeader('Access-Control-Allow-Origin', req.headers.origin)` without validation

## Fix

Whitelist origins: `cors({ origin: ['https://app.com'], credentials: true })`.

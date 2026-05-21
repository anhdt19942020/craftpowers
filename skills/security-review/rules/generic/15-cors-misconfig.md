---
id: CORS-MISCONFIG
severity_max: HIGH
applies_to: all
---

# CORS Misconfiguration

## Intent

Wrong CORS config allows any website to read data from your API as logged-in user. `Access-Control-Allow-Origin: *` + `Allow-Credentials: true` = any site steals user data.

## Search patterns

- `Access-Control-Allow-Origin: *` combined with `Access-Control-Allow-Credentials: true`
- Dynamic origin set to `req.headers.origin` without validation
- `cors({ origin: true })` in Express
- CORS reflecting request origin unconditionally

## L1-L4 reasoning

Flag if: wildcard origin + credentials enabled. `Allow-Origin: *` alone is fine for public APIs without cookies.

## Fix

```js
// Wrong
cors({ origin: '*', credentials: true })
// Right
cors({ origin: ['https://yourapp.com'], credentials: true })
```

## Related rules

`11-csrf` (CORS + CSRF = full session hijack)

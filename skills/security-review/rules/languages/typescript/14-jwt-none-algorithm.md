---
id: JWT-NONE-ALGORITHM
severity_max: CRITICAL
applies_to: typescript
---

# JWT None Algorithm Attack — TypeScript

## Intent

JWT library accepting `alg: "none"` → attacker creates unsigned token, bypasses all auth.

## Search patterns

- `jwt.verify(token, secret)` without `algorithms` option
- `jsonwebtoken` verify without `{ algorithms: ['HS256'] }`
- `jose` without algorithm restriction

## Fix

Always specify algorithms: `jwt.verify(token, secret, { algorithms: ['HS256'] })`.

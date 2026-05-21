---
id: CSRF
severity_max: HIGH
applies_to: typescript
---

# CSRF — TypeScript

`csurf` deprecated April 2022 — still widely used, has unfixed CVEs.

## Search patterns

- Using deprecated `csurf` package
- Cookie session without any CSRF middleware
- `SameSite` not set on session cookies

## Fix

Replace `csurf` with `csrf-csrf`. Set `SameSite=Lax` on cookies.

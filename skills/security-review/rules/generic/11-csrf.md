---
id: CSRF
severity_max: HIGH
applies_to: all
---

# Cross-Site Request Forgery (CSRF)

## Intent

Browser auto-sends session cookies. If app uses cookie auth and state-changing endpoints lack CSRF token or cookie lacks `SameSite`, attacker's site auto-submits forms targeting victim's session.

## Search patterns

- Session auth via cookies without CSRF token validation on POST/PUT/DELETE
- Cookie set without `SameSite=Lax` or `SameSite=Strict`
- Express without CSRF middleware
- Flask without `CSRFProtect`
- Django with `@csrf_exempt` on state-changing views

## L1-L4 reasoning

Flag if: cookie-based auth + state-changing endpoint + no CSRF protection. NOT a finding if: JWT in Authorization header (no cookies), or `SameSite=Strict` set.

## Fix

- Set `SameSite=Lax` on session cookies
- For APIs: use JWT in `Authorization: Bearer` header
- For cookie sessions: use `csrf-csrf` (Node), `flask-wtf` (Python), Django built-in CSRF

## Related rules

`03-xss` (XSS can bypass CSRF protections from inside session)

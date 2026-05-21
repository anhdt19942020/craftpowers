---
id: CSRF
severity_max: HIGH
applies_to: php
---

# CSRF — PHP

## Search patterns

- Auto-submit forms, `<img>` for GET forgeries
- Laravel: `->withoutMiddleware(VerifyCsrfToken::class)` bypassing built-in CSRF
- Raw PHP with no CSRF token in forms

## Fix

Laravel: don't bypass CSRF middleware. Raw PHP: generate + validate CSRF tokens on all state-changing forms.

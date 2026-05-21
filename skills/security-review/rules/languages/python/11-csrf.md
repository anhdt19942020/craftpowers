---
id: CSRF
severity_max: HIGH
applies_to: python
---

# CSRF — Python

Django has CSRF middleware ON by default. Flask has no built-in CSRF.

## Search patterns

- Django: `@csrf_exempt` on state-changing views
- Flask: no `CSRFProtect` from flask-wtf on forms

## Fix

Django: remove `@csrf_exempt`. Flask: install flask-wtf, initialize `CSRFProtect(app)`.

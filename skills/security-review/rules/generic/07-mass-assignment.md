---
id: MASS-ASSIGNMENT
severity_max: CRITICAL
applies_to: all
---

# Mass Assignment

## Intent

Endpoint spreads/merges entire `req.body` into model/DB without field filtering. Attacker adds `is_admin: true`, `role: "admin"`, `balance: 999999` to self-promote.

## Search patterns

- `User.create(req.body)` — entire body to create
- `user.update(req.body)` — entire body to update
- `Object.assign(user, req.body)` — merge all fields
- `{ ...req.body }` spread into model
- Django: `ModelForm(request.POST)` with `fields = '__all__'`
- Python: `User(**request.json)` without whitelist

## L1-L4 reasoning

`req.body` is L1. If L1 passes to model create/update without explicit field selection → finding.

## Fix

Whitelist allowed fields:
```js
// Bad
User.create(req.body)
// Good
User.create({ name: req.body.name, email: req.body.email })
```
Or use DTO/schema validation (Zod, Joi, Pydantic) that strips extra fields.

## Related rules

`04-idor` (mass assignment to change `user_id`), `12-broken-access-control`

---
id: IDOR
severity_max: HIGH
applies_to: all
---

# Insecure Direct Object Reference (IDOR)

## Intent

Endpoint receives `id` from user (L1), returns/modifies resource WITHOUT ownership check. Attacker changes ID in URL to access other users' data.

## Search patterns

- `db.findById(req.params.id)` without ownership check
- `User.findOne({ id: req.query.userId })` without `req.user.id === result.userId`
- Any endpoint taking `id` param → DB lookup without `WHERE user_id = currentUser.id`
- `DELETE /api/items/:id` without `item.owner_id === req.user.id`

## L1-L4 reasoning

`req.params.id` is L1. Resource fetched is L2. Flag if L1 ID accesses L2 resource without ownership validation.

## Fix

Add ownership check: `if (resource.user_id !== req.user.id) return 403`. Or scoped query: `db.findOne({ id: req.params.id, user_id: req.user.id })`.

## Related rules

`07-mass-assignment` (change `user_id` field), `03-xss` (steal token → IDOR)

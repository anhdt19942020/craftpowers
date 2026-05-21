---
id: SQL-INJECTION
severity_max: CRITICAL
applies_to: all
---

# SQL Injection

## Intent

L1 input concatenated into SQL. Attacker sends `' OR 1=1--` or `'; DROP TABLE users;--` to dump DB, delete tables, escalate to admin.

## Search patterns

- `f"SELECT ... {user_input}"` / f-string with L1 var
- `"SELECT ... " + variable` string concat
- `.query("... " + req.body.x)`
- Template literals: `` `SELECT * FROM users WHERE id = ${req.params.id}` ``

## L1-L4 reasoning

Source must be L1. Trace from `req.body`, `req.query`, `req.params` → SQL string. If parameterized query or ORM query builder used → NOT a finding.

## Fix

Use parameterized queries:
- Node: `db.query('SELECT * FROM users WHERE id = $1', [req.params.id])`
- Python: `cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))`
- Go: `db.Query("SELECT * FROM users WHERE id = ?", id)`

## Related rules

`17-verbose-error-debug-mode` (SQL error returns full query), `04-idor` (SQLi + missing auth = nuke DB), `07-mass-assignment`

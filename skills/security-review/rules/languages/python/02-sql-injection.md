---
id: SQL-INJECTION
severity_max: CRITICAL
applies_to: python
---

# SQL Injection — Python

Multiple DB APIs with specific dangerous patterns.

## Search patterns

- `cursor.execute(f"SELECT ... {user_input}")`
- `cursor.execute("SELECT ... " + user_input)`
- SQLAlchemy: `db.execute(text(f"SELECT ... {input}"))` or `db.execute(text("SELECT ... " + input))`
- Django: `Model.objects.raw("SELECT ... " + input)`, `Model.objects.extra(where=[input])`

Safe: parameterized `cursor.execute("SELECT ... WHERE id = %s", (id,))`, Django ORM, SQLAlchemy ORM.

## Fix

Use parameterized queries. Django: use ORM. SQLAlchemy: use `text(:param)` with `.bindparams()`.

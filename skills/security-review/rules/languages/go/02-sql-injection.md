---
id: SQL-INJECTION
severity_max: CRITICAL
applies_to: go
---

# SQL Injection — Go

## Search patterns

- `fmt.Sprintf("SELECT ... %s", userInput)` into `db.Query()`
- String `+` concat into SQL: `"SELECT * FROM users WHERE id = " + id`
- `db.Raw("SELECT ... " + userInput)` (GORM)

Safe patterns (NOT findings):
- `db.Query("SELECT * FROM users WHERE id = ?", id)` (database/sql parameterized)
- GORM query builder: `db.Where("id = ?", id).Find(&user)`

## Fix

Use `database/sql` placeholders `$1`/`?` or GORM query builder. Never `fmt.Sprintf` into SQL.

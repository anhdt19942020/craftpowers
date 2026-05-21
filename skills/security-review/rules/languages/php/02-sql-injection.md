---
id: SQL-INJECTION
severity_max: CRITICAL
applies_to: php
---

# SQL Injection — PHP

Heaviest history of SQLi. `$_GET`, `$_POST`, `$_REQUEST`, `$_COOKIE` are L1 superglobals.

## Search patterns

- `mysql_query("SELECT * FROM users WHERE id = " . $_GET['id'])`
- `mysqli_query($conn, "SELECT ... " . $input)`
- Raw PDO without prepare: `$pdo->query("SELECT ... $input")`
- Laravel `DB::select("SELECT ... $input")` without bindings

Safe: PDO prepared statements, Laravel query builder with `?` bindings.

## Fix

Use PDO prepared: `$stmt = $pdo->prepare("SELECT * FROM users WHERE id = ?"); $stmt->execute([$id]);`

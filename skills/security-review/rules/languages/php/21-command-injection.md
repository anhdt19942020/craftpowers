---
id: COMMAND-INJECTION
severity_max: CRITICAL
applies_to: php
---

# Command Injection — PHP

6 shell execution families: `system()`, `exec()`, `shell_exec()`, `passthru()`, backticks, `proc_open()`.

## Search patterns

- `system("convert " . $_FILES['img']['name'])`
- `exec("git clone " . $url)`
- `shell_exec("ping " . $_GET['host'])`
- `` `ls $dir` `` (backtick syntax)

## Fix

Use `escapeshellarg()` and `escapeshellcmd()`. Better: avoid shell, use PHP native functions.

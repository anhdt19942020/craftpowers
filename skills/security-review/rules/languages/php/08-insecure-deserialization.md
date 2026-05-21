---
id: INSECURE-DESERIALIZATION
severity_max: CRITICAL
applies_to: php
---

# Insecure Deserialization — PHP

`unserialize()` is RCE classic via magic methods (`__wakeup`, `__destruct`, `__toString`, `__call`).

## Search patterns

- `unserialize($_GET['data'])`, `unserialize($_POST['data'])`, `unserialize($_COOKIE['session'])`

## Fix

Never `unserialize` user input. Use `json_decode()` for data exchange.

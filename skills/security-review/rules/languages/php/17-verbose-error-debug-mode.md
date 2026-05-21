---
id: VERBOSE-ERROR-DEBUG-MODE
severity_max: CRITICAL
applies_to: php
---

# Verbose Error — PHP (CRITICAL)

Severity CRITICAL for PHP — Ignition debugger exposes full env vars.

## Search patterns

- `display_errors = On` in production php.ini
- Laravel `APP_DEBUG=true` in production
- `ini_set('display_errors', 1)` in production code

## Fix

`APP_DEBUG=false` in production. `display_errors = Off` in php.ini. Use structured logging.

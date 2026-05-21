# Data Flow Classification — L1–L4 Trust Levels

Core methodology for determining whether a code pattern is a real vulnerability or a false positive.

## Trust Levels

| Level | Name | Trust | Description |
|-------|------|-------|-------------|
| L1 | User-controlled input | NOT TRUSTED | HTTP request (body, query, header, cookie, file upload, URL param), WebSocket message, CLI args, env var that user can set |
| L2 | DB / storage | PARTIAL | Data from DB/Redis/file — was originally L1, may have been transformed or validated. Check if sanitized before stored |
| L3 | Internal service / config | MOSTLY TRUSTED | Internal microservice data, config file, env var set by DevOps (not user-settable) |
| L4 | Constants / literals | FULLY TRUSTED | Hardcoded in source: string literal, const, enum value |

## Decision Rules

- A pattern is only a finding if data flows **L1 → sink** without proper sanitization/parameterization
- **L2 → sink**: flag only if the original L1 input was not validated before storage
- **L3/L4 → sink**: NOT a finding (false positive)
- Exception: Rule 01 (HARDCODED-SECRET) — flag L4 literals that are credentials

## Common L1 Sources

| Framework | L1 Sources |
|-----------|-----------|
| Express/Node | `req.body`, `req.query`, `req.params`, `req.headers`, `req.cookies`, `req.files` |
| Go (Gin/Chi/Fiber) | `ctx.Query()`, `ctx.Param()`, `ctx.PostForm()`, `r.URL.Query()`, `r.FormValue()` |
| PHP | `$_GET`, `$_POST`, `$_REQUEST`, `$_COOKIE`, `$_FILES`, `$_SERVER['HTTP_*']` |
| Python (Flask) | `request.args`, `request.form`, `request.json`, `request.files`, `request.headers` |
| Python (Django) | `request.GET`, `request.POST`, `request.body`, `request.FILES` |

## Reasoning Protocol

For each potential pattern match:

1. **Identify the source** — where does the data originate?
2. **Classify trust level** — L1/L2/L3/L4
3. **Trace the path** — does data pass through any sanitizer, validator, or parameterizer?
4. **Identify the sink** — SQL query, DOM render, shell command, file path, HTTP request, etc.
5. **Verdict** — flag only if L1 reaches sink without mitigation

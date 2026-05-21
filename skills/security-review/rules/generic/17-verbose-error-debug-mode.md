---
id: VERBOSE-ERROR-DEBUG-MODE
severity_max: HIGH
applies_to: all
---

# Verbose Error / Debug Mode

## Intent

Debug mode or stack traces in responses → attacker reads file paths, DB names, SQL queries, framework version, env vars. Werkzeug/Flask debug with `/console` → RCE.

## Search patterns

- `DEBUG=True` in production config
- `debug: true` in Express/Fastify
- `res.json({ error: err.stack })` or `res.send(err.message)`
- `FLASK_ENV=development` in production .env
- Stack trace in HTTP response body

## L1-L4 reasoning

Debug config = L3/L4 but the issue is exposure to L1 users. Flag if debug mode enabled in production paths or error details returned to client.

## Fix

- Never enable debug in production
- Return generic: `res.status(500).json({ error: 'Internal server error' })`
- Log full error server-side only
- Environment-conditional: `if (NODE_ENV !== 'production') { detail } else { generic }`

## Related rules

`01-hardcoded-secret` (secrets in error logs), `02-sql-injection` (SQL in error messages)

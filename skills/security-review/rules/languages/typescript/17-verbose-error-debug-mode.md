---
id: VERBOSE-ERROR-DEBUG-MODE
severity_max: HIGH
applies_to: typescript
---

# Verbose Error — TypeScript

## Search patterns

- `app.use((err, req, res, next) => res.json({ error: err.stack }))`
- `debug: true` in Express/Fastify/NestJS config
- `res.status(500).send(err.message)` with full error

## Fix

Generic error handler: `res.status(500).json({ error: 'Internal server error' })`. Log details with Winston/Pino.

---
id: SSRF
severity_max: HIGH
applies_to: typescript
---

# SSRF — TypeScript

## Search patterns

- `fetch(userUrl)`, `axios.get(userUrl)`, `got(userUrl)`, `node-fetch(userUrl)`

## Fix

Validate URL, block private IPs, allow HTTPS only.

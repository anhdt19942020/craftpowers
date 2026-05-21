---
id: INSECURE-DESERIALIZATION
severity_max: CRITICAL
applies_to: typescript
---

# Insecure Deserialization — TypeScript

## Search patterns

- `node-serialize` package (RCE CVE-2017-5941)
- `serialize-javascript` with eval
- `vm.runInThisContext(userCode)`
- `eval("(" + json + ")")`

## Fix

Use `JSON.parse()`. Never `eval` or `vm.runInContext` on user data.

---
id: SESSION-COOKIES-IN-LOGS
severity: HIGH
applies_to: all
---

# Session Cookies In Logs

## Intent

Debug logging includes raw cookie values, Authorization headers, or session tokens. If logs are compromised or shared, attacker can hijack active sessions on financial platforms.

## Search patterns

- `console.log(response.headers())` — dumps all headers including Set-Cookie
- `logger.debug(cookies)`, `logger.debug(headers)`
- `JSON.stringify(page.context().cookies())` in log output
- No header redaction in HTTP interceptor logs

## Fix

Redact sensitive headers before logging:
```typescript
function redactHeaders(headers: Record<string, string>): Record<string, string> {
  const sensitive = ['cookie', 'set-cookie', 'authorization'];
  return Object.fromEntries(
    Object.entries(headers).map(([k, v]) =>
      sensitive.includes(k.toLowerCase()) ? [k, '[REDACTED]'] : [k, v]
    )
  );
}
```

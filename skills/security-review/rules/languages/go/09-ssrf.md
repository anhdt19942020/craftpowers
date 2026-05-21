---
id: SSRF
severity_max: CRITICAL
applies_to: go
---

# SSRF — Go (CRITICAL)

Severity bumped to CRITICAL for Go (common in microservices).

## Search patterns

- `http.Get(userURL)`, `http.Post(userURL, ...)`
- `http.Client.Do(req)` where URL from user
- Colly `c.Visit(url)` with no host validation

## Fix

Validate URL, block private IPs, allow HTTPS only, DNS rebinding protection.

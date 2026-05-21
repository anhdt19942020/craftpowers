---
id: SSRF
severity_max: HIGH
applies_to: python
---

# SSRF — Python

## Search patterns

- `requests.get(user_url)`
- `urllib.request.urlopen(user_url)`
- `httpx.get(user_url)`
- `aiohttp.ClientSession.get(user_url)`

## Fix

Validate URL, block private IPs, allow HTTPS only. Use `ipaddress` module to check resolved IP.

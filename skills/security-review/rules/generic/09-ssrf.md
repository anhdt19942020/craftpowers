---
id: SSRF
severity_max: HIGH
applies_to: all
---

# Server-Side Request Forgery (SSRF)

## Intent

Server sends HTTP request to URL provided by user (L1). Attacker specifies `http://169.254.169.254/latest/meta-data/iam/security-credentials/` to read AWS IAM credentials, or `http://localhost:8080/admin` to pivot inside internal network.

## Search patterns

- `fetch(req.query.url)` / `axios.get(req.body.url)`
- `requests.get(user_url)` / `httpx.get(user_url)`
- `http.Get(userURL)` (Go)
- Image proxy, webhook handler, URL preview, screenshot service, RSS importer

## L1-L4 reasoning

User-provided URL = L1. Flag if L1 URL passed to server-side HTTP client without validation. If URL comes from config (L3) → NOT a finding.

## Fix

- Block private IPs: `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`, `127.0.0.1`, `169.254.0.0/16`
- Allow only HTTPS
- DNS rebinding protection (validate IP after resolution)
- Whitelist domains if possible

## Related rules

`01-hardcoded-secret` (SSRF to metadata = credential theft)

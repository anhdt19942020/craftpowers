---
id: HARDCODED-SECRET
severity_max: CRITICAL
applies_to: all
---

# Hardcoded Secret

## Intent

API keys, DB passwords, tokens embedded directly in source code or committed to Git. GitHub has 24/7 scanning bots — seconds of exposure and credentials are compromised.

## Search patterns

- `API_KEY\s*=\s*["'][A-Za-z0-9]{20,}["']`
- `password\s*=\s*["'][^"']{6,}["']` (non-env-var assignment)
- `secret\s*=\s*["'][^"']{8,}["']`
- `private_key\s*=\s*["']-----BEGIN`
- `Bearer\s+[A-Za-z0-9\-._~+/]{20,}`
- Any token/credential not loaded from env var or secrets manager

## L1-L4 reasoning

Exception rule — hardcoded strings are L4 but the vulnerability is committing them. Flag any credential literal in source that is NOT a placeholder like `YOUR_KEY_HERE`.

## Fix

Move to environment variables (`process.env.X`, `os.environ['X']`, `os.Getenv("X")`). Use secrets manager (AWS Secrets Manager, HashiCorp Vault, Doppler) for production.

## Related rules

Cross-check `17-verbose-error-debug-mode` (secret may leak via error logs).

---
id: INSECURE-DESERIALIZATION
severity_max: HIGH
applies_to: go
---

# Insecure Deserialization — Go

No "magic method RCE" like PHP/Python, but risks exist:
- `encoding/gob.NewDecoder().Decode()` with registered types from user data
- `gopkg.in/yaml.v2` unmarshaling to `interface{}` can be exploited

## Fix

Use `json.Unmarshal` for untrusted data. If gob/yaml needed, validate and restrict types.

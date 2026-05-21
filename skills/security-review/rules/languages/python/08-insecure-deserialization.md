---
id: INSECURE-DESERIALIZATION
severity_max: CRITICAL
applies_to: python
---

# Insecure Deserialization — Python

`pickle.loads()` is most dangerous — arbitrary code execution on load.

## Search patterns

- `pickle.loads(user_data)`, `pickle.load(file_from_user)`
- `yaml.load(content)` without `Loader=yaml.SafeLoader`
- `eval(user_input)`, `exec(user_code)`
- `dill.loads(data)`

## Fix

Never pickle untrusted data. Use `json.loads()`. YAML: `yaml.safe_load()`. Never `eval`/`exec` on user input.

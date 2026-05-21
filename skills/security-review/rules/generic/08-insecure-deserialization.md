---
id: INSECURE-DESERIALIZATION
severity_max: CRITICAL
applies_to: all
---

# Insecure Deserialization

## Intent

Code uses `pickle.loads`, `yaml.load`, `eval`, `unserialize`, `ObjectInputStream` on user-controlled data. These execute arbitrary code during deserialization → RCE.

## Search patterns

- Python: `pickle.loads(user_data)`, `yaml.load(content)` (without SafeLoader), `eval(user_input)`, `exec(user_code)`
- PHP: `unserialize($user_input)`
- Node: `node-serialize`, `eval("(" + json + ")")`
- Java: `ObjectInputStream.readObject()` with user-controlled stream
- .NET: `BinaryFormatter.Deserialize()`

## L1-L4 reasoning

If data being deserialized originates from L1 → CRITICAL. If from L3 (internal service) with HMAC verification → NOT a finding.

## Fix

- Python: never `pickle.loads` on untrusted data. Use `json.loads`. If YAML: `yaml.safe_load`
- PHP: never `unserialize` user input. Use JSON
- Sign serialized data with HMAC, verify before deserializing

## Related rules

`21-command-injection` (similar RCE family)

---
id: MASS-ASSIGNMENT
severity_max: CRITICAL
applies_to: python
---

# Mass Assignment — Python

## Search patterns

- `User(**request.json)` without field whitelist
- Django: `ModelForm(request.POST)` with `fields = '__all__'`
- Pydantic models that don't exclude sensitive fields

## Fix

Whitelist fields explicitly. Pydantic: use `model_config = ConfigDict(extra='forbid')`. Django: list fields explicitly.

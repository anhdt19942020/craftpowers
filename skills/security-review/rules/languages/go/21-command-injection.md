---
id: COMMAND-INJECTION
severity_max: CRITICAL
applies_to: go
---

# Command Injection — Go

## Search patterns

`exec.Command` with variadic args is default safe. Dangerous:
- `exec.Command("sh", "-c", "ls " + userPath)`
- `exec.Command("bash", "-c", fmt.Sprintf("convert %s out.jpg", userFile))`

## Fix

Use variadic args: `exec.Command("ls", userPath)` — no shell involved.

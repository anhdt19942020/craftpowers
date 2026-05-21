---
id: COMMAND-INJECTION
severity_max: CRITICAL
applies_to: typescript
---

# Command Injection — TypeScript

## Search patterns

- `child_process.exec("cmd " + input)` (goes through shell)
- `execSync("cmd " + input)`
- `require('child_process').exec(userInput)`

Safe: `child_process.spawn('cmd', [input])` (no shell)

## Fix

Use `spawn` with array args. Never `exec` with string concatenation.

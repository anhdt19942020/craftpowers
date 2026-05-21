---
id: COMMAND-INJECTION
severity_max: CRITICAL
applies_to: python
---

# Command Injection — Python

## Search patterns

- `os.system("cmd " + input)`
- `os.popen("cmd " + input)`
- `subprocess.run("cmd " + input, shell=True)`
- `subprocess.call(f"cmd {input}", shell=True)`

Safe: `subprocess.run(['cmd', input], shell=False)`

## Fix

Always use list form with `shell=False`. If shell unavoidable: `shlex.quote(input)`.

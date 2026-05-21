---
id: PATH-TRAVERSAL
severity_max: HIGH
applies_to: all
---

# Path Traversal

## Intent

File operations with path containing user input (L1). Attacker passes `../../../../etc/passwd` or absolute path to read system files, overwrite config, leak `.env`.

## Search patterns

- `fs.readFile(req.params.filename)` without normalization
- `open(os.path.join(base, user_input))`
- `path.join(uploadDir, req.body.filename)` without validation
- Any file operation where user controls part of path

## L1-L4 reasoning

User-controlled filename/path = L1. Flag if L1 reaches file system operation without `path.resolve()` + prefix check.

## Fix

```js
const safePath = path.resolve(baseDir, userFilename);
if (!safePath.startsWith(baseDir)) return res.status(400).send('Invalid path');
```

## Related rules

`16-unrestricted-file-upload` (upload + path traversal = write anywhere)

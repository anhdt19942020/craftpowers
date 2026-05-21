---
id: UNRESTRICTED-FILE-UPLOAD
severity_max: CRITICAL
applies_to: all
---

# Unrestricted File Upload

## Intent

Upload with no validation → attacker uploads `shell.php` to webroot → RCE. Or `evil.svg` with JavaScript → XSS.

## Search patterns

- File upload handler with no extension whitelist
- `multer({ dest: 'uploads/' })` without `fileFilter`
- Saving to publicly accessible directory (webroot, static folder)
- No MIME type validation
- Storing with user-provided filename

## L1-L4 reasoning

Uploaded file = L1. Flag if: no extension whitelist, no MIME check, stored in webroot, or user-controlled filename.

## Fix

- Whitelist extensions: `['.jpg', '.png', '.gif', '.pdf']`
- Validate MIME type + magic bytes
- Store OUTSIDE webroot
- Rename to UUID: `crypto.randomUUID() + ext`
- Serve via signed URL, never direct access

## Related rules

`10-path-traversal` (upload + traversal = write anywhere), `21-command-injection` (uploaded file processed by shell)

---
id: VERBOSE-ERROR-DEBUG-MODE
severity_max: HIGH
applies_to: go
---

# Verbose Error — Go

## Search patterns

- `gin.SetMode(gin.DebugMode)` in production
- GORM error returning full SQL
- Panic messages leaking env vars
- `http.Error(w, err.Error(), 500)` exposing internal errors

## Fix

Use recovery middleware, return generic errors, log details server-side.

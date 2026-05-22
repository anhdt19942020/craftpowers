---
description: "Instrument code with temporary console.logs to trace bug execution flow. Auto-cleanup after. Use when bug location is unclear."
---

Invoke the `debug-flight-recorder` skill now.

This skill instruments code with `[FLIGHT-RECORDER]` markers, runs repro, collects logs, then removes all markers automatically.

**Prerequisite:** Working tree must be clean (no uncommitted changes). If dirty, ask user to stash or commit first.

**Integration with /man-debug:** If after tracing the root cause is found, user can run `/man-debug` to apply the systematic debugging process for the actual fix.

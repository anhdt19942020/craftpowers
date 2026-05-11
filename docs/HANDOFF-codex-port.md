# Codex Port — Handoff / Status

**Updated:** 2026-05-12
**Goal:** Port the craftpowers (mankit) Claude Code plugin to OpenAI Codex CLI. Monorepo, full feature parity, easy install.
**Plan:** `docs/mankit/plans/2026-05-11-codex-port.md` (7 phases, ~32 tasks, TDD)
**Spec:** `docs/mankit/specs/2026-05-11-codex-port-design.md`
**Execution method:** Subagent-Driven Development (dispatch `implementer` agent per phase/task; controller reviews between).
**Pacing decision:** Stop after each phase for user review. Branch: `main` (consent given).

---

## Done

### Phase 1 — Foundation ✅ (committed `7d35ac6` → `64e7213`)
Extracted shared pure logic into `hooks/lib/`, added pytest, refactored Claude hooks into thin wrappers. **No behavior change** — verified.

- `pyproject.toml` — pytest config (`testpaths=["tests"]`, `pythonpath=["."]`)
- `hooks/lib/security_gate.py` — `evaluate(command) -> (ok, reason)` (17 DANGEROUS_PATTERNS verbatim)
- `hooks/lib/credential_scanner.py` — `scan_content(content, file_path) -> list[str]`, `build_warning(file_path, findings) -> str`
- `hooks/lib/session_context.py` — `build_session_start_context(plugin_root, home=None) -> str` (injects using-man block; `.rstrip("\n")` to match bash `$(cat)`)
- `hooks/lib/context_tracker.py` — `context_warning(transcript_path, model) -> str|None` (model-aware: opus-4-7 → 1M limit, else 200k; warn ≥140k, critical ≥175k)
- `hooks/lib/session_summary.py` — `build_summary(transcript_path, rtk_runner=None) -> str` (token summary box + RTK savings)
- `hooks/claude/{__init__,_bootstrap,pre_tool_use,post_tool_use,user_prompt_submit,session_start,stop}.py` — thin entry points, inline `sys.path` bootstrap
- `hooks/hooks.json` — repointed `command` to `python "${CLAUDE_PLUGIN_ROOT}/hooks/claude/*.py"` (matchers unchanged, all `async: false`)
- `tests/lib/test_*.py` — 32 tests, all pass
- Old standalone hooks (`hooks/security-gate.py`, `hooks/credential-scanner.py`, `hooks/context-tracker.py`, `hooks/session-summary.py`, `hooks/session-start`, `hooks/run-hook.cmd`) **left in place** (no longer referenced, nothing deleted)

**Parity verified** (old scripts vs new wrappers, identical stdin → identical stdout + exit code): security-gate (safe/rm-rf/force-push), credential-scanner (clean/AKIA/skip-ext), context-tracker (no-transcript/large/large+opus-4-7), session-summary (empty), session-start (bash vs python — byte-for-byte after the `rstrip` fix in `64e7213`).

### Phase 2 plan — patched, NOT yet implemented
The plan markdown for Phase 2 (Tasks 2.1–2.6) has been reconciled to the post-Phase-1 lib API and a missing Codex `user_prompt_submit.py` was added. Ready to dispatch.

---

## Next — Phase 2: Codex hook adapters (READY TO DISPATCH)

Create `hooks/codex/*` mirroring the 5 Claude entry points + Codex hook manifest. Purely additive — does not touch `hooks/hooks.json`, `hooks/claude/*`, or `hooks/lib/*`.

Tasks (full code is in the plan, `docs/mankit/plans/2026-05-11-codex-port.md` §"Phase 2"):
- **2.1** — golden fixtures `tests/fixtures/codex/{pre_tool_use_safe,pre_tool_use_destructive,session_start,stop}.json` + `tests/fixtures/claude/{pre_tool_use_safe,pre_tool_use_destructive}.json`
- **2.2** — `hooks/codex/{__init__,_bootstrap,pre_tool_use}.py` + `tests/adapters/{__init__,test_codex_pre_tool_use}.py`. Deny output: `{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":...}}` on stdout, **exit 0**.
- **2.3** — `hooks/codex/session_start.py` + test. Output: `{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":ctx}}`. MUST inject the full using-man block.
- **2.4** — `hooks/codex/stop.py` + test. **NEVER emit a `decision` key** — Codex Stop semantics are INVERTED (`{"decision":"block"}` = *continue with reason as new prompt*). Only emits `{"systemMessage": build_summary(...)}`.
- **2.5** — `hooks/codex/post_tool_use.py` (no-op shim) + `hooks/codex/user_prompt_submit.py` (context warning; reads `model` from stdin payload, not env var) + tests
- **2.6** — `hooks/codex/hooks.json` — mirrors all 5 events; `python "${CODEX_PLUGIN_ROOT}/hooks/codex/*.py"` (quoted, `python` not `python3`)

**Dispatch context the implementer needs:** Windows/PowerShell; use `python` not `python3`; the revised lib API (see Done §Phase 1); inline `sys.path` bootstrap pattern (copy from `hooks/claude/*.py`); Codex deny-JSON shape + inverted Stop semantics (above); leave old files alone; **do not commit `docs/`**; run `python -m pytest tests/ -q` after.

After Phase 2: controller self-verify (mechanical) or spec+quality review → report to user → STOP.

---

## Remaining phases (one at a time, await user go-ahead)

- **Phase 3 — Skill source migration (W3):** `skills/man-*/SKILL.md` becomes source of truth; `scripts/generate_commands.py` renders Claude `commands/man-*.md` from it. Verify Claude slash commands still work end-to-end.
- **Phase 4 — Codex packaging:** Codex equivalent of `.claude-plugin/` — agents via `[agents.<name>]` TOML, MCP via optional per-skill `agents/openai.yaml`, generated Codex prompt files.
- **Phase 5 — Install UX:** `/plugins install mankit` (primary) + `install-codex.{sh,ps1}` fallback. Easy install is the headline goal.
- **Phase 6 — CI & verification:** GitHub Actions running pytest + the parity/smoke checks on both harness layouts.
- **Phase 7 — Docs & release:** `README.codex.md`, version bump, changelog.

---

## Key gotchas (don't relearn the hard way)

- **Use `python`, not `python3`** on this machine (Windows; `python3` may not resolve).
- **chicken-and-egg sys.path:** entry-point scripts run as `python hooks/X/foo.py` with repo root NOT on `sys.path` → can't `from hooks.X import _bootstrap` until path is set. Do INLINE `sys.path.insert(0, _root)` at the top of every entry point (see `hooks/claude/*.py`).
- **Codex Stop is inverted vs Claude.** `hooks/codex/stop.py` must never emit `decision`.
- **`$(cat)` strips trailing newlines** — `session_context.py` uses `.rstrip("\n")` to keep the injected block byte-identical to the old bash hook.
- Old hooks are still on disk on purpose. Don't delete them until the Codex side is proven and the install paths are sorted.
- Plan/spec files under `docs/mankit/plans/` and `docs/mankit/specs/` are working docs — **don't commit them**. (This HANDOFF file is committed by explicit request.)

"""Consolidated hook dispatcher — runs all gates for an event in a single process.

Instead of spawning N Python processes per event, this module runs all
registered evaluators in-process and returns the combined result.
"""
from __future__ import annotations

import sys
from typing import Any, Callable

EvalFn = Callable[..., dict[str, Any]]


class HookDispatcher:
    """Dispatch multiple hook evaluators for a single event."""

    def __init__(self, event_name: str):
        self.event_name = event_name
        self._gates: list[tuple[str, EvalFn, dict[str, str]]] = []

    def register(self, name: str, evaluate_fn: EvalFn, *, arg_map: dict[str, str] | None = None) -> "HookDispatcher":
        """Register an evaluator function.

        arg_map maps dispatcher context keys to function parameter names.
        Example: {"tool_name": "tool_name", "file_path": "file_path"}
        """
        self._gates.append((name, evaluate_fn, arg_map or {}))
        return self

    def run(self, context: dict[str, Any], *, logger: Any = None) -> dict[str, Any]:
        """Run all registered gates in order. First block wins."""
        messages: list[str] = []

        for name, fn, arg_map in self._gates:
            try:
                kwargs = {}
                for ctx_key, param_name in arg_map.items():
                    if ctx_key in context:
                        kwargs[param_name] = context[ctx_key]

                result = fn(**kwargs) if kwargs else fn()

                if isinstance(result, dict):
                    if result.get("decision") == "block":
                        if logger:
                            logger(self.event_name, "block", result.get("reason", name))
                        return result
                    if result.get("systemMessage"):
                        messages.append(result["systemMessage"])
                elif isinstance(result, tuple):
                    ok, reason = result
                    if not ok:
                        if logger:
                            logger(self.event_name, "block", reason)
                        return {"decision": "block", "reason": reason}
                elif isinstance(result, str) and result:
                    print(result, file=sys.stderr)
            except Exception as exc:
                if logger:
                    try:
                        from hooks.lib.hook_logger import log_error
                        log_error(self.event_name, exc)
                    except Exception:
                        pass

        out: dict[str, Any] = {"decision": "ok"}
        if messages:
            out["systemMessage"] = "\n".join(messages)
        return out

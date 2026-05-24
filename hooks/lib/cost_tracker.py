"""Cost tracker — append per-session token cost record to ~/.claude/metrics/costs.jsonl.

record schema:
  date, session_id, model, input_tokens, output_tokens, estimated_usd
"""
from __future__ import annotations
import json
import os
import pathlib
from datetime import datetime, timezone

from hooks.lib.session_summary import estimate_tokens, _safe_transcript_path

# Cost per million tokens in USD (input, output)
MODEL_COSTS: dict[str, tuple[float, float]] = {
    "claude-opus-4-7": (15.0, 75.0),
    "claude-opus-4.7": (15.0, 75.0),
    "claude-opus-4-6": (15.0, 75.0),
    "claude-opus-4.6": (15.0, 75.0),
    "claude-sonnet-4-6": (3.0, 15.0),
    "claude-sonnet-4.6": (3.0, 15.0),
    "claude-haiku-4-5": (0.80, 4.0),
    "claude-haiku-4.5": (0.80, 4.0),
}

_DEFAULT_COST = (3.0, 15.0)  # fall back to Sonnet pricing if model unknown


def _model_cost(model: str) -> tuple[float, float]:
    m = (model or "").lower()
    for key, cost in MODEL_COSTS.items():
        if key in m:
            return cost
    return _DEFAULT_COST


def _metrics_path() -> pathlib.Path:
    p = pathlib.Path.home() / ".claude" / "metrics"
    p.mkdir(parents=True, exist_ok=True)
    return p / "costs.jsonl"


def track(transcript_path: str | None, session_id: str, model: str) -> dict:
    safe_path = _safe_transcript_path(transcript_path)
    input_tok, output_tok = estimate_tokens(safe_path)
    input_cost_per_m, output_cost_per_m = _model_cost(model)
    estimated_usd = (
        input_tok * input_cost_per_m / 1_000_000
        + output_tok * output_cost_per_m / 1_000_000
    )
    record = {
        "date": datetime.now(tz=timezone.utc).strftime("%Y-%m-%d"),
        "session_id": session_id or "",
        "model": model or "",
        "input_tokens": input_tok,
        "output_tokens": output_tok,
        "estimated_usd": round(estimated_usd, 6),
    }
    try:
        metrics_file = _metrics_path()
        with open(metrics_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
    except Exception:
        pass
    return record

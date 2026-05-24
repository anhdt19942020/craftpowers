"""Strategic compact suggestion — count tool calls, suggest /compact at phase boundaries."""
import json
import os
import tempfile

THRESHOLD = 50
REMIND_INTERVAL = 25


def _state_path() -> str:
    session_id = os.environ.get("CLAUDE_SESSION_ID", "default")
    return os.path.join(tempfile.gettempdir(), f"mankit-compact-{session_id}.json")


def _load_state() -> dict:
    path = _state_path()
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {"count": 0, "last_suggested_at": 0}


def _save_state(state: dict) -> None:
    with open(_state_path(), "w") as f:
        json.dump(state, f)


def evaluate() -> str | None:
    state = _load_state()
    state["count"] += 1
    count = state["count"]
    last = state["last_suggested_at"]

    msg = None
    if count >= THRESHOLD and (count - last) >= REMIND_INTERVAL:
        state["last_suggested_at"] = count
        msg = (
            f"Context budget note: {count} tool calls this session. "
            "Consider running /compact at the next phase boundary to preserve context quality. "
            "Best timing: after completing a task, before starting the next one."
        )

    _save_state(state)
    return msg

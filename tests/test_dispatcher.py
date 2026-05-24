"""Tests for HookDispatcher."""
from hooks.lib.dispatcher import HookDispatcher


def test_all_pass():
    d = HookDispatcher("test")
    d.register("a", lambda: {"decision": "ok"})
    d.register("b", lambda: {"decision": "ok"})
    assert d.run({})["decision"] == "ok"


def test_first_block_wins():
    d = HookDispatcher("test")
    d.register("a", lambda: {"decision": "block", "reason": "blocked by a"})
    d.register("b", lambda: {"decision": "ok"})
    result = d.run({})
    assert result["decision"] == "block"
    assert "blocked by a" in result["reason"]


def test_arg_mapping():
    def check(tool_name: str, file_path: str):
        if file_path.endswith(".env"):
            return {"decision": "block", "reason": "sensitive file"}
        return {"decision": "ok"}

    d = HookDispatcher("test")
    d.register("privacy", check, arg_map={"tool_name": "tool_name", "file_path": "file_path"})

    assert d.run({"tool_name": "Read", "file_path": "config.py"})["decision"] == "ok"
    assert d.run({"tool_name": "Read", "file_path": ".env"})["decision"] == "block"


def test_exception_doesnt_crash():
    def bad_gate():
        raise ValueError("boom")

    d = HookDispatcher("test")
    d.register("bad", bad_gate)
    d.register("good", lambda: {"decision": "ok"})
    assert d.run({})["decision"] == "ok"


def test_system_messages_collected():
    d = HookDispatcher("test")
    d.register("a", lambda: {"decision": "ok", "systemMessage": "msg1"})
    d.register("b", lambda: {"decision": "ok", "systemMessage": "msg2"})
    result = d.run({})
    assert "msg1" in result.get("systemMessage", "")
    assert "msg2" in result.get("systemMessage", "")


def test_tuple_result_block():
    d = HookDispatcher("test")
    d.register("sec", lambda: (False, "dangerous command"))
    result = d.run({})
    assert result["decision"] == "block"
    assert "dangerous command" in result["reason"]


def test_tuple_result_ok():
    d = HookDispatcher("test")
    d.register("sec", lambda: (True, ""))
    assert d.run({})["decision"] == "ok"

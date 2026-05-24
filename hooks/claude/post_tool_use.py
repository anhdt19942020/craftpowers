"""Claude PostToolUse entry — credential scanner. Mirrors hooks/credential-scanner.py output."""
import json
import os
import sys

# Ensure repo root is on sys.path before importing hooks.lib
_here = os.path.dirname(os.path.abspath(__file__))
_root = (
    os.environ.get("CLAUDE_PLUGIN_ROOT")
    or os.environ.get("CURSOR_PLUGIN_ROOT")
    or os.path.abspath(os.path.join(_here, "..", ".."))
)
if _root not in sys.path:
    sys.path.insert(0, _root)

from hooks.lib.credential_scanner import scan_content, build_warning  # noqa: E402
from hooks.lib.hook_logger import log_hook, log_error  # noqa: E402
from hooks.lib.hook_profiles import is_gate_active  # noqa: E402
from hooks.lib.suggest_compact import evaluate as compact_evaluate  # noqa: E402
from hooks.lib.write_quality import evaluate as quality_evaluate  # noqa: E402


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0
    tool_input = data.get("tool_input", {})
    if not isinstance(tool_input, dict):
        return 0

    if is_gate_active("credential_scanner"):
        try:
            content = tool_input.get("content", "")
            file_path = tool_input.get("file_path", "")
            findings = scan_content(content, file_path)
            if findings:
                print(json.dumps({"systemMessage": build_warning(file_path, findings)}))
            log_hook("post_tool_use", "ok")
        except Exception as exc:
            log_error("post_tool_use", exc)

    # Write-quality enforcement (PostToolUse on Edit/Write)
    if is_gate_active("write_quality"):
        try:
            tool_name = data.get("tool_name", "")
            file_path = data.get("tool_input", {}).get("file_path", "")
            if tool_name in ("Edit", "Write"):
                qr = quality_evaluate(tool_name, file_path)
                if qr.get("decision") == "block":
                    print(json.dumps({"decision": "block", "reason": qr["reason"]}))
                    return 2
                if qr.get("systemMessage"):
                    print(json.dumps({"systemMessage": qr["systemMessage"]}))
        except Exception as exc:
            log_error("post_tool_use", exc)

    # Strategic compact suggestion
    if is_gate_active("suggest_compact"):
        try:
            compact_msg = compact_evaluate()
            if compact_msg:
                print(compact_msg, file=sys.stderr)
        except Exception as exc:
            log_error("post_tool_use", exc)
    return 0


if __name__ == "__main__":
    sys.exit(main())

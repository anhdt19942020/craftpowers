#!/usr/bin/env python3
"""
PostToolUse/Stop hook: Match events against rules and suggest agent dispatch.
Input: JSON via stdin. Output: systemMessage (JSON) if a rule matches, else nothing.
Exit 0 always (non-blocking).
"""
import json
import os
import re
import sys


RULES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "auto-dispatch-rules.json")


def load_rules():
    try:
        with open(RULES_PATH, "r", encoding="utf-8") as f:
            return json.load(f).get("rules", [])
    except Exception:
        return []


def had_failure_in_session(transcript_path):
    """Scan JSONL transcript for any non-zero exit_code. Returns False on any error."""
    if not transcript_path or not os.path.isfile(transcript_path):
        return False
    try:
        with open(transcript_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except Exception:
                    continue
                ec = entry.get("tool_response", {}).get("exit_code")
                if isinstance(ec, int) and ec != 0:
                    return True
    except Exception:
        pass
    return False


def subagent_had_repeated_failures(tool_response):
    """Check if subagent response indicates repeated failures (3+ errors or loop detected)."""
    if not tool_response:
        return False
    error_count = tool_response.get("error_count", 0)
    if isinstance(error_count, int) and error_count >= 3:
        return True
    result_text = str(tool_response.get("result", ""))
    loop_indicators = ["tried multiple times", "same error", "still failing", "repeated attempt"]
    return any(ind in result_text.lower() for ind in loop_indicators)


def match_rule(rule, event_name, tool_name, tool_input, tool_response, transcript_path):
    """Return True if the rule matches this event."""
    if rule.get("event") != event_name:
        return False

    m = rule.get("match", {})

    # Tool name match (regex fullmatch, only for tool events)
    rule_tool = rule.get("tool", "")
    if rule_tool:
        if not tool_name:
            return False
        if not re.fullmatch(rule_tool, tool_name):
            return False

    # exit_code_nonzero
    if m.get("exit_code_nonzero"):
        exit_code = tool_response.get("exit_code") if tool_response else None
        if not isinstance(exit_code, int) or exit_code == 0:
            return False

    # command_regex
    if "command_regex" in m:
        command = tool_input.get("command", "") if tool_input else ""
        if not re.search(m["command_regex"], command):
            return False

    # file_path_regex
    if "file_path_regex" in m:
        file_path = tool_input.get("file_path", "") if tool_input else ""
        if not re.search(m["file_path_regex"], file_path):
            return False

    # had_failure_in_session (Stop event)
    if "had_failure_in_session" in m:
        if m["had_failure_in_session"] and not had_failure_in_session(transcript_path):
            return False

    # subagent_had_repeated_failures (SubagentStop event)
    if "subagent_had_repeated_failures" in m:
        if m["subagent_had_repeated_failures"] and not subagent_had_repeated_failures(tool_response):
            return False

    return True


def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    event_name = data.get("hook_event_name", "")
    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input") or {}
    tool_response = data.get("tool_response") or {}
    transcript_path = data.get("transcript_path", "")

    rules = load_rules()

    for rule in rules:
        if match_rule(rule, event_name, tool_name, tool_input, tool_response, transcript_path):
            suggest = rule.get("suggest", "")
            reason = rule.get("reason", "")
            # Include contextual detail when available
            detail = ""
            cmd = tool_input.get("command", "")
            fp = tool_input.get("file_path", "")
            if cmd:
                detail = f" in `{cmd}`"
            elif fp:
                detail = f" in `{fp}`"
            message = (
                f"Auto-dispatch suggests: {suggest}\n\n"
                f"Reason: {reason}{detail}"
            )
            print(json.dumps({"systemMessage": message}))
            sys.exit(0)

    sys.exit(0)


if __name__ == "__main__":
    main()

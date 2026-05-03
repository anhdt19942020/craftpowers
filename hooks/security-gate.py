#!/usr/bin/env python3
"""
PreToolUse hook: Block dangerous Bash commands before execution.
Input: JSON via stdin. Output: block decision via stdout + exit 2.
"""
import json
import re
import sys

DANGEROUS_PATTERNS = [
    (r'\brm\s+-[a-zA-Z]*r[a-zA-Z]*f\b', "Recursive force delete (rm -rf)"),
    (r'\brm\s+-[a-zA-Z]*f[a-zA-Z]*r\b', "Recursive force delete (rm -fr)"),
    (r'\bsudo\s+rm\b', "Privileged delete (sudo rm)"),
    (r'git\s+push\s+[^|&;]*--force(?!\s*-with-lease)', "Force push without --force-with-lease"),
    (r'git\s+push\s+[^|&;]*\s-f\b', "Force push (-f flag)"),
    (r'git\s+push\s+[^|&;]*\s-f$', "Force push (-f flag)"),
    (r'\bDROP\s+TABLE\b', "Destructive SQL: DROP TABLE"),
    (r'\bDROP\s+DATABASE\b', "Destructive SQL: DROP DATABASE"),
    (r'\bDROP\s+SCHEMA\b', "Destructive SQL: DROP SCHEMA"),
    (r'\bchmod\s+777\b', "World-writable permissions (chmod 777)"),
    (r'curl\s+[^|]*\|\s*(?:sudo\s+)?(?:bash|sh)\b', "Piped remote execution (curl | bash)"),
    (r'wget\s+[^|]*\|\s*(?:sudo\s+)?(?:bash|sh)\b', "Piped remote execution (wget | bash)"),
    (r'\bdd\s+[^|&;]*\bof=/dev/[sh]d[a-z]\b', "Raw disk overwrite (dd to block device)"),
    (r'>\s*/dev/sd[a-z]\b', "Raw disk write"),
    (r'git\s+reset\s+--hard\s+HEAD~[2-9][0-9]*', "Hard reset of 20+ commits"),
    (r'\btruncate\s+[^|&;]*--size\s+0\b', "Truncate file to zero"),
    (r':(){:|:&};:', "Fork bomb"),
]

def main():
    try:
        data = json.load(sys.stdin)
    except Exception:
        sys.exit(0)

    tool_input = data.get("tool_input", {})
    command = tool_input.get("command", "") if isinstance(tool_input, dict) else ""

    for pattern, reason in DANGEROUS_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            print(json.dumps({
                "decision": "block",
                "reason": f"[craftpowers/security-gate] Blocked: {reason}\nCommand: {command[:300]}"
            }))
            sys.exit(2)

    sys.exit(0)

if __name__ == "__main__":
    main()

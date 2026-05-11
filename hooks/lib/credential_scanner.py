"""Credential scanner for written/edited file content (ported from hooks/credential-scanner.py).

scan_content(content, file_path) -> list[str]   # each entry: "  Line N [label]: preview"
build_warning(file_path, findings) -> str       # "" when no findings
"""
from __future__ import annotations
import os
import re

# Copied verbatim from hooks/credential-scanner.py — keep both in sync.
CREDENTIAL_PATTERNS = [
    (r'(?i)(?:password|passwd|pwd)\s*=\s*["\'](?!\s*["\']|.*\$\{)([^"\']{6,})["\']', "Hardcoded password"),
    (r'(?i)(?:api_key|apikey|api_secret|access_key)\s*=\s*["\']([a-zA-Z0-9_\-]{16,})["\']', "Hardcoded API key"),
    (r'\bAKIA[0-9A-Z]{16}\b', "AWS Access Key ID"),
    (r'(?i)aws_secret_access_key\s*[=:]\s*["\']?([A-Za-z0-9/+=]{40})["\']?', "AWS Secret Access Key"),
    (r'\bsk-[a-zA-Z0-9]{32,}\b', "OpenAI API key"),
    (r'\bsk-ant-[a-zA-Z0-9\-_]{32,}\b', "Anthropic API key"),
    (r'-----BEGIN\s+(?:RSA\s+|EC\s+|OPENSSH\s+)?PRIVATE\s+KEY-----', "Private key"),
    (r'(?i)(?:secret|token)\s*=\s*["\']([a-zA-Z0-9_\-\.]{20,})["\']', "Hardcoded secret/token"),
    (r'\bghp_[a-zA-Z0-9]{36}\b', "GitHub Personal Access Token"),
    (r'\bxoxb-[0-9]{11}-[0-9]{11}-[a-zA-Z0-9]{24}\b', "Slack Bot Token"),
    (r'\bACo[a-f0-9]{32}\b', "Twilio Account SID"),
]

FALSE_POSITIVE_MARKERS = [
    r'\$\{', r'\$[A-Z_]+', r'process\.env', r'os\.environ', r'getenv\(',
    r'YOUR_', r'<YOUR', r'REPLACE_ME', r'CHANGEME', r'example\.com',
    r'placeholder', r'dummy', r'fake', r'test_secret', r'mock_',
    r'#\s*noqa', r'nosec',
]

FP_RE = re.compile('|'.join(FALSE_POSITIVE_MARKERS), re.IGNORECASE)

SKIP_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.woff',
                   '.woff2', '.ttf', '.eot', '.pdf', '.zip', '.tar', '.gz',
                   '.lock', '.sum'}


def scan_content(content: str, file_path: str) -> list[str]:
    if not content or not file_path:
        return []
    ext = os.path.splitext(file_path)[1].lower()
    if ext in SKIP_EXTENSIONS:
        return []
    findings: list[str] = []
    for i, line in enumerate(content.splitlines(), 1):
        if FP_RE.search(line):
            continue
        for pattern, label in CREDENTIAL_PATTERNS:
            if re.search(pattern, line):
                preview = line.strip()[:100]
                findings.append(f"  Line {i} [{label}]: {preview}")
                break
        if len(findings) >= 5:
            break
    return findings


def build_warning(file_path: str, findings: list[str]) -> str:
    if not findings:
        return ""
    return (
        "<important-reminder>STOP. You MUST tell the user the following before continuing:\n\n"
        f"⚠️ [craftpowers/credential-scanner] Hardcoded credentials detected in `{file_path}`:\n"
        + "\n".join(findings)
        + "\n\nThese must be moved to environment variables. Do NOT proceed without warning the user.</important-reminder>"
    )

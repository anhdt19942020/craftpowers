"""WorktreeCreate hook — auto-provision worktrees with project setup."""
from __future__ import annotations
import json
import os
import subprocess
import shutil


def provision(data: dict, base_dir: str | None = None) -> str | None:
    """After worktree creation, run project setup if needed.

    Returns a systemMessage with setup status, or None.
    """
    worktree_path = data.get("worktree_path", "")
    if not worktree_path or not os.path.isdir(worktree_path):
        return None

    messages = []

    # Copy .env if exists in main worktree
    if base_dir:
        env_src = os.path.join(base_dir, ".env")
        env_dst = os.path.join(worktree_path, ".env")
        if os.path.isfile(env_src) and not os.path.isfile(env_dst):
            shutil.copy2(env_src, env_dst)
            messages.append(".env copied")

    # Check for package.json and suggest install
    pkg = os.path.join(worktree_path, "package.json")
    if os.path.isfile(pkg):
        messages.append("package.json found — run npm/pnpm install")

    if messages:
        return f"[craftpowers/worktree-provision] Worktree ready at {worktree_path}. {'; '.join(messages)}."
    return None

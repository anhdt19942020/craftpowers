#!/usr/bin/env python3
"""
worktree-spawn.py <task-id>

Creates .worktrees/task-<id> from current HEAD on branch impl/task-<id>.
Prints absolute path to stdout. Idempotent: if worktree exists, just prints path.
"""

import subprocess
import sys
from pathlib import Path


def get_repo_root() -> Path:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True, text=True, check=True
    )
    return Path(result.stdout.strip())


def worktree_exists(repo_root: Path, task_id: str) -> bool:
    worktree_path = repo_root / ".worktrees" / f"task-{task_id}"
    return worktree_path.exists()


def list_worktrees(repo_root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "worktree", "list", "--porcelain"],
        capture_output=True, text=True, check=True,
        cwd=str(repo_root)
    )
    paths = []
    for line in result.stdout.splitlines():
        if line.startswith("worktree "):
            paths.append(line[len("worktree "):])
    return paths


def branch_exists(repo_root: Path, branch: str) -> bool:
    result = subprocess.run(
        ["git", "branch", "--list", branch],
        capture_output=True, text=True, check=True,
        cwd=str(repo_root)
    )
    return bool(result.stdout.strip())


def spawn(task_id: str) -> str:
    repo_root = get_repo_root()
    worktree_dir = repo_root / ".worktrees" / f"task-{task_id}"
    branch = f"impl/task-{task_id}"

    # Idempotent: if worktree already registered with git, just print path
    existing = list_worktrees(repo_root)
    if str(worktree_dir) in existing or worktree_dir.exists():
        return str(worktree_dir)

    # Create branch if it doesn't exist, then add worktree
    worktree_dir.parent.mkdir(parents=True, exist_ok=True)

    if branch_exists(repo_root, branch):
        subprocess.run(
            ["git", "worktree", "add", str(worktree_dir), branch],
            check=True, cwd=str(repo_root)
        )
    else:
        subprocess.run(
            ["git", "worktree", "add", "-b", branch, str(worktree_dir)],
            check=True, cwd=str(repo_root)
        )

    return str(worktree_dir)


def main() -> None:
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <task-id>", file=sys.stderr)
        sys.exit(1)

    task_id = sys.argv[1]
    path = spawn(task_id)
    print(path)


if __name__ == "__main__":
    main()

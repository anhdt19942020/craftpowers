#!/usr/bin/env python3
"""
worktree-cleanup.py <task-id> [--merge-to <branch>] [--force-branch]

Without --merge-to: dry-run, prints what would happen.
With --merge-to <branch>: cherry-picks implementor's commits into target branch,
then removes the worktree and deletes the impl branch.

Safety:
- Refuses to remove a worktree that has uncommitted changes (commit/stash first).
- Uses `git branch -d` (refuses unmerged); pass --force-branch to use -D.
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


def get_impl_branch(task_id: str) -> str:
    return f"impl/task-{task_id}"


def get_worktree_path(repo_root: Path, task_id: str) -> Path:
    return repo_root / ".worktrees" / f"task-{task_id}"


def get_commits_ahead(repo_root: Path, branch: str, base: str) -> list[str]:
    """Return list of commit SHAs on branch not in base."""
    result = subprocess.run(
        ["git", "log", "--format=%H", f"{base}..{branch}"],
        capture_output=True, text=True, check=True,
        cwd=str(repo_root)
    )
    shas = [s.strip() for s in result.stdout.splitlines() if s.strip()]
    return list(reversed(shas))  # oldest first


def worktree_registered(repo_root: Path, worktree_path: Path) -> bool:
    result = subprocess.run(
        ["git", "worktree", "list", "--porcelain"],
        capture_output=True, text=True, check=True,
        cwd=str(repo_root)
    )
    for line in result.stdout.splitlines():
        if line.startswith("worktree ") and line[len("worktree "):] == str(worktree_path):
            return True
    return False


def branch_exists(repo_root: Path, branch: str) -> bool:
    result = subprocess.run(
        ["git", "branch", "--list", branch],
        capture_output=True, text=True, check=True,
        cwd=str(repo_root)
    )
    return bool(result.stdout.strip())


def dry_run(task_id: str) -> None:
    repo_root = get_repo_root()
    branch = get_impl_branch(task_id)
    worktree_path = get_worktree_path(repo_root, task_id)

    print(f"[dry-run] Would perform the following actions for task-{task_id}:")
    print(f"  1. Remove git worktree: {worktree_path}")
    if branch_exists(repo_root, branch):
        print(f"  2. Delete branch: {branch}")
    else:
        print(f"  2. Branch {branch!r} does not exist — skip delete")
    print()
    print("Run with --merge-to <branch> to execute.")


def merge_and_cleanup(task_id: str, target_branch: str, force_branch: bool = False) -> None:
    repo_root = get_repo_root()
    branch = get_impl_branch(task_id)
    worktree_path = get_worktree_path(repo_root, task_id)

    if not branch_exists(repo_root, branch):
        print(f"Branch {branch!r} does not exist. Nothing to do.", file=sys.stderr)
        sys.exit(1)

    # Cherry-pick commits from impl branch into target
    commits = get_commits_ahead(repo_root, branch, target_branch)
    if commits:
        print(f"Cherry-picking {len(commits)} commit(s) from {branch} into {target_branch}...")
        subprocess.run(
            ["git", "checkout", target_branch],
            check=True, cwd=str(repo_root)
        )
        subprocess.run(
            ["git", "cherry-pick"] + commits,
            check=True, cwd=str(repo_root)
        )
        print("Cherry-pick complete.")
    else:
        print(f"No commits ahead of {target_branch} on {branch}. Nothing to merge.")

    # Remove worktree — refuse if dirty to avoid silent data loss
    if worktree_registered(repo_root, worktree_path) or worktree_path.exists():
        status = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True, text=True, cwd=str(worktree_path)
        )
        if status.stdout.strip():
            print(f"ABORT: worktree {worktree_path} has uncommitted changes:")
            print(status.stdout)
            print("Commit, stash, or discard manually before re-running cleanup.")
            sys.exit(2)
        print(f"Removing worktree at {worktree_path}...")
        subprocess.run(
            ["git", "worktree", "remove", str(worktree_path)],
            check=True, cwd=str(repo_root)
        )
        print("Worktree removed.")

    # Delete impl branch — use -d (refuses unmerged); user must pass --force-branch for -D
    if branch_exists(repo_root, branch):
        delete_flag = "-D" if force_branch else "-d"
        print(f"Deleting branch {branch} ({delete_flag})...")
        subprocess.run(
            ["git", "branch", delete_flag, branch],
            check=True, cwd=str(repo_root)
        )
        print(f"Branch {branch} deleted.")


def main() -> None:
    args = sys.argv[1:]

    if not args:
        print(f"Usage: {sys.argv[0]} <task-id> [--merge-to <branch>]", file=sys.stderr)
        sys.exit(1)

    task_id = args[0]
    merge_to = None
    force_branch = False
    remaining = args[1:]

    while remaining:
        flag = remaining[0]
        if flag == "--merge-to" and len(remaining) >= 2:
            merge_to = remaining[1]
            remaining = remaining[2:]
        elif flag == "--force-branch":
            force_branch = True
            remaining = remaining[1:]
        else:
            print(f"Unexpected arguments: {remaining}", file=sys.stderr)
            print(f"Usage: {sys.argv[0]} <task-id> [--merge-to <branch>] [--force-branch]", file=sys.stderr)
            sys.exit(1)

    if merge_to:
        merge_and_cleanup(task_id, merge_to, force_branch=force_branch)
    else:
        dry_run(task_id)


if __name__ == "__main__":
    main()

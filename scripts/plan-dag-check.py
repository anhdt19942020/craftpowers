#!/usr/bin/env python3
"""
plan-dag-check.py <plan.md>

Validates the Task DAG in a plan markdown file.
- Parses `### Task N:` headers and `**Depends on:** Task M, Task K` lines.
- Asserts: every referenced task exists; no cycles; no self-loops.
- Exit 0 if valid, 1 if invalid (with reason on stderr).
"""

import re
import sys
from pathlib import Path


TASK_HEADER_RE = re.compile(r"^###\s+Task\s+(\d+)\s*[:.]", re.MULTILINE)
DEPENDS_RE = re.compile(
    r"\*\*Depends on:\*\*\s*(.+?)(?:\n|$)", re.IGNORECASE
)
TASK_REF_RE = re.compile(r"Task\s+(\d+)", re.IGNORECASE)


def parse_plan(text: str) -> dict[int, set[int]]:
    """Returns {task_id: {dep_id, ...}}."""
    headers = list(TASK_HEADER_RE.finditer(text))
    if not headers:
        raise ValueError("No `### Task N:` headers found in plan.")

    task_ids = [int(m.group(1)) for m in headers]
    if len(set(task_ids)) != len(task_ids):
        dupes = [t for t in task_ids if task_ids.count(t) > 1]
        raise ValueError(f"Duplicate task IDs: {sorted(set(dupes))}")

    deps: dict[int, set[int]] = {}
    for i, header in enumerate(headers):
        tid = int(header.group(1))
        start = header.end()
        end = headers[i + 1].start() if i + 1 < len(headers) else len(text)
        body = text[start:end]

        match = DEPENDS_RE.search(body)
        if not match:
            raise ValueError(
                f"Task {tid}: missing `**Depends on:**` line (use `none` for wave-1)."
            )
        raw = match.group(1).strip()
        if raw.lower() in ("none", "-", "n/a", ""):
            deps[tid] = set()
        else:
            deps[tid] = {int(m.group(1)) for m in TASK_REF_RE.finditer(raw)}

    return deps


def detect_cycle(deps: dict[int, set[int]]) -> list[int] | None:
    """Returns the first cycle found (as a list of task IDs), or None."""
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {t: WHITE for t in deps}
    path: list[int] = []

    def dfs(node: int) -> list[int] | None:
        color[node] = GRAY
        path.append(node)
        for parent in deps.get(node, set()):
            if color.get(parent, WHITE) == GRAY:
                idx = path.index(parent)
                return path[idx:] + [parent]
            if color.get(parent, WHITE) == WHITE:
                cycle = dfs(parent)
                if cycle:
                    return cycle
        color[node] = BLACK
        path.pop()
        return None

    for t in deps:
        if color[t] == WHITE:
            cycle = dfs(t)
            if cycle:
                return cycle
    return None


def validate(deps: dict[int, set[int]]) -> list[str]:
    """Returns list of error messages (empty if valid)."""
    errors: list[str] = []
    tasks = set(deps.keys())

    for tid, parents in deps.items():
        if tid in parents:
            errors.append(f"Task {tid}: self-dependency.")
        missing = parents - tasks
        if missing:
            errors.append(
                f"Task {tid}: depends on undefined task(s) {sorted(missing)}."
            )

    cycle = detect_cycle(deps)
    if cycle:
        errors.append(
            "Cycle detected: " + " -> ".join(f"Task {t}" for t in cycle)
        )

    return errors


def main() -> None:
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <plan.md>", file=sys.stderr)
        sys.exit(2)

    plan_path = Path(sys.argv[1])
    if not plan_path.is_file():
        print(f"Plan file not found: {plan_path}", file=sys.stderr)
        sys.exit(2)

    text = plan_path.read_text(encoding="utf-8")

    try:
        deps = parse_plan(text)
    except ValueError as e:
        print(f"PARSE ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    errors = validate(deps)
    if errors:
        for e in errors:
            print(f"INVALID: {e}", file=sys.stderr)
        sys.exit(1)

    wave_one = sorted(t for t, p in deps.items() if not p)
    print(f"OK: {len(deps)} tasks, DAG valid.")
    print(f"Wave 1 (no dependencies): {wave_one}")
    print(f"Edges: {sum(len(p) for p in deps.values())}")


if __name__ == "__main__":
    main()

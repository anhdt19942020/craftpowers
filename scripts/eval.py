"""
eval.py — Human-driven A/B eval harness for mankit skills.

Usage:
    python scripts/eval.py <skill-name> [--baseline <git-ref>]

Loads fixtures from evals/<skill-name>/*.json, prints paste-ready eval cards,
collects human pass/fail judgement interactively, writes results to
evals/<skill-name>/results-<timestamp>.md
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Ensure UTF-8 output on Windows consoles that default to cp1252
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO_ROOT = Path(__file__).parent.parent


def find_skill_content(skill_name: str, git_ref: str | None = None) -> str:
    skill_path = REPO_ROOT / "skills" / skill_name / "SKILL.md"
    if git_ref:
        result = subprocess.run(
            ["git", "show", f"{git_ref}:skills/{skill_name}/SKILL.md"],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        if result.returncode != 0:
            print(f"[WARN] Could not load skill from ref {git_ref}: {result.stderr.strip()}")
            return "(skill content unavailable at baseline ref)"
        return result.stdout
    if not skill_path.exists():
        print(f"[ERROR] Skill not found: {skill_path}")
        sys.exit(1)
    return skill_path.read_text(encoding="utf-8")


def find_agents_using_skill(skill_name: str) -> list[str]:
    agents_dir = REPO_ROOT / "agents"
    matches = []
    for agent_file in sorted(agents_dir.glob("*.md")):
        content = agent_file.read_text(encoding="utf-8")
        for line in content.splitlines():
            if line.strip().startswith("skills:") and skill_name in line:
                matches.append(agent_file.stem)
                break
    return matches


def load_fixtures(skill_name: str) -> list[dict]:
    fixtures_dir = REPO_ROOT / "evals" / skill_name
    if not fixtures_dir.exists():
        print(f"[ERROR] No fixtures directory found: {fixtures_dir}")
        sys.exit(1)
    fixtures = []
    for fixture_file in sorted(fixtures_dir.glob("*.json")):
        with open(fixture_file, encoding="utf-8") as f:
            data = json.load(f)
        data["_file"] = fixture_file.name
        fixtures.append(data)
    if not fixtures:
        print(f"[ERROR] No fixture JSON files found in {fixtures_dir}")
        sys.exit(1)
    return fixtures


def print_separator(char="=", width=72):
    print(char * width)


def print_eval_card(
    index: int,
    total: int,
    fixture: dict,
    skill_content: str,
    baseline_content: str | None,
    agents: list[str],
):
    print_separator()
    print(f"  EVAL CARD {index}/{total} — {fixture['_file']}")
    print_separator()

    if agents:
        print(f"Agents using this skill: {', '.join(agents)}")
    else:
        print("Agents using this skill: (none found)")
    print()

    print("-- SKILL CONTENT (paste together with the prompt) ---------------")
    print(skill_content.strip())
    print()

    if baseline_content is not None:
        print("-- BASELINE SKILL CONTENT ---------------------------------------")
        print(baseline_content.strip())
        print()

    print("-- PROMPT (paste into Claude) -----------------------------------")
    print(fixture["prompt"])
    print()

    expected = fixture.get("expected_signals", [])
    forbidden = fixture.get("forbidden_signals", [])
    if expected:
        print("-- EXPECTED SIGNALS (look for these in the response) ------------")
        for sig in expected:
            print(f"  + {sig}")
        print()
    if forbidden:
        print("-- FORBIDDEN SIGNALS (these should NOT appear) ------------------")
        for sig in forbidden:
            print(f"  - {sig}")
        print()


def collect_judgement(index: int, total: int) -> bool:
    while True:
        try:
            answer = input(f"Fixture {index}/{total} — Pass or Fail? [p/f]: ").strip().lower()
        except EOFError:
            answer = "p"
        if answer in ("p", "pass", "y", "yes"):
            return True
        if answer in ("f", "fail", "n", "no"):
            return False
        print("  Please enter 'p' (pass) or 'f' (fail).")


def write_results(skill_name: str, results: list[dict], timestamp: str):
    out_dir = REPO_ROOT / "evals" / skill_name
    out_file = out_dir / f"results-{timestamp}.md"

    passed = sum(1 for r in results if r["passed"])
    total = len(results)
    pass_rate = f"{passed}/{total} ({100 * passed // total}%)" if total else "0/0"

    lines = [
        f"# Eval Results — {skill_name}",
        f"",
        f"Run: {timestamp}  ",
        f"Pass rate: **{pass_rate}**",
        f"",
        f"| # | Fixture | Result |",
        f"|---|---------|--------|",
    ]
    for i, r in enumerate(results, 1):
        result_str = "PASS" if r["passed"] else "FAIL"
        lines.append(f"| {i} | {r['fixture']} | {result_str} |")

    lines.append("")
    out_file.write_text("\n".join(lines), encoding="utf-8")
    print()
    print(f"Results written to: {out_file}")
    return out_file


def main():
    parser = argparse.ArgumentParser(description="Mankit skill eval harness")
    parser.add_argument("skill_name", help="Skill name (e.g. engineering-principles)")
    parser.add_argument(
        "--baseline",
        metavar="GIT_REF",
        help="Git ref to load baseline skill content from (e.g. HEAD~1, main)",
    )
    args = parser.parse_args()

    skill_name = args.skill_name
    baseline_ref = args.baseline

    skill_content = find_skill_content(skill_name)
    baseline_content = find_skill_content(skill_name, git_ref=baseline_ref) if baseline_ref else None
    agents = find_agents_using_skill(skill_name)
    fixtures = load_fixtures(skill_name)

    total = len(fixtures)
    results = []

    print()
    print(f"Eval: {skill_name}  |  {total} fixture(s)")
    if baseline_ref:
        print(f"Baseline ref: {baseline_ref}")
    print()

    for i, fixture in enumerate(fixtures, 1):
        print_eval_card(i, total, fixture, skill_content, baseline_content, agents)
        passed = collect_judgement(i, total)
        results.append({"fixture": fixture["_file"], "passed": passed})
        print()

    passed_count = sum(1 for r in results if r["passed"])
    print_separator()
    print(f"  SUMMARY: {passed_count}/{total} passed")
    print_separator()

    timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    write_results(skill_name, results, timestamp)


if __name__ == "__main__":
    main()

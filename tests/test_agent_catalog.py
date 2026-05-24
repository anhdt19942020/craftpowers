"""Catalog CI tests — validate agent filesystem vs roles.json parity.

Checks:
1. Every agents/*.md has valid frontmatter (name, description, model)
2. Frontmatter `name` matches the filename stem
3. Every roles.json `roles` value references an existing agents/<value>.md
4. Every roles.json `models` key references an existing agents/<key>.md
5. Agent count parity: agents/*.md count == roles.json `roles` count
"""
from __future__ import annotations
import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
AGENTS_DIR = REPO_ROOT / "agents"
ROLES_JSON = AGENTS_DIR / "roles.json"

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---", re.DOTALL)
FIELD_RE = re.compile(r"^(\w[\w-]*):\s*(.+)$", re.MULTILINE)


def _agent_files() -> list[Path]:
    return sorted(AGENTS_DIR.glob("*.md"))


def _parse_frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}
    fields: dict[str, str] = {}
    for key, val in FIELD_RE.findall(m.group(1)):
        fields[key] = val.strip()
    return fields


def _roles_data() -> dict:
    return json.loads(ROLES_JSON.read_text(encoding="utf-8"))


# ── Tests ──────────────────────────────────────────────────────────────────────

def test_agents_dir_exists():
    assert AGENTS_DIR.is_dir(), f"agents/ directory not found at {AGENTS_DIR}"


def test_roles_json_exists():
    assert ROLES_JSON.is_file(), f"roles.json not found at {ROLES_JSON}"


def test_every_agent_has_frontmatter():
    missing = []
    for f in _agent_files():
        fm = _parse_frontmatter(f)
        if not fm:
            missing.append(f.name)
    assert not missing, f"No frontmatter found in: {missing}"


def test_every_agent_has_required_fields():
    errors = []
    for f in _agent_files():
        fm = _parse_frontmatter(f)
        for field in ("name", "description", "model"):
            if field not in fm:
                errors.append(f"{f.name}: missing `{field}`")
    assert not errors, "\n".join(errors)


def test_frontmatter_name_matches_filename():
    mismatches = []
    for f in _agent_files():
        fm = _parse_frontmatter(f)
        name = fm.get("name", "")
        if name != f.stem:
            mismatches.append(f"{f.name}: frontmatter name={name!r}, expected {f.stem!r}")
    assert not mismatches, "\n".join(mismatches)


def test_roles_json_structure():
    data = _roles_data()
    assert "roles" in data, "roles.json missing `roles` key"
    assert "models" in data, "roles.json missing `models` key"
    assert isinstance(data["roles"], dict), "`roles` must be a dict"
    assert isinstance(data["models"], dict), "`models` must be a dict"


def test_roles_reference_existing_agents():
    data = _roles_data()
    missing = []
    for role, agent_name in data.get("roles", {}).items():
        agent_file = AGENTS_DIR / f"{agent_name}.md"
        if not agent_file.exists():
            missing.append(f"roles[{role!r}] → {agent_name!r}: agents/{agent_name}.md not found")
    assert not missing, "\n".join(missing)


def test_models_reference_existing_agents():
    data = _roles_data()
    missing = []
    for agent_name in data.get("models", {}):
        agent_file = AGENTS_DIR / f"{agent_name}.md"
        if not agent_file.exists():
            missing.append(f"models[{agent_name!r}]: agents/{agent_name}.md not found")
    assert not missing, "\n".join(missing)


def test_agent_count_parity():
    agent_files = _agent_files()
    data = _roles_data()
    roles_count = len(data.get("roles", {}))
    files_count = len(agent_files)
    assert files_count == roles_count, (
        f"Agent count mismatch: {files_count} .md files in agents/ "
        f"but {roles_count} entries in roles.json. "
        f"Files: {[f.stem for f in agent_files]}"
    )


def test_roles_model_matches_agent_frontmatter():
    data = _roles_data()
    mismatches = []
    for agent_name, expected_model in data.get("models", {}).items():
        agent_file = AGENTS_DIR / f"{agent_name}.md"
        if not agent_file.exists():
            continue
        fm = _parse_frontmatter(agent_file)
        actual_model = fm.get("model", "")
        if actual_model != expected_model:
            mismatches.append(
                f"{agent_name}: roles.json model={expected_model!r} "
                f"but frontmatter model={actual_model!r}"
            )
    assert not mismatches, "\n".join(mismatches)

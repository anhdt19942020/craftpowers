"""
generate-codex.py — Generate mankit agents + skills into Codex CLI global format.

Usage:
    python scripts/generate-codex.py [--dry-run]

Output:
    ~/.codex/AGENTS.md     — merged agent instructions
    ~/.codex/config.toml   — agent role entries
    ~/.agents/skills/*/    — all skills with SKILL.md
"""

import argparse
import os
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
TOML_SECTION_RE = re.compile(r"^\[(.+?)\]\s*$")
LEGACY_COMMAND_SKILL_PREFIX = "source-command-"
MANAGED_TOML_PREFIXES = ("agents.",)


def resolve_mankit_root() -> Path:
    env = os.environ.get("CLAUDE_PLUGIN_ROOT")
    if env:
        return Path(env)
    return Path(__file__).parent.parent


def parse_frontmatter(text: str) -> tuple[dict, str]:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    raw = m.group(1)
    body = text[m.end():]
    meta: dict = {}
    current_key = None
    current_val_lines: list[str] = []

    def flush():
        if current_key is not None:
            val = "\n".join(current_val_lines).strip()
            if val.startswith("[") and val.endswith("]"):
                meta[current_key] = [
                    v.strip().strip("'\"") for v in val[1:-1].split(",") if v.strip()
                ]
            else:
                meta[current_key] = val

    for line in raw.splitlines():
        colon_match = re.match(r"^(\w[\w-]*):\s*(.*)", line)
        if colon_match and not line.startswith("  "):
            flush()
            current_key = colon_match.group(1)
            val = colon_match.group(2).strip()
            if val == "|":
                current_val_lines = []
            else:
                current_val_lines = [val]
        else:
            current_val_lines.append(line)
    flush()
    return meta, body


def load_roles(root: Path) -> dict:
    import json
    roles_path = root / "agents" / "roles.json"
    with open(roles_path, encoding="utf-8") as f:
        return json.load(f)


def generate_agents_md(root: Path, roles: dict) -> str:
    agents_dir = root / "agents"
    role_lookup = {v: k for k, v in roles.get("roles", {}).items()}
    models = roles.get("models", {})
    sections: list[str] = []

    for agent_file in sorted(agents_dir.glob("*.md")):
        text = agent_file.read_text(encoding="utf-8")
        meta, body = parse_frontmatter(text)
        name = meta.get("name", agent_file.stem)
        aliases = meta.get("aliases", [])
        if isinstance(aliases, str):
            aliases = [aliases]
        model = meta.get("model", models.get(name, "unknown"))
        description = meta.get("description", "")
        role = role_lookup.get(name, "")

        title_parts = [f"## {name}"]
        if aliases:
            title_parts.append(f"({', '.join(aliases)})")
        if role:
            title_parts.append(f"— role: {role}")
        title_parts.append(f"— {model}")
        title = " ".join(title_parts)

        section = f"{title}\n\n{description}\n\n{body.strip()}"
        sections.append(section)

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    header = f"# Mankit Agents — Generated for Codex CLI\n\nGenerated: {now}\n\n"
    return header + "\n\n---\n\n".join(sections) + "\n"


def _is_managed_section(section_name: str) -> bool:
    return any(section_name.startswith(p) for p in MANAGED_TOML_PREFIXES)


def parse_toml_sections(text: str) -> list[tuple[str | None, list[str]]]:
    """Parse TOML into (section_name, lines) pairs. None = top-level/comments."""
    sections: list[tuple[str | None, list[str]]] = []
    current_name: str | None = None
    current_lines: list[str] = []

    for line in text.splitlines():
        m = TOML_SECTION_RE.match(line)
        if m:
            sections.append((current_name, current_lines))
            current_name = m.group(1)
            current_lines = [line]
        else:
            current_lines.append(line)

    sections.append((current_name, current_lines))
    return sections


def merge_config_toml(generated: str, existing: str) -> str:
    """Merge generated config with existing, preserving user-defined sections."""
    if not existing.strip():
        return generated

    existing_sections = parse_toml_sections(existing)

    user_sections: list[tuple[str, list[str]]] = []
    for name, lines in existing_sections:
        if name is not None and not _is_managed_section(name):
            user_sections.append((name, lines))

    if not user_sections:
        return generated

    result = generated.rstrip("\n")
    result += "\n\n"
    for _name, lines in user_sections:
        result += "\n".join(lines) + "\n"

    return result


def generate_config_toml(roles: dict, agents_meta: dict[str, dict]) -> str:
    lines = [
        "# Mankit agent roles — Generated for Codex CLI",
        f"# Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}",
        "",
    ]
    for role, agent_name in sorted(roles.get("roles", {}).items()):
        meta = agents_meta.get(agent_name, {})
        desc = meta.get("description", "")
        first_line = desc.split("\n")[0].strip() if desc else agent_name
        if len(first_line) > 120:
            first_line = first_line[:117] + "..."
        escaped = first_line.replace("\\", "\\\\").replace('"', '\\"')
        lines.append(f"[agents.{role}]")
        lines.append(f'description = "{escaped}"')
        lines.append("")
    return "\n".join(lines) + "\n"


def collect_agents_meta(root: Path) -> dict[str, dict]:
    agents_dir = root / "agents"
    result: dict[str, dict] = {}
    for agent_file in sorted(agents_dir.glob("*.md")):
        text = agent_file.read_text(encoding="utf-8")
        meta, _ = parse_frontmatter(text)
        name = meta.get("name", agent_file.stem)
        result[name] = meta
    return result


def copy_skills(root: Path, target: Path, dry_run: bool = False) -> int:
    skills_dir = root / "skills"
    count = 0
    for skill_dir in sorted(skills_dir.iterdir()):
        if not skill_dir.is_dir():
            continue
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            print(f"  [SKIP] {skill_dir.name}/ — no SKILL.md")
            continue
        dest_dir = target / skill_dir.name
        if dry_run:
            print(f"  [DRY] Would copy {skill_dir.name}/SKILL.md → {dest_dir}")
        else:
            dest_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy2(skill_md, dest_dir / "SKILL.md")
        refs_dir = skill_dir / "references"
        if refs_dir.is_dir():
            dest_refs = dest_dir / "references"
            if dry_run:
                print(f"  [DRY] Would copy {skill_dir.name}/references/ → {dest_refs}")
            else:
                if dest_refs.exists():
                    shutil.rmtree(dest_refs)
                shutil.copytree(refs_dir, dest_refs)
        count += 1
    return count


def unquote_frontmatter_scalar(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def render_command_skill(command_path: Path) -> tuple[str, str]:
    text = command_path.read_text(encoding="utf-8")
    meta, body = parse_frontmatter(text)
    command_name = command_path.stem
    description = unquote_frontmatter_scalar(meta.get("description", f"Run /{command_name}."))
    escaped_description = description.replace('"', '\\"')
    skill = f"""---
name: "{command_name}"
description: "{escaped_description}"
---

# {command_name}

Use this skill when the user asks to run `/{command_name}` or `${command_name}`.

## Command Template

{body.strip()}
"""
    return command_name, skill


def remove_legacy_command_skill(target: Path, command_name: str, dry_run: bool) -> bool:
    legacy_dir = target / f"{LEGACY_COMMAND_SKILL_PREFIX}{command_name}"
    if not legacy_dir.exists():
        return False
    if dry_run:
        print(f"  [DRY] Would remove legacy {legacy_dir.name}/")
    else:
        shutil.rmtree(legacy_dir)
        print(f"  [REMOVE] legacy {legacy_dir.name}/")
    return True


def copy_command_skills(root: Path, target: Path, dry_run: bool = False) -> tuple[int, int]:
    commands_dir = root / "commands"
    skills_dir = root / "skills"
    count = 0
    removed = 0
    for command_path in sorted(commands_dir.glob("*.md")):
        command_name, skill = render_command_skill(command_path)
        dest_dir = target / command_name
        dest_file = dest_dir / "SKILL.md"
        if remove_legacy_command_skill(target, command_name, dry_run):
            removed += 1
        if (skills_dir / command_name / "SKILL.md").exists():
            print(f"  [SKIP] command {command_name} -> native skill already exists")
            continue
        if dry_run:
            print(f"  [DRY] Would write command {command_name} -> {dest_file}")
        else:
            dest_dir.mkdir(parents=True, exist_ok=True)
            dest_file.write_text(skill, encoding="utf-8")
            print(f"  Wrote command {command_name} -> {dest_file}")
        count += 1
    return count, removed


def main():
    parser = argparse.ArgumentParser(
        description="Generate mankit agents + skills into Codex CLI global format"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be written without writing",
    )
    args = parser.parse_args()

    root = resolve_mankit_root()
    home = Path.home()
    codex_dir = home / ".codex"
    agents_skills_dir = home / ".agents" / "skills"

    print(f"Mankit root: {root}")
    print(f"Codex dir:   {codex_dir}")
    print(f"Skills dir:  {agents_skills_dir}")
    print()

    roles = load_roles(root)
    agents_meta = collect_agents_meta(root)

    agents_md = generate_agents_md(root, roles)
    config_toml = generate_config_toml(roles, agents_meta)

    agents_md_path = codex_dir / "AGENTS.md"
    config_toml_path = codex_dir / "config.toml"

    if args.dry_run:
        print("=== AGENTS.md (preview) ===")
        preview_lines = agents_md.splitlines()[:30]
        print("\n".join(preview_lines))
        if len(agents_md.splitlines()) > 30:
            print(f"  ... ({len(agents_md.splitlines())} total lines)")
        print()
        print("=== config.toml (preview) ===")
        print(config_toml)
        print("=== Skills ===")
        count = copy_skills(root, agents_skills_dir, dry_run=True)
        print("=== Commands as Skills ===")
        command_count, legacy_removed = copy_command_skills(root, agents_skills_dir, dry_run=True)
        print(f"\n[DRY RUN] Would write {len(agents_md)} chars to {agents_md_path}")
        print(f"[DRY RUN] Would write {len(config_toml)} chars to {config_toml_path}")
        print(f"[DRY RUN] Would copy {count} skills to {agents_skills_dir}")
        print(f"[DRY RUN] Would write {command_count} command skills to {agents_skills_dir}")
        print(f"[DRY RUN] Would remove {legacy_removed} legacy command skills")
    else:
        codex_dir.mkdir(parents=True, exist_ok=True)
        agents_skills_dir.mkdir(parents=True, exist_ok=True)

        if agents_md_path.exists():
            print(f"[OVERWRITE] {agents_md_path}")
        agents_md_path.write_text(agents_md, encoding="utf-8")
        print(f"Wrote {agents_md_path} ({len(agents_md)} chars)")

        if config_toml_path.exists():
            existing_toml = config_toml_path.read_text(encoding="utf-8")
            config_toml = merge_config_toml(config_toml, existing_toml)
            print(f"[MERGE] {config_toml_path} — user sections preserved")
        config_toml_path.write_text(config_toml, encoding="utf-8")
        print(f"Wrote {config_toml_path} ({len(config_toml)} chars)")

        print()
        print("Copying skills...")
        count = copy_skills(root, agents_skills_dir)
        print(f"Copied {count} skills to {agents_skills_dir}")
        print()
        print("Writing commands as short-named skills...")
        command_count, legacy_removed = copy_command_skills(root, agents_skills_dir)
        print(f"Wrote {command_count} command skills to {agents_skills_dir}")
        if legacy_removed:
            print(f"Removed {legacy_removed} legacy command skills")

    print()
    print("Done.")


if __name__ == "__main__":
    main()

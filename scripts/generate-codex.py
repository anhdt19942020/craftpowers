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
        print(f"\n[DRY RUN] Would write {len(agents_md)} chars to {agents_md_path}")
        print(f"[DRY RUN] Would write {len(config_toml)} chars to {config_toml_path}")
        print(f"[DRY RUN] Would copy {count} skills to {agents_skills_dir}")
    else:
        codex_dir.mkdir(parents=True, exist_ok=True)
        agents_skills_dir.mkdir(parents=True, exist_ok=True)

        if agents_md_path.exists():
            print(f"[OVERWRITE] {agents_md_path}")
        agents_md_path.write_text(agents_md, encoding="utf-8")
        print(f"Wrote {agents_md_path} ({len(agents_md)} chars)")

        if config_toml_path.exists():
            print(f"[OVERWRITE] {config_toml_path}")
        config_toml_path.write_text(config_toml, encoding="utf-8")
        print(f"Wrote {config_toml_path} ({len(config_toml)} chars)")

        print()
        print("Copying skills...")
        count = copy_skills(root, agents_skills_dir)
        print(f"Copied {count} skills to {agents_skills_dir}")

    print()
    print("Done.")


if __name__ == "__main__":
    main()

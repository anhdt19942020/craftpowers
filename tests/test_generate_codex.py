import importlib.util
from pathlib import Path


def load_generate_codex_module():
    script_path = Path(__file__).resolve().parents[1] / "scripts" / "generate-codex.py"
    spec = importlib.util.spec_from_file_location("generate_codex", script_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_command_skills_use_short_command_names(tmp_path):
    module = load_generate_codex_module()
    root = tmp_path / "mankit"
    commands = root / "commands"
    skills = root / "skills"
    target = tmp_path / "target"
    commands.mkdir(parents=True)
    skills.mkdir(parents=True)
    legacy = target / "source-command-man-fix"
    legacy.mkdir(parents=True)
    (legacy / "SKILL.md").write_text("legacy", encoding="utf-8")
    (commands / "man-fix.md").write_text(
        '---\ndescription: "Debug a bug."\n---\n\nFix command body.\n',
        encoding="utf-8",
    )

    command_count, legacy_removed = module.copy_command_skills(root, target)

    assert command_count == 1
    assert legacy_removed == 1
    assert not legacy.exists()
    generated = target / "man-fix" / "SKILL.md"
    assert generated.exists()
    text = generated.read_text(encoding="utf-8")
    assert 'name: "man-fix"' in text
    assert 'description: "Debug a bug."' in text
    assert "# man-fix" in text
    assert "Fix command body." in text


def test_command_skill_does_not_overwrite_native_skill(tmp_path):
    module = load_generate_codex_module()
    root = tmp_path / "mankit"
    commands = root / "commands"
    native_skill = root / "skills" / "man-assess"
    target = tmp_path / "target"
    commands.mkdir(parents=True)
    native_skill.mkdir(parents=True)
    target_skill = target / "man-assess"
    target_skill.mkdir(parents=True)
    (native_skill / "SKILL.md").write_text("native source", encoding="utf-8")
    (target_skill / "SKILL.md").write_text("native target", encoding="utf-8")
    (commands / "man-assess.md").write_text(
        '---\ndescription: "Assess."\n---\n\nInvoke the `man-assess` skill now.\n',
        encoding="utf-8",
    )

    command_count, legacy_removed = module.copy_command_skills(root, target)

    assert command_count == 0
    assert legacy_removed == 0
    assert (target_skill / "SKILL.md").read_text(encoding="utf-8") == "native target"

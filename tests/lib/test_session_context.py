from pathlib import Path
from hooks.lib.session_context import build_session_start_context

REPO_ROOT = Path(__file__).resolve().parents[2]

def test_includes_using_man_content():
    ctx = build_session_start_context(plugin_root=str(REPO_ROOT))
    assert "<EXTREMELY_IMPORTANT>" in ctx
    assert "You have man." in ctx
    # using-man SKILL.md content is embedded verbatim somewhere in the block
    using_man = (REPO_ROOT / "skills" / "using-man" / "SKILL.md").read_text(encoding="utf-8")
    snippet = using_man.strip().splitlines()[0]
    assert snippet in ctx

def test_no_legacy_warning_when_dir_absent(tmp_path):
    # legacy_skills_dir resolves under a HOME we control and does not exist
    ctx = build_session_start_context(plugin_root=str(REPO_ROOT), home=str(tmp_path))
    assert "WARNING" not in ctx

def test_legacy_warning_when_dir_present(tmp_path):
    legacy = tmp_path / ".config" / "superpowers" / "skills"
    legacy.mkdir(parents=True)
    ctx = build_session_start_context(plugin_root=str(REPO_ROOT), home=str(tmp_path))
    assert "WARNING" in ctx
    assert "~/.config/superpowers/skills" in ctx

def test_missing_skill_file_degrades_gracefully(tmp_path):
    # plugin_root with no skills/using-man/SKILL.md -> still returns a string, no crash
    ctx = build_session_start_context(plugin_root=str(tmp_path), home=str(tmp_path))
    assert isinstance(ctx, str)
    assert "<EXTREMELY_IMPORTANT>" in ctx

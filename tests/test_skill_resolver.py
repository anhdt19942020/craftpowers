"""Tests for sub-skill resolver."""
import os
import tempfile
from hooks.lib.skill_resolver import resolve_skill, list_sub_skills, clear_cache


def _make_skill(directory: str, *path_parts: str, content: str = "# Skill") -> str:
    """Create a SKILL.md at the given path."""
    skill_dir = os.path.join(directory, *path_parts)
    os.makedirs(skill_dir, exist_ok=True)
    skill_file = os.path.join(skill_dir, "SKILL.md")
    with open(skill_file, "w") as f:
        f.write(content)
    return skill_file


def test_exact_match():
    with tempfile.TemporaryDirectory() as d:
        skill_file = _make_skill(d, "skills", "council")
        clear_cache()
        result = resolve_skill("council", d)
        assert result == skill_file


def test_namespace_match():
    with tempfile.TemporaryDirectory() as d:
        skill_file = _make_skill(d, "skills", "council", "skeptic")
        clear_cache()
        result = resolve_skill("council:skeptic", d)
        assert result == skill_file


def test_man_prefix_stripped():
    with tempfile.TemporaryDirectory() as d:
        skill_file = _make_skill(d, "skills", "council")
        clear_cache()
        result = resolve_skill("man:council", d)
        assert result == skill_file


def test_man_prefix_with_namespace():
    with tempfile.TemporaryDirectory() as d:
        skill_file = _make_skill(d, "skills", "council", "skeptic")
        clear_cache()
        result = resolve_skill("man:council:skeptic", d)
        assert result == skill_file


def test_not_found():
    with tempfile.TemporaryDirectory() as d:
        os.makedirs(os.path.join(d, "skills"))
        clear_cache()
        result = resolve_skill("nonexistent", d)
        assert result is None


def test_no_skills_dir():
    with tempfile.TemporaryDirectory() as d:
        clear_cache()
        result = resolve_skill("council", d)
        assert result is None


def test_cache_hit():
    with tempfile.TemporaryDirectory() as d:
        skill_file = _make_skill(d, "skills", "council")
        clear_cache()
        r1 = resolve_skill("council", d)
        r2 = resolve_skill("council", d)
        assert r1 == r2 == skill_file


def test_list_sub_skills():
    with tempfile.TemporaryDirectory() as d:
        _make_skill(d, "skills", "council", content="# Parent")
        skill_file = _make_skill(d, "skills", "council", "skeptic")
        result = list_sub_skills("council", d)
        assert len(result) == 1
        assert "skeptic" in result[0]["name"]
        assert result[0]["parent"] == "council"


def test_list_sub_skills_empty():
    with tempfile.TemporaryDirectory() as d:
        _make_skill(d, "skills", "council")
        result = list_sub_skills("council", d)
        assert result == []


def test_list_sub_skills_no_parent():
    with tempfile.TemporaryDirectory() as d:
        result = list_sub_skills("nonexistent", d)
        assert result == []

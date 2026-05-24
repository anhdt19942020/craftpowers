import os
import tempfile
from hooks.lib.instinct_loader import (
    _parse_frontmatter, _scan_directory, discover_instincts, format_instincts,
    CONFIDENCE_THRESHOLD, MAX_INJECTED,
)


def test_parse_frontmatter():
    text = "---\nid: test\nconfidence: 0.85\n---\nSome body text"
    meta, body = _parse_frontmatter(text)
    assert meta["id"] == "test"
    assert meta["confidence"] == 0.85
    assert body == "Some body text"


def test_parse_frontmatter_no_frontmatter():
    meta, body = _parse_frontmatter("Just plain text")
    assert meta == {}
    assert body == "Just plain text"


def test_scan_empty_dir():
    with tempfile.TemporaryDirectory() as d:
        assert _scan_directory(d, "global") == []


def test_scan_nonexistent_dir():
    assert _scan_directory("/nonexistent/path/xyz", "global") == []


def test_scan_with_instinct():
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "test.md")
        with open(p, "w") as f:
            f.write("---\nid: test-instinct\nconfidence: 0.9\n---\nAlways test first")
        result = _scan_directory(d, "project")
        assert len(result) == 1
        assert result[0]["id"] == "test-instinct"
        assert result[0]["confidence"] == 0.9
        assert result[0]["scope"] == "project"


def test_scan_skips_no_id():
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "no-id.md")
        with open(p, "w") as f:
            f.write("---\nconfidence: 0.9\n---\nNo id here")
        result = _scan_directory(d, "global")
        assert len(result) == 0


def test_discover_dedup_project_wins():
    with tempfile.TemporaryDirectory() as home, tempfile.TemporaryDirectory() as proj:
        gp = os.path.join(home, ".claude", "instincts", "personal")
        pp = os.path.join(proj, ".claude", "instincts", "personal")
        os.makedirs(gp)
        os.makedirs(pp)
        with open(os.path.join(gp, "x.md"), "w") as f:
            f.write("---\nid: same\nconfidence: 0.8\n---\nGlobal version")
        with open(os.path.join(pp, "x.md"), "w") as f:
            f.write("---\nid: same\nconfidence: 0.75\n---\nProject version")
        result = discover_instincts(project_root=proj, home=home)
        assert len(result) == 1
        assert result[0]["scope"] == "project"


def test_discover_filters_low_confidence():
    with tempfile.TemporaryDirectory() as home, tempfile.TemporaryDirectory() as proj:
        gp = os.path.join(home, ".claude", "instincts", "personal")
        os.makedirs(gp)
        with open(os.path.join(gp, "low.md"), "w") as f:
            f.write("---\nid: low-conf\nconfidence: 0.3\n---\nLow confidence")
        result = discover_instincts(project_root=proj, home=home)
        assert len(result) == 0


def test_discover_cap_at_max():
    with tempfile.TemporaryDirectory() as home, tempfile.TemporaryDirectory() as proj:
        gp = os.path.join(home, ".claude", "instincts", "personal")
        os.makedirs(gp)
        for i in range(MAX_INJECTED + 3):
            with open(os.path.join(gp, f"inst-{i}.md"), "w") as f:
                f.write(f"---\nid: inst-{i}\nconfidence: 0.8\n---\nInstinct {i}")
        result = discover_instincts(project_root=proj, home=home)
        assert len(result) == MAX_INJECTED


def test_discover_sorts_by_confidence():
    with tempfile.TemporaryDirectory() as home, tempfile.TemporaryDirectory() as proj:
        gp = os.path.join(home, ".claude", "instincts", "personal")
        os.makedirs(gp)
        with open(os.path.join(gp, "a.md"), "w") as f:
            f.write("---\nid: low\nconfidence: 0.75\n---\nLower")
        with open(os.path.join(gp, "b.md"), "w") as f:
            f.write("---\nid: high\nconfidence: 0.95\n---\nHigher")
        result = discover_instincts(project_root=proj, home=home)
        assert result[0]["id"] == "high"
        assert result[1]["id"] == "low"


def test_format_instincts():
    instincts = [
        {"id": "test", "confidence": 0.85, "scope": "project", "body": "Always test first"},
    ]
    output = format_instincts(instincts)
    assert "[project 85%]" in output
    assert "test:" in output
    assert "Always test first" in output


def test_format_instincts_empty():
    assert format_instincts([]) == ""


def test_format_instincts_skips_headers():
    instincts = [
        {"id": "test", "confidence": 0.9, "scope": "global", "body": "# Header\n## Subheader\nActual content"},
    ]
    output = format_instincts(instincts)
    assert "Actual content" in output
    assert "# Header" not in output


def test_confidence_threshold_value():
    assert CONFIDENCE_THRESHOLD == 0.7


def test_max_injected_value():
    assert MAX_INJECTED == 6

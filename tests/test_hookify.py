"""Tests for hookify declarative rule loader."""
import os
import tempfile
from hooks.lib.hookify_loader import (
    _parse_hookify_frontmatter,
    discover_hookify_rules,
    evaluate_hookify_rules,
)


def test_parse_frontmatter():
    text = '---\nevent: bash\naction: block\npattern: "rm -rf"\n---\nBlock rm -rf'
    meta, body = _parse_hookify_frontmatter(text)
    assert meta["event"] == "bash"
    assert meta["action"] == "block"
    assert meta["pattern"] == "rm -rf"
    assert body == "Block rm -rf"


def test_parse_frontmatter_no_quotes():
    text = "---\nevent: write\naction: warn\npattern: TODO\n---\nTODO found"
    meta, body = _parse_hookify_frontmatter(text)
    assert meta["pattern"] == "TODO"


def test_parse_frontmatter_no_match():
    meta, body = _parse_hookify_frontmatter("no frontmatter here")
    assert meta == {}


def test_discover_rules():
    with tempfile.TemporaryDirectory() as d:
        claude_dir = os.path.join(d, ".claude")
        os.makedirs(claude_dir)
        rule_path = os.path.join(claude_dir, "hookify.no-force-push.md")
        with open(rule_path, "w") as f:
            f.write('---\nevent: bash\naction: block\npattern: "git push.*--force"\n---\nNo force push')
        rules = discover_hookify_rules(d)
        assert len(rules) == 1
        assert rules[0]["name"] == "no-force-push"
        assert rules[0]["event"] == "bash"
        assert rules[0]["action"] == "block"


def test_discover_rules_skips_missing_fields():
    with tempfile.TemporaryDirectory() as d:
        claude_dir = os.path.join(d, ".claude")
        os.makedirs(claude_dir)
        bad_path = os.path.join(claude_dir, "hookify.bad.md")
        with open(bad_path, "w") as f:
            f.write("---\naction: block\n---\nMissing event field")
        rules = discover_hookify_rules(d)
        assert len(rules) == 0


def test_discover_no_claude_dir():
    with tempfile.TemporaryDirectory() as d:
        rules = discover_hookify_rules(d)
        assert rules == []


def test_evaluate_block():
    rules = [{"name": "test", "event": "bash", "action": "block", "pattern": "rm -rf /", "description": "Blocked"}]
    result = evaluate_hookify_rules(rules, "bash", "rm -rf /home")
    assert result["decision"] == "block"
    assert "hookify/test" in result["reason"]


def test_evaluate_no_match():
    rules = [{"name": "test", "event": "bash", "action": "block", "pattern": "rm -rf /", "description": "Blocked"}]
    result = evaluate_hookify_rules(rules, "bash", "ls -la")
    assert result["decision"] == "ok"


def test_evaluate_wrong_event():
    rules = [{"name": "test", "event": "bash", "action": "block", "pattern": "rm -rf", "description": "Blocked"}]
    result = evaluate_hookify_rules(rules, "write", "rm -rf")
    assert result["decision"] == "ok"


def test_warn_action():
    rules = [{"name": "todo", "event": "write", "action": "warn", "pattern": "TODO", "description": "TODO found"}]
    result = evaluate_hookify_rules(rules, "write", "# TODO fix this")
    assert result["decision"] == "ok"
    assert "TODO found" in result.get("systemMessage", "")


def test_invalid_regex_skipped():
    rules = [{"name": "bad", "event": "bash", "action": "block", "pattern": "[invalid", "description": "Bad regex"}]
    result = evaluate_hookify_rules(rules, "bash", "some command")
    assert result["decision"] == "ok"

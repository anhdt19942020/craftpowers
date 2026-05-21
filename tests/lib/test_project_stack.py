"""Tests for hooks/lib/project_stack.py."""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "hooks"))

from lib.project_stack import detect_stack, get_linters, format_stack_context


class TestDetectStack:
    def test_php_project(self, tmp_path):
        (tmp_path / "composer.json").write_text("{}", encoding="utf-8")
        result = detect_stack(str(tmp_path))
        assert "php" in result

    def test_laravel_project(self, tmp_path):
        (tmp_path / "composer.json").write_text("{}", encoding="utf-8")
        (tmp_path / "artisan").write_text("", encoding="utf-8")
        result = detect_stack(str(tmp_path))
        assert "php" in result
        assert "laravel" in result

    def test_node_project(self, tmp_path):
        (tmp_path / "package.json").write_text("{}", encoding="utf-8")
        result = detect_stack(str(tmp_path))
        assert "node" in result

    def test_typescript_project(self, tmp_path):
        (tmp_path / "tsconfig.json").write_text("{}", encoding="utf-8")
        result = detect_stack(str(tmp_path))
        assert "typescript" in result

    def test_python_project(self, tmp_path):
        (tmp_path / "pyproject.toml").write_text("", encoding="utf-8")
        result = detect_stack(str(tmp_path))
        assert "python" in result

    def test_go_project(self, tmp_path):
        (tmp_path / "go.mod").write_text("", encoding="utf-8")
        result = detect_stack(str(tmp_path))
        assert "go" in result

    def test_rust_project(self, tmp_path):
        (tmp_path / "Cargo.toml").write_text("", encoding="utf-8")
        result = detect_stack(str(tmp_path))
        assert "rust" in result

    def test_empty_dir(self, tmp_path):
        result = detect_stack(str(tmp_path))
        assert result == []

    def test_multi_stack(self, tmp_path):
        (tmp_path / "composer.json").write_text("{}", encoding="utf-8")
        (tmp_path / "package.json").write_text("{}", encoding="utf-8")
        result = detect_stack(str(tmp_path))
        assert "php" in result
        assert "node" in result

    def test_nextjs_framework(self, tmp_path):
        (tmp_path / "package.json").write_text("{}", encoding="utf-8")
        (tmp_path / "next.config.js").write_text("", encoding="utf-8")
        result = detect_stack(str(tmp_path))
        assert "node" in result
        assert "nextjs" in result

    def test_sorted_output(self, tmp_path):
        (tmp_path / "package.json").write_text("{}", encoding="utf-8")
        (tmp_path / "composer.json").write_text("{}", encoding="utf-8")
        result = detect_stack(str(tmp_path))
        assert result == sorted(result)

    def test_no_duplicates(self, tmp_path):
        (tmp_path / "composer.json").write_text("{}", encoding="utf-8")
        result = detect_stack(str(tmp_path))
        assert len(result) == len(set(result))


class TestGetLinters:
    def test_php_linters(self):
        result = get_linters(["php"])
        assert "static" in result
        assert "phpstan" in result["static"]

    def test_typescript_linters(self):
        result = get_linters(["typescript"])
        assert "static" in result
        assert "tsc" in result["static"]

    def test_python_linters(self):
        result = get_linters(["python"])
        assert "static" in result
        assert "lint" in result

    def test_unknown_stack(self):
        result = get_linters(["unknown"])
        assert result == {}

    def test_multi_stack_merges(self):
        result = get_linters(["php", "typescript"])
        assert "static" in result


class TestFormatStackContext:
    def test_single_stack(self):
        result = format_stack_context(["php"])
        assert "[project-stack: php]" in result
        assert "phpstan" in result

    def test_multi_stack(self):
        result = format_stack_context(["node", "php"])
        assert "[project-stack: node,php]" in result

    def test_empty_stack(self):
        result = format_stack_context([])
        assert "[project-stack: unknown]" in result

    def test_contains_skip_instruction(self):
        result = format_stack_context(["php"])
        assert "Skip" in result

    def test_no_linters_for_unknown(self):
        result = format_stack_context(["ruby"])
        assert "[project-linters:" not in result

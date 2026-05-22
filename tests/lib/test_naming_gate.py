"""Tests for hooks.lib.naming_gate."""
import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from hooks.lib.naming_gate import evaluate


class TestPassThrough:
    def test_non_write_tool_passes(self):
        result = evaluate("Read", "/some/file.py")
        assert result["decision"] == "approve"

    def test_edit_tool_passes(self):
        result = evaluate("Edit", "/some/utils.py")
        assert result["decision"] == "approve"

    def test_empty_path_passes(self):
        result = evaluate("Write", "")
        assert result["decision"] == "approve"

    def test_json_files_pass(self):
        result = evaluate("Write", "/project/package.json")
        assert result["decision"] == "approve"

    def test_yaml_files_pass(self):
        result = evaluate("Write", "/project/config.yaml")
        assert result["decision"] == "approve"

    def test_dotfiles_pass(self):
        result = evaluate("Write", "/project/.gitignore")
        assert result["decision"] == "approve"

    def test_node_modules_pass(self):
        result = evaluate("Write", "/project/node_modules/pkg/utils.js")
        assert result["decision"] == "approve"


class TestAlwaysAllow:
    def test_readme_passes(self):
        result = evaluate("Write", "/project/README.md")
        assert result["decision"] == "approve"

    def test_claude_md_passes(self):
        result = evaluate("Write", "/project/CLAUDE.md")
        assert result["decision"] == "approve"

    def test_init_py_passes(self):
        result = evaluate("Write", "/project/hooks/__init__.py")
        assert result["decision"] == "approve"

    def test_conftest_passes(self):
        result = evaluate("Write", "/project/tests/conftest.py")
        assert result["decision"] == "approve"

    def test_dockerfile_passes(self):
        result = evaluate("Write", "/project/Dockerfile")
        assert result["decision"] == "approve"


class TestGenericNames:
    def test_utils_py_blocked(self):
        result = evaluate("Write", "/project/utils.py")
        assert result["decision"] == "block"
        assert "Generic name" in result["reason"]

    def test_helpers_js_blocked(self):
        result = evaluate("Write", "/project/helpers.js")
        assert result["decision"] == "block"

    def test_temp_ts_blocked(self):
        result = evaluate("Write", "/project/temp.ts")
        assert result["decision"] == "block"

    def test_common_py_blocked(self):
        result = evaluate("Write", "/project/common.py")
        assert result["decision"] == "block"

    def test_utils_md_passes(self):
        result = evaluate("Write", "/project/utils.md")
        assert result["decision"] == "approve"

    def test_descriptive_name_passes(self):
        result = evaluate("Write", "/project/workflow-utils.py")
        assert result["decision"] == "approve"


class TestBadPrefixes:
    def test_enhanced_blocked(self):
        result = evaluate("Write", "/project/enhanced-auth.py")
        assert result["decision"] == "block"
        assert "Bad prefix" in result["reason"]
        assert "'auth.py'" in result["reason"]

    def test_new_blocked(self):
        result = evaluate("Write", "/project/new-parser.js")
        assert result["decision"] == "block"

    def test_v2_blocked(self):
        result = evaluate("Write", "/project/v2-config.ts")
        assert result["decision"] == "block"

    def test_copy_blocked(self):
        result = evaluate("Write", "/project/copy-handler.py")
        assert result["decision"] == "block"

    def test_backup_blocked(self):
        result = evaluate("Write", "/project/backup-server.js")
        assert result["decision"] == "block"


class TestKebabCase:
    def test_camelcase_warns(self):
        result = evaluate("Write", "/project/myComponent.tsx")
        assert result["decision"] == "warn"

    def test_kebab_case_passes(self):
        result = evaluate("Write", "/project/my-component.tsx")
        assert result["decision"] == "approve"

    def test_snake_case_passes(self):
        result = evaluate("Write", "/project/my_module.py")
        assert result["decision"] == "approve"

    def test_test_prefix_passes(self):
        result = evaluate("Write", "/project/test_auth.py")
        assert result["decision"] == "approve"

    def test_underscore_prefix_passes(self):
        result = evaluate("Write", "/project/_internal.py")
        assert result["decision"] == "approve"

    def test_pascal_case_warns(self):
        result = evaluate("Write", "/project/AuthService.ts")
        assert result["decision"] == "warn"


class TestMarkdownFiles:
    def test_uppercase_md_passes(self):
        result = evaluate("Write", "/project/CHANGELOG.md")
        assert result["decision"] == "approve"

    def test_kebab_md_passes(self):
        result = evaluate("Write", "/project/my-feature.md")
        assert result["decision"] == "approve"

    def test_phase_md_passes(self):
        result = evaluate("Write", "/project/plans/phase-01-setup.md")
        assert result["decision"] == "approve"

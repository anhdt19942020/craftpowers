"""Tests for hooks.lib.privacy_gate."""
from __future__ import annotations
import sys

from hooks.lib.privacy_gate import evaluate


# --- Non-file tools ---

def test_bash_tool_allowed():
    result = evaluate("Bash", "some command string")
    assert result["decision"] == "allow"


def test_task_tool_allowed():
    result = evaluate("Task", "/some/path/file.py")
    assert result["decision"] == "allow"


# --- .env files ---

def test_read_dotenv_blocked():
    result = evaluate("Read", ".env")
    assert result["decision"] == "block"


def test_edit_dotenv_blocked():
    result = evaluate("Edit", "/project/.env")
    assert result["decision"] == "block"


def test_write_dotenv_blocked():
    result = evaluate("Write", "/home/user/.env")
    assert result["decision"] == "block"


def test_read_dotenv_example_allowed():
    result = evaluate("Read", ".env.example")
    assert result["decision"] == "allow"


def test_read_dotenv_template_allowed():
    result = evaluate("Read", ".env.template")
    assert result["decision"] == "allow"


def test_read_dotenv_sample_allowed():
    result = evaluate("Read", "config/.env.sample")
    assert result["decision"] == "allow"


# --- Regular source files ---

def test_read_python_allowed():
    result = evaluate("Read", "src/app.py")
    assert result["decision"] == "allow"


def test_edit_ts_allowed():
    result = evaluate("Edit", "src/components/Button.tsx")
    assert result["decision"] == "allow"


# --- Credentials / secrets ---

def test_edit_credentials_json_blocked():
    result = evaluate("Edit", "credentials.json")
    assert result["decision"] == "block"


def test_read_secrets_yaml_blocked():
    result = evaluate("Read", "config/secrets.yaml")
    assert result["decision"] == "block"


# --- PEM / key files ---

def test_write_pem_blocked():
    result = evaluate("Write", "server.pem")
    assert result["decision"] == "block"


def test_read_key_blocked():
    result = evaluate("Read", "private.key")
    assert result["decision"] == "block"


def test_read_p12_blocked():
    result = evaluate("Read", "cert.p12")
    assert result["decision"] == "block"


def test_read_pfx_blocked():
    result = evaluate("Read", "cert.pfx")
    assert result["decision"] == "block"


# --- SSH keys ---

def test_write_id_rsa_blocked():
    result = evaluate("Write", "/home/user/.ssh/id_rsa")
    assert result["decision"] == "block"


def test_read_id_ed25519_blocked():
    result = evaluate("Read", "/home/user/.ssh/id_ed25519")
    assert result["decision"] == "block"


# --- Git config ---

def test_read_git_config_blocked():
    result = evaluate("Read", ".git/config")
    assert result["decision"] == "block"


# --- Token files ---

def test_read_token_file_blocked():
    result = evaluate("Read", "github_token")
    assert result["decision"] == "block"


# --- Cloud credential dirs ---

def test_read_aws_creds_blocked():
    result = evaluate("Read", "/home/user/.aws/credentials")
    assert result["decision"] == "block"


def test_read_gcp_key_blocked():
    result = evaluate("Read", "/home/user/.gcp/service-account.json")
    assert result["decision"] == "block"


# --- Test/fixture directories (whitelist) ---

def test_read_test_fixture_dotenv_allowed():
    result = evaluate("Read", "tests/fixtures/.env.test")
    assert result["decision"] == "allow"


def test_read_mock_dir_allowed():
    result = evaluate("Read", "src/__mocks__/credentials.json")
    assert result["decision"] == "allow"


def test_read_fixture_secret_allowed():
    result = evaluate("Read", "tests/fixtures/secrets.yaml")
    assert result["decision"] == "allow"


# --- Case insensitivity ---

def test_read_dotenv_uppercase_blocked():
    result = evaluate("Read", ".ENV")
    assert result["decision"] == "block"


def test_read_credentials_uppercase_blocked():
    result = evaluate("Read", "CREDENTIALS.json")
    assert result["decision"] == "block"


# --- MultiEdit ---

def test_multiedit_dotenv_blocked():
    result = evaluate("MultiEdit", "/project/.env")
    assert result["decision"] == "block"

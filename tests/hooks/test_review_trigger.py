import sys, os, json, subprocess
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'hooks'))

from lib.review_trigger import get_diff, write_handoff, should_trigger_security
from pathlib import Path

def test_get_diff_returns_string(tmp_path):
    subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=tmp_path, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, capture_output=True)
    (tmp_path / "a.txt").write_text("hello")
    subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=tmp_path, capture_output=True)
    result = get_diff(cwd=str(tmp_path))
    assert isinstance(result, str)

def test_get_diff_empty_when_no_commits(tmp_path):
    subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
    result = get_diff(cwd=str(tmp_path))
    assert result == ""

def test_write_handoff_creates_file(tmp_path):
    write_handoff(diff="+ auth code", metadata={"agent": "implementer"}, out_dir=str(tmp_path))
    handoff = tmp_path / "review-handoff.md"
    assert handoff.exists()
    content = handoff.read_text()
    assert "+ auth code" in content
    assert "implementer" in content

def test_should_trigger_security_true_for_sensitive_diff():
    diff = "+    token = jwt.encode(payload, secret)"
    assert should_trigger_security(diff) is True

def test_should_trigger_security_false_for_clean_diff():
    diff = "+    total = sum(items)"
    assert should_trigger_security(diff) is False

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'hooks'))

from lib.worktree_provision import provision


def test_returns_none_when_no_worktree_path():
    result = provision({})
    assert result is None


def test_returns_none_when_worktree_path_does_not_exist():
    result = provision({"worktree_path": "/nonexistent/path/xyz"})
    assert result is None


def test_returns_message_when_worktree_exists(tmp_path):
    pkg = tmp_path / "package.json"
    pkg.write_text('{"name": "test"}')
    result = provision({"worktree_path": str(tmp_path)})
    assert result is not None
    assert str(tmp_path) in result
    assert "package.json" in result


def test_copies_env_from_base_dir(tmp_path):
    base = tmp_path / "base"
    base.mkdir()
    (base / ".env").write_text("SECRET=123")
    wt = tmp_path / "worktree"
    wt.mkdir()
    result = provision({"worktree_path": str(wt)}, base_dir=str(base))
    assert result is not None
    assert ".env copied" in result
    assert (wt / ".env").exists()


def test_skips_env_copy_if_already_present(tmp_path):
    base = tmp_path / "base"
    base.mkdir()
    (base / ".env").write_text("SECRET=123")
    wt = tmp_path / "worktree"
    wt.mkdir()
    (wt / ".env").write_text("EXISTING=1")
    provision({"worktree_path": str(wt)}, base_dir=str(base))
    # original content must be preserved
    assert (wt / ".env").read_text() == "EXISTING=1"


def test_returns_none_when_nothing_to_report(tmp_path):
    # empty worktree, no base_dir, no package.json
    result = provision({"worktree_path": str(tmp_path)})
    assert result is None

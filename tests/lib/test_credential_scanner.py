from hooks.lib.credential_scanner import scan_content, build_warning

def test_clean_content():
    assert scan_content("print('hello world')\n", "app.py") == []

def test_aws_access_key_id():
    findings = scan_content("KEY = 'AKIAIOSFODNN7EXAMPLE'\n", "config.py")
    assert any("AWS Access Key ID" in f for f in findings)
    assert findings[0].startswith("  Line 1 ")

def test_github_pat():
    # ghp_ token on its own line (no competing earlier pattern)
    line = "ghp_" + "a" * 36 + "\n"
    findings = scan_content(line, "deploy.py")
    assert any("GitHub Personal Access Token" in f for f in findings)

def test_false_positive_marker_skips_line():
    findings = scan_content("password = process.env.DB_PASSWORD\n", "db.js")
    assert findings == []

def test_env_var_interpolation_skipped():
    findings = scan_content('api_key = "${MY_API_KEY}"\n', "x.sh")
    assert findings == []

def test_skip_binary_extension():
    assert scan_content("AKIAIOSFODNN7EXAMPLE", "logo.png") == []

def test_findings_capped_at_five():
    # Use AWS Access Key ID pattern which reliably triggers per line
    body = "\n".join(f"AKIA{'ABCDEFGHIJKLMNOP'}" for _ in range(10)) + "\n"
    findings = scan_content(body, "secrets.py")
    assert len(findings) == 5

def test_build_warning_wraps_findings():
    findings = ["  Line 3 [Hardcoded password]: password = 'hunter2hunter2'"]
    msg = build_warning("config.py", findings)
    assert "config.py" in msg
    assert msg.startswith("<important-reminder>")
    assert "Line 3" in msg

def test_build_warning_empty_returns_empty():
    assert build_warning("config.py", []) == ""

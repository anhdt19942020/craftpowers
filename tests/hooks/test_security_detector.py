import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'hooks'))

from lib.security_detector import evaluate

def test_detects_auth_keyword():
    diff = "+    if user.authenticate(password):\n+        return token"
    found, keywords = evaluate(diff)
    assert found is True
    assert "auth" in keywords

def test_detects_sql_keyword():
    diff = "+    query = 'SELECT * FROM users WHERE id = ' + user_id"
    found, keywords = evaluate(diff)
    assert found is True
    assert "sql" in keywords or "query" in keywords

def test_ignores_removed_lines():
    diff = "-    old_auth_code = True\n+    new_code = True"
    found, keywords = evaluate(diff)
    assert found is False

def test_clean_diff_returns_false():
    diff = "+    result = calculate_total(items)\n+    return result"
    found, keywords = evaluate(diff)
    assert found is False
    assert keywords == []

def test_detects_jwt():
    diff = "+    token = jwt.encode(payload, secret)"
    found, keywords = evaluate(diff)
    assert found is True

def test_detects_subprocess():
    diff = "+    os.system(user_input)"
    found, keywords = evaluate(diff)
    assert found is True

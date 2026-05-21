import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'hooks'))

from lib.stop_failure import handle_failure


def test_includes_error_type():
    result = handle_failure({"error": "rate_limit", "message": "Too many requests"})
    assert "rate_limit" in result


def test_includes_message():
    result = handle_failure({"error": "auth_failure", "message": "Invalid API key"})
    assert "Invalid API key" in result


def test_includes_retry_hint_for_rate_limit():
    result = handle_failure({"error": "rate_limit", "message": ""})
    assert "rate" in result.lower() or "retry" in result.lower()


def test_includes_api_key_hint_for_auth():
    result = handle_failure({"error": "auth_failure", "message": ""})
    assert "API key" in result


def test_default_error_type_when_missing():
    result = handle_failure({})
    assert "unknown" in result


def test_returns_non_empty_string():
    result = handle_failure({"error": "billing", "message": "Quota exceeded"})
    assert isinstance(result, str)
    assert len(result) > 0

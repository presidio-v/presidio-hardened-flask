"""Tests for secret redaction in request data."""

from __future__ import annotations

from presidio_flask._redaction import is_sensitive_key, redact_dict


def test_redact_dict_masks_secrets():
    data = {"username": "alice", "password": "hunter2", "api_key": "sk-123"}
    result = redact_dict(data)
    assert result["username"] == "alice"
    assert result["password"] == "***REDACTED***"
    assert result["api_key"] == "***REDACTED***"


def test_redact_dict_preserves_non_sensitive():
    data = {"name": "Bob", "age": "30", "city": "NYC"}
    result = redact_dict(data)
    assert result == data


def test_is_sensitive_key_matches():
    assert is_sensitive_key("password")
    assert is_sensitive_key("API_KEY")
    assert is_sensitive_key("auth_token")
    assert is_sensitive_key("secret_value")
    assert not is_sensitive_key("username")
    assert not is_sensitive_key("email")


def test_redaction_in_request(client):
    resp = client.post(
        "/json",
        json={"user": "alice", "password": "secret123"},
        content_type="application/json",
    )
    assert resp.status_code == 200


def test_nested_dict_redaction():
    data = {"config": {"db_password": "secret", "host": "localhost"}}
    result = redact_dict(data)
    assert result["config"]["db_password"] == "***REDACTED***"
    assert result["config"]["host"] == "localhost"

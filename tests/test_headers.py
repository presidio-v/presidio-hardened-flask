"""Tests for automatic security headers."""

from __future__ import annotations


def test_security_headers_present(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.headers["X-Content-Type-Options"] == "nosniff"
    assert resp.headers["X-Frame-Options"] == "DENY"
    assert resp.headers["X-XSS-Protection"] == "0"
    assert "strict-origin" in resp.headers["Referrer-Policy"]
    assert "geolocation=()" in resp.headers["Permissions-Policy"]
    assert "default-src 'self'" in resp.headers["Content-Security-Policy"]
    assert "max-age=" in resp.headers["Strict-Transport-Security"]
    assert resp.headers["Cross-Origin-Opener-Policy"] == "same-origin"
    assert resp.headers["Cross-Origin-Resource-Policy"] == "same-origin"


def test_custom_header_override(app):
    app.config["PRESIDIO_SECURITY_HEADERS"] = {"X-Frame-Options": "SAMEORIGIN"}
    # Force re-init
    app._presidio_initialized = False
    c = app.test_client()
    resp = c.get("/")
    assert resp.headers["X-Frame-Options"] == "SAMEORIGIN"

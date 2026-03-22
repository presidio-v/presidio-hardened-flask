"""Tests for session cookie hardening."""

from __future__ import annotations


def test_session_cookie_defaults(app):
    assert app.config["SESSION_COOKIE_SECURE"] is True
    assert app.config["SESSION_COOKIE_HTTPONLY"] is True
    assert app.config["SESSION_COOKIE_SAMESITE"] == "Lax"
    assert app.config["SESSION_COOKIE_NAME"] == "__Host-session"


def test_session_config_not_overridden_if_set():
    from presidio_flask import Flask

    app = Flask(__name__)
    app.config["SESSION_COOKIE_SAMESITE"] = "Strict"
    app.config["PRESIDIO_CVE_CHECK"] = False
    app.test_client().get("/")  # trigger init
    assert app.config["SESSION_COOKIE_SAMESITE"] == "Strict"

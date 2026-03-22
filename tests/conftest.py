"""Shared fixtures for Presidio-Hardened Flask tests."""

from __future__ import annotations

import pytest

from presidio_flask import Flask


@pytest.fixture()
def app():
    """Create a minimal Presidio-hardened app for testing."""
    app = Flask(__name__)
    app.config.update(
        TESTING=True,
        SECRET_KEY="test-secret-key",
        PRESIDIO_CVE_CHECK=False,
        PRESIDIO_RATE_LIMIT=5,
        PRESIDIO_RATE_WINDOW=60,
    )

    @app.route("/")
    def index():
        return "OK"

    @app.route("/json", methods=["POST"])
    def json_endpoint():
        from presidio_flask import jsonify, request

        return jsonify(request.get_json(silent=True) or {})

    @app.route("/form", methods=["POST"])
    def form_endpoint():
        from presidio_flask import request

        return f"name={request.form.get('name', '')}"

    return app


@pytest.fixture()
def client(app):
    """Test client from the hardened app."""
    return app.test_client()


@pytest.fixture(autouse=True)
def _reset_rate_limiter():
    """Reset the rate limiter between tests."""
    from presidio_flask._rate_limit import get_store

    get_store().reset()

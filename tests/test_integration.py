"""Integration tests verifying the full Presidio-hardened Flask stack."""

from __future__ import annotations


def test_full_stack_get(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.data == b"OK"
    assert "X-Content-Type-Options" in resp.headers
    assert "X-RateLimit-Limit" in resp.headers


def test_full_stack_post_json(client):
    resp = client.post(
        "/json",
        headers={"Sec-Fetch-Site": "same-origin"},
        json={"message": "hello"},
    )
    assert resp.status_code == 200
    assert resp.get_json()["message"] == "hello"


def test_version_importable():
    from presidio_flask import __version__

    assert __version__ == "0.2.0"


def test_flask_subclass():
    from presidio_flask import Flask

    app = Flask(__name__)
    assert hasattr(app, "_presidio_initialized")


def test_blueprint_importable():
    from presidio_flask import Blueprint

    bp = Blueprint("test", __name__)
    assert bp.name == "test"


def test_cve_check_runs(app):
    """Ensure CVE check can run without error."""
    from presidio_flask._cve_check import run_cve_check

    with app.app_context():
        run_cve_check(app)

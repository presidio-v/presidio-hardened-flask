"""Tests for CSRF protection."""

from __future__ import annotations


def test_safe_methods_pass(client):
    resp = client.get("/")
    assert resp.status_code == 200


def test_post_with_same_origin_header(client):
    resp = client.post("/json", headers={"Sec-Fetch-Site": "same-origin"}, json={})
    assert resp.status_code == 200


def test_post_blocked_cross_site(client):
    resp = client.post(
        "/json",
        headers={"Sec-Fetch-Site": "cross-site"},
        json={},
    )
    assert resp.status_code == 403


def test_post_with_valid_csrf_token(app):
    c = app.test_client()
    with app.test_request_context():
        from presidio_flask import generate_csrf_token

        token = generate_csrf_token()

    resp = c.post(
        "/json",
        headers={"X-CSRF-Token": token},
        json={"hello": "world"},
    )
    assert resp.status_code == 200


def test_post_without_sec_fetch_or_token_allowed(client):
    """Without Sec-Fetch-Site header and no token, request passes through
    (lenient mode – no cross-origin signal detected)."""
    resp = client.post("/json", json={"data": "value"})
    assert resp.status_code == 200


def test_csrf_disabled(app):
    app.config["PRESIDIO_CSRF_ENABLED"] = False
    app._presidio_initialized = False
    c = app.test_client()
    resp = c.post(
        "/json",
        headers={"Sec-Fetch-Site": "cross-site"},
        json={},
    )
    assert resp.status_code == 200

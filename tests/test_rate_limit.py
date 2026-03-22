"""Tests for rate limiting with exponential backoff."""

from __future__ import annotations


def test_rate_limit_allows_within_limit(client):
    for _ in range(5):
        resp = client.get("/")
        assert resp.status_code == 200
    assert resp.headers.get("X-RateLimit-Limit") == "5"


def test_rate_limit_blocks_over_limit(client):
    for _ in range(5):
        client.get("/")
    resp = client.get("/")
    assert resp.status_code == 429


def test_rate_limit_headers_present(client):
    resp = client.get("/")
    assert "X-RateLimit-Limit" in resp.headers
    assert "X-RateLimit-Remaining" in resp.headers


def test_rate_limit_disabled(app):
    app.config["PRESIDIO_RATE_LIMIT_ENABLED"] = False
    app._presidio_initialized = False
    c = app.test_client()
    for _ in range(20):
        resp = c.get("/")
        assert resp.status_code == 200

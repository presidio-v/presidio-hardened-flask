"""Tests for input sanitization."""

from __future__ import annotations


def test_normal_request_passes(client):
    resp = client.get("/?name=Alice&age=30")
    assert resp.status_code == 200


def test_sql_injection_blocked(client):
    resp = client.get("/?q=1'+OR+'1'='1")
    assert resp.status_code == 400


def test_xss_blocked_in_query(client):
    resp = client.get("/?q=<script>alert(1)</script>")
    assert resp.status_code == 400


def test_path_traversal_blocked(client):
    resp = client.get("/?file=../../../etc/passwd")
    assert resp.status_code == 400


def test_xss_blocked_in_json(client):
    resp = client.post(
        "/json",
        headers={"Sec-Fetch-Site": "same-origin"},
        json={"name": "<script>alert('xss')</script>"},
    )
    assert resp.status_code == 400


def test_clean_json_passes(client):
    resp = client.post(
        "/json",
        headers={"Sec-Fetch-Site": "same-origin"},
        json={"name": "Alice", "age": 30},
    )
    assert resp.status_code == 200

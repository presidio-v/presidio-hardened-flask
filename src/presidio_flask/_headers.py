"""Automatic security headers middleware."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flask import Flask, Response

DEFAULT_HEADERS: dict[str, str] = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "0",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "geolocation=(), camera=(), microphone=()",
    "Content-Security-Policy": (
        "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'"
    ),
    "Strict-Transport-Security": "max-age=63072000; includeSubDomains; preload",
    "Cross-Origin-Opener-Policy": "same-origin",
    "Cross-Origin-Resource-Policy": "same-origin",
}


def register_security_headers(app: Flask) -> None:
    overrides = app.config.get("PRESIDIO_SECURITY_HEADERS", {})
    merged = {**DEFAULT_HEADERS, **overrides}

    @app.after_request
    def _set_security_headers(response: Response) -> Response:
        for header, value in merged.items():
            if value is not None:
                response.headers.setdefault(header, value)
        return response

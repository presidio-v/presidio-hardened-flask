"""Enhanced session cookie defaults."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flask import Flask

_PRESIDIO_SESSION_DEFAULTS: dict[str, object] = {
    "SESSION_COOKIE_SECURE": True,
    "SESSION_COOKIE_HTTPONLY": True,
    "SESSION_COOKIE_SAMESITE": "Lax",
    "SESSION_COOKIE_NAME": "__Host-session",
    "PERMANENT_SESSION_LIFETIME": 1800,
}

_FLASK_ORIGINAL_DEFAULTS: dict[str, object] = {
    "SESSION_COOKIE_SECURE": False,
    "SESSION_COOKIE_HTTPONLY": True,
    "SESSION_COOKIE_SAMESITE": None,
    "SESSION_COOKIE_NAME": "session",
    "PERMANENT_SESSION_LIFETIME": 2678400,  # 31 days
}


def register_session_hardening(app: Flask) -> None:
    for key, presidio_val in _PRESIDIO_SESSION_DEFAULTS.items():
        current = app.config.get(key)
        flask_default = _FLASK_ORIGINAL_DEFAULTS.get(key)
        if current == flask_default:
            app.config[key] = presidio_val

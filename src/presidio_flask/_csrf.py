"""CSRF protection using Sec-Fetch-Site with token-based fallback."""

from __future__ import annotations

import hashlib
import hmac
import os
import time
from typing import TYPE_CHECKING

from flask import abort, g, request, session

if TYPE_CHECKING:
    from flask import Flask

_SAFE_METHODS = frozenset({"GET", "HEAD", "OPTIONS", "TRACE"})
_TOKEN_TTL = 3600


def _generate_token(secret: str) -> str:
    nonce = os.urandom(16).hex()
    ts = str(int(time.time()))
    payload = f"{nonce}:{ts}"
    sig = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return f"{payload}:{sig}"


def _validate_token(secret: str, token: str) -> bool:
    parts = token.split(":")
    if len(parts) != 3:
        return False
    nonce, ts_str, sig = parts
    try:
        ts = int(ts_str)
    except ValueError:
        return False
    if time.time() - ts > _TOKEN_TTL:
        return False
    expected = hmac.new(secret.encode(), f"{nonce}:{ts_str}".encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(sig, expected)


def generate_csrf_token() -> str:
    from flask import current_app

    secret = current_app.config.get("SECRET_KEY")
    if not secret or secret == "presidio-dev-key":
        # v0.2: no dangerous fallback; require explicit strong SECRET_KEY
        raise RuntimeError(
            "PRESIDIO CSRF requires a strong SECRET_KEY in app.config "
            "(never use the old 'presidio-dev-key' default). "
            "Set app.config['SECRET_KEY'] = 'your-strong-random-value'."
        )
    token = _generate_token(secret)
    session["_presidio_csrf"] = token
    return token


def register_csrf_protection(app: Flask) -> None:
    if not app.config.get("PRESIDIO_CSRF_ENABLED", True):
        return

    @app.before_request
    def _csrf_check() -> None:
        if request.method in _SAFE_METHODS:
            return

        fetch_site = request.headers.get("Sec-Fetch-Site", "")
        if fetch_site in ("same-origin", "none"):
            g.presidio_csrf_ok = True
            return

        # Token-based fallback
        token = request.headers.get("X-CSRF-Token") or request.form.get("_csrf_token") or ""
        secret = app.config.get("SECRET_KEY")
        if not secret or secret == "presidio-dev-key":
            app.logger.error("PRESIDIO CSRF misconfigured: no strong SECRET_KEY set")
            abort(500)
        if token and _validate_token(secret, token):
            g.presidio_csrf_ok = True
            return

        if fetch_site and fetch_site not in ("same-origin", "none"):
            app.logger.warning(
                "Presidio CSRF: blocked cross-origin %s to %s (Sec-Fetch-Site: %s)",
                request.method,
                request.path,
                fetch_site,
            )
            abort(403)

        g.presidio_csrf_ok = False

"""Presidio-Hardened Flask – drop-in hardened replacement for Flask.

Usage::

    from presidio_flask import Flask, Blueprint, request, jsonify

    app = Flask(__name__)

    @app.route("/")
    def index():
        return "Hello, secure world!"

All standard Flask imports are re-exported so existing code works unchanged
while automatically receiving security hardening.
"""

from __future__ import annotations

__version__ = "0.1.0"

# ---------------------------------------------------------------------------
# Re-exports: users can ``from presidio_flask import ...`` instead of flask
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# Core: PresidioFlask subclass
# ---------------------------------------------------------------------------
import flask as _flask
from flask import (
    Blueprint,
    Request,
    Response,
    abort,
    current_app,
    g,
    jsonify,
    make_response,
    redirect,
    render_template,
    request,
    send_file,
    send_from_directory,
    session,
    url_for,
)

from ._csrf import generate_csrf_token, register_csrf_protection
from ._cve_check import run_cve_check
from ._headers import register_security_headers
from ._logging import register_security_logging
from ._rate_limit import register_rate_limiter
from ._redaction import redact_dict, register_redaction
from ._sanitize import register_input_sanitization
from ._session import register_session_hardening


class Flask(_flask.Flask):
    """Drop-in Flask replacement with automatic Presidio security hardening.

    All standard Flask functionality is preserved. Security middleware is
    registered automatically unless individually disabled via config flags:

    - ``PRESIDIO_RATE_LIMIT_ENABLED`` (default ``True``)
    - ``PRESIDIO_REDACTION_ENABLED`` (default ``True``)
    - ``PRESIDIO_CSRF_ENABLED`` (default ``True``)
    - ``PRESIDIO_SANITIZE_ENABLED`` (default ``True``)
    - ``PRESIDIO_LOGGING_ENABLED`` (default ``True``)
    - ``PRESIDIO_SECURITY_HEADERS`` (dict of header overrides)
    - ``PRESIDIO_RATE_LIMIT`` (int, requests per window, default 60)
    - ``PRESIDIO_RATE_WINDOW`` (int, seconds, default 60)
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._presidio_initialized = False
        register_session_hardening(self)

    def _apply_presidio_hardening(self) -> None:
        if self._presidio_initialized:
            return
        self._presidio_initialized = True

        register_security_logging(self)
        register_input_sanitization(self)
        register_redaction(self)
        register_csrf_protection(self)
        register_rate_limiter(self)
        register_security_headers(self)

        if self.config.get("PRESIDIO_CVE_CHECK", True):
            with self.app_context():
                run_cve_check(self)

        self.logger.info(
            "Presidio hardening v%s applied – all security middleware active.",
            __version__,
        )

    def __call__(self, environ, start_response):
        self._apply_presidio_hardening()
        return super().__call__(environ, start_response)


__all__ = [
    # Core
    "Flask",
    "Blueprint",
    "Request",
    "Response",
    # Globals & helpers
    "abort",
    "current_app",
    "g",
    "jsonify",
    "make_response",
    "redirect",
    "render_template",
    "request",
    "send_file",
    "send_from_directory",
    "session",
    "url_for",
    # Presidio extras
    "generate_csrf_token",
    "redact_dict",
    "__version__",
]

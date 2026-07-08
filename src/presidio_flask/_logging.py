"""Security event logging for Presidio hardening.

v0.2.0: Adds sink-level RedactingFilter to the Flask app logger for secret redaction
on all log output (addresses previous audit finding of incomplete redaction).
"""

from __future__ import annotations

import logging
import re
import time
from typing import TYPE_CHECKING

from flask import g, request

if TYPE_CHECKING:
    from flask import Flask


_FLASK_SECRET_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"(sk_(?:live|test)_)[A-Za-z0-9]+"), r"\1***REDACTED***"),
    (re.compile(r"(sk-ant-)[A-Za-z0-9\-_]+"), r"\1***REDACTED***"),
    (re.compile(r"(Bearer\s+)[A-Za-z0-9\-._~+/]+=*"), r"\1***REDACTED***"),
    (re.compile(r"(access_token=)[^&\s]+"), r"\1***REDACTED***"),
    (re.compile(r"(api_key=)[^&\s]+"), r"\1***REDACTED***"),
    # noqa: E501 - long regex required for broad secret matching
    (
        re.compile(r"(SECRET_KEY|password|token)[\"']?\s*[:=]\s*[\"']?[^\"'\s,]+", re.IGNORECASE),
        r"\1=***REDACTED***",
    ),
]


class RedactingFilter(logging.Filter):
    """Sink redaction filter for Flask app logs (v0.2)."""

    def filter(self, record: logging.LogRecord) -> bool:
        try:
            message = record.getMessage()
        except Exception:  # pragma: no cover
            return True
        for pattern, repl in _FLASK_SECRET_PATTERNS:
            message = pattern.sub(repl, message)
        record.msg = message
        record.args = None
        return True


def register_security_logging(app: Flask) -> None:
    if not app.config.get("PRESIDIO_LOGGING_ENABLED", True):
        return

    # v0.2: install sink redaction filter on the app logger
    app.logger.addFilter(RedactingFilter())

    if not app.logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter("[%(asctime)s] PRESIDIO %(levelname)s: %(message)s")
        )
        app.logger.addHandler(handler)
        app.logger.setLevel(logging.INFO)

    @app.before_request
    def _log_request_start() -> None:
        g.presidio_request_start = time.monotonic()
        app.logger.debug(
            "Presidio hardening applied to %s %s from %s",
            request.method,
            request.path,
            request.remote_addr,
        )

    @app.after_request
    def _log_request_end(response):
        start = getattr(g, "presidio_request_start", None)
        duration_ms = (time.monotonic() - start) * 1000 if start else 0
        app.logger.debug(
            "Presidio request completed: %s %s → %s (%.1fms)",
            request.method,
            request.path,
            response.status_code,
            duration_ms,
        )
        return response

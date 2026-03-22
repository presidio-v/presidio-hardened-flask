"""Security event logging for Presidio hardening."""

from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING

from flask import g, request

if TYPE_CHECKING:
    from flask import Flask


def register_security_logging(app: Flask) -> None:
    if not app.config.get("PRESIDIO_LOGGING_ENABLED", True):
        return

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

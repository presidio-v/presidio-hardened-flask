"""Input sanitization hooks for common OWASP top-10 risks."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

from flask import abort, request

if TYPE_CHECKING:
    from flask import Flask

_SQL_INJECTION_PATTERNS = [
    re.compile(
        r"(\b(UNION|SELECT|INSERT|UPDATE|DELETE|DROP|ALTER)\b.*\b(FROM|INTO|TABLE|SET)\b)",
        re.IGNORECASE,
    ),
    re.compile(r"(--|;)\s*(DROP|DELETE|UPDATE|INSERT)", re.IGNORECASE),
    re.compile(r"'\s*(OR|AND)\s+'", re.IGNORECASE),
]

_XSS_PATTERNS = [
    re.compile(r"<script[\s>]", re.IGNORECASE),
    re.compile(r"javascript\s*:", re.IGNORECASE),
    re.compile(r"on(error|load|click|mouseover)\s*=", re.IGNORECASE),
]

_PATH_TRAVERSAL = re.compile(r"\.\./|\.\.\\")


def _check_value(value: str) -> str | None:
    for pattern in _SQL_INJECTION_PATTERNS:
        if pattern.search(value):
            return "Potential SQL injection detected"
    for pattern in _XSS_PATTERNS:
        if pattern.search(value):
            return "Potential XSS detected"
    if _PATH_TRAVERSAL.search(value):
        return "Potential path traversal detected"
    return None


def _scan_values(data: dict) -> str | None:
    for value in data.values():
        if isinstance(value, str):
            threat = _check_value(value)
            if threat:
                return threat
    return None


def register_input_sanitization(app: Flask) -> None:
    if not app.config.get("PRESIDIO_SANITIZE_ENABLED", True):
        return

    @app.before_request
    def _sanitize_inputs() -> None:
        threat = _scan_values(dict(request.args))
        if threat:
            app.logger.warning("Presidio sanitizer: %s in query params", threat)
            abort(400)

        if request.is_json:
            json_data = request.get_json(silent=True)
            if isinstance(json_data, dict):
                threat = _scan_values(json_data)
                if threat:
                    app.logger.warning("Presidio sanitizer: %s in JSON body", threat)
                    abort(400)

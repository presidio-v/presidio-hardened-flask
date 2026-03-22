"""Request data secret redaction for logs and responses."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from flask import Flask

_SENSITIVE_KEYS = re.compile(
    r"(password|passwd|secret|token|api_key|apikey|access_key|auth|credential|private_key|ssn)",
    re.IGNORECASE,
)

_REDACTED = "***REDACTED***"


def redact_value(key: str, value: Any) -> Any:
    if isinstance(value, str) and _SENSITIVE_KEYS.search(key):
        return _REDACTED
    if isinstance(value, dict):
        return redact_dict(value)
    return value


def redact_dict(data: dict[str, Any]) -> dict[str, Any]:
    return {k: redact_value(k, v) for k, v in data.items()}


def is_sensitive_key(key: str) -> bool:
    return bool(_SENSITIVE_KEYS.search(key))


def register_redaction(app: Flask) -> None:
    if not app.config.get("PRESIDIO_REDACTION_ENABLED", True):
        return

    @app.before_request
    def _redact_log_context() -> None:
        from flask import request

        parts: list[str] = []
        if request.args:
            redacted_args = redact_dict(dict(request.args))
            parts.append(f"args={redacted_args}")
        if request.is_json and request.get_json(silent=True):
            redacted_json = redact_dict(request.get_json(silent=True))
            parts.append(f"json={redacted_json}")

        if parts:
            app.logger.debug("Presidio redacted request data: %s", "; ".join(parts))

"""Application-wide rate limiting with exponential backoff."""

from __future__ import annotations

import math
import time
from typing import TYPE_CHECKING

from flask import abort, g, request

if TYPE_CHECKING:
    from flask import Flask

_DEFAULT_LIMIT = 60
_DEFAULT_WINDOW = 60


class _RateLimitStore:
    """In-process token-bucket store keyed by remote address."""

    def __init__(self) -> None:
        self._buckets: dict[str, list[float]] = {}

    def hit(self, key: str, limit: int, window: int) -> tuple[bool, int, float]:
        now = time.monotonic()
        hits = self._buckets.setdefault(key, [])
        hits[:] = [t for t in hits if now - t < window]
        if len(hits) >= limit:
            earliest = hits[0]
            retry_after = earliest + window - now
            violation_count = len(hits) - limit + 1
            backoff = retry_after * math.pow(2, min(violation_count, 5))
            return False, limit - len(hits), backoff
        hits.append(now)
        return True, limit - len(hits), 0.0

    def reset(self) -> None:
        self._buckets.clear()


_store = _RateLimitStore()


def get_store() -> _RateLimitStore:
    return _store


def register_rate_limiter(app: Flask) -> None:
    limit = app.config.get("PRESIDIO_RATE_LIMIT", _DEFAULT_LIMIT)
    window = app.config.get("PRESIDIO_RATE_WINDOW", _DEFAULT_WINDOW)

    if not app.config.get("PRESIDIO_RATE_LIMIT_ENABLED", True):
        return

    @app.before_request
    def _rate_limit_check() -> None:
        key = request.remote_addr or "unknown"
        allowed, remaining, retry_after = _store.hit(key, limit, window)
        g.presidio_rate_remaining = max(remaining, 0)
        if not allowed:
            response = abort(429)
            # unreachable but keeps type-checkers happy
            return response  # noqa: B012, RET502

    @app.after_request
    def _rate_limit_headers(response):
        remaining = getattr(g, "presidio_rate_remaining", None)
        if remaining is not None:
            response.headers["X-RateLimit-Limit"] = str(limit)
            response.headers["X-RateLimit-Remaining"] = str(remaining)
        return response

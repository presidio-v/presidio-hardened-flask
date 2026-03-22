# Presidio-Hardened Flask – Top-Level Requirements

## Overview
Build a production-ready Python package `presidio-hardened-flask` that acts as a hardened replacement layer for Flask.
Users write: `from presidio_flask import Flask, Blueprint, request` (and similar re-exports) instead of directly from `flask`, and their existing Flask code mostly works unchanged while automatically receiving strong security defaults via middleware, config patches, and helpers.

## Mandatory Presidio Security Extensions
- Automatic security headers middleware (CSP, X-Content-Type-Options, X-Frame-Options, Strict-Transport-Security hints, Permissions-Policy, etc.)
- Built-in application-wide rate limiting with exponential backoff (using flask-limiter style logic)
- Request data secret redaction: scan JSON/form/query/headers for tokens/keys/passwords and redact in logs/responses
- Enhanced session cookie defaults (Secure, HttpOnly, SameSite=Lax/Strict, partitioned if possible)
- Automatic CSRF protection enforcement hints + helper for forms (build on modern Sec-Fetch-Site aware approach where feasible, fallback to token-based)
- Input sanitization / extra validation hooks for common OWASP top-10 risks
- On-startup dependency/CVE quick-check for Flask and key deps
- Security event logging ("Presidio hardening applied to request X")
- Full GitHub security files: SECURITY.md, .github/dependabot.yml, .github/workflows/codeql.yml + pytest + ruff workflow

## Technical Requirements
- Python 3.9+
- Modern pyproject.toml + hatchling/uv
- src/presidio_flask/__init__.py layout with re-exports, custom Flask subclass, and auto-applied middleware
- Do NOT copy Flask source; wrap/extend via subclassing Flask, before/after request hooks, and helpers
- 90%+ test coverage with pytest + client testing
- Black + ruff enforced
- README.md with side-by-side examples: plain Flask vs presidio-hardened-flask showing security improvements (e.g. headers, rate limit, redaction)
- LICENSE = MIT
- Version = 0.1.0


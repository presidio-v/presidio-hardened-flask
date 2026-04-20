# Presidio-Hardened Flask — Requirements

## Overview

`presidio-hardened-flask` is a drop-in replacement for Flask that applies
production-grade security defaults through a single import swap
(`from presidio_flask import Flask`). Developed on customer specification;
not linked to any PRES-EDU experiment (the Flask reference in
`PRES-EDU-SEC-101 Experiment 3` is to a deliberately-vulnerable target app,
not to this library).

## Mandatory Presidio Security Extensions

- Security response headers on every response — CSP, HSTS, X-Frame-Options,
  X-Content-Type-Options, Referrer-Policy, Permissions-Policy
- Rate limiting per IP (60 req/min default, exponential backoff,
  configurable)
- CSRF protection — `Sec-Fetch-Site` aware with a token-based fallback for
  legacy clients and mutating requests
- Secret redaction — passwords, API keys, and tokens are scrubbed from log
  output
- Session hardening — `Secure`, `HttpOnly`, `SameSite=Lax` cookies by
  default
- Input sanitisation — SQL-injection, XSS, and path-traversal attempts are
  rejected before the view function runs
- On-startup CVE quick-check for Flask and the caller's security-relevant
  dependencies
- Structured security event logging for every hardened request
  (`presidio_flask` logger)
- Full GitHub security files: `SECURITY.md`, `.github/dependabot.yml`,
  `.github/workflows/codeql.yml`, `.github/workflows/ci.yml`

## Technical Requirements

- Python 3.9+
- `flask` (upstream dependency — not wrapped)
- `src/presidio_flask/` layout
- pytest with ≥ 90 % line coverage (enforced by `--cov-fail-under=90`)
- ruff lint + format enforced in CI
- MIT License, version 0.1.0

## Out of scope

- WSGI server hardening — handled by the deployment (gunicorn, uWSGI,
  waitress) not by the library
- Vulnerabilities in upstream Flask / Werkzeug / Jinja (reported directly
  to those projects)

## Version Deliberation Log

### v0.1.0 — Initial release

**Scope decision:** Import-swap pattern over a Flask-extension pattern. The
customer's brief mandated *zero code changes* beyond the import line so
that the hardening baseline could be rolled out across an inventory of
Flask apps without per-app review. A Flask-extension approach would have
required every app to wire `init_app(app)` calls correctly.

**Scope decision:** CSRF uses `Sec-Fetch-Site` as the primary signal with a
token fallback, rather than pure token-based CSRF. Modern browsers send
`Sec-Fetch-Site` reliably and a Sec-Fetch-Site=same-origin check blocks
cross-site mutating requests without the form-field plumbing; the token
fallback covers older browsers and non-browser clients that cannot rely on
the header. This matches the customer's threat model (predominantly modern
SPA clients with a handful of legacy integrations).

**Scope decision:** Python 3.9+ floor. The customer's deployment targets
include Ubuntu 20.04 LTS (Python 3.8 EOL, 3.9 available via `deadsnakes`);
raising above 3.9 would have excluded existing production hosts.

**Scope decision:** Rate-limit defaults (60 req/min per IP) match the
customer's existing reverse-proxy policy to avoid conflicting throttles.

## SDLC

These requirements are delivered under the family-wide Presidio SDLC:
<https://github.com/presidio-v/presidio-hardened-docs/blob/main/sdlc/sdlc-report.md>.

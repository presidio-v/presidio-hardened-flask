# Security Policy

## Supported Versions

| Version | Supported          |
|---------|--------------------|
| 0.2.x   | :white_check_mark: (current) |
| 0.1.x   | :white_check_mark: (legacy) |

## Reporting a Vulnerability

If you discover a security vulnerability in presidio-hardened-flask, please report it responsibly.

**Do NOT open a public GitHub issue for security vulnerabilities.**

Instead, please email: **security@presidio.dev**

Include:
- A description of the vulnerability
- Steps to reproduce
- Potential impact assessment
- Suggested fix (if any)

### Response Timeline

- **Acknowledgment**: Within 48 hours
- **Initial Assessment**: Within 5 business days
- **Fix/Patch**: Within 30 days for critical issues

### Disclosure Policy

- We follow **coordinated disclosure** practices.
- We will credit reporters (unless anonymity is requested) in the release notes.
- We aim to release patches before any public disclosure.

## Security Features (v0.2.0)

This package provides the following security hardening for Flask applications:

1. **Security Headers** — CSP, HSTS, X-Frame-Options, Permissions-Policy, X-Content-Type-Options
2. **Rate Limiting** — Per-IP rate limiting with exponential backoff
3. **CSRF Protection** — Sec-Fetch-Site aware with HMAC token fallback (v0.2: no dangerous 'presidio-dev-key' fallback; requires strong SECRET_KEY)
4. **Secret Redaction** — Key-based + pattern redaction in before_request; sink-level RedactingFilter on app.logger for *all* log records (v0.2)
5. **Session Hardening** — Secure, HttpOnly, SameSite=Lax cookie defaults
6. **Input Sanitization** — SQL injection, XSS, and path traversal detection (before_request abort on match)
7. **CVE Quick-Check** — Startup check + pip-audit in dev/CI (v0.2)
8. **Security Event Logging** — Structured logging (with automatic sink redaction)

## Dependencies

We keep our dependency surface minimal:

- **Flask** ≥ 2.3 (the framework we harden)
- No additional runtime dependencies

Development dependencies are isolated in the `[dev]` extra.

## Best Practices for Users

1. **Always set a strong `SECRET_KEY`** in production (v0.2 enforces this for CSRF; old weak default removed).
2. Deploy behind HTTPS to benefit from HSTS and Secure cookies.
3. Review the default CSP and adjust for your application's needs.
4. Monitor the Presidio security logs for anomalous activity (redaction is now sink-enforced).
5. Keep dependencies updated — `pip-audit` is included in dev extras and CI.
6. Use the redaction/sanitize helpers where additional control is needed on responses or specific inputs.

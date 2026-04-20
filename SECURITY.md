# Security Policy

## Supported Versions

| Version | Supported          |
|---------|--------------------|
| 0.1.x   | :white_check_mark: |

## Reporting a Vulnerability

Please report security vulnerabilities by opening a private GitHub Security Advisory
(via the "Security" tab → "Report a vulnerability") rather than a public issue.

Include:

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

You will receive an acknowledgement within 5 business days. We aim to release a patch
within 30 days of a confirmed vulnerability.

## Security Features

This package provides the following security hardening for Flask applications:

1. **Security Headers** — CSP, HSTS, X-Frame-Options, Permissions-Policy, X-Content-Type-Options
2. **Rate Limiting** — Per-IP rate limiting with exponential backoff
3. **CSRF Protection** — Sec-Fetch-Site aware with HMAC token fallback
4. **Secret Redaction** — Automatic redaction of passwords, tokens, and API keys in logs
5. **Session Hardening** — Secure, HttpOnly, SameSite=Lax cookie defaults
6. **Input Sanitization** — SQL injection, XSS, and path traversal detection
7. **CVE Quick-Check** — Startup check against known vulnerabilities in dependencies
8. **Security Event Logging** — Structured logging for security-relevant events

## Dependencies

We keep our dependency surface minimal:

- **Flask** ≥ 2.3 (the framework we harden)
- No additional runtime dependencies

Development dependencies are isolated in the `[dev]` extra.

## Best Practices for Users

1. Always set a strong `SECRET_KEY` in production
2. Deploy behind HTTPS to benefit from HSTS and Secure cookies
3. Review the default CSP and adjust for your application's needs
4. Monitor the Presidio security logs for anomalous activity
5. Keep dependencies updated — enable Dependabot or similar tools

## Software Development Lifecycle

This repository is developed under the Presidio hardened-family SDLC. The public report
— scope, standards mapping, threat-model gates, and supply-chain controls — is at
<https://github.com/presidio-v/presidio-hardened-docs/blob/main/sdlc/sdlc-report.md>.

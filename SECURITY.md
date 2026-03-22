# Security Policy

## Supported Versions

| Version | Supported          |
|---------|--------------------|
| 0.1.x   | :white_check_mark: |

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

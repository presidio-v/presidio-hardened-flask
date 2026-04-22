# presidio-hardened-flask

[![CI](https://github.com/presidio-v/presidio-hardened-flask/actions/workflows/ci.yml/badge.svg)](https://github.com/presidio-v/presidio-hardened-flask/actions/workflows/ci.yml)
[![CodeQL](https://github.com/presidio-v/presidio-hardened-flask/actions/workflows/codeql.yml/badge.svg)](https://github.com/presidio-v/presidio-hardened-flask/actions/workflows/codeql.yml)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A **hardened drop-in replacement** for Flask that automatically applies production-grade security defaults. Change one import line and your existing Flask app gets security headers, rate limiting, CSRF protection, secret redaction, input sanitization, and more.

## Quick Start

### Install

```bash
pip install presidio-hardened-flask
```

### Usage — Change One Import

**Before (plain Flask):**

```python
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route("/")
def index():
    return "Hello, world!"
```

**After (presidio-hardened-flask):**

```python
from presidio_flask import Flask, jsonify, request

app = Flask(__name__)

@app.route("/")
def index():
    return "Hello, secure world!"
```

That's it. Your app now automatically receives:

| Feature | What It Does |
|---|---|
| **Security Headers** | CSP, HSTS, X-Frame-Options, Permissions-Policy, and more on every response |
| **Rate Limiting** | 60 req/min per IP with exponential backoff (configurable) |
| **CSRF Protection** | Sec-Fetch-Site aware + token-based fallback for mutating requests |
| **Secret Redaction** | Passwords, API keys, and tokens are redacted in logs |
| **Session Hardening** | Secure, HttpOnly, SameSite=Lax cookies by default |
| **Input Sanitization** | Blocks SQL injection, XSS, and path traversal attempts |
| **CVE Quick-Check** | Warns at startup if key dependencies have known vulnerabilities |
| **Security Logging** | Structured Presidio event logging for all requests |

## Side-by-Side Comparison

### Security Headers

**Plain Flask** returns no security headers by default:

```
HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8
```

**presidio-hardened-flask** adds them automatically:

```
HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Referrer-Policy: strict-origin-when-cross-origin
Content-Security-Policy: default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'
Strict-Transport-Security: max-age=63072000; includeSubDomains; preload
Permissions-Policy: geolocation=(), camera=(), microphone=()
Cross-Origin-Opener-Policy: same-origin
Cross-Origin-Resource-Policy: same-origin
```

### Rate Limiting

**Plain Flask** has no built-in rate limiting. A single client can hammer your API.

**presidio-hardened-flask** enforces per-IP rate limits with informative headers:

```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 57
```

When exceeded, returns `429 Too Many Requests` with exponential backoff.

### Secret Redaction

**Plain Flask** will happily log passwords and tokens in plain text:

```python
app.logger.info("Request: %s", request.json)
# {"username": "alice", "password": "hunter2", "api_key": "sk-live-abc123"}
```

**presidio-hardened-flask** automatically redacts sensitive fields:

```python
from presidio_flask import redact_dict
print(redact_dict({"password": "hunter2", "api_key": "sk-123"}))
# {"password": "***REDACTED***", "api_key": "***REDACTED***"}
```

### CSRF Protection

**Plain Flask** has no CSRF protection.

**presidio-hardened-flask** uses a modern two-layer approach:

1. **Sec-Fetch-Site header** — blocks cross-origin mutating requests automatically
2. **Token-based fallback** — for older browsers or custom setups

```python
from presidio_flask import generate_csrf_token

# In your template / API response:
token = generate_csrf_token()
# Include as X-CSRF-Token header or _csrf_token form field
```

## Configuration

All features are enabled by default but fully configurable:

```python
app = Flask(__name__)
app.config.update(
    # Rate limiting
    PRESIDIO_RATE_LIMIT=100,           # requests per window (default: 60)
    PRESIDIO_RATE_WINDOW=120,          # window in seconds (default: 60)
    PRESIDIO_RATE_LIMIT_ENABLED=True,  # disable entirely if False

    # CSRF
    PRESIDIO_CSRF_ENABLED=True,

    # Input sanitization
    PRESIDIO_SANITIZE_ENABLED=True,

    # Secret redaction
    PRESIDIO_REDACTION_ENABLED=True,

    # Security logging
    PRESIDIO_LOGGING_ENABLED=True,

    # CVE check on startup
    PRESIDIO_CVE_CHECK=True,

    # Custom security headers (merge with/override defaults)
    PRESIDIO_SECURITY_HEADERS={
        "X-Frame-Options": "SAMEORIGIN",
        "Content-Security-Policy": "default-src 'self'; img-src *",
    },
)
```

## Development

```bash
# Clone and install
git clone https://github.com/presidio-v/presidio-hardened-flask.git
cd presidio-hardened-flask
uv venv .venv && source .venv/bin/activate
uv pip install -e ".[dev]"

# Run tests
pytest --cov=presidio_flask

# Lint and format
ruff format .
ruff check . --fix
```

## License

[MIT](LICENSE)

"""On-startup dependency/CVE quick-check for Flask and key dependencies."""

from __future__ import annotations

import importlib.metadata
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from flask import Flask

_KEY_PACKAGES = ["flask", "werkzeug", "jinja2", "markupsafe", "itsdangerous"]

_KNOWN_VULNERABLE: dict[str, str] = {
    "werkzeug<2.3.3": "CVE-2023-23934 – cookie parsing vulnerability",
    "flask<2.3.2": "CVE-2023-30861 – session cookie security",
}


def _parse_constraint(spec: str) -> tuple[str, str, str]:
    for op in ("<=", ">=", "<", ">", "=="):
        if op in spec:
            name, ver = spec.split(op, 1)
            return name.strip(), op, ver.strip()
    return spec, "", ""


def _version_tuple(v: str) -> tuple[int, ...]:
    return tuple(int(x) for x in v.split(".") if x.isdigit())


def _check_vulnerable(name: str, version: str) -> list[str]:
    warnings: list[str] = []
    ver = _version_tuple(version)
    for spec, desc in _KNOWN_VULNERABLE.items():
        pkg, op, threshold = _parse_constraint(spec)
        if pkg != name:
            continue
        thr = _version_tuple(threshold)
        if op == "<" and ver < thr:
            warnings.append(f"  ⚠  {name}=={version} may be affected by {desc}")
    return warnings


def run_cve_check(app: Flask) -> None:
    app.logger.info("Presidio CVE quick-check starting...")
    all_warnings: list[str] = []
    for pkg in _KEY_PACKAGES:
        try:
            version = importlib.metadata.version(pkg)
            app.logger.info("  ✓ %s==%s", pkg, version)
            all_warnings.extend(_check_vulnerable(pkg, version))
        except importlib.metadata.PackageNotFoundError:
            app.logger.warning("  ? %s not found", pkg)

    if all_warnings:
        for w in all_warnings:
            app.logger.warning(w)
    else:
        app.logger.info("  No known CVEs detected in key dependencies.")

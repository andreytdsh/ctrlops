"""SSL certificate inspection service."""

from __future__ import annotations

import json
import socket
import ssl
from datetime import UTC, datetime
from typing import Any

from ctrlops.database import connect, now_iso
from ctrlops.utils.validators import validate_domain


def calculate_ssl_status(days_remaining: int) -> str:
    """Return OK, WARNING or EXPIRED from days remaining."""

    if days_remaining <= 0:
        return "EXPIRED"
    if days_remaining <= 30:
        return "WARNING"
    return "OK"


def _parse_cert_date(value: str) -> datetime:
    return datetime.strptime(value, "%b %d %H:%M:%S %Y %Z").replace(tzinfo=UTC)


def check_ssl(domain: str, port: int = 443, timeout: float = 5.0) -> dict[str, Any]:
    """Inspect a domain's TLS certificate."""

    normalized = validate_domain(domain)
    context = ssl.create_default_context()
    with socket.create_connection((normalized, port), timeout=timeout) as sock:
        with context.wrap_socket(sock, server_hostname=normalized) as tls:
            cert = tls.getpeercert()

    valid_from = _parse_cert_date(cert["notBefore"])
    valid_until = _parse_cert_date(cert["notAfter"])
    days_remaining = (valid_until - datetime.now(UTC)).days
    subject = dict(item[0] for item in cert.get("subject", []))
    issuer = dict(item[0] for item in cert.get("issuer", []))
    sans = [value for key, value in cert.get("subjectAltName", []) if key == "DNS"]

    result = {
        "domain": normalized,
        "common_name": subject.get("commonName", normalized),
        "issuer": issuer.get("organizationName") or issuer.get("commonName", "Unknown"),
        "valid_from": valid_from.isoformat(),
        "valid_until": valid_until.isoformat(),
        "days_remaining": days_remaining,
        "status": calculate_ssl_status(days_remaining),
        "sans": sans,
    }
    with connect() as connection:
        connection.execute(
            """
            INSERT INTO ssl_history (domain, status, days_remaining, payload, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                normalized,
                result["status"],
                days_remaining,
                json.dumps(result, default=str),
                now_iso(),
            ),
        )
    return result

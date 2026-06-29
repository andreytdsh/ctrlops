"""DNS inspection service."""

from __future__ import annotations

from typing import Any

import dns.exception
import dns.resolver

from ctrlops.database import connect, now_iso
from ctrlops.utils.validators import validate_domain

RECORD_TYPES = ("A", "AAAA", "MX", "NS", "TXT", "CNAME")


def inspect_dns(domain: str) -> dict[str, Any]:
    """Return common DNS records for a domain."""

    normalized = validate_domain(domain)
    resolver = dns.resolver.Resolver()
    result: dict[str, Any] = {"domain": normalized, "records": {}, "errors": []}

    for record_type in RECORD_TYPES:
        try:
            answer = resolver.resolve(normalized, record_type, raise_on_no_answer=False)
            records = []
            for item in answer:
                value = item.to_text().strip('"')
                records.append({"type": record_type, "value": value, "ttl": answer.rrset.ttl})
            result["records"][record_type] = records
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
            result["records"][record_type] = []
        except dns.exception.DNSException as exc:
            result["records"][record_type] = []
            result["errors"].append(f"{record_type}: {exc}")

    with connect() as connection:
        connection.execute(
            "INSERT OR IGNORE INTO saved_domains (domain, created_at) VALUES (?, ?)",
            (normalized, now_iso()),
        )
    return result

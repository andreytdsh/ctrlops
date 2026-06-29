"""Input validation helpers."""

from __future__ import annotations

import re
from pathlib import Path

DOMAIN_RE = re.compile(
    r"^(?=.{1,253}$)(?!-)(?:[a-zA-Z0-9-]{1,63}\.)+[a-zA-Z]{2,63}\.?$"
)


def validate_domain(domain: str) -> str:
    """Validate and normalize a DNS domain name."""

    normalized = domain.strip().rstrip(".").lower()
    if not DOMAIN_RE.match(normalized):
        raise ValueError(f"Invalid domain: {domain}")
    return normalized


def resolve_existing_path(path: str | Path) -> Path:
    """Resolve a path and require that it exists."""

    resolved = Path(path).expanduser().resolve()
    if not resolved.exists():
        raise ValueError(f"Path does not exist: {path}")
    return resolved


def ensure_safe_restore_target(path: str | Path) -> Path:
    """Resolve a restore target without allowing archive traversal tricks."""

    resolved = Path(path).expanduser().resolve()
    if resolved.anchor == str(resolved):
        raise ValueError("Refusing to restore directly into a filesystem root")
    resolved.mkdir(parents=True, exist_ok=True)
    return resolved

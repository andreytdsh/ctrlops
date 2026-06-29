"""Formatting helpers for human output."""

from __future__ import annotations


def format_bytes(size: int | float) -> str:
    """Format bytes as a human readable string."""

    value = float(size)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if value < 1024 or unit == "TB":
            return f"{value:.1f} {unit}" if unit != "B" else f"{int(value)} B"
        value /= 1024
    return f"{value:.1f} TB"

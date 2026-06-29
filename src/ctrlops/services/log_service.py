"""Access log analyzer for common Nginx/Apache logs."""

from __future__ import annotations

import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from ctrlops.utils.validators import resolve_existing_path

LOG_RE = re.compile(
    r'(?P<ip>\S+) \S+ \S+ \[(?P<time>[^\]]+)\] "(?P<method>\S+) (?P<url>\S+) [^"]+" '
    r"(?P<status>\d{3}) (?P<size>\S+)"
)


def analyze_log(path: str | Path, top_n: int = 10) -> dict[str, Any]:
    """Analyze an Apache/Nginx access log."""

    log_path = resolve_existing_path(path)
    total = 0
    ips: Counter[str] = Counter()
    urls: Counter[str] = Counter()
    statuses: Counter[str] = Counter()
    per_minute: defaultdict[str, int] = defaultdict(int)

    with log_path.open("r", encoding="utf-8", errors="replace") as file:
        for line in file:
            match = LOG_RE.search(line)
            if not match:
                continue
            total += 1
            data = match.groupdict()
            ips[data["ip"]] += 1
            urls[data["url"]] += 1
            statuses[data["status"]] += 1
            per_minute[data["time"][:17]] += 1

    return {
        "file": str(log_path),
        "total_requests": total,
        "top_ips": ips.most_common(top_n),
        "top_urls": urls.most_common(top_n),
        "status_distribution": dict(sorted(statuses.items())),
        "count_404": statuses.get("404", 0),
        "count_500": statuses.get("500", 0),
        "requests_per_minute": dict(sorted(per_minute.items())),
    }

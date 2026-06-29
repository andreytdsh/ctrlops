"""Server health checks."""

from __future__ import annotations

import os
import platform
import shutil
import subprocess
import time
from typing import Any

import psutil


def get_health() -> dict[str, Any]:
    """Return local server health metrics."""

    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    try:
        load_average = os.getloadavg()
    except (AttributeError, OSError):
        load_average = (0.0, 0.0, 0.0)

    docker_available = shutil.which("docker") is not None
    docker_version = None
    if docker_available:
        result = subprocess.run(
            ["docker", "--version"],
            text=True,
            capture_output=True,
            timeout=5,
            check=False,
        )
        docker_version = result.stdout.strip() if result.returncode == 0 else "installed"

    return {
        "os": platform.platform(),
        "kernel": platform.release(),
        "uptime_seconds": int(time.time() - psutil.boot_time()),
        "cpu_usage_percent": psutil.cpu_percent(interval=0.1),
        "ram": {
            "total": memory.total,
            "used": memory.used,
            "percent": memory.percent,
        },
        "disk": {
            "total": disk.total,
            "used": disk.used,
            "percent": disk.percent,
        },
        "load_average": load_average,
        "process_count": len(psutil.pids()),
        "docker": {
            "available": docker_available,
            "version": docker_version,
        },
    }

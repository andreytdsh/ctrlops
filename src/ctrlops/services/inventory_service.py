"""Local inventory scanning."""

from __future__ import annotations

import platform
import shutil
import socket
import subprocess
from typing import Any

import psutil


def _installed_packages(limit: int = 50) -> list[str]:
    commands = [
        ["dpkg-query", "-W", "-f=${binary:Package}\n"],
        ["rpm", "-qa"],
    ]
    for command in commands:
        if shutil.which(command[0]):
            result = subprocess.run(
                command,
                text=True,
                capture_output=True,
                timeout=10,
                check=False,
            )
            if result.returncode == 0:
                return sorted(result.stdout.splitlines())[:limit]
    return []


def _docker_containers() -> list[str]:
    if not shutil.which("docker"):
        return []
    result = subprocess.run(
        ["docker", "ps", "--format", "{{.Names}}"],
        text=True,
        capture_output=True,
        timeout=5,
        check=False,
    )
    return result.stdout.splitlines() if result.returncode == 0 else []


def _open_ports() -> list[int]:
    ports: set[int] = set()
    for conn in psutil.net_connections(kind="inet"):
        if conn.status == psutil.CONN_LISTEN and conn.laddr:
            ports.add(conn.laddr.port)
    return sorted(ports)


def scan_inventory() -> dict[str, Any]:
    """Return local host inventory information."""

    return {
        "hostname": socket.gethostname(),
        "os": platform.platform(),
        "kernel": platform.release(),
        "cpu": platform.processor() or f"{psutil.cpu_count(logical=True)} logical CPUs",
        "ram_bytes": psutil.virtual_memory().total,
        "disks": [
            {
                "device": part.device,
                "mountpoint": part.mountpoint,
                "fstype": part.fstype,
                "total_bytes": psutil.disk_usage(part.mountpoint).total,
            }
            for part in psutil.disk_partitions(all=False)
        ],
        "network_interfaces": {
            name: [addr.address for addr in addrs]
            for name, addrs in psutil.net_if_addrs().items()
        },
        "installed_packages": _installed_packages(),
        "docker_containers": _docker_containers(),
        "open_ports": _open_ports(),
    }

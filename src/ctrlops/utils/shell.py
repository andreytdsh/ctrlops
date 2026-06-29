"""Safe shell execution helpers."""

from __future__ import annotations

import subprocess
from pathlib import Path


def run_configured_command(
    command: str,
    cwd: Path,
    timeout: int = 600,
) -> subprocess.CompletedProcess[str]:
    """Run an explicitly configured deployment command."""

    return subprocess.run(
        command,
        cwd=cwd,
        shell=True,
        text=True,
        capture_output=True,
        timeout=timeout,
        check=False,
    )

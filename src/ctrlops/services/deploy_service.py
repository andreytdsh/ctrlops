"""Configured deployment runner."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from ctrlops.config import Settings, load_settings
from ctrlops.database import connect, now_iso
from ctrlops.utils.shell import run_configured_command

DEPLOYMENT_NAME_RE = re.compile(r"^[a-zA-Z0-9_-]{1,64}$")


def list_deployments(settings: Settings | None = None) -> list[str]:
    """List deployment names from configuration."""

    current_settings = settings or load_settings()
    return sorted(current_settings.deployments)


def list_deployment_configs(settings: Settings | None = None) -> list[dict[str, Any]]:
    """List deployment configurations."""

    current_settings = settings or load_settings()
    return [
        {
            "name": deployment.name,
            "path": str(deployment.path),
            "commands": deployment.commands,
        }
        for deployment in sorted(
            current_settings.deployments.values(),
            key=lambda item: item.name,
        )
    ]


def get_deployment_config(name: str, settings: Settings | None = None) -> dict[str, Any]:
    """Return one deployment configuration."""

    current_settings = settings or load_settings()
    deployment = current_settings.deployments.get(name)
    if deployment is None:
        raise ValueError(f"Deployment '{name}' is not configured in ctrlops.yml")
    return {
        "name": deployment.name,
        "path": str(deployment.path),
        "commands": deployment.commands,
    }


def create_deployment(
    name: str,
    path: str,
    commands_text: str,
    config_path: str = "ctrlops.yml",
) -> dict[str, Any]:
    """Add or update a deployment in ctrlops.yml."""

    normalized_name = name.strip()
    if not DEPLOYMENT_NAME_RE.match(normalized_name):
        raise ValueError(
            "Deployment name may only contain letters, numbers, underscores and dashes"
        )

    deployment_path = path.strip()
    if not deployment_path:
        raise ValueError("Deployment path is required")

    commands = [line.strip() for line in commands_text.splitlines() if line.strip()]
    if not commands:
        raise ValueError("At least one deployment command is required")

    config_file = load_settings_path(config_path)
    data = read_config_data(config_file)
    deployments = data.setdefault("deployments", {})
    if not isinstance(deployments, dict):
        raise ValueError("ctrlops.yml deployments section must be a mapping")

    deployments[normalized_name] = {
        "path": deployment_path,
        "commands": commands,
    }
    with config_file.open("w", encoding="utf-8") as file:
        yaml.safe_dump(data, file, sort_keys=False, allow_unicode=True)

    return {"name": normalized_name, "path": deployment_path, "commands": commands}


def load_settings_path(config_path: str) -> Path:
    """Return config path, creating parent directories when needed."""

    path = Path(config_path)
    if path.parent != Path("."):
        path.parent.mkdir(parents=True, exist_ok=True)
    return path


def read_config_data(config_file: Path) -> dict[str, Any]:
    """Read ctrlops.yml as a YAML mapping."""

    if not config_file.exists():
        return {"app": {"backup_dir": "./backups", "database_url": "sqlite:///ctrlops.db"}}
    with config_file.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file) or {}
    if not isinstance(data, dict):
        raise ValueError("ctrlops.yml must contain a YAML mapping")
    return data


def run_deployment(name: str, settings: Settings | None = None) -> dict[str, Any]:
    """Run a configured deployment by name."""

    current_settings = settings or load_settings()
    deployment = current_settings.deployments.get(name)
    if deployment is None:
        raise ValueError(f"Deployment '{name}' is not configured in ctrlops.yml")
    if not deployment.path.exists() or not deployment.path.is_dir():
        raise ValueError(f"Deployment path does not exist or is not a directory: {deployment.path}")
    if not deployment.commands:
        raise ValueError(f"Deployment '{name}' has no commands")

    output: list[str] = []
    status = "success"
    for command in deployment.commands:
        output.append(f"$ {command}")
        result = run_configured_command(command, deployment.path)
        if result.stdout:
            output.append(result.stdout.rstrip())
        if result.stderr:
            output.append(result.stderr.rstrip())
        if result.returncode != 0:
            status = "failed"
            output.append(f"Command failed with exit code {result.returncode}")
            break

    combined = "\n".join(output)
    with connect() as connection:
        connection.execute(
            "INSERT INTO deployment_logs (name, status, output, created_at) VALUES (?, ?, ?, ?)",
            (name, status, combined, now_iso()),
        )
    return {"name": name, "status": status, "output": combined}


def recent_deployment_logs(limit: int = 20) -> list[dict[str, Any]]:
    """Return recent deployment log entries."""

    with connect() as connection:
        rows = connection.execute(
            """
            SELECT name, status, output, created_at
            FROM deployment_logs
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [dict(row) for row in rows]

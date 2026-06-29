"""Configuration loading for CtrlOps."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml
from dotenv import load_dotenv


@dataclass(frozen=True)
class DeploymentConfig:
    """A configured deployment target."""

    name: str
    path: Path
    commands: list[str]


@dataclass(frozen=True)
class Settings:
    """Runtime settings loaded from environment and ctrlops.yml."""

    backup_dir: Path = Path("./backups")
    database_url: str = "sqlite:///ctrlops.db"
    host: str = "127.0.0.1"
    port: int = 8000
    deployments: dict[str, DeploymentConfig] = field(default_factory=dict)


def _read_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file) or {}
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a YAML mapping")
    return data


def load_settings(config_path: Path | str = "ctrlops.yml") -> Settings:
    """Load settings from .env, environment variables and ctrlops.yml."""

    load_dotenv()
    path = Path(config_path)
    data = _read_yaml(path)
    app_config = data.get("app", {}) if isinstance(data.get("app", {}), dict) else {}

    backup_dir = Path(
        os.getenv("CTRLOPS_BACKUP_DIR") or app_config.get("backup_dir") or "./backups"
    )
    database_url = (
        os.getenv("CTRLOPS_DATABASE_URL") or app_config.get("database_url") or "sqlite:///ctrlops.db"
    )
    host = os.getenv("CTRLOPS_HOST") or app_config.get("host") or "127.0.0.1"
    port = int(os.getenv("CTRLOPS_PORT") or app_config.get("port") or 8000)

    deployments: dict[str, DeploymentConfig] = {}
    raw_deployments = data.get("deployments", {})
    if isinstance(raw_deployments, dict):
        for name, raw in raw_deployments.items():
            if not isinstance(raw, dict):
                continue
            commands = raw.get("commands", [])
            if isinstance(commands, list) and all(isinstance(item, str) for item in commands):
                deployments[name] = DeploymentConfig(
                    name=name,
                    path=Path(raw.get("path", ".")),
                    commands=commands,
                )

    return Settings(
        backup_dir=backup_dir,
        database_url=database_url,
        host=host,
        port=port,
        deployments=deployments,
    )


def sqlite_path(database_url: str) -> Path:
    """Return a filesystem path for a sqlite:/// database URL."""

    prefix = "sqlite:///"
    if not database_url.startswith(prefix):
        raise ValueError("Only sqlite:/// database URLs are supported")
    return Path(database_url.removeprefix(prefix))

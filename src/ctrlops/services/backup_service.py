"""Backup creation, listing and restore service."""

from __future__ import annotations

import tarfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ctrlops.config import Settings, load_settings
from ctrlops.database import connect, now_iso
from ctrlops.utils.validators import ensure_safe_restore_target, resolve_existing_path


def create_backup(path: str | Path, settings: Settings | None = None) -> dict[str, Any]:
    """Create a .tar.gz backup for a file or directory."""

    current_settings = settings or load_settings()
    source = resolve_existing_path(path)
    backup_dir = current_settings.backup_dir.expanduser().resolve()
    backup_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
    archive = backup_dir / f"{source.name}-{timestamp}.tar.gz"

    with tarfile.open(archive, "w:gz") as tar:
        tar.add(source, arcname=source.name)

    size = archive.stat().st_size
    with connect() as connection:
        connection.execute(
            """
            INSERT INTO backup_records (file, source_path, size_bytes, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (str(archive), str(source), size, now_iso()),
        )
    return {"file": str(archive), "source_path": str(source), "size_bytes": size}


def list_backups(settings: Settings | None = None) -> list[dict[str, Any]]:
    """List backup archives from the configured directory."""

    current_settings = settings or load_settings()
    backup_dir = current_settings.backup_dir.expanduser().resolve()
    if not backup_dir.exists():
        return []
    backups = []
    for file in sorted(
        backup_dir.glob("*.tar.gz"),
        key=lambda item: item.stat().st_mtime,
        reverse=True,
    ):
        stat = file.stat()
        backups.append(
            {
                "file": str(file),
                "name": file.name,
                "size_bytes": stat.st_size,
                "created_at": datetime.fromtimestamp(stat.st_mtime, UTC).isoformat(
                    timespec="seconds"
                ),
            }
        )
    return backups


def _safe_extract(tar: tarfile.TarFile, target: Path) -> None:
    target_root = target.resolve()
    for member in tar.getmembers():
        destination = (target_root / member.name).resolve()
        if not destination.is_relative_to(target_root):
            raise ValueError(f"Unsafe path in archive: {member.name}")
    tar.extractall(target_root, filter="data")


def restore_backup(file: str | Path, target: str | Path) -> dict[str, Any]:
    """Restore a backup archive into a target directory."""

    archive = resolve_existing_path(file)
    target_path = ensure_safe_restore_target(target)
    if not tarfile.is_tarfile(archive):
        raise ValueError(f"Not a valid tar archive: {file}")
    with tarfile.open(archive, "r:gz") as tar:
        _safe_extract(tar, target_path)
    return {"file": str(archive), "target": str(target_path)}

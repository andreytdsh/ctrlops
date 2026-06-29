"""Small SQLite persistence layer."""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from ctrlops.config import load_settings, sqlite_path


def get_database_path() -> Path:
    """Return the configured SQLite database path."""

    return sqlite_path(load_settings().database_url)


@contextmanager
def connect(path: Path | None = None) -> Iterator[sqlite3.Connection]:
    """Open a SQLite connection and initialize the schema."""

    db_path = path or get_database_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    try:
        initialize(connection)
        yield connection
        connection.commit()
    finally:
        connection.close()


def initialize(connection: sqlite3.Connection) -> None:
    """Create database tables if they do not exist."""

    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS command_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            command TEXT NOT NULL,
            payload TEXT,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS backup_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file TEXT NOT NULL,
            source_path TEXT NOT NULL,
            size_bytes INTEGER NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS deployment_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            status TEXT NOT NULL,
            output TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS saved_domains (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            domain TEXT NOT NULL UNIQUE,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS ssl_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            domain TEXT NOT NULL,
            status TEXT NOT NULL,
            days_remaining INTEGER NOT NULL,
            payload TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        """
    )


def now_iso() -> str:
    """Return current UTC time in ISO format."""

    return datetime.now(UTC).isoformat(timespec="seconds")


def record_command(command: str, payload: dict[str, Any] | None = None) -> None:
    """Persist a command invocation."""

    with connect() as connection:
        connection.execute(
            "INSERT INTO command_history (command, payload, created_at) VALUES (?, ?, ?)",
            (command, json.dumps(payload or {}, default=str), now_iso()),
        )


def list_backup_records() -> list[dict[str, Any]]:
    """Return backup records ordered newest first."""

    with connect() as connection:
        rows = connection.execute(
            "SELECT file, source_path, size_bytes, created_at FROM backup_records ORDER BY id DESC"
        ).fetchall()
    return [dict(row) for row in rows]

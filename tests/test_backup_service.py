from pathlib import Path

from ctrlops.config import Settings
from ctrlops.services.backup_service import create_backup, list_backups, restore_backup


def test_backup_create_and_restore(tmp_path, monkeypatch):
    monkeypatch.setenv("CTRLOPS_DATABASE_URL", f"sqlite:///{tmp_path / 'ctrlops.db'}")
    source = tmp_path / "data"
    source.mkdir()
    (source / "file.txt").write_text("hello", encoding="utf-8")
    settings = Settings(backup_dir=tmp_path / "backups")

    backup = create_backup(source, settings=settings)

    archive = Path(backup["file"])
    assert archive.exists()
    assert archive.suffixes[-2:] == [".tar", ".gz"]
    assert list_backups(settings=settings)

    restore_target = tmp_path / "restore"
    restore_backup(archive, restore_target)
    assert (restore_target / "data" / "file.txt").read_text(encoding="utf-8") == "hello"

from ctrlops.config import load_settings


def test_config_loading(tmp_path, monkeypatch):
    monkeypatch.delenv("CTRLOPS_BACKUP_DIR", raising=False)
    monkeypatch.delenv("CTRLOPS_DATABASE_URL", raising=False)
    config = tmp_path / "ctrlops.yml"
    config.write_text(
        """
app:
  backup_dir: "./archives"
  database_url: "sqlite:///local.db"
deployments:
  demo:
    path: "."
    commands:
      - "git status"
""",
        encoding="utf-8",
    )

    settings = load_settings(config)

    assert str(settings.backup_dir) == "archives"
    assert settings.database_url == "sqlite:///local.db"
    assert "demo" in settings.deployments

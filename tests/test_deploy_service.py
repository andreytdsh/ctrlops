import yaml

from ctrlops.services.deploy_service import create_deployment


def test_create_deployment_writes_config(tmp_path):
    config = tmp_path / "ctrlops.yml"
    config.write_text(
        """
app:
  backup_dir: "./backups"
  database_url: "sqlite:///ctrlops.db"
""",
        encoding="utf-8",
    )

    result = create_deployment(
        "myapp",
        "/var/www/myapp",
        "git pull\ndocker compose up -d --build",
        config_path=str(config),
    )

    data = yaml.safe_load(config.read_text(encoding="utf-8"))
    assert result["name"] == "myapp"
    assert data["deployments"]["myapp"]["path"] == "/var/www/myapp"
    assert data["deployments"]["myapp"]["commands"] == [
        "git pull",
        "docker compose up -d --build",
    ]

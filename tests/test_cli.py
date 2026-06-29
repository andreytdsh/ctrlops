import json

from typer.testing import CliRunner

from ctrlops.cli import app

runner = CliRunner()


def test_cli_deployment_add_and_list(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(
        app,
        [
            "deployment",
            "add",
            "--name",
            "myapp",
            "--path",
            ".",
            "-c",
            "git status",
        ],
    )
    assert result.exit_code == 0

    list_result = runner.invoke(app, ["deployment", "list", "--json"])
    assert list_result.exit_code == 0
    deployments = json.loads(list_result.output)
    assert deployments[0]["name"] == "myapp"

    check_result = runner.invoke(app, ["deployment", "check", "myapp", "--json"])
    assert check_result.exit_code == 0
    deployment = json.loads(check_result.output)
    assert deployment["commands"] == ["git status"]


def test_cli_status_json_without_domain():
    result = runner.invoke(app, ["status", "--json"])

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert "health" in payload
    assert "latest_backup" in payload
    assert payload["ssl"] is None

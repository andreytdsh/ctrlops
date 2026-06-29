# CtrlOps

![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Web_UI-green)
![CLI](https://img.shields.io/badge/CLI-Typer-orange)
![License](https://img.shields.io/badge/License-MIT-black)

CtrlOps is a lightweight DevOps toolkit for Linux servers, VPS infrastructure and self-hosted projects.

It provides both a CLI and a Web UI for checking DNS records, monitoring SSL certificates, inspecting server health, creating backups, analyzing logs and running simple deployments.

## Features

- DNS inspection for A, AAAA, MX, NS, TXT and CNAME records.
- SSL certificate checks with expiry status.
- Local server health metrics.
- Host inventory scanning.
- `.tar.gz` backup creation, listing and restore.
- Nginx/Apache access log analysis.
- Configured deployment runner using `ctrlops.yml`.
- FastAPI, Jinja2 and HTMX Web UI.
- SQLite persistence for backups and deployment logs.

## Screenshots

Screenshots can be added under `docs/screenshots.md` after running the Web UI locally.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

## CLI Examples

```bash
ctrlops dns example.com
ctrlops ssl example.com --json
ctrlops health
ctrlops status --domain example.com
ctrlops inventory --output inventory.json
ctrlops logs /var/log/nginx/access.log
ctrlops backup create --path ./data
ctrlops backup list
ctrlops deployment add --name myapp --path /var/www/myapp -c "git pull" -c "docker compose up -d --build"
ctrlops deployment list
ctrlops deployment check myapp
ctrlops backup restore --file ./backups/data-20260629-120000.tar.gz --target ./restore
ctrlops deploy --name demo
```

## Web UI

Start the dashboard:

```bash
ctrlops web
```

Open `http://localhost:8000`.

## Docker

```bash
docker compose up --build
```

The Web UI is exposed at `http://localhost:8000`.

## Configuration

CtrlOps reads `.env` and `ctrlops.yml`. See `.env.example` and `ctrlops.yml`.

```yaml
app:
  backup_dir: "./backups"
  database_url: "sqlite:///ctrlops.db"

deployments:
  demo:
    path: "."
    commands:
      - "git status"
```

Deployments can be configured from the CLI or Web UI, then executed with `ctrlops deploy --name NAME`.

## Development

```bash
pytest
ruff check .
```

## Roadmap

- Telegram alerts.
- Email alerts.
- Cron scheduling.
- Remote SSH checks.
- Prometheus export.
- Multi-server inventory.
- Role-based users.
- Auth for Web UI.

## License

MIT

# Configuration

CtrlOps reads environment variables from `.env` and local configuration from `ctrlops.yml`.

## Environment

Use `.env.example` as a template:

```env
CTRLOPS_BACKUP_DIR=./backups
CTRLOPS_DATABASE_URL=sqlite:///ctrlops.db
CTRLOPS_HOST=127.0.0.1
CTRLOPS_PORT=8000
```

Do not commit real `.env` files.

## `ctrlops.yml`

```yaml
app:
  backup_dir: "./backups"
  database_url: "sqlite:///ctrlops.db"
  host: "127.0.0.1"
  port: 8000

deployments:
  demo:
    path: "."
    commands:
      - "git status"
```

Deployment commands are the only shell commands CtrlOps executes. They must be declared in configuration.

Deployments can be added manually in this file, through the Web UI Deployments page, or from the CLI:

```bash
ctrlops deployment add --name myapp --path /var/www/myapp -c "git pull" -c "docker compose up -d --build"
ctrlops deploy --name myapp
```

The Web UI writes the deployment name, working directory and one command per line back to `ctrlops.yml`.

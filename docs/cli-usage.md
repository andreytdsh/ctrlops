# CLI Usage

Main command:

```bash
ctrlops
```

## DNS

```bash
ctrlops dns example.com
ctrlops dns example.com --json
```

## SSL

```bash
ctrlops ssl example.com
ctrlops ssl example.com --json
```

## Health

```bash
ctrlops health
ctrlops health --json
```

## Status

```bash
ctrlops status
ctrlops status --domain example.com
ctrlops status --domain example.com --json
```

`status` prints a compact operational dashboard: health metrics, the latest backup, configured deployments and SSL status when a domain is provided.

## Inventory

```bash
ctrlops inventory
ctrlops inventory --json
ctrlops inventory --output inventory.json
```

## Logs

```bash
ctrlops logs /var/log/nginx/access.log
ctrlops logs ./access.log --json
```

The path is resolved on the machine where CtrlOps is running. Common paths:

- Nginx: `/var/log/nginx/access.log`
- Apache on Debian/Ubuntu: `/var/log/apache2/access.log`
- Apache on RHEL/CentOS: `/var/log/httpd/access_log`
- Project-local logs: `./logs/access.log`

## Backups

```bash
ctrlops backup create --path ./data
ctrlops backup list
ctrlops backup list --json
ctrlops backup restore --file ./backups/data-20260629-120000.tar.gz --target ./restore
```

## Deployments

```bash
ctrlops deployment add --name myapp --path /var/www/myapp -c "git pull" -c "docker compose up -d --build"
ctrlops deployment list
ctrlops deployment show myapp
ctrlops deployment check myapp
ctrlops deploy --name demo
```

Deployments only run when explicitly configured in `ctrlops.yml`.
You can edit `ctrlops.yml` manually, add a deployment from the Web UI Deployments page, or add one from the CLI with `ctrlops deployment add`.
Use `ctrlops deployment check NAME` before running a deployment to inspect its working directory and commands without executing anything.

## Web UI

```bash
ctrlops web
ctrlops web --host 0.0.0.0 --port 8000
```

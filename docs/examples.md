# Examples

## Check SSL for a Domain

```bash
ctrlops ssl example.com
ctrlops ssl example.com --json
```

Use this before certificate renewals or when validating DNS changes.

## Inspect DNS

```bash
ctrlops dns example.com
```

The command returns common DNS records and TTL values where available.

## Create a Backup

```bash
ctrlops backup create --path ./data
ctrlops backup list
```

Archives are written to the configured backup directory.

## Analyze Nginx Logs

```bash
ctrlops logs /var/log/nginx/access.log
```

The analyzer reports request totals, top IPs, top URLs and HTTP status distribution.
The path must exist on the machine running CtrlOps. In Docker, mount the log directory into the container first.

## Check Operational Status

```bash
ctrlops status --domain example.com
```

This prints local health, latest backup, configured deployments and SSL status for the domain.

## Run a Deployment

Configure `ctrlops.yml`:

```yaml
deployments:
  myapp:
    path: "/var/www/myapp"
    commands:
      - "git pull"
      - "docker compose up -d --build"
```

Then run:

```bash
ctrlops deploy --name myapp
```

The same deployment can also be created from the Web UI on the Deployments page by entering `myapp`, `/var/www/myapp` and the commands one per line.

Or create it from the CLI:

```bash
ctrlops deployment add --name myapp --path /var/www/myapp -c "git pull" -c "docker compose up -d --build"
ctrlops deployment check myapp
ctrlops deploy --name myapp
```

# Web UI

Start the Web UI with:

```bash
ctrlops web
```

Default address: `http://localhost:8000`.

## Pages

- Dashboard: health metrics, recent backups and configured deployments.
- DNS Inspector: domain input, DNS record table and copyable JSON result.
- SSL Checker: certificate summary, status badge and days remaining.
- Server Health: CPU, RAM, disk, process count, OS and Docker availability.
- Backups: create backups and inspect existing archives.
- Logs Analyzer: parse access logs and show request totals, top IPs and URLs. The path is a server-side path on the machine running CtrlOps, such as `/var/log/nginx/access.log`.
- Inventory: host overview and JSON export.
- Deployments: inspect command lists, edit deployments in `ctrlops.yml`, run configured deployments and inspect logs.
- Documentation link: opens the CtrlOps GitHub Wiki.

# Modules

## `ctrlops.config`

Loads `.env` values and `ctrlops.yml`, including backup paths, database URL and deployments.

## `ctrlops.database`

Initializes SQLite tables for command history, backup records, deployment logs, saved domains and SSL history.

## `ctrlops.services.dns_service`

Validates domains and resolves A, AAAA, MX, NS, TXT and CNAME records using dnspython.

## `ctrlops.services.ssl_service`

Connects to port 443, reads the peer certificate and calculates OK, WARNING or EXPIRED status.

## `ctrlops.services.health_service`

Collects local OS, kernel, uptime, CPU, memory, disk, load, process count and Docker availability.

## `ctrlops.services.inventory_service`

Scans hostname, OS, kernel, CPU, RAM, disks, interfaces, packages, containers and open ports.

## `ctrlops.services.backup_service`

Creates `.tar.gz` archives, lists backup files and restores archives with path traversal protection.

## `ctrlops.services.log_service`

Parses common Nginx and Apache access logs and aggregates IPs, URLs, statuses and requests per minute.

## `ctrlops.services.deploy_service`

Runs explicitly configured deployment commands from `ctrlops.yml`, stops on failure and stores logs.

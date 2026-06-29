"""CtrlOps command line interface."""

from __future__ import annotations

import json
from contextlib import suppress
from pathlib import Path
from typing import Annotated, Any

import typer
import uvicorn
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ctrlops.config import load_settings
from ctrlops.database import record_command
from ctrlops.services.backup_service import create_backup, list_backups, restore_backup
from ctrlops.services.deploy_service import (
    create_deployment,
    get_deployment_config,
    list_deployment_configs,
    list_deployments,
    run_deployment,
)
from ctrlops.services.dns_service import inspect_dns
from ctrlops.services.health_service import get_health
from ctrlops.services.inventory_service import scan_inventory
from ctrlops.services.log_service import analyze_log
from ctrlops.services.ssl_service import check_ssl
from ctrlops.utils.formatting import format_bytes

DOCS_URL = "https://github.com/andreytdsh/ctrlops#readme"
HELP_EPILOG = f"Documentation: {DOCS_URL}"

app = typer.Typer(
    help=(
        "CtrlOps is a DevOps toolkit for small VPS servers and self-hosted projects.\n\n"
        "Typical workflow:\n"
        "  1. ctrlops status --domain example.com\n"
        "  2. ctrlops dns example.com\n"
        "  3. ctrlops ssl example.com\n"
        "  4. ctrlops deployment check demo\n"
        "  5. ctrlops deploy --name demo\n\n"
        "All deployment commands must be explicitly configured in ctrlops.yml."
    ),
    epilog=HELP_EPILOG,
    no_args_is_help=True,
    rich_markup_mode="rich",
)
backup_app = typer.Typer(
    help=(
        "Create, list and restore local .tar.gz backups.\n\n"
        "Backups are stored in the configured backup_dir from ctrlops.yml or "
        "CTRLOPS_BACKUP_DIR."
    ),
    epilog=HELP_EPILOG,
    no_args_is_help=True,
)
deployment_app = typer.Typer(
    help=(
        "Configure deployments in ctrlops.yml.\n\n"
        "Use 'deployment check NAME' to inspect commands before running "
        "'deploy --name NAME'."
    ),
    epilog=HELP_EPILOG,
    no_args_is_help=True,
)
app.add_typer(backup_app, name="backup")
app.add_typer(deployment_app, name="deployment")
console = Console()


def _json(data: Any) -> None:
    console.print_json(json.dumps(data, default=str))


def _error(message: str) -> None:
    console.print(f"[bold red]Error:[/bold red] {message}")


def _record(command: str, payload: dict[str, Any] | None = None) -> None:
    with suppress(Exception):
        record_command(command, payload)


def _print_health_summary(health_data: dict[str, Any]) -> None:
    table = Table(title="Health")
    table.add_column("Metric", style="cyan")
    table.add_column("Value")
    table.add_row("OS", health_data["os"])
    table.add_row("CPU", f"{health_data['cpu_usage_percent']}%")
    table.add_row("RAM", f"{health_data['ram']['percent']}%")
    table.add_row("Disk", f"{health_data['disk']['percent']}%")
    table.add_row("Processes", str(health_data["process_count"]))
    table.add_row("Docker", health_data["docker"]["version"] or "not available")
    console.print(table)


@app.command()
def dns(
    domain: str,
    json_output: Annotated[bool, typer.Option("--json", help="Print JSON output.")] = False,
) -> None:
    """Inspect A, AAAA, MX, NS, TXT and CNAME records for a domain."""

    try:
        result = inspect_dns(domain)
    except Exception as exc:
        _error(str(exc))
        raise typer.Exit(1) from exc
    if json_output:
        _json(result)
        _record("dns", {"domain": domain})
        return

    table = Table(title=f"DNS records for {result['domain']}")
    table.add_column("Type", style="cyan")
    table.add_column("Value")
    table.add_column("TTL", justify="right")
    for record_type, records in result["records"].items():
        if not records:
            table.add_row(record_type, "-", "-")
        for record in records:
            table.add_row(record_type, record["value"], str(record["ttl"]))
    console.print(table)
    if result["errors"]:
        console.print("[yellow]Partial errors:[/yellow] " + "; ".join(result["errors"]))
    _record("dns", {"domain": domain})


@app.command(name="ssl")
def ssl_command(
    domain: str,
    json_output: Annotated[bool, typer.Option("--json", help="Print JSON output.")] = False,
) -> None:
    """Check certificate issuer, dates, SANs and expiry status for a domain."""

    try:
        result = check_ssl(domain)
    except Exception as exc:
        _error(str(exc))
        raise typer.Exit(1) from exc
    if json_output:
        _json(result)
        _record("ssl", {"domain": domain})
        return

    table = Table(title=f"SSL certificate for {result['domain']}")
    table.add_column("Field", style="cyan")
    table.add_column("Value")
    for key in ("status", "issuer", "common_name", "valid_from", "valid_until", "days_remaining"):
        table.add_row(key.replace("_", " ").title(), str(result[key]))
    table.add_row("SANs", ", ".join(result["sans"][:8]) or "-")
    console.print(table)
    _record("ssl", {"domain": domain})


@app.command()
def health(
    json_output: Annotated[bool, typer.Option("--json", help="Print JSON output.")] = False,
) -> None:
    """Show OS, uptime, CPU, RAM, disk, load, processes and Docker status."""

    result = get_health()
    if json_output:
        _json(result)
        _record("health")
        return
    table = Table(title="Server health")
    table.add_column("Metric", style="cyan")
    table.add_column("Value")
    table.add_row("OS", result["os"])
    table.add_row("Kernel", result["kernel"])
    table.add_row("Uptime", f"{result['uptime_seconds']} seconds")
    table.add_row("CPU", f"{result['cpu_usage_percent']}%")
    table.add_row("RAM", f"{result['ram']['percent']}% ({format_bytes(result['ram']['used'])})")
    table.add_row("Disk", f"{result['disk']['percent']}% ({format_bytes(result['disk']['used'])})")
    table.add_row("Load average", ", ".join(f"{item:.2f}" for item in result["load_average"]))
    table.add_row("Processes", str(result["process_count"]))
    table.add_row("Docker", result["docker"]["version"] or "not available")
    console.print(table)
    _record("health")


@app.command()
def inventory(
    json_output: Annotated[bool, typer.Option("--json", help="Print JSON output.")] = False,
    output: Annotated[
        Path | None,
        typer.Option("--output", help="Write JSON inventory to a file."),
    ] = None,
) -> None:
    """Scan hostname, OS, disks, network interfaces, packages, ports and Docker."""

    result = scan_inventory()
    if output:
        output.write_text(json.dumps(result, indent=2, default=str), encoding="utf-8")
        console.print(f"Inventory written to {output}")
    if json_output:
        _json(result)
        _record("inventory", {"output": str(output) if output else None})
        return
    table = Table(title="Inventory")
    table.add_column("Item", style="cyan")
    table.add_column("Value")
    table.add_row("Hostname", result["hostname"])
    table.add_row("OS", result["os"])
    table.add_row("Kernel", result["kernel"])
    table.add_row("CPU", result["cpu"])
    table.add_row("RAM", format_bytes(result["ram_bytes"]))
    table.add_row("Disks", str(len(result["disks"])))
    table.add_row("Network interfaces", str(len(result["network_interfaces"])))
    table.add_row("Open ports", ", ".join(map(str, result["open_ports"])) or "-")
    table.add_row("Docker containers", str(len(result["docker_containers"])))
    console.print(table)
    _record("inventory", {"output": str(output) if output else None})


@app.command()
def logs(
    path: Path,
    json_output: Annotated[bool, typer.Option("--json", help="Print JSON output.")] = False,
) -> None:
    """Analyze a server-side Nginx/Apache access log file."""

    try:
        result = analyze_log(path)
    except Exception as exc:
        _error(str(exc))
        console.print(
            "Use a path on the machine where CtrlOps is running, for example "
            "/var/log/nginx/access.log, /var/log/apache2/access.log, "
            "/var/log/httpd/access_log or ./logs/access.log."
        )
        raise typer.Exit(1) from exc
    if json_output:
        _json(result)
        _record("logs", {"path": str(path)})
        return
    summary = Table(title=f"Log summary: {path}")
    summary.add_column("Metric", style="cyan")
    summary.add_column("Value")
    summary.add_row("Total requests", str(result["total_requests"]))
    summary.add_row("404 count", str(result["count_404"]))
    summary.add_row("500 count", str(result["count_500"]))
    console.print(summary)
    top = Table(title="Top IPs and URLs")
    top.add_column("Type", style="cyan")
    top.add_column("Value")
    top.add_column("Count", justify="right")
    for value, count in result["top_ips"][:5]:
        top.add_row("IP", value, str(count))
    for value, count in result["top_urls"][:5]:
        top.add_row("URL", value, str(count))
    console.print(top)
    _record("logs", {"path": str(path)})


@app.command()
def status(
    domain: Annotated[
        str | None,
        typer.Option("--domain", help="Optional domain for SSL status."),
    ] = None,
    json_output: Annotated[bool, typer.Option("--json", help="Print JSON output.")] = False,
) -> None:
    """Print health, latest backup, deployments and optional SSL status."""

    health_data = get_health()
    backups = list_backups()
    latest_backup = backups[0] if backups else None
    ssl_result = None
    ssl_error = None
    if domain:
        try:
            ssl_result = check_ssl(domain)
        except Exception as exc:
            ssl_error = str(exc)

    result = {
        "health": health_data,
        "latest_backup": latest_backup,
        "ssl": ssl_result,
        "ssl_error": ssl_error,
        "deployments": list_deployments(),
    }
    if json_output:
        _json(result)
        _record("status", {"domain": domain})
        return

    console.print(Panel.fit("CtrlOps Status", style="bold cyan"))
    _print_health_summary(health_data)

    backup_table = Table(title="Latest backup")
    backup_table.add_column("Field", style="cyan")
    backup_table.add_column("Value")
    if latest_backup:
        backup_table.add_row("Name", latest_backup["name"])
        backup_table.add_row("File", latest_backup["file"])
        backup_table.add_row("Size", format_bytes(latest_backup["size_bytes"]))
        backup_table.add_row("Created", latest_backup["created_at"])
    else:
        backup_table.add_row("Status", "No backups found")
    console.print(backup_table)

    ssl_table = Table(title="SSL")
    ssl_table.add_column("Field", style="cyan")
    ssl_table.add_column("Value")
    if ssl_result:
        ssl_table.add_row("Domain", ssl_result["domain"])
        ssl_table.add_row("Status", ssl_result["status"])
        ssl_table.add_row("Days remaining", str(ssl_result["days_remaining"]))
        ssl_table.add_row("Issuer", ssl_result["issuer"])
    elif ssl_error:
        ssl_table.add_row("Error", ssl_error)
    else:
        ssl_table.add_row("Status", "Skipped. Use --domain example.com to include SSL.")
    console.print(ssl_table)

    deployments = result["deployments"]
    console.print(
        "[cyan]Deployments:[/cyan] "
        + (", ".join(deployments) if deployments else "none configured")
    )
    _record("status", {"domain": domain})


@backup_app.command("create")
def backup_create(
    path: Annotated[Path, typer.Option("--path", help="File or directory to archive.")],
) -> None:
    """Create a .tar.gz backup archive from a file or directory."""

    try:
        result = create_backup(path)
    except Exception as exc:
        _error(str(exc))
        raise typer.Exit(1) from exc
    console.print(
        f"Created backup: [green]{result['file']}[/green] "
        f"({format_bytes(result['size_bytes'])})"
    )


@backup_app.command("list")
def backup_list(
    json_output: Annotated[bool, typer.Option("--json", help="Print JSON output.")] = False,
) -> None:
    """List backup archives from the configured backup directory."""

    backups = list_backups()
    if json_output:
        _json(backups)
        return
    table = Table(title="Backups")
    table.add_column("File", style="cyan")
    table.add_column("Size", justify="right")
    table.add_column("Created")
    for item in backups:
        table.add_row(item["name"], format_bytes(item["size_bytes"]), item["created_at"])
    console.print(table)


@backup_app.command("restore")
def backup_restore(
    file: Annotated[Path, typer.Option("--file", help="Backup archive to restore.")],
    target: Annotated[Path, typer.Option("--target", help="Target directory.")],
) -> None:
    """Restore a backup archive into a target directory."""

    try:
        result = restore_backup(file, target)
    except Exception as exc:
        _error(str(exc))
        raise typer.Exit(1) from exc
    console.print(f"Restored [green]{result['file']}[/green] to {result['target']}")


@deployment_app.command("add")
def deployment_add(
    name: Annotated[str, typer.Option("--name", help="Deployment name.")],
    path: Annotated[Path, typer.Option("--path", help="Working directory.")],
    commands: Annotated[
        list[str] | None,
        typer.Option("--command", "-c", help="Command to run. Can be used multiple times."),
    ] = None,
) -> None:
    """Add or update a deployment in ctrlops.yml from CLI options."""

    if not commands:
        _error("At least one --command/-c value is required")
        raise typer.Exit(1)
    try:
        result = create_deployment(name, str(path), "\n".join(commands))
    except Exception as exc:
        _error(str(exc))
        raise typer.Exit(1) from exc
    console.print(f"Saved deployment [green]{result['name']}[/green] to ctrlops.yml")
    console.print("Run it with: " f"ctrlops deploy --name {result['name']}")


@deployment_app.command("list")
def deployment_list(
    json_output: Annotated[bool, typer.Option("--json", help="Print JSON output.")] = False,
) -> None:
    """List configured deployments with paths and command lists."""

    deployments = list_deployment_configs()
    if json_output:
        _json(deployments)
        return
    table = Table(title="Configured deployments")
    table.add_column("Name", style="cyan")
    table.add_column("Path")
    table.add_column("Commands")
    for deployment in deployments:
        table.add_row(
            deployment["name"],
            deployment["path"],
            "\n".join(deployment["commands"]),
        )
    console.print(table)


def _print_deployment_config(deployment: dict[str, Any]) -> None:
    table = Table(title=f"Deployment: {deployment['name']}")
    table.add_column("Field", style="cyan")
    table.add_column("Value")
    table.add_row("Path", deployment["path"])
    table.add_row("Commands", "\n".join(deployment["commands"]))
    console.print(table)


@deployment_app.command("show")
def deployment_show(
    name: Annotated[str, typer.Argument(help="Deployment name.")],
    json_output: Annotated[bool, typer.Option("--json", help="Print JSON output.")] = False,
) -> None:
    """Show one deployment config without executing commands."""

    try:
        deployment = get_deployment_config(name)
    except Exception as exc:
        _error(str(exc))
        raise typer.Exit(1) from exc
    if json_output:
        _json(deployment)
        return
    _print_deployment_config(deployment)


@deployment_app.command("check")
def deployment_check(
    name: Annotated[str, typer.Argument(help="Deployment name.")],
    json_output: Annotated[bool, typer.Option("--json", help="Print JSON output.")] = False,
) -> None:
    """Check what a deployment would run without executing it."""

    try:
        deployment = get_deployment_config(name)
    except Exception as exc:
        _error(str(exc))
        raise typer.Exit(1) from exc
    if json_output:
        _json(deployment)
        return
    _print_deployment_config(deployment)
    console.print(f"Run it with: ctrlops deploy --name {deployment['name']}")


@app.command()
def deploy(
    name: Annotated[str, typer.Option("--name", help="Configured deployment name.")],
) -> None:
    """Run a configured deployment from ctrlops.yml."""

    try:
        result = run_deployment(name)
    except Exception as exc:
        _error(str(exc))
        available = list_deployments()
        if available:
            console.print("Configured deployments: " + ", ".join(available))
        raise typer.Exit(1) from exc
    console.print(f"Deployment {result['name']}: {result['status']}")
    console.print(result["output"])
    _record("deploy", {"name": name, "status": result["status"]})
    if result["status"] != "success":
        raise typer.Exit(1)


@app.command()
def web(
    host: Annotated[str | None, typer.Option("--host", help="Bind host.")] = None,
    port: Annotated[int | None, typer.Option("--port", help="Bind port.")] = None,
) -> None:
    """Start the FastAPI/Jinja2 Web UI."""

    settings = load_settings()
    uvicorn.run(
        "ctrlops.web.app:create_app",
        host=host or settings.host,
        port=port or settings.port,
        factory=True,
    )


if __name__ == "__main__":
    app()

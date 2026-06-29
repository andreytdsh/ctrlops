"""Web UI routes."""

from __future__ import annotations

from pathlib import Path
from urllib.parse import parse_qs

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from ctrlops.config import load_settings
from ctrlops.services.backup_service import create_backup, list_backups
from ctrlops.services.deploy_service import (
    create_deployment,
    get_deployment_config,
    list_deployment_configs,
    list_deployments,
    recent_deployment_logs,
    run_deployment,
)
from ctrlops.services.dns_service import inspect_dns
from ctrlops.services.health_service import get_health
from ctrlops.services.inventory_service import scan_inventory
from ctrlops.services.log_service import analyze_log
from ctrlops.services.ssl_service import check_ssl

router = APIRouter()


def template_dir() -> Path:
    """Return template directory."""

    return Path(__file__).parent / "templates"


def static_dir() -> Path:
    """Return static directory."""

    return Path(__file__).parent / "static"


templates = Jinja2Templates(directory=str(template_dir()))


@router.get("/", response_class=HTMLResponse)
def dashboard(request: Request) -> HTMLResponse:
    health = get_health()
    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {"health": health, "backups": list_backups()[:5], "deployments": list_deployments()},
    )


@router.get("/dns", response_class=HTMLResponse)
def dns_page(request: Request, domain: str | None = None) -> HTMLResponse:
    result = error = None
    if domain:
        try:
            result = inspect_dns(domain)
        except Exception as exc:
            error = str(exc)
    return templates.TemplateResponse(
        request,
        "dns.html",
        {"result": result, "domain": domain or "", "error": error},
    )


@router.get("/ssl", response_class=HTMLResponse)
def ssl_page(request: Request, domain: str | None = None) -> HTMLResponse:
    result = error = None
    if domain:
        try:
            result = check_ssl(domain)
        except Exception as exc:
            error = str(exc)
    return templates.TemplateResponse(
        request,
        "ssl.html",
        {"result": result, "domain": domain or "", "error": error},
    )


@router.get("/health", response_class=HTMLResponse)
def health_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "health.html", {"health": get_health()})


@router.get("/inventory", response_class=HTMLResponse)
def inventory_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "inventory.html", {"inventory": scan_inventory()})


@router.get("/inventory.json")
def inventory_json() -> JSONResponse:
    return JSONResponse(scan_inventory())


@router.get("/backups", response_class=HTMLResponse)
def backups_page(request: Request, path: str | None = None) -> HTMLResponse:
    message = error = None
    if path:
        try:
            result = create_backup(path)
            message = f"Created backup {result['file']}"
        except Exception as exc:
            error = str(exc)
    return templates.TemplateResponse(
        request,
        "backups.html",
        {"backups": list_backups(), "path": path or "", "message": message, "error": error},
    )


@router.get("/logs", response_class=HTMLResponse)
def logs_page(request: Request, path: str | None = None) -> HTMLResponse:
    result = error = None
    if path:
        try:
            result = analyze_log(path)
        except Exception as exc:
            error = str(exc)
    return templates.TemplateResponse(
        request,
        "logs.html",
        {"result": result, "path": path or "", "error": error},
    )


@router.get("/deploy", response_class=HTMLResponse)
def deploy_page(
    request: Request,
    name: str | None = None,
    selected: str | None = None,
    edit: str | None = None,
) -> HTMLResponse:
    result = error = details = None
    form = {"name": "", "path": "", "commands": ""}
    if name:
        try:
            result = run_deployment(name)
        except Exception as exc:
            error = str(exc)
    if selected:
        try:
            details = get_deployment_config(selected)
        except Exception as exc:
            error = str(exc)
    if edit:
        try:
            editable = get_deployment_config(edit)
            details = editable
            form = {
                "name": editable["name"],
                "path": editable["path"],
                "commands": "\n".join(editable["commands"]),
            }
        except Exception as exc:
            error = str(exc)
    return templates.TemplateResponse(
        request,
        "deploy.html",
        {
            "deployments": list_deployment_configs(load_settings()),
            "logs": recent_deployment_logs(),
            "result": result,
            "details": details,
            "error": error,
            "message": None,
            "form": form,
        },
    )


@router.post("/deployments", response_class=HTMLResponse)
async def create_deployment_page(request: Request) -> HTMLResponse:
    body = (await request.body()).decode("utf-8")
    form_data = parse_qs(body)
    form = {
        "name": form_data.get("name", [""])[0],
        "path": form_data.get("path", [""])[0],
        "commands": form_data.get("commands", [""])[0],
    }
    message = error = None
    try:
        deployment = create_deployment(form["name"], form["path"], form["commands"])
        message = f"Deployment '{deployment['name']}' saved to ctrlops.yml"
        form = {"name": "", "path": "", "commands": ""}
    except Exception as exc:
        error = str(exc)

    return templates.TemplateResponse(
        request,
        "deploy.html",
        {
            "deployments": list_deployment_configs(load_settings()),
            "logs": recent_deployment_logs(),
            "result": None,
            "details": None,
            "error": error,
            "message": message,
            "form": form,
        },
    )

"""FastAPI application factory."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from ctrlops.web.routes import router, static_dir


def create_app() -> FastAPI:
    """Create the CtrlOps FastAPI app."""

    app = FastAPI(title="CtrlOps", version="0.1.0")
    app.mount("/static", StaticFiles(directory=static_dir()), name="static")
    app.include_router(router)
    return app


app = create_app()

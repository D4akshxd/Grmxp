from __future__ import annotations

import logging
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import get_settings
from .core.database import engine
from .models import Base
from .routers import analysis, auth


LOGGER = logging.getLogger("gem_analyzer")
settings = get_settings()


def create_application() -> FastAPI:
    application = FastAPI(title=settings.project_name, version="1.0.0")

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.include_router(auth.router, prefix=settings.api_v1_prefix)
    application.include_router(analysis.router, prefix=settings.api_v1_prefix)

    @application.get("/health", tags=["health"])  # type: ignore[misc]
    def healthcheck() -> dict[str, Any]:
        return {"status": "ok"}

    return application


app = create_application()


@app.on_event("startup")
def on_startup() -> None:
    LOGGER.info("Creating database tables if not present")
    Base.metadata.create_all(bind=engine)

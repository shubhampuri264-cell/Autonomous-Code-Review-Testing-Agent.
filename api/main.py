"""FastAPI application factory."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import health, runs, repositories, webhooks
from core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup: initialize DB client, Docker client, etc.
    yield
    # Shutdown: cleanup resources


def create_app() -> FastAPI:
    """Build and configure the FastAPI application."""
    app = FastAPI(
        title=settings.app_name,
        version="1.0.0",
        lifespan=lifespan,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Tighten in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routers
    app.include_router(health.router, prefix="/api", tags=["health"])
    app.include_router(runs.router, prefix="/api/runs", tags=["runs"])
    app.include_router(repositories.router, prefix="/api/repositories", tags=["repositories"])
    app.include_router(webhooks.router, prefix="/api/webhooks", tags=["webhooks"])

    return app


app = create_app()

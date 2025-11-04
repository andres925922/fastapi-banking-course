from contextlib import asynccontextmanager
from fastapi import FastAPI

from core.db import init_db
from core.settings import settings
from api.main import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """ Lifespan context manager for FastAPI application. """
    await init_db()
    yield

def create_app() -> FastAPI:
    """ Create and configure the FastAPI application. """
    app = FastAPI(
        lifespan=lifespan,
        title=settings.PROJECT_NAME,
        description=settings.PROJECT_DESCRIPTION,
        docs_url=f"{settings.API_V1_STR}/docs",
        redoc_url=f"{settings.API_V1_STR}/redoc",
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
    )

    app.include_router(api_router, prefix=settings.API_V1_STR)

    return app

app = create_app()

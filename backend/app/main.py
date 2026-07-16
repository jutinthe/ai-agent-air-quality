from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import get_settings
from app.schemas.extraction import PaperExtraction


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    settings.create_storage_directories()
    yield


app = FastAPI(
    title="Air Quality–Health Research Agent",
    description=(
        "Extracts structured scientific information from "
        "air quality and health research papers."
    ),
    version="0.2.0",
    lifespan=lifespan,
)

app.include_router(api_router)


@app.get("/")
async def root() -> dict[str, str]:
    return {
        "message": "Air Quality–Health Research Agent API",
        "documentation": "/docs",
    }


@app.get("/health", tags=["System"])
async def health_check() -> dict[str, str]:
    return {
        "status": "healthy",
        "service": "air-health-research-agent",
        "version": "0.2.0",
    }


@app.get("/schema/extraction", tags=["Schema"])
async def extraction_schema() -> dict:
    return PaperExtraction.model_json_schema()

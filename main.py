import sys
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.responses import UJSONResponse
from loguru import logger

from src.core.settings import settings
from src.api.api_v1.api import api_router

logger.remove()
logger.add(sys.stderr, level="DEBUG" if settings.run.DEBUG else "INFO")

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    app.include_router(api_router)
    logger.info(f"Start server")
    yield
    logger.warning(f"Stop server")

app = FastAPI(
    debug=settings.run.DEBUG,
    title=settings.api.SERVICE_NAME,
    version=settings.api.VERSION,
    default_response_class=UJSONResponse,
    lifespan=lifespan
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.run.HOST,
        port=settings.run.PORT,
        reload=settings.run.DEBUG,
    )
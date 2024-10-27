from fastapi import APIRouter

from .endpoints.users import router as clients_router
from .endpoints.blogs import router as blogs_router, statistics_router
from src.core.settings import settings



api_router = APIRouter(prefix="/api/{}".format(settings.api.VERSION), tags=["api"])

api_router.include_router(clients_router)
api_router.include_router(blogs_router)
api_router.include_router(statistics_router)
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.core import settings

engine = create_async_engine(
    settings.db.as_dns(),
    echo=settings.run.DEBUG
)

async_session_factory = async_sessionmaker(engine)
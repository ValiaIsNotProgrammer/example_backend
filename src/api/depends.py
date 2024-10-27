from typing import AsyncGenerator, Callable

from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from loguru import logger
from sqlalchemy import exc
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.exceptions import HTTPException

from src.core.secure import encrypt_token
from src.crud.database import async_session_factory
from src.crud.models.base import BaseORMModel
from src.crud.models.user import UserModel
from src.crud.repo.base import BaseRepository

oauth2_scheme = HTTPBearer(auto_error=False)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except exc.SQLAlchemyError as error:
            logger.error(error)
            await session.rollback()
            raise


def get_repo(
    model: type[BaseORMModel],
    repo_cls: type[BaseRepository] = BaseRepository
) -> Callable[[AsyncSession], BaseRepository[BaseORMModel]]:
    def func(session: AsyncSession = Depends(get_db_session)):
        logger.debug(f"Get {model.__tablename__} repo")
        return repo_cls(model, session)
    return func


async def get_current_user(token: HTTPAuthorizationCredentials = Depends(oauth2_scheme), repo: BaseRepository[UserModel] = Depends(get_repo(UserModel))) -> UserModel:
    logger.debug(f"Get current user with token {token}")
    if not token:
        raise HTTPException(429, "Client token missing")
    existing_client = await repo.get_by_where_one_or_none(UserModel.token == encrypt_token(token.credentials))
    if existing_client:
        logger.debug(f"User with token {token} success was found")
        return existing_client
    logger.debug(f"User with token {token} not found")
    raise HTTPException(429, "Invalid token or client not authenticated")
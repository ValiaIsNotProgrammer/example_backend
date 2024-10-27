from typing import Generic, TypeVar
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from loguru import logger
from sqlalchemy import select, exc, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.elements import ClauseElement

from ..models.base import BaseORMModel
from ...exceptions.crud import RepoNotFoundException, RepoConflictException

BaseModel = TypeVar('BaseModel', bound=BaseORMModel)

class BaseRepository(Generic[BaseModel]):
    def __init__(self, model: type[BaseModel], session: AsyncSession):
        self.model = model
        self.session = session

    async def get_multi_paginated(self, offset: int = 0, limit: int = 0,
                                  whereclause: ClauseElement | None = None) -> list[BaseModel]:
        query = select(self.model).offset(offset).limit(limit)
        if whereclause is not None:
            query = query.where(whereclause)
        logger.info(f"Query: {str(query)}")
        response = await self.session.execute(query)
        return response.scalars().all()

    async def get_by_id(self, id: UUID,
                        whereclause: ClauseElement | None = None) -> BaseModel | None:
        query = select(self.model).where(self.model.id == id)
        if whereclause is not None:
            query = query.where(whereclause)
        response = await self.session.execute(query)
        result = response.scalar_one_or_none()
        if result is None:
            raise RepoNotFoundException("Id not found")
        return result

    async def get_by_where(self, whereclause: ClauseElement) -> BaseModel | None:
        query = select(self.model)
        if whereclause is not None:
            query = query.where(whereclause)
        logger.info(f"Query: {str(query)}")
        response = await self.session.execute(query)
        return response.scalars().all()

    async def get_by_where_one_or_none(self, whereclause: ClauseElement) -> BaseModel | None:
        query = select(self.model)
        if whereclause is not None:
            query = query.where(whereclause)
        logger.info(f"Query: {str(query)}")
        response = await self.session.execute(query)
        obj = response.scalars().one_or_none()
        if not obj:
            raise RepoNotFoundException("Id not found")
        return obj

    async def delete(self, id: UUID, whereclause: ClauseElement | None = None) -> None:
        obj = await self.get_by_id(id=id, whereclause=whereclause)
        if not obj:
            raise RepoNotFoundException("Id not found")
        await self.session.delete(obj)
        await self.session.commit()

    async def create(self, obj_in: BaseModel) -> BaseModel | None:
        try:
            self.session.add(obj_in)
            await self.session.commit()
            await self.session.refresh(obj_in)
        except exc.IntegrityError as e:
            logger.error(e)
            await self.session.rollback()
            raise RepoConflictException("Resource already exists")
        except exc.SQLAlchemyError as e:
            await self.session.rollback()
            raise e
        return obj_in

    async def create_all(self, objs_in: list[BaseModel]) -> list[BaseModel] | None:
        try:
            self.session.add_all(objs_in)
            await self.session.commit()
        except exc.IntegrityError:
            await self.session.rollback()
            raise RepoConflictException("Resource already exists")
        except exc.SQLAlchemyError as e:
            await self.session.rollback()
            raise e
        return objs_in

    async def update(self, id: UUID, obj_in: BaseModel,
                     whereclause: ClauseElement | None = None) -> BaseModel | None:
        query = update(self.model).where(self.model.id == id).values(jsonable_encoder(obj_in))
        obj = await self.get_by_id(id=id, whereclause=whereclause)
        if not obj:
            raise RepoNotFoundException("Object not found")

        await self.session.execute(query)
        await self.session.commit()
        await self.session.commit()
        await self.session.refresh(obj)
        return obj

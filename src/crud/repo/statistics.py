import uuid
from typing import Generic, TypeVar

from sqlalchemy import select, func

from src.crud.models import BlogModel
from src.crud.repo.base import BaseRepository


T = TypeVar('T', bound=BlogModel)

class StatisticsRepository(BaseRepository, Generic[T]):

    async def get_average_blog_count_per_user(self, user_id: uuid.UUID) -> float:
        user_blog_counts = (
            select(BlogModel.user_id, func.count(BlogModel.id).label("blog_count"))
            .group_by(BlogModel.user_id)
            .subquery()
        )
        stmt = (
            select(func.avg(user_blog_counts.c.blog_count))
            .select_from(user_blog_counts)
            .where(user_blog_counts.c.user_id == user_id)  # Фильтр по user_id
        )
        result = await self.session.execute(stmt)
        average_blog_count = result.scalar()

        return float(average_blog_count) if average_blog_count is not None else 0.0

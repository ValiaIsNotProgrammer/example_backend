from sqlalchemy import Column, DateTime, Text, String, ForeignKey, func, UUID

from .base import BaseORMModel


class BlogModel(BaseORMModel):
    __tablename__ = 'blog'

    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user_id = Column(UUID, ForeignKey('user.id'), nullable=False)

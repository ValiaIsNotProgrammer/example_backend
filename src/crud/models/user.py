from sqlalchemy import Column, String, UniqueConstraint
from sqlalchemy.orm import relationship

from .base import BaseORMModel
from .blog import BlogModel


class UserModel(BaseORMModel):
    __tablename__ = 'user'

    name = Column(String(255), nullable=False)
    token = Column(String(255), nullable=False)

    blogs = relationship(BlogModel, backref='user', lazy=True)

    __table_args__ = (
        UniqueConstraint('token', name='token_uc'),
    )

from dataclasses import Field
from datetime import datetime
import uuid
from decimal import Decimal

from pydantic import BaseModel, model_validator


class BlogInput(BaseModel):
    title: str
    content: str

class BlogSearchInput(BlogInput):
    title: str | None = None
    content: str | None = None

    @model_validator(mode='before')
    def check_at_least_one_field(cls, values):
        if not any(values.get(field) for field in ('title', 'content')):
            raise ValueError('Хотя бы одно из полей "title" или "content" должно быть заполнено.')
        return values


class BlogOutput(BlogInput):
    created_at: datetime
    updated_at: datetime | None
    id: uuid.UUID


class StatisticsBlogOutput(BaseModel):
    average: float








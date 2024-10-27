import uuid

from sqlalchemy.util.preloaded import orm


class BaseORMModel(orm.DeclarativeBase):
    __abstract__ = True

    id: orm.Mapped[uuid.UUID] = orm.mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
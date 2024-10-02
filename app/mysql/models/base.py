import uuid

from sqlalchemy import MetaData
from sqlalchemy.orm import registry, DeclarativeBase, Mapped, mapped_column

mapper_registry = registry(metadata=MetaData())


class Base(DeclarativeBase):
    registry = mapper_registry
    metadata = mapper_registry.metadata

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)

    __abstract__ = True

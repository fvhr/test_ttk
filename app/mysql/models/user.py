from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from sqlalchemy import Column, String, Boolean

from .base import Base


class User(SQLAlchemyBaseUserTable[int], Base):
    __tablename__ = "user"

    hashed_password = Column(String(length=1024), nullable=False)
    email = Column(String(length=100), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)

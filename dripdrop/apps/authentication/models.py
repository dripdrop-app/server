from sqlalchemy import Column
from sqlalchemy.types import String, Boolean

from dripdrop.models.base import Base


class User(Base):
    __tablename__ = "users"
    email = Column(String, primary_key=True)
    password = Column(String, nullable=False)
    admin = Column(Boolean, nullable=False)

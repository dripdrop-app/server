from sqlalchemy import Column
from sqlalchemy.types import String, Boolean, TIMESTAMP

from dripdrop.models.base import Base
from dripdrop.utils import get_current_time


class User(Base):
    __tablename__ = "users"
    email = Column(String, primary_key=True)
    password = Column(String, nullable=False)
    admin = Column(Boolean, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=get_current_time,
    )

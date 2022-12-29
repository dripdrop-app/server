from dripdrop.utils import get_current_time
from sqlalchemy import Column
from sqlalchemy.orm import declarative_base
from sqlalchemy.types import String, Boolean, TIMESTAMP

Base = declarative_base()


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

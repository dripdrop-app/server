from datetime import datetime
from dripdrop.models import OrmBase, get_current_time
from pydantic import BaseModel, SecretStr
from sqlalchemy import Column, String, Boolean, TIMESTAMP


class Users(OrmBase):
    __tablename__ = "users"
    email = Column(String, primary_key=True)
    password = Column(String, nullable=False)
    admin = Column(Boolean, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=get_current_time,
    )


class ApiBase(BaseModel):
    class Config:
        orm_mode = True


class User(ApiBase):
    email: str
    password: SecretStr
    admin: bool
    created_at: datetime

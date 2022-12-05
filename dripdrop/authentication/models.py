from datetime import datetime
from dripdrop.models import OrmBase
from pydantic import BaseModel, SecretStr
from sqlalchemy import Column, String, Boolean, text, TIMESTAMP
from sqlalchemy.orm import relationship


class Users(OrmBase):
    __tablename__ = "users"
    email = Column(String, primary_key=True)
    password = Column(String, nullable=False)
    admin = Column(Boolean, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("NOW()"),
    )
    google_account = relationship(
        "GoogleAccounts",
        back_populates="user",
        uselist=False,
    )
    music_jobs = relationship("MusicJobs", back_populates="user")


class ApiBase(BaseModel):
    class Config:
        orm_mode = True


class User(ApiBase):
    email: str
    password: SecretStr
    admin: bool
    created_at: datetime

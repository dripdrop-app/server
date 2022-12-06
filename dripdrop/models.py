from datetime import datetime, timezone
from pydantic import BaseModel
from sqlalchemy import MetaData
from sqlalchemy.orm import declarative_base

metadata = MetaData()
OrmBase = declarative_base(metadata=metadata)


class ApiBase(BaseModel):
    class Config:
        orm_mode = True


def get_current_time():
    return datetime.now(timezone.utc)

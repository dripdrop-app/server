from datetime import datetime
from sqlalchemy import Column, MetaData, TIMESTAMP
from sqlalchemy.orm import declarative_base

from dripdrop.settings import settings

metadata = MetaData()


def get_current_time():
    return datetime.now(tz=settings.timezone)


class ModelBase:
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=get_current_time,
    )
    last_updated = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=get_current_time,
        onupdate=get_current_time,
    )


Base = declarative_base(metadata=metadata, cls=ModelBase)

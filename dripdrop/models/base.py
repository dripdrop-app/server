from datetime import datetime
from sqlalchemy import MetaData, TIMESTAMP
from sqlalchemy.orm import declarative_base, Mapped, mapped_column

from dripdrop.settings import settings

metadata = MetaData()


def get_current_time():
    return datetime.now(tz=settings.timezone)


class ModelBaseMixin(object):
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=get_current_time,
    )
    last_updated: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=get_current_time,
        onupdate=get_current_time,
    )


Base = declarative_base(metadata=metadata)

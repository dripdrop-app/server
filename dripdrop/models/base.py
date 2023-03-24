from datetime import datetime
from sqlalchemy import MetaData, TIMESTAMP
from sqlalchemy.orm import declarative_base, Mapped, mapped_column

from dripdrop.utils import get_current_time

metadata = MetaData()


class ModelBaseMixin(object):
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=get_current_time,
    )
    modified_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=get_current_time,
        onupdate=get_current_time,
    )


Base = declarative_base(metadata=metadata)

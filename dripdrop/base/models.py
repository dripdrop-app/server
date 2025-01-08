from datetime import datetime

from sqlalchemy import TIMESTAMP, MetaData
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

import dripdrop.utils as dripdrop_utils


class Base(DeclarativeBase):
    metadata = MetaData()

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=dripdrop_utils.get_current_time,
    )
    modified_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=dripdrop_utils.get_current_time,
        onupdate=dripdrop_utils.get_current_time,
    )

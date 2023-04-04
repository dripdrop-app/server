from datetime import datetime
from sqlalchemy import MetaData, TIMESTAMP
from sqlalchemy.orm import declarative_base, Mapped, mapped_column

import dripdrop.utils as dripdrop_utils

metadata = MetaData()


class ModelBaseMixin(object):
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


Base = declarative_base(metadata=metadata)

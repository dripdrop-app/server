from datetime import datetime
from sqlalchemy import TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column


from dripdrop.base.models import Base


class Proxy(Base):
    __tablename__ = "proxies"

    ip_address: Mapped[str] = mapped_column(primary_key=True)
    port: Mapped[int] = mapped_column(nullable=False)
    last_used: Mapped[datetime | None] = mapped_column(
        TIMESTAMP(timezone=True), nullable=True
    )

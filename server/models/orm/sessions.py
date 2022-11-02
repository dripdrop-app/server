from .base_model import Base
from .users import Users
from sqlalchemy import Column, String, text, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship


class Sessions(Base):
    __tablename__ = "sessions"
    id = Column(String, primary_key=True)
    user_email = Column(
        ForeignKey(
            Users.email,
            onupdate="CASCADE",
            ondelete="CASCADE",
            name="sessions_user_email_fkey",
        ),
        nullable=False,
    )
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("NOW()"),
    )
    user = relationship(
        "Users",
        back_populates="sessions",
        uselist=False,
    )

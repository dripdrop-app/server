from sqlalchemy.orm import Mapped, mapped_column

from dripdrop.models.base import Base, ModelBaseMixin


class User(ModelBaseMixin, Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(primary_key=True)
    password: Mapped[str] = mapped_column(nullable=False)
    admin: Mapped[bool] = mapped_column(nullable=False)

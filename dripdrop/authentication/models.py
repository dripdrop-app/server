from passlib.context import CryptContext
from sqlalchemy import select, event
from sqlalchemy.orm import Mapped, mapped_column

from dripdrop.base.models import Base
from dripdrop.services.database import AsyncSession


password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(primary_key=True)
    password: Mapped[str] = mapped_column(nullable=False)
    admin: Mapped[bool] = mapped_column(nullable=False, default=False)
    verified: Mapped[bool] = mapped_column(nullable=False, default=False)

    @classmethod
    async def find_by_email(cls, email: str, session: AsyncSession):
        query = select(User).where(User.email == email)
        results = await session.scalars(query)
        user = results.first()
        return user


@event.listens_for(User, "init")
def init_user(target: User, args, kwargs):
    if "password" in kwargs:
        kwargs["password"] = password_context.hash(kwargs["password"])

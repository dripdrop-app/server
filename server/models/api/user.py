from .base_model import Base
from datetime import datetime
from pydantic import SecretStr
from typing import Optional


class User(Base):
    email: str
    password: SecretStr
    admin: bool
    created_at: datetime


SessionUser = Optional[User]

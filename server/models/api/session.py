from .base_model import Base
from datetime import datetime


class Session(Base):
    id: str
    user_email: str
    created_at: datetime

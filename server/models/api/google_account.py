from .base_model import Base
from datetime import datetime


class GoogleAccount(Base):
    email: str
    user_email: str
    access_token: str
    refresh_token: str
    expires: int
    subscriptions_loading: bool
    created_at: datetime
    last_updated: datetime

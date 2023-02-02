from asgiref.sync import sync_to_async
from datetime import datetime
from sqlalchemy import select

from dripdrop.database import AsyncSession, Session
from dripdrop.services.google_api import google_api_service
from dripdrop.settings import settings

from .models import GoogleAccount


async def async_update_google_access_token(
    google_email: str = ..., session: AsyncSession = ...
):
    query = select(GoogleAccount).where(GoogleAccount.email == google_email)
    results = await session.scalars(query)
    account: GoogleAccount | None = results.first()
    if account:
        last_updated: datetime = account.last_updated
        difference = datetime.now(tz=settings.timezone) - last_updated.replace(
            tzinfo=settings.timezone
        )
        if difference.seconds >= account.expires:
            try:
                refresh_access_token = sync_to_async(
                    google_api_service.refresh_access_token
                )
                new_access_token = await refresh_access_token(
                    refresh_token=account.refresh_token
                )
                if new_access_token:
                    account.access_token = new_access_token["access_token"]
                    account.expires = new_access_token["expires_in"]
                    await session.commit()
            except Exception:
                account.access_token = ""
                account.expires = 0
                await session.commit()


def update_google_access_token(google_email: str = ..., session: Session = ...):
    query = select(GoogleAccount).where(GoogleAccount.email == google_email)
    results = session.scalars(query)
    account: GoogleAccount | None = results.first()
    if account:
        last_updated: datetime = account.last_updated
        difference = datetime.now(tz=settings.timezone) - last_updated.replace(
            tzinfo=settings.timezone
        )
        if difference.seconds >= account.expires:
            try:
                new_access_token = google_api_service.refresh_access_token(
                    refresh_token=account.refresh_token
                )
                if new_access_token:
                    account.access_token = new_access_token["access_token"]
                    account.expires = new_access_token["expires_in"]
                    session.commit()
            except Exception:
                account.access_token = ""
                account.expires = 0
                session.commit()

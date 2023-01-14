from fastapi import Depends, HTTPException, status
from sqlalchemy import select

from dripdrop.apps.authentication.models import User
from dripdrop.dependencies import (
    get_authenticated_user,
    create_db_session,
    AsyncSession,
)

from .models import GoogleAccount


async def get_google_user(
    user: User = Depends(get_authenticated_user),
    db: AsyncSession = Depends(create_db_session),
):
    query = select(GoogleAccount).where(GoogleAccount.user_email == user.email)
    results = await db.scalars(query)
    google_account: GoogleAccount | None = results.first()
    if google_account:
        return google_account
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

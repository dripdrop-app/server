from .models import GoogleAccount, GoogleAccounts
from dripdrop.authentication.models import User
from dripdrop.dependencies import (
    get_authenticated_user,
    create_db_session,
    AsyncSession,
)
from fastapi import Depends, HTTPException, status
from sqlalchemy import select


async def get_google_user(
    user: User = Depends(get_authenticated_user),
    db: AsyncSession = Depends(create_db_session),
):
    query = select(GoogleAccounts).where(GoogleAccounts.user_email == user.email)
    results = await db.scalars(query)
    google_account = results.first()
    if google_account:
        return GoogleAccount.from_orm(google_account)
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

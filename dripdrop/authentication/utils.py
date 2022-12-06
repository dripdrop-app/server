from .responses import AccountExistsResponse
from dripdrop.authentication.models import Users
from dripdrop.dependencies import AsyncSession, password_context
from fastapi import HTTPException, status
from sqlalchemy import select


async def create_new_account(
    email: str = ..., password: str = ..., db: AsyncSession = ...
):
    query = select(Users).where(Users.email == email)
    results = await db.scalars(query)
    user = results.first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=AccountExistsResponse
        )
    hashed_pw = password_context.hash(password.encode("utf-8"))
    account = Users(email=email, password=hashed_pw, admin=False)
    db.add(account)
    await db.commit()
    return account

from .responses import AccountExistsResponse
from dripdrop.authentication.models import User
from dripdrop.dependencies import AsyncSession, password_context
from fastapi import HTTPException, status
from sqlalchemy import select


async def create_new_account(
    email: str = ..., password: str = ..., db: AsyncSession = ...
):
    query = select(User).where(User.email == email)
    results = await db.scalars(query)
    user: User | None = results.first()
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=AccountExistsResponse
        )
    hashed_pw = password_context.hash(password)
    account = User(email=email, password=hashed_pw, admin=False)
    db.add(account)
    await db.commit()
    return account

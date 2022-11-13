import bcrypt
from dripdrop.dependencies import AsyncSession
from dripdrop.models import Users
from sqlalchemy import select


async def create_new_account(
    email: str = ..., password: str = ..., db: AsyncSession = ...
):
    query = select(Users).where(Users.email == email)
    results = await db.scalars(query)
    user = results.first()
    if user:
        raise Exception(message=f"Account with email `{email}` exists.")
    hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    account = Users(
        email=email,
        password=hashed_pw.decode("utf-8"),
        admin=False,
    )
    db.add(account)
    await db.commit()
    return account

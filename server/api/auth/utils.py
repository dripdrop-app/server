import bcrypt
from soupsieve import select
from server.dependencies import DBSession
from server.models.orm import Users


async def create_new_account(
    email: str = ...,
    password: str = ...,
    db: DBSession = ...,
):
    query = select(Users).where(Users.email == email)
    results = await db.scalars(query)
    user = results.first()
    if user:
        raise Exception(message=f"Account with email `{email}` exists.")
    hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    db.add(
        Users(
            email=email,
            password=hashed_pw.decode("utf-8"),
            admin=False,
        )
    )
    await db.commit()

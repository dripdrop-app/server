import jwt
from .responses import TokenResponse
from .utils import create_new_account
from datetime import timedelta, datetime
from dripdrop.settings import settings
from dripdrop.dependencies import (
    AsyncSession,
    create_db_session,
    get_authenticated_user,
    password_context,
    ALGORITHM,
)
from dripdrop.models import User, Users
from fastapi import FastAPI, Body, Depends, HTTPException, status
from fastapi.responses import PlainTextResponse, JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr
from sqlalchemy import select

app = FastAPI(openapi_tags=["Authentication"])


@app.get(
    "/session",
    dependencies=[Depends(get_authenticated_user)],
    responses={status.HTTP_401_UNAUTHORIZED: {}},
)
async def check_session():
    return PlainTextResponse(None, 200)


@app.post(
    "/login",
    responses={
        status.HTTP_401_UNAUTHORIZED: {},
        status.HTTP_404_NOT_FOUND: {},
        status.HTTP_400_BAD_REQUEST: {"description": "Incorrect Credentials"},
    },
)
async def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(create_db_session),
):
    query = select(Users).where(Users.email == form.username)
    results = await db.scalars(query)
    account = results.first()
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    account = User.from_orm(account)
    if not password_context.verify_and_update(
        secret=form.password.encode("utf-8"),
        hash=account.password.get_secret_value().encode("utf-8"),
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect Credentials"
        )
    token = jwt.encode(
        payload={"email": account.email, "exp": datetime.utcnow() + timedelta(days=14)},
        key=settings.secret_key,
        algorithm=ALGORITHM,
    )
    return JSONResponse(
        content=TokenResponse(access_token=token, token_type="bearer").dict(
            by_alias=True
        ),
        headers={"Authorization": f"Bearer {token}"},
    )


@app.post("/create")
async def create_account(
    email: EmailStr = Body(...),
    password: str = Body(..., min_length=8),
    db: AsyncSession = Depends(create_db_session),
):
    try:
        await create_new_account(
            email=email,
            password=password,
            db=db,
        )
    except Exception as e:
        raise HTTPException(400, detail=e.message)
    token = jwt.encode(
        payload={"email": email, "exp": datetime.utcnow() + timedelta(days=14)},
        key=settings.secret_key,
        algorithm=ALGORITHM,
    )
    return JSONResponse(
        content=TokenResponse(access_token=token, token_type="bearer").dict(
            by_alias=True
        ),
        headers={"Authorization": f"Bearer {token}"},
    )

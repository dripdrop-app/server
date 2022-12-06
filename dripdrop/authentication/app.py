import jwt
from .responses import (
    AuthenticatedResponse,
    IncorrectCredentialsResponse,
    UserResponse,
    AccountExistsResponse,
)
from .utils import create_new_account
from datetime import timedelta, datetime, timezone
from dripdrop.authentication.models import User, Users
from dripdrop.settings import settings
from dripdrop.dependencies import (
    AsyncSession,
    create_db_session,
    get_authenticated_user,
    password_context,
    ALGORITHM,
    COOKIE_NAME,
    TWO_WEEKS_EXPIRATION,
)
from fastapi import FastAPI, Body, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import PlainTextResponse, JSONResponse
from pydantic import EmailStr
from sqlalchemy import select

app = FastAPI(openapi_tags=["Authentication"])


@app.get(
    "/session",
    responses={status.HTTP_401_UNAUTHORIZED: {}},
)
async def check_session(user: User = Depends(get_authenticated_user)):
    return UserResponse(**user.dict())


@app.post(
    "/login",
    response_model=AuthenticatedResponse,
    responses={
        status.HTTP_401_UNAUTHORIZED: {},
        status.HTTP_404_NOT_FOUND: {},
        status.HTTP_400_BAD_REQUEST: {"description": IncorrectCredentialsResponse},
    },
)
async def login(
    email: str = Body(...),
    password: str = Body(..., min_length=8),
    db: AsyncSession = Depends(create_db_session),
):
    query = select(Users).where(Users.email == email)
    results = await db.scalars(query)
    account = results.first()
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    user = User.from_orm(account)
    verified, new_hashed_pw = password_context.verify_and_update(
        secret=password.encode("utf-8"),
        hash=user.password.get_secret_value().encode("utf-8"),
    )
    if new_hashed_pw:
        account.password = new_hashed_pw
        await db.commit()
    if not verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=IncorrectCredentialsResponse
        )
    token = jwt.encode(
        payload={
            "email": user.email,
            "exp": datetime.now(timezone.utc) + timedelta(days=14),
        },
        key=settings.secret_key,
        algorithm=ALGORITHM,
    )
    response = JSONResponse(
        content=jsonable_encoder(
            AuthenticatedResponse(access_token=token, token_type="bearer", user=user)
        ),
        headers={"Authorization": f"Bearer {token}"},
    )
    response.set_cookie(
        COOKIE_NAME,
        value=token,
        expires=TWO_WEEKS_EXPIRATION,
        max_age=TWO_WEEKS_EXPIRATION,
        httponly=True,
        secure=settings.env == "production",
    )
    return response


@app.get(
    "/logout",
    dependencies=[Depends(get_authenticated_user)],
    response_model=AuthenticatedResponse,
    responses={
        status.HTTP_401_UNAUTHORIZED: {},
        status.HTTP_400_BAD_REQUEST: {"description": AccountExistsResponse},
    },
)
async def logout():
    response = PlainTextResponse(None, status_code=status.HTTP_200_OK)
    response.delete_cookie(COOKIE_NAME)
    return response


@app.post("/create")
async def create_account(
    email: EmailStr = Body(...),
    password: str = Body(..., min_length=8),
    db: AsyncSession = Depends(create_db_session),
):
    account = await create_new_account(
        email=email,
        password=password,
        db=db,
    )
    token = jwt.encode(
        payload={
            "email": account.email,
            "exp": datetime.now(timezone.utc) + timedelta(days=14),
        },
        key=settings.secret_key,
        algorithm=ALGORITHM,
    )
    response = JSONResponse(
        content=jsonable_encoder(
            AuthenticatedResponse(access_token=token, token_type="bearer", user=account)
        ),
        headers={"Authorization": f"Bearer {token}"},
    )
    response.set_cookie(
        COOKIE_NAME,
        value=token,
        expires=TWO_WEEKS_EXPIRATION,
        max_age=TWO_WEEKS_EXPIRATION,
        httponly=True,
        secure=settings.env == "production",
    )
    return response

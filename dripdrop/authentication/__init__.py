import jwt
from .responses import AuthenticatedResponse, IncorrectCredentialsResponse
from .utils import create_new_account
from datetime import timedelta, datetime
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
from dripdrop.models import User, Users
from fastapi import FastAPI, Body, Depends, HTTPException, status
from fastapi.responses import PlainTextResponse, JSONResponse
from pydantic import EmailStr
from sqlalchemy import select

app = FastAPI(openapi_tags=["Authentication"])


@app.get(
    "/session",
    dependencies=[Depends(get_authenticated_user)],
    responses={status.HTTP_401_UNAUTHORIZED: {}},
)
async def check_session():
    return PlainTextResponse(None, status_code=status.HTTP_200_OK)


@app.post(
    "/login",
    responses={
        status.HTTP_401_UNAUTHORIZED: {},
        status.HTTP_404_NOT_FOUND: {},
        status.HTTP_400_BAD_REQUEST: IncorrectCredentialsResponse,
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
    account = User.from_orm(account)
    if not password_context.verify_and_update(
        secret=password.encode("utf-8"),
        hash=account.password.get_secret_value().encode("utf-8"),
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=IncorrectCredentialsResponse
        )
    token = jwt.encode(
        payload={"email": account.email, "exp": datetime.utcnow() + timedelta(days=14)},
        key=settings.secret_key,
        algorithm=ALGORITHM,
    )
    response = JSONResponse(
        content=AuthenticatedResponse(
            access_token=token, token_type="bearer", user=account
        ).dict(by_alias=True),
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
    responses={status.HTTP_401_UNAUTHORIZED: {}},
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
    try:
        account = await create_new_account(
            email=email,
            password=password,
            db=db,
        )
        token = jwt.encode(
            payload={
                "email": account.email,
                "exp": datetime.utcnow() + timedelta(days=14),
            },
            key=settings.secret_key,
            algorithm=ALGORITHM,
        )
        response = JSONResponse(
            content=AuthenticatedResponse(
                access_token=token, token_type="bearer", user=account
            ).dict(by_alias=True),
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
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)

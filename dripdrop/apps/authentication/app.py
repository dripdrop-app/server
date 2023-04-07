from fastapi import FastAPI, Body, Depends, HTTPException, status
from fastapi.responses import PlainTextResponse
from passlib.context import CryptContext
from pydantic import EmailStr

from dripdrop.dependencies import (
    create_database_session,
    get_authenticated_user,
    COOKIE_NAME,
)
from dripdrop.services.database import AsyncSession

from . import utils
from .models import User
from .responses import (
    AuthenticatedResponse,
    AuthenticatedResponseModel,
    UserResponse,
    ErrorMessages,
)

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI(openapi_tags=["Authentication"])


@app.get(
    "/session",
    response_model=UserResponse,
    responses={status.HTTP_401_UNAUTHORIZED: {}},
)
async def check_session(user: User = Depends(get_authenticated_user)):
    return UserResponse.from_orm(user)


@app.post(
    "/login",
    response_model=AuthenticatedResponseModel,
    responses={
        status.HTTP_401_UNAUTHORIZED: {},
        status.HTTP_404_NOT_FOUND: {},
        status.HTTP_400_BAD_REQUEST: {
            "description": ErrorMessages.IncorrectCredentials
        },
    },
)
async def login(
    email: str = Body(...),
    password: str = Body(..., min_length=8),
    session: AsyncSession = Depends(create_database_session),
):
    user = await utils.find_user_by_email(email=email, session=session)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    verified, new_hashed_pw = password_context.verify_and_update(
        secret=password, hash=user.password
    )
    if new_hashed_pw:
        user.password = new_hashed_pw
        await session.commit()
    if not verified:
        raise HTTPException(
            detail=ErrorMessages.IncorrectCredentials,
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    return AuthenticatedResponse(access_token=utils.create_jwt(email=email), user=user)


@app.get(
    "/logout",
    dependencies=[Depends(get_authenticated_user)],
    response_model=AuthenticatedResponseModel,
    responses={status.HTTP_401_UNAUTHORIZED: {}},
)
async def logout():
    response = PlainTextResponse(None, status_code=status.HTTP_200_OK)
    response.delete_cookie(COOKIE_NAME)
    return response


@app.post(
    "/create",
    response_model=AuthenticatedResponseModel,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": ErrorMessages.AccountExists},
    },
)
async def create_account(
    email: EmailStr = Body(...),
    password: str = Body(..., min_length=8),
    session: AsyncSession = Depends(create_database_session),
):
    user = await utils.find_user_by_email(email=email, session=session)
    if user:
        raise HTTPException(
            detail=ErrorMessages.AccountExists, status_code=status.HTTP_400_BAD_REQUEST
        )
    hashed_pw = password_context.hash(password)
    user = User(email=email, password=hashed_pw, admin=False)
    session.add(user)
    await session.commit()
    return AuthenticatedResponse(access_token=utils.create_jwt(email=email), user=user)

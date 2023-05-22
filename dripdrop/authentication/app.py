import traceback
from fastapi import (
    FastAPI,
    Body,
    Depends,
    HTTPException,
    status,
    Query,
    Request,
    Response,
)
from fastapi.responses import RedirectResponse
from passlib.context import CryptContext
from pydantic import EmailStr, BaseModel

from dripdrop.authentication import utils
from dripdrop.authentication.dependencies import (
    AuthenticatedUser,
    COOKIE_NAME,
    get_authenticated_user,
)
from dripdrop.authentication.models import User
from dripdrop.authentication.responses import (
    AuthenticatedResponse,
    AuthenticatedResponseModel,
    UserResponse,
    ErrorMessages,
)
from dripdrop.base.dependencies import DatabaseSession, RedisClient
from dripdrop.logger import logger
from dripdrop.services import sendgrid_client

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI(openapi_tags=["Authentication"])


@app.get(
    "/session",
    response_model=UserResponse,
    responses={status.HTTP_401_UNAUTHORIZED: {}},
)
async def check_session(user: AuthenticatedUser):
    return UserResponse.from_orm(user)


@app.post(
    "/login",
    response_model=AuthenticatedResponseModel,
    responses={status.HTTP_401_UNAUTHORIZED: {}, status.HTTP_404_NOT_FOUND: {}},
)
async def login(
    session: DatabaseSession,
    email: str = Body(...),
    password: str = Body(..., min_length=8),
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
    if not user.verified:
        raise HTTPException(
            detail=ErrorMessages.AccountUnverified,
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
    response = Response(None, status_code=status.HTTP_204_NO_CONTENT)
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
    request: Request,
    session: DatabaseSession,
    redis: RedisClient,
    email: EmailStr = Body(...),
    password: str = Body(..., min_length=8),
):
    user = await utils.find_user_by_email(email=email, session=session)
    if user:
        raise HTTPException(
            detail=ErrorMessages.AccountExists, status_code=status.HTTP_400_BAD_REQUEST
        )
    hashed_pw = password_context.hash(password)
    user = User(email=email, password=hashed_pw)
    verification_code = utils.generate_random_string(length=7)
    await redis.set(f"verify:{verification_code}", email, ex=3600)
    verify_link = utils.generate_server_link(
        request=request,
        path="/api/auth/verify",
        query={"token": verification_code},
    )
    try:
        await sendgrid_client.send_verification_email(email=email, link=verify_link)
    except Exception:
        logger.exception(traceback.format_exc())
        raise HTTPException(
            detail=ErrorMessages.EmailSendFail, status_code=status.HTTP_400_BAD_REQUEST
        )
    session.add(user)
    await session.commit()
    return Response(None, status_code=status.HTTP_204_NO_CONTENT)


@app.get("/verify")
async def verify_email(
    session: DatabaseSession,
    redis: RedisClient,
    token: str = Query(...),
):
    email = await redis.get(f"verify:{token}")
    if not email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    email = email.decode()
    user = await utils.find_user_by_email(email=email, session=session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorMessages.AccountDoesNotExist,
        )
    user.verified = True
    await session.commit()
    await redis.delete(f"verify:{token}")
    return RedirectResponse("/account")


class ResetEmail(BaseModel):
    email: EmailStr


@app.post("/sendreset")
async def send_reset_email(
    session: DatabaseSession,
    redis: RedisClient,
    reset_email: ResetEmail = Body(...),
):
    email = reset_email.email
    user = await utils.find_user_by_email(email=email, session=session)
    if not user:
        raise HTTPException(
            detail=ErrorMessages.AccountDoesNotExist,
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    if not user.verified:
        raise HTTPException(
            detail=ErrorMessages.AccountUnverified,
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    reset_code = utils.generate_random_string(length=7)
    await redis.set(f"reset:{reset_code}", email, ex=3600)
    try:
        await sendgrid_client.send_password_reset_email(email=email, token=reset_code)
    except Exception:
        logger.exception(traceback.format_exc())
        raise HTTPException(
            detail=ErrorMessages.EmailSendFail, status_code=status.HTTP_400_BAD_REQUEST
        )
    return Response(None, status_code=status.HTTP_204_NO_CONTENT)


@app.post("/reset")
async def reset_password(
    session: DatabaseSession,
    redis: RedisClient,
    token: str = Body(...),
    password: str = Body(..., min_length=8),
):
    email = await redis.get(f"reset:{token}")
    if not email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    email = email.decode()
    user = await utils.find_user_by_email(email=email, session=session)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=ErrorMessages.AccountDoesNotExist,
        )
    hashed_pw = password_context.hash(password)
    user.password = hashed_pw
    await session.commit()
    await redis.delete(f"reset:{token}")
    return Response(None, status_code=status.HTTP_204_NO_CONTENT)

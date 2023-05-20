import traceback
import uuid
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
from pydantic import EmailStr

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
    verification_code = str(uuid.uuid4())
    verification_token = utils.create_jwt_token(email=email, code=verification_code)
    await redis.set(f"verify:{email}", verification_code, ex=3600)
    verify_link = utils.generate_server_link(
        request=request,
        path="/api/auth/verify",
        query={"token": verification_token},
    )
    try:
        await sendgrid_client.send_verification_email(email=email, link=verify_link)
    except Exception:
        logger.exception(traceback.format_exc())
        raise HTTPException(detail=ErrorMessages.EmailSendFail)
    session.add(user)
    await session.commit()
    return Response(None, status_code=status.HTTP_204_NO_CONTENT)


@app.get("/verify")
async def verify_email(
    session: DatabaseSession,
    redis: RedisClient,
    token: str = Query(...),
):
    payload = utils.decode_jwt(token=token)
    if not payload:
        raise HTTPException(
            detail=ErrorMessages.TokenError, status_code=status.HTTP_400_BAD_REQUEST
        )
    email = payload.get("email", None)
    code = payload.get("code", None)
    user = await utils.find_user_by_email(email=email, session=session)
    verification_code = await redis.get(f"verify:{email}")
    if verification_code:
        verification_code = verification_code.decode()
    if str(code) != verification_code or not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    user.verified = True
    await session.commit()
    await redis.delete(f"verify:{email}")
    return RedirectResponse("/account")


@app.get("/sendreset")
async def send_reset_email(
    session: DatabaseSession,
    redis: RedisClient,
    email: EmailStr = Query(...),
):
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
    existing_code = await redis.get(f"reset:{email}")
    if existing_code:
        raise HTTPException(
            detail=ErrorMessages.ResetEmailExists,
            status_code=status.HTTP_400_BAD_REQUEST,
        )
    reset_code = str(uuid.uuid4())
    reset_token = utils.create_jwt_token(email=email, code=reset_code)
    await redis.set(f"reset:{email}", reset_code, ex=3600)
    try:
        await sendgrid_client.send_password_reset_email(email=email, token=reset_token)
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
    payload = utils.decode_jwt(token=token)
    if not payload:
        raise HTTPException(
            detail=ErrorMessages.TokenError, status_code=status.HTTP_400_BAD_REQUEST
        )
    email = payload.get("email", None)
    code = payload.get("code", None)
    user = await utils.find_user_by_email(email=email, session=session)
    reset_code = await redis.get(f"reset:{email}")
    if reset_code:
        reset_code = reset_code.decode()
    if str(code) != reset_code or not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    hashed_pw = password_context.hash(password)
    user.password = hashed_pw
    await session.commit()
    await redis.delete(f"reset:{email}")
    return Response(None, status_code=status.HTTP_204_NO_CONTENT)

import bcrypt
import uuid
from .utils import create_new_account
from fastapi import APIRouter, Body, Depends, Response, HTTPException
from fastapi.responses import JSONResponse
from pydantic import EmailStr
from server.config import config
from server.dependencies import (
    SessionHandler,
    DBSession,
    create_db_session,
    get_authenticated_user,
)
from server.models.api import AuthResponses, User
from server.models.orm import Users, Sessions
from sqlalchemy import select

auth_api = APIRouter(prefix="/auth", tags=["Authentication"])


@auth_api.get(
    "/session",
    response_model=AuthResponses.User,
    responses={401: {}},
)
async def check_session(user: User = Depends(get_authenticated_user)):
    return AuthResponses.User(email=user.email, admin=user.admin).dict()


@auth_api.post(
    "/login",
    response_model=AuthResponses.User,
    responses={401: {}, 404: {"description": "Account not found"}},
)
async def login(
    email: str = Body(...),
    password: str = Body(...),
    db: DBSession = Depends(create_db_session),
):
    query = select(Users).where(Users.email == email)
    results = await db.scalars(query)
    account = results.first()
    if not account:
        raise HTTPException(404)
    account = User.from_orm(account)
    if not bcrypt.checkpw(
        password.encode("utf-8"),
        account.password.get_secret_value().encode("utf-8"),
    ):
        raise HTTPException(400)
    session_id = str(uuid.uuid4())
    db.add(Sessions(id=session_id, user_email=email))
    await db.commit()
    response = JSONResponse(AuthResponses.User(email=email, admin=account.admin).dict())
    TWO_WEEKS_EXPIRATION = 14 * 24 * 60 * 60
    response.set_cookie(
        SessionHandler.cookie_name,
        await SessionHandler.encrypt({"id": session_id}),
        max_age=TWO_WEEKS_EXPIRATION,
        expires=TWO_WEEKS_EXPIRATION,
        httponly=True,
        secure=config.env == "production",
    )
    return response


@auth_api.get(
    "/logout",
    dependencies=[Depends(get_authenticated_user)],
    responses={401: {}},
)
async def logout():
    response = Response(None, 200)
    response.set_cookie(
        "session",
        max_age=-1,
        expires=-1,
    )
    return response


@auth_api.post(
    "/create",
    response_model=AuthResponses.User,
    status_code=201,
)
async def create_account(
    email: EmailStr = Body(...),
    password: str = Body(..., min_length=8),
    db: DBSession = Depends(create_db_session),
):
    try:
        await create_new_account(
            email=email,
            password=password,
            db=db,
        )
    except Exception as e:
        raise HTTPException(400, detail=e.message)
    return AuthResponses.User(email=email, admin=False)

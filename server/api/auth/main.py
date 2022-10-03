import bcrypt
import uuid
from fastapi import Body, FastAPI, Depends, Response, HTTPException
from fastapi.responses import JSONResponse
from pydantic import EmailStr
from server.config import config
from server.dependencies import SessionHandler, get_authenticated_user
from server.models.api import AuthResponses
from server.models.main import db, Users, Sessions, User
from sqlalchemy import select, insert

auth_app = FastAPI()


@auth_app.get("/session", response_model=AuthResponses.User, responses={401: {}})
async def check_session(user: User = Depends(get_authenticated_user)):
    return AuthResponses.User(email=user.email, admin=user.admin).dict()


@auth_app.post(
    "/login", response_model=AuthResponses.User, responses={401: {}, 404: {}}
)
async def login(email: str = Body(...), password: str = Body(...)):
    query = select(Users).where(Users.email == email)
    account = await db.fetch_one(query)
    if not account:
        raise HTTPException(404, "Account not found.")
    account = User.parse_obj(account)
    if not bcrypt.checkpw(
        password.encode("utf-8"), account.password.get_secret_value().encode("utf-8")
    ):
        raise HTTPException(400, "Email or Password is incorrect.")
    session_id = str(uuid.uuid4())
    query = insert(Sessions).values(id=session_id, user_email=email)
    await db.execute(query)
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


@auth_app.get(
    "/logout", dependencies=[Depends(get_authenticated_user)], responses={401: {}}
)
async def logout():
    response = Response(None, 200)
    response.set_cookie("session", max_age=-1, expires=-1)
    return response


async def create_new_account(email: str = ..., password: str = ...):
    query = select(Users).where(Users.email == email)
    account = await db.fetch_one(query)
    if account:
        raise HTTPException(400, f"Account with email `{email}` exists.")
    hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    query = insert(Users).values(
        email=email,
        password=hashed_pw.decode("utf-8"),
        admin=False,
    )
    await db.execute(query)


@auth_app.post("/create", response_model=AuthResponses.User, status_code=201)
async def create_account(
    email: EmailStr = Body(...), password: str = Body(..., min_length=8)
):
    await create_new_account(email=email, password=password)
    return AuthResponses.User(email=email, admin=False)

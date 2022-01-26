import bcrypt
import uuid
from asyncpg.exceptions import UniqueViolationError
from fastapi import FastAPI, Depends, Response, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.sql.expression import true
from server.api.youtube import google_api
from server.dependencies import SessionHandler, get_authenticated_user
from server.models import AuthenticatedUser
from server.models.api import AuthRequests, AuthResponses
from server.config import config
from server.models import db, GoogleAccounts, Users, Sessions, User
from server.queue import q
from sqlalchemy import select, insert, update
from typing import Optional

app = FastAPI()


@app.get("/check_session", response_model=AuthResponses.User, responses={401: {}})
async def check_session(user: AuthenticatedUser = Depends(get_authenticated_user)):
    return JSONResponse({"email": user.email, "admin": user.admin}, 200)


@app.post("/login", response_model=AuthResponses.User, responses={401: {}, 404: {}})
async def login(body: AuthRequests.Login):
    email = body.email
    password = body.password

    query = select(Users).where(Users.email == email)
    account = await db.fetch_one(query)
    if not account:
        raise HTTPException(404, "Account not found.")

    account = User.parse_obj(account)
    if not bcrypt.checkpw(
        password.encode("utf-8"), account.password.get_secret_value().encode("utf-8")
    ):
        raise HTTPException(400, "Email or Password is incorrect.")

    if not account.approved:
        raise HTTPException(401, "User has not been approved.")

    session_id = str(uuid.uuid4())
    query = insert(Sessions).values(id=session_id, user_email=email)
    await db.execute(query)

    response = JSONResponse(
        {
            "email": email,
            "admin": account.admin,
        }
    )

    TWO_WEEKS_EXPIRATION = 14 * 24 * 60 * 60
    response.set_cookie(
        SessionHandler.cookie_name,
        await SessionHandler.encrypt({"id": session_id}),
        max_age=TWO_WEEKS_EXPIRATION,
        expires=TWO_WEEKS_EXPIRATION,
        httponly=true,
        secure=config.env == "production",
    )
    return response


@app.get("/logout", dependencies=[Depends(get_authenticated_user)], responses={401: {}})
async def logout():
    response = Response(None, 200)
    response.set_cookie("session", max_age=-1, expires=-1)
    return response


async def create_new_account(email: str, password: str):
    query = select(Users).where(Users.email == email)
    account = await db.fetch_one(query)
    if account:
        raise HTTPException(400, f"Account with email `{email}` exists.")

    hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    query = insert(Users).values(
        email=email, password=hashed_pw.decode("utf-8"), admin=False, approved=False
    )
    await db.execute(query)


@app.post("/create", response_model=AuthRequests.Login, status_code=201)
async def create_account(body: AuthRequests.CreateAccount):
    email = body.email
    password = body.password
    await create_new_account(email, password)
    return JSONResponse({"email": email, "admin": False})


# @requires([AuthScopes.ADMIN])
# async def admin_create_account(email: str, password: str):
#     try:
#         await create_new_account(email, password)
#     except ValueError as e:
#         return JSONResponse({'error': e.message}, 400)

#     return Response({'email': email, 'admin': False}, 201)


@app.get(
    "/googleoauth2", dependencies=[Depends(get_authenticated_user)], responses={401: {}}
)
async def google_oauth2(state: str, code: str, error: Optional[str] = None):
    if error:
        raise HTTPException(400)

    email = state
    query = select(Users).where(Users.email == email)
    user = await db.fetch_one(query)
    if not user:
        return RedirectResponse("/")

    tokens = await google_api.get_oauth_tokens(
        f"{config.server_url}/auth/googleoauth2", code
    )
    if tokens:
        google_email = await google_api.get_user_email(tokens.get("access_token"))
        if google_email:
            try:
                query = insert(GoogleAccounts).values(
                    email=google_email,
                    user_email=email,
                    access_token=tokens["access_token"],
                    refresh_token=tokens["refresh_token"],
                    expires=tokens["expires_in"],
                )
                await db.execute(query)
            except UniqueViolationError:
                query = (
                    update(GoogleAccounts)
                    .values(
                        access_token=tokens["access_token"],
                        refresh_token=tokens["refresh_token"],
                        expires=tokens["expires_in"],
                    )
                    .where(GoogleAccounts.email == google_email)
                )
                await db.execute(query)
            except Exception:
                return RedirectResponse("/youtubeCollections")
            update_categories_job = q.enqueue(
                "server.api.youtube.tasks.update_youtube_video_categories", False
            )
            q.enqueue_call(
                "server.api.youtube.tasks.update_user_youtube_subscriptions_job",
                args=(email,),
                depends_on=update_categories_job.id,
            )
    return RedirectResponse("/youtubeCollections")
